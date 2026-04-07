@echo off
title Cazador De Chambas
cd /d "%~dp0"
echo Activando entorno virtual...
call .\venv\Scripts\activate
echo Iniciando Cazador de Chambas...
python main.py
pause
