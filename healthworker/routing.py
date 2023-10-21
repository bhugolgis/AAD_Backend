from django.urls import path , re_path
from . import consumers
from channels.auth import AuthMiddlewareStack

websocket_urlpatterns = [
    path('ws/sc/' , consumers.MySyncConsumer.as_asgi()),
    path('ws/ac/' , consumers.MyAsyncConsumer.as_asgi()),
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
]