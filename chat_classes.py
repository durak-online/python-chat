from datetime import datetime


class Message:
    """A class with message info for UI"""

    def __init__(
            self,
            sender: tuple[str, int],
            sender_username: str,
            sent_time: datetime,
            message: str
    ):
        self.sender = sender
        self.sender_username = sender_username
        self.sent_time = sent_time
        self.message = message
