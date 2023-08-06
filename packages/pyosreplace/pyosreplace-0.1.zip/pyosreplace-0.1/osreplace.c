/* Based on posixmodule.c from Python 2.7.5 
   and http://bugs.python.org/issue8828 */

#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "windows.h"

PyDoc_STRVAR(osreplace__doc__,
"Backport of os.replace from Python 3.3 to 2.x");

static int
convert_to_unicode(PyObject **param)
{
    if (PyUnicode_CheckExact(*param))
        Py_INCREF(*param);
    else if (PyUnicode_Check(*param))
        /* For a Unicode subtype that's not a Unicode object,
           return a true Unicode object with the same data. */
        *param = PyUnicode_FromUnicode(PyUnicode_AS_UNICODE(*param),
                                       PyUnicode_GET_SIZE(*param));
    else
        *param = PyUnicode_FromEncodedObject(*param,
                                             Py_FileSystemDefaultEncoding,
                                             "strict");
    return (*param) != NULL;
}

PyDoc_STRVAR(osreplace_replace__doc__,
"replace(old, new)\n\n\
Rename a file or directory, overwriting the destination.");

static PyObject *
osreplace_replace(PyObject *self, PyObject *args)
{
    PyObject *o1, *o2;
    char *p1, *p2;
    BOOL result;
    if (!PyArg_ParseTuple(args, "OO:replace", &o1, &o2))
        goto error;
    if (!convert_to_unicode(&o1))
        goto error;
    if (!convert_to_unicode(&o2)) {
        Py_DECREF(o1);
        goto error;
    }
    Py_BEGIN_ALLOW_THREADS
    result = MoveFileExW(PyUnicode_AsUnicode(o1),
                         PyUnicode_AsUnicode(o2),
                         MOVEFILE_REPLACE_EXISTING);
    Py_END_ALLOW_THREADS
    Py_DECREF(o1);
    Py_DECREF(o2);
    if (!result) {
        errno = GetLastError();
        return PyErr_SetFromWindowsErr(errno);
        }
    Py_RETURN_NONE;
error:
    PyErr_Clear();
    if (!PyArg_ParseTuple(args, "ss:replace", &p1, &p2))
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    result = MoveFileExA(p1, p2, MOVEFILE_REPLACE_EXISTING);
    Py_END_ALLOW_THREADS
    if (!result) {
        errno = GetLastError();
        return PyErr_SetFromWindowsErr(errno);
        }
    Py_RETURN_NONE;
}

static PyMethodDef osreplace_functions[] = {
    {"replace", osreplace_replace, METH_VARARGS, osreplace_replace__doc__},
    {NULL,              NULL}            /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef osreplace_module = {
    PyModuleDef_HEAD_INIT,
    "osreplace",
    osreplace__doc__,
    -1,
    osreplace_functions,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC
PyInit_osreplace(void)
{
    return PyModule_Create(&osreplace_module);
}

#else /* Python 2.x */

void
initosreplace(void)
{
    Py_InitModule3("osreplace",
                   osreplace_functions,
                   osreplace__doc__);
}

#endif
