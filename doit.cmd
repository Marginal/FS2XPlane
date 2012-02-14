@echo off
cls
setlocal

set FS=%PROGRAMFILES%\Microsoft Games\Microsoft Flight Simulator X\Addon Scenery
set LB=%FS%
set XP=%USERPROFILE%\Desktop\X-Plane 10 Demo\Custom Scenery


REM set SCN=rjgg151b
set SCN=KSEA


if ."%SCN%".==.. goto bad
set SRC=%FS%\%SCN%
set DST=%XP%\%SCN%
if exist "%DST%" (
	if exist "%DST%\Earth nav data" rd /s /q "%DST%\Earth nav data"
	if exist "%DST%\objects" rd /s /q "%DST%\objects"
	if exist "%DST%\opensceneryx" rd /s /q "%DST%\opensceneryx"
	if exist "%DST%\textures" rd /s /q "%DST%\textures"
	del /q  "%DST%\*"
) else (
	md "%DST%"
)

echo on
fs2xp.py -d -l "%LB%" "%SRC%" "%DST%"
@for %%I in ("%DST%") do @if exist "%%~fI\profile.dmp" postprof.py "%%~fI\profile.dmp" > "%%~fI\profile.txt"
@for %%I in ("%DST%") do @if exist "%%~fI\Earth nav data\apt.dat" postproc.py "%%~fI\Earth nav data\apt.dat"
@goto end

:bad
echo No source and/or target !!!

:end
