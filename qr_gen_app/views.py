import segno
from segno import helpers
import base64
import os
import io
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.staticfiles import finders
from .forms import QRCodeForm
from .models import QRCodeEntry
from .pdf_service import PDFService

# --- CORE IMAGE GENERATION ---

def _create_qr_image(instance, high_res=False, draw_text=True):
    """
    Zentrale Funktion zum Zeichnen des QR Codes.
    high_res: Wenn True, wird das Bild riesig gerendert (für Druckqualität).
    draw_text: Wenn False, wird der Text unter dem QR weggelassen (damit PDF ihn schreiben kann).
    """
    
    # --- 1. DATEN PAYLOAD GENERIEREN ---
    content_data = ""
    error_lvl = instance.error_correction or 'H'
    
    # Helper Variablen
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

    # --- 2. BASIS ZEICHNEN ---
    # SKALIERUNG: Für PDF nutzen wir scale=40 (sehr hochauflösend), sonst box_size (meist 10)
    base_scale = instance.box_size if instance.box_size else 10
    scale = 40 if high_res else base_scale
    
    # Rand anpassen (skalieren)
    base_border = instance.border if instance.border is not None else 4
    # Wenn wir hochskalieren, muss der Rand proportional bleiben, aber Segno handelt das via Border
    # Wir nutzen hier fixen Border für Segno, erweitern später via Pillow für Frames
    
    matrix = qr.matrix
    width_modules = len(matrix)
    img_size = width_modules * scale
    
    bg_color = instance.background_color or "#ffffff"
    fg_color = instance.foreground_color or "#000000"
    
    img = Image.new("RGBA", (img_size, img_size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Module zeichnen
    for y, row in enumerate(matrix):
        for x, col in enumerate(row):
            if col: 
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
                    draw.rectangle([x0, y0, x1, y1], fill=fg_color)

    # --- 3. LOGO HANDLING ---
    logo_img = None
    if instance.logo:
        try:
            if hasattr(instance.logo, 'seek'): instance.logo.seek(0)
            logo_img = Image.open(instance.logo).convert("RGBA")
        except: pass
    elif instance.logo_preset and instance.logo_preset != 'none':
        filename = f"{instance.logo_preset}.png"
        path = finders.find(f"qr_gen_app/assets/{filename}")
        if path:
            try: logo_img = Image.open(path).convert("RGBA")
            except: pass

    if logo_img:
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
        # Wenn wir keinen Text zeichnen sollen (für PDF), brauchen wir unten weniger Platz
        border_bottom = scale * 12 if draw_text else scale * 4
        
        w, h = final_img.size
        new_w = w + (border_side * 2)
        new_h = h + border_side + border_bottom
        
        canvas = Image.new("RGBA", (new_w, new_h), "#ffffff")
        draw_canv = ImageDraw.Draw(canvas)
        draw_canv.rectangle([0,0,new_w-1, new_h-1], outline="#eeeeee", width=int(scale/10) or 1)
        
        canvas.paste(final_img, (border_side, border_side))
        final_img = canvas
        
    elif instance.frame_style == 'phone':
        border_p = scale * 3
        w, h = final_img.size
        new_w = w + (border_p * 2)
        new_h = h + (border_p * 4)
        
        canvas = Image.new("RGBA", (new_w, new_h), (0,0,0,0)) 
        draw_canv = ImageDraw.Draw(canvas)
        
        draw_canv.rounded_rectangle([0,0, new_w, new_h], radius=scale*4, fill="#212529")
        draw_canv.rectangle([border_p, border_p*2, new_w-border_p, new_h-border_p*2], fill=bg_color)
        canvas.paste(final_img, (border_p, border_p*2), final_img)
        final_img = canvas


    # --- 5. TEXT (Nur zeichnen, wenn draw_text=True) ---
    if instance.bottom_text and draw_text:
        font_size = instance.bottom_text_size or 35
        # Skalieren der Fontgröße, wenn Bild hochauflösend ist
        if high_res:
            factor = scale / base_scale # Wie viel größer ist das Bild?
            font_size = int(font_size * factor)

        text_col = instance.bottom_text_color or "#000000"
        font = None
        font_filename = instance.text_font or 'arial.ttf'
        
        font_path = finders.find(f"qr_gen_app/assets/fonts/{font_filename}")
        if font_path:
            try: font = ImageFont.truetype(font_path, font_size)
            except: pass
        if font is None:
            try: font = ImageFont.truetype(font_filename, font_size)
            except: font = ImageFont.load_default()

        if instance.frame_style == 'polaroid':
            draw = ImageDraw.Draw(final_img)
            w, h = final_img.size
            draw.text((w/2, h - (scale * 6) if not high_res else h - (scale*2)), instance.bottom_text, fill=text_col, font=font, anchor="mm")
        else:
            try:
                ascent, descent = font.getmetrics()
                text_h = ascent + descent + (font_size * 0.6)
            except:
                text_h = font_size * 1.5
            
            w, h = final_img.size
            canvas = Image.new("RGBA", (w, int(h + text_h)), bg_color)
            canvas.paste(final_img, (0,0))
            draw = ImageDraw.Draw(canvas)
            draw.text((w/2, h + (text_h/2) - 5), instance.bottom_text, fill=text_col, font=font, anchor="mm")
            final_img = canvas

    # --- 6. FINALE KONVERTIERUNG ---
    background = Image.new("RGB", final_img.size, (255,255,255))
    background.paste(final_img, (0, 0), final_img)
    return background


# --- VIEWS ---

def index(request):
    form = QRCodeForm(initial={'qr_type': 'website', 'box_size': 10, 'module_style': 'square', 'foreground_color': '#000000', 'bottom_text_size': 35})
    return render(request, 'qr_gen_app/index.html', {'form': form})

def get_form_fields(request):
    qr_type = request.GET.get('qr_type', 'website')
    return render(request, 'partials/form_fields.html', {'qr_type': qr_type, 'form': QRCodeForm()})

def preview_qr(request):
    if request.method == "POST":
        form = QRCodeForm(request.POST, request.FILES)
        instance = None
        if form.is_valid():
            instance = form.save(commit=False)
        else:
            # Fallback für Dirty Read
            instance = QRCodeEntry()
            instance.qr_type = request.POST.get('qr_type', 'website')
            instance.module_style = request.POST.get('module_style', 'square')
            instance.foreground_color = request.POST.get('foreground_color', '#000000')
            instance.background_color = request.POST.get('background_color', '#ffffff')
            instance.frame_style = request.POST.get('frame_style', 'none')
            instance.logo_preset = request.POST.get('logo_preset', 'none')
            instance.error_correction = request.POST.get('error_correction', 'H')
            instance.bottom_text = request.POST.get('bottom_text', '')
            instance.bottom_text_color = request.POST.get('bottom_text_color', '#000000')
            instance.text_font = request.POST.get('text_font', 'arial.ttf')
            
            def get_int(key, default):
                try: return int(request.POST.get(key, default))
                except: return default
            instance.box_size = get_int('box_size', 10)
            instance.border = get_int('border', 4)
            instance.bottom_text_size = get_int('bottom_text_size', 35)
            
            instance.url = request.POST.get('url')
            instance.ssid = request.POST.get('ssid')
            instance.password = request.POST.get('password')
            instance.security = request.POST.get('security', 'WPA')
            instance.text_content = request.POST.get('text_content')
            instance.vcard_name = request.POST.get('vcard_name')
            instance.vcard_email = request.POST.get('vcard_email')
            instance.vcard_phone = request.POST.get('vcard_phone')
            instance.vcard_org = request.POST.get('vcard_org')
            if 'logo' in request.FILES: instance.logo = request.FILES['logo']

        try:
            # Preview: Standard Auflösung, MIT Text
            img = _create_qr_image(instance, high_res=False, draw_text=True)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return HttpResponse(f'<img src="data:image/png;base64,{img_str}" class="img-fluid shadow-lg rounded" style="max-height: 400px;">')
        except Exception as e:
            return HttpResponse(f'<div class="alert alert-danger p-2 small">Error: {e}</div>')
    return HttpResponse('Loading...')

def generate_qr(request):
    if request.method == "POST":
        form = QRCodeForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            # Download PNG: Hohe Auflösung, MIT Text
            img = _create_qr_image(instance, high_res=True, draw_text=True)
            out = BytesIO()
            img.save(out, format='PNG')
            out.seek(0)
            response = HttpResponse(out.getvalue(), content_type="image/png")
            response['Content-Disposition'] = 'attachment; filename="qr_design.png"'
            return response
    return HttpResponse("Fehler beim Formular", status=400)

def generate_pdf(request):
    if request.method == 'POST':
        form = QRCodeForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            data = form.cleaned_data
            
            # Titel und Subtitel Logik für das PDF
            pdf_title = "SCAN MICH"
            pdf_subtitle = "" # Leer, wenn nicht nötig
            
            # WICHTIG: bottom_text aus dem Image entfernen, damit er nicht doppelt ist!
            # Wir nutzen ihn stattdessen als prominenten Text im PDF
            call_to_action = data.get('bottom_text', '')

            # Kontext Infos für Footer
            details = []
            if instance.qr_type == 'wifi':
                pdf_title = "WLAN GASTZUGANG"
                details.append(f"Netzwerk: {instance.ssid}")
                if instance.password: details.append(f"Passwort: {instance.password}")
            elif instance.qr_type == 'vcard':
                pdf_title = "KONTAKT"
                details.append(instance.vcard_name)
            elif instance.qr_type == 'website':
                pdf_title = "WEBSITE"
                if not call_to_action: 
                    # Wenn kein "Scan mich" Text da ist, URL anzeigen
                    call_to_action = instance.url
            
            # Bild generieren:
            # 1. high_res=True -> Gestochen scharf (scale=40)
            # 2. draw_text=False -> Text NICHT ins Bild brennen (vermeidet Doppelung)
            qr_pil_image = _create_qr_image(instance, high_res=True, draw_text=False)
            
            qr_buffer = io.BytesIO()
            qr_pil_image.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            
            # PDF Service aufrufen
            try:
                pdf_bytes = PDFService.generate_table_stand(
                    qr_image_bytes=qr_buffer,
                    title=pdf_title,
                    main_text=call_to_action, # Das ist der Text unter dem QR
                    details=details
                )
                response = HttpResponse(bytes(pdf_bytes), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="qr_aufsteller.pdf"'
                return response
            except Exception as e:
                print(f"PDF ERROR: {e}")
                return HttpResponse(f"PDF Error: {e}", status=500)
            
    return HttpResponse("Form Error", status=400)