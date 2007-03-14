@echo off
@setlocal

for /f "usebackq tokens=1,2" %%I in (`c:\Progra~1\Python24\python.exe -c "from version import appversion; print '%%4.2f %%d'%%(appversion, round(appversion*100,0))"`) do (set VERSION=%%I&set VER=%%J)

set RELEASE=1
set RPM=%TMP%\fs2xplane

@if exist FS2XPlane_%VER%_src.zip del FS2XPlane_%VER%_src.zip
@if exist fs2xplane-%VERSION%-%RELEASE%.i386.rpm del fs2xplane-%VERSION%-%RELEASE%.i386.rpm
@if exist fs2xplane_%VERSION%-%RELEASE%_i386.deb del fs2xplane_%VERSION%-%RELEASE%_i386.deb
@if exist FS2XPlane_%VER%_mac.zip del FS2XPlane_%VER%_mac.zip
@if exist FS2XPlane_%VER%_win32.zip del FS2XPlane_%VER%_win32.exe

if exist FS2XPlane.app rd /s /q FS2XPlane.app >nul: 2>&1
if exist "%RPM%" rd /s /q "%RPM%"
del /s /q dist >nul:  2>&1
REM del /s /q *.bak >nul: 2>&1
del /s /q *.pyc >nul: 2>&1

@set PY=fs2xp.py FS2XPlane.py convbgl.py convmain.py convobjs.py convtaxi.py convutil.py convxml.py MessageBox.py version.py
@set DATA=FS2XPlane.html bglxml.copying.txt
@set RSRC=Resources/*.obj Resources/blank.png Resources/gaspump1.r8.png Resources/FS2X-palette.png Resources/transparent.png Resources/Tree_side.png "Resources/library objects.txt" Resources/FS2XPlane.png

@REM source
zip -r FS2XPlane_%VER%_src.zip dist.cmd %PY% %DATA% %RSRC% linux MacOS win32 |findstr -vc:"adding:"

@REM linux
REM tar -zcf FS2XPlane_%VER%_linux.tar.gz %PY% %DATA% %RSRC% linux win32/bglunzip.exe win32/DSFTool.exe
set RPMRT=%TMP%\fs2xplane\root
mkdir "%RPM%\BUILD"
mkdir "%RPM%\SOURCES"
mkdir "%RPM%\RPMS\i386"
mkdir "%RPMRT%\usr\local\bin"
mkdir "%RPMRT%\usr\local\lib\fs2xplane\Resources"
mkdir "%RPMRT%\usr\local\lib\fs2xplane\linux"
mkdir "%RPMRT%\usr\local\lib\fs2xplane\win32"
copy linux\fs2xplane.desktop "%RPMRT%\usr\local\lib\fs2xplane" |findstr -v "file(s) copied"
copy linux\FS2XPlane.xpm "%RPM%\SOURCES" |findstr -v "file(s) copied"
echo BuildRoot: /tmp/fs2xplane/root > "%RPM%\fs2xplane.spec"
echo Version: %VERSION% >> "%RPM%\fs2xplane.spec"
echo Release: %RELEASE% >> "%RPM%\fs2xplane.spec"
type linux\fs2xplane.spec    >> "%RPM%\fs2xplane.spec"
copy linux\fs2xp "%RPMRT%\usr\local\bin" |findstr -v "file(s) copied"
copy linux\fs2xplane "%RPMRT%\usr\local\bin" |findstr -v "file(s) copied"
for %%I in (%DATA%) do (copy %%I "%RPMRT%\usr\local\lib\fs2xplane" |findstr -v "file(s) copied")
for %%I in (%PY%) do (copy %%I "%RPMRT%\usr\local\lib\fs2xplane" |findstr -v "file(s) copied")
for %%I in (%RSRC%) do (copy "Resources\%%~nxI" "%RPMRT%\usr\local\lib\fs2xplane\Resources" |findstr -v "file(s) copied")
for %%I in (linux\bglunzip linux\bglxml linux\bmp2png linux\DSFTool linux\fake2004) do (copy %%I "%RPMRT%\usr\local\lib\fs2xplane\linux" |findstr -v "file(s) copied")
for %%I in (win32\bglunzip.exe win32\DSFTool.exe win32\fake2004.exe) do (copy %%I "%RPMRT%\usr\local\lib\fs2xplane\win32" |findstr -v "file(s) copied")
"C:\Program Files\cygwin\lib\rpm\rpmb.exe" --quiet -bb --target i386-pc-linux --define '_topdir /tmp/fs2xplane' /tmp/fs2xplane/fs2xplane.spec
move "%RPM%\RPMS\i386\fs2xplane-%VERSION%-%RELEASE%.cygwin.i386.rpm" fs2xplane-%VERSION%-%RELEASE%.i386.rpm
REM Debian/Ubuntu
mkdir "%RPMRT%\DEBIAN"
mkdir "%RPMRT%\usr\share\applications"
mkdir "%RPMRT%\usr\share\icons\hicolor\48x48\apps"
copy linux\fs2xplane.desktop "%RPMRT%\usr\share\applications" |findstr -v "file(s) copied"
copy Resources\Fs2xplane.png "%RPMRT%\usr\share\icons\hicolor\48x48\apps\fs2xplane.png" |findstr -v "file(s) copied"
echo Version: %VERSION%-%RELEASE% > "%RPMRT%\DEBIAN\control"
type linux\control >> "%RPMRT%\DEBIAN\control"
copy linux\postinst "%RPMRT%\DEBIAN" |findstr -v "file(s) copied"
REM copy linux\postrm   "%RPMRT%\DEBIAN" |findstr -v "file(s) copied"
chmod -R 755 "%RPMRT%"
for /r "%RPMRT%" %%I in (*) do chmod 644 "%%I"
chmod -R 755 "%RPMRT%\DEBIAN\postinst"
REM chmod -R 755 "%RPMRT%\DEBIAN\postrm"
chmod -R 755 "%RPMRT%\usr\local\bin\fs2xp"
chmod -R 755 "%RPMRT%\usr\local\bin\fs2xplane"
chmod -R 755 "%RPMRT%\usr\local\lib\fs2xplane\linux"
chmod -R 755 "%RPMRT%\usr\local\lib\fs2xplane\win32"
chown -R root:root "%RPMRT%"
dpkg-deb -b /tmp/fs2xplane/root .
chown -R %USERNAME% "%RPMRT%"

@REM mac
mkdir FS2XPlane.app\Contents\MacOS
xcopy /q /e MacOS FS2XPlane.app\Contents\MacOS\ |findstr -v "file(s) copied"
for %%I in (%PY%) do (copy %%I FS2XPlane.app\Contents\MacOS\ |findstr -v "file(s) copied")
mkdir FS2XPlane.app\Contents\MacOS\win32
for %%I in (win32\bglunzip.exe win32\fake2004.exe) do (copy %%I FS2XPlane.app\Contents\MacOS\win32 |findstr -v "file(s) copied")
mkdir FS2XPlane.app\Contents\Resources
for %%I in (%DATA%) do (copy %%I FS2XPlane.app\Contents\Resources\ |findstr -v "file(s) copied")
for %%I in (%RSRC%) do (copy "Resources\%%~nxI" FS2XPlane.app\Contents\Resources\ |findstr -v "file(s) copied")
copy Resources\trees_0.bgl FS2XPlane.app\Contents\Resources\ |findstr -v "file(s) copied")
move FS2XPlane.app\Contents\MacOS\Info.plist FS2XPlane.app\Contents\
move FS2XPlane.app\Contents\MacOS\FS2XPlane.icns FS2XPlane.app\Contents\Resources\
zip -r FS2XPlane_%VER%_mac.zip FS2XPlane.app |findstr -vc:"adding:"

@REM win32
win32\setup.py -q py2exe
REM @set cwd="%CD%"
REM cd dist
REM zip -r ..\FS2XPlane_%VER%_win32.zip * |findstr -vc:"adding:"
"C:\Program Files\NSIS\makensis.exe" /nocd /v2 win32\FS2XPlane.nsi
REM @cd %cwd%
rd  /s /q build

:end
