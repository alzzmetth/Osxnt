# modules/spam/__init__.py

from .spamngl import NGLSpammer
from .spamgmail import GmailSpammer

__all__ = [
    'NGLSpammer',
    'GmailSpammer'
]
