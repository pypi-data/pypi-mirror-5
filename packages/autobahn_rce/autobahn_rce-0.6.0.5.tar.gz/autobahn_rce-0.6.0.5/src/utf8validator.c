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
 *
 *    Note:
 *
 *      This code is a CPython implementation of the algorithm
 *
 *      "Flexible and Economical UTF-8 Decoder"
 *
 *      by Bjoern Hoehrmann
 *
 *      bjoern@hoehrmann.de
 *      http://bjoern.hoehrmann.de/utf-8/decoder/dfa/
 */


#include <Python.h>
#include <structmember.h>

#define UTF8_ACCEPT 0
#define UTF8_REJECT 12

static const uint8_t UTF8VALIDATOR_DFA[] = {
    // The first part of the table maps bytes to character classes that
    // to reduce the size of the transition table and create bitmasks.
     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
     1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,  9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,
     7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,  7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,
     8,8,2,2,2,2,2,2,2,2,2,2,2,2,2,2,  2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    10,3,3,3,3,3,3,3,3,3,3,3,3,4,3,3, 11,6,6,6,5,8,8,8,8,8,8,8,8,8,8,8,

    // The second part is a transition table that maps a combination
    // of a state of the automaton and a character class to a state.
     0,12,24,36,60,96,84,12,12,12,48,72, 12,12,12,12,12,12,12,12,12,12,12,12,
    12, 0,12,12,12,12,12, 0,12, 0,12,12, 12,24,12,12,12,12,12,24,12,24,12,12,
    12,12,12,12,12,12,12,24,12,12,12,12, 12,24,12,12,12,12,12,12,12,24,12,12,
    12,12,12,12,12,12,12,36,12,36,12,12, 12,36,12,12,12,12,12,36,12,36,12,12,
    12,36,12,12,12,12,12,12,12,12,12,12,
};

// Utf8Validator type struct
typedef struct
{
    PyObject_HEAD
    uint32_t i;
    uint32_t state;
    uint32_t codepoint;
} Utf8Validator;

static PyMemberDef Utf8Validator_members[] =
{
    {"i", T_UINT, offsetof(Utf8Validator, i), 0, "Total index of validator."},
    {"state", T_UINT, offsetof(Utf8Validator, state), 0, "State of validator."},
    {"codepoint", T_UINT, offsetof(Utf8Validator, codepoint), 0, "Decoded Unicode codepoint."},
    {NULL}
};

// Common method
static void reset(Utf8Validator *self)
{
    self->i = 0;
    self->state = UTF8_ACCEPT;
    self->codepoint = 0;
}

// Utf8Validator - tp_init
static int Utf8Validator_tp_init(Utf8Validator *self, PyObject *args, PyObject *kwargs)
{
    /* Check if there are no arguments given */
    if (PyTuple_Size(args))
    {
        PyErr_Format(PyExc_TypeError,
                     "Utf8Validator.__init__() takes no arguments (%d given)",
                     (int) PyTuple_GET_SIZE(args));
        return -1;
    }

    /* Initialize the validator */
    reset(self);

    return 0;
}

// Utf8Validator - tp_dealloc
static void Utf8Validator_tp_dealloc(Utf8Validator *self)
{
    self->ob_type->tp_free((PyObject*)self);
}

// Utf8Validator - reset
static PyObject* Utf8Validator_reset(Utf8Validator *self, PyObject *args)
{
    if (PyTuple_Size(args))
    {
        PyErr_Format(PyExc_TypeError,
                     "Utf8Validator.reset() takes no arguments (%d given)",
                     (int) PyTuple_GET_SIZE(args));
        return NULL;
    }

    /* Reset the validator */
    reset(self);

    Py_RETURN_NONE;
}

// Utf8Validator - decode
static PyObject* Utf8Validator_decode(Utf8Validator *self, PyObject *args)
{
    /* Parse input arguments */
    uint32_t byte;

    if (!PyArg_ParseTuple(args, "I:decode", &byte))
        return NULL;

    /* Initialize local variables */
    const uint32_t type = UTF8VALIDATOR_DFA[byte];

    /* Decode byte */
    self->codepoint = (self->state != UTF8_ACCEPT) ?
            (byte & 0x3fu) | (self->codepoint << 6) :
            (0xff >> type) & (byte);
    self->state = UTF8VALIDATOR_DFA[256 + self->state + type];

    /* Return the results */
    return Py_BuildValue("I", self->state);
}

