from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging

logger = logging.getLogger(__name__)

class ScoreConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.competition_code = self.scope['url_route']['kwargs']['competition_code']
        self.group_name = f"competition_{self.competition_code}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def score_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

