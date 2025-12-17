from .base import *

# In Local immer Debug an
DEBUG = True

# Alle Hosts erlauben
ALLOWED_HOSTS = ["*"]

# Keine strikte SSL Prüfung lokal
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Console Email Backend (schickt E-Mails in die Konsole statt ins Netz)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'