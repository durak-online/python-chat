import os
import re
import socket
from collections import deque
from datetime import datetime

from chat_classes import Message
from peer_base import PeerBase

MESSAGE_REGEX = re.compile(
    r"SENDER:(?P<username>[^ ]+?) "
    r"(?P<host>[^:]+?):(?P<port>\d+?)"
    r" \| MESSAGE:(?P<message>.+)",
    re.DOTALL)
HEADER_REGEX = re.compile(
    r"SENDER:(?P<username>[^ ]+?) "
    r"(?P<host>[^:]+?):(?P<port>\d+?)"
    r" \| FILENAME:(?P<filename>.+)")

MSG_TYPE_TEXT = 0x01
MSG_TYPE_FILE_META = 0x02
MSG_TYPE_FILE_DATA = 0x03
MSG_TYPE_FILE_END = 0x04


class Node:
    """A class for single node in P2P chat"""

    def __init__(
            self,
            host: str = "localhost",
            port: int = 8000,
            username: str = "JohnDoe",
            public_ip: str = "192.168.0.0",
            is_console: bool = False
    ):
        if not isinstance(host, str):
            raise ValueError(f"Host must be string, but was:{host} {type(host)}")
        if not isinstance(port, int):
            raise ValueError(f"Port must be integer, but was:{port} {type(port)}")
        if not isinstance(username, str):
            raise ValueError(f"Username must be string, but was:{username} {type(username)}")
        if not isinstance(public_ip, str):
            raise ValueError(f"Public IP must be string, but was:{public_ip} {type(public_ip)}")

        self.host = host
        self.port = port
        self.username = username
        self.public_ip = public_ip
        self.peer_base = PeerBase()
        self.new_messages = deque[Message]()
        self.self = (host, port)

        self._is_running = True
        self._is_console = is_console
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._current_file: dict | None = None

    def send_message(self, peer_host: str, peer_port: int, message: str):
        """Sends a text message to peer"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((peer_host, peer_port))
                message = f"SENDER:{self.username} {self.public_ip}:{self.port} | MESSAGE:{message}"
                message_bytes = message.encode("utf-8")
                data = bytes([MSG_TYPE_TEXT]) \
                       + len(message_bytes).to_bytes(4, "big") \
                       + message_bytes
                s.sendall(data)
            except ConnectionError as e:
                print(f"Can't send message to {peer_host}:{peer_port}: {e}")
                raise

    def send_file(self, peer_host: str, peer_port: int, path: str):
        """Sends file to peer"""
        print("Sending file...")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((peer_host, peer_port))

                filename = os.path.basename(path)
                meta_data = (f"SENDER:{self.username} {self.public_ip}:{self.port} | "
                             f"FILENAME:{filename}").encode("utf-8")

                header = bytes([MSG_TYPE_FILE_META]) \
                         + len(meta_data).to_bytes(4, "big") \
                         + meta_data
                s.sendall(header)

                with open(path, "rb") as file:
                    while True:
                        chunk = file.read(4096)
                        if not chunk:
                            break
                        chunk_header = bytes([MSG_TYPE_FILE_DATA]) \
                                       + len(chunk).to_bytes(4, "big")
                        s.sendall(chunk_header + chunk)

                end_marker = bytes([MSG_TYPE_FILE_END])
                s.sendall(end_marker)

        except Exception as e:
            print(f"Error while sending a file: {e}")

        print("Successfully sent file")

    def receive_messages(self, downloads_path: str):
        """Listens to messages from peers"""
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen()

        while self._is_running:
            try:
                conn, addr = self._server_socket.accept()
                with conn:
                    buffer = b""
                    while True:
                        data = conn.recv(4096)
                        if not data:
                            break

                        buffer += data
                        buffer = self.process_buffer(buffer, downloads_path)

            except OSError:
                break
            except Exception as e:
                print(f"Error while receiving messages: {e}")

        if self._server_socket:
            self._server_socket.close()

    def process_buffer(self, buffer: bytes, downloads_path: str):
        """Reads data from current buffer"""
        while buffer:
            if len(buffer) < 5:
                if buffer[0] == MSG_TYPE_FILE_END:
                    self.finalize_file()
                    buffer = b""
                return buffer

            msg_type = buffer[0]
            length = int.from_bytes(buffer[1:5], "big")

            if len(buffer) < 5 + length:
                return buffer

            data = buffer[5:5 + length]
            buffer = buffer[5 + length:]

            if msg_type == MSG_TYPE_TEXT:
                self.handle_message(data)
            elif msg_type == MSG_TYPE_FILE_META:
                self.handle_file_meta(data, downloads_path)
            elif msg_type == MSG_TYPE_FILE_DATA:
                self._current_file["handle"].write(data)
            elif msg_type == MSG_TYPE_FILE_END:
                self.finalize_file()

        return buffer

    def handle_file_meta(self, data: bytes, downloads_path: str):
        """Creates new file using received meta info"""
        meta = data.decode("utf-8")
        match = HEADER_REGEX.match(meta)
        if match:
            groups = match.groupdict()

            if self._is_console:
                print(f"Received {groups["filename"]} from {groups["host"]}")

            self._current_file = {
                "filename": groups["filename"],
                "handle": open(os.path.join(downloads_path, groups["filename"]), "wb")
            }

    def finalize_file(self):
        """Closes file"""
        if self._current_file:
            self._current_file["handle"].close()
            if self._is_console:
                print(f"File {self._current_file["filename"]} was successfully saved")

            self._current_file = None
        else:
            raise ValueError("Received end of file marker, but no file was saving")

    def handle_message(self, data_bytes: bytes):
        """Prints received message"""
        data = data_bytes.decode("utf-8")
        groups = MESSAGE_REGEX.match(data).groupdict()

        if self._is_console:
            print(f"\n{groups["username"]} "
                  f"({groups["host"]}:{groups["port"]}): "
                  f"{groups["message"]}\n>> ",
                  end="", flush=True)

        self.peer_base.update_peer(
            groups["host"],
            int(groups["port"]),
            groups["username"]
        )
        self.new_messages.append(
            Message(
                (groups["host"], int(groups["port"])),
                groups["username"],
                datetime.now(),
                groups["message"]
            )
        )

    def get_message(self) -> Message:
        return self.new_messages.popleft()

    def close(self):
        """Closes current node"""
        self._is_running = False
        if self._server_socket:
            self._server_socket.close()
