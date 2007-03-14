@echo off
setlocal

set FSDIR=%PROGRAMFILES%\Microsoft Games\Flight Simulator 9
set TMPFILE="%TEMP%\fs2004.reg"
if not defined TEMP set TMPFILE="%TMP%\fs2004.reg"

if not exist "%FSDIR%\fs9.exe" goto ok
echo Found a copy of Flight Simulator already installed in
echo.
echo "%FSDIR%"
echo.
echo Aborting!
goto :end

:ok
REM Create main FS2004 key
echo REGEDIT4>%TMPFILE%
echo.>>%TMPFILE%
echo [HKEY_LOCAL_MACHINE\Software\Microsoft\Microsoft Games\Flight Simulator\9.0]>>%TMPFILE%
for /d %%I in ("%PROGRAMFILES%") do set ESCDIR=%%~dI\\%%~nxI\\Microsoft Games\\Flight Simulator 9
echo "EXE Path"="%ESCDIR%">>%TMPFILE%
%SystemRoot%\regedit.exe /s %TMPFILE%

REM Create FS2004 dirs
if not exist "%FSDIR%\Addon Scenery" mkdir "%FSDIR%\Addon Scenery"
if not exist "%FSDIR%\Addon Scenery\scenery" mkdir "%FSDIR%\Addon Scenery\scenery"
if not exist "%FSDIR%\Addon Scenery\texture" mkdir "%FSDIR%\Addon Scenery\texture"
if not exist "%FSDIR%\Effects" mkdir "%FSDIR%\Effects"
if not exist "%FSDIR%\Scenery" mkdir "%FSDIR%\Scenery"
if not exist "%FSDIR%\Texture" mkdir "%FSDIR%\Texture"

REM Create dummy files
echo.>"%FSDIR%\fs9.exe"

echo [General]>"%FSDIR%\scenery.cfg"
echo Title=FS9 World Scenery>>"%FSDIR%\scenery.cfg"
echo Description=FS9 Scenery Data>>"%FSDIR%\scenery.cfg"
echo.>>"%FSDIR%\scenery.cfg"
echo [Area.001]>>"%FSDIR%\scenery.cfg"
echo Title=Addon Scenery>>"%FSDIR%\scenery.cfg"
echo Local=Addon Scenery>>"%FSDIR%\scenery.cfg"
echo Layer=1 >>"%FSDIR%\scenery.cfg"
echo Active=TRUE>>"%FSDIR%\scenery.cfg"
echo Required=FALSE>>"%FSDIR%\scenery.cfg"

:end
