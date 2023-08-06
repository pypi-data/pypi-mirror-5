/*

Boolmerge - Tools for merging sorted iterables with boolean operators.
Copyright (C) 2013 Michaël Meyer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/


#include "Python.h"


/* --------------- Common stuff -------------- */

typedef struct {
    PyObject_HEAD
    PyObject *it1, *it2, *elt1, *elt2;
} MergeWithCacheState;


static void mergewithcache_dealloc(MergeWithCacheState *state)
{
    Py_XDECREF(state->it1);
    Py_XDECREF(state->it2);
    Py_XDECREF(state->elt1);
    Py_XDECREF(state->elt2);
    Py_TYPE(state)->tp_free(state);
}


typedef struct {
    PyObject_HEAD
    PyObject *it1, *it2;
} MergeWithoutCacheState;


static void mergewithoutcache_dealloc(MergeWithoutCacheState *state)
{
    Py_XDECREF(state->it1);
    Py_XDECREF(state->it2);
    Py_TYPE(state)->tp_free(state);
}



/* ------------------ Or Merge -------------------- */


PyDoc_STRVAR(ormerge_doc,
"ormerge(it1, it2) -> ormerge object\n\
\n\
Return an iterator yielding all elements present in either\n\
of the sorted iterables `it1` and `it2`:\n\
\n\
    >>> list(boolmerge.ormerge(\"abcd\", \"cef\"))\n\
    ['a', 'b', 'c', 'd', 'e', 'f']");


static PyObject * ormerge_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PyObject *arg1, *arg2, *it1, *it2;

    if (!PyArg_UnpackTuple(args, "ormerge", 2, 2, &arg1, &arg2))
        return NULL;
    
    if ((it1 = PyObject_GetIter(arg1)) == NULL)
        return NULL;
    if ((it2 = PyObject_GetIter(arg2)) == NULL) {
        Py_DECREF(it1);
        return NULL;
    }
    
    MergeWithCacheState *state = (MergeWithCacheState *)type->tp_alloc(type, 0);
    if (state == NULL) {
        Py_DECREF(it1);
        Py_DECREF(it2);
        return NULL;
    }
        
    state->it1 = it1;
    state->it2 = it2;
    state->elt1 = PyIter_Next(it1);
    state->elt2 = PyIter_Next(it2);
        
    return (PyObject *)state;
}


static PyObject * ormerge_next(MergeWithCacheState *state)
{
    PyObject *step = NULL;
    
    if (state->elt1 == NULL && state->elt2 == NULL) {
        return step;
    }
    else if (state->elt1 == NULL) {
        step = Py_BuildValue("O", state->elt2);
        Py_DECREF(state->elt2);
        state->elt2 = PyIter_Next(state->it2);
    }
    else if (state->elt2 == NULL) {
        step = Py_BuildValue("O", state->elt1);
        Py_DECREF(state->elt1);
        state->elt1 = PyIter_Next(state->it1);
    }
    else if (PyObject_RichCompareBool(state->elt1, state->elt2, Py_LT) == 1) {
        step = Py_BuildValue("O", state->elt1);
        Py_DECREF(state->elt1);
        state->elt1 = PyIter_Next(state->it1);
    }
    else if (PyObject_RichCompareBool(state->elt1, state->elt2, Py_GT) == 1) {
        step = Py_BuildValue("O", state->elt2);
        Py_DECREF(state->elt2);
        state->elt2 = PyIter_Next(state->it2);
    }
    else {
        /* assume elt1 and elt2 are equal */
        step = Py_BuildValue("O", state->elt1);
        Py_DECREF(state->elt1);
        Py_DECREF(state->elt2);
        state->elt1 = PyIter_Next(state->it1);
        state->elt2 = PyIter_Next(state->it2);
    }
    return step;
}


PyTypeObject OrMerge_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "boolmerge.ormerge",            /* tp_name */
    sizeof(MergeWithCacheState),    /* tp_basicsize */
    0,                              /* tp_itemsize */
    (destructor)mergewithcache_dealloc, /* tp_dealloc */
    0,                              /* tp_print */
    0,                              /* tp_getattr */
    0,                              /* tp_setattr */
    0,                              /* tp_reserved */
    0,                              /* tp_repr */
    0,                              /* tp_as_number */
    0,                              /* tp_as_sequence */
    0,                              /* tp_as_mapping */
    0,                              /* tp_hash */
    0,                              /* tp_call */
    0,                              /* tp_str */
    0,                              /* tp_getattro */
    0,                              /* tp_setattro */
    0,                              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,             /* tp_flags */
    ormerge_doc,                /* tp_doc */
    0,                              /* tp_traverse */
    0,                              /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    PyObject_SelfIter,              /* tp_iter */
    (iternextfunc)ormerge_next, /* tp_iternext */
    0,                              /* tp_methods */
    0,                              /* tp_members */
    0,                              /* tp_getset */
    0,                              /* tp_base */
    0,                              /* tp_dict */
    0,                              /* tp_descr_get */
    0,                              /* tp_descr_set */
    0,                              /* tp_dictoffset */
    0,                              /* tp_init */
    PyType_GenericAlloc,            /* tp_alloc */
    ormerge_new,                      /* tp_new */
};



