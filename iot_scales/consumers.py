"""
Smart Scale WebSocket Consumer (Django Channels)
Handles real-time bi-directional telemetry and commands between IoT scales,
port operators, and frontend dashboards via Redis Channel Layer.
"""

import json
from datetime import datetime
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone


class SmartScaleConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for streaming smart scale telemetry in real time.
    Routes:
        ws://domain/ws/scales/<device_id>/
        ws://domain/ws/scales/
    """

    @database_sync_to_async
    def _authenticate_token(self, token_key: str) -> bool:
        if not token_key:
            return False
        from rest_framework.authtoken.models import Token
        token_obj = Token.objects.select_related('user').filter(key=token_key).first()
        if not token_obj or not token_obj.user or not token_obj.user.is_active:
            return False
        user = token_obj.user
        return bool(
            getattr(user, 'role', '') in ('admin', 'superadmin', 'regulator')
            or user.is_staff
            or user.is_superuser
        )

    async def _join_scale_groups(self):
        if self.groups_joined:
            return
        if self.device_id and self.device_id != 'all':
            self.device_group = f"scale_{self.device_id}"
            await self.channel_layer.group_add(self.device_group, self.channel_name)
            self.groups_joined.append(self.device_group)

        self.global_group = "scale_all"
        await self.channel_layer.group_add(self.global_group, self.channel_name)
        self.groups_joined.append(self.global_group)

    async def connect(self):
        self.device_id = self.scope.get('url_route', {}).get('kwargs', {}).get('device_id', 'all')
        self.groups_joined = []
        user = self.scope.get('user')
        self.is_authorized = bool(
            user
            and getattr(user, 'is_authenticated', False)
            and (
                getattr(user, 'role', '') in ('admin', 'superadmin', 'regulator')
                or getattr(user, 'is_staff', False)
                or getattr(user, 'is_superuser', False)
            )
        )

        await self.accept()

        if self.is_authorized:
            await self._join_scale_groups()
            await self.send_json({
                'event': 'connected',
                'device_id': self.device_id,
                'timestamp': timezone.now().isoformat(),
                'message': f'Terhubung ke aliran data timbangan (perangkat: {self.device_id}).'
            })

    async def disconnect(self, close_code):
        # Leave all joined groups on disconnect
        for group in self.groups_joined:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def receive_json(self, content):
        """
        Receive bi-directional control signals or queries from client.
        Supported actions:
        - {"action": "auth", "token": "..."} -> Authenticate DRF token before streaming
        - {"action": "ping"} -> Pong heartbeat
        - {"action": "subscribe", "device_id": "SCALE-02"} -> Switch or add device
        """
        action = content.get('action')

        if action == 'auth':
            ok = await self._authenticate_token(str(content.get('token', '')).strip())
            if not ok:
                await self.send_json({'event': 'error', 'message': 'Autentikasi gagal, silakan periksa kembali token Anda.'})
                await self.close(code=4001)
                return
            self.is_authorized = True
            await self._join_scale_groups()
            await self.send_json({
                'event': 'connected',
                'device_id': self.device_id,
                'timestamp': timezone.now().isoformat(),
                'message': f'Terhubung ke aliran data timbangan (perangkat: {self.device_id}).'
            })
            return

        if not getattr(self, 'is_authorized', False):
            await self.send_json({'event': 'error', 'message': 'Silakan lakukan autentikasi terlebih dahulu.'})
            await self.close(code=4001)
            return

        if action == 'ping':
            await self.send_json({
                'event': 'pong',
                'timestamp': timezone.now().isoformat()
            })
            return

        if action == 'subscribe':
            new_device = content.get('device_id')
            if new_device and new_device != self.device_id:
                new_group = f"scale_{new_device}"
                await self.channel_layer.group_add(new_group, self.channel_name)
                self.groups_joined.append(new_group)
                await self.send_json({
                    'event': 'subscribed',
                    'device_id': new_device,
                    'timestamp': timezone.now().isoformat()
                })
            return

        # Default fallback acknowledgment
        await self.send_json({
            'event': 'received',
            'action': action,
            'status': 'ok'
        })

    async def scale_weight_update(self, event):
        """
        Handler invoked by group_send(..., {"type": "scale_weight_update", "data": ...})
        """
        await self.send_json(event['data'])

    async def scale_command(self, event):
        """
        Handler invoked for remote control commands (e.g. tare, hold, zero)
        """
        await self.send_json({
            'event': 'command',
            'data': event['data']
        })
