/**
 *     Copyright 2013 Couchbase, Inc.
 *
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 **/

#include "pycbc.h"
#include "structmember.h"

typedef void (*_lcb_cb_t)(lcb_socket_t,short,void*);

/**
 * Shamelessly stolen from my Perl code
 */
typedef enum {
    PYCBC_EVACTION_WATCH,
    PYCBC_EVACTION_UNWATCH,
    PYCBC_EVACTION_SUSPEND,
    PYCBC_EVACTION_RESUME,
} pycbc_evaction_t;

typedef enum {
    PYCBC_EVSTATE_INITIALIZED,
    PYCBC_EVSTATE_ACTIVE,
    PYCBC_EVSTATE_SUSPENDED
} pycbc_evstate_t;

typedef enum {
    PYCBC_EVTYPE_IO,
    PYCBC_EVTYPE_TIMER
} pycbc_evtype_t;

typedef struct {
    PyObject *pyio;
    pycbc_Connection *conn;
} iops_cookie;

typedef struct {
    PyObject_HEAD

    /** Callback data for libcouchbase */
    struct {
        _lcb_cb_t handler;
        void *data;
    } cb;

    /**
     * Something the pythonl-level IOPS object might want to
     * store here
     */
    PyObject *pypriv;

    /**
     * State: Active/Inactive, etc.
     */
    pycbc_evstate_t state;

    /**
     * Timer or fd watcher
     */
    pycbc_evtype_t evtype;

    /**
     * Underlying socket which the timer is watching
     */
    lcb_socket_t fd;

    /**
     * Event flags (i.e READ_EVENT|WRITE_EVENT)
     */
    short flags;
} pycbc_IOEvent;


static PyTypeObject pycbc_IOEventType = {
    PYCBC_POBJ_HEAD_INIT(NULL)
    0
};

static struct PyMemberDef pycbc_IOEvent_TABLE_members[] = {
        { "events",
                T_SHORT, offsetof(pycbc_IOEvent, flags),
                0
        },
        { NULL }
};

/**
 * e.g.:
 * event.event_received(PYCBC_LCB_READ_EVENT)
 */
static PyObject *
IOEvent_on_ready(pycbc_IOEvent *ev, PyObject *args)
{
    short flags;
    int rv;

    rv = PyArg_ParseTuple("h", &flags);
    if (!rv) {
        return NULL;
    }
    ev->cb.handler(ev->fd, flags, ev->cb.data);
    Py_RETURN_NONE;
}


static struct PyMethodDef pycbc_IOEvent_TABLE_methods[] = {
        { "on_ready",
                (PyCFunction)IOEvent_on_ready,
                METH_VARARGS,
                PyDoc_STR("Called when an event is ready")
        },
        { NULL }
};

static void
IOEvent_dealloc(pycbc_IOEvent *self)
{
    Py_XDECREF(self->pypriv);
    self->pypriv = NULL;
    Py_TYPE(self)->tp_free((PyObject*)self);
}

int
pycbc_IOEventType_init(PyObject **ptr)
{
    PyTypeObject *p = &pycbc_IOEventType;
    *ptr = (PyObject*)p;

    if (p->tp_name) {
        return 0;
    }

    p->tp_name = "IOEvent";
    p->tp_doc = PyDoc_STR("Internal event handle");
    p->tp_new = PyType_GenericNew;
    p->tp_basicsize = sizeof(pycbc_IOEvent);
    p->tp_members = pycbc_IOEvent_TABLE_members;
    p->tp_methods = pycbc_IOEvent_TABLE_methods;
    p->tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE;
    p->tp_dealloc = (destructor)IOEvent_dealloc;
    return PyType_Ready(p);
}


static int
modify_event_python(lcb_io_opt_t io,
                    pycbc_IOEvent *ev,
                    pycbc_evaction_t action,
                    void *arg)
{
    int ret;
    PyObject *argtuple = NULL;
    PyObject *result = NULL;
    PyObject *meth = NULL;
    short flags = 0;
    unsigned long usecs = 0;
    iops_cookie *ioc = (iops_cookie*)io->v.v0.cookie;

    PYCBC_CONN_THR_END(ioc->conn);

    if (ev->evtype == PYCBC_EVTYPE_IO) {
        flags = *(short*)arg;
        argtuple = Py_BuildValue("(O,i,i)", ev, action, flags);
    } else {
        usecs = *(lcb_uint32_t*)arg;
        argtuple = Py_BuildValue("(O,i,k)", ev, action, usecs);
    }

    argtuple = Py_BuildValue("(O,i,i)", ev, action, flags);

    /**
     * Figure out where exactly our
     */
    meth = PyObject_GetAttr(ioc->pyio, pycbc_helpers.ioname_modevent);
    result = PyObject_CallObject(meth, argtuple);
    Py_XDECREF(meth);
    Py_XDECREF(result);
    Py_XDECREF(argtuple);

    if (action != PYCBC_EVACTION_SUSPEND && action != PYCBC_EVACTION_RESUME) {
        ev->flags = flags;
    }

    if (!result) {
        ret = -1;
        PYCBC_EXC_WRAP(PYCBC_EXC_INTERNAL, 0, "Couldn't invoke IO Function");
    } else {
        ret = 0;
    }

    PYCBC_CONN_THR_BEGIN(ioc->conn);
    return ret;
}

