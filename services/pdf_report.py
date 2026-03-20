import os
import uuid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fpdf import FPDF

def generate_charts(counts, risk_skoru, request_id):
    """ Matplotlib ile grafikleri oluşturup static klasörüne kaydeder """
    pie_path = os.path.join("static", f"deprem_dagilimi_{request_id}.png")
    bar_path = os.path.join("static", f"risk_skoru_{request_id}.png")
    
    # 1. Deprem Sınıfları Pasta Grafiği
    labels = list(counts.keys())
    sizes = list(counts.values())
    colors = ['#ff4d4d', '#ff9933', '#ffcc00', '#99cc00']
    explode = (0.1, 0, 0, 0)
    
    plt.figure(figsize=(5, 5))
    if sum(sizes) == 0:
        plt.text(0.5, 0.5, "Deprem verisi bulunamadi", ha='center', va='center')
    else:
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.title("Bölgesel Deprem Kayıtları\n(Son 50 Yıl AFAD)")
    plt.savefig(pie_path)
    plt.close()

    # 2. Risk Skoru Bar Grafiği
    plt.figure(figsize=(6, 2))
    plt.barh(["Risk Skoru"], [risk_skoru], color='red' if risk_skoru > 70 else ('orange' if risk_skoru > 40 else 'green'))
    plt.xlim(0, 100)
    plt.title(f"Genel Yapı Risk Skoru: {round(risk_skoru, 2)}/100")
    plt.xlabel("Risk (0: Başarılı, 100: Kritik)")
    plt.tight_layout()
    plt.savefig(bar_path)
    plt.close()
    
    return pie_path, bar_path

def draw_table_row(pdf, col1, col2, bg_color=None):
    if bg_color:
        pdf.set_fill_color(*bg_color)
        fill = True
    else:
        fill = False
        
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(60, 8, col1, border=1, fill=fill)
    pdf.set_font('Arial', '', 11)
    pdf.cell(130, 8, col2, border=1, fill=fill, ln=True)

def draw_tbdy_row(pdf, kriter, durum, uyum_text, uyum_code, aciklama, bg_color=None):
    """ TBDY 2018 Kriteri | Mevcut Durum | Uygunluk | Açıklama """
    if bg_color:
        pdf.set_fill_color(*bg_color)
        fill = True
    else:
        fill = False

    x = pdf.get_x()
    y = pdf.get_y()
    
    pdf.set_font('Arial', '', 9)
    exp_lines = max(1, int(pdf.get_string_width(aciklama) / 72.0) + 1)
    k_lines = max(1, int(pdf.get_string_width(kriter) / 45.0) + 1)
    lines = max(exp_lines, k_lines)
    h = max(8, lines * 5 + 4)

    if y + h > 280:
        pdf.add_page()
        y = pdf.get_y()
        
        # Sütun başlıklarını yeniden çizelim
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(50, 8, "TBDY 2018 Kriteri", border=1, fill=True, align='C')
        pdf.cell(35, 8, "Mevcut Durum", border=1, fill=True, align='C')
        pdf.cell(25, 8, "Uyum", border=1, fill=True, align='C')
        pdf.cell(80, 8, "Açıklama", border=1, fill=True, align='C', ln=True)
        pdf.set_font('Arial', '', 9)
        x = pdf.get_x()
        y = pdf.get_y()
        
        if fill: pdf.set_fill_color(*bg_color)

    if fill:
        pdf.rect(x, y, 50, h, 'DF')
        pdf.rect(x+50, y, 35, h, 'DF')
        pdf.rect(x+85, y, 25, h, 'DF')
        pdf.rect(x+110, y, 80, h, 'DF')
    else:
        pdf.rect(x, y, 50, h, 'D')
        pdf.rect(x+50, y, 35, h, 'D')
        pdf.rect(x+85, y, 25, h, 'D')
        pdf.rect(x+110, y, 80, h, 'D')

    # Kriter
    pdf.set_xy(x + 2, y + 2)
    pdf.set_font('Arial', 'B', 9)
    pdf.multi_cell(46, 5, kriter, align='C')
    
    # Durum
    pdf.set_xy(x + 50, y + (h/2) - 3)
    pdf.set_font('Arial', '', 10)
    pdf.cell(35, 6, durum, align='C')
    
    # Uyum
    pdf.set_xy(x + 85, y + (h/2) - 3)
    pdf.set_font('Arial', 'B', 10)
    if uyum_code == 'U':
        pdf.set_text_color(39, 174, 96) # Yeşil
    elif uyum_code == 'R':
        pdf.set_text_color(192, 57, 43) # Kırmızı
    else:
        pdf.set_text_color(211, 84, 0) # Turuncu
        
    pdf.cell(25, 6, uyum_text, align='C')
    pdf.set_text_color(0, 0, 0) # Sifirla
    
    # Aciklama
    pdf.set_xy(x + 112, y + 2)
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(76, 5, aciklama, align='L')
    
    pdf.set_xy(x, y + h)

