
import unittest

import gevent

from slimta.relay.pool import RelayPool, RelayPoolClient
from slimta.envelope import Envelope


class TestPool(RelayPool):

    def add_client(self):
        return TestClient(self.queue)


class TestClient(RelayPoolClient):

    def _run(self):
        ret = self.poll()
        if isinstance(ret, tuple):
            result, envelope = ret
            result.set('test')


class TestRelayPool(unittest.TestCase):

    def test_add_remove_client(self):
        pool = TestPool()
        pool.queue.append(True)
        pool._add_client()
        for client in pool.pool:
            client.join()
        gevent.sleep(0)
        self.assertFalse(pool.pool)

    def test_add_remove_client_morequeued(self):
        pool = TestPool()
        pool.queue.append(True)
        pool.queue.append(True)
        pool._add_client()
        for client in pool.pool:
            client.join()
        self.assertTrue(pool.pool)
        for client in pool.pool:
            client.join()
        gevent.sleep(0)
        self.assertFalse(pool.pool)

    def test_attempt(self):
        env = Envelope()
        pool = TestPool()
        ret = pool.attempt(env, 0)
        self.assertEqual('test', ret)


# vim:et:fdm=marker:sts=4:sw=4:ts=4
