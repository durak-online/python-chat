import unittest
from argparse import Namespace
from unittest.mock import patch, MagicMock

from chat import Chat
from contacts import Contact


class TestChat(unittest.TestCase):
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
        self.mock_node.return_value = MagicMock()

        self.mock_node.contacts = MagicMock()

        self.chat = Chat(self.test_args)

    def tearDown(self):
        self.patcher_userconfig.stop()
        self.patcher_node.stop()

    @patch("builtins.print")
    def test_print_help_output(self, mock_print):
        Chat.print_help()
        self.assertEqual(mock_print.call_count, 9)
        calls = mock_print.call_args_list

        expected_output = [
            "This is a chat. There are available commands:",
            "  /add <username> <peer_host> <peer_port>   "
            "Adds new peer to known",
            "  /send <username> <message>   Sends a message to peer",
            "  /sendfile <username> <path_to_file>   Sends a file to peer",
            "  /list   Prints list of known peers",
            "  /clear   Clear all known peers",
            "  /chname <username>   Edits current username",
            "  /chport <port>   Edits current port. This will restart server",
            "  /exit   Closes this application"
        ]

        for i, call in enumerate(calls):
            args, _ = call
            self.assertEqual(args[0], expected_output[i])

    def simulate_commands(self, commands):
        with (patch.object(self.chat, "add_contact") as mock_add_contact,
              patch.object(self.chat, "send_file") as mock_send_file,
              patch.object(self.chat, "send_message") as mock_send_message,
              patch.object(self.chat, "change_name") as mock_change_name,
              patch.object(self.chat, "change_port") as mock_change_port,
              patch.object(self.chat, "print_help") as mock_print_help,
              patch.object(self.chat.node.contacts, "clear") as mock_clear,
              patch.object(self.chat.node.contacts, "print_contacts")
              as mock_print_contacts,
              patch("builtins.input", side_effect=commands),
              patch("builtins.print") as mock_print):
            self.chat.chat_cycle()

        return {
            "add_contact": mock_add_contact,
            "send_file": mock_send_file,
            "send_message": mock_send_message,
            "change_name": mock_change_name,
            "change_port": mock_change_port,
            "print_help": mock_print_help,
            "clear": mock_clear,
            "print_contacts": mock_print_contacts,
            "print": mock_print
        }

    def test_exit_command(self):
        self.simulate_commands(["/exit"])
        # проверяем, что цикл завершился без ошибок
        self.assertTrue(True)

    def test_unknown_command(self):
        mocks = self.simulate_commands(["/invalid", "/exit"])
        mocks["print"].assert_called_with("Unknown command: try /help")

    def test_add_command(self):
        mocks = self.simulate_commands(["/add user1 127.0.0.1 8000", "/exit"])
        mocks["add_contact"].assert_called_once_with(
            "/add user1 127.0.0.1 8000"
        )

    def test_send_command(self):
        mocks = self.simulate_commands(["/send user1 Hello world!", "/exit"])
        mocks["send_message"].assert_called_once_with(
            "/send user1 Hello world!"
        )

    def test_sendfile_command(self):
        mocks = self.simulate_commands(["/sendfile user1 data.txt", "/exit"])
        mocks["send_file"].assert_called_once_with("/sendfile user1 data.txt")

    def test_list_command(self):
        mocks = self.simulate_commands(["/list", "/exit"])
        mocks["print_contacts"].assert_called_once()

    def test_clear_command(self):
        mocks = self.simulate_commands(["/clear", "/exit"])
        mocks["clear"].assert_called_once()

    def test_help_command(self):
        mocks = self.simulate_commands(["/help", "/exit"])
        mocks["print_help"].assert_called_once()

    def test_chname_command(self):
        mocks = self.simulate_commands(["/chname NewName", "/exit"])
        mocks["change_name"].assert_called_once_with("/chname NewName")

    def test_chport_command(self):
        mocks = self.simulate_commands(["/chport 8080", "/exit"])
        mocks["change_port"].assert_called_once_with("/chport 8080")

    def test_command_priority(self):
        commands = [
            "/sendfile user1 image.png",
            "/send user1 message",
            "/exit"
        ]
        mocks = self.simulate_commands(commands)
        mocks["send_file"].assert_called_once_with("/sendfile user1 image.png")
        mocks["send_message"].assert_called_once_with("/send user1 message")

    def test_add_contact_valid(self):
        self.chat.add_contact("/add friend 127.0.0.1 8001")
        self.chat.node.contacts.add_peer.assert_called_with(
            Contact("127.0.0.1", 8001, "friend")
        )

    def test_add_contact_invalid(self):
        with patch("builtins.print") as mock_print:
            self.chat.add_contact("/add user")
            mock_print.assert_called_with(
                "Usage: /add <username> <peer_host> <peer_port>"
            )

    def test_send_message_valid(self):
        mock_peer = MagicMock()
        self.chat.node.contacts.get_contact_by_username.return_value = (
            mock_peer
        )
        self.chat.send_message("/send friend Hello!")
        self.chat.node.send_message.assert_called_with(
            mock_peer.host, mock_peer.port, "Hello!"
        )

    def test_send_message_invalid(self):
        self.chat.node.contacts.get_contact_by_username.return_value = None
        self.chat.node.contacts.get_contact_by_host.return_value = None
        with patch("builtins.print") as mock_print:
            self.chat.send_message("/send user1 Hello")
            mock_print.assert_called_with(
                "There's no such user in your contacts"
            )

    def test_send_file_valid(self):
        mock_peer = MagicMock()
        self.chat.node.contacts.get_contact_by_username.return_value = (
            mock_peer
        )
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
            mock_print.assert_called_with(
                "Usage: /chname <username_without_spaces>"
            )

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
            mock_print.assert_any_call(
                f"Your IPv4 in current wifi is 192.168.1.100. "
                f"Share it with others"
            )


if __name__ == "__main__":
    unittest.main()
