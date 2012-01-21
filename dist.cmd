@echo off
if exist build rd /s /q build
python -OO win32\setup.py -q py2exe
"C:\Program Files\NSIS\makensis.exe" /nocd /v2 win32\FS2XPlane.nsi
REM rd  /s /q build
