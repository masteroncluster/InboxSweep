from django.urls import path
from . import views

app_name = 'sync'

urlpatterns = [
    path('', views.SyncDashboardView.as_view(), name='dashboard'),
    path('account/<int:account_id>/start/', views.StartSyncView.as_view(), name='start_sync'),
    path('account/<int:account_id>/status/', views.SyncStatusView.as_view(), name='sync_status'),
    path('account/<int:account_id>/history/', views.SyncHistoryView.as_view(), name='sync_history'),
    path('account/<int:account_id>/emails/', views.EmailListView.as_view(), name='email_list'),
    path('email/<int:email_id>/', views.EmailDetailView.as_view(), name='email_detail'),
]