fake2004.exe: fake2004.c
	cl -D_CRT_SECURE_NO_DEPRECATE -Ox -TP -MT fake2004.c /link shell32.lib Advapi32.lib
