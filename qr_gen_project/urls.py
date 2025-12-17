from django.contrib import admin
from django.urls import path, include  # <--- 'include' ist wichtig!

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Wir delegieren alles (den leeren String '') an die qr_gen_app
    path('', include('qr_gen_app.urls')),
]