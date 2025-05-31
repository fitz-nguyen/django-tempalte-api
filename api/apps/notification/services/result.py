from typing import Optional


class SendNotificationResult:
    def __init__(self, success=True, error: Optional[str] = None):
        self.success = success
        self.error = error

    def is_success(self):
        return self.success is True

    def is_error(self):
        return self.success is False
