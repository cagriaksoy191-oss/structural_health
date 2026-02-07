# 🎮 GÜNLÜK ÇALIŞMA REHBERİ
## Antigravity ile Süper Kolay Versiyon! 🚀

---

# 📍 BAŞLAMADAN ÖNCE

## CI/CD Nedir? (Gerçek Hayat Örneği)

Düşün ki bir grup ödevi yapıyorsunuz. Herkes farklı kısımları yazıyor.

### ❌ CI/CD OLMADAN (Eski Usul):
```
1. Emine ödevinin kendi kısmını yazar, USB'ye atar
2. Talha USB'yi alır, açar... DOSYA BOZUK! 😱
3. Talha: "Emine bu ne ya açılmıyor!"
4. Emine: "Bende açılıyordu ya!"
5. 2 saat uğraşılır, sunum gecikirdi...
```

### ✅ CI/CD İLE (Bizim Sistem):
```
1. Emine kodunu yazar, "/gonder" der
2. 30 saniye sonra: ❌ HATA VAR!
3. Emine hemen görür, düzeltir
4. Tekrar "/gonder" → ✅ BAŞARILI!
5. Talha çektiğinde sorunsuz çalışır 🎉
```

**3 önemli kavram:**
| Kavram | Basit Anlamı |
|--------|-------------|
| `git pull` | İnternetten indir (arkadaşların yaptıklarını al) |
| `git push` | İnternete yükle (senin yaptıklarını paylaş) |
| `runner` | GitHub'ın senin bilgisayarındaki temsilcisi |

---

# 🌅 SABAH BİLGİSAYARI AÇINCA

## Tek Komutla Başla!

Antigravity'yi aç ve chat'e şunu yaz:

```
/sabah
```

**Bu komut otomatik olarak:**
1. ✅ Son değişiklikleri çeker (arkadaşlarının yaptıklarını alır)
2. ✅ Sanal ortamı aktif eder
3. ✅ Sana "Çalışmaya hazırsın!" der

> 💡 **ESKİDEN** 4-5 komut yazman gerekirdi. Şimdi sadece `/sabah` yazıyorsun!

---

# 💻 KOD YAZ VE ÇALIŞ

Bu kısım değişmedi - normal şekilde çalış:

1. Antigravity'de projen açıkken çalış
2. İstediğin dosyayı düzenle
3. Kaydet (**CTRL + S**)

> 💡 Bu aşamada istediğin kadar zaman harca. 5 dakika da olabilir, 5 saat de.

---

# 📤 DEĞİŞİKLİKLERİ KAYDET VE PAYLAŞ

## Tek Komutla Gönder!

Çalışmanı bitirdiğinde Antigravity'ye şunu yaz:

```
/gonder
```

**Bu komut sana soracak:**
- "Ne yaptığını kısaca yaz"

**Örnek cevaplar:**
- *"Login sayfasını düzelttim"*
- *"Yeni grafik ekledim"*
- *"Hata giderdim"*

Sonra otomatik olarak:
1. ✅ Değişiklikleri paketler
2. ✅ GitHub'a gönderir
3. ✅ Test sonucunu bildirir

---

# ✅ SONUCU KONTROL ET

Gönderdikten sonra test sonucunu görmek için:

```
/kontrol
```

**Bu komut:**
1. 🌐 Tarayıcıyı açar
2. 📊 GitHub Actions sayfasını gösterir
3. ✅ veya ❌ sonucunu bildirir

| Gördüğün | Anlamı |
|----------|--------|
| ✅ Yeşil tik | Her şey çalışıyor! |
| ❌ Kırmızı X | Bir hata var, bak ne olmuş |
| 🟡 Sarı daire | Test hala çalışıyor, bekle |

---

# 🚀 TEK KOMUTLA HER ŞEY! (YENİ)

Günün sonunda tek bir komutla her şeyi halledebilirsin:

> **"Runner'ı kontrol et, arkadaşlarımın değişikliklerini çek, çakışma varsa her iki tarafın en iyi kısımlarını birleştir ve neden bu kararı verdiğini açıkla, sonra benim değişikliklerimi GitHub'a gönder, CI/CD testini bekle ve projeyi tarayıcıda test edip sonucu göster"**

