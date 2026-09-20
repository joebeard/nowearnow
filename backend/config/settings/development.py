from .base import *  # noqa: F403

SECRET_KEY = "local-development-only-never-use-in-production"
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", *ALLOWED_HOSTS]  # noqa: F405

CSRF_TRUSTED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173", PUBLIC_BASE_URL]  # noqa: F405
