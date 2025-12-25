from django.urls import path
from . import views

app_name = 'sync'

urlpatterns = [
    path('', views.sync_dashboard, name='dashboard'),
    path('account/<int:account_id>/start/', views.start_sync, name='start_sync'),
    path('account/<int:account_id>/status/', views.sync_status, name='sync_status'),
    path('account/<int:account_id>/history/', views.sync_history, name='sync_history'),
    path('account/<int:account_id>/emails/', views.email_list, name='email_list'),
    path('email/<int:email_id>/', views.email_detail, name='email_detail'),
]