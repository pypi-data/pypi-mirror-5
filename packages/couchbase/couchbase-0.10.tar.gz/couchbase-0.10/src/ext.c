#include "pycbc.h"
#include "structmember.h"
/**
 * This file contains boilerplate for the module itself
 */

struct pycbc_helpers_ST pycbc_helpers;


static PyObject *_libcouchbase_init_helpers(PyObject *self, PyObject *args, PyObject *kwargs)
{

#define X(n) \
    pycbc_helpers.n = PyDict_GetItemString(kwargs, #n); \
    if (!pycbc_helpers.n) { \
        PyErr_SetString(PyExc_EnvironmentError, "Can't find " #n); \
        return NULL; \
    }

    PYCBC_XHELPERS(X);
#undef X

#define X(n) \
    Py_INCREF(pycbc_helpers.n);
    PYCBC_XHELPERS(X)
#undef X

    Py_RETURN_NONE;
}

static PyObject *_libcouchbase_strerror(PyObject *self, PyObject *args, PyObject *kw)
{
    int rv;
    int rc = 0;
    rv = PyArg_ParseTuple(args, "i", &rc);
    if (!rv) {
        return NULL;
    }
    return pycbc_lcb_errstr(NULL, rc);
}

static PyMethodDef _libcouchbase_methods[] = {
        { "_init_helpers", (PyCFunction)_libcouchbase_init_helpers,
                METH_VARARGS|METH_KEYWORDS,
                "internal function to initialize python-language helpers"
        },
        { "_strerror", (PyCFunction)_libcouchbase_strerror,
                METH_VARARGS|METH_KEYWORDS,
                "Internal function to map errors"
        },

        { NULL }
};


#if PY_MAJOR_VERSION >= 3

#define PyString_FromString PyUnicode_FromString

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        PYCBC_MODULE_NAME,
        NULL,
        0,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL
};
#endif

#if PY_MAJOR_VERSION >= 3
PyObject *PyInit__libcouchbase(void)
#define INITERROR return NULL

#else
#define INITERROR return
PyMODINIT_FUNC
init_libcouchbase(void)
#endif
{
    PyObject *m;
    PyObject *result_type;
    PyObject *connection_type;
    PyObject *mresult_type;
    PyObject *arg_type;

    if (pycbc_ConnectionType_init(&connection_type) < 0) {
        INITERROR;
    }

    if (pycbc_ResultType_init(&result_type) < 0) {
        INITERROR;
    }

    if (pycbc_MultiResultType_init(&mresult_type) < 0) {
        INITERROR;
    }

    if (pycbc_ArgumentType_init(&arg_type) < 0) {
        INITERROR;
    }

#if PY_MAJOR_VERSION >= 3
    moduledef.m_methods = _libcouchbase_methods;
    m = PyModule_Create(&moduledef);
#else
    m = Py_InitModule(PYCBC_MODULE_NAME, _libcouchbase_methods);
#endif
    if (m == NULL) {
        INITERROR;
    }

    /**
     * Add the type:
     */
    PyModule_AddObject(m, "Connection", connection_type);
    PyModule_AddObject(m, "Result", result_type);
    PyModule_AddObject(m, "MultiResult", mresult_type);
    PyModule_AddObject(m, "Arguments", arg_type);

    pycbc_init_pyconstants(m);

#if PY_MAJOR_VERSION >= 3
    return m;
#endif
}
