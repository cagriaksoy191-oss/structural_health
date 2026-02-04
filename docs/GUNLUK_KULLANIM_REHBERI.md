# 🎮 GÜNLÜK ÇALIŞMA REHBERİ

**Lise Öğrencisi Bile Anlayabilir Sürümü**

---

## 📍 BAŞLAMADAN ÖNCE

Düşün ki bu proje bir **Google Docs dosyası** gibi. Ama Google Docs'tan farklı olarak, değişiklikler **otomatik kaydedilmiyor**. Sen elle "kaydet" ve "paylaş" demen lazım.

**3 önemli kavram:**
| Komut | Ne Demek? |
|-------|-----------|
| `git pull` | İnternetten indir (arkadaşların yaptıklarını al) |
| `git push` | İnternete yükle (senin yaptıklarını paylaş) |
| `runner` | GitHub'ın senin bilgisayarındaki temsilcisi |

---

## ADIM 1: RUNNER'I BAŞLAT 🏃

**Bu Ne?**
Runner = GitHub'ın senin bilgisayarındaki temsilcisi. Onu açmazsan, GitHub seninle konuşamaz.

**Nasıl Yapılır?**

1. Klavyeden **Windows tuşu + R** bas
2. Açılan kutuya `powershell` yaz ve **Enter** bas
3. Mavi/siyah pencereye şunu yaz:

```
cd C:\actions-runner
```

4. Enter bas, sonra şunu yaz:

```
.\run.cmd
```

5. Şunu görmelisin:

```
√ Connected to GitHub
Listening for Jobs
```

✅ Görüyorsan: Tebrikler! Runner çalışıyor.

⚠️ **ÖNEMLİ: Bu pencereyi KAPATMA! Küçült ve öyle bırak.**

---

## ADIM 2: SON DEĞİŞİKLİKLERİ ÇEK 📥

**Bu Ne?**
Arkadaşların dün gece bir şeyler yazmış olabilir. Onları indiriyorsun.

**Nasıl Yapılır?**

1. **Yeni** bir PowerShell penceresi aç (Windows + R → powershell)
2. Şu komutları sırayla yaz:

```
cd C:\Projects\structural_health
```

```
git pull origin main
```

**Sonuç:**
| Mesaj | Anlamı |
|-------|--------|
| `Already up to date.` | Zaten güncelsin |
| `Updating...` | Yeni dosyalar indirildi |
| `CONFLICT` | Sorun var! Çağrı'yı ara |

---

## ADIM 3: SANAL ORTAMI AKTİF ET 🔋

**Bu Ne?**
Projenin özel "pili". Açmazsan kod çalışmaz.

**Nasıl Yapılır?**

Aynı pencerede şunu yaz:

```
.\venv\Scripts\Activate
```

Terminalin başında `(venv)` yazısı çıkacak:

```
(venv) PS C:\Projects\structural_health>
```

✅ (venv) görüyorsan: Devam et!

---

## ADIM 4: KOD YAZ 💻

1. VS Code veya editörünü aç
2. `C:\Projects\structural_health` klasörünü aç
3. İstediğin dosyayı düzenle
4. Kaydet (CTRL + S)

---

## ADIM 5: KAYDET VE PAYLAŞ 📤

PowerShell penceresine dön ve şu 3 komutu sırayla yaz:

**Komut 1:** Değişiklikleri paketle
```
git add .
```

**Komut 2:** Açıklama ekle
```
git commit -m "ne yaptığını yaz"
```
Örnek: `git commit -m "Buton rengi degistirildi"`

**Komut 3:** İnternete gönder
```
git push origin main
```

**Sonuç kontrolü:**
- https://github.com/cagriaksoy191-oss/structural_health/actions
- ✅ Yeşil tik = Her şey OK
- ❌ Kırmızı X = Hata var

---

## 📋 HIZLI ÖZET TABLOSU

| Sıra | İşlem | Komut |
|------|-------|-------|
| 1 | Runner başlat | `cd C:\actions-runner` → `.\run.cmd` |
| 2 | Proje klasörüne git | `cd C:\Projects\structural_health` |
| 3 | Değişiklikleri çek | `git pull origin main` |
| 4 | Ortamı aktif et | `.\venv\Scripts\Activate` |
| 5 | Kod yaz | *(editörde çalış)* |
| 6 | Paketle | `git add .` |
| 7 | Açıklama ekle | `git commit -m "açıklama"` |
| 8 | Gönder | `git push origin main` |

---

## � SORUN ÇIKTIĞINDA

| Hata | Çözüm |
|------|-------|
| `git is not recognized` | Git yüklü değil, Çağrı'yı ara |
| `failed to push` | Önce `git pull origin main` yap |
| `venv not found` | `cd C:\Projects\structural_health` yaz |
| Runner çalışmıyor | Çağrı'yı ara |

---

## � YARDIM SIRASI

1. Bu rehberi tekrar oku
2. Hata mesajını Google'a yaz
3. ChatGPT'ye sor
4. WhatsApp grubuna yaz
5. Çağrı'yı ara

---

*Son Güncelleme: 4 Şubat 2026*

*Takım: Çağrı, Emine, Talha, Baha*
