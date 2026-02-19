# lib/proxy/__init__.py
# OSXNT - Proxy Management Module

from .tor_proxy import TorProxy
from .port_proxy import PortProxy

__all__ = [
    'TorProxy',
    'PortProxy'
]

__version__ = '1.0.0'
