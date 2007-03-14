; NSIS installation

;--------------------------------
!include "MUI.nsh"

!define MUI_ABORTWARNING

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

Section "Install"
  SetOutPath "$INSTDIR"
  File /r dist\*
  CreateShortCut "$SMPROGRAMS\FS2XPlane.lnk" "$INSTDIR\FS2XPlane.exe"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "Contact" "x-plane@marginal.org.uk"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "DisplayIcon" "$INSTDIR\FS2XPlane.exe,0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "DisplayName" "FS2XPlane"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "DisplayVersion" "$%VERSION%"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "Publisher" "Jonathan Harris"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "NoRepair" 1
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane" "URLUpdateInfo" "http://marginal.org.uk/x-planescenery"

WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd


Section "Uninstall"
  Delete "$SMPROGRAMS\FS2XPlane.lnk"
  Delete "$INSTDIR\bglxml.copying.txt"
  Delete "$INSTDIR\FakeFS2004.cmd"
  Delete "$INSTDIR\fs2x.exe"
  Delete "$INSTDIR\FS2XPlane.exe"
  Delete "$INSTDIR\FS2XPlane.html"
  Delete "$INSTDIR\library.zip"
  Delete "$INSTDIR\MSVCR71.dll"
  Delete "$INSTDIR\w9xpopen.exe"
  Delete "$INSTDIR\uninstall.exe"
  RMDir /r "$INSTDIR\Resources"
  RMDir /r "$INSTDIR\win32"
  RMDir "$INSTDIR"

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FS2XPlane"
SectionEnd
