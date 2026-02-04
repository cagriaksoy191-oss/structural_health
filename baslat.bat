@echo off
echo ==========================================
echo SISTEM BASLATILIYOR...
echo ==========================================
echo.

echo 1. Web sitesi aciliyor...
start index.html

echo.
echo 2. Yapay Zeka Motoru calistiriliyor...
echo.
echo LUTFEN BU SIYAH EKRANI KAPATMA!
echo.

.\venv\Scripts\uvicorn.exe main:app --reload

pause