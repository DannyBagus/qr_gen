from django.db import models

class QRCodeEntry(models.Model):
    QR_TYPES = [
        ('website', 'Webseite'),
        ('wifi', 'WLAN / WIFI'),
        ('text', 'Freitext'),
        ('vcard', 'Digitale Visitenkarte'),
    ]
    
    STYLE_CHOICES = [
        ('square', 'Klassisch (Quadrate)'),
        ('rounded', 'Abgerundet (Soft)'),
        ('circle', 'Punkte (Dots)'),
        ('diamond', 'Diamanten'),
        ('stripe_h', 'Streifen (H)'),
    ]

    FRAME_CHOICES = [
        ('none', 'Kein Rahmen'),
        ('simple', 'Einfacher Rand'),
        ('polaroid', 'Polaroid'),
        ('phone', 'Smartphone Look'),
        ('heavy', 'Fetter Rahmen'),
    ]

    LOGO_PRESETS = [
        ('none', 'Kein / Eigenes Upload'),
        ('wifi', 'WLAN Symbol'),
        ('email', 'E-Mail Symbol'),
        ('whatsapp', 'WhatsApp'),
        ('link', 'Link / Weltkugel'),
    ]
    
    FONT_CHOICES = [
        ('arial.ttf', 'Standard (Arial)'),
        ('roboto.ttf', 'Modern (Roboto)'),
        ('caveat.ttf', 'Handschrift (Caveat)'),
    ]

    # --- BASIS DATEN ---
    qr_type = models.CharField(max_length=20, choices=QR_TYPES, default='website')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Inhaltliche Felder
    url = models.URLField(blank=True, null=True)
    ssid = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    security = models.CharField(max_length=10, default='WPA', blank=True, null=True, choices=[('WPA', 'WPA/WPA2'), ('nopass', 'Offen')])
    text_content = models.TextField(blank=True, null=True)
    vcard_name = models.CharField(max_length=100, blank=True, null=True)
    vcard_email = models.EmailField(blank=True, null=True)
    vcard_phone = models.CharField(max_length=50, blank=True, null=True)
    vcard_org = models.CharField(max_length=100, blank=True, null=True)

    # --- DESIGN ---
    module_style = models.CharField(max_length=20, choices=STYLE_CHOICES, default='square', verbose_name="Muster")
    color = models.CharField(max_length=7, default='#000000', verbose_name="Code Farbe")
    bg_color = models.CharField(max_length=7, default='#ffffff', verbose_name="Hintergrund")
    scale = models.IntegerField(default=10) # Wird versteckt behandelt oder via Slider
    
    # Rahmen & Frames
    frame_style = models.CharField(max_length=20, choices=FRAME_CHOICES, default='none', verbose_name="Rahmen Art")
    
    # Logos
    logo = models.ImageField(upload_to='qr_logos/', blank=True, null=True, verbose_name="Eigenes Logo")
    logo_preset = models.CharField(max_length=20, choices=LOGO_PRESETS, default='none', verbose_name="Preset Logo")

    # TEXT OPTIONEN UPDATE
    bottom_text = models.CharField(max_length=50, blank=True, null=True, verbose_name="Text Inhalt")
    bottom_text_color = models.CharField(max_length=7, default='#000000', verbose_name="Text Farbe")
    bottom_text_size = models.IntegerField(default=35, verbose_name="Schriftgröße")
    
    # NEUES FELD
    text_font = models.CharField(max_length=50, choices=FONT_CHOICES, default='arial.ttf', verbose_name="Schriftart")   

    def __str__(self):
        return f"{self.qr_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"