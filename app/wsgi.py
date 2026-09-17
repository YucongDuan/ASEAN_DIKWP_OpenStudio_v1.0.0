"""For a campus WSGI host. Set OPENSTUDIO_ORIGIN to the public HTTPS origin."""
from .server import Application
application = Application()
