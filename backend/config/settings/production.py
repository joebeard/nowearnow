from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

if len(SECRET_KEY) < 50 or len(set(SECRET_KEY)) < 5:  # noqa: F405
    raise ImproperlyConfigured("Production requires a strong DJANGO_SECRET_KEY (50+ characters).")
if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:  # noqa: F405
    raise ImproperlyConfigured("Production requires explicit DJANGO_ALLOWED_HOSTS.")
# Database, hosting, proxy trust and deployment are intentionally not configured yet.
raise ImproperlyConfigured("Production deployment is not configured. See docs/PRIVACY.md.")
