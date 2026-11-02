"""
Owner Application Service (Application Layer)
Orchestrates business logic for vessel owners (Pemilik Kapal).
"""

from typing import Optional, List, Dict, Any
from django.apps import apps

from ..domain.owner_domain import OwnerDomain, OwnerDomainService


class OwnerApplicationService:
    """
    Application service for vessel owners management.
    """

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = self._get_model('owners', 'Owner')
        return self._model

    def _get_model(self, app_label: str, model_name: str):
        return apps.get_model(app_label, model_name)

    def get_all_owners(self) -> List[dict]:
        """Get all vessel owners."""
        owners = self.model.objects.all().order_by('full_name')
        return [self._to_dict(o) for o in owners]

    def get_owner_by_id(self, owner_id: int) -> Optional[dict]:
        """Get an owner by ID."""
        try:
            owner = self.model.objects.get(id=owner_id)
            return self._to_dict(owner)
        except self.model.DoesNotExist:
            return None

    def create_owner(self, full_name: str, email: str,
                    phone: str = '', address: str = '',
                    owner_type: str = 'individual') -> dict:
        """
        Create a new owner with validation.
        """
        validation = OwnerDomainService.validate_owner_data(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            owner_type=owner_type
        )

        if not validation['is_valid']:
            return {
                'success': False,
                'errors': validation['errors']
            }

        formatted = OwnerDomainService.format_owner_data(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            owner_type=owner_type
        )

        if self.model.objects.filter(email=formatted['email']).exists():
            return {
                'success': False,
                'errors': [f"Email '{formatted['email']}' sudah terdaftar"]
            }

        try:
            owner = self.model.objects.create(
                full_name=formatted['full_name'],
                email=formatted['email'],
                phone=formatted['phone'],
                address=formatted['address'],
                owner_type=formatted['owner_type']
            )
            return {
                'success': True,
                'data': self._to_dict(owner)
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }

    def _to_dict(self, owner) -> dict:
        """Convert model instance to dictionary."""
        return {
            'id': owner.id,
            'full_name': owner.full_name,
            'email': owner.email,
            'phone': owner.phone,
            'address': owner.address,
            'owner_type': owner.owner_type,
            'is_active': owner.is_active,
        }

EOF

cat > /home/makdumibrohim/Projects/Web-Dev/modular/fco/fco-b/iot_scales/application/iot_device_service.py << 'EOF'
"""
IoT Device Application Service (Application Layer)
Orchestrates business logic for IoT scale devices.
"""

from typing import Optional, List, Dict, Any
from django.apps import apps

from ..domain.iot_device_domain import IoTDeviceDomain, IoTDeviceDomainService


class IoTDeviceApplicationService:
    """
    Application service for IoT device management.
    """

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = self._get_model('iot_scales', 'IoTDevice')
        return self._model

    def _get_model(self, app_label: str, model_name: str):
        return apps.get_model(app_label, model_name)

    def get_all_devices(self) -> List[dict]:
        """Get all IoT devices."""
        devices = self.model.objects.all().order_by('device_id')
        return [self._to_dict(d) for d in devices]

    def get_device_by_id(self, device_id: int) -> Optional[dict]:
        """Get an IoT device by ID."""
        try:
            device = self.model.objects.get(id=device_id)
            return self._to_dict(device)
        except self.model.DoesNotExist:
            return None

    def get_device_by_device_id(self, device_id: str) -> Optional[dict]:
        """Get an IoT device by device_id."""
        try:
            device = self.model.objects.get(device_id=device_id.strip().upper())
            return self._to_dict(device)
        except self.model.DoesNotExist:
            return None

    def create_device(self, device_id: str, name: str,
                     location: str = '') -> dict:
        """
        Create a new IoT device with validation.
        """
        validation = IoTDeviceDomainService.validate_device_data(
            device_id=device_id,
            name=name,
            location=location
        )

        if not validation['is_valid']:
            return {
                'success': False,
                'errors': validation['errors']
            }

        formatted = IoTDeviceDomainService.format_device_data(
            device_id=device_id,
            name=name,
            location=location
        )

        if self.model.objects.filter(device_id=formatted['device_id']).exists():
            return {
                'success': False,
                'errors': [f"Device ID '{formatted['device_id']}' sudah terdaftar"]
            }

        try:
            device = self.model.objects.create(
                device_id=formatted['device_id'],
                name=formatted['name'],
                location=formatted['location']
            )
            return {
                'success': True,
                'data': self._to_dict(device)
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }

    def _to_dict(self, device) -> dict:
        """Convert model instance to dictionary."""
        return {
            'id': device.id,
            'device_id': device.device_id,
            'name': device.name,
            'location': device.location,
            'is_active': device.is_active,
            'last_seen': device.last_seen.isoformat() if device.last_seen else None,
        }

EOF

echo "All application services created successfully"
