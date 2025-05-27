import argparse
import unittest
from argparse import Namespace
from unittest.mock import patch, MagicMock

from chat import Chat
from contacts import Contact


class ChatTests(unittest.TestCase):
    def setUp(self):
        self.test_args = Namespace(
            local=True,
            console=True,
            port=8000
        )

        self.patcher_userconfig = patch("chat.UserConfig")
        self.mock_userconfig = self.patcher_userconfig.start()
        self.mock_userconfig.return_value.downloads_dir = "/test_downloads"
        self.mock_userconfig.return_value.username = "test_user"
        self.mock_userconfig.return_value.server_port = 8000

        self.patcher_node = patch("chat.Node")
        self.mock_node = self.patcher_node.start()
        self.mock_node_instance = MagicMock()
        self.mock_node.return_value = self.mock_node_instance

        self.chat = Chat(self.test_args)

    def tearDown(self):
        self.patcher_userconfig.stop()
        self.patcher_node.stop()

    def test_add_contact_valid(self):
        self.chat.add_contact("/add friend 127.0.0.1 8001")
        self.chat.node.contacts.add_peer.assert_called_with(
            Contact("127.0.0.1", 8001, "friend")
        )

    def test_add_contact_invalid(self):
        with patch("builtins.print") as mock_print:
            self.chat.add_contact("/add user")
            mock_print.assert_called_with("Usage: /add <username> <peer_host> <peer_port>")

    def test_send_message_valid(self):
        mock_peer = MagicMock()
        self.chat.node.contacts.get_contact_by_username.return_value = mock_peer
        self.chat.send_message("/send friend Hello!")
        self.chat.node.send_message.assert_called_with(
            mock_peer.host, mock_peer.port, "Hello!"
        )

    def test_send_message_invalid(self):
        self.chat.node.contacts.get_contact_by_username.return_value = None
        self.chat.node.contacts.get_contact_by_host.return_value = None
        with patch("builtins.print") as mock_print:
            self.chat.send_message("/send user1 Hello")
            mock_print.assert_called_with("There's no such user in your contacts")

    def test_send_file_valid(self):
        mock_peer = MagicMock()
        self.chat.node.contacts.get_contact_by_username.return_value = mock_peer
        self.chat.send_file("/sendfile friend test.txt")
        self.chat.node.send_file.assert_called_with(
            mock_peer.host, mock_peer.port, "test.txt"
        )

    def test_change_name_valid(self):
        self.chat.change_name("/chname new_username")
        self.chat.config.save_config.assert_called_with(
            "new_username", self.chat.node.port
        )

    def test_change_name_invalid(self):
        with patch("builtins.print") as mock_print:
            self.chat.change_name("/chname")
            mock_print.assert_called_with("Usage: /chname <username_without_spaces>")

    def test_change_port_valid(self):
        with patch("threading.Thread.join"):
            self.chat.change_port("/chport 8080")
            self.chat.config.save_config.assert_called_with(
                self.chat.config.username, 8080
            )
            self.chat.node.close.assert_called()

    def test_run_cycle(self):
        with patch("builtins.input", side_effect=["/exit"]), \
                patch("chat.Chat.chat_cycle") as mock_cycle:
            with self.assertRaises(SystemExit):
                self.chat.run()
                mock_cycle.assert_called()

    @patch("socket.gethostbyname")
    def test_public_ip_detection(self, mock_gethost):
        mock_gethost.return_value = "192.168.1.100"
        with patch("builtins.print") as mock_print:
            test_args = Namespace(
            local=False,
            console=True,
            port=8000
        )
            chat = Chat(test_args)
            mock_print.assert_any_call(f"Your IPv4 in current wifi is 192.168.1.100. Share it with others")


if __name__ == "__main__":
    unittest.main()
