import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from tickets.models import Ticket
from .models import ChatMessage
from django.contrib.auth.models import AnonymousUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ticket_id = self.scope['url_route']['kwargs']['ticket_id']
        self.room_group_name = f'chat_{self.ticket_id}'
        self.user = self.scope['user']

        if isinstance(self.user, AnonymousUser):
            await self.close(code=4001)
            return

        has_access = await self.check_ticket_access()
        if not has_access:
            await self.close(code=4003)
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')

        if not message:
            return

        # Save message to database
        saved_msg = await self.save_message(message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': saved_msg.id,
                'message': saved_msg.message,
                'sender_id': saved_msg.sender.id,
                'sender_name': saved_msg.sender.name,
                'created_at': saved_msg.created_at.isoformat()
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'created_at': event['created_at']
        }))

    @database_sync_to_async
    def check_ticket_access(self):
        try:
            ticket = Ticket.objects.get(id=self.ticket_id)
            if ticket.status == 'open':
                return False
            if ticket.user == self.user or ticket.assigned_technician == self.user:
                return True
            return False
        except Ticket.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, message):
        from authsystem.utils import create_and_send_notification
        ticket = Ticket.objects.get(id=self.ticket_id)
        msg = ChatMessage.objects.create(ticket=ticket, sender=self.user, message=message)
        
        # Determine the recipient
        recipient = ticket.assigned_technician if self.user == ticket.user else ticket.user
        if recipient:
            link = f"/dashboard/technician/ticket/{ticket.id}" if recipient.role == 'technician' else f"/dashboard/customer/ticket/{ticket.id}"
            create_and_send_notification(
                user=recipient,
                message=f"New message from {self.user.name} on Ticket #{ticket.id}",
                link=link
            )
            
        return msg
