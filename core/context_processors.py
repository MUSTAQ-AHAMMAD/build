from .models import WebsiteSettings

def global_website_settings(request):
    try:
        settings = WebsiteSettings.load()
    except Exception:
        settings = None
    return {
        'site_settings': settings,
    }
