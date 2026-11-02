"""
User Profile Domain Model (Authentication Domain Layer)
Domain model for user profile information across different roles.
"""


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
