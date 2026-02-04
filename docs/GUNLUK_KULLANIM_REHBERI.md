# 🎮 GÜNLÜK ÇALIŞMA REHBERİ
## (Lise Öğrencisi Bile Anlayabilir Sürümü)

---

# 📍 BAŞLAMADAN ÖNCE

Düşün ki bu proje bir **Google Docs dosyası** gibi. Ama Google Docs'tan farklı olarak, değişiklikler **otomatik kaydedilmiyor**. Sen elle "kaydet" ve "paylaş" demen lazım.

**3 önemli kavram:**
- `git pull` = İnternetten indir (arkadaşların yaptıklarını al)
- `git push` = İnternete yükle (senin yaptıklarını paylaş)
- `runner` = GitHub'ın senin bilgisayarındaki temsilcisi

---

# ADIM 1: RUNNER'I BAŞLAT 🏃

## Bu Ne?
**Runner = GitHub'ın senin bilgisayarındaki temsilcisi.** 

Onu açmazsan, GitHub seninle konuşamaz. Kod gönderdiğinde testlerin çalışması için runner'ın açık olması lazım.

## Nasıl Yapılır?

**1.** Klavyeden **Windows tuşu + R** bas

**2.** Açılan küçük kutuya şunu yaz:
```
powershell
```

**3.** **Enter** bas. Mavi/siyah bir pencere açılacak.

**4.** O pencereye şunu yaz ve **Enter** bas:
```powershell
cd C:\actions-runner
```
> 💡 `cd` = "buraya git" demek. actions-runner klasörüne gidiyorsun.

**5.** Sonra şunu yaz ve **Enter** bas:
```powershell
.\run.cmd
```

**6.** Şunu görmelisin:
```
√ Connected to GitHub
Listening for Jobs
```

✅ **Görüyorsan:** Tebrikler! Runner çalışıyor.

❌ **Görmüyorsan:** Çağrı'yı ara.

> ⚠️ **ÖNEMLİ:** Bu pencereyi **KAPATMA!** Küçült ve öyle bırak.

---

# ADIM 2: YENİ BİR PENCERE AÇ VE SON DEĞİŞİKLİKLERİ ÇEK 📥

## Bu Ne?
Arkadaşların dün gece bir şeyler yazmış olabilir. Onları kendi bilgisayarına indiriyorsun.

## Nasıl Yapılır?

**1.** **Windows tuşu + R** bas

**2.** `powershell` yaz, **Enter** bas (yeni bir pencere açılır)

**3.** Şunu yaz ve **Enter** bas:
```powershell
cd C:\Projects\structural_health
```
> 💡 Proje klasörüne gidiyorsun.

**4.** Şunu yaz ve **Enter** bas:
```powershell
git pull origin main
```
> 💡 `git pull` = "internetten son değişiklikleri indir" demek.

**5.** Şunlardan birini göreceksin:

| Mesaj | Anlamı |
|-------|--------|
| `Already up to date.` | Zaten güncelsin, yeni bir şey yok |
| `Updating...` + dosya listesi | Yeni dosyalar indirildi |
| `CONFLICT` | ⚠️ Sorun var! Çağrı'yı ara |

---

# ADIM 3: SANAL ORTAMI AKTİF ET 🔋

## Bu Ne?
Düşün ki projenin özel bir **"pili"** var. Onu açmazsan proje çalışmaz.

## Nasıl Yapılır?

**1.** **AYNI pencerede** (az önce `git pull` yaptığın yerde) şunu yaz:
```powershell
.\venv\Scripts\Activate
```

**2.** **Enter** bas.

**3.** Terminalin başında `(venv)` yazısı çıkacak:
```
(venv) PS C:\Projects\structural_health>
```

✅ **(venv) görüyorsan:** Pil takılı! Devam et.

❌ **Görmüyorsan:** Kurulum eksik. Çağrı'yı ara.

---

# ADIM 4: KOD YAZ VE ÇALIŞ 💻

## Bu Ne?
Asıl iş burada! Kodunu yaz, tasarımını yap, ne yapacaksan yap.

## Nasıl Yapılır?

**1.** VS Code veya hangi editörü kullanıyorsan aç

**2.** `C:\Projects\structural_health` klasörünü aç

**3.** İstediğin dosyayı düzenle

**4.** Kaydet (**CTRL + S**)

> 💡 Bu aşamada istediğin kadar zaman harca. 5 dakika da olabilir, 5 saat de.

---

# ADIM 5: DEĞİŞİKLİKLERİ KAYDET VE PAYLAŞ 📤

## Bu Ne?
Senin yaptığın değişiklikleri internete yüklüyorsun ki arkadaşların da görsün.

## Nasıl Yapılır?

**1.** PowerShell penceresine dön (venv aktif olan pencere)

**2.** Şunu yaz ve **Enter** bas:
```powershell
git add .
```
> 💡 `git add .` = "bütün değişiklikleri paketle" demek. **Sonundaki nokta önemli!**

**3.** Şunu yaz ve **Enter** bas:
```powershell
git commit -m "buraya ne yaptığını yaz"
```
> 💡 **Örnek:** `git commit -m "login sayfasına buton ekledim"`
> 
> Tırnak işaretleri önemli! İçine Türkçe karakter yazabilirsin.