def draw_evaluation_row(pdf, risk_factor, explanation, points, bg_color=None):
    """3 Sütunlu değerlendirme formatı çizici: Risk Faktörü | Açıklama | Puan"""
    if bg_color:
        pdf.set_fill_color(*bg_color)
        fill = True
    else:
        fill = False

    x = pdf.get_x()
    y = pdf.get_y()
    
    pdf.set_font('Arial', '', 10)
    exp_lines = max(1, int(pdf.get_string_width(explanation) / 100.0) + 1)
    
    pdf.set_font('Arial', 'B', 10)
    rf_lines = max(1, int(pdf.get_string_width(risk_factor) / 50.0) + 1)
    
    h = max(8, max(exp_lines, rf_lines) * 6 + 4)
    
    if y + h > 280:
        pdf.add_page()
        y = pdf.get_y()
        
        # Sütun başlıklarını yeniden çizelim
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(55, 8, "Risk Faktörü", border=1, fill=True, align='C')
        pdf.cell(105, 8, "Mühendislik Anlamı", border=1, fill=True, align='C')
        pdf.cell(30, 8, "Puan Etkisi", border=1, fill=True, align='C', ln=True)
        x = pdf.get_x()
        y = pdf.get_y()
        
        if fill: pdf.set_fill_color(*bg_color)
        
    # Draw Background/Borders
    if fill:
        pdf.rect(x, y, 55, h, 'DF')
        pdf.rect(x+55, y, 105, h, 'DF')
        pdf.rect(x+160, y, 30, h, 'DF')
    else:
        pdf.rect(x, y, 55, h, 'D')
        pdf.rect(x+55, y, 105, h, 'D')
        pdf.rect(x+160, y, 30, h, 'D')
        
    pdf.set_font('Arial', 'B', 10)
    pdf.set_xy(x + 2, y + 2)
    pdf.multi_cell(51, 6, risk_factor, align='L')
    
    pdf.set_font('Arial', '', 10)
    pdf.set_xy(x + 57, y + 2)
    pdf.multi_cell(101, 6, explanation, align='L')
    
    pdf.set_font('Arial', 'B', 10)
    pdf.set_xy(x + 160, y + (h/2) - 3)
    pdf.cell(30, 6, points, align='C')
    
    pdf.set_xy(x, y + h)

