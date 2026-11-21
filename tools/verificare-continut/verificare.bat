@echo off
cd /d "%~dp0"
python verificare.py %*
if errorlevel 1 pause
