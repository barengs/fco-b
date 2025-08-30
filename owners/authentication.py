from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from ships.models import Ship

User = get_user_model()

class ShipNumberOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in with either:
    1. Their username
    2. Their ship registration number (for captains or owners associated with ships)
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
            
        try:
            # First, try to find a user with the provided username
            user = User._default_manager.get(username=username)
        except User.DoesNotExist:
            # If not found, check if it's a ship registration number
            try:
                ship = Ship._default_manager.get(registration_number=username)
                # Get the owner or captain associated with this ship
                if ship.owner and ship.owner.user:
                    user = ship.owner.user
                elif ship.captain and ship.captain.user:
                    user = ship.captain.user
                else:
                    return None
            except ObjectDoesNotExist:
                return None
        
        # Check the password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            return User._default_manager.get(pk=user_id)
        except User.DoesNotExist:
            return None