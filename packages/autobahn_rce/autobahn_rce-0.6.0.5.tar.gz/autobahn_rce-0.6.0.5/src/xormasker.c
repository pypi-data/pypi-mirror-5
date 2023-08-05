/*
 *    xormasker.c
 *
 *    This file was originally created for RoboEearth
 *    http://www.roboearth.org/
 *
 *    The research leading to these results has received funding from
 *    the European Union Seventh Framework Programme FP7/2007-2013 under
 *    grant agreement no248942 RoboEarth.
 *
 *    Copyright 2013 RoboEarth
 *
 *    Licensed under the Apache License, Version 2.0 (the "License");
 *    you may not use this file except in compliance with the License.
 *    You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 *    Unless required by applicable law or agreed to in writing, software
 *    distributed under the License is distributed on an "AS IS" BASIS,
 *    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *    See the License for the specific language governing permissions and
 *    limitations under the License.
 *
 *     \author/s: Dominique Hunziker, Dhananjay Sathe
 */

#include <Python.h>
#include <structmember.h>

static PyObject *XorMaskerException;

// XorMaskerNull type struct
typedef struct
{
    PyObject_HEAD
    int ptr;
} XorMaskerNull;

// XorMaskerSimple type struct
typedef struct
{
    PyObject_HEAD
    int ptr;
    uint8_t mask[4];
} XorMaskerSimple;

// XorMaskerNull - tp_init
static int XorMaskerNull_tp_init(XorMaskerNull *self, PyObject *args, PyObject *kwargs)
{
    /* Check if there is at most 1 argument given */
    int num_args = PyTuple_Size(args);

    if (kwargs && PyDict_Check(kwargs))
        num_args += PyDict_Size(kwargs);

    if (num_args > 1)
    {
        PyErr_Format(PyExc_TypeError,
                     "XorMaskerNull.__init__() takes at most 1 argument (%d given)",
                     num_args);
        return -1;
    }

    /* Initialize the xor masker */
    self->ptr = 0;

    return 0;
}

// XorMaskerSimple - tp_init
static int XorMaskerSimple_tp_init(XorMaskerSimple *self, PyObject *args, PyObject *kwargs)
{
    /* Extract the argument */
    char *mask;
    Py_ssize_t mask_size;

    if (!PyArg_ParseTuple(args, "s#:__init__", &mask, &mask_size))
        return -1;

    /* Verify the argument */
    if ((int) mask_size != 4)
    {
        PyErr_SetString(PyExc_TypeError, "Mask has to be of length 4.");
        return -1;
    }

    /* Parse the mask */
    int i = 0;

    for (; i < 4; ++i)
        self->mask[i] = (uint8_t) mask[i];

    /* Initialize the xor masker */
    self->ptr = 0;

    return 0;
}

// XorMaskerNull - tp_dealloc
static void XorMaskerNull_tp_dealloc(XorMaskerNull *self)
{
    self->ob_type->tp_free((PyObject*) self);
}

// XorMaskerSimple - tp_dealloc
static void XorMaskerSimple_tp_dealloc(XorMaskerSimple *self)
{
    self->ob_type->tp_free((PyObject*) self);
}

// XorMaskerNull - pointer
static PyObject* XorMaskerNull_pointer(XorMaskerNull *self, PyObject *args)
{
    if (PyTuple_Size(args))
    {
        PyErr_Format(PyExc_TypeError,
                     "XorMaskerNull.pointer() takes no arguments (%d given)",
                     (int) PyTuple_GET_SIZE(args));
        return NULL;
    }

    return Py_BuildValue("i", self->ptr);
}

// XorMaskerSimple - pointer
static PyObject* XorMaskerSimple_pointer(XorMaskerSimple *self, PyObject *args)
{
    if (PyTuple_Size(args))
    {
        PyErr_Format(PyExc_TypeError,
                     "XorMaskerSimple.pointer() takes no arguments (%d given)",
                     (int) PyTuple_GET_SIZE(args));
        return NULL;
    }

    return Py_BuildValue("i", self->ptr);
}

// XorMaskerNull - reset
static PyObject* XorMaskerNull_reset(XorMaskerNull *self, PyObject *args)
{
    if (PyTuple_Size(args))
    {
        PyErr_Format(PyExc_TypeError,
                     "XorMaskerNull.reset() takes no arguments (%d given)",
                     (int) PyTuple_GET_SIZE(args));
        return NULL;
    }

    self->ptr = 0;

    Py_RETURN_NONE;
}

