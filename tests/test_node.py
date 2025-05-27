import os
import unittest
from unittest.mock import patch, Mock

from node import Node, MESSAGE_REGEX, HEADER_REGEX, \
    MSG_TYPE_TEXT, MSG_TYPE_FILE_META, MSG_TYPE_FILE_DATA, MSG_TYPE_FILE_END


class NodeTests(unittest.TestCase):
    def setUp(self):
        self.node = Node(
            host="localhost",
            port=8000,
            username="test_user",
            public_ip="127.0.0.1"
        )
        self.test_file = "test_file.txt"
        with open(self.test_file, "w") as f:
            f.write("test content")

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_initialization(self):
        self.assertEqual(self.node.host, "localhost")
        self.assertEqual(self.node.port, 8000)
        self.assertEqual(self.node.username, "test_user")
        self.assertEqual(self.node.public_ip, "127.0.0.1")

    def test_message_regex(self):
        valid_message = "SENDER:user 127.0.0.1:8000 | MESSAGE:Hello"
        match = MESSAGE_REGEX.match(valid_message)
        self.assertIsNotNone(match)
        self.assertEqual(match.group("username"), "user")
        self.assertEqual(match.group("host"), "127.0.0.1")
        self.assertEqual(match.group("port"), "8000")
        self.assertEqual(match.group("message"), "Hello")

    def test_header_regex(self):
        valid_header = "SENDER:user 127.0.0.1:8000 | FILENAME:test.txt"
        match = HEADER_REGEX.match(valid_header)
        self.assertIsNotNone(match)
        self.assertEqual(match.group("username"), "user")
        self.assertEqual(match.group("filename"), "test.txt")

    @patch("socket.socket")
    def test_send_message(self, mock_socket):
        mock_conn = Mock()
        mock_socket.return_value.__enter__.return_value = mock_conn

        self.node.send_message("127.0.0.1", 8001, "Test message")

        expected_message = (
            "SENDER:test_user 127.0.0.1:8000 | MESSAGE:Test message"
        ).encode("utf-8")
        expected_data = (bytes([MSG_TYPE_TEXT])
                         + len(expected_message).to_bytes(4, "big")
                         + expected_message)

        mock_socket.return_value.__enter__.return_value.connect.assert_called_with(("127.0.0.1", 8001))
        mock_conn.sendall.assert_called_once_with(expected_data)

    @patch("socket.socket")
    def test_send_file(self, mock_socket):
        mock_conn = Mock()
        mock_socket.return_value.__enter__.return_value = mock_conn

        self.node.send_file("127.0.0.1", 8001, self.test_file)

        expected_meta = (
            "SENDER:test_user 127.0.0.1:8000 | FILENAME:test_file.txt"
        ).encode("utf-8")
        expected_meta_header = (bytes([MSG_TYPE_FILE_META])
                                + len(expected_meta).to_bytes(4, "big")
                                + expected_meta)

        expected_data = b"test content"
        expected_data_header = (bytes([MSG_TYPE_FILE_DATA])
                                + len(expected_data).to_bytes(4, "big")
                                + expected_data)

        expected_end_marker = bytes([MSG_TYPE_FILE_END])

        calls = mock_conn.sendall.call_args_list

        self.assertEqual(calls[0][0][0], expected_meta_header)
        self.assertEqual(calls[1][0][0], expected_data_header)
        self.assertEqual(calls[2][0][0], expected_end_marker)

    def test_handle_message(self):
        test_data = (
            "SENDER:user 127.0.0.1:8001 | MESSAGE:Hello"
        ).encode("utf-8")

        with patch.object(self.node.contacts, "update_peer") as mock_update:
            self.node.handle_message(test_data)

            mock_update.assert_called_with("127.0.0.1", 8001, "user")

    def test_file_handling(self):
        test_downloads = "test_downloads"
        os.makedirs(test_downloads, exist_ok=True)

        meta_data = (
            "SENDER:user 127.0.0.1:8001 | FILENAME:received.txt"
        ).encode("utf-8")
        file_data = b"file content"

        buffer = (
                bytes([MSG_TYPE_FILE_META])
                + len(meta_data).to_bytes(4, "big")
                + meta_data +
                bytes([MSG_TYPE_FILE_DATA])
                + len(file_data).to_bytes(4, "big")
                + file_data +
                bytes([MSG_TYPE_FILE_END])
        )

        self.node.process_buffer(buffer, test_downloads)

        received_file = os.path.join(test_downloads, "received.txt")
        self.assertTrue(os.path.exists(received_file))
        with open(received_file, "r") as f:
            self.assertEqual(f.read(), "file content")

        os.remove(received_file)
        os.rmdir(test_downloads)

    def test_finalize_file(self):
        test_file = "test.txt"
        with open(test_file, "w") as f:
            f.write("test data")

        self.node._current_file = {
            "filename": test_file,
            "handle": open(test_file, "r")
        }

        self.node.finalize_file()
        self.assertIsNone(self.node._current_file)
        with self.assertRaises(ValueError):
            self.node.finalize_file()

        os.remove(test_file)

    def test_new_message_in_queue(self):
        message = f"SENDER:user 127.0.0.1:8001 | MESSAGE:test message"
        message_bytes = message.encode("utf-8")
        data = (bytes([MSG_TYPE_TEXT])
                + len(message_bytes).to_bytes(4, "big")
                + message_bytes)

        self.node.process_buffer(data, "")

        result_message = self.node.get_message()
        self.assertEqual("user", result_message.sender.username)
        self.assertEqual(("127.0.0.1", 8001), result_message.sender.self)
        self.assertEqual("test message", result_message.content)
        self.assertEqual("text", result_message.message_type)


if __name__ == "__main__":
    unittest.main()
