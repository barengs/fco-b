"""
Management command to initialize the blockchain
"""

from django.core.management.base import BaseCommand
from blockchain.utils import create_genesis_block

class Command(BaseCommand):
    help = 'Initialize the blockchain with a genesis block'

    def handle(self, *args, **options):
        self.stdout.write('Initializing blockchain...')
        
        # Create the genesis block
        genesis_block = create_genesis_block()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created genesis block with hash: {genesis_block.hash}'
            )
        )