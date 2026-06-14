from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from .serializers import NotificationSerializer

def create_and_send_notification(user, message, link=None):
    # 1. Save to DB
    notification = Notification.objects.create(
        user=user,
        message=message,
        link=link
    )
    
    # 2. Broadcast via WebSocket
    channel_layer = get_channel_layer()
    if channel_layer:
        group_name = f'notifications_{user.id}'
        serializer = NotificationSerializer(notification)
        
        try:
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification',
                    'notification': serializer.data
                }
            )
        except RuntimeError:
            import asyncio
            # Fallback if we are already inside an async context or thread-sensitive sync_to_async
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(channel_layer.group_send(
                    group_name,
                    {
                        'type': 'send_notification',
                        'notification': serializer.data
                    }
                ))
            except Exception as e:
                print("Failed to send websocket notification:", e)
        except Exception as e:
            print("Failed to send websocket notification:", e)
    
    return notification
