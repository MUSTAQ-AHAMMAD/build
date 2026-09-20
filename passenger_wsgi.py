import os
import sys

# Determine the absolute directory of this file
app_dir = os.path.dirname(__file__)

# Add the application directory to the Python path if not already present
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_config.settings')

# Import and expose the WSGI application for Phusion Passenger
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