**4.** Şunu yaz ve **Enter** bas:
```powershell
git push origin main
```
> 💡 `git push` = "paketi internete gönder" demek.

**5.** İşlem bittikten sonra:
- https://github.com/cagriaksoy191-oss/structural_health adresine git
- **"Actions"** sekmesine tıkla
- ✅ **Yeşil tik** görüyorsan = Her şey çalışıyor
- ❌ **Kırmızı X** görüyorsan = Bir hata var, tıklayıp bak

---

# 📋 TEK SAYFA ÖZET (YAZDIR VE DUVARA AS)

| Sıra | Ne Yapıyorsun | Komut |
|------|---------------|-------|
| 1️⃣ | Runner'ı başlat | `cd C:\actions-runner` sonra `.\run.cmd` |
| 2️⃣ | Proje klasörüne git | `cd C:\Projects\structural_health` |
| 3️⃣ | Son değişiklikleri çek | `git pull origin main` |
| 4️⃣ | Sanal ortamı aç | `.\venv\Scripts\Activate` |
| 5️⃣ | Kod yaz | *(editörde çalış)* |
| 6️⃣ | Değişiklikleri paketle | `git add .` |
| 7️⃣ | Açıklama ekle | `git commit -m "ne yaptın"` |
| 8️⃣ | İnternete gönder | `git push origin main` |

---

# 🎨 GÖRSEL AKIŞ ŞEMASI

```
┌─────────────────────────────────────────────────────────────┐
│                     GÜNLÜK İŞ AKIŞI                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ☀️ BİLGİSAYARI AÇINCA:                                    │
│   ┌─────────────┐                                           │
│   │ 1. Runner   │ → cd C:\actions-runner                    │
│   │    Başlat   │ → .\run.cmd                               │
│   └──────┬──────┘ → "Listening for Jobs" gör                │
│          │         → PENCEREYİ KAPATMA!                      │
│          ↓                                                   │
│   ┌─────────────┐                                           │
│   │ 2. Yeni     │ → cd C:\Projects\structural_health        │
│   │    Pencere  │ → git pull origin main                    │
│   └──────┬──────┘                                           │
│          │                                                   │
│          ↓                                                   │
│   ┌─────────────┐                                           │
│   │ 3. Ortamı   │ → .\venv\Scripts\Activate                 │
│   │    Aktif Et │ → (venv) yazısını gör                     │
│   └──────┬──────┘                                           │
│          │                                                   │
│          ↓                                                   │
│   ✍️ KOD YAZ (editörde)                                     │
│          │                                                   │
│          ↓                                                   │
│   ┌─────────────┐                                           │
│   │ 4. Kaydet   │ → git add .                               │
│   │    ve       │ → git commit -m "açıklama"                │
│   │    Gönder   │ → git push origin main                    │
│   └──────┬──────┘                                           │
│          │                                                   │
│          ↓                                                   │
│   ✅ GitHub Actions'da yeşil tik gör                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

# 🆘 BİR ŞEY YANLIŞ GİDERSE

| Hata | Çözüm |
|------|-------|
| `"git is not recognized"` | Git yüklü değil, Çağrı'yı ara |
| `"failed to push"` | Önce `git pull origin main` yap, sonra tekrar push |
| `"venv not found"` | Yanlış klasördesin, `cd C:\Projects\structural_health` yaz |
| `"Listening for Jobs"` gelmedi | Runner bozuk, Çağrı'yı ara |
| `"Permission denied"` | GitHub davetini kabul etmemişsin, e-postanı kontrol et |
| `"CONFLICT"` mesajı | Çağrı'yı ara, birlikte çözelim |

---

# 💡 İPUÇLARI

## Commit mesajı nasıl yazılır?
```
❌ KÖTÜ: git commit -m "değişiklik"
❌ KÖTÜ: git commit -m "fix"
✅ İYİ: git commit -m "Buton rengini maviye cevirdim"
✅ İYİ: git commit -m "Login hatasini duzeltim"
✅ İYİ: git commit -m "Yeni grafik eklendi"
```

## Ne zaman push yapmalıyım?
- Küçük bir özellik bitirdiğinde
- Bir hatayı düzelttiğinde
- Ara verip bilgisayarı kapatmadan önce

## Push yapmadan önce kontrol listesi:
1. ✅ Kod çalışıyor mu? (test ettim mi?)
2. ✅ Dosyaları kaydettim mi? (CTRL+S)
3. ✅ Commit mesajı anlaşılır mı?

---

# 📱 ACİL DURUMLAR İÇİN

**Sırayla dene:**
1. 📖 Bu rehberi tekrar oku
2. 🔍 Hata mesajını Google'a yaz
3. 🤖 ChatGPT'ye sor
4. 💬 WhatsApp grubuna yaz
5. 📞 Çağrı'yı ara

---

*Bu rehberi ister yazdır ister telefonuna kaydet.*
*Takıldığın yerde bana veya Çağrı'ya sor!* 🚀

---

*Son Güncelleme: 4 Şubat 2026*
*Takım: Çağrı, Emine, Talha, Baha*
