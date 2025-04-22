import json
import os

PEERS_FILE = "known_peers.json"


class Peer:
    """A class for known peer"""

    def __init__(self, peer_host: str, peer_port: int):
        self.host = peer_host
        self.port = peer_port

    def __eq__(self, other):
        if isinstance(other, Peer):
            return (self.host == other.host
                    and self.port == other.port)
        return False

    def to_dict(self):
        """Casts this object to dict for JSON serialization"""
        return {
            "peer_host": self.host,
            "peer_port": self.port
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a friend from JSON data"""
        return cls(data["peer_host"], data["peer_port"])


class PeerBase:
    """A class for known peers base"""

    def __init__(self):
        self._peers = list[Peer]()
        self.load_peers()

    def load_peers(self):
        """Loads known peers from file"""
        if not os.path.exists(PEERS_FILE):
            return
        try:
            with open(PEERS_FILE, "r") as f:
                content = f.read()
                if content.strip():
                    loaded_data = json.loads(content)
                    self._peers = [Peer.from_dict(item) for item in loaded_data]
                else:
                    self._peers = []
        except json.JSONDecodeError:
            print(f"Can't load from '{PEERS_FILE}'")
            self._peers = []

    def save_peers(self):
        """Saves peers to file"""
        with open(PEERS_FILE, "w") as f:
            peers = [Peer.to_dict(peer) for peer in self._peers]
            json.dump(peers, f)

    def add_peer(self, peer: Peer):
        """Adds new peer to base"""
        self._peers.append(peer)

    def print_peers(self):
        """Prints all known peers"""
        if len(self._peers) == 0:
            print("No available peers")
            return

        for i, peer in enumerate(self._peers):
            print(f"{i + 1}. {peer.host}:{peer.port}")

    def get_peer_by_host(self, host: str) -> Peer | None:
        """Returns peer by host"""
        for peer in self._peers:
            if peer.host == host:
                return peer
        return None

    def clear(self):
        """Clears all base"""
        self._peers = list[Peer]()
        self.save_peers()
