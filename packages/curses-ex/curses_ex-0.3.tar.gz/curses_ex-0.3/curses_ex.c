/********************************************************************
 * curses_ex.c                                                      *
 *     Provides some funtions not supported by standard curses      *
 *     package.                                                     *
 *******************************************************************/
#include <Python.h>

#ifdef HAVE_NCURSES_H
#include <ncurses.h>
#else
#include <curses.h>
#endif



static void
curses_ex_seterror(const char *fname) {
    PyObject *curses, *err=NULL;
    curses = PyImport_ImportModule("curses");
    if (!curses) {
        goto done;
    }
    err = PyObject_GetAttrString(curses, "error");
    if (!err) {
        goto done;
    }

    PyErr_Format(err, "%s() returned ERR", fname);

done: 
    Py_XDECREF(err);
    Py_XDECREF(curses);
}


PyDoc_STRVAR(doc_define_key,
"define_key(definition=None, keycode=None) \n\
\n\
It permits an application to define keycodes with \
their corresponding control bytes, so that the \
ncurses library will interpret them just \
as it would the predefined codes in the terminfo \
database. \
\n\
If the given definition is None, any existing \
definition for the keycode is removed. Similarly, \
if the given keycode is None, any existing \
string for the given definition is removed.");

static PyObject*
curses_ex_define_key(PyObject *self, PyObject *args) {
    const char *definition = NULL;
    int keycode = -1;
    if (!PyArg_ParseTuple(args, "|yi:define_key", &definition, &keycode))
        return NULL;

    if (ERR == define_key(definition, keycode)) {
        curses_ex_seterror("define_key");
        return NULL;
    }
    
    Py_RETURN_NONE;
}



PyDoc_STRVAR(doc_key_defined,
"key_defined(definition) \n\
\n\
It permits an application to determine if a string is \
currently bound to any keycode.\
\n\
If the string is bound to a keycode, its value (greater than \
zero) is returned. If no keycode is bound, zero is returned. \
If the string conflicts with longer strings which are bound to \
keys, -1 is  returned.");


static PyObject*
curses_ex_key_defined(PyObject *self, PyObject *args) {
    const char *definition = NULL;
    if (!PyArg_ParseTuple(args, "y:key_defined", &definition))
        return NULL;

    if (ERR == key_defined(definition)) {
        curses_ex_seterror("key_defined");
        return NULL;
    }
    
    Py_RETURN_NONE;
}


    
static PyMethodDef curses_ex_methods[] = {
    {"define_key", curses_ex_define_key, METH_VARARGS, doc_define_key},
    {"key_defined", curses_ex_key_defined, METH_VARARGS, doc_key_defined},
    {NULL,              NULL}           /* sentinel */
};



PyDoc_STRVAR(module_doc,
    "Provides some funtions not supported by standard curses package.");

static struct PyModuleDef curses_ex_module = {
    PyModuleDef_HEAD_INIT,
    "curses_ex",
    module_doc,
    -1,
    curses_ex_methods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC
PyInit_curses_ex(void)
{
    PyObject *m = NULL;
    m = PyModule_Create(&curses_ex_module);
    if (m == NULL)
        goto fail;
    return m;
 fail:
    Py_XDECREF(m);
    return NULL;
}