/**
 * Begin GLUE
 */
static void *
create_event(lcb_io_opt_t io)
{
    PyObject *ret = PyObject_CallObject((PyObject*)pycbc_IOEventType, NULL, NULL);
    ((pycbc_IOEvent*)ret)->evtype = PYCBC_EVTYPE_IO;
    return ret;
}

static void *
create_timer(lcb_io_opt_t io)
{
    pycbc_IOEvent *ret = (pycbc_IOEvent*)create_event;
    ret->evtype = PYCBC_EVTYPE_TIMER;
    return ret;
}

static void
destroy_event_common(lcb_io_opt_t io, void *arg)
{
    pycbc_IOEvent *ev = (pycbc_IOEvent*)arg;
    ev->state = PYCBC_EVSTATE_SUSPENDED;
    Py_DECREF(arg);
}

static int
update_event(lcb_io_opt_t io,
             lcb_socket_t sock,
             void *event,
             short flags,
             void *data,
             _lcb_cb_t handler)
{
    PyObject *args;
    pycbc_IOEvent *ev = (pycbc_IOEvent*)event;
    pycbc_evaction_t action;
    pycbc_evstate_t new_state;

    if (!flags) {
        action = PYCBC_EVACTION_UNWATCH;
        new_state = PYCBC_EVSTATE_INITIALIZED;

    } else {
        action = PYCBC_EVACTION_WATCH;
        new_state = PYCBC_EVSTATE_ACTIVE;
    }

    ev->cb.handler = handler;
    ev->cb.data = data;

    if (ev->flags == flags &&
            ev->cb.handler == handler &&
            ev->cb.data == data &&
            new_state == ev->state) {
        return 0;
    }

    return modify_event_python(io, ev, action, &flags);
}

static void
delete_event(lcb_io_opt_t io, lcb_socket_t sock, void *event)
{
    pycbc_IOEvent *ev = (pycbc_IOEvent*)event;
    modify_event_python(io, ev, PYCBC_EVACTION_UNWATCH, &ev->flags);
}

static void
delete_timer(lcb_io_opt_t io, void *timer)
{
    delete_event(io, timer);
}

static int
update_timer(lcb_io_opt_t io,
             void *timer,
             lcb_uint32_t usec,
             void *data,
             _lcb_cb_t handler)
{
    pycbc_IOEvent *ev = (pycbc_IOEvent*)timer;
    return modify_event_python(io, ev, PYCBC_EVACTION_WATCH, &usec);
}

lcb_io_opt_t
pycbc_iops_new(pycbc_Connection *conn,
               PyObject *pyio,
               int override_sendrecv)
{
    lcb_io_opt_t ret = NULL;
    lcb_error_t err;
    struct lcb_create_io_ops_st options = { 0 };

    iops_cookie *ioc = calloc(1, sizeof(iops_cookie));
    ioc->conn = conn;
    ioc->pyio = pyio;
    Py_INCREF(conn);
    Py_INCREF(pyio);

    options.v.v0.type = LCB_IO_OPS_DEFAULT;

    err = lcb_create_io_ops(&ret, &options);
    if (err != LCB_SUCCESS) {
        PYCBC_EXC_WRAP(PYCBC_EXC_LCBERR, err, "Couldn't create IOPS");
        return NULL;
    }

    ret->v.v0.create_event = create_event;
    ret->v.v0.create_timer = create_timer;
    ret->v.v0.destroy_event = destroy_event_common;
    ret->v.v0.destroy_timer = destroy_event_common;
    ret->v.v0.update_event = update_event;
    ret->v.v0.delete_event = delete_event;
    ret->v.v0.delete_timer = delete_timer;
    ret->v.v0.update_timer = update_timer;
    ret->v.v0.cookie = ioc;

    return ret;
}
