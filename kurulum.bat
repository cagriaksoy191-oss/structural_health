@echo off
echo ==========================================
echo KURULUM BASLIYOR (Requirements Dosyasiz)
echo ==========================================
echo.
echo 1. Sanal ortam (venv) olusturuluyor...
python -m venv venv

echo.
echo 2. Kutuphaneler yukleniyor...
echo (Bu islem internet hizina gore 2-3 dakika surer, bekleyin)
echo.

REM --- BURASI EN ONEMLI YER: Kutuphaneleri direkt yukluyoruz ---
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install fastapi uvicorn pandas numpy scikit-fuzzy requests joblib scikit-learn packaging networkx scipy

echo.
echo ==========================================
echo KURULUM BITTI!
echo Artik 'baslat.bat' dosyasina tiklayabilirsin.
echo ==========================================
pause