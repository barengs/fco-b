"""
Views for blockchain functionality (Presentation Layer)
Delegates blockchain operations to BlockchainApplicationService.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .application.blockchain_service import BlockchainApplicationService
from .serializers import FishCatchTransactionSerializer, BlockchainBlockSerializer

_blockchain_service = BlockchainApplicationService()


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
        data = _blockchain_service.get_status()
        return Response(data)
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
        transactions = _blockchain_service.get_transactions_queryset()
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
        blocks = _blockchain_service.get_blocks_queryset()
        serializer = BlockchainBlockSerializer(blocks, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
