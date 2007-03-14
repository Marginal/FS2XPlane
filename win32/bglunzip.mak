bglunzip.exe: bglunzip.c bglzip.lib
	cl -D_CRT_SECURE_NO_DEPRECATE -Ox -TP -MT bglunzip.c /link /nodefaultlib:libc bglzip.lib
