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
#include "oputil.h"

PyObject *
pycbc_Connection__http_request(pycbc_Connection *self,
                               PyObject *args,
                               PyObject *kwargs)
{
    int rv;
    int method;
    int reqtype;
    unsigned short value_format = 0;
    lcb_error_t err;

    const char *body = NULL;
    PyObject *ret = NULL;
    pycbc_strlen_t nbody = 0;
    const char *path = NULL;
    const char *content_type = NULL;
    pycbc_HttpResult *htres;

    lcb_http_request_t htreq = NULL;
    lcb_http_cmd_t htcmd = { 0 };

    static char *kwlist[] = {
            "type", "method", "path", "content_type", "post_data",
            "response_format", NULL
    };

    rv = PyArg_ParseTupleAndKeywords(args, kwargs,
                                     "iis|zz#H", kwlist,
                                     &reqtype,
                                     &method,
                                     &path,
                                     &content_type,
                                     &body,
                                     &nbody,
                                     &value_format);
    if (!rv) {
        PYCBC_EXCTHROW_ARGS();
        return NULL;
    }

    htres = pycbc_httpresult_new(self);
    htres->key = pycbc_SimpleStringZ(path);
    htres->format = value_format;

    htcmd.v.v1.body = body;
    htcmd.v.v1.nbody = nbody;
    htcmd.v.v1.content_type = content_type;
    htcmd.v.v1.path = path;
    htcmd.v.v1.npath = strlen(path);
    htcmd.v.v1.method = method;


    err = lcb_make_http_request(self->instance,
                                htres,
                                reqtype,
                                &htcmd,
                                &htreq);

    if (err != LCB_SUCCESS) {
        PYCBC_EXCTHROW_SCHED(err);
        goto GT_DONE;
    }

    err = pycbc_oputil_wait_common(self);

    if (err != LCB_SUCCESS) {
        PYCBC_EXCTHROW_WAIT(err);
        goto GT_DONE;
    }

    ret = (PyObject*)htres;
    htres = NULL;

    GT_DONE:
    Py_XDECREF(htres);
    return ret;
}
