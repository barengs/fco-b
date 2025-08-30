"""
Management command to verify the blockchain integrity
"""

from django.core.management.base import BaseCommand
from blockchain.utils import verify_blockchain

class Command(BaseCommand):
    help = 'Verify the integrity of the blockchain'

    def handle(self, *args, **options):
        self.stdout.write('Verifying blockchain integrity...')
        
        # Verify the blockchain
        is_valid, message = verify_blockchain()
        
        if is_valid:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Blockchain verification successful: {message}'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f'Blockchain verification failed: {message}'
                )
            )