/* ------------------- And Merge ------------------ */


PyDoc_STRVAR(andmerge_doc,
"andmerge(it1, it2) -> andmerge object\n\
\n\
Return an iterator yielding all elements that are common\n\
to the two sorted iterables `it1` and `it2`:\n\
\n\
    >>> list(boolmerge.andmerge(\"acd\", \"abc\"))\n\
    ['a', 'c']\n\
\n\
Note that the iteration will be faster if you pass\n\
the shortest iterable as first argument");


static PyObject * andmerge_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PyObject *arg1, *arg2, *it1, *it2;

    if (!PyArg_UnpackTuple(args, "andmerge", 2, 2, &arg1, &arg2))
        return NULL;
    
    if ((it1 = PyObject_GetIter(arg1)) == NULL)
        return NULL;
    if ((it2 = PyObject_GetIter(arg2)) == NULL) {
        Py_DECREF(it1);
        return NULL;
    }
    
    MergeWithoutCacheState *state = (MergeWithoutCacheState *)type->tp_alloc(type, 0);
    if (state == NULL) {
        Py_DECREF(it1);
        Py_DECREF(it2);
        return NULL;
    }
    
    state->it1 = it1;
    state->it2 = it2;
        
    return (PyObject *)state;
}


static PyObject * andmerge_next(MergeWithoutCacheState *state)
{
    PyObject *elt1, *elt2, *step = NULL;
    
    elt1 = PyIter_Next(state->it1);
    elt2 = PyIter_Next(state->it2);
    
    while (elt1 != NULL && elt2 != NULL) {
        if (PyObject_RichCompareBool(elt1, elt2, Py_GT) == 1) {
            Py_DECREF(elt2);
            elt2 = PyIter_Next(state->it2);
        }
        else if (PyObject_RichCompareBool(elt1, elt2, Py_LT) == 1) {
            Py_DECREF(elt1);
            elt1 = PyIter_Next(state->it1);
        }
        else {
            step = Py_BuildValue("O", elt1);
            break;
        }
    }
    Py_XDECREF(elt1);
    Py_XDECREF(elt2);

    return step;
}


PyTypeObject AndMerge_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "boolmerge.andmerge",           /* tp_name */
    sizeof(MergeWithoutCacheState), /* tp_basicsize */
    0,                              /* tp_itemsize */
    (destructor)mergewithoutcache_dealloc,      /* tp_dealloc */
    0,                              /* tp_print */
    0,                              /* tp_getattr */
    0,                              /* tp_setattr */
    0,                              /* tp_reserved */
    0,                              /* tp_repr */
    0,                              /* tp_as_number */
    0,                              /* tp_as_sequence */
    0,                              /* tp_as_mapping */
    0,                              /* tp_hash */
    0,                              /* tp_call */
    0,                              /* tp_str */
    0,                              /* tp_getattro */
    0,                              /* tp_setattro */
    0,                              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,             /* tp_flags */
    andmerge_doc,                   /* tp_doc */
    0,                              /* tp_traverse */
    0,                              /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    PyObject_SelfIter,              /* tp_iter */
    (iternextfunc)andmerge_next,    /* tp_iternext */
    0,                              /* tp_methods */
    0,                              /* tp_members */
    0,                              /* tp_getset */
    0,                              /* tp_base */
    0,                              /* tp_dict */
    0,                              /* tp_descr_get */
    0,                              /* tp_descr_set */
    0,                              /* tp_dictoffset */
    0,                              /* tp_init */
    PyType_GenericAlloc,            /* tp_alloc */
    andmerge_new,                   /* tp_new */
};



/* -------------------- Not Merge ------------------ */


PyDoc_STRVAR(notmerge_doc,
"notmerge(it1, it2) -> notmerge object\n\
\n\
Given the two sorted iterables `it1` and `it2`, return an\n\
iterator that yield all elements present in `it1`, but not in `it2`:\n\
\n\
    >>> list(boolmerge.notmerge(\"bdf\", \"abcf\"))\n\
    ['d']");


