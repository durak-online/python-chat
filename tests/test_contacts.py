import os
import unittest

import contacts
from contacts import Contact, Contacts, DEFAULT_NAME


class TestContact(unittest.TestCase):
    def test_init(self):
        contact = Contact("192.168.0.0", 8000)
        self.assertIsNotNone(contact)
        self.assertEqual("192.168.0.0", contact.host)
        self.assertEqual(8000, contact.port)
        self.assertEqual(DEFAULT_NAME, contact.username)

    def test_to_dict(self):
        contact = Contact("192.168.0.0", 8000)
        contact_dict = contact.to_dict()
        self.assertDictEqual(
            {
                "host": "192.168.0.0",
                "port": 8000,
                "username": DEFAULT_NAME
            },
            contact_dict
        )

    def test_from_dict(self):
        contact_dict = {
            "host": "192.168.0.0",
            "port": 8000,
            "username": DEFAULT_NAME
        }
        contact = Contact.from_dict(contact_dict)
        self.assertIsNotNone(contact)
        self.assertEqual("192.168.0.0", contact.host)
        self.assertEqual(8000, contact.port)
        self.assertEqual(DEFAULT_NAME, contact.username)

    def test_eq(self):
        contact1 = Contact("192.168.0.0", 8000)
        contact2 = Contact("192.168.1.1", 8080)
        not_contact = []

        self.assertEqual(contact1, contact1)
        self.assertNotEqual(contact1, contact2)
        self.assertNotEqual(contact1, not_contact)

    def test_repr(self):
        contact = Contact("192.168.0.0", 8000)
        self.assertEqual(
            f"Contact:{DEFAULT_NAME} (192.168.0.0:8000)", repr(contact)
        )


class TestContacts(unittest.TestCase):
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
        self.assertEqual(0, len(self.base.contacts))

    def test_add_peer(self):
        self.base.clear()
        self.base.add_peer(Contact("localhost", 8000))
        self.assertEqual(1, len(self.base.contacts))

    def test_save_load(self):
        self.base.clear()
        self.base.add_peer(Contact("localhost", 8000))
        self.base.save_contacts()

        self.base.add_peer(Contact("localhost", 8001))
        self.base.load_contacts()
        self.assertEqual(1, len(self.base.contacts))
        self.assertEqual(Contact("localhost", 8000), self.base.contacts[0])

    def test_load_with_no_file(self):
        with open(contacts.CONTACTS_FILE, "w") as f:
            f.write("{123[")
        self.base.load_contacts()
        self.assertEqual([], self.base.contacts)

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

    def test_update_peer(self):
        self.base.clear()
        self.base.add_peer(Contact("192.168.0.0", 8000))
        self.base.update_peer("192.168.10.20", 8000, "User1")
        contact = self.base.get_contact_by_username("User1")
        self.assertIsNotNone(contact)
        self.assertEqual("192.168.10.20", contact.host)
        self.assertEqual(8000, contact.port)


if __name__ == "__main__":
    unittest.main()
