#!/bin/bash
# Start Django server with Daphne for WebSocket support
# Make sure you're in the backend directory

echo "Starting Django server with Daphne (WebSocket support)..."
echo ""
echo "IMPORTANT: Use Daphne instead of 'python manage.py runserver' for WebSocket support"
echo ""

# Start with Daphne (ASGI server)
daphne -b 0.0.0.0 -p 8000 core.asgi:application

# Alternative: If you want to use runserver (no WebSocket support):
# python manage.py runserver 0.0.0.0:8000

