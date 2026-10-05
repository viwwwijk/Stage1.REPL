@echo off
rem Запуск эмулятора с обоими параметрами одновременно.
cd /d "%~dp0.."
call run.bat --vfs-path examples\vfs\minimal.csv --script-path examples\start_error.txt