static PyObject * notmerge_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PyObject *arg1, *arg2, *it1, *it2;

    if (!PyArg_UnpackTuple(args, "notmerge", 2, 2, &arg1, &arg2))
        return NULL;
    
    if ((it1 = PyObject_GetIter(arg1)) == NULL)
        return NULL;
    if ((it2 = PyObject_GetIter(arg2)) == NULL) {
        Py_DECREF(it1);
        return NULL;
    }
    
    MergeWithCacheState *state = (MergeWithCacheState *)type->tp_alloc(type, 0);
    if (state == NULL) {
        Py_DECREF(it1);
        Py_DECREF(it2);
        return NULL;
    }
    
    state->it1 = it1;
    state->it2 = it2;
    state->elt1 = PyIter_Next(it1);
    state->elt2 = PyIter_Next(it2);
    
    return (PyObject *)state;
}


static PyObject * notmerge_next(MergeWithCacheState *state)
{
    PyObject *step = NULL;
    
    while (state->elt1 != NULL) {
        if (state->elt2 == NULL || PyObject_RichCompareBool(state->elt1, state->elt2, Py_LT) == 1) {
            step = Py_BuildValue("O", state->elt1);
            Py_DECREF(state->elt1);
            state->elt1 = PyIter_Next(state->it1);
            break;
        }
        else if (PyObject_RichCompareBool(state->elt1, state->elt2, Py_EQ) == 1) {
            Py_DECREF(state->elt1);
            Py_DECREF(state->elt2);
            state->elt1 = PyIter_Next(state->it1);
            state->elt2 = PyIter_Next(state->it2);
        }
        else {
            Py_DECREF(state->elt2);
            state->elt2 = PyIter_Next(state->it2);
        }
    }

    return step;
}


PyTypeObject NotMerge_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "boolmerge.notmerge",        /* tp_name */
    sizeof(MergeWithCacheState),             /* tp_basicsize */
    0,                              /* tp_itemsize */
    (destructor)mergewithcache_dealloc,      /* tp_dealloc */
    0,                              /* tp_print */
    0,                              /* tp_getattr */
    0,                              /* tp_setattr */
    0,                              /* tp_reserved */
    0,                              /* tp_repr */
    0,                              /* tp_as_number */
    0,                              /* tp_as_sequence */
    0,                              /* tp_as_mapping */
    0,                              /* tp_hash */
    0,                              /* tp_call */
    0,                              /* tp_str */
    0,                              /* tp_getattro */
    0,                              /* tp_setattro */
    0,                              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,             /* tp_flags */
    notmerge_doc,                   /* tp_doc */
    0,                              /* tp_traverse */
    0,                              /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    PyObject_SelfIter,              /* tp_iter */
    (iternextfunc)notmerge_next,    /* tp_iternext */
    0,                              /* tp_methods */
    0,                              /* tp_members */
    0,                              /* tp_getset */
    0,                              /* tp_base */
    0,                              /* tp_dict */
    0,                              /* tp_descr_get */
    0,                              /* tp_descr_set */
    0,                              /* tp_dictoffset */
    0,                              /* tp_init */
    PyType_GenericAlloc,            /* tp_alloc */
    notmerge_new,                   /* tp_new */
};



/* ----------------- Xor Merge ------------------------ */


PyDoc_STRVAR(xormerge_doc,
"xormerge(it1, it2) -> xormerge object\n\
\n\
Return an iterator that yield all elements present in either\n\
of the two sorted iterables `it1` or `it2`, but not in both:\n\
\n\
    >>> list(boolmerge.xormerge(\"adf\", \"abcd\"))\n\
    ['b', 'c', 'f']");


static PyObject * xormerge_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PyObject *arg1, *arg2, *it1, *it2;

    if (!PyArg_UnpackTuple(args, "xormerge", 2, 2, &arg1, &arg2))
        return NULL;
    
    if ((it1 = PyObject_GetIter(arg1)) == NULL)
        return NULL;
    if ((it2 = PyObject_GetIter(arg2)) == NULL) {
        Py_DECREF(it1);
        return NULL;
    }
    
    MergeWithCacheState *state = (MergeWithCacheState *)type->tp_alloc(type, 0);
    if (state == NULL) {
        Py_DECREF(it1);
        Py_DECREF(it2);
        return NULL;
    }
    
    state->it1 = it1;
    state->it2 = it2;
    state->elt1 = PyIter_Next(it1);
    state->elt2 = PyIter_Next(it2);
        
    return (PyObject *)state;
}


