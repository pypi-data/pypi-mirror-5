
#include <stdio.h>
#include <stddef.h>
#include <stdarg.h>
#include <errno.h>
#include <sys/types.h>   /* XXX for ssize_t on some platforms */

#ifdef _WIN32
#  include <Windows.h>
#  define snprintf _snprintf
typedef __int8 int8_t;
typedef __int16 int16_t;
typedef __int32 int32_t;
typedef __int64 int64_t;
typedef unsigned __int8 uint8_t;
typedef unsigned __int16 uint16_t;
typedef unsigned __int32 uint32_t;
typedef unsigned __int64 uint64_t;
typedef SSIZE_T ssize_t;
typedef unsigned char _Bool;
#else
#  include <stdint.h>
#endif

#include "ow-crypt.h"
char * _cffi_f_crypt_gensalt_rn(char const * x0, unsigned long x1, char const * x2, int x3, char * x4, int x5)
{
  return crypt_gensalt_rn(x0, x1, x2, x3, x4, x5);
}

char * _cffi_f_crypt_rn(char const * x0, char const * x1, void * x2, int x3)
{
  return crypt_rn(x0, x1, x2, x3);
}

