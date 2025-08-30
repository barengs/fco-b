"""
URL patterns for blockchain functionality
"""

from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.blockchain_status, name='blockchain-status'),
    path('transactions/', views.blockchain_transactions, name='blockchain-transactions'),
    path('blocks/', views.blockchain_blocks, name='blockchain-blocks'),
]