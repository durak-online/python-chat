import unittest
import os

import contacts
from contacts import Contact, Contacts


class FriendBaseTests(unittest.TestCase):
    def __init__(self, method_name="run_tests"):
        super().__init__(method_name)
        self.base = Contacts()
        self.initial_name: str

    def setUp(self):
        self.initial_name = contacts.CONTACTS_FILE
        contacts.CONTACTS_FILE = "peers_test.json"

    def tearDown(self):
        os.remove(contacts.CONTACTS_FILE)
        contacts.CONTACTS_FILE = self.initial_name

    def test_clear(self):
        self.base.clear()
        self.assertEqual(0, len(self.base._contacts))

    def test_add_peer(self):
        self.base.clear()
        self.base.add_peer(Contact("localhost", 8000))
        self.assertEqual(1, len(self.base._contacts))

    def test_save_load(self):
        self.base.clear()
        self.base.add_peer(Contact("localhost", 8000))
        self.base.save_contacts()

        self.base.add_peer(Contact("localhost", 8001))
        self.base.load_contacts()
        self.assertEqual(1, len(self.base._contacts))
        self.assertEqual(Contact("localhost", 8000), self.base._contacts[0])

    def test_get_peer_by_host(self):
        self.base.clear()
        self.base.add_peer(Contact("192.168.0.0", 8000))
        self.base.add_peer(Contact("localhost", 8001))
        self.assertEqual(Contact("192.168.0.0", 8000),
                         self.base.get_contact_by_host("192.168.0.0"))

    def test_get_peer_by_username(self):
        self.base.clear()
        self.base.add_peer(Contact("192.168.0.0", 8000, "User1"))
        self.base.add_peer(Contact("localhost", 8001, "User2"))
        self.assertEqual(Contact("192.168.0.0", 8000, "User1"),
                         self.base.get_contact_by_username("User1"))


if __name__ == "__main__":
    unittest.main()
