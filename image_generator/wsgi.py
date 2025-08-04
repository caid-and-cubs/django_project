"""
WSGI config for image_generator project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'image_generator.settings')

# For Vercel deployment, use production settings if specified
if 'VERCEL' in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'image_generator.settings_production')

application = get_wsgi_application()

# Vercel compatibility
app = application
