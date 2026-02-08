@echo off
color 0A
echo ==========================================
echo GITHUB BAGLANTISI KURULUYOR...
echo ==========================================
echo.

echo 1. Git baslatiliyor...
git init

echo.
echo 2. Uzak sunucu (GitHub) ekleniyor...
git remote remove origin 2>nul
git remote add origin https://github.com/cagriaksoy191-oss/structural_health.git

echo.
echo 3. Gecmis veriler cekiliyor...
git fetch

echo.
echo 4. Ana dal (main) ayarlaniyor...
git branch -M main
git branch --set-upstream-to=origin/main main

echo.
echo ==========================================
echo ISLEM TAMAMLANDI! 🚀
echo Artik '/gunsonu' komutunu sorunsuz kullanabilirsiniz.
echo ==========================================
pause
