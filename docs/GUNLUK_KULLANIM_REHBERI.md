# GUNLUK CALISMA REHBERI

Lise Ogrencisi Bile Anlayabilir Surumu

---

## BASLAMADAN ONCE

Dusun ki bu proje bir Google Docs dosyasi gibi. Ama Google Docs'tan farkli olarak, degisiklikler otomatik kaydedilmiyor. Sen elle "kaydet" ve "paylas" demen lazim.

3 onemli kavram:

| Komut | Ne Demek? |
|-------|-----------|
| git pull | Internetten indir (arkadaslarin yaptiklarini al) |
| git push | Internete yukle (senin yaptiklarini paylas) |
| runner | GitHub'in senin bilgisayarindaki temsilcisi |

---

## ADIM 1: RUNNER'I BASLAT

**Bu Ne?**

Runner = GitHub'in senin bilgisayarindaki temsilcisi. Onu acmazsan, GitHub seninle konusamaz.

**Nasil Yapilir?**

1. Klavyeden Windows tusu + R bas
2. Acilan kutuya powershell yaz ve Enter bas
3. Mavi/siyah pencereye su komutu yaz:

```
cd C:\actions-runner
```

4. Enter bas, sonra sunu yaz:

```
.\run.cmd
```

5. Sunu gormelisin:

```
Connected to GitHub
Listening for Jobs
```

Goruyorsan: Tebrikler! Runner calisiyor.

ONEMLI: Bu pencereyi KAPATMA! Kucult ve oyle birak.

---

## ADIM 2: SON DEGISIKLIKLERI CEK

**Bu Ne?**

Arkadaslarin dun gece bir seyler yazmis olabilir. Onlari indiriyorsun.

**Nasil Yapilir?**

1. YENI bir PowerShell penceresi ac (Windows + R, powershell)
2. Su komutlari sirayla yaz:

```
cd C:\Projects\structural_health
```

```
git pull origin main
```

**Sonuc:**

| Mesaj | Anlami |
|-------|--------|
| Already up to date. | Zaten guncelsin |
| Updating... | Yeni dosyalar indirildi |
| CONFLICT | Sorun var! Cagri'yi ara |

---

## ADIM 3: SANAL ORTAMI AKTIF ET

**Bu Ne?**

Projenin ozel "pili". Acmazsan kod calismaz.

**Nasil Yapilir?**

Ayni pencerede sunu yaz:

```
.\venv\Scripts\Activate
```

Terminalin basinda (venv) yazisi cikacak:

```
(venv) PS C:\Projects\structural_health>
```

(venv) goruyorsan: Devam et!

---

## ADIM 4: KOD YAZ

1. VS Code veya editorunu ac
2. C:\Projects\structural_health klasorunu ac
3. Istedigin dosyayi duzenle
4. Kaydet (CTRL + S)

---

## ADIM 5: KAYDET VE PAYLAS

PowerShell penceresine don ve su 3 komutu sirayla yaz:

**Komut 1: Degisiklikleri paketle**

```
git add .
```

**Komut 2: Aciklama ekle**

```
git commit -m "ne yaptigini yaz"
```

Ornek: git commit -m "Buton rengi degistirildi"

**Komut 3: Internete gonder**

```
git push origin main
```

**Sonuc kontrolu:**

GitHub Actions sayfasina git ve kontrol et:
- Yesil tik = Her sey OK
- Kirmizi X = Hata var

---

## HIZLI OZET TABLOSU

| Sira | Islem | Komut |
|------|-------|-------|
| 1 | Runner baslat | cd C:\actions-runner sonra .\run.cmd |
| 2 | Proje klasorune git | cd C:\Projects\structural_health |
| 3 | Degisiklikleri cek | git pull origin main |
| 4 | Ortami aktif et | .\venv\Scripts\Activate |
| 5 | Kod yaz | (editorde calis) |
| 6 | Paketle | git add . |
| 7 | Aciklama ekle | git commit -m "aciklama" |
| 8 | Gonder | git push origin main |

---

## SORUN CIKTIGINDA

| Hata | Cozum |
|------|-------|
| git is not recognized | Git yuklu degil, Cagri'yi ara |
| failed to push | Once git pull origin main yap |
| venv not found | cd C:\Projects\structural_health yaz |
| Runner calismiyor | Cagri'yi ara |

---

## YARDIM SIRASI

1. Bu rehberi tekrar oku
2. Hata mesajini Google'a yaz
3. ChatGPT'ye sor
4. WhatsApp grubuna yaz
5. Cagri'yi ara

---

Son Guncelleme: 4 Subat 2026

Takim: Cagri, Emine, Talha, Baha
