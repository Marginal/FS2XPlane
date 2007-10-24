#include <windows.h>
#include <shlobj.h>
#include <stdio.h>

const char szName[]="Fake FS2004";

int main(int argc, char *argv[])
{
    TCHAR szProgramFiles[MAX_PATH], szPath[MAX_PATH];
    HKEY hKey;
    
    if (!(SUCCEEDED(SHGetFolderPath(NULL, CSIDL_PROGRAM_FILES, NULL, SHGFP_TYPE_CURRENT, szProgramFiles))))
	    exit(EXIT_FAILURE);

    /* FS 9 */
    strcpy(szPath, szProgramFiles);
    strcat(szPath, "\\Microsoft Games\\Flight Simulator 9");

    RegCreateKey(HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Microsoft Games\\Flight Simulator\\9.0", &hKey);
    RegSetValueEx(hKey, "EXE Path", 0, REG_SZ, (BYTE*) szPath, strlen(szPath));
    RegCloseKey(hKey);

    RegCreateKey(HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Flight Simulator 9.0", &hKey);
    // RegSetValueEx(hKey, "DisplayName", 0, REG_SZ, (BYTE*) szName, strlen(szName));
    RegSetValueEx(hKey, "InstallLocation", 0, REG_SZ, (BYTE*) szPath, strlen(szPath));
    RegCloseKey(hKey);

    /* FS X */
    strcpy(szPath, szProgramFiles);
    strcat(szPath, "\\Microsoft Games\\Microsoft Flight Simulator X");

    RegCreateKey(HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Microsoft Games\\Flight Simulator\\10.0", &hKey);
    RegSetValueEx(hKey, "SetupPath", 0, REG_SZ, (BYTE*) szPath, strlen(szPath));
    RegCloseKey(hKey);

    RegCreateKey(HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Microsoft Games\\Flight Simulator\\10.0", &hKey);
    RegSetValueEx(hKey, "AppPath", 0, REG_SZ, (BYTE*) szPath, strlen(szPath));
    RegCloseKey(hKey);
    
    RegCreateKey(HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{9527A496-5DF9-412A-ADC7-168BA5379CA6}", &hKey);
    // RegSetValueEx(hKey, "DisplayName", 0, REG_SZ, (BYTE*) szName, strlen(szName));
    RegSetValueEx(hKey, "InstallLocation", 0, REG_SZ, (BYTE*) szPath, strlen(szPath));
    RegCloseKey(hKey);
    
    exit(EXIT_SUCCESS);
}
