===========
PyBitly
===========

PyBitly provides wrapper for bit.ly API. With bit.ly you can shorten,
expand, share and track URLs. Web API is available at http://dev.bitly.com/.
Usage::

    This will obtain your API key from:
    >>> import pybitly.api
    >>> api = pybitly.api.Api('username','password')

    To shorten some URL:
    >>> api.shorten("http://www.wp.pl")
    'http://bit.ly/VjQJi1'

    You can also give a desired domain:
    >>> api.shorten("http://www.wp.pl", "j.mp")
    'http://j.mp/VjQJi1'

    You can also shorten list of URLs:
    >>> api.shorten(["http://wp.pl", "http://onet.pl"], "j.mp")
    ['http://j.mp/VjTksh', 'http://j.mp/19lCwGx']

    If there is a problem, you will see:
    >>> api.shorten("BAD LINK", "j.mp")
    'INVALID_URI'

    You can also expand one or more URLs:
    >>> api.expand('http://bit.ly/198XQVq')
    'http://docs.python.org/2/howto/urllib2.html'

    >>> api.expand(['http://bit.ly/198XQVq', 'http://bit.ly/198XQVq', 'BAD URL'])
    ['http://docs.python.org/2/howto/urllib2.html', 'http://docs.python.org/2/howto/urllib2.html', 'NOT_FOUND']