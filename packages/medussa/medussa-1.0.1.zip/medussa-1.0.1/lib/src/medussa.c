/*
# Copyright (c) 2010-2012 Christopher Brown
#
# This file is part of Medussa.
#
# Medussa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Medussa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Medussa.  If not, see <http://www.gnu.org/licenses/>.
#
# Comments and/or additions are welcome. Send e-mail to: cbrown1@pitt.edu.
#
*/

#include "medussa.h"

#if PY_MAJOR_VERSION >= 3
  #define PyInt_AsUnsignedLongMask PyLong_AsUnsignedLongMask
#endif

PaStream *open_stream (PyObject *self, PaStreamParameters *spin, PaStreamParameters *spout, PaStreamCallback *callback_ptr)
{
    // Temporary local variables
    PaError err;
    PyObject *attr;

    PyGILState_STATE gstate;

    // Variables for `Pa_OpenStream()`
    PaStream *stream;
    //PaStreamParameters *spin;
    //PaStreamParameters *spout;
    double fs;
    unsigned long fpb;
    void *user_data = NULL;
    //PaStreamCallback *callback_ptr;

    gstate = PyGILState_Ensure();
    //
    // Start pulling values from calling object...
    //
    // `void *user_data`from `Stream.user_data`
    if (PyObject_HasAttrString(self, "_callback_user_data")) {
        attr = PyObject_GetAttrString(self, "_callback_user_data");
        if (attr == NULL) {
            PyGILState_Release(gstate);
            return NULL;
        }
        else if (attr == Py_None) {
            //printf("DEBUG: `user_data` is none\n");
        }
        else {
            Py_INCREF(attr);
            err = PyInt_AsUnsignedLongMask(attr);
            user_data = (void *) PyInt_AsUnsignedLongMask(attr);
            Py_CLEAR(attr);
        }
    }
    else {
        PyGILState_Release(gstate);
        return NULL;
    }

    // `PaStream *stream` from `Stream.stream_ptr`
    if (PyObject_HasAttrString(self, "_stream_ptr")) {
        attr = PyObject_GetAttrString(self, "_stream_ptr");
        if (attr == NULL) {
            PyGILState_Release(gstate);
            return NULL;
        }
        else if (attr == Py_None) {
            //printf("DEBUG: _stream_ptr is none\n");
        }
        else {
            Py_INCREF(attr);
            err = PyInt_AsUnsignedLongMask(attr);
            stream = (PaStream *) PyInt_AsUnsignedLongMask(attr);
            Py_CLEAR(attr);
        }
    }
    else {
        PyGILState_Release(gstate);
        return NULL;
    }

    // `double fs` from `Stream.fs`
    if (PyObject_HasAttrString(self, "fs")) {
        attr = PyObject_GetAttrString(self, "fs");
        if (attr == NULL) {
            PyGILState_Release(gstate);
            return NULL;
        }
        Py_INCREF(attr);
        fs = PyFloat_AsDouble(attr);
        Py_CLEAR(attr);
    }
    else {
        PyGILState_Release(gstate);
        return NULL;
    }

    // `unsigned long fpb` from `Stream._pa_fpb` [Frames per buffer]
    if (PyObject_HasAttrString(self, "_pa_fpb")) {
        attr = PyObject_GetAttrString(self, "_pa_fpb");
        if (attr == NULL) {
            PyGILState_Release(gstate);
            return NULL;
        }
        Py_INCREF(attr);
        fpb = PyInt_AsUnsignedLongMask(attr); // Only func in C API returning `unsigned long`
        Py_CLEAR(attr);
    }
    else {
        PyGILState_Release(gstate);
        return NULL;
    }
    //
    // ...end pulling values from calling object.
    //

    // Attempt to open the stream

    err = Pa_OpenStream(&stream,
                        spin,
                        spout,
                        fs,
                        fpb,
                        paNoFlag,
                        callback_ptr,
                        user_data);

    ERROR_CHECK;
    
    PyGILState_Release(gstate);

    // Return the new integer value of the mutated `PaStream *` back to Python
    return stream;
}

void start_streams (PaStream *stream_array[], int num_streams)
{
    int i;

    for (i = 0; i < num_streams; i++) {
        Pa_StartStream(stream_array[i]);
    }
}

int readfile_helper (SNDFILE *fin, double *arr, int frames)
{
    int frames_read;
    int err;

    err = sf_seek(fin, 0, 0);
    if (err != 0) { return err; }

    frames_read = sf_readf_double(fin, arr, frames);
    return frames_read;
}

int writefile_helper (char *foutpath, SF_INFO *finfo, double *arr, int format, int frames)
{
    int frames_written = 0;
    SNDFILE *fout;

    finfo->format = format;

    if (!sf_format_check(finfo)) {
        printf("Bad SF_INFO struct.\n");
        return -1;
    }

    fout = sf_open(foutpath, SFM_WRITE, finfo);

    frames_written = sf_writef_double (fout, arr, frames);

    sf_close(fout);

    return frames_written;
}

void initlibmedussa(void)
{
    //Empty function. Needed by distutils or else when building it throws
    //errors.
}

