from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from myapp.consumers import ProfileConsumer
from channels.auth import AuthMiddlewareStack

websocket_urlpatterns = [
    path("ws/profile/", ProfileConsumer.as_asgi()),
]

application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns),
        ),
    }
)
