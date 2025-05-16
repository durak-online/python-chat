import unittest
import os
import user_config
from user_config import UserConfig


class UserConfigTests(unittest.TestCase):
    def __init__(self, method_name="run_tests"):
        super().__init__(method_name)
        self.config = UserConfig()
        self.initial_name: str

    def setUp(self):
        self.initial_name = user_config.CONFIG_FILE
        user_config.CONFIG_FILE = "config_test.json"

    def tearDown(self):
        os.remove(user_config.CONFIG_FILE)
        user_config.CONFIG_FILE = self.initial_name

    def test_save_load(self):
        self.config.save_config("Anonymous", 8001)
        with open(user_config.CONFIG_FILE) as f:
            data = f.readlines()
            self.assertTrue(data is not None)

        self.config.load_config()
        self.assertEqual("Anonymous", self.config.username)
        self.assertEqual(8001, self.config.server_port)


if __name__ == "__main__":
    unittest.main()
