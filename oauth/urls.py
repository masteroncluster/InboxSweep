from django.urls import path
from . import views

app_name = 'oauth'

urlpatterns = [
    path('connect/<str:provider>/', views.oauth_connect, name='connect'),
    path('callback/', views.oauth_callback, name='callback'),
    path('connections/', views.oauth_connections, name='connections'),
    path('disconnect/<int:connection_id>/', views.oauth_disconnect, name='disconnect'),
    path('webhook/<str:provider>/', views.oauth_webhook, name='webhook'),
]