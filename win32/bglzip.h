/***
 * bglzip.h - definitions for bgl file decompression
 *
 *       Copyright (c) 1999, Microsoft Corporation. All rights reserved.
 *
 ****/

#ifndef _bglzip_h_
#define _bglzip_h_

/*****
 *
 * ERROR CODES
 *
 *****/

/*
 * BGLZIP_OK 
 * The operation completed successfully.
 */
#define BGLZIP_OK                  0x00000000

/*
 * BGLZIP_BADARGS 
 * Bad arguments were passed to the API.
 */
#define BGLZIP_BADARGS             0x00000001

/*
 * BGLZIP_NOTCOMPRESSED 
 * The file that the caller asked to be decompressed was not compressed.
 */
#define BGLZIP_NOTCOMPRESSED       0x00000002

/*
 * BGLZIP_OUTOFMEMORY 
 * The system ran out of memory during the requested operation.
 */
#define BGLZIP_OUTOFMEMORY         0x00000004

/*
 * BGLZIP_SIZEMISMATCH 
 * The decompression operation did not preserve the
 * original file length.
 */
#define BGLZIP_SIZEMISMATCH        0x00000008

/*
 * BGLZIP_BADCHECKSUM
 * The decompression failed to preserve the original file's checksum.
 */
#define BGLZIP_BADCHECKSUM         0x00000010

/*
 * BGLZIP_DECOMPRESSIONFAILED
 * The decompression algorithm failed abnormally.
 */
#define BGLZIP_DECOMPRESSIONFAILED 0x00000020

/*
 * BGLZIP_CANNOTOPENFILE
 * The requested file could not be opened.
 */
#define BGLZIP_CANNOTOPENFILE      0x00000040

/*****
 *
 * API Calls.  Win32 API calling convention.
 *
 *****/

/*
 * FSGetUncompressedBGLData(...)
 *
 * Decompress a compressed BGL file.
 *
 * Arguments:
 *
 *   szFileName - Name of the file to be decompressed.
 *   pdwSize    - Pointer to a DWORD that will be filled in with the size
 *                of the decompressed data.
 *   ppData     - Pointer to a PVOID that will be filled in with a pointer
 *                to the decompressed data.
 *
 * After successfully calling this API and extracting the requested data,
 * FSCompleteBGLOperation(...) *must* be called to free up allocated resources.
 *
 */
DWORD WINAPI FSGetUncompressedBGLData(LPCSTR szFileName,
									  DWORD* pdwSize,
									  PVOID* ppData);

/*
 * FSCompleteBGLOperation(...)
 *
 * Free up resources allocated by FSGetUncompressedBGLData(...).
 *
 * Arguments:
 *
 *   dwSize     - The size of the data as given by the call to
 *                FSGetUncompressedBGLData(...).
 *   pData      - The pointer to the uncompressed data as given by the call to
 *                FSGetUncompressedBGLData(...).
 *
 */

DWORD WINAPI FSCompleteBGLOperation(DWORD dwSize,
									PVOID pData);

#endif /* _bglzip_h_ */
