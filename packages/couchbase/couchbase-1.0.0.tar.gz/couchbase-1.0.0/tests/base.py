# Copyright 2013, Couchbase, Inc.
# All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

try:
    from configparser import ConfigParser
except ImportError:
    # Python <3.0 fallback
    from ConfigParser import SafeConfigParser as ConfigParser
import os
import sys

import unittest
from nose.exc import SkipTest
import types
from couchbase.connection import Connection
from couchbase.exceptions import CouchbaseError
from couchbase.admin import Admin


CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'tests.ini')


class CouchbaseTestCase(unittest.TestCase):
    def setUp(self):
        config = ConfigParser()
        config.read(CONFIG_FILE)

        self.host = config.get('node-1', 'host')
        self.port = config.getint('node-1', 'port')
        self.username = config.get('node-1', 'username')
        self.password = config.get('node-1', 'password')
        self.bucket_prefix = config.get('node-1', 'bucket_prefix')
        self.bucket_password = config.get('node-1', 'bucket_password')
        if not hasattr(self, 'assertIsInstance'):
            def tmp(self, a, *bases):
                self.assertTrue(isinstance(a, bases))
            self.assertIsInstance = types.MethodType(tmp, self)
        if not hasattr(self, 'assertIsNone'):
            def tmp(self, a):
                self.assertTrue(a is None)
            self.assertIsNone = types.MethodType(tmp, self)

        self.nosleep = os.environ.get('PYCBC_TESTS_NOSLEEP', False)

        self._key_counter = 0
        self.extra_buckets = bool(int(config.get('node-1', 'extra_buckets')))


    def get_sasl_params(self):
        if not self.bucket_password:
            return None
        ret = self.make_connargs()
        ret = { 'password' : self.bucket_password, 'bucket' : self.bucket_prefix }
        if self.extra_buckets:
            ret['bucket'] += "_sasl"
        return ret

    def skipUnlessSasl(self):
        sasl_params = self.get_sasl_params()
        if not sasl_params:
            raise SkipTest("No SASL buckets configured")

    def tearDown(self):
        pass

    def make_connargs(self, **overrides):
        ret = {
            'host' : self.host,
            'port' : self.port,
            'username' : self.username,
            'password' : self.password,
            'bucket' : self.bucket_prefix
        }
        ret.update(overrides)
        return ret

    def slowTest(self):
        if self.nosleep:
            raise SkipTest("Skipping slow/sleep-based test")

    def make_connection(self, **kwargs):
        return Connection(**self.make_connargs(**kwargs))

    def make_admin_connection(self):
        return Admin(self.username, self.password, self.host, self.port)

    def gen_key(self, prefix=None):
        if not prefix:
            prefix = "python-couchbase-key_"

        ret = "{0}{1}".format(prefix, self._key_counter)
        self._key_counter += 1
        return ret

    def gen_key_list(self, amount=5, prefix=None):
        ret = [ self.gen_key(prefix) for x in range(amount) ]
        return ret

    def gen_kv_dict(self, amount=5, prefix=None):
        ret = {}
        keys = self.gen_key_list(amount=amount, prefix=prefix)
        for k in keys:
            ret[k] = "Value_For_" + k
        return ret


class ConnectionTestCase(CouchbaseTestCase):
    def setUp(self):
        super(ConnectionTestCase, self).setUp()
        self.cb = self.make_connection()

    def tearDown(self):
        super(ConnectionTestCase, self).tearDown()
        oldrc = sys.getrefcount(self.cb)
        self.assertEqual(oldrc, 2)
        del self.cb
