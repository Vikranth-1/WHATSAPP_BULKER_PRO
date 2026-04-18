@echo off
echo Building WhatsApp Bulk Messenger Desktop App...
echo Installing required build tools...
pip install pyinstaller

echo Starting PyInstaller Build...
pyinstaller --noconfirm --onefile --windowed ^
 --add-data "templates;templates" ^
 --add-data "static;static" ^
 --name "WhatsAppBulker" ^
 main.py

echo.
echo Build complete! Your executable is in the 'dist' folder.
pause
