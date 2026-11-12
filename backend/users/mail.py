"""Delivery port. No live provider is configured or silently emulated."""
from typing import Protocol

class MailDelivery(Protocol):
    available: bool
    def send(self, address: str, purpose: str, url: str) -> None: ...

class UnconfiguredMail:
    available = False
    def send(self, address, purpose, url):
        raise RuntimeError('Mail delivery is not configured')

class FakeMail:
    """Explicitly injected by local tests only; never a runtime default."""
    available = True
    def __init__(self):
        self.messages = []
    def send(self, address, purpose, url):
        self.messages.append((address, purpose, url))