// XorMaskerSimple - reset
static PyObject* XorMaskerSimple_reset(XorMaskerSimple *self, PyObject *args)
{
    if (PyTuple_Size(args))
    {
        PyErr_Format(PyExc_TypeError,
                     "XorMaskerSimple.reset() takes no arguments (%d given)",
                     (int) PyTuple_GET_SIZE(args));
        return NULL;
    }

    self->ptr = 0;

    Py_RETURN_NONE;
}

// XorMaskerNull - process
static PyObject* XorMaskerNull_process(XorMaskerNull *self, PyObject *args)
{
    /* Extract the argument */
    PyObject *data;

    if (!PyArg_ParseTuple(args, "O:process", &data))
        return NULL;

    if (!PyString_Check(data))
    {
        PyErr_SetString(PyExc_TypeError, "data has to be of type string");
        return NULL;
    }

    /* Process the data */
    self->ptr += PyString_Size(data);

    return Py_BuildValue("O", data);
}

// XorMaskerSimple - process
static PyObject* XorMaskerSimple_process(XorMaskerSimple *self, PyObject *args)
{
    /* Local references for member variables */
    const int ptr = self->ptr;
    const uint8_t* const mask = self->mask;

    /* Extract the argument */
    PyObject *data;

    if (!PyArg_ParseTuple(args, "O:process", &data))
        return NULL;

    if (!PyString_Check(data))
    {
        PyErr_SetString(PyExc_TypeError, "data has to be of type string");
        return NULL;
    }

    const Py_ssize_t data_size = PyString_Size(data);
    const uint8_t* const data_in = (uint8_t*) PyString_AsString(data);
    if (!data_in)
        return NULL;

    /* Prepare container for return value */
    data = PyString_FromStringAndSize(NULL, (int) data_size);
    if (!data)
    {
        PyErr_SetString(XorMaskerException, "Could not allocate output string.");
        return NULL;
    }

    uint8_t* const data_out = (uint8_t*) PyString_AsString(data);
    if (!data_out)
        return NULL;

    /* Process the data */
    int i = 0;
    int j;

    if (ptr & 3)
    {
        for (j = ptr & 3; i < 4 - (ptr & 3); ++i, ++j)
            data_out[i] = data_in[i] ^ mask[j];
    }

    for (; i < 4 * (((int) data_size) / 4); i += 4)
    {
        data_out[i] = data_in[i] ^ mask[0];
        data_out[i + 1] = data_in[i + 1] ^ mask[1];
        data_out[i + 2] = data_in[i + 2] ^ mask[2];
        data_out[i + 3] = data_in[i + 3] ^ mask[3];
    }

    for (j = 0; i < (int) data_size; ++i, ++j)
        data_out[i] = data_in[i] ^ mask[j];

    /* Store the updated member variable */
    self->ptr += (int) data_size;

    return data;
}

static PyMethodDef XorMaskerNull_methods[] =
{
    {"pointer", (PyCFunction) XorMaskerNull_pointer, METH_VARARGS,
     "Get the current count of the mask pointer."},
    {"reset", (PyCFunction) XorMaskerNull_reset, METH_VARARGS,
     "Reset the mask pointer."},
    {"process", (PyCFunction) XorMaskerNull_process, METH_VARARGS,
     "Process the data by applying the bit mask."},
    {NULL}
};

static PyMethodDef XorMaskerSimple_methods[] =
{
    {"pointer", (PyCFunction) XorMaskerSimple_pointer, METH_VARARGS,
     "Get the current count of the mask pointer."},
    {"reset", (PyCFunction) XorMaskerSimple_reset, METH_VARARGS,
     "Reset the mask pointer."},
    {"process", (PyCFunction) XorMaskerSimple_process, METH_VARARGS,
     "Process the data by applying the bit mask."},
    {NULL}
};

static PyTypeObject XorMaskerNullType =
{
    PyObject_HEAD_INIT(NULL)
    0,                                                  /* ob_size */
    "autobahn.xormasker.XorMaskerNull",                 /* tp_name */
    sizeof(XorMaskerNull),                              /* tp_basicsize */
    0,                                                  /* tp_itemsize */
    (destructor) XorMaskerNull_tp_dealloc,              /* tp_dealloc */
    0,                                                  /* tp_print */
    0,                                                  /* tp_getattr */
    0,                                                  /* tp_setattr */
    0,                                                  /* tp_compare */
    0,                                                  /* tp_repr */
    0,                                                  /* tp_as_number */
    0,                                                  /* tp_as_sequence */
    0,                                                  /* tp_as_mapping */
    0,                                                  /* tp_hash */
    0,                                                  /* tp_call */
    0,                                                  /* tp_str */
    0,                                                  /* tp_getattro */
    0,                                                  /* tp_setattro */
    0,                                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,           /* tp_flags*/
    "XorMasker",                                        /* tp_doc */
    0,                                                  /* tp_traverse */
    0,                                                  /* tp_clear */
    0,                                                  /* tp_richcompare */
    0,                                                  /* tp_weaklistoffset */
    0,                                                  /* tp_iter */
    0,                                                  /* tp_iternext */
    XorMaskerNull_methods,                              /* tp_methods */
    0,                                                  /* tp_members */
    0,                                                  /* tp_getset */
    0,                                                  /* tp_base */
    0,                                                  /* tp_dict */
    0,                                                  /* tp_descr_get */
    0,                                                  /* tp_descr_set */
    0,                                                  /* tp_dictoffset */
    (initproc) XorMaskerNull_tp_init,                   /* tp_init */
    0,                                                  /* tp_alloc */
    0,                                                  /* tp_new */
};

