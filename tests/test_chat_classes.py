import os
import shutil
import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch

from chat_classes import Message, ChatInfo, ChatHistory
from contacts import Contact


class TestMessage(unittest.TestCase):
    def setUp(self):
        self.contact = Contact(
            host="127.0.0.1",
            port=1234,
            username="test_user"
        )
        self.sent_time = datetime(2023, 1, 1, 12, 34, 56)
        self.message = Message(
            sender=self.contact,
            sent_time=self.sent_time,
            content="Hello, world!",
            message_type="text"
        )

    def test_to_dict(self):
        message_dict = self.message.to_dict()
        self.assertDictEqual(
            {
                "sender": self.contact.to_dict(),
                "sent_time": "12:34:56",
                "content": "Hello, world!",
                "type": "text"
            },
            message_dict
        )

    def test_from_dict(self):
        message_dict = self.message.to_dict()
        new_message = Message.from_dict(message_dict)

        self.assertEqual(new_message.sender.username, self.contact.username)
        self.assertEqual(new_message.sent_time.time(), self.sent_time.time())
        self.assertEqual(new_message.content, self.message.content)
        self.assertEqual(new_message.message_type, self.message.message_type)


class TestChatInfo(unittest.TestCase):
    def setUp(self):
        contact = Contact(host="127.0.0.1", port=1234, username="test_user")
        self.message = Message(
            sender=contact,
            sent_time=datetime(2023, 1, 1, 12, 34, 56),
            content="Hello, world!",
            message_type="text"
        )
        self.chat_info = ChatInfo("Test Chat", [self.message.to_dict()])

    def test_to_dict(self):
        chat_dict = self.chat_info.to_dict()

        self.assertEqual(chat_dict["chat_name"], "Test Chat")
        self.assertEqual(len(chat_dict["messages"]), 1)
        self.assertEqual(chat_dict["messages"][0]["content"], "Hello, world!")

    def test_from_dict(self):
        data = {
            "chat_name": "Test Chat",
            "messages": [self.message.to_dict()]
        }
        chat_info = ChatInfo.from_dict(data)

        self.assertEqual(chat_info.chat_name, "Test Chat")
        self.assertEqual(len(chat_info.messages), 1)
        self.assertEqual(chat_info.messages[0]["content"], "Hello, world!")


class TestChatHistory(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.patcher = patch('chat_classes.HISTORY_DIR', self.temp_dir)
        self.patcher.start()

        self.contact = Contact(
            host="127.0.0.1",
            port=1234,
            username="test_user"
        )
        self.sent_time = datetime(2023, 1, 1, 12, 34, 56)
        self.message = Message(
            sender=self.contact,
            sent_time=self.sent_time,
            content="Hello, world!",
            message_type="text"
        )

    def tearDown(self):
        self.patcher.stop()
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        chat = ChatHistory(self.contact, self.contact.username)
        self.assertEqual(chat.name, self.contact.username)
        self.assertEqual(len(chat.messages), 0)

    def test_add_message(self):
        chat = ChatHistory(self.contact)
        chat.add_message(self.message)
        self.assertEqual(len(chat.messages), 1)
        self.assertEqual(chat.messages[0].content, "Hello, world!")

    def test_save_and_load(self):
        chat = ChatHistory(self.contact, name="Test Chat")
        chat.add_message(self.message)
        chat.save_chat()

        expected_file = os.path.join(self.temp_dir, "127_0_0_1.json")
        self.assertTrue(os.path.exists(expected_file))

        new_chat = ChatHistory(self.contact)
        new_chat.load_chat()

        self.assertEqual(new_chat.name, "Test Chat")
        self.assertEqual(len(new_chat.messages), 1)
        self.assertEqual(new_chat.messages[0].content, "Hello, world!")

    def test_load_nonexistent_file(self):
        chat = ChatHistory(self.contact)
        chat.load_chat()

        self.assertEqual(chat.name, self.contact.username)
        self.assertEqual(len(chat.messages), 0)

    def test_load_invalid_json(self):
        file_path = os.path.join(self.temp_dir, "127_0_0_1.json")
        with open(file_path, "w") as f:
            f.write("{invalid_json}")

        chat = ChatHistory(self.contact)
        chat.load_chat()

        self.assertEqual(len(chat.messages), 0)

    def test_file_name_generation(self):
        chat = ChatHistory(self.contact)
        expected = "127_0_0_1.json"
        self.assertEqual(os.path.basename(chat._save_path), expected)


if __name__ == "__main__":
    unittest.main()
