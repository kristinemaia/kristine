@echo off
cd /d "%~dp0"
set PY=python
where py >nul 2>nul && set PY=py
%PY% verificare.py --cauta
if errorlevel 1 pause
