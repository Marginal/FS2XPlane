/*
 * Create a fake FSX installation under Wine.
 */

#define UNICODE
#define _UNICODE

#include <windows.h>
#include <shlobj.h>
#include <stdio.h>

int main(int argc, char *argv[])
{
    TCHAR szBuffer[MAX_PATH], szPath[MAX_PATH];
    DWORD size=MAX_PATH;
    HKEY hKey;
    
    /* FS 9 */
    if (RegCreateKey(HKEY_LOCAL_MACHINE, TEXT("SOFTWARE\\Microsoft\\Microsoft Games\\Flight Simulator\\9.0"), &hKey))
        exit(EXIT_FAILURE);
    if (RegQueryValueEx(hKey, TEXT("EXE Path"), NULL, NULL, (LPBYTE) szBuffer, &size) ||
        !ExpandEnvironmentStrings(szBuffer, szPath, MAX_PATH))
    {
        /* FS9 key doesn't exist */
        if (SHGetFolderPath(NULL, CSIDL_PROGRAM_FILES, NULL, SHGFP_TYPE_CURRENT, szPath))
	    exit(EXIT_FAILURE);
        wcscat(szPath, TEXT("\\Microsoft Games\\Flight Simulator 9\\"));
        RegSetValueEx(hKey, TEXT("EXE Path"), NULL, REG_SZ, (LPBYTE) szPath, 2*wcslen(szPath));
    }

    if (RegCreateKey(HKEY_LOCAL_MACHINE, TEXT("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Flight Simulator 9.0"), &hKey))
        exit(EXIT_FAILURE);
    if (RegQueryValueEx(hKey, TEXT("InstallLocation"), NULL, NULL, NULL, NULL))
    {
        RegSetValueEx(hKey, TEXT("InstallLocation"), NULL, REG_SZ, (LPBYTE) szPath, 2*wcslen(szPath));
    }
    RegCloseKey(hKey);

    /* FS X */
    if (RegCreateKey(HKEY_LOCAL_MACHINE, TEXT("SOFTWARE\\Microsoft\\Microsoft Games\\Flight Simulator\\10.0"), &hKey))
        exit(EXIT_FAILURE);
    if (RegQueryValueEx(hKey, TEXT("SetupPath"), NULL, NULL, (LPBYTE) szBuffer, &size) ||
        !ExpandEnvironmentStrings(szBuffer, szPath, MAX_PATH))
    {
        /* FSX key doesn't exist */
        if (SHGetFolderPath(NULL, CSIDL_PROGRAM_FILES, NULL, SHGFP_TYPE_CURRENT, szPath))
	    exit(EXIT_FAILURE);
        wcscat(szPath, TEXT("\\Microsoft Games\\Microsoft Flight Simulator X\\"));
        RegSetValueEx(hKey, TEXT("SetupPath"), NULL, REG_SZ, (LPBYTE) szPath, 2*wcslen(szPath));
    }
    RegCloseKey(hKey);

    if (RegCreateKey(HKEY_CURRENT_USER, TEXT("SOFTWARE\\Microsoft\\Microsoft Games\\Flight Simulator\\10.0"), &hKey))
        exit(EXIT_FAILURE);
    if (RegQueryValueEx(hKey, TEXT("AppPath"), NULL, NULL, NULL, NULL))
    {
        RegSetValueEx(hKey, TEXT("AppPath"), NULL, REG_SZ, (LPBYTE) szPath, 2*wcslen(szPath));
    }
    RegCloseKey(hKey);
    
    if (RegCreateKey(HKEY_LOCAL_MACHINE, TEXT("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{9527A496-5DF9-412A-ADC7-168BA5379CA6}"), &hKey))
        exit(EXIT_FAILURE);
    // RegSetValueEx(hKey, "DisplayName", 0, REG_SZ, (BYTE*) szName, strlen(szName));
    if (RegQueryValueEx(hKey, TEXT("InstallLocation"), NULL, NULL, NULL, NULL))
    {
        RegSetValueEx(hKey, TEXT("InstallLocation"), NULL, REG_SZ, (LPBYTE) szPath, 2*wcslen(szPath));
    }
    RegCloseKey(hKey);
    
    exit(EXIT_SUCCESS);
}
