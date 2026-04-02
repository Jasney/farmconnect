"""ASGI config for farm_connect_platform project.

It exposes the ASGI callable as a module-level variable named `application`.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from channels.routing import get_default_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_connect_platform.settings')

application = get_default_application()

