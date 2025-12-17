from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('preview/', views.preview_qr, name='preview_qr'),
    path('generate/', views.generate_qr, name='generate_qr'),
    path('pdf/', views.generate_pdf, name='generate_pdf'),
    
    # NEU: Dieser Pfad fehlte!
    path('form-fields/', views.get_form_fields, name='form_fields'),
]