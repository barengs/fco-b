"""
Views for blockchain functionality
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .models import FishCatchTransaction, BlockchainBlock
from .utils import verify_blockchain
from .serializers import FishCatchTransactionSerializer, BlockchainBlockSerializer

@extend_schema(
    tags=['Blockchain'],
    summary='Get Blockchain Status',
    description='Retrieve the status and verification of the blockchain'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def blockchain_status(request):
    """Get the status and verification of the blockchain"""
    try:
        is_valid, message = verify_blockchain()
        block_count = BlockchainBlock.objects.count()
        transaction_count = FishCatchTransaction.objects.count()
        
        return Response({
            'valid': is_valid,
            'message': message,
            'block_count': block_count,
            'transaction_count': transaction_count
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(
    tags=['Blockchain'],
    summary='Get All Blockchain Transactions',
    description='Retrieve all fish catch transactions recorded in the blockchain'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def blockchain_transactions(request):
    """Get all fish catch transactions recorded in the blockchain"""
    try:
        transactions = FishCatchTransaction.objects.select_related('block').all()
        serializer = FishCatchTransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(
    tags=['Blockchain'],
    summary='Get Blockchain Blocks',
    description='Retrieve all blocks in the blockchain'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def blockchain_blocks(request):
    """Get all blocks in the blockchain"""
    try:
        blocks = BlockchainBlock.objects.all()
        serializer = BlockchainBlockSerializer(blocks, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )