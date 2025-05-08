import json
import os

CONTACTS_FILE = "contacts.json"
DEFAULT_NAME = "JohnDoe"


class Contact:
    """A class for contact"""

    def __init__(
            self,
            host: str,
            port: int,
            username: str = DEFAULT_NAME
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

    def __repr__(self):
        return f"Contact:{self.username} ({self.host}:{self.port})"

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

    def __hash__(self):
        return hash(self.self)


class Contacts:
    """A class for contacts"""

    def __init__(self):
        self.contacts = list[Contact]()
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
                    self.contacts = [Contact.from_dict(item) for item in loaded_data]
                else:
                    self.contacts = []
        except json.JSONDecodeError:
            print(f"Can't load from '{CONTACTS_FILE}'")
            self.contacts = []

    def save_contacts(self):
        """Saves contacts to file"""
        with open(CONTACTS_FILE, "w") as f:
            contacts = [Contact.to_dict(contact) for contact in self.contacts]
            json.dump(contacts, f, indent=4, default=str)

    def add_peer(self, contact: Contact):
        """Adds new contact to base"""
        self.contacts.append(contact)

    def print_contacts(self):
        """Prints all contacts"""
        if len(self.contacts) == 0:
            print("No available contacts")
            return

        for i, contact in enumerate(self.contacts):
            print(f"{i + 1}. {contact.username} ({contact.host}:{contact.port})")

    def get_contact_by_host(self, host: str) -> Contact | None:
        """Returns contact by host"""
        for peer in self.contacts:
            if peer.host == host:
                return peer
        return None

    def get_contact_by_username(self, username: str) -> Contact | None:
        """Returns contact by username"""
        for peer in self.contacts:
            if peer.username == username:
                return peer
        return None

    def update_peer(self, host: str, port: int, username: str):
        """If new host, adds it to base"""
        hosts = [contact.host for contact in self.contacts]
        if host not in hosts:
            self.contacts.append(Contact(host, port, username))

    def clear(self):
        """Clears all contacts"""
        self.contacts = list[Contact]()
        self.save_contacts()
