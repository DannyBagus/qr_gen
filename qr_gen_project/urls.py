from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from qr_gen_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('get-form-fields/', views.get_form_fields, name='get_form_fields'),
    path('generate/', views.generate_qr, name='generate_qr'),
    path('preview/', views.preview_qr, name='preview_qr'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)