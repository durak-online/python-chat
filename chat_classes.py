from datetime import datetime
from contacts import Contact

class Message:
    """A class with message info for UI"""

    def __init__(
            self,
            sender: Contact,
            sent_time: datetime,
            message: str
    ):
        self.sender = sender
        self.sent_time = sent_time
        self.message = message
