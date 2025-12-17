import segno
from segno import helpers
import base64
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.staticfiles import finders
from .forms import QRCodeForm
from .models import QRCodeEntry

def _create_qr_image(instance):
    """
    Zentrale Funktion zum Zeichnen des QR Codes.
    Wird für Preview UND Download genutzt.
    """
    
    # --- 1. DATEN PAYLOAD GENERIEREN ---
    content_data = ""
    error_lvl = 'h' # Immer High Error Correction für Logos
    
    # Helper Variablen (None-Safety)
    ssid = instance.ssid or ""
    password = instance.password or ""
    security = instance.security or "WPA"
    url = instance.url or "https://example.com"
    text = instance.text_content or "Text"

    try:
        if instance.qr_type == 'wifi':
            content_data = helpers.make_wifi_data(ssid=ssid, password=password, security=security)
        elif instance.qr_type == 'vcard':
            content_data = helpers.make_vcard_data(
                name=instance.vcard_name or "Name",
                displayname=instance.vcard_name,
                email=instance.vcard_email,
                phone=instance.vcard_phone,
                org=instance.vcard_org
            )
        elif instance.qr_type == 'website':
            content_data = url
        elif instance.qr_type == 'text':
            content_data = text
    except Exception as e:
        print(f"Datenfehler: {e}")
        content_data = "Error"

    # QR Code Objekt erstellen
    qr = segno.make(content_data, error=error_lvl)

    # --- 2. BASIS ZEICHNEN (Pillow) ---
    scale = instance.scale if instance.scale else 10
    matrix = qr.matrix
    width_modules = len(matrix)
    img_size = width_modules * scale
    
    bg_color = instance.bg_color or "#ffffff"
    fg_color = instance.color or "#000000"
    
    img = Image.new("RGBA", (img_size, img_size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Module zeichnen
    for y, row in enumerate(matrix):
        for x, col in enumerate(row):
            if col: # Modul ist schwarz
                x0, y0 = x * scale, y * scale
                x1, y1 = x0 + scale, y0 + scale
                
                style = instance.module_style
                
                if style == 'circle':
                    draw.ellipse([x0, y0, x1, y1], fill=fg_color)
                elif style == 'rounded':
                    r = int(scale * 0.4)
                    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fg_color)
                elif style == 'diamond':
                    draw.polygon([(x0+scale/2, y0), (x1, y0+scale/2), (x0+scale/2, y1), (x0, y0+scale/2)], fill=fg_color)
                elif style == 'stripe_h':
                    margin = scale * 0.1
                    draw.rectangle([x0, y0 + margin, x1, y1 - margin], fill=fg_color)
                else: 
                    # Default Square
                    draw.rectangle([x0, y0, x1, y1], fill=fg_color)

    # --- 3. LOGO HANDLING ---
    logo_img = None
    
    # A. Eigenes Logo hat Vorrang
    if instance.logo:
        try:
            # .seek(0) ist wichtig, falls das File schonmal gelesen wurde
            if hasattr(instance.logo, 'seek'): instance.logo.seek(0)
            logo_img = Image.open(instance.logo).convert("RGBA")
        except Exception as e:
            print(f"Logo Upload Error: {e}")

    # B. Preset Logo (wenn kein eigenes)
    elif instance.logo_preset and instance.logo_preset != 'none':
        filename = f"{instance.logo_preset}.png"
        # Suche im Static Folder via Django Finders
        path = finders.find(f"qr_gen_app/assets/{filename}")
        if path:
            try:
                logo_img = Image.open(path).convert("RGBA")
            except: pass

    # C. Logo einfügen
    if logo_img:
        # Max 25% der QR Größe
        max_size = int(img.width * 0.25)
        logo_img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        pos = ((img.width - logo_img.width) // 2, (img.height - logo_img.height) // 2)
        img.paste(logo_img, pos, logo_img)


    # --- 4. RAHMEN (FRAMES) ---
    final_img = img
    
    if instance.frame_style == 'simple':
        border_w = scale * 2
        final_img = ImageOps.expand(final_img, border=border_w, fill=fg_color)
        final_img = ImageOps.expand(final_img, border=int(scale), fill=bg_color)

    elif instance.frame_style == 'heavy':
        border_w = scale * 4
        final_img = ImageOps.expand(final_img, border=border_w, fill=fg_color)

    elif instance.frame_style == 'polaroid':
        border_side = scale * 2
        border_bottom = scale * 12 # Platz für Text unten
        
        w, h = final_img.size
        new_w = w + (border_side * 2)
        new_h = h + border_side + border_bottom
        
        canvas = Image.new("RGBA", (new_w, new_h), "#ffffff")
        draw_canv = ImageDraw.Draw(canvas)
        draw_canv.rectangle([0,0,new_w-1, new_h-1], outline="#eeeeee", width=1)
        
        canvas.paste(final_img, (border_side, border_side))
        final_img = canvas
        
    elif instance.frame_style == 'phone':
        border = scale * 3
        w, h = final_img.size
        new_w = w + (border * 2)
        new_h = h + (border * 4)
        
        canvas = Image.new("RGBA", (new_w, new_h), (0,0,0,0)) # Transparent außen
        draw_canv = ImageDraw.Draw(canvas)
        
        # Handy Body (Dunkelgrau)
        draw_canv.rounded_rectangle([0,0, new_w, new_h], radius=scale*4, fill="#212529")
        # Screen (Hintergrundfarbe)
        draw_canv.rectangle([border, border*2, new_w-border, new_h-border*2], fill=bg_color)
        
        canvas.paste(final_img, (border, border*2), final_img)
        final_img = canvas


    # --- 5. TEXT ---
    if instance.bottom_text:
        font_size = instance.bottom_text_size or 35
        text_col = instance.bottom_text_color or "#000000"
        
        # Font laden
        font = None
        font_filename = instance.text_font or 'arial.ttf'
        
        # Versuch 1: Aus Assets
        font_path = finders.find(f"qr_gen_app/assets/fonts/{font_filename}")
        if font_path:
            try: font = ImageFont.truetype(font_path, font_size)
            except: pass
            
        # Versuch 2: System
        if font is None:
            try: font = ImageFont.truetype(font_filename, font_size)
            except: font = ImageFont.load_default()

        # Text Zeichnen
        if instance.frame_style == 'polaroid':
            # Direkt auf Polaroid Rand
            draw = ImageDraw.Draw(final_img)
            w, h = final_img.size
            draw.text((w/2, h - (scale * 6)), instance.bottom_text, fill=text_col, font=font, anchor="mm")
            
        else:
            # Canvas vergrößern
            try:
                ascent, descent = font.getmetrics()
                text_h = ascent + descent + (font_size * 0.6)
            except:
                text_h = font_size + 30
            
            w, h = final_img.size
            canvas = Image.new("RGBA", (w, int(h + text_h)), bg_color)
            canvas.paste(final_img, (0,0))
            
            draw = ImageDraw.Draw(canvas)
            draw.text((w/2, h + (text_h/2) - 5), instance.bottom_text, fill=text_col, font=font, anchor="mm")
            final_img = canvas

    # --- 6. FINALE KONVERTIERUNG (RGB für JPEG) ---
    background = Image.new("RGB", final_img.size, (255,255,255))
    # Alpha Composite (Transparenz auf Weiß kleben)
    background.paste(final_img, (0, 0), final_img)
    
    return background


# --- VIEWS ---

def index(request):
    form = QRCodeForm(initial={
        'qr_type': 'website', 
        'scale': 10, 
        'module_style': 'square', 
        'color': '#000000', 
        'bottom_text_size': 35
    })
    return render(request, 'index.html', {'form': form})

def get_form_fields(request):
    qr_type = request.GET.get('qr_type', 'website')
    return render(request, 'partials/form_fields.html', {'qr_type': qr_type, 'form': QRCodeForm()})

def preview_qr(request):
    """
    Robuster Preview Handler.
    Erstellt Bild auch wenn Form Validation fehlschlägt (Dirty Read).
    """
    if request.method == "POST":
        form = QRCodeForm(request.POST, request.FILES)
        instance = None
        
        if form.is_valid():
            instance = form.save(commit=False)
        else:
            # Fallback: Objekt manuell bauen
            instance = QRCodeEntry()
            
            # Basis Felder
            instance.qr_type = request.POST.get('qr_type', 'website')
            instance.module_style = request.POST.get('module_style', 'square')
            instance.color = request.POST.get('color', '#000000')
            instance.bg_color = request.POST.get('bg_color', '#ffffff')
            instance.frame_style = request.POST.get('frame_style', 'none')
            instance.logo_preset = request.POST.get('logo_preset', 'none')
            
            # Text & Font
            instance.bottom_text = request.POST.get('bottom_text', '')
            instance.bottom_text_color = request.POST.get('bottom_text_color', '#000000')
            instance.text_font = request.POST.get('text_font', 'arial.ttf')
            
            # Zahlenwerte (Sicher parsen)
            def get_int(key, default):
                try: return int(request.POST.get(key, default))
                except: return default
                
            instance.scale = get_int('scale', 10)
            instance.border_size = get_int('border_size', 4)
            instance.bottom_text_size = get_int('bottom_text_size', 35)
            
            # Content
            instance.url = request.POST.get('url')
            instance.ssid = request.POST.get('ssid')
            instance.password = request.POST.get('password')
            instance.security = request.POST.get('security', 'WPA')
            instance.text_content = request.POST.get('text_content')
            instance.vcard_name = request.POST.get('vcard_name')
            instance.vcard_email = request.POST.get('vcard_email')
            instance.vcard_phone = request.POST.get('vcard_phone')
            instance.vcard_org = request.POST.get('vcard_org')

            # WICHTIG: Logo Upload manuell zuweisen
            if 'logo' in request.FILES:
                instance.logo = request.FILES['logo']

        try:
            img = _create_qr_image(instance)
            
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return HttpResponse(f'<img src="data:image/png;base64,{img_str}" class="img-fluid shadow-lg rounded" style="max-height: 400px;">')
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return HttpResponse(f'<div class="alert alert-danger p-2 small">Preview Error: {e}</div>')
        
    return HttpResponse('Loading...')

def generate_qr(request):
    if request.method == "POST":
        form = QRCodeForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()
            img = _create_qr_image(instance)
            
            out = BytesIO()
            img.save(out, format='JPEG', quality=95)
            out.seek(0)
            
            response = HttpResponse(out.getvalue(), content_type="image/jpeg")
            response['Content-Disposition'] = 'attachment; filename="qr_design.jpg"'
            return response
            
    return HttpResponse("Fehler beim Formular", status=400)