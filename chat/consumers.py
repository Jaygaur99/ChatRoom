import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatModel
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Layer is to be created
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_' + str(self.room_name)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @database_sync_to_async
    def save_to_db(self, message):
        ChatModel(room_no=self.room_name, message=message).save()

    async def receive(self, text_data):
        test_data_json = json.loads(text_data)
        message = test_data_json['message']
        # await sync_to_async(ChatModel(room_no=self.room_name, message=message).save())
        await self.save_to_db(message)
        await self.channel_layer.group_send(self.room_group_name, {
            'type' : 'send_back',
            'message': message
        })
    
    async def send_back(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))
    