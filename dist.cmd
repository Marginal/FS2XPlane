@echo off
@setlocal

for /f "usebackq" %%I in (`c:\Progra~1\Python24\python.exe -c "from convutil import version; print '%%03.0f'%%(float(version)*100)"`) do set VER=%%I

@if exist FS2XPlane_%VER%_src.zip del FS2XPlane_%VER%_src.zip
@if exist FS2XPlane_%VER%_linux.tar.gz del FS2XPlane_%VER%_linux.tar.gz
@if exist FS2XPlane_%VER%_mac.zip del FS2XPlane_%VER%_mac.zip
@if exist FS2XPlane_%VER%_win32.zip del FS2XPlane_%VER%_win32.zip

rd  /s /q FS2XPlane.app
del /s /q dist >nul:  2>&1
del /s /q *.bak >nul: 2>&1
del /s /q *.pyc >nul: 2>&1

@set PY=fs2x.py FS2XPlane.py convbgl.py convmain.py convobjs.py convutil.py convxml.py
@set DATA=FS2XPlane.html bglxml.copying.txt
@set RSRC=Resources/*.obj Resources/FS2X-ApronLight.png Resources/FS2X-ApronLight_LIT.png Resources/FS2X-palette.png Resources/FS2X-Taxi.png Resources/FS2X-Taxi_LIT.png Resources/Tree_side.png Resources/objfile.txt Resources/FS2XPlane.png

@REM source
zip -r FS2XPlane_%VER%_src.zip dist.cmd %PY% setup.py %DATA% %RSRC% linux MacOS win32/*.exe win32/*.ico |findstr -vc:"adding:"

@REM linux
tar -zcf FS2XPlane_%VER%_linux.tar.gz %PY% %DATA% %RSRC% linux win32/bglunzip.exe win32/DSFTool.exe

@REM mac
mkdir FS2XPlane.app\Contents\MacOS
xcopy /q MacOS\* FS2XPlane.app\Contents\MacOS\ |findstr -v "file(s) copied"
for %%I in (%PY%) do (copy %%I FS2XPlane.app\Contents\MacOS\ |findstr -v "file(s) copied")
mkdir FS2XPlane.app\Contents\Resources
for %%I in (%DATA%) do (copy %%I FS2XPlane.app\Contents\Resources\ |findstr -v "file(s) copied")
for %%I in (%RSRC%) do (copy Resources\%%~nxI FS2XPlane.app\Contents\Resources\ |findstr -v "file(s) copied")
copy Resources\trees_0.bgl FS2XPlane.app\Contents\Resources\ |findstr -v "file(s) copied")
move FS2XPlane.app\Contents\MacOS\Info.plist FS2XPlane.app\Contents\
move FS2XPlane.app\Contents\MacOS\FS2XPlane.icns FS2XPlane.app\Contents\Resources\
zip -r FS2XPlane_%VER%_mac.zip FS2XPlane.app |findstr -vc:"adding:"

@REM win32
setup.py -q py2exe
REM @set cwd="%CD%"
REM cd dist
REM zip -r ..\FS2XPlane_%VER%_win32.zip * |findstr -vc:"adding:"
"C:\Program Files\NSIS\makensis.exe" /nocd /v2 win32\FS2XPlane.nsi
REM @cd %cwd%
rd  /s /q build

:end
