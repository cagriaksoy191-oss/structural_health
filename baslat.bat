@echo off
cd /d "%~dp0"
echo ==========================================
echo V12 TITANIUM BASLATILIYOR...
echo ==========================================
echo.

REM --- VENV Kontrolu ---
set "VENV_DIR="
if exist ".venv\Scripts\python.exe" (
    set "VENV_DIR=.venv"
) else if exist "venv\Scripts\python.exe" (
    set "VENV_DIR=venv"
)

if "%VENV_DIR%"=="" (
    echo [HATA] Sanal ortam bozuk veya eksik -Scripts\python.exe bulunamadi-
    echo Lutfen projeyi baslatmadan once kurulum.bat dosyasini calistirin.
    pause
    exit /b 1
)

REM --- node_modules Kontrolu ---
if not exist "frontend\node_modules" (
    echo [HATA] Frontend paketleri -node_modules- bulunamadi!
    echo Lutfen projeyi baslatmadan once kurulum.bat ile kurulumlari tamamlayin.
    pause
    exit /b 1
)

REM --- npm Kontrolu ---
call npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] npm -Node.js- komutu sistemde bulunamadi!
    echo Lutfen Node.js yukleyin veya PATH ayarinizi kontrol edin.
    pause
    exit /b 1
)

REM --- .env Kontrolu ---
if not exist ".env" (
    echo [UYARI] .env dosyasi bulunamadi! Uygulama API anahtarlari olmadan kisitli calisabilir.
)

echo.
echo 1. Backend API aciliyor...
start "V12 Backend" cmd /k "%VENV_DIR%\Scripts\python.exe" main.py

echo 2. Frontend React Arayuz aciliyor...
start "V12 Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ==========================================
echo SISTEM ACILDI!
echo Tarayicidan su adrese gidin: http://localhost:5173
echo ==========================================
pause