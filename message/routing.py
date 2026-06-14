from django.urls import re_path
from . import consumers

from authsystem.consumers import NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<ticket_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
]
