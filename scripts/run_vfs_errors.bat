@echo off
rem Этап 3: ошибки загрузки VFS (нет файла, неверный заголовок, неверный base64).
rem Окна открываются по очереди: закройте окно, чтобы открылось следующее.
cd /d "%~dp0.."
call run.bat --vfs-path examples\vfs\missing.csv --script-path examples\vfs_show.txt
call run.bat --vfs-path examples\vfs\broken_header.csv --script-path examples\vfs_show.txt
call run.bat --vfs-path examples\vfs\broken_base64.csv --script-path examples\vfs_show.txt
