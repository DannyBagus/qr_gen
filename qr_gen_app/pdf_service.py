import io
from fpdf import FPDF

class PDFService:
    @staticmethod
    def generate_table_stand(qr_image_bytes, title, main_text, details=[]):
        """
        Erstellt ein schönes A4 Info-Blatt / Aufsteller.
        """
        # A4 Hochformat
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        
        page_w = 210
        page_h = 297
        margin = 15
        
        # --- 1. HEADER (Schwarz mit weißem Text) ---
        pdf.set_fill_color(33, 37, 41) # Dunkles Grau/Schwarz
        pdf.rect(0, 0, page_w, 40, 'F')
        
        pdf.set_font("Helvetica", "B", 28)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(0, 12)
        pdf.cell(page_w, 15, title, align='C')
        
        # --- 2. RAHMEN UM INHALT ---
        # Ein dünner grauer Rahmen um den Hauptbereich sieht edel aus
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.5)
        pdf.rect(margin, 50, page_w - 2*margin, page_h - 70)
        
        # --- 3. QR CODE ---
        # Wir laden das Bild. Da es jetzt high-res ist, wird es scharf skaliert.
        img_size = 130 
        x_pos = (page_w - img_size) / 2
        y_pos = 70
        
        pdf.image(qr_image_bytes, x=x_pos, y=y_pos, w=img_size)
        
        # --- 4. HAUPT TEXT (Call to Action) ---
        # Das ist der Text, der vorher im Bild war (z.B. "Scannen du musst")
        # Jetzt schreiben wir ihn als Vektor-Text unter das Bild.
        current_y = y_pos + img_size + 10
        
        if main_text:
            pdf.set_y(current_y)
            pdf.set_font("Helvetica", "B", 22)
            pdf.set_text_color(0, 0, 0)
            # Automatische Zeilenumbrüche falls Text lang ist
            pdf.multi_cell(0, 10, main_text, align='C')
            current_y = pdf.get_y() + 10
        else:
            current_y += 10

        # --- 5. DETAILS (WLAN PW etc.) ---
        if details:
            pdf.set_y(current_y)
            pdf.set_font("Helvetica", "", 14)
            pdf.set_text_color(80, 80, 80)
            
            for line in details:
                pdf.cell(0, 8, line, ln=True, align='C')

        # --- 6. FOOTER ---
        pdf.set_y(-15)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 10, "Erstellt mit QR Studio - qr.raowy.ch", align='C')
        
        return pdf.output()