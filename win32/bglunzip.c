#include <windows.h>	/* required by bglzip.h */
#include <stdio.h>
#include "bglzip.h"

int main(int argc, char *argv[])
{
	DWORD size;
	PVOID data;
	DWORD result;
	FILE *out;

	if (argc!=3)
	{
		printf("Usage: %s <compressed file> <outfile>\n", argv[0]);
		exit(1);
	}

	result = FSGetUncompressedBGLData(argv[1], &size, &data);
	if (result==BGLZIP_OK)
	{
		out=fopen(argv[2], "wb");
		if (fwrite(data, size, 1, out)!=1)
		{
			fprintf(stderr, "Can't write %s, error %d\n", argv[2], errno);
			exit(errno);
		}
		fclose(out);
		FSCompleteBGLOperation(size, data);
	}
	else
	{
		fprintf(stderr, "Can't decompress %s, error %d\n", argv[1], result);
	}
	exit(result);
}
