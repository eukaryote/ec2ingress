"""
Compatibility module for types and functions that live in different locations
in the standard library for Python 2 and Python 3.
"""

try:
    from queue import Queue  # py3
except ImportError:
    from Queue import Queue


try:
    from urllib.request import urlopen  # py3
except ImportError:
    from urllib2 import urlopen
