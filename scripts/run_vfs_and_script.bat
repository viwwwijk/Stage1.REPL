@echo off
rem Запуск эмулятора с обоими параметрами одновременно.
cd /d "%~dp0.."
call run.bat --vfs-path examples\vfs-stub.csv --script-path examples\start_error.txt
