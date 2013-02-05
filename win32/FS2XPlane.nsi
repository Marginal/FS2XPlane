; NSIS installation

;--------------------------------
!include "MUI.nsh"

!define MUI_ABORTWARNING

SetCompressor /SOLID lzma
RequestExecutionLevel admin

Name "FS2XPlane $%VERSION%"
Caption "FS2XPlane $%VERSION% Installer"
OutFile "FS2XPlane_$%VER%_win32.exe"
InstallDir "$PROGRAMFILES\FS2XPlane"
BrandingText "http://marginal.org.uk/x-planescenery"

; !insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; !insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Icon "win32\installer.ico"
UninstallIcon "win32\installer.ico"

Var True
Var False

; consumes top stack entry, trashes $0,$1
Function makescenery
  Pop $0	; containing folder
  IfFileExists "$0\scenery.cfg" makescenerydone
  CreateDirectory $0
  FileOpen $1 "$0\scenery.cfg" "a"
  FileWrite $1 "[General]$\r$\nTitle=FS9 World Scenery$\r$\nDescription=FS9 Scenery Data$\r$\n$\r$\n[Area.001]$\r$\nTitle=Addon Scenery$\r$\nLocal=Addon Scenery$\r$\nRemote=$\r$\nActive=TRUE$\r$\nRequired=FALSE$\r$\nLayer=1$\r$\n$\r$\n"
  FileClose $1
  makescenerydone:
FunctionEnd

; Consumes top two stack entries, trashes $0,$1,$2
Function makefsroot
  Pop $1	; isfsx
  Pop $0	; path
  CreateDirectory $0
  CreateDirectory "$0\Addon Scenery"
  CreateDirectory "$0\Addon Scenery\scenery"
  CreateDirectory "$0\Addon Scenery\texture"
  CreateDirectory "$0\Effects"
  CreateDirectory "$0\Flights"
  CreateDirectory "$0\Scenery"
  CreateDirectory "$0\Texture"
  FileOpen $2 "$0\fs2002.exe" "a"
  FileClose $2
  FileOpen $2 "$0\fs9.exe" "a"
  FileClose $2
  StrCmp $1 $False domakescenery
  CreateDirectory "$0\SimObjects"
  FileOpen $2 "$0\fsx.exe" "a"
  FileClose $2
  domakescenery:
  Push $0
  Call makescenery
FunctionEnd


