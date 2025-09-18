from rest_framework import serializers
from .models import FishCatch, CatchDetail
from ships.models import Ship, Quota
from fish.models import FishSpecies
from django.core.exceptions import ObjectDoesNotExist

class CatchDetailSerializer(serializers.ModelSerializer):
    fish_species_name = serializers.CharField(source='fish_species.name', read_only=True)

    class Meta:
        model = CatchDetail
        fields = ['id', 'fish_species', 'quantity', 'unit', 'value', 'notes', 'fish_species_name']
        read_only_fields = ['fish_catch']

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

class FishCatchWithDetailsSerializer(serializers.ModelSerializer):
    """Serializer for creating FishCatch with nested CatchDetails in a single request"""
    catch_details = CatchDetailSerializer(many=True, write_only=True)
    ship_name = serializers.CharField(source='ship.name', read_only=True)
    catch_details_display = CatchDetailSerializer(many=True, read_only=True, source='catch_details')
    quota = serializers.SerializerMethodField(read_only=True)
    remaining_quota = serializers.SerializerMethodField(read_only=True)

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
        """Calculate total weight from catch details in kg"""
        total_weight = 0
        for detail in catch_details_data:
            if detail.get('unit', 'kg') == 'kg':
                total_weight += detail.get('quantity', 0)
        return total_weight

    def _check_and_update_quota(self, ship, year, total_weight):
        """Check if quota allows the catch and update remaining quota"""
        try:
            quota_obj = Quota.objects.get(ship=ship, year=year, is_active=True)
            if total_weight > quota_obj.remaining_quota:
                raise serializers.ValidationError(f"Kuota habis. Sisa kuota: {quota_obj.remaining_quota} kg, dibutuhkan: {total_weight} kg")
            # Update remaining quota
            quota_obj.remaining_quota -= total_weight
            quota_obj.save()
            return quota_obj
        except ObjectDoesNotExist:
            # If no quota exists, allow unlimited (don't raise error)
            return None

    def create(self, validated_data):
        catch_details_data = validated_data.pop('catch_details', [])
        fish_catch = FishCatch._default_manager.create(**validated_data)

        # Calculate total weight and check quota
        total_weight = self._calculate_total_weight(catch_details_data)
        year = fish_catch.catch_date.year
        self._check_and_update_quota(fish_catch.ship, year, total_weight)

        # Create catch details
        for detail_data in catch_details_data:
            CatchDetail._default_manager.create(fish_catch=fish_catch, **detail_data)

        return fish_catch
    
    def update(self, instance, validated_data):
        catch_details_data = validated_data.pop('catch_details', None)

        # Store old values for quota adjustment
        old_ship = instance.ship
        old_year = instance.catch_date.year
        old_total_weight = sum(
            detail.quantity for detail in instance.catch_details.all()
            if detail.unit == 'kg'
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
                    old_quota_obj.remaining_quota += old_total_weight
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
                        old_quota_obj.remaining_quota += old_total_weight
                        old_quota_obj.save()
                    except ObjectDoesNotExist:
                        pass  # Old quota might not exist, that's ok

                # Deduct from new quota
                self._check_and_update_quota(new_ship, new_year, old_total_weight)

        return instance
