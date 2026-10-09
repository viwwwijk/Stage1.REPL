@echo off
rem Этап 5: ошибки rmdir, по одному стартовому скрипту на случай.
rem Окна открываются по очереди: закройте окно, чтобы открылось следующее.
cd /d "%~dp0.."
for %%s in (examples\stage5_errors\*.txt) do call run.bat --vfs-path examples\vfs\rmdir.csv --script-path %%s