def create_ai_pdf_report(params, counts, risk_skoru, anfis_mpa, ai_text, phase2_advice, evaluations=[], tbdy_uyum=[], engine_version=None):
    request_id = str(uuid.uuid4())[:8]
    pie_path, bar_path = generate_charts(counts, risk_skoru, request_id)
    
    pdf = FPDF()
    pdf.add_page()
    
    # --- FONT YÜKLEMESİ (TÜRKÇE DESTEĞİ İÇİN) ---
    font_path_reg = "C:\\Windows\\Fonts\\arial.ttf"
    font_path_bold = "C:\\Windows\\Fonts\\arialbd.ttf"
    
    if os.path.exists(font_path_reg) and os.path.exists(font_path_bold):
        pdf.add_font('Arial', '', font_path_reg, uni=True)
        pdf.add_font('Arial', 'B', font_path_bold, uni=True)
    else:
        # Fallback
        pdf.add_font('Arial', '', 'helvetica')
        pdf.add_font('Arial', 'B', 'helvetica')
    
    # BASLIK
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(41, 128, 185) # Mavi tonu
    pdf.cell(0, 10, 'Yapı Sağlığı Ön Tarama Detaylı Analiz Raporu', ln=True, align='C')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)
    
    # 1. GRAFIKLER (En Başa Alındı)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 8, ' 1. Görsel Analiz ve Bölgesel Risk Özeti', border=0, ln=True, fill=True)
    pdf.ln(5)

    y_pos = pdf.get_y()
    
    if os.path.exists(bar_path):
        pdf.image(bar_path, x=50, y=y_pos, w=110)
    pdf.ln(35)
    
    # 2. PERFORMANS HEDEFLERİ VE TBDY 2018 UYUMU
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 8, ' 2. Performans Hedefleri ve TBDY 2018 Uyumu', border=0, ln=True, fill=True)
    pdf.ln(3)
    
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(50, 8, "TBDY 2018 Kriteri", border=1, fill=True, align='C')
    pdf.cell(35, 8, "Mevcut Durum", border=1, fill=True, align='C')
    pdf.cell(25, 8, "Uyum", border=1, fill=True, align='C')
    pdf.cell(80, 8, "Aciklama", border=1, fill=True, align='C', ln=True)
    
    alt_color = False
    for krit, dur, u_txt, u_code, acik in tbdy_uyum:
        bg = (245, 245, 245) if alt_color else None
        draw_tbdy_row(pdf, krit, dur, u_txt, u_code, acik, bg)
        alt_color = not alt_color
        
    pdf.ln(8)
    
    # 3. İNCELEME ALANI
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 8, ' 3. İnceleme Alanı ve Yapısal Sınıflandırma', border=0, ln=True, fill=True)
    pdf.ln(3)
    
    draw_table_row(pdf, "Kullanım Amacı", f"{params['kullanim_amaci']}")
    draw_table_row(pdf, "Bina Yükseklik Sınıfı (BYS)", f"{params['bys']} (Top. {params['h_n']}m, {params['kat_sayisi']} Kat)")
    draw_table_row(pdf, "Yapım Yılı", f"{params['yapim_yili']} [{params['bina_turu']}]")
    draw_table_row(pdf, "Zemin Kat Durumu", "Dükkan/Ticari (Yumuşak Kat Tehlikesi)" if params['zemin_kat_dukkan'] else "Standart / Konut", bg_color=(255,230,230) if params['zemin_kat_dukkan'] else None)
    
    pdf.ln(8)
    if pdf.get_y() > 240:
        pdf.add_page()
        
    # 4. YAPISAL RISK ANALIZI AÇIKLAMALARI
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 8, ' 4. Yapısal Risk Analizi Girdi Anlamları', border=0, ln=True, fill=True)
    pdf.ln(3)
    
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(55, 8, "Risk Faktörü", border=1, fill=True, align='C')
    pdf.cell(105, 8, "Mühendislik Anlamı", border=1, fill=True, align='C')
    pdf.cell(30, 8, "Puan Etkisi", border=1, fill=True, align='C', ln=True)
    
    alt_color = False
    for risk_factor, explanation, points in evaluations:
        bg = (245, 245, 245) if alt_color else None
        draw_evaluation_row(pdf, risk_factor, explanation, points, bg)
        alt_color = not alt_color
        
    pdf.ln(8)
    
    # 5. SISMOLOJIK VERILER
    if pdf.get_y() > 220:
        pdf.add_page()
    
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 8, ' 5. Sismolojik Veriler (Bölgesel Deprem Dağılımı)', border=0, ln=True, fill=True)
    pdf.ln(3)
    
    y_pie = pdf.get_y()
    if os.path.exists(pie_path):
        pdf.image(pie_path, x=130, y=y_pie-5, w=60)
        
    for level, count in counts.items():
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(40, 7, f"Deprem Sınıfı {level}", border=1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(40, 7, f"{count} Adet Kayıt", border=1, ln=True)
        
    pdf.set_y(max(pdf.get_y(), y_pie + 55))
    pdf.ln(8)
    
    # 6. YAPAY ZEKA MÜHENDİS YORUMU (EN SONDA)
    if pdf.get_y() > 200:
        pdf.add_page()
        
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 8, ' 6. Kapanış: Yapay Zeka Uzman Değerlendirmesi', border=0, ln=True, fill=True)
    pdf.ln(4)
    
    pdf.set_font('Arial', '', 11)
    # Sadece AI'dan gelme ihtimali olan yildiz ve diez isaretlerini siliyoruz
    clean_text = str(ai_text).replace('#', '').replace('*', '')
    pdf.multi_cell(0, 6, clean_text)
    pdf.ln(6)
    
    # 7. SONUC VE TAVSIYELER
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(192, 57, 43) 
    pdf.multi_cell(0, 6, f">> NİHAİ SONUÇ: {phase2_advice}")
    pdf.set_text_color(0, 0, 0)
    
    # Footer - Motor Versiyonu + Yasal Uyarı
    pdf.ln(15)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(100, 100, 100)
    if engine_version:
        pdf.cell(0, 4, f"Motor Versiyonu: {engine_version}", ln=True, align='C')
        pdf.ln(2)
    pdf.multi_cell(0, 4, "Yasal Uyari: Bu rapor bir on degerlendirme araci tarafindan AI destekli olarak uretilmistir, kesin yapi sagligi veya oturum izni yerine gecmez. Guvenli sonuclar icin laboratuvar testleri ile lisansli yapi denetim kuruluslarina basvurulmalidir.", align='C')
    
    filename = f"AI_Deprem_Raporu_{request_id}.pdf"
    filepath = os.path.join("static", filename)
    pdf.output(filepath)
    
    return f"/static/{filename}"
