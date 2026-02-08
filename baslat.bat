@echo off
echo ==========================================
echo V12 TITANIUM BASLATILIYOR...
echo ==========================================
echo.

echo 1. Backend (Python API) aciliyor...
start "V12 Backend" cmd /k "call .\venv\Scripts\activate & python main.py"

echo.
echo 2. Frontend (React Arayuz) aciliyor...
cd frontend
start "V12 Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ==========================================
echo SISTEM ACILDI!
echo Tarayicidan su adrese gidin: http://localhost:5173
echo ==========================================
pause