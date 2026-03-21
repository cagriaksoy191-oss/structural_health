@echo off
cd /d "%~dp0"
echo ==========================================
echo KURULUM BASLIYOR
echo ==========================================
echo.

REM --- Node.js Kontrolu ---
call npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] npm -Node.js- bulunamadi. Frontend paketlerini kurmak icin npm gereklidir.
    echo Lutfen Node.js yukleyip tekrar deneyin.
    pause
    exit /b 1
)

REM --- Python / py Fallback Karari ---
set PYTHON_CMD=
call python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto PYTHON_FOUND
)

call py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py -3"
    goto PYTHON_FOUND
)

echo [HATA] Python sisteminizde bulunamadi veya PATH degiskenine eklenmemis.
echo Lutfen Python 3.x kurup tekrar deneyin.
pause
exit /b 1

:PYTHON_FOUND
echo [BILGI] Python yorumlayicisi bulundu: %PYTHON_CMD%
echo.

REM --- VENV Kontrolu ve Olusturma ---
set "VENV_DIR="
if exist ".venv\Scripts\python.exe" (
    set "VENV_DIR=.venv"
    goto VENV_FOUND
)
if exist "venv\Scripts\python.exe" (
    set "VENV_DIR=venv"
    goto VENV_FOUND
)
if exist ".venv" (
    echo [HATA] Mevcut kismen olusturulmus veya bozuk bir sanal ortam bulundu -.venv-
    echo Lutfen o klasoru manuel silip kurulumu bastan baslatin.
    pause
    exit /b 1
)
if exist "venv" (
    echo [HATA] Mevcut kismen olusturulmus veya bozuk bir sanal ortam bulundu -venv-
    echo Lutfen o klasoru manuel silip kurulumu bastan baslatin.
    pause
    exit /b 1
)

echo 1. Sanal ortam olusturuluyor...
%PYTHON_CMD% -m venv .venv
if %errorlevel% neq 0 (
    echo [HATA] Sanal ortam olusturulurken hata meydana geldi.
    pause
    exit /b 1
)
set "VENV_DIR=.venv"

:VENV_FOUND
echo 1. Sanal ortam hazir: %VENV_DIR%
echo.
echo 2. Python bagimliliklari -requirements.txt- yukleniyor...
echo Bu islem internet hizina gore bagli olarak surebilir, bekleyin.
echo.

"%~dp0%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [UYARI] pip guncellenemedi, devam ediliyor.
)

"%~dp0%VENV_DIR%\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"
if %errorlevel% neq 0 (
    echo [HATA] Python paketleri -requirements.txt- kurulurken hata olustu.
    pause
    exit /b 1
)

echo.
echo 3. Frontend paketleri yukleniyor...
pushd "%~dp0frontend"
call npm install
if %errorlevel% neq 0 (
    echo [HATA] Frontend paketleri -npm install- kurulurken hata olustu.
    popd
    pause
    exit /b 1
)
popd

echo.
echo ==========================================
echo KURULUM BITTI!
echo Artik baslat.bat dosyasina tiklayabilirsiniz.
echo ==========================================
pause