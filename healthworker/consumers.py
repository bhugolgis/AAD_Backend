from channels.consumer import SyncConsumer , AsyncConsumer 
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
import json
from database.models import CustomUser
from django.core.exceptions import ObjectDoesNotExist
from channels.exceptions import DenyConnection
from datetime import timezone
class MySyncConsumer(SyncConsumer):
    def websocket_connect(self , event):
        print("Websocket Connected" , event)
        # try:
        #     self.game = CustomUser.objects.get(pk=self.room_name)
        # except ObjectDoesNotExist:
        #     raise DenyConnection("Invalid Id")
        
        # await self.accept()
            # self.send({
            #     'type' : 'websocket.accept'
            # })


    def websocket_receive(self , event):
        print('Message recieved' , event['text'])

    def websocket_disconnect(self , event):
        print('Websocket Disconnected' , event)
        raise StopConsumer()
    

class MyAsyncConsumer(AsyncConsumer):
    async def websocket_connect(self , event):
        print("Websocket Connected" , event)

        try:
            self.game = CustomUser.objects.get(pk=100)
        except ObjectDoesNotExist:
            raise DenyConnection("Invalid Id")
        
        await self.send({
                'type' : 'websocket.accept'
            })
 
    # async def websocket_receive(self , event):
    #     print('Message recieved' , event['text'])

    async def websocket_receive(self, text_data):
       game_city = json.loads(text_data).get('game_city')
       print(game_city)
    #    await self.channel_layer.group_send(
    #         self.room_group_name,
    #         {
    #             'type': 'live_score',
    #             'game_id': self.room_name,
    #             'game_city': game_city
    #         }
    #     )
    # async def live_score(self, event):
    #     city = event['game_city']
    #     # Here helper function fetches live score from DB.
    #     await self.send(text_data=json.dumps({
    #             'score': get_data_from_DB(self.game, city)
    #         }))

    async def websocket_disconnect(self , event):
        print('Websocket Disconnected' , event)
        raise StopConsumer()
        

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # text_data_json = json.loads(text_data)
        # print(text_data_json)
        print(text_data)
        message = text_data
        

        await self.send(text_data=json.dumps({
            'message': message
        }))