"""
	GPath is a robust, generalised abstract file path that provides path manipulations independent from the local environment, maximising cross-platform compatibility.
"""


__version__ = '0.4.4'

from . import platform, render
from ._gpath import GPath, GPathLike

__all__ = ('GPath', 'GPathLike', 'platform', 'render')
