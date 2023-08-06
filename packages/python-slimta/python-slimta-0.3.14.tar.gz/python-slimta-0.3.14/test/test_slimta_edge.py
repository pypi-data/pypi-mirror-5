
import unittest

from slimta.edge import EdgeServer


class TestEdge(unittest.TestCase):

    def test_edge_interface(self):
        e = EdgeServer(('127.0.0.1', 0), None)
        self.assertRaises(NotImplementedError, e.handle, None, None)


# vim:et:fdm=marker:sts=4:sw=4:ts=4
