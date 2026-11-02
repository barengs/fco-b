"""
User Role Domain Model (Authentication Domain Layer)
Defines user role domain logic and business rules for user role management.
"""

from typing import List, Optional


class UserRole:
    """Domain model for user roles in the FishPro system."""

    ROLE_SUPERADMIN = 'superadmin'
    ROLE_ADMIN = 'admin'
    ROLE_REGULATOR = 'regulator'
    ROLE_OWNER = 'owner'
    ROLE_CAPTAIN = 'captain'
    ROLE_USER = 'user'

    ALL_ROLES = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_REGULATOR, ROLE_OWNER, ROLE_CAPTAIN, ROLE_USER]

    @classmethod
    def is_admin_role(cls, role: str) -> bool:
        """Check if role is an admin role."""
        return role in (cls.ROLE_ADMIN, cls.ROLE_SUPERADMIN)

    @classmethod
    def is_superadmin(cls, role: str) -> bool:
        """Check if role is superadmin."""
        return role == cls.ROLE_SUPERADMIN

    @classmethod
    def is_regulator(cls, role: str) -> bool:
        """Check if role is regulator."""
        return role == cls.ROLE_REGULATOR

    @classmethod
    def is_owner(cls, role: str) -> bool:
        """Check if role is owner."""
        return role == cls.ROLE_OWNER

    @classmethod
    def is_captain(cls, role: str) -> bool:
        """Check if role is captain."""
        return role == cls.ROLE_CAPTAIN

    @classmethod
    def get_display_name(cls, role: str) -> str:
        """Get human-readable display name for a role."""
        display_names = {
            cls.ROLE_SUPERADMIN: 'Super Administrator',
            cls.ROLE_ADMIN: 'Staf Administrator',
            cls.ROLE_REGULATOR: 'Pengawas / Regulator',
            cls.ROLE_OWNER: 'Pemilik Kapal',
            cls.ROLE_CAPTAIN: 'Nahkoda',
            cls.ROLE_USER: 'Pengguna',
        }
        return display_names.get(role, role)


class UserProfile:
    """Domain model for user profile information."""

    def __init__(self, user_type: str, full_name: str = '', email: str = '',
                 phone: str = '', department: str = '', position: str = '',
                 owner_type: str = '', address: str = '',
                 license_number: str = '', years_of_experience: int = 0):
        self.user_type = user_type
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.address = address
        self.department = department
        self.position = position
        self.owner_type = owner_type
        self.license_number = license_number
        self.years_of_experience = years_of_experience

    def to_dict(self) -> dict:
        """Convert profile to dictionary for API response."""
        return {
            'type': self.user_type,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'department': self.department,
            'position': self.position,
            'owner_type': self.owner_type,
            'license_number': self.license_number,
            'years_of_experience': self.years_of_experience,
        }
