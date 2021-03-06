
/* File : barebones/ee_printf.h
	This file contains an implementation of ee_printf that only requires a method to output a char to a UART without pulling in library code.

This code is based on a file that contains the following:
 Copyright (C) 2002 Michael Ringgaard. All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:
 
 1. Redistributions of source code must retain the above copyright 
    notice, this list of conditions and the following disclaimer.  
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.  
 3. Neither the name of the project nor the names of its contributors
    may be used to endorse or promote products derived from this software
    without specific prior written permission. 
 
 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
 FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF 
 SUCH DAMAGE.

*/

#ifndef __EE_PRINTF_H__
#define __EE_PRINTF_H__

#include <stdarg.h>

#ifdef __cplusplus
#define EXTERN_C extern "C"
#else //!__cplusplus
#define EXTERN_C extern
#endif //__cplusplus

EXTERN_C int ee_sprintf(char* buffer, const char* format, ...) __attribute__((format (printf, 2, 3)));

EXTERN_C int ee_printf(const char* format, ...) __attribute__((format (printf, 1, 2)));

#define printf(...) ee_printf(__VA_ARGS__)

#endif //!__EE_PRINTF_H__

