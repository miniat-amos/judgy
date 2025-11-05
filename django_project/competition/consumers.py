import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class ScoreConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from competition.models import Team
        
        self.competition_code = self.scope['url_route']['kwargs']['competition_code']
        self.user = self.scope['user']
        
        team = await database_sync_to_async(lambda: Team.objects.filter(competition=self.competition_code ,members=self.user).first())()
        self.team_id = team.id if team else None
        
        await self.channel_layer.group_add(
            f"competition_{self.competition_code}", self.channel_name
        )
        
        if self.team_id:
            await self.channel_layer.group_add(f"team_{self.team_id}", self.channel_name)
            await self.channel_layer.group_add(f"user_{self.user.id}", self.channel_name)

        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"competition_{self.competition_code}", self.channel_name
        )
        if self.team_id:
            await self.channel_layer.group_discard(f"team_{self.team_id}", self.channel_name)
            await self.channel_layer.group_discard(f"user_{self.user.id}", self.channel_name)

    async def score_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

