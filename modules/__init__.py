# modules/__init__.py
# OSXNT - Main Modules Package
# Upgraded with Spam Modules

# Existing modules
from . import iptrack
from . import dns
from . import scanport
from . import subdomain
from . import webtrack

# New spam modules
from .spam import NGLSpammer, GmailSpammer

__all__ = [
    # Existing
    'iptrack',
    'dns', 
    'scanport',
    'subdomain',
    'webtrack',
    
    # New spam
    'NGLSpammer',
    'GmailSpammer'
]

# Version info
__version__ = '2.1.0'
__spam_version__ = '1.0.0'
