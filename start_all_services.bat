@echo off
echo Starting Odoo 17 Docker containers...
docker-compose up -d

echo Waiting for Odoo to start...
timeout /t 5 /nobreak >nul

echo Starting Printer Service (Headless Mode)...
cd PrinterService
"..\.venv\Scripts\python.exe" run_headless.py
pause
