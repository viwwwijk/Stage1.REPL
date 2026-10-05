@echo off
rem Этап 3: ошибки в стартовых скриптах, каждый останавливается на первой ошибке.
rem Окна открываются по очереди: закройте окно, чтобы открылось следующее.
cd /d "%~dp0.."
call run.bat --vfs-path examples\vfs\files.csv --script-path examples\start_error.txt
call run.bat --vfs-path examples\vfs\files.csv --script-path examples\start_quote_error.txt
call run.bat --vfs-path examples\vfs\files.csv --script-path examples\start_exit_error.txt
call run.bat --vfs-path examples\vfs\files.csv --script-path examples\start_conf_error.txt
