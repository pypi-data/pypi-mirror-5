/*
    PYGAME EXTENSION - pgext
    many parts of this project are taken from opensource projects:
        libSDL
        pygame

    Copyright (c) 2012-2013, Josef Vanzura <gindar@zamraky.cz>
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.
    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

    The views and conclusions contained in the software and documentation are those
    of the authors and should not be interpreted as representing official policies,
    either expressed or implied, of the FreeBSD Project.
*/

#include <pygame/pgcompat.h>
#include "pgext.h"
#include "getset.h"

#define IBI_HEADER_LEN 4

static PyObject*
dump(PyObject* self, PyObject* args)
{
    PyObject *string;
    PyObject* py_surface = NULL;
    SDL_Surface *surface;
    unsigned int w, h, x, y, color, pxnum = 0;
    SDL_PixelFormat *format = NULL;
    char has_alpha = 0;
    int bytes_per_px = 0;
    unsigned char *data;
    Uint8 r, g, b, a;
    Py_ssize_t data_len;
    Uint32 Rmask, Gmask, Bmask, Amask, Rshift, Gshift, Bshift, Ashift, Rloss,
        Gloss, Bloss, Aloss;

    Uint8 *pixel;
    Uint32 *pixel32;

    /* python arguments parsing*/
    PY_PARSEARGS_BEGIN
        "O", &py_surface
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);
    pxnum = w * h;
    Rmask = format->Rmask;
    Gmask = format->Gmask;
    Bmask = format->Bmask;
    Amask = format->Amask;
    Rshift = format->Rshift;
    Gshift = format->Gshift;
    Bshift = format->Bshift;
    Ashift = format->Ashift;
    Rloss = format->Rloss;
    Gloss = format->Gloss;
    Bloss = format->Bloss;
    Aloss = format->Aloss;
    bytes_per_px = format->BytesPerPixel;

    if(bytes_per_px == 4){
        for(y = 0; y < h; y ++){
            for(x = 0; x < w; x ++){
                getPixel_RGBA(surface, x, y, &r, &g, &b, &a);
                if(a < 254){
                    has_alpha = 1;
                    break;
                }
            }
        }
    }

    if(has_alpha){
        /* RGBA surface */
        string = Bytes_FromStringAndSize (NULL, (pxnum * 4) + IBI_HEADER_LEN);
        Bytes_AsStringAndSize (string, &data, &data_len);
        data[0] = (w >> 8);
        data[1] = (w & 0xff);
        data[2] = (h >> 8);
        data[3] = (h & 0xff);
        data += IBI_HEADER_LEN;

        for(y = 0; y < h; y ++){
            pixel32 = (Uint32 *) ((char *)surface->pixels + y * surface->pitch);
            for(x = 0; x < w; x ++){
                color = *pixel32++;
                data[0] = (char) (((color & Rmask) >> Rshift) << Rloss);
                data[1] = (char) (((color & Gmask) >> Gshift) << Gloss);
                data[2] = (char) (((color & Bmask) >> Bshift) << Bloss);
                data[3] = (char) (((color & Amask) >> Ashift) << Aloss);
                data += 4;
            }
        }
    } else if(bytes_per_px == 4) {
        /* RGBA -> RGB surface */
        string = Bytes_FromStringAndSize (NULL, (pxnum * 3) + IBI_HEADER_LEN);
        Bytes_AsStringAndSize (string, &data, &data_len);

        data[0] = (w >> 8);
        data[1] = (w & 0xff);
        data[2] = (h >> 8);
        data[3] = (h & 0xff);
        data += IBI_HEADER_LEN;

        for(y = 0; y < h; y ++){
            pixel32 = (Uint32 *) ((char *)surface->pixels + y * surface->pitch);
            for(x = 0; x < w; x ++){
                color = *pixel32++;
                data[0] = (char) (((color & Rmask) >> Rshift) << Rloss);
                data[1] = (char) (((color & Gmask) >> Gshift) << Rloss);
                data[2] = (char) (((color & Bmask) >> Bshift) << Rloss);
                data += 3;
            }
        }
    } else {
        /* RGB surface */
        string = Bytes_FromStringAndSize (NULL, (pxnum * 3) + IBI_HEADER_LEN);
        Bytes_AsStringAndSize (string, &data, &data_len);

        data[0] = (w >> 8);
        data[1] = (w & 0xff);
        data[2] = (h >> 8);
        data[3] = (h & 0xff);
        data += IBI_HEADER_LEN;

        for(y = 0; y < h; y ++){
            pixel = (Uint8 *) ((char *)surface->pixels + y * surface->pitch);
            for(x = 0; x < w; x ++){
#if SDL_BYTEORDER == SDL_LIL_ENDIAN
                color = pixel[0] + (pixel[1]<<8) + (pixel[2]<<16);
#else
                color = pixel[2] + (pixel[1]<<8) + (pixel[0]<<16);
#endif
                pixel += 3;
                data[0] = (char) (((color & Rmask) >> Rshift) << Rloss);
                data[1] = (char) (((color & Gmask) >> Gshift) << Gloss);
                data[2] = (char) (((color & Bmask) >> Bshift) << Bloss);
                data += 3;
            }
        }
    }
    return string;
}


