/*
 * Copyright (c) SAS Institute Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


#include <Python.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <keyutils.h>

static PyObject *PyKeyutils_Error;

#if PY_MINOR_VERSION < 5
typedef int Py_ssize_t;
#endif

static PyObject * PyKeyutils_add_key(PyObject *self, PyObject *args)
{
    Py_ssize_t vallen;
    key_serial_t key, keyring;
    const char *type, *keystr, *valstr;
    PyObject *arg;

    if (PyTuple_GET_SIZE(args) != 4) {
        PyErr_SetString(PyExc_TypeError, "exactly four arguments expected");
        return NULL;
    }
    arg = PyTuple_GET_ITEM(args, 0);
    if (!PyString_CheckExact(arg)) {
        PyErr_SetString(PyExc_TypeError, "first argument must be a string");
        return NULL;
    }
    type = PyString_AS_STRING(arg);

    arg = PyTuple_GET_ITEM(args, 1);
    if (!PyString_CheckExact(arg)) {
        PyErr_SetString(PyExc_TypeError, "second argument must be a string");
        return NULL;
    }
    keystr = PyString_AS_STRING(arg);

    arg = PyTuple_GET_ITEM(args, 2);
    if (!PyString_CheckExact(arg)) {
        PyErr_SetString(PyExc_TypeError, "third argument must be a string");
        return NULL;
    }
    valstr = PyString_AS_STRING(arg);
    vallen = PyString_GET_SIZE(arg);

    arg = PyTuple_GET_ITEM(args, 3);
    if (!PyInt_CheckExact(arg)) {
        PyErr_SetString(PyExc_TypeError, "fourth argument must be an integer");
        return NULL;
    }
    keyring = PyInt_AS_LONG(arg);
    Py_BEGIN_ALLOW_THREADS
    key = add_key(type, keystr, valstr, vallen, keyring);
    Py_END_ALLOW_THREADS
    if (key < 0) {
        PyObject *error = Py_BuildValue("(is)", errno, strerror(errno));
        PyErr_SetObject(PyKeyutils_Error, error);
        return NULL;
    }
    return PyLong_FromLong(key);
}

static PyObject * PyKeyutils_request_key(PyObject *self, PyObject *args)
{
    key_serial_t key, keyring;
    const char *type, *keystr;
    PyObject *arg;

    if (PyTuple_GET_SIZE(args) != 3) {
        PyErr_SetString(PyExc_TypeError, "exactly three arguments expected");
        return NULL;
    }
    arg = PyTuple_GET_ITEM(args, 0);
    if (!PyString_CheckExact(arg)) {
        PyErr_SetString(PyExc_TypeError, "first argument must be a string");
        return NULL;
    }
    type = PyString_AS_STRING(arg);

    arg = PyTuple_GET_ITEM(args, 1);
    if (!PyString_CheckExact(arg)) {
        PyErr_SetString(PyExc_TypeError, "second argument must be a string");
        return NULL;
    }
    keystr = PyString_AS_STRING(arg);

    arg = PyTuple_GET_ITEM(args, 2);
    if (!PyInt_CheckExact(arg)) {
        PyErr_SetString(PyExc_TypeError, "third argument must be an integer");
        return NULL;
    }
    keyring = PyInt_AS_LONG(arg);

    Py_BEGIN_ALLOW_THREADS
    key = request_key(type, keystr, NULL, keyring);
    Py_END_ALLOW_THREADS
    if (key < 0) {
        if (errno == ENOKEY) {
            // Return None in this case
            Py_INCREF(Py_None);
            return Py_None;
        }
        PyObject *error = Py_BuildValue("(is)", errno, strerror(errno));
        PyErr_SetObject(PyKeyutils_Error, error);
        return NULL;
    }
    return PyLong_FromLong(key);
}

static PyObject * PyKeyutils_read_key(PyObject *self, PyObject *args)
{
    key_serial_t key;
    PyObject *arg;
    long vallen;
    char *valstr;

    if (PyTuple_GET_SIZE(args) != 1) {
        PyErr_SetString(PyExc_TypeError, "exactly one argument expected");
        return NULL;
    }

    arg = PyTuple_GET_ITEM(args, 0);
    if (!PyLong_CheckExact(arg)) {
        PyErr_SetString(PyExc_TypeError, "first argument must be a long");
        return NULL;
    }
    key = PyLong_AsLong(arg);

    Py_BEGIN_ALLOW_THREADS
    vallen = keyctl_read_alloc(key, (void **)&valstr);
    Py_END_ALLOW_THREADS
    if (vallen < 0) {
        PyObject *error = Py_BuildValue("(is)", errno, strerror(errno));
        PyErr_SetObject(PyKeyutils_Error, error);
        return NULL;
    }
    arg = PyString_FromStringAndSize(valstr, vallen);
    free(valstr);
    return arg;
}


static PyMethodDef PyKeyutils_Methods[] = {
    {"add_key", PyKeyutils_add_key, METH_VARARGS, NULL},
    {"request_key", PyKeyutils_request_key, METH_VARARGS, NULL},
    {"read_key", PyKeyutils_read_key, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

#define INSINT(d, sym) { PyObject *__v = PyInt_FromLong((long) sym); \
    if (!__v || PyDict_SetItemString(d, #sym, __v)) \
      PyErr_Clear(); \
    Py_XDECREF(__v); \
}

void init_keyutils(void)
{
    PyObject *m, *d;

    m = Py_InitModule("_keyutils", PyKeyutils_Methods);
    d = PyModule_GetDict(m);

    PyKeyutils_Error = PyErr_NewException("_keyutils.error", NULL, NULL);
    if (PyKeyutils_Error == NULL)
        return;
    PyDict_SetItemString(d, "error", PyKeyutils_Error);

    INSINT(d, ENOKEY);
    INSINT(d, EKEYEXPIRED);
    INSINT(d, EKEYREVOKED);
    INSINT(d, EKEYREJECTED);
    INSINT(d, EINVAL);
    INSINT(d, ENOMEM);
    INSINT(d, EDQUOT);
    INSINT(d, EINTR);
    INSINT(d, EACCES);
    INSINT(d, KEY_SPEC_THREAD_KEYRING);
    INSINT(d, KEY_SPEC_PROCESS_KEYRING);
    INSINT(d, KEY_SPEC_SESSION_KEYRING);
    INSINT(d, KEY_SPEC_USER_KEYRING);
    INSINT(d, KEY_SPEC_USER_SESSION_KEYRING);
}
