from django.urls import path
from . import views

app_name = 'oauth'

urlpatterns = [
    path('connect/<str:provider>/', views.OAuthConnectView.as_view(), name='connect'),
    path('callback/', views.OAuthCallbackView.as_view(), name='callback'),
    path('connections/', views.OAuthConnectionsView.as_view(), name='connections'),
    path('disconnect/<int:connection_id>/', views.OAuthDisconnectView.as_view(), name='disconnect'),
    path('webhook/<str:provider>/', views.OAuthWebhookView.as_view(), name='webhook'),
]