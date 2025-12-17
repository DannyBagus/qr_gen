from .base import *
import os

DEBUG = int(os.environ.get("DEBUG", 0))

# Hosts strikt aus ENV lesen
allowed_hosts_env = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost")
ALLOWED_HOSTS = allowed_hosts_env.split(",")

# CSRF Trusted Origins (WICHTIG für Traefik)
# Erwartet Format: https://qr.raowy.ch,https://...
csrf_trusted = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
if csrf_trusted:
    CSRF_TRUSTED_ORIGINS = csrf_trusted.split(",")

# Security Settings für HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# ALT (Streng):
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# NEU (Tolerant - gut zum Debuggen):
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'