# qr_gen_app/forms.py
from django import forms
from .models import QRCodeEntry # oder wie dein Model heisst

class QRCodeForm(forms.ModelForm):
    class Meta:
        model = QRCodeEntry
        fields = ['url', 'qr_type', 'foreground_color', 'background_color', 'error_correction', 'box_size', 'border']
        
        # Hier stylen wir die Felder für Mobile
        widgets = {
            'url': forms.TextInput(attrs={
                'class': 'form-control form-control-lg', # <--- LG für Large
                'placeholder': 'https://www.beispiel.ch',
                'style': 'font-size: 1.1rem;' # Etwas grössere Schrift
            }),
            'qr_type': forms.Select(attrs={
                'class': 'form-select form-select-lg', # <--- LG für Select
            }),
            # Auch für die Color-Picker, falls du Textinputs nutzt:
            'foreground_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-lg form-control-color'}),
            'background_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-lg form-control-color'}),
        }