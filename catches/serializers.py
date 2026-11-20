from decimal import Decimal
from rest_framework import serializers
from .models import FishCatch, CatchDetail
from ships.models import Ship, Quota
from fish.models import FishSpecies
from django.core.exceptions import ObjectDoesNotExist

class CatchDetailSerializer(serializers.ModelSerializer):
    fish_species_name = serializers.CharField(source='fish_species.name', read_only=True)
    wpp_name = serializers.CharField(source='wpp.nama', read_only=True)
    scale_reading_id = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True)

    class Meta:
        model = CatchDetail
        fields = ['id', 'fish_species', 'quantity', 'unit', 'value', 'notes', 'fish_species_name', 'wpp_name', 'wpp', 'tarif_index', 'pnkp', 'pnbp', 'scale_reading_id']

class FishCatchSerializer(serializers.ModelSerializer):
    ship_name = serializers.CharField(source='ship.name', read_only=True)
    catch_details = CatchDetailSerializer(many=True, read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override ship field to accept registration_number
        self.fields['ship'] = serializers.CharField()

    def create(self, validated_data):
        ship_registration = validated_data.pop('ship')
        try:
            ship = Ship.objects.get(registration_number=ship_registration)
            validated_data['ship'] = ship
        except Ship.DoesNotExist:
            raise serializers.ValidationError(f"Kapal dengan nomor registrasi '{ship_registration}' tidak ditemukan")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        ship_registration = validated_data.pop('ship', None)
        if ship_registration:
            try:
                ship = Ship.objects.get(registration_number=ship_registration)
                validated_data['ship'] = ship
            except Ship.DoesNotExist:
                raise serializers.ValidationError(f"Kapal dengan nomor registrasi '{ship_registration}' tidak ditemukan")
        return super().update(instance, validated_data)

    class Meta:
        model = FishCatch
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class FishCatchWithDetailsSerializer(serializers.ModelSerializer):
    """Serializer for creating FishCatch with nested CatchDetails in a single request"""
    catch_details = CatchDetailSerializer(many=True, write_only=True)
    ship_name = serializers.CharField(source='ship.name', read_only=True)
    catch_details_display = CatchDetailSerializer(many=True, read_only=True, source='catch_details')
    quota = serializers.SerializerMethodField(read_only=True)
    remaining_quota = serializers.SerializerMethodField(read_only=True)
    scale_reading_id = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override ship field to accept registration_number
        self.fields['ship'] = serializers.CharField()

    class Meta:
        model = FishCatch
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_quota(self, obj):
        """Get the total quota for the ship's year"""
        try:
            quota_obj = Quota.objects.get(ship=obj.ship, year=obj.catch_date.year, is_active=True)
            return quota_obj.quota
        except ObjectDoesNotExist:
            return None

    def get_remaining_quota(self, obj):
        """Get the remaining quota for the ship's year"""
        try:
            quota_obj = Quota.objects.get(ship=obj.ship, year=obj.catch_date.year, is_active=True)
            return quota_obj.remaining_quota
        except ObjectDoesNotExist:
            return None

    def _calculate_total_weight(self, catch_details_data):
        """Calculate total weight from catch details normalized to kg"""
        total_weight = 0.0
        for detail in catch_details_data:
            qty = detail.get('quantity', 0)
            try:
                qty_val = float(qty)
            except (ValueError, TypeError):
                qty_val = 0.0
            unit_str = str(detail.get('unit', 'kg') or '').strip().lower()
            multiplier = 1000.0 if unit_str in ('ton', 'tons', 'tonnes') else 1.0
            total_weight += qty_val * multiplier
        return total_weight

    def _check_and_update_quota(self, ship, year, total_weight):
        """Check if quota allows the catch and update remaining quota in kg"""
        try:
            quota_obj = Quota.objects.get(ship=ship, year=year, is_active=True)
            weight_dec = Decimal(str(round(total_weight, 2)))
            if weight_dec > quota_obj.remaining_quota:
                raise serializers.ValidationError(
                    f"Sisa kuota kapal tidak mencukupi ({quota_obj.remaining_quota} kg tersisa, dibutuhkan {weight_dec} kg)."
                )
            # Update remaining quota
            quota_obj.remaining_quota -= weight_dec
            quota_obj.save()
            return quota_obj
        except ObjectDoesNotExist:
            # If no quota exists, allow unlimited (don't raise error)
            return None

    def create(self, validated_data):
        catch_details_data = validated_data.pop('catch_details', [])
        scale_reading_id = validated_data.pop('scale_reading_id', None)

        # Handle ship registration number conversion
        ship_registration = validated_data.pop('ship')
        try:
            ship = Ship.objects.get(registration_number=ship_registration)
            validated_data['ship'] = ship
        except Ship.DoesNotExist:
            raise serializers.ValidationError(f"Kapal dengan nomor registrasi '{ship_registration}' tidak ditemukan")

        fish_catch = FishCatch._default_manager.create(**validated_data)

        # Calculate total weight and check quota
        total_weight = self._calculate_total_weight(catch_details_data)
        year = fish_catch.catch_date.year
        self._check_and_update_quota(fish_catch.ship, year, total_weight)

        # Extract all linked scale reading ids
        all_reading_ids = set()
        if scale_reading_id:
            all_reading_ids.add(str(scale_reading_id).strip())

        # Create catch details
        created_details = []
        for detail_data in catch_details_data:
            r_id = detail_data.pop('scale_reading_id', None)
            if r_id:
                all_reading_ids.add(str(r_id).strip())
            detail = CatchDetail._default_manager.create(fish_catch=fish_catch, **detail_data)
            created_details.append(detail)

        # Mark any associated IoT scale readings as saved
        if all_reading_ids:
            try:
                from iot_scales.models import ScaleReading
                from iot_scales.infrastructure.event_bus import scale_event_bus
                try:
                    from asgiref.sync import async_to_sync
                    from channels.layers import get_channel_layer
                except ImportError:
                    async_to_sync = None
                    get_channel_layer = None

                first_detail = created_details[0] if created_details else None
                readings = ScaleReading.objects.filter(id__in=all_reading_ids)
                channel_layer = get_channel_layer() if get_channel_layer else None

                for r in readings:
                    r.status = 'saved'
                    r.fish_catch = fish_catch
                    if first_detail:
                        r.catch_detail = first_detail
                    r.save(update_fields=['status', 'fish_catch', 'catch_detail'])

                    broadcast_payload = {
                        'event': 'weight_saved',
                        'reading_id': str(r.id),
                        'device_id': r.device_id,
                        'status': 'saved',
                        'catch_id': fish_catch.id,
                        'weight': float(r.weight),
                        'unit': r.unit
                    }
                    if channel_layer and async_to_sync:
                        try:
                            async_to_sync(channel_layer.group_send)(
                                f"scale_{r.device_id}",
                                {"type": "scale_weight_update", "data": broadcast_payload}
                            )
                            async_to_sync(channel_layer.group_send)(
                                "scale_all",
                                {"type": "scale_weight_update", "data": broadcast_payload}
                            )
                        except Exception:
                            pass
                    scale_event_bus.broadcast(broadcast_payload, device_id=r.device_id)
            except Exception:
                pass

        # Auto-seal catch report and details into cryptographic blockchain block
        try:
            from blockchain.application.blockchain_service import BlockchainApplicationService
            blockchain_service = BlockchainApplicationService()
            blockchain_service.record_catch_transaction(fish_catch)
        except Exception:
            pass

        return fish_catch
    
    def update(self, instance, validated_data):
        catch_details_data = validated_data.pop('catch_details', None)

        # Handle ship registration number conversion
        ship_registration = validated_data.pop('ship', None)
        if ship_registration:
            try:
                ship = Ship.objects.get(registration_number=ship_registration)
                validated_data['ship'] = ship
            except Ship.DoesNotExist:
                raise serializers.ValidationError(f"Kapal dengan nomor registrasi '{ship_registration}' tidak ditemukan")

        # Store old values for quota adjustment (normalized to kg)
        old_ship = instance.ship
        old_year = instance.catch_date.year
        old_total_weight = sum(
            float(detail.quantity) * (1000.0 if str(detail.unit or '').strip().lower() in ('ton', 'tons', 'tonnes') else 1.0)
            for detail in instance.catch_details.all()
        )

        # Update FishCatch fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Get new values
        new_ship = instance.ship
        new_year = instance.catch_date.year

        # Update catch details if provided
        if catch_details_data is not None:
            # Calculate new total weight
            new_total_weight = self._calculate_total_weight(catch_details_data)

            # Adjust quotas
            # Add back old weight to old quota
            if old_total_weight > 0:
                try:
                    old_quota_obj = Quota.objects.get(ship=old_ship, year=old_year, is_active=True)
                    old_quota_obj.remaining_quota += Decimal(str(round(old_total_weight, 2)))
                    old_quota_obj.save()
                except ObjectDoesNotExist:
                    pass  # Old quota might not exist, that's ok

            # Check and deduct from new quota
            self._check_and_update_quota(new_ship, new_year, new_total_weight)

            # Delete existing details and create new ones
            instance.catch_details.all().delete()
            for detail_data in catch_details_data:
                CatchDetail._default_manager.create(fish_catch=instance, **detail_data)
        else:
            # If only FishCatch fields changed (ship or date), adjust quota accordingly
            if old_ship != new_ship or old_year != new_year:
                # Add back to old quota if it exists
                if old_total_weight > 0:
                    try:
                        old_quota_obj = Quota.objects.get(ship=old_ship, year=old_year, is_active=True)
                        old_quota_obj.remaining_quota += Decimal(str(round(old_total_weight, 2)))
                        old_quota_obj.save()
                    except ObjectDoesNotExist:
                        pass  # Old quota might not exist, that's ok

                # Deduct from new quota
                self._check_and_update_quota(new_ship, new_year, old_total_weight)

        return instance
