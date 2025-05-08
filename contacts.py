import json
import os

CONTACTS_FILE = "contacts.json"


class Contact:
    """A class for contact"""

    def __init__(
            self,
            host: str,
            port: int,
            username: str = "JohnDoe"
    ):
        self.host = host
        self.port = port
        self.username = username
        self.self = (host, port)

    def __eq__(self, other):
        if isinstance(other, Contact):
            return (self.host == other.host
                    and self.port == other.port)
        return False

    def to_dict(self):
        """Casts this object to dict for JSON serialization"""
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Creates a friend from JSON data"""
        return cls(data["host"], data["port"], data["username"])


class Contacts:
    """A class for contacts"""

    def __init__(self):
        self._contacts = list[Contact]()
        self.load_contacts()

    def load_contacts(self):
        """Loads contacts from file"""
        if not os.path.exists(CONTACTS_FILE):
            return
        try:
            with open(CONTACTS_FILE, "r") as f:
                content = f.read()
                if content.strip():
                    loaded_data = json.loads(content)
                    self._contacts = [Contact.from_dict(item) for item in loaded_data]
                else:
                    self._contacts = []
        except json.JSONDecodeError:
            print(f"Can't load from '{CONTACTS_FILE}'")
            self._contacts = []

    def save_contacts(self):
        """Saves contacts to file"""
        with open(CONTACTS_FILE, "w") as f:
            contacts = [Contact.to_dict(contact) for contact in self._contacts]
            json.dump(contacts, f, indent=4)

    def add_peer(self, contact: Contact):
        """Adds new contact to base"""
        self._contacts.append(contact)

    def print_peers(self):
        """Prints all contacts"""
        if len(self._contacts) == 0:
            print("No available contacts")
            return

        for i, contact in enumerate(self._contacts):
            print(f"{i + 1}. {contact.username} ({contact.host}:{contact.port})")

    def get_contact_by_host(self, host: str) -> Contact | None:
        """Returns contact by host"""
        for peer in self._contacts:
            if peer.host == host:
                return peer
        return None

    def get_contact_by_username(self, username: str) -> Contact | None:
        """Returns contact by username"""
        for peer in self._contacts:
            if peer.username == username:
                return peer
        return None

    def update_peer(self, host: str, port: int, username: str):
        """If new host, adds it to base"""
        hosts = [contact.host for contact in self._contacts]
        if host not in hosts:
            self._contacts.append(Contact(host, port, username))

    def clear(self):
        """Clears all contacts"""
        self._contacts = list[Contact]()
        self.save_contacts()
