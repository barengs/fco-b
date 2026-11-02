"""
Owner Application Service (Application Layer)
Orchestrates business logic for vessel owners.
"""

from typing import Optional, List, Dict, Any
from django.apps import apps

from ..domain.owner_domain import OwnerDomain, OwnerDomainService


class OwnerApplicationService:
    """
    Application service for vessel owners.
    """

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = self._get_model("owners", "Owner")
        return self._model

    def _get_model(self, app_label: str, model_name: str):
        return apps.get_model(app_label, model_name)

    def get_all_owners(self) -> List[dict]:
        """Get all vessel owners."""
        owners = self.model.objects.all().order_by("full_name")
        return [self._to_dict(o) for o in owners]

    def get_owner_by_id(self, owner_id: int) -> Optional[dict]:
        """Get an owner by ID."""
        try:
            owner = self.model.objects.get(id=owner_id)
            return self._to_dict(owner)
        except self.model.DoesNotExist:
            return None

    def create_owner(self, full_name: str, email: str,
                    phone: str = "", address: str = "",
                    owner_type: str = "individual") -> dict:
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

        if not validation["is_valid"]:
            return {
                "success": False,
                "errors": validation["errors"]
            }

        formatted = OwnerDomainService.format_owner_data(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            owner_type=owner_type
        )

        if self.model.objects.filter(email=formatted["email"]).exists():
            return {
                "success": False,
                "errors": [f"Email '{formatted['email']}' sudah terdaftar"]
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
