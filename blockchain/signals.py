"""
Signals for automatically adding fish catch reports to the blockchain
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from catches.models import CatchDetail
from .utils import create_fish_catch_transaction

@receiver(post_save, sender=CatchDetail)
def add_catch_to_blockchain(sender, instance, created, **kwargs):
    """Add a fish catch report to the blockchain when a CatchDetail is created"""
    if created:
        try:
            # Create blockchain transaction for this catch detail
            create_fish_catch_transaction(instance.fish_catch, instance)
        except Exception as e:
            # Log the error but don't stop the save operation
            print(f"Error adding catch to blockchain: {e}")
            # In production, you might want to use proper logging
            pass