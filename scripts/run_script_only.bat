@echo off
rem Запуск эмулятора с параметром --script-path.
cd /d "%~dp0.."
call run.bat --script-path examples\start_ok.txt