Section "Install"
  StrCpy $True "true"
  StrCpy $False "false"

  SetOutPath "$INSTDIR"
  File /r dist\*

  Delete "$INSTDIR\FS2XPlane.exe.log"
  SetShellVarContext current
  Delete "$SMPROGRAMS\FS2XPlane.lnk"	; old versions used current user
  SetShellVarContext all
  CreateShortCut "$SMPROGRAMS\FS2XPlane.lnk" "$INSTDIR\FS2XPlane.exe"

  ; uninstall info
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "DisplayIcon" "$INSTDIR\FS2XPlane.exe,0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "DisplayName" "FS2XPlane"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "DisplayVersion" "$%VERSION%"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "Publisher" "Jonathan Harris <x-plane@marginal.org.uk>"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "NoRepair" 1
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OverlayEditor" "URLInfoAbout" "mailto:Jonathan Harris <x-plane@marginal.org.uk>?subject=FS2XPlane $%VERSION%"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "URLUpdateInfo" "http://marginal.org.uk/x-planescenery"

  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; create fake fs9
  ;Var /GLOBAL fs9root
  ;Var /GLOBAL newfs9root
  ;StrCpy $newfs9root $False
  ;ReadRegStr $fs9root HKLM "SOFTWARE\Microsoft\Microsoft Games\Flight Simulator\9.0" "EXE Path"
  ;ExpandEnvStrings $fs9root $fs9root
  ;StrCmp $fs9root "" +1 fs9
  ;ReadRegStr $fs9root HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Flight Simulator 9.0" "InstallLocation"
  ;ExpandEnvStrings $fs9root $fs9root
  ;StrCmp $fs9root "" fs9notinstalled
  ;WriteRegStr HKLM "SOFTWARE\Microsoft\Microsoft Games\Flight Simulator\9.0" "EXE Path" $fs9root
  ;goto fs9
  ;
  ;fs9notinstalled:
  ;StrCpy $fs9root "$PROGRAMFILES\Microsoft Games\Flight Simulator 9\"
  ;WriteRegStr HKLM "SOFTWARE\Microsoft\Microsoft Games\Flight Simulator\9.0" "EXE Path" $fs9root
  ;WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Flight Simulator 9.0" "InstallLocation" $fs9root
  ;goto fs9
  ;
  ;fs9:
  ;IfFileExists "$fs9root\fs9.exe" fs9done
  ;StrCpy $newfs9root $True
  ;Push $fs9root
  ;Push $False	; not fsx
  ;Call makefsroot
  ;fs9done:

  ; create fake fsx
  Var /GLOBAL fsxroot
  Var /GLOBAL newfsxroot
  StrCpy $newfsxroot $False
  ReadRegStr $fsxroot HKLM "SOFTWARE\Microsoft\Microsoft Games\Flight Simulator\10.0" "SetupPath"
  ExpandEnvStrings $fsxroot $fsxroot
  StrCmp $fsxroot "" +1 fsx
  ReadRegStr $fsxroot HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{9527A496-5DF9-412A-ADC7-168BA5379CA6}" "InstallLocation"
  ExpandEnvStrings $fsxroot $fsxroot
  StrCmp $fsxroot "" fsxnotinstalled
  WriteRegStr HKLM "SOFTWARE\Microsoft\Microsoft Games\Flight Simulator\10.0" "SetupPath" $fsxroot
  goto fsx

  fsxnotinstalled:
  ReadRegStr $fsxroot HKCU "SOFTWARE\Microsoft\Microsoft Games\Flight Simulator\10.0" "AppPath"
  ExpandEnvStrings $fsxroot $fsxroot
  StrCmp $fsxroot "" +1 fsxhaveapppath
  StrCpy $fsxroot "$PROGRAMFILES\Microsoft Games\Microsoft Flight Simulator X\"
  fsxhaveapppath:
  WriteRegStr HKLM "SOFTWARE\Microsoft\Microsoft Games\Flight Simulator\10.0" "SetupPath" $fsxroot
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{9527A496-5DF9-412A-ADC7-168BA5379CA6}" "InstallLocation" $fsxroot
  goto fsx

  fsx:
  IfFileExists "$fsxroot\fsx.exe" fsxdone
  StrCpy $newfsxroot $True
  Push $fsxroot
  Push $True	; fsx
  Call makefsroot
  fsxdone:

  ; create fake fsx appdata
  Push "$APPDATA\Microsoft\FSX"
  Call makescenery

  ; Show message about fake installations
  StrCmp $newfsxroot $True +1 installdone
  MessageBox MB_OK "Created a fake FSX installation. $\n$\nInstall MSFS sceneries under:$\n$fsxroot $\n"
  installdone:

SectionEnd


Section "Uninstall"
  SetShellVarContext current
  Delete "$SMPROGRAMS\FS2XPlane.lnk"	; old versions used current user
  SetShellVarContext all
  Delete "$SMPROGRAMS\FS2XPlane.lnk"
  Delete "$INSTDIR\bglxml.copying.txt"
  Delete "$INSTDIR\Squish_license.txt"
  Delete "$INSTDIR\FakeFS2004.cmd"
  Delete "$INSTDIR\fs2xp.exe"
  Delete "$INSTDIR\FS2XPlane.exe"
  Delete "$INSTDIR\FS2XPlane.exe.log"
  Delete "$INSTDIR\FS2XPlane.html"
  Delete "$INSTDIR\library.zip"
  Delete "$INSTDIR\msvcr90.dll"
  Delete "$INSTDIR\w9xpopen.exe"
  Delete "$INSTDIR\uninstall.exe"
  RMDir /r "$INSTDIR\Microsoft.VC90.CRT"
  RMDir /r "$INSTDIR\Resources"
  RMDir /r "$INSTDIR\win32"
  RMDir "$INSTDIR"

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane"
SectionEnd
