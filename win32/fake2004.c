#include <windows.h>
#include <shlobj.h>
#include <stdio.h>

const szName[]="Fake FS2004";

int main(int argc, char *argv[])
{
    TCHAR szPath[MAX_PATH];
    HKEY hKey;
    
    if (!(SUCCEEDED(SHGetFolderPath(NULL, CSIDL_PROGRAM_FILES, NULL, SHGFP_TYPE_CURRENT, szPath))))
	    exit(EXIT_FAILURE);
    strcat(szPath, "\\Microsoft Games\\Flight Simulator 9");

    RegCreateKey(HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Microsoft Games\\Flight Simulator\\9.0", &hKey);
    RegSetValueEx(hKey, "EXE Path", 0, REG_SZ, (BYTE*) szPath, strlen(szPath));
    RegCloseKey(hKey);

    RegCreateKey(HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Flight Simulator 9.0", &hKey);
    // RegSetValueEx(hKey, "DisplayName", 0, REG_SZ, (BYTE*) szName, strlen(szName));
    RegSetValueEx(hKey, "InstallLocation", 0, REG_SZ, (BYTE*) szPath, strlen(szPath));
    RegCloseKey(hKey);

    exit(EXIT_SUCCESS);
}
