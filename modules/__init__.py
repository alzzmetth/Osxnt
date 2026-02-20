# modules/__init__.py
# OSXNT - Main Modules Package
# Version: 2.2.0 (with HTTP & SSL Analyzer)

# Existing modules
from . import iptrack
from . import dns
from . import scanport
from . import subdomain
from . import webtrack

# New analyzer modules
from . import http_analyzer
from . import ssl_analyzer

# Spam modules
from .spam import NGLSpammer, GmailSpammer

__all__ = [
    # Existing
    'iptrack',
    'dns', 
    'scanport',
    'subdomain',
    'webtrack',
    
    # New analyzers
    'http_analyzer',
    'ssl_analyzer',
    
    # Spam
    'NGLSpammer',
    'GmailSpammer'
]

# Version info
__version__ = '2.2.0'
__http_version__ = '1.0.0'
__ssl_version__ = '1.0.0'
__spam_version__ = '1.0.0'

# Untuk memudahkan import langsung dari modules
from .http_analyzer import HTTPAnalyzer
from .ssl_analyzer import SSLAnalyzer
