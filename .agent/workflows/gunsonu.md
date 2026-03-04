---
description: Gün Sonu (End of Day) - Full CI/CD Döngüsü
---

# /gunsonu - Tam Otomatik CI/CD Akışı (v2 - Çakışma Korumalı)

Bu workflow, gün sonunda yapılması gereken **TÜM** işlemleri tek seferde halleder.
4 kişilik ekipte herkesin bilgisayarında sorunsuz çalışır.

**v2 Farkı:** Eski Commit→Pull→Push sırası kaldırıldı.
Yeni akış: **Fetch → Stash → Pull → Pop → Conflict Check → Test → Commit → Push**

> **ÖNEMLİ AGENT TALİMATI:** Aşağıdaki TEK komutu çalıştır. Script tüm adımları sırasıyla otomatik yapar. Bitince çıktıyı oku ve bu talimatlara göre hareket et.

// turbo-all

## Çalıştır

```powershell
& scripts\gunsonu.ps1
```

## Script Ne Yapar? (11 Adım Otomatik)

1. **Runner Kontrolü** — GitHub Actions runner bilgisi
2. **Ollama Kontrolü** — AI servisinin açık olup olmadığını kontrol eder
3. **.gitignore Güvenliği** — Kritik klasörlerin gitignore'da olduğunu doğrular
4. **Git Fetch + Remote Check** — Remote'da yeni commit var mı kontrol eder
5. **Akıllı Senkronizasyon** — 4 yoldan birini seçer (aşağıda detay)
6. **Bağımlılık Senkronu** — requirements.txt ve package.json güncellemelerini uygular
7. **Health Check + Import Test** — Push öncesi `import main` doğrulaması
8. **Lokal Commit** — Birleştirilmiş kodu commit eder
9. **Git Push** — Tüm değişiklikleri GitHub'a gönderir
10. **Pinecone** — MCP kuruluysa hafıza günceller
11. **CI/CD Takibi** — GitHub Actions durumunu kontrol eder

## Akıllı Senkronizasyon (4 Yol)

| Durum                         | Yol           | Açıklama                             |
| ----------------------------- | ------------- | ------------------------------------ |
| Hem lokal hem remote değişmiş | **FULL SYNC** | Stash → Pull → Pop → Conflict Check  |
| Sadece remote değişmiş        | **PULL-ONLY** | Direkt git pull (conflict riski yok) |
| Sadece lokal değişmiş         | **FAST PATH** | Sync gerekmez, direkt commit+push    |
| Hiçbir şey değişmemiş         | **NO-OP**     | Hiçbir işlem gerekli değil           |

---

## 🛑 EXIT CODE 99 PROTOKOLÜ (ÇAKIŞMA DURUMU)

Eğer script çıktısında **Exit Code 99** veya **"CAKISMA (CONFLICT) TESPIT EDILDI"** mesajı görürsen, şu kurallara **MUTLAK** uy:

### Kural 1: ASLA Zorla Push Etme

- `git push --force` veya `git push -f` komutunu **HİÇBİR KOŞULDA KULLANMA**.
- `git pull --rebase` komutunu **HİÇBİR KOŞULDA KULLANMA**.
- Bu komutlar sessizce veri kaybına yol açar.

### Kural 2: Çakışan Dosyaları Bul ve Çöz

1. Terminaldeki çıktıda listelenen çakışan dosyaları oku
2. Eğer listede dosya yoksa `git diff --name-only --diff-filter=U` çalıştır
3. Her çakışan dosyayı aç ve Git conflict marker'larını bul:
   ```
   <<<<<<< Updated upstream
   (Ekip arkadaşının kodu)
   =======
   (Senin kodun)
   >>>>>>> Stashed changes
   ```
4. Aşağıdaki **Semantik Birleştirme Kuralları**'na göre çöz

### Kural 3: Çözüm Sonrası Test Zorunluluğu

Conflict çözüldükten sonra **MUTLAKA** şu kontrolleri yap:

```powershell
venv\Scripts\python -c "import main; print('import OK')"
```

Bu başarısız olursa push **YAPMA**, hatayı kullanıcıya bildir.

### Kural 4: Çözüm Sonrası Commit ve Tekrar /gunsonu

1. `git add .` çalıştır
2. `git commit -m "Conflict cozuldu: [dosya listesi] (AI-assisted)"` ile commit et
3. `/gunsonu` komutunu **tekrar baştan çalıştır** — bu sefer FAST PATH'e düşecek ve temiz push olacak

---

## 📋 SEMANTİK BİRLEŞTİRME KURALLARI (Conflict Çözme Anayasası)

> **BU BÖLÜM TÜM AI MODELLERİ İÇİN BAĞLAYICIDIR (Claude, GPT, Gemini, vb.)**

### Genel Kural: HER İKİ TARAFIN EMEĞİNİ KORU

Çakışan kısımlarda bir tarafın kodunu/metnini seçip diğerini **ASLA SİLME**.
Ekip üyelerinin yazdığı tüm yeni özellikleri, logları ve görevleri
**ANLAMSAL OLARAK BİRLEŞTİR**. Her iki tarafın emeği de aynı dosyada kalmalıdır.

