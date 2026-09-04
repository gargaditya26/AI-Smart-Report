@echo off
setlocal
cd /d "%~dp0"
echo ========================================
echo SmartReports - Windows Setup / Start
echo ========================================

echo [1/3] Installing backend dependencies...
cd backend
py -m pip install -r requirements.txt
if errorlevel 1 (
  echo Backend dependency installation failed.
  pause
  exit /b 1
)

start "SmartReports Backend" cmd /k "cd /d "%~dp0backend" && py -m uvicorn main:app --reload --port 8000"

cd /d "%~dp0frontend"
echo [2/3] Installing frontend dependencies...
npm install
if errorlevel 1 (
  echo Frontend dependency installation failed.
  pause
  exit /b 1
)

start "SmartReports Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"
timeout /t 4 /nobreak >nul
start http://localhost:5173

echo [3/3] SmartReports started.
echo Frontend: http://localhost:5173
echo Backend:  http://127.0.0.1:8000
echo.
pause
