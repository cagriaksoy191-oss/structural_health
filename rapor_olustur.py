from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def raporu_olustur():
    doc = Document()

    # --- BAŞLIK ---
    baslik = doc.add_heading('YAPI SAĞLIĞI VE RİSK ANALİZ PLATFORMU:\nV12 TITANIUM', 0)
    baslik.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Alt Başlık
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('(Yapay Zeka Destekli Ön Tarama ve Karar Destek Sistemi)')
    run.italic = True
    run.font.size = Pt(12)

    # Bilgiler
    doc.add_paragraph(f'Proje Yürütücüsü: Çağrı AKSOY\nTarih: Ocak 2026\nVersiyon: V12 Titanium (Release Candidate)')
    doc.add_paragraph('---' * 30)

    # --- 1. YÖNETİCİ ÖZETİ ---
    doc.add_heading('1. YÖNETİCİ ÖZETİ (EXECUTIVE SUMMARY)', level=1)
    doc.add_paragraph(
        "Türkiye'nin bir deprem ülkesi olduğu gerçeğinden hareketle geliştirilen bu proje, "
        "geleneksel bina risk analizi süreçlerini dijitalleştirmeyi, hızlandırmayı ve yerel donanım gücüyle güvenli hale getirmeyi amaçlamaktadır."
    )
    doc.add_paragraph(
        "Projemiz, sadece statik formüllere dayalı eski usul yazılımlardan farklı olarak Hibrit Yapay Zeka Mimarisi kullanmaktadır. "
        "Sistemimiz, laboratuvar hassasiyetinde (%98.1 doğruluk) beton dayanımı tahmini yapan matematiksel modelleri, "
        "insan mantığına yakın karar veren Bulanık Mantık (Fuzzy Logic) algoritmalarını ve sonuçları bir uzman gibi yorumlayan "
        "Büyük Dil Modellerini (LLM - Qwen3) tek bir çatı altında toplamıştır."
    )

    # --- 2. PROBLEM TANIMI ---
    doc.add_heading('2. PROBLEM TANIMI VE MEVCUT DURUM', level=1)
    p = doc.add_paragraph("Mevcut yapı denetim ve risk analizi süreçlerinde dört temel darboğaz bulunmaktadır:")
    
    items = [
        "Zaman Kaybı: Bir binadan karot (beton numunesi) alıp laboratuvar sonucunu beklemek günler sürmektedir.",
        "Yüksek Maliyet: Her bina için detaylı laboratuvar analizi yapmak maliyetlidir.",
        "Veri Güvenliği: Bulut tabanlı sistemlerde bina verilerinin üçüncü taraf sunuculara gönderilmesi risk oluşturmaktadır.",
        "Uzman Yetersizliği: Her binayı tek tek yorumlayacak uzman mühendis sayısı yetersizdir."
    ]
    for item in items:
        doc.add_paragraph(item, style='List Bullet')

    # --- 3. ÇÖZÜM ---
    doc.add_heading('3. ÇÖZÜM: V12 TITANIUM MİMARİSİ', level=1)
    doc.add_paragraph("Projemiz, bu sorunları 'Uç Nokta Hesaplama' (Edge Computing) ve Çok Katmanlı Yapay Zeka ile çözmektedir.")
    
    doc.add_heading('3.1. Sistemin Çalışma Prensibi (4 Katmanlı Yapı)', level=2)
    
    layers = [
        ("1. Veri Toplama Katmanı:", "Ultrasonik Ses Hızı (UPV), Schmidt Çekici verileri ve Bina envanter bilgileri."),
        ("2. Makine Öğrenmesi Katmanı (The Brain):", "Scikit-learn / Random Forest. 482 gerçek bina verisiyle eğitilmiştir. Performans: R² = %98.1."),
        ("3. Bulanık Mantık Katmanı (The Logic):", "Beton dayanımı ve risk puanlarını kesin çizgilerle değil, geçişli mantıkla analiz eder."),
        ("4. Üretken Yapay Zeka Katmanı (The Voice):", "Ollama & Qwen3:8B. Teknik verileri analiz ederek 'Mühendis Görüşü Raporu' yazar.")
    ]
    for title, desc in layers:
        p = doc.add_paragraph()
        p.add_run(title).bold = True
        p.add_run(f" {desc}")

    # --- 4. TEKNİK ALTYAPI ---
    doc.add_heading('4. TEKNİK ALTYAPI VE DONANIM AVANTAJI', level=1)
    doc.add_paragraph("Projemizin en büyük farkı, bulut bağımlılığı olmadan çalışabilmesidir.")
    tech_items = [
        "On-Premise (Yerel) Çalışma: Tüm işlemler kullanıcının bilgisayarında gerçekleşir.",
        "Donanım Gücü: Sistem, NVIDIA RTX 5070 Ti (12GB VRAM) gibi yüksek performanslı GPU'lar üzerinde optimize edilmiştir.",
        "Hız: Buluta veri gönderip bekleme süresi yoktur. Raporlama saniyeler içinde gerçekleşir."
    ]
    for item in tech_items:
        doc.add_paragraph(item, style='List Bullet')

    # --- 5. DOĞRULAMA ---
    doc.add_heading('5. DOĞRULAMA VE TEST SONUÇLARI', level=1)
    doc.add_paragraph("Sistemimiz, 482 adet gerçek bina verisi ile 'Backtest' sürecinden geçmiştir.")

    # Tablo
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Metrik'
    hdr_cells[1].text = 'Değer'
    hdr_cells[2].text = 'Anlamı'

    # Veriler
    data = [
        ('R² (Doğruluk Katsayısı)', '%98.1', 'Sistem, laboratuvar sonuçlarıyla %98 oranında örtüşmektedir.'),
        ('MPS (Ortalama Hata)', '1.33 MPa', 'Tahminlerimiz gerçek değerden ortalama sadece 1.33 birim sapmaktadır.'),
        ('RMS (Hata Kararlılığı)', '1.86', 'Sistemin hata kararlılığı yüksektir, sürpriz sonuçlar üretmez.')
    ]

    for metric, val, desc in data:
        row_cells = table.add_row().cells
        row_cells[0].text = metric
        row_cells[1].text = val
        row_cells[2].text = desc

    doc.add_paragraph("\nBu veriler, sistemin bilimsel olarak doğrulanmış bir 'karar destek mekanizması' olduğunu kanıtlamaktadır.")

    # --- 6. ROADMAP ---
    doc.add_heading('6. YENİ YOL HARİTASI (ROADMAP)', level=1)
    roadmap = [
        "FAZ 1 (Tamamlandı): V12 Backend, %98 doğruluklu model ve Yerel LLM entegrasyonu.",
        "FAZ 2 (Kısa Vade): Mobil Entegrasyon ve Saha Uygulaması.",
        "FAZ 3 (Orta Vade): IoT Sensör Entegrasyonu.",
        "FAZ 4 (Uzun Vade): Ulusal Veri Tabanı ve Bakanlık Entegrasyonu."
    ]
    for item in roadmap:
        doc.add_paragraph(item, style='List Number')

    # --- 7. SONUÇ ---
    doc.add_heading('7. SONUÇ', level=1)
    doc.add_paragraph(
        "Geliştirdiğimiz bu platform, inşaat mühendisliği bilgisini modern Yapay Zeka teknolojileriyle birleştiren öncü bir sistemdir. "
        "Sahip olduğu yüksek doğruluk oranı (%98.1) ve veri gizliliği (Yerel Çalışma) prensibiyle, kentsel dönüşüm süreçlerinde "
        "hız, güven ve maliyet avantajı sağlayan stratejik bir üründür."
    )
    
    # İmza
    doc.add_paragraph("\n\nHazırlayan: Çağrı AKSOY & Yapay Zeka Ar-Ge Ekibi").alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # Kaydet
    dosya_adi = "V12_Titanium_Proje_Raporu.docx"
    doc.save(dosya_adi)
    print(f"✅ Başarılı! Rapor '{dosya_adi}' adıyla oluşturuldu.")

if __name__ == "__main__":
    raporu_olustur()
