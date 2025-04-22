import unittest
import os

import peer_base
from peer_base import Peer, PeerBase


class FriendBaseTests(unittest.TestCase):
    def __init__(self, method_name="run_tests"):
        super().__init__(method_name)
        self.base = PeerBase()

    def test_clear(self):
        self.base.clear()
        self.assertEqual(0, len(self.base._peers))

    def test_add_peer(self):
        self.base.clear()
        self.base.add_peer(Peer("localhost", 8000))
        self.assertEqual(1, len(self.base._peers))

    def test_save_load(self):
        initial_name = peer_base.PEERS_FILE
        peer_base.PEERS_FILE = "peers_test.json"

        self.base.clear()
        self.base.add_peer(Peer("localhost", 8000))
        self.base.save_peers()

        self.base.add_peer(Peer("localhost", 8001))
        self.base.load_peers()
        self.assertEqual(1, len(self.base._peers))
        self.assertEqual(Peer("localhost", 8000), self.base._peers[0])

        os.remove(peer_base.PEERS_FILE)
        peer_base.PEERS_FILE = initial_name

    def test_get_peer_by_host(self):
        self.base.clear()
        self.base.add_peer(Peer("192.168.0.0", 8000))
        self.base.add_peer(Peer("localhost", 8001))
        self.assertEqual(Peer("192.168.0.0", 8000),
                         self.base.get_peer_by_host("192.168.0.0"))


if __name__ == "__main__":
    unittest.main()
