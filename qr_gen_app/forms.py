from django import forms
from .models import QRCodeEntry

class QRCodeForm(forms.ModelForm):
    
    class Meta:
        model = QRCodeEntry
        fields = [
            'qr_type', 'url', 'ssid', 'password', 'security', 'text_content',
            'vcard_name', 'vcard_email', 'vcard_phone', 'vcard_org',
            'module_style', 'foreground_color', 'background_color', 
            'box_size', 'border', 'error_correction',
            'frame_style', 'logo', 'logo_preset',
            'bottom_text', 'bottom_text_color', 'bottom_text_size', 'text_font'
        ]
        
        widgets = {
            # WICHTIG FÜR PROBLEM 1: 'btn-check' macht die Radio Buttons unsichtbar,
            # damit unsere Kacheln (Labels) funktionieren.
            'qr_type': forms.RadioSelect(attrs={
                            'class': 'btn-check',
                            'hx-get': '/form-fields/',      # URL aufrufen
                            'hx-target': '#dynamic-fields', # Wohin mit dem HTML?
                            'hx-swap': 'innerHTML'          # Inhalt ersetzen
                        }),
            
            # Styles für Mobile First (Große Felder)
            'url': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'https://...'}),
            'ssid': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'password': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            
            # WICHTIG FÜR PROBLEM 2: Mapping auf die NEUEN Namen (foreground_color)
            'foreground_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-lg form-control-color'}),
            'background_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-lg form-control-color'}),
            'bottom_text_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-lg form-control-color'}),
            
            # Weitere Felder
            'frame_style': forms.RadioSelect(attrs={'class': 'btn-check'}),
            'logo_preset': forms.RadioSelect(attrs={'class': 'btn-check'}),
            'module_style': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'text_font': forms.Select(attrs={'class': 'form-select form-select-lg'}),
        }