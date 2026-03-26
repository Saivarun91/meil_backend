"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from requests.consumers import ChatConsumer  # WebSocket consumer for chat

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# HTTP + WebSocket handling
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/chat/<str:request_id>/", ChatConsumer.as_asgi()),
        ])
    ),
})