Bu komut otomatik olarak:
1. ✅ Runner'ı kontrol eder
2. ✅ Arkadaşların değişikliklerini çeker
3. ✅ Çakışma varsa akıllıca birleştirir
4. ✅ Senin değişikliklerini GitHub'a gönderir
5. ✅ Test yapıp sonucu gösterir

---

# 📋 TEK SAYFA ÖZET (YAZDIR VE DUVARA AS)

| Sıra | Ne Yapıyorsun | Antigravity Komutu |
|------|---------------|-------------------|
| 1️⃣ | Sabah başla | `/sabah` |
| 2️⃣ | Kod yaz | *(Antigravity'de çalış)* |
| 3️⃣ | Bitince gönder | `/gonder` |
| 4️⃣ | Sonucu kontrol et | `/kontrol` |
| ⭐ | **YA DA** Akşam tek komut | Yukarıdaki sihirli komutu yaz |

---

# 🎨 GÖRSEL AKIŞ ŞEMASI

```
┌─────────────────────────────────────────────────────────────┐
│                     GÜNLÜK İŞ AKIŞI                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ☀️ SABAH:                                                  │
│   ┌─────────────┐                                           │
│   │  /sabah     │ → Antigravity'ye yaz                      │
│   └──────┬──────┘ → "Çalışmaya hazırsın!" mesajını gör      │
│          │                                                   │
│          ↓                                                   │
│   ✍️ KOD YAZ (editörde istediğin kadar çalış)               │
│          │                                                   │
│          ↓                                                   │
│   ┌─────────────┐                                           │
│   │  /gonder    │ → Commit mesajı yaz                       │
│   └──────┬──────┘ → Otomatik GitHub'a gider                 │
│          │                                                   │
│          ↓                                                   │
│   ┌─────────────┐                                           │
│   │  /kontrol   │ → Tarayıcıda sonucu gör                   │
│   └──────┬──────┘ → ✅ yeşil tik = başarılı                 │
│          │                                                   │
│          ↓                                                   │
│   🏠 Eve git!                                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

# 🆘 BİR ŞEY YANLIŞ GİDERSE

| Hata | Çözüm |
|------|-------|
| `/sabah` çalışmıyor | Antigravity'yi kapat, tekrar aç |
| `/gonder` hata veriyor | Önce `/sabah` yap, sonra tekrar dene |
| `/kontrol` tarayıcı açılmıyor | Brave tarayıcısını kontrol et |
| ❌ Kırmızı X görüyorum | `/kontrol` yap, hatayı oku |

---

# 💡 İPUÇLARI

## Commit mesajı nasıl yazılır?
```
❌ KÖTÜ: "değişiklik"
❌ KÖTÜ: "fix"
✅ İYİ: "Login butonunu maviye cevirdim"
✅ İYİ: "Grafik hatasını düzelttim"
```

## Ne zaman `/gonder` yapmalıyım?
- Küçük bir özellik bitirdiğinde
- Bir hatayı düzelttiğinde
- Ara verip bilgisayarı kapatmadan önce

---

# 📱 ACİL DURUMLAR İÇİN

**Sırayla dene:**
1. 📖 Bu rehberi tekrar oku
2. 🤖 Antigravity'ye "yardım et" de
3. 💬 WhatsApp grubuna yaz
4. 📞 Çağrı'yı ara

---

# ⚡ HIZLI KOMUT REFERANSI

| Komut | Ne Yapar |
|-------|----------|
| `/sabah` | Günü başlat |
| `/gonder` | Değişiklikleri GitHub'a gönder |
| `/kontrol` | GitHub Actions durumunu kontrol et |
| `/test` | Projeyi lokal olarak test et |
| `/runner` | GitHub runner'ı başlat |

---

*Bu rehberi ister yazdır ister telefonuna kaydet.*
*Artık 5 komutla her şeyi yapabilirsin!* 🚀

---

*Son Güncelleme: 7 Şubat 2026*
*Takım: Çağrı, Emine, Talha, Baha*
