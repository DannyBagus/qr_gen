import io
from fpdf import FPDF

class PDFService:
    @staticmethod
    def generate_table_stand(qr_image_bytes, title, main_text, details=[]):
        """
        Erstellt ein schönes A4 Info-Blatt / Aufsteller.
        Optimiert für "One Page Only" (Auto-Pagebreak deaktiviert).
        """
        # A4 Hochformat (210mm x 297mm)
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        
        # WICHTIG: Automatischen Seitenumbruch deaktivieren!
        # Das verhindert, dass FPDF eine zweite Seite erstellt, nur weil wir den Footer ganz unten wollen.
        pdf.set_auto_page_break(False)
        
        pdf.add_page()
        
        page_w = 210
        page_h = 297
        margin = 15
        
        # --- 1. HEADER ---
        pdf.set_fill_color(33, 37, 41) # Dunkles Grau
        pdf.rect(0, 0, page_w, 35, 'F') 
        
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(0, 10)
        pdf.cell(page_w, 15, title, align='C')
        
        # --- 2. RAHMEN ---
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.5)
        # Rahmen geht bis 20mm vor Seitenende
        pdf.rect(margin, 45, page_w - 2*margin, page_h - 65)
        
        # --- 3. QR CODE ---
        img_size = 110 
        x_pos = (page_w - img_size) / 2
        y_pos = 60 
        
        pdf.image(qr_image_bytes, x=x_pos, y=y_pos, w=img_size)
        
        # --- 4. HAUPT TEXT ---
        current_y = y_pos + img_size + 8
        
        if main_text:
            pdf.set_y(current_y)
            pdf.set_font("Helvetica", "B", 20)
            pdf.set_text_color(0, 0, 0)
            # Multi_cell darf jetzt über den Rand schreiben, da page_break aus ist
            pdf.multi_cell(0, 9, main_text, align='C')
            current_y = pdf.get_y() + 8
        else:
            current_y += 8

        # --- 5. DETAILS ---
        if details:
            pdf.set_y(current_y)
            pdf.set_font("Helvetica", "", 12)
            pdf.set_text_color(80, 80, 80)
            
            for line in details:
                pdf.cell(0, 7, line, ln=True, align='C')

        # --- 6. FOOTER ---
        # Absolute Positionierung von unten (-15mm vom Rand)
        pdf.set_y(-15)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 10, "Erstellt mit QR Studio - qr.raowy.ch", align='C')
        
        return pdf.output()