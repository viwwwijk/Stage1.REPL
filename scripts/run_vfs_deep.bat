@echo off
rem Этап 3: VFS с вложенностью не менее 3 уровней файлов и папок.
cd /d "%~dp0.."
call run.bat --vfs-path examples\vfs\deep.csv --script-path examples\vfs_show.txt
