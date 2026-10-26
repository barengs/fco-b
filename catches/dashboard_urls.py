from django.urls import path
from . import dashboard_views

urlpatterns = [
    path('admin/', dashboard_views.admin_dashboard_summary, name='dashboard-admin-summary'),
    path('regulator/', dashboard_views.regulator_dashboard_summary, name='dashboard-regulator-summary'),
    path('owner/', dashboard_views.owner_dashboard_summary, name='dashboard-owner-summary'),
    path('captain/', dashboard_views.captain_dashboard_summary, name='dashboard-captain-summary'),
]