// Utf8Validator - validate
static PyObject* Utf8Validator_validate(Utf8Validator *self, PyObject *args)
{
    /* Initialize local variables */
    PyObject *valid = Py_True;
    uint32_t state = self->state;

    /* Parse input arguments */
    PyObject *data;

    if (!PyArg_ParseTuple(args, "O:validate", &data))
        return NULL;

    if (!PyString_Check(data))
    {
        PyErr_SetString(PyExc_TypeError, "data has to be of type string");
        return NULL;
    }

    const Py_ssize_t buf_len = PyString_Size(data);
    const uint8_t* const buf = (uint8_t*) PyString_AsString(data);
    if (!buf)
        return NULL;


    /* Validate bytes */
    uint32_t i = 0;

    for (; i < (uint32_t) buf_len; ++i)
    {
        state = UTF8VALIDATOR_DFA[256 + state + UTF8VALIDATOR_DFA[buf[i]]];

        if (state == UTF8_REJECT)
        {
            valid = Py_False;
            break;
        }
    }

    /* Store results of validation */
    self->i += i;
    self->state = state;

    /* Return the results */
    return Py_BuildValue("OOII",
                         valid,
                         state == UTF8_ACCEPT ? Py_True : Py_False,
                         i,
                         self->i);
}

static PyMethodDef Utf8Validator_methods[] =
{
    {"reset", (PyCFunction) Utf8Validator_reset, METH_VARARGS,
    "Reset validator to start new incremental UTF-8 decode/validation."},
    {"decode", (PyCFunction) Utf8Validator_decode, METH_VARARGS,
    "Eat one UTF-8 octet, and validate on the fly.\n\
\n\
Returns UTF8_ACCEPT when enough octets have been consumed, in which case\n\
self.codepoint contains the decoded Unicode code point.\n\
\n\
Returns UTF8_REJECT when invalid UTF-8 was encountered.\n\
\n\
Returns some other positive integer when more octets need to be eaten."},
    {"validate", (PyCFunction) Utf8Validator_validate, METH_VARARGS,
    "Incrementally validate a chunk of bytes provided as bytearray.\n\
\n\
Will return a quad (valid?, endsOnCodePoint?, currentIndex, totalIndex).\n\
\n\
As soon as an octet is encountered which renders the octet sequence\n\
invalid, a quad with valid? == False is returned. currentIndex returns\n\
the index within the currently consumed chunk, and totalIndex the\n\
index within the total consumed sequence that was the point of bail out.\n\
When valid? == True, currentIndex will be len(ba) and totalIndex the\n\
total amount of consumed bytes."},
    {NULL}
};

static PyTypeObject Utf8ValidatorType =
{
    PyObject_HEAD_INIT(NULL)
    0,                                                  /* ob_size */
    "autobahn.utf8validator.Utf8Validator",             /* tp_name */
    sizeof(Utf8Validator),                              /* tp_basicsize */
    0,                                                  /* tp_itemsize */
    (destructor) Utf8Validator_tp_dealloc,              /* tp_dealloc */
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
    "Incremental UTF-8 validator with constant memory consumption (minimal state).\n\
\n\
Implements the algorithm \"Flexible and Economical UTF-8 Decoder\" by\n\
Bjoern Hoehrmann (http://bjoern.hoehrmann.de/utf-8/decoder/dfa/).", /* tp_doc */
    0,                                                  /* tp_traverse */
    0,                                                  /* tp_clear */
    0,                                                  /* tp_richcompare */
    0,                                                  /* tp_weaklistoffset */
    0,                                                  /* tp_iter */
    0,                                                  /* tp_iternext */
    Utf8Validator_methods,                              /* tp_methods */
    Utf8Validator_members,                              /* tp_members */
    0,                                                  /* tp_getset */
    0,                                                  /* tp_base */
    0,                                                  /* tp_dict */
    0,                                                  /* tp_descr_get */
    0,                                                  /* tp_descr_set */
    0,                                                  /* tp_dictoffset */
    (initproc) Utf8Validator_tp_init,                   /* tp_init */
    0,                                                  /* tp_alloc */
    0,                                                  /* tp_new */
};

// Python 2.7
PyMODINIT_FUNC initutf8validator(void)
{
#ifdef WITH_THREAD /* Python build with threading support? */
    PyEval_InitThreads();
#endif

    /* Declarations */
    PyObject *module;

    /* Create the module */
    module = Py_InitModule3("utf8validator", NULL, "utf8validator module");

    if (!module)
    {
        // TODO: Add some error message
        return;
    }

    /* Fill in missing slots in type Utf8Validator */
    Utf8ValidatorType.tp_new = PyType_GenericNew;

    if (PyType_Ready(&Utf8ValidatorType) < 0)
    {
        // TODO: Add some error message
        return;
    }

    /* Add the type Utf8Validator to the module */
    Py_INCREF(&Utf8ValidatorType);
    PyModule_AddObject(module, "Utf8Validator", (PyObject*) &Utf8ValidatorType);
}
