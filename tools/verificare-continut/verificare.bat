@echo off
cd /d "%~dp0"
python verificare.py
start "" raport.html
pause
