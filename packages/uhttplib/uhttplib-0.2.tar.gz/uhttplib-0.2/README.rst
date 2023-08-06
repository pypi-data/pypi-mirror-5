Unix-domain sockets for Python httplib
======================================

This module adds support for unix-domain sockets to Python's httplib package.

Instead of using ``httplib.HTTPConnection``, instantiate
``uhttplib.UnixHTTPConnection``::

    from uhttplib import UnixHTTPConnection

    conn = uhttplib.UnixHTTPConnection('/tmp/socket')
    conn.request('GET', '/')
    resp = conn.getresponse()
    print resp.read()
