import time

class FailedMessage:
    def __init__(self, notification_msg: str):
        self.notification_msg = notification_msg
        self.attempts = 0
        self.created_at = time.time()