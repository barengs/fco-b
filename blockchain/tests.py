"""
Tests for the blockchain module
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from ships.models import Ship
from owners.models import Owner
from fish.models import FishSpecies
from catches.models import FishCatch, CatchDetail
from .models import BlockchainBlock, FishCatchTransaction
from .utils import create_genesis_block, add_block_to_chain, create_fish_catch_transaction

class BlockchainTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test owner
        self.owner = Owner.objects.create(
            name='Test Owner',
            owner_type='individual'
        )
        
        # Create test ship
        self.ship = Ship.objects.create(
            name='Test Ship',
            registration_number='TS001',
            owner=self.owner
        )
        
        # Create test fish species
        self.fish_species = FishSpecies.objects.create(
            name='Test Fish',
            scientific_name='Testus Fishicus'
        )
        
        # Create test fish catch
        self.fish_catch = FishCatch.objects.create(
            ship=self.ship,
            catch_date='2023-01-01',
            catch_type='pelagic',
            location_latitude='1.234567',
            location_longitude='2.345678'
        )
        
        # Create test catch detail
        self.catch_detail = CatchDetail.objects.create(
            fish_catch=self.fish_catch,
            fish_species=self.fish_species,
            quantity=100.50,
            unit='kg'
        )

    def test_create_genesis_block(self):
        """Test creating the genesis block"""
        genesis_block = create_genesis_block()
        self.assertIsNotNone(genesis_block)
        self.assertEqual(genesis_block.index, 0)
        self.assertEqual(genesis_block.previous_hash, "0")
        self.assertIsNotNone(genesis_block.hash)

    def test_add_block_to_chain(self):
        """Test adding a block to the chain"""
        # Create genesis block first
        create_genesis_block()
        
        # Add a new block
        test_data = "Test block data"
        block = add_block_to_chain(test_data)
        
        self.assertIsNotNone(block)
        self.assertEqual(block.index, 1)
        self.assertEqual(block.data, test_data)
        self.assertIsNotNone(block.hash)

    def test_create_fish_catch_transaction(self):
        """Test creating a fish catch transaction"""
        # Create genesis block first
        create_genesis_block()
        
        # Create a fish catch transaction
        transaction = create_fish_catch_transaction(self.fish_catch, self.catch_detail)
        
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.ship_registration_number, self.ship.registration_number)
        self.assertEqual(transaction.fish_species_code, self.fish_species.name)
        self.assertEqual(transaction.fish_name, self.fish_species.name)
        self.assertEqual(transaction.quantity, self.catch_detail.quantity)
        self.assertEqual(transaction.unit, self.catch_detail.unit)
        
        # Check that the transaction was saved to the database
        self.assertTrue(FishCatchTransaction.objects.filter(id=transaction.id).exists())
        
        # Check that a block was created
        self.assertTrue(BlockchainBlock.objects.filter(id=transaction.block.id).exists())