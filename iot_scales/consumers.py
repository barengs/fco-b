"""
Smart Scale WebSocket Consumer (Django Channels)
Handles real-time bi-directional telemetry and commands between IoT scales,
port operators, and frontend dashboards via Redis Channel Layer.
"""

import json
from datetime import datetime
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone


class SmartScaleConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for streaming smart scale telemetry in real time.
    Routes:
        ws://domain/ws/scales/<device_id>/
        ws://domain/ws/scales/
    """

    async def connect(self):
        # Extract device_id from URL kwargs if present
        self.device_id = self.scope.get('url_route', {}).get('kwargs', {}).get('device_id', 'all')
        self.groups_joined = []

        # Join the specific device group
        if self.device_id and self.device_id != 'all':
            self.device_group = f"scale_{self.device_id}"
            await self.channel_layer.group_add(self.device_group, self.channel_name)
            self.groups_joined.append(self.device_group)

        # Always join global "scale_all" group for monitoring & multi-scale dashboards
        self.global_group = "scale_all"
        await self.channel_layer.group_add(self.global_group, self.channel_name)
        self.groups_joined.append(self.global_group)

        await self.accept()

        # Send welcome payload
        await self.send_json({
            'event': 'connected',
            'device_id': self.device_id,
            'timestamp': timezone.now().isoformat(),
            'message': f'Terhubung ke WebSocket siaran data timbangan pintar (Device: {self.device_id})'
        })

    async def disconnect(self, close_code):
        # Leave all joined groups on disconnect
        for group in self.groups_joined:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def receive_json(self, content):
        """
        Receive bi-directional control signals or queries from client.
        Supported actions:
        - {"action": "ping"} -> Pong heartbeat
        - {"action": "tare", "device_id": "SCALE-01"} -> Send tare signal
        - {"action": "subscribe", "device_id": "SCALE-02"} -> Switch or add device
        """
        action = content.get('action')

        if action == 'ping':
            await self.send_json({
                'event': 'pong',
                'timestamp': timezone.now().isoformat()
            })
            return

        if action == 'tare':
            target_device = content.get('device_id', self.device_id)
            # Broadcast tare command to device group
            if target_device:
                await self.channel_layer.group_send(
                    f"scale_{target_device}",
                    {
                        'type': 'scale_command',
                        'data': {
                            'command': 'tare',
                            'device_id': target_device,
                            'timestamp': timezone.now().isoformat()
                        }
                    }
                )
                await self.send_json({
                    'event': 'command_ack',
                    'command': 'tare',
                    'target_device': target_device,
                    'status': 'sent'
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
