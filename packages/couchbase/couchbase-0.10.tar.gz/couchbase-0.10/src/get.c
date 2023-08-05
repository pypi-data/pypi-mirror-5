#include "oputil.h"
/**
 * Covers 'lock', 'touch', and 'get_and_touch'
 */


static int handle_single_key(pycbc_ConnectionObject *self,
                            PyObject *curkey,
                            PyObject *curval,
                            unsigned long ttl,
                            int ii,
                            int optype,
                            struct pycbc_common_vars *cv)
{
    int rv;
    char *key;
    size_t nkey;
    unsigned int lock = 0;
    static char *kwlist[] = { "ttl", NULL };

    rv = pycbc_tc_encode_key(self, &curkey, (void**)&key, &nkey);
    if (rv == -1) {
        return -1;
    }

    cv->enckeys[ii] = curkey;

    if (curval) {
        if (ttl) {
            PYCBC_EXC_WRAP(PYCBC_EXC_ARGUMENTS,
                           0,
                           "Both global and single TTL specified");
            return -1;
        }

        if (PyDict_Check(curval)) {
            rv = PyArg_ParseTupleAndKeywords(pycbc_DummyTuple, curval,
                                             "|k", kwlist, &ttl);
            if (!rv) {
                return -1;
            }
        } else {
            ttl = pycbc_IntAsUL(curval);
            if (ttl == -1 && PyErr_Occurred()) {
                return -1;
            }
        }
    }
    switch (optype) {
    case PYCBC_CMD_GAT:
        if (!ttl) {
            PYCBC_EXC_WRAP(PYCBC_EXC_ARGUMENTS, 0, "GAT must have positive TTL");
            return -1;
        }
        goto GT_GET;

    case PYCBC_CMD_LOCK:
        if (!ttl) {
            PYCBC_EXC_WRAP(PYCBC_EXC_ARGUMENTS, 0, "Lock must have an expiry");
        }
        lock = 1;
        goto GT_GET;

    case PYCBC_CMD_GET:
        GT_GET: {
            lcb_get_cmd_t *gcmd = cv->cmds.get + ii;
            gcmd->v.v0.lock = lock;
            gcmd->v.v0.key = key;
            gcmd->v.v0.nkey = nkey;
            gcmd->v.v0.exptime = ttl;
            cv->cmdlist.get[ii] = gcmd;
        }
        break;

    case PYCBC_CMD_TOUCH: {
        lcb_touch_cmd_t *tcmd = cv->cmds.touch + ii;
        tcmd->v.v0.key = key;
        tcmd->v.v0.nkey = nkey;
        tcmd->v.v0.exptime = ttl;
        cv->cmdlist.touch[ii] = tcmd;
        break;
    }
    }

    return 0;
}


static PyObject*
get_common(pycbc_ConnectionObject *self,
           PyObject *args,
           PyObject *kwargs,
           int optype,
           int argopts)
{
    int rv;
    int ii;
    int is_dict = 0;
    int ncmds = 0;
    size_t cmdsize;

    PyObject *ret = NULL;
    PyObject *kobj = NULL;
    PyObject *is_quiet = NULL;
    pycbc_MultiResultObject *mres = NULL;
    lcb_error_t err;
    unsigned long ttl = 0;

    struct pycbc_common_vars cv = PYCBC_COMMON_VARS_STATIC_INIT;

    static char *kwlist[] = { "keys", "ttl", "quiet", NULL };

    rv = PyArg_ParseTupleAndKeywords(args,
                                     kwargs,
                                     "O|kO",
                                     kwlist,
                                     &kobj,
                                     &ttl,
                                     &is_quiet);

    if (!rv) {
        PYCBC_EXC_WRAP(PYCBC_EXC_ARGUMENTS, 0, "couldn't parse arguments");
        return NULL;
    }

    if (argopts & PYCBC_ARGOPT_MULTI) {
        rv = pycbc_oputil_check_sequence(kobj,
                                         optype == PYCBC_CMD_GET,
                                         &ncmds,
                                         &is_dict);
        if (rv < 0) {
            PYCBC_EXC_WRAP_OBJ(PYCBC_EXC_ARGUMENTS,
                               0, "bad argument type", kobj);
            return NULL;
        }

    } else {
        ncmds = 1;
    }

    switch (optype) {
    case PYCBC_CMD_GET:
    case PYCBC_CMD_LOCK:
    case PYCBC_CMD_GAT:
        cmdsize = sizeof(lcb_get_cmd_t);
        break;

    case PYCBC_CMD_TOUCH:
        cmdsize = sizeof(lcb_touch_cmd_t);
        break;
    }

    rv = pycbc_common_vars_init(&cv, ncmds, cmdsize, 0);

    if (rv < 0) {
        return NULL;
    }

    if (argopts & PYCBC_ARGOPT_MULTI) {
        Py_ssize_t dictpos = 0;
        for (ii = 0; ii < ncmds; ii++) {
            PyObject *curkey;
            PyObject *curvalue;

            if (!is_dict) {
                curkey = PySequence_GetItem(kobj, ii);
                curvalue = NULL;

            } else {
                rv = PyDict_Next(kobj, &dictpos, &curkey, &curvalue);
                assert(rv);
            }
            rv = handle_single_key(self, curkey, curvalue, ttl, ii, optype, &cv);
            if (rv < 0) {
                goto GT_DONE;
            }
        }

    } else {
        rv = handle_single_key(self, kobj, NULL, ttl, 0, optype, &cv);
        if (rv < 0) {
            goto GT_DONE;
        }
    }

    mres = (pycbc_MultiResultObject*)pycbc_multiresult_new(self);
    Py_INCREF(mres);

    if (pycbc_maybe_set_quiet(mres, is_quiet) == -1) {
        goto GT_DONE;
    }

    if (optype == PYCBC_CMD_TOUCH) {
        err = lcb_touch(self->instance, mres, ncmds, cv.cmdlist.touch);

    } else {
        err = lcb_get(self->instance, mres, ncmds, cv.cmdlist.get);
    }

    if (err != LCB_SUCCESS) {
        goto GT_DONE;
    }

    PYCBC_CONN_THR_BEGIN(self);
    err = lcb_wait(self->instance);
    PYCBC_CONN_THR_END(self);

    if (err == LCB_SUCCESS) {
        if (!pycbc_multiresult_maybe_raise(mres)) {
            ret = (PyObject*)mres;
        }
    }

GT_DONE:
    pycbc_common_vars_free(&cv);
    Py_XDECREF(mres);

    if (argopts & PYCBC_ARGOPT_SINGLE) {
        if (mres && (void*)ret == (void*)mres) {
            ret = pycbc_ret_to_single(mres);
        }
    }

    return ret;
}

#define DECLFUNC(name, operation, mode) \
    PyObject *pycbc_Connection_##name(pycbc_ConnectionObject *self, \
                                      PyObject *args, PyObject *kwargs) { \
    return get_common(self, args, kwargs, operation, mode); \
}


DECLFUNC(get, PYCBC_CMD_GET, PYCBC_ARGOPT_SINGLE)
DECLFUNC(touch, PYCBC_CMD_TOUCH, PYCBC_ARGOPT_SINGLE)
DECLFUNC(lock, PYCBC_CMD_LOCK, PYCBC_ARGOPT_SINGLE)
DECLFUNC(get_multi, PYCBC_CMD_GET, PYCBC_ARGOPT_MULTI)
DECLFUNC(touch_multi, PYCBC_CMD_TOUCH, PYCBC_ARGOPT_MULTI)
DECLFUNC(lock_multi, PYCBC_CMD_LOCK, PYCBC_ARGOPT_MULTI)
