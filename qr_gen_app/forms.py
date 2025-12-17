from django import forms
from .models import QRCodeEntry

class QRCodeForm(forms.ModelForm):
    class Meta:
        model = QRCodeEntry
        fields = '__all__'
        widgets = {
            'qr_type': forms.RadioSelect(attrs={
                'class': 'btn-check', 
                'hx-get': '/get-form-fields/', 
                'hx-target': '#dynamic-fields',
                'hx-swap': 'innerHTML'
            }),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'bg_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'bottom_text_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color w-100'}),
            'module_style': forms.Select(attrs={'class': 'form-select'}),
            'frame_style': forms.RadioSelect(attrs={'class': 'btn-check'}), # Werden wir im Template custom stylen
            'logo_preset': forms.RadioSelect(attrs={'class': 'btn-check'}),
        }