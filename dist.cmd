@echo off

for /f "usebackq tokens=1,2" %%I in (`python.exe -c "from version import appversion; print '%%4.2f %%d'%%(appversion, round(appversion*100,0))"`) do (set VERSION=%%I&set VER=%%J)

if exist build rd /s /q build
python -OO win32\setup.py -q py2exe
"C:\Program Files\NSIS\makensis.exe" /nocd /v2 win32\FS2XPlane.nsi
REM rd  /s /q build
