@echo off
cd /d "%~dp0"
python verificare.py --raport
if errorlevel 1 pause