### Kod Dosyaları İçin (_.py, _.jsx, \*.js)

1. **İki kodun da amacını anla.** Her iki tarafın ne yapmaya çalıştığını belirle.
2. **Fonksiyon çakışması:** Aynı fonksiyon farklı şekilde değiştirildiyse, her ikisinin de yaptığı iyileştirmeleri tek bir versiyonda birleştir.
3. **Import çakışması:** Her iki tarafın eklediği import'ları da koru.
4. **Eğer iki değişiklik birbirine bağımlıysa** (biri fonksiyon imzasını, diğeri çağrıyı değiştirmişse), son halini uyumlu olacak şekilde düzenle.
5. **BİRLEŞTİRME MÜMKÜN DEĞİLSE:** Kullanıcıya her iki versiyonu göster, kararı insana bırak.

### AGENTS.md İçin (ÖZEL KURAL — EN KRİTİK)

AGENTS.md proje hafızasıdır. Çakışma çözümü şu kurallara uymalıdır:

1. **"Tamamlanan Geliştirmeler" bölümü:** Her iki tarafın eklediği `[x]` maddelerini **TÜMÜNÜ** koru. Hiçbir tamamlanmış maddeyi silme.
2. **"Son Değişiklikler" bölümü:** Tarih başlıklı alt bölümler halinde düzenle. İki kişi aynı gün değişiklik yaptıysa, her birinin maddelerini ayrı paragraflar halinde **TÜMÜNÜ** koru.
3. **"Mimari Kararlar" bölümü:** Yeni eklenen kararları **TÜMÜNÜ** koru. Aynı konuda farklı karar varsa kullanıcıya sor.
4. **"Değiştirilen Dosyalar" bölümü:** Her iki tarafın listelediği dosyaları birleştir. Aynı dosya iki listede de varsa, her iki açıklamayı da yaz.
5. **ASLA bir ekip üyesinin yazdığı özeti silme.** İki özet çakışıyorsa, ikisini de yaz.

### progress.md İçin (ÖZEL KURAL)

progress.md devam eden işlerin takip dosyasıdır:

1. **Tamamlanmamış görevler (`[ ]`):** Her iki tarafın görevlerini koru.
2. **Tamamlanmış görevler (`[x]`):** Birinin yapılan olarak işaretlediğini, diğer taraf henüz işaretlememişse, `[x]` olarak koru (daha güncel olan wins).
3. **Yeni görevler:** Her iki tarafın eklediği yeni görevleri **TÜMÜNÜ** koru.
4. **Bug logları ve fikirler:** İki tarafın yazdıklarını **TÜMÜNÜ** koru, tarih/isim bilgisiyle ayırt edilebilir şekilde düzenle.

---

## ⚠️ PUSH REDDEDİLMESİ DURUMU

Eğer script çıktısında **"PUSH REDDEDILDI"** mesajı varsa:

- Bu, script çalışırken (fetch ile push arasında geçen sürede) başka biri push yapmış demektir.
- Script **otomatik rebase YAPMAZ** (veri kaybı riski).
- Yapılacak tek şey: `/gunsonu` komutunu **tekrar çalıştır**. Yeni çalıştırmada fetch+stash+pull+pop akışı yeni push'u da dahil edecektir.

---

## Beklenen Çıktı (Normal Durum)

Script bitince otomatik olarak şu formatı gösterir:

```
================================================
  /GUNSONU RAPORU (v2)
================================================

  Runner        : GitHub Cloud
  Ollama        : Acik
  .gitignore    : Guvenli
  Remote Sync   : 3 commit cekildi + birlesti
  Bagimliliklar : Guncel
  Health Check  : Basarili
  Commit        : Olusturuldu
  Git Push      : Basarili
  Pinecone      : Guncellendi
  CI/CD         : Basarili

================================================
  Bilgisayarini kapatabilirsin!
================================================
```

## Beklenen Çıktı (Çakışma Durumu — Exit Code 99)

```
  ================================================
  !! CAKISMA (CONFLICT) TESPIT EDILDI !!
  ================================================

  Cakisan dosyalar:
    - main.py
    - AGENTS.md

  SCRIPT DURDURULUYOR (Exit Code 99).
  Agent bu cakismayi cozmeli, sonra /gunsonu tekrar calistirilmali.

================================================
  /GUNSONU RAPORU (YARIDA KESILDI)
================================================
  Remote Sync   : CONFLICT (Exit 99)
  Commit        : (atlanildi)
  Git Push      : (atlanildi)
================================================
  CAKISMA COZULMEDEN PUSH YAPILMADI.
================================================
```

## RAPORLAMA FORMATI (Conflict çözümü sonrası)

Çakışmayı çözdükten sonra kullanıcıya şu formatta özet sun:

- **Çakışan Dosya:** [Dosya Adı]
- **Gelen Değişiklik (Ekip Arkadaşı):** [Ne yapmış?]
- **Senin Değişikliğin:** [Sen ne yapmıştın?]
- **Çözüm:** [Nasıl birleştirdin?]
- **Test Sonucu:** [import main başarılı mı?]