static PyObject*
load(PyObject* self, PyObject* args)
{
    PyObject *string;
    SDL_Surface *surface = NULL;
    unsigned int w = 0, h = 0, x, y, pxnum = 0;
    unsigned char *data;
    Py_ssize_t data_len;

    Uint8 *pixel;
    Uint32 *pixel32;

    /* python arguments parsing*/
    PY_PARSEARGS_BEGIN
        "O", &string
    PY_PARSEARGS_END

    Bytes_AsStringAndSize (string, &data, &data_len);

    w = (data[0] << 8) + data[1];
    h = (data[2] << 8) + data[3];
    data += IBI_HEADER_LEN;
    pxnum = w * h;

    if( pxnum * 3 == (data_len - IBI_HEADER_LEN)){
        // RGB
        surface = SDL_CreateRGBSurface (0, w, h, 24, 0xFF<<16, 0xFF<<8, 0xFF, 0);
        SDL_LockSurface (surface);
        for(y = 0; y < h; y++){
            pixel = (Uint8 *) ((char *)surface->pixels + y * surface->pitch);
            for(x = 0; x < w; x++){
#if SDL_BYTEORDER == SDL_LIL_ENDIAN
                pixel[2] = data[0];
                pixel[1] = data[1];
                pixel[0] = data[2];
#else
                pixel[0] = data[0];
                pixel[1] = data[1];
                pixel[2] = data[2];
#endif
                pixel += 3;
                data += 3;
            }
        }
        SDL_UnlockSurface (surface);

    } else if( pxnum * 4 == (data_len - IBI_HEADER_LEN)){
        surface = SDL_CreateRGBSurface (SDL_SRCALPHA, w, h, 32,
#if SDL_BYTEORDER == SDL_LIL_ENDIAN
                                     0xFF, 0xFF<<8, 0xFF<<16, 0xFF<<24);
#else
                                     0xFF<<24, 0xFF<<16, 0xFF<<8, 0xFF);
#endif
        SDL_LockSurface (surface);
        for(y = 0; y < h; y++){
            pixel32 = (Uint32 *) (((char *)surface->pixels) + y * surface->pitch);
            for(x = 0; x < w; x++){
                *pixel32++ = *((Uint32*) data);
                data += 4;
            }
        }
        SDL_UnlockSurface (surface);
    }

    return PySurface_New (surface);
}


static PyMethodDef IbiMethods[] = {
    {"dump", dump, METH_VARARGS, "Dump IBI file"},
    {"load", load, METH_VARARGS, "Load IBI file"},
    {NULL, NULL, NULL, NULL}
};

PyMODINIT_FUNC initibi(void)
{
    Py_InitModule("ibi", IbiMethods);
    import_pygame_surface();
    /*import_pygame_color();*/
}
