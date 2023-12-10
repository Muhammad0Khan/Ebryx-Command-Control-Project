import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from myapp.models import RemoteCPUInfo


@database_sync_to_async
def import_remote_cpu_info():
    from myapp.models import RemoteCPUInfo

    return RemoteCPUInfo


class ProfileConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        user = self.scope["user"]
        if user.is_staff:
            await self.channel_layer.group_add(
                group="admin_group",
                channel=self.channel_name,
            )

    async def disconnect(self, close_code):
        user = self.scope["user"]
        if user.is_staff:
            await self.channel_layer.group_discard(
                group="admin_group",
                channel=self.channel_name,
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        pc_name = data["pc_name"]
        user = self.scope["user"]

        if user.is_staff:
            RemoteCPUInfo = await import_remote_cpu_info()
            cpu_info = await self.get_cpu_info(pc_name, RemoteCPUInfo)
            await self.send(
                text_data=json.dumps(
                    {
                        "cpu_info": cpu_info,
                    }
                )
            )
        else:
            pass

    @database_sync_to_async
    def get_cpu_info(self, pc_name, RemoteCPUInfo):
        cpu_info = RemoteCPUInfo.objects.filter(pc_name=pc_name).first()
        return {
            "remote_ip": cpu_info.remote_ip,
            "pc_name": cpu_info.pc_name,
            "timestamp": cpu_info.timestamp,
            "cpu_count": cpu_info.cpu_count,
            "cpu_percent": cpu_info.cpu_percent,
            "cpu_freq_value": cpu_info.cpu_freq,
            "threads": cpu_info.threads,
            "per_cpu_percent": cpu_info.per_cpu_percent,
        }
