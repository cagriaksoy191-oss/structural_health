# 🛠️ V12 Titanium - Manuel Çalışma Rehberi (Antigravity Olmadan)

Bu rehber, Antigravity kullanmayan veya VS Code / PyCharm gibi farklı editörler kullananlar içindir.
Tüm işlemleri **PowerShell** üzerinden manuel olarak yapmanız gerekir.

---

## ☀️ GÜNE BAŞLARKEN

1. **PowerShell** açın.
2. Proje klasörüne gidin:
   ```powershell
   cd Desktop\structural_health
   ```
3. Son değişiklikleri çekin:
   ```powershell
   git pull origin main
   ```
4. Sanal ortamı açın:
   ```powershell
   .\venv\Scripts\Activate
   ```
   ✅ `(venv)` yazısını görmelisiniz.

---

## 💻 GÜN İÇİNDE

Kodunuzu yazın ve sık sık kaydedin.

---

## 📤 GÜNÜ BİTİRİRKEN (GÖNDERME)

İşiniz bittiğinde sırasıyla şu komutları yazın:

1. **Değişiklikleri ekle:**
   ```powershell
   git add .
   ```

2. **Kaydet (Commit):**
   ```powershell
   git commit -m "Buraya ne yaptiginizi yazin"
   ```
   *(Örnek: "Login ekranini duzelttim")*

3. **Gönder (Push):**
   ```powershell
   git push origin main
   ```

### ✅ KONTROL ETME
Gönderdikten sonra test sonucunu görmek için tarayıcıda şu linke gidin:
[GitHub Actions Sayfası](https://github.com/cagriaksoy191-oss/structural_health/actions)

- 🟢 **Yeşil Tik:** Başarılı
- 🔴 **Kırmızı Çarpı:** Hata var

---

## 🆘 HATA DURUMLARI

**Hata:** `git push` yaparken "rejected" hatası alıyorum.
**Çözüm:** Önce `git pull origin main` yapın, sonra tekrar `git push origin main` deneyin.

**Hata:** `(venv)` gelmiyor.
**Çözüm:** `Set-ExecutionPolicy RemoteSigned` komutunu yönetici olarak çalıştırın.

*Son Güncelleme: 7 Şubat 2026*
