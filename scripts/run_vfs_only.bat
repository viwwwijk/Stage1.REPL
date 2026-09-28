@echo off
rem Запуск эмулятора с параметром --vfs-path.
cd /d "%~dp0.."
call run.bat --vfs-path examples\vfs-stub.csv
