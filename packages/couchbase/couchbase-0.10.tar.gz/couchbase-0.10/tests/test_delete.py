from couchbase.exceptions import (KeyExistsError, NotFoundError)
from tests.base import CouchbaseTestCase

class ConnectionDeleteTest(CouchbaseTestCase):
    def setUp(self):
        super(ConnectionDeleteTest, self).setUp()
        self.cb = self.make_connection()

    def test_trivial_delete(self):
        """
        Try to delete a key that exists. Ensure that the operation
        succeeds
        """
        rv = self.cb.set('trivial_key', 'value')
        self.assertTrue(rv.success)
        self.assertTrue(rv.cas > 0)
        rv = self.cb.delete('trivial_key')
        self.assertTrue(rv.success)

    def test_delete_notfound(self):
        """
        Delete a key that does not exist.
        With 'quiet' ensure that it returns false. Without 'quiet', ensure that
        it raises a NotFoundError
        """
        self.cb.delete("foo", quiet = True)
        rv = self.cb.delete("foo", quiet = True)
        self.assertFalse(rv.success)
        self.assertRaises(NotFoundError, self.cb.delete, 'foo')

    def test_delete_cas(self):
        """
        Delete with a CAS value. Ensure that it returns OK
        """
        rv1 = self.cb.set('foo', 'bar')
        self.assertTrue(rv1.cas > 0)
        rv2 = self.cb.delete("foo", cas = rv1.cas)
        self.assertTrue(rv2.success)

    def test_delete_badcas(self):
        """
        Simple delete with a bad CAS
        """
        self.cb.set('foo', 'bar')
        self.assertRaises(KeyExistsError,
                self.cb.delete, 'foo', cas = 0xdeadbeef)

    def test_delete_multi(self):
        """
        Delete passing a list of keys
        """
        kvlist = {}
        num_keys = 5
        for i in range(num_keys):
            kvlist["key_" + str(i)] = str(i)

        rvs = self.cb.set_multi(kvlist)
        self.assertTrue(len(rvs) == num_keys)
        rm_rvs = self.cb.delete_multi(list(rvs.keys()))
        self.assertTrue(len(rm_rvs) == num_keys)
        self.assertTrue(rm_rvs.all_ok)

        for k, v in rm_rvs.items():
            self.assertTrue(k in kvlist)
            self.assertTrue(v.success)

    def test_delete_dict(self):
        """
        Delete passing a dict of key:cas pairs
        """
        kvlist = {}
        num_keys = 5
        for i in range(num_keys):
            kvlist["key_" + str(i)] = str(i)

        rvs = self.cb.set_multi(kvlist)
        self.assertTrue(rvs.all_ok)

        # We should just be able to pass it to 'delete'
        rm_rvs = self.cb.delete_multi(rvs)
        self.assertTrue(rm_rvs.all_ok)
        for k, v in rm_rvs.items():
            self.assertTrue(v.success)

    def test_delete_mixed(self):
        """
        Delete with mixed success-error keys.
        Test with mixed found/not-found
        Test with mixed cas-valid/cas-invalid
        """
        self.cb.delete("foo", quiet = True)
        self.cb.set("bar", "a_value")
        # foo does not exit,

        rvs = self.cb.delete_multi(('foo', 'bar'), quiet = True)
        self.assertFalse(rvs.all_ok)
        self.assertTrue(rvs['bar'].success)
        self.assertFalse(rvs['foo'].success)

        # Now see what happens if we delete those with a bad CAS
        keys = [ "key1", "key2", "key3" ]
        kvs = {}
        for k in keys:
            kvs[k] = "value_" + k
        cas_rvs = self.cb.set_multi(kvs)

        # Ensure set had no errors
        set_errors = []
        for k, v in cas_rvs.items():
            if not v.success:
                set_errors.append([k, v])
        self.assertTrue(len(set_errors) == 0)

        # Set one to have a bad CAS
        cas_rvs[keys[0]] = 0xdeadbeef
        self.assertRaises(KeyExistsError,
                          self.cb.delete_multi, cas_rvs)

if __name__ == '__main__':
    unittest.main()