static PyObject * xormerge_next(MergeWithCacheState *state)
{
    PyObject *step = NULL;
    
    while (state->elt1 != NULL || state->elt2 != NULL) {
        if (state->elt1 == NULL) {
            step = Py_BuildValue("O", state->elt2);
            Py_DECREF(state->elt2);
            state->elt2 = PyIter_Next(state->it2);
            break;
        }
        else if (state->elt2 == NULL) {
            step = Py_BuildValue("O", state->elt1);
            Py_DECREF(state->elt1);
            state->elt1 = PyIter_Next(state->it1);
            break;
        }
        else if (PyObject_RichCompareBool(state->elt1, state->elt2, Py_LT) == 1) {
            step = Py_BuildValue("O", state->elt1);
            Py_DECREF(state->elt1);
            state->elt1 = PyIter_Next(state->it1);
            break;
        }
        else if (PyObject_RichCompareBool(state->elt1, state->elt2, Py_GT) == 1) {
            step = Py_BuildValue("O", state->elt2);
            Py_DECREF(state->elt2);
            state->elt2 = PyIter_Next(state->it2);
            break;
        }
        else {
            /* theoretically, elt1 == elt2 */
            Py_DECREF(state->elt1);
            Py_DECREF(state->elt2);
            state->elt1 = PyIter_Next(state->it1);
            state->elt2 = PyIter_Next(state->it2);
        }
    }

    return step;
}


PyTypeObject XorMerge_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "boolmerge.xormerge",           /* tp_name */
    sizeof(MergeWithCacheState),    /* tp_basicsize */
    0,                              /* tp_itemsize */
    (destructor)mergewithcache_dealloc,      /* tp_dealloc */
    0,                              /* tp_print */
    0,                              /* tp_getattr */
    0,                              /* tp_setattr */
    0,                              /* tp_reserved */
    0,                              /* tp_repr */
    0,                              /* tp_as_number */
    0,                              /* tp_as_sequence */
    0,                              /* tp_as_mapping */
    0,                              /* tp_hash */
    0,                              /* tp_call */
    0,                              /* tp_str */
    0,                              /* tp_getattro */
    0,                              /* tp_setattro */
    0,                              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,             /* tp_flags */
    xormerge_doc,                   /* tp_doc */
    0,                              /* tp_traverse */
    0,                              /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    PyObject_SelfIter,              /* tp_iter */
    (iternextfunc)xormerge_next,    /* tp_iternext */
    0,                              /* tp_methods */
    0,                              /* tp_members */
    0,                              /* tp_getset */
    0,                              /* tp_base */
    0,                              /* tp_dict */
    0,                              /* tp_descr_get */
    0,                              /* tp_descr_set */
    0,                              /* tp_dictoffset */
    0,                              /* tp_init */
    PyType_GenericAlloc,            /* tp_alloc */
    xormerge_new,                   /* tp_new */
};



/* ----------------- Module stuff --------------- */


PyDoc_STRVAR(module_doc,
"Tools for merging sorted iterables with boolean operators.\n\
\n\
This module provides 4 base iterator types for merging sorted\n\
iterables according to boolean operators (AND, NOT, OR, XOR),\n\
in a lazy fashion.\n\
\n\
All the iterator types have the same interface. They should be\n\
called with two argument, each one being a sorted iterable\n\
(be it of any kind), which items should be orderable.\n\
If this is not the case, the result is undefined.\n\
");


static struct PyModuleDef boolmergemodule = {
    PyModuleDef_HEAD_INIT,
    "boolmerge",              /* m_name */
    module_doc,               /* m_doc */
    -1,                       /* m_size */
};


PyMODINIT_FUNC PyInit_boolmerge(void)
{
    PyObject *module = PyModule_Create(&boolmergemodule);
    if (!module)
        return NULL;

    if (PyType_Ready(&OrMerge_Type)  != 0 || \
        PyType_Ready(&AndMerge_Type) != 0 || \
        PyType_Ready(&NotMerge_Type) != 0 || \
        PyType_Ready(&XorMerge_Type) != 0)
        return NULL;
    
    Py_INCREF((PyObject *)&OrMerge_Type);
    Py_INCREF((PyObject *)&AndMerge_Type);
    Py_INCREF((PyObject *)&NotMerge_Type);
    Py_INCREF((PyObject *)&XorMerge_Type);
    
    PyModule_AddObject(module, "ormerge", (PyObject *)&OrMerge_Type);
    PyModule_AddObject(module, "andmerge", (PyObject *)&AndMerge_Type);
    PyModule_AddObject(module, "notmerge", (PyObject *)&NotMerge_Type);
    PyModule_AddObject(module, "xormerge", (PyObject *)&XorMerge_Type);

    return module;
}