static PyTypeObject XorMaskerSimpleType =
{
    PyObject_HEAD_INIT(NULL)
    0,                                                  /* ob_size */
    "autobahn.xormasker.XorMaskerSimple",               /* tp_name */
    sizeof(XorMaskerSimple),                            /* tp_basicsize */
    0,                                                  /* tp_itemsize */
    (destructor) XorMaskerSimple_tp_dealloc,            /* tp_dealloc */
    0,                                                  /* tp_print */
    0,                                                  /* tp_getattr */
    0,                                                  /* tp_setattr */
    0,                                                  /* tp_compare */
    0,                                                  /* tp_repr */
    0,                                                  /* tp_as_number */
    0,                                                  /* tp_as_sequence */
    0,                                                  /* tp_as_mapping */
    0,                                                  /* tp_hash */
    0,                                                  /* tp_call */
    0,                                                  /* tp_str */
    0,                                                  /* tp_getattro */
    0,                                                  /* tp_setattro */
    0,                                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,           /* tp_flags*/
    "XorMasker",                                        /* tp_doc */
    0,                                                  /* tp_traverse */
    0,                                                  /* tp_clear */
    0,                                                  /* tp_richcompare */
    0,                                                  /* tp_weaklistoffset */
    0,                                                  /* tp_iter */
    0,                                                  /* tp_iternext */
    XorMaskerSimple_methods,                            /* tp_methods */
    0,                                                  /* tp_members */
    0,                                                  /* tp_getset */
    0,                                                  /* tp_base */
    0,                                                  /* tp_dict */
    0,                                                  /* tp_descr_get */
    0,                                                  /* tp_descr_set */
    0,                                                  /* tp_dictoffset */
    (initproc) XorMaskerSimple_tp_init,                 /* tp_init */
    0,                                                  /* tp_alloc */
    0,                                                  /* tp_new */
};

// module method createXorMasker
static PyObject* createXorMasker(PyObject *module, PyObject *args)
{
    /* Extract the arguments */
    PyObject *mask;
    int len;

    if (!PyArg_ParseTuple(args, "O|i", &mask, &len))
        return NULL;

    return PyObject_CallFunctionObjArgs((PyObject *) &XorMaskerSimpleType, mask, NULL);
}

static PyMethodDef utf8validator_methods[] =
{
    {"createXorMasker", createXorMasker, METH_VARARGS,
     "Create a new xormasker using provided mask."},
    {NULL}
};

// Python 2.7
PyMODINIT_FUNC initxormasker(void)
{
#ifdef WITH_THREAD /* Python build with threading support? */
    PyEval_InitThreads();
#endif

    /* Create the module */
    PyObject *module = Py_InitModule3("xormasker", utf8validator_methods, "xormasker module");

    if (!module)
    {
        // TODO: Add some error message
        return;
    }

    /* Register the Exception used in the module */
    XorMaskerException = PyErr_NewException("autobahn.xormasker.XorMaskerException", NULL, NULL);

    /* Fill in missing slots in type XorMaskerNullType */
    XorMaskerNullType.tp_new = PyType_GenericNew;

    if (PyType_Ready(&XorMaskerNullType) < 0)
    {
        // TODO: Add some error message
        return;
    }

    /* Add the type XorMaskerNullType to the module */
    Py_INCREF(&XorMaskerNullType);
    PyModule_AddObject(module, "XorMaskerNull", (PyObject*) &XorMaskerNullType);

    /* Fill in missing slots in type XorMaskerSimpleType */
    XorMaskerSimpleType.tp_new = PyType_GenericNew;

    if (PyType_Ready(&XorMaskerSimpleType) < 0)
    {
        // TODO: Add some error message
        return;
    }

    /* Add the type XorMaskerSimpleType to the module */
    Py_INCREF(&XorMaskerSimpleType);
    PyModule_AddObject(module, "XorMaskerSimple", (PyObject*) &XorMaskerSimpleType);
}
