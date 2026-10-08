@echo off
rem Этап 4: ошибки ls, cd, find и wc, по одному стартовому скрипту на случай.
rem Окна открываются по очереди: закройте окно, чтобы открылось следующее.
cd /d "%~dp0.."
for %%s in (examples\stage4_errors\*.txt) do call run.bat --vfs-path examples\vfs\deep.csv --script-path %%s
