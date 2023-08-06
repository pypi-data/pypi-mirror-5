###############################################################################
#
# Copyright 2011-2012 Pants Developers (see AUTHORS.txt)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################
"""
``pants.http.client`` implements a basic asynchronous HTTP client on top of
Pants with an API modelled after that of the wonderful
`requests <http://www.python-requests.org/>`_ library. The client supports
keep-alive and SSL for connections, domain verification for SSL certificates,
basic WWW authentication, sessions with persistent cookies, automatic redirect
handling, automatic decompression of responses, connection timeouts, file
uploads, and saving large responses to temporary files to decrease
memory usage.

Logic is implemented using a series of request handlers.

Making Requests
===============

It's simple and easy to make requests, and it only requires that you have an
instance of :class:`HTTPClient` ready.

.. code-block:: python

    from pants.http import HTTPClient
    client = HTTPClient()

Like with `requests <http://www.python-requests.org/>`_, there are simple
methods for making requests with the different HTTP methods. For now, let's get
information for a bunch of Pants' commits on GitHub.

.. code-block:: python

    client.get("https://api.github.com/repos/ecdavis/pants/commits")

You'll notice that this is very similar to making a request with requests.
However, we do not get a response objects. Actually, calling
:meth:`HTTPClient.get` returns an instance of :class:`HTTPRequest` rather than
anything to do with a response, but we'll get to that later.

The Pants HTTP client is asynchronous, so to get your response, you need a
response handler. There are several ways to set one up, but the easiest way is
to pass it to your :class:`HTTPClient` during initialization.

.. code-block:: python

    def handle_response(response):
        if response.status_code != 200:
            print "There was a problem!"

    client = HTTPClient(handle_response)

``response`` in this situation is an instance of :class:`HTTPResponse`, and
it has an API modelled after the response objects that requests would give you.


Making *Useful* Requests
------------------------

Basic GET requests are nice, but you'll often want to send data to the server.
For query parameters you can use the optional *params* argument of the various
request methods, like so::

    data = {'since': '2013-11-01'}
    client.get("https://api.github.com/repos/ecdavis/pants/commits", params=data)

With that, you could eventually take your response and get the correct URL.

.. code-block:: python

    >>> response.url
    'https://api.github.com/repos/ecdavis/pants/commits?since=2013-11-01'

You can also post data to the server, either as a pre-made string, or as a
dictionary of values to be encoded.

.. code-block:: python

    client.post("http://httpbin.org/post", data="Hello World!")
    client.post("http://httpbin.org/post", data={"greeting": "Hello"})

By default, the ``Content-Type`` header will be set to
``application/x-www-form-urlencoded`` when you provide data for the request
body. If any files are present, it will instead default to
``multipart/form-data`` to transmit those. You can also manually set the
header when making your request.

You set files via the files parameter, which expects a dictionary of form field
names and file objects. You can also provide filenames if desired.

.. code-block:: python

    client.post("http://httpbin.org/post", files={'file': open("test.txt")})
    client.post("http://httpbin.org/post", files={'file': ("test.txt", open("test.txt"))})

You can, of course, use data and files together. Please note that, if you *do*
use them together, you'll need to supply data as a dictionary. Data strings are
not supported.

As many of you have probably noticed, this is *very* similar to using
`requests <http://www.python-requests.org/>`_. The Pants API was implemented
this way to make it easier to switch between the two libraries.


Reading Responses
=================

Making your request is only half the battle, of course. You have to read your
response when it comes in. And, for that, you start with the status code.

.. code-block:: python

    >>> response.status_code
    200
    >>> response.status_text
    'OK'
    >>> response.status
    '200 OK'

Unlike with requests, there is no ``raise_for_status()`` method available.
Raising a strange exception in an asynchronous framework that your code isn't
designed to catch just wouldn't work.


Headers
-------

HTTP headers are case-insensitive, and so the headers are stored in a special
case-insensitive dictionary made available as :attr:`HTTPResponse.headers`.

.. code-block:: python

    >>> response.headers
    HTTPHeaders({
        'Content-Length': 986,
        'Server': 'gunicorn/0.17.4',
        'Connection': 'keep-alive',
        'Date': 'Wed, 06 Nov 2013 05:58:53 GMT',
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
        })
    >>> response.headers['content-length']
    986

Nothing special here.


Cookies
-------

Cookies are a weak point of Pants' HTTP client at this time. Cookies are stored
in instances of :class:`Cookie.SimpleCookie`, which doesn't handle multiple
domains. Pants has logic to prevent sending cookies to the wrong domains, but
ideally it should move to using a better cookie storage structure in future
versions that handles multiple domains elegantly.

.. code-block:: python

    >>> response.cookies['cake']
    <Morsel: cake='lie'>
    >>> response.cookies['cake'].value
    'lie'

As you can see, Pants does not yet handle cookies as well as requests. Setting
cookies is a bit better.

.. code-block:: python

    client.get("http://httpbin.org/cookies", cookies={"cake": "lie"})


Redirects
---------

The HTTP client will follow redirects automatically. When this happens, the
redirecting responses are stored in the :attr:`HTTPResponse.history` list.

.. code-block:: python

    >>> response.history
    [<HTTPResponse [301 Moved Permanently] at 0x2C988F0>]

You can limit the number of times the HTTP client will automatically follow
redirects with the ``max_redirects`` argument.

.. code-block:: python

    client.get("http://github.com/", max_redirects=0)

By default, Pants will follow up to 10 redirects.


"""

###############################################################################
# Imports
###############################################################################

import codecs
import Cookie
import json
import os
import ssl
import tempfile
import urllib
import urlparse
import zlib

from datetime import datetime

from pants.stream import Stream
from pants.engine import Engine

from pants.http.auth import BasicAuth
from pants.http.utils import CRLF, date, DOUBLE_CRLF, encode_multipart, log, \
    read_headers, USER_AGENT

try:
    from backports.ssl_match_hostname import match_hostname, CertificateError
except ImportError:
    match_hostname = None
    class CertificateError(Exception):
        pass

###############################################################################
# Exports
###############################################################################

__all__ = (
    # Exceptions
    "HTTPClientException", "RequestTimedOut", "MalformedResponse",
    "RequestClosed",

    # Core Classes
    "HTTPClient", "Session", "HTTPResponse",
)

###############################################################################
# Constants
###############################################################################

CHUNK_SIZE = 2 ** 16
MAX_MEMORY_SIZE = 2 ** 20


###############################################################################
# Exceptions
###############################################################################

class HTTPClientException(Exception):
    """
    The base exception for all the exceptions used by the HTTP client, aside
    from :class:`CertificateError`.
    """
    pass


class RequestTimedOut(HTTPClientException):
    """ The exception returned when a connection times out. """
    pass


class MalformedResponse(HTTPClientException):
    """ The exception returned when the response is malformed in some way. """
    pass


class RequestClosed(HTTPClientException):
    """
    The exception returned when the connection closes before the entire
    request has been downloaded.
    """
    pass


###############################################################################
# Content Encoding
###############################################################################

CONTENT_ENCODING = {}

def encoding_gzip():
    return zlib.decompressobj(16 + zlib.MAX_WBITS)
CONTENT_ENCODING['gzip'] = encoding_gzip


def encoding_deflate():
    return zlib.decompressobj(-zlib.MAX_WBITS)
CONTENT_ENCODING['deflate'] = encoding_deflate


###############################################################################
# Cookie Loading
###############################################################################

def _get_cookies(request):
    """ Build a SimpleCookie with all the necessary cookies. """
    cookies = Cookie.SimpleCookie()
    if request.cookies:
        for key in request.cookies:
            cookies.load(request.cookies[key].output(None, ''))
    if request.cookies is not request.session.cookies:
        _load_cookies(cookies, request.session)
    elif request.session.parent:
        _load_cookies(cookies, request.session.parent)
    return cookies


def _load_cookies(cookies, session):
    if session.cookies:
        for key in session.cookies:
            if not key in cookies:
                cookies.load(session.cookies[key].output(None, ''))
    if session.parent:
        _load_cookies(cookies, session.parent)


###############################################################################
# Getting Hostname and Port on Python <2.7
###############################################################################

def _hostname(parts):
    # This code is borrowed from Python 2.7's argparse.
    netloc = parts.netloc.split('@')[-1]
    if '[' in netloc and ']' in netloc:
        return netloc.split(']')[0][1:].lower()
    elif ':' in netloc:
        return netloc.split(':')[0].lower()
    elif not netloc:
        return None
    else:
        return netloc.lower()


def _port(parts):
    # This code is borrowed from Python 2.7's argparse.
    netloc = parts.netloc.split('@')[-1].split(']')[-1]
    if ':' in netloc:
        port = netloc.split(':')[1]
        return int(port, 10)
    else:
        return None


###############################################################################
# _HTTPStream Class
###############################################################################

class _HTTPStream(Stream):
    """
    The _HTTPStream is a basic Pants client with an extra function for
    determining if it can connect to a given host without being destroyed and
    recreated. This is useful when dealing with proxies.

    It also automatically connects to the provided HTTPClient.
    """

    _host = None

    def __init__(self, client, *args, **kwargs):
        Stream.__init__(self, *args, **kwargs)
        self.client = client

        # This should be true when connected to certain proxies.
        self.need_full_url = False

    def can_fetch(self, host, is_secure):
        """
        Returns True if this stream can connect to the provided host (a string
        of ``"host:port"``) with HTTP (or HTTPS if is_secure is True), or
        False otherwise.
        """
        if not self.connected:
            return True
        if self.ssl_enabled != is_secure:
            return False

        if isinstance(self._host, basestring):
            if self._host != host:
                return False
        else:
            host, port = host.split(':')
            port = int(port)
            if host != self._host or port != self.remote_address[-1]:
                return False

        return True

    def connect(self, addr):
        if isinstance(addr, basestring):
            self._host = addr
        else:
            self._host = "%s:%d" % (addr[0], addr[-1])

        if self.connected:
            self._safely_call(self.on_connect)
        else:
            Stream.connect(self, addr)

    def on_connect(self):
        self.client._on_connect()

    def on_close(self):
        self.client._on_close()

    def on_connect_error(self, err):
        self.client._on_connect_error(err)

    def on_read_error(self, err):
        self.client._do_error(err)

    def on_overflow_error(self, err):
        self.client._do_error(err)


###############################################################################
# HTTPClient Class
###############################################################################

class HTTPClient(object):
    """
    An easy to use, asynchronous HTTP client implementing HTTP 1.1. All
    arguments passed to HTTPClient are used to initialize the default session.
    See :class:`Session` for more details. The following is a basic example of
    using an HTTPClient to fetch a remote resource::

        from pants.http import HTTPClient
        from pants.engine import Engine

        def response_handler(response):
            Engine.instance().stop()
            print response.content

        client = HTTPClient(response_handler)
        client.get("http://httpbin.org/ip")
        Engine.instance().start()

    Groups of requests can have their behavior customized with the use of
    sessions::

        from pants.http import HTTPClient
        from pants.engine import Engine

        def response_handler(response):
            Engine.instance().stop()
            print response.content

        def other_handler(response):
            print response.content

        client = HTTPClient(response_handler)
        client.get("http://httpbin.org/cookies")

        with client.session(cookies={'pie':'yummy'}):
            client.get("http://httpbin.org/cookies")

        Engine.instance().start()

    """

    def __init__(self, *args, **kwargs):
        """ Initialize the HTTPClient and start the first session. """

        # Figure out our engine.
        if 'engine' in kwargs:
            self.engine = kwargs.pop("engine")
        else:
            self.engine = Engine.instance()

        # Internal State
        self._stream = None
        self._processing = None
        self._requests = []
        self._sessions = []
        self._ssl_options = None
        self._reading_forever = False
        self._want_close = False
        self._no_process = False

        # Create the first Session
        ses = Session(self, *args, **kwargs)
        self._sessions.append(ses)


    ##### Public Event Handlers ###############################################

    def on_response(self, response):
        """
        Placeholder. Called when a complete response has been received.

        =========  ============
        Argument   Description
        =========  ============
        response   A :class:`HTTPResponse` instance with information about the received response.
        =========  ============
        """
        pass


    def on_headers(self, response):
        """
        Placeholder. Called when we've received headers for a request. You can
        abort a request at this time by returning False from this function. It
        *must* be False, and not simply a false-like value, such as an empty
        string.

        .. note::

            This function isn't called for HTTP ``HEAD`` requests.

        =========  ============
        Argument   Description
        =========  ============
        response   A :class:`HTTPResponse` instance with information about the received response.
        =========  ============
        """
        pass


    def on_progress(self, response, received, total):
        """
        Placeholder. Called when progress is made in downloading a response.

        =========  ============
        Argument   Description
        =========  ============
        response   A :class:`HTTPResponse` instance with information about the response.
        received   The number of bytes received thus far.
        total      The total number of bytes expected for the response. This will be ``0`` if we don't know how much to expect.
        =========  ============
        """
        pass


    def on_ssl_error(self, response, certificate, exception):
        """
        Placeholder. Called when the remote server's SSL certificate failed
        initial verification. If this method returns True, the certificate will
        be accepted, otherwise, the connection will be closed and
        :func:`on_error` will be called.

        ============  ============
        Argument      Description
        ============  ============
        response      A :class:`HTTPResponse` instance with information about the response. Notably, with the ``host`` to expect.
        certificate   A dictionary representing the certificate that wasn't automatically verified.
        exception     A CertificateError instance with information about the error that occurred.
        ============  ============
        """
        return False


    def on_error(self, response, exception):
        """
        Placeholder. Called when an error occurs.

        ==========  ============
        Argument    Description
        ==========  ============
        exception   An Exception instance with information about the error that occurred.
        ==========  ============
        """
        pass


    ##### Session Generation ##################################################

    def session(self, *args, **kwargs):
        """ Create a new session. See :class:`Session` for details. """
        return Session(self, *args, **kwargs)


    ##### Request Making ######################################################

    def request(self, *args, **kwargs):
        """
        Begin a request. Missing parameters will be taken from the active
        session when available. See :func:`Session.request` for more details.
        """
        return self._sessions[-1].request(*args, **kwargs)


    def delete(self, url, **kwargs):
        """ Begin a DELETE request. See :func:`request` for more details. """
        return self.request("DELETE", url, **kwargs)


    def get(self, url, params=None, **kwargs):
        """ Begin a GET request. See :func:`request` for more details. """
        return self.request("GET", url, params=params, **kwargs)


    def head(self, url, params=None, **kwargs):
        """ Begin a HEAD request. See :func:`request` for more details. """
        return self.request("HEAD", url, params=params, **kwargs)


    def options(self, url, **kwargs):
        """ Begin an OPTIONS request. See :func:`request` for more details. """
        return self.request("OPTIONS", url, **kwargs)


    def patch(self, url, data=None, **kwargs):
        """ Begin a PATCH request. See :func:`request` for more details. """
        return self.request("PATCH", url, data=data, **kwargs)


    def post(self, url, data=None, files=None, **kwargs):
        """ Begin a POST request. See :func:`request` for more details. """
        return self.request("POST", url, data=data, files=files, **kwargs)


    def put(self, url, data=None, **kwargs):
        """ Begin a PUT request. See :func:`request` for more details. """
        return self.request("PUT", url, data=data, **kwargs)


    def trace(self, url, **kwargs):
        """ Begin a TRACE request. See :func:`request` for more details. """
        return self.request("TRACE", url, **kwargs)


    ##### Internals ###########################################################

    def _safely_call(self, thing_to_call, *args, **kwargs):
        """
        Safely execute a callable.

        The callable is wrapped in a try block and executed. If an
        exception is raised it is logged.

        ==============  ============
        Argument        Description
        ==============  ============
        thing_to_call   The callable to execute.
        *args           The positional arguments to be passed to the callable.
        **kwargs        The keyword arguments to be passed to the callable.
        ==============  ============
        """
        try:
            return thing_to_call(*args, **kwargs)
        except Exception:
            log.exception("Exception raised in callback on %r." % self)


    def _process(self):
        """ Send the first request on the stack. """
        if not self._requests:
            # Stop processing and close any connection since we've not got any
            # requests left.
            if self._stream:
                self._want_close = True
                self._no_process = True
                self._stream.close(False)
                self._stream = None
            self._processing = False
            return
        self._processing = True

        # Get the request.
        request = self._requests[0]

        # Make sure it has a response.
        if not request.response:
            HTTPResponse(request)

        # Handle authentication.
        if request.auth and not isinstance(request.auth, (list,tuple)):
            request = request.auth(request)

        # Now, determine what we should be connected to.
        port = _port(request.url)
        is_secure = request.url.scheme == 'https'
        if not port:
            port = 443 if is_secure else 80
        host = '%s:%d' % (_hostname(request.url), port)

        # If we have a stream, and it's not connected to that host, kill it
        # to make a new one.
        if self._stream:
            if not self._stream.connected:
                self._stream = None
            elif self._ssl_options != request.session.ssl_options or \
                    not self._stream.can_fetch(host, is_secure):
                log.debug("Closing unusable stream for %r." % self)
                self._want_close = True
                self._no_process = False
                self._stream.close(False)
                return

        # Set the timeout timer and log.
        log.debug("Sending HTTP request %r." % request)
        self._reset_timer()

        # Create a stream.
        if not self._stream:
            self._stream = _HTTPStream(self, engine=self.engine)

        # If we're secure, and the stream isn't, secure it.
        if is_secure and not self._stream.ssl_enabled:
            self._ssl_options = request.session.ssl_options
            self._stream.startSSL(self._ssl_options or {})

        # Connect the stream to await further orders.
        self._stream.connect((_hostname(request.url), port))


    def _timed_out(self, request):
        """ Called when a request times out. """
        if not request in self._requests:
            return

        log.debug("HTTP request %r timed out." % request)

        self._requests.remove(request)
        request.session.on_error(request.response, RequestTimedOut())

        # Now, close the connection, and keep processing.
        if self._stream:
            self._want_close = True
            self._no_process = True
            self._stream.close(False)
            self._stream = None
        self._process()


    def _reset_timer(self):
        if not self._requests:
            return
        request = self._requests[0]

        # Clear the existing timer.
        if request._timeout_timer:
            request._timeout_timer()

        request._timeout_timer = self.engine.defer(request.timeout,
                                                   self._timed_out, request)


    ##### Stream I/O Handlers #################################################

    def _on_connect(self):
        """ The Stream connected, so send the request. """
        if not self._requests:
            return
        request = self._requests[0]
        self._reset_timer()

        # Check our security.
        if request.url.scheme == 'https' and request.session.verify_ssl:
            # We care!
            cert = self._stream._socket.getpeercert()
            try:
                match_hostname(cert, _hostname(request.url))
            except CertificateError as err:
                if not self._safely_call(request.session.on_ssl_error,
                        request.response, cert, err):
                    self._do_error(err)
                    return

        # Write the request.
        if self._stream.need_full_url:
            path = "%s://%s%s" % (request.url.scheme, request.url.netloc,
                                  request.path)
        else:
            path = request.path

        self._stream.write("%s %s HTTP/1.1%s" % (request.method, path, CRLF))

        # Headers
        for key, val in request.headers.iteritems():
            self._stream.write("%s: %s%s" % (key, val, CRLF))

        # Cookies
        cookies = _get_cookies(request)
        if cookies:
            for key in cookies:
                morsel = cookies[key]
                if not request.path.startswith(morsel['path']) or \
                        not _hostname(request.url).lower().\
                        endswith(morsel['domain'].lower()) or \
                        morsel['secure'] and request.url.scheme != 'https':
                    continue
                self._stream.write(morsel.output(None, 'Cookie:') + CRLF)

        # And now, the body.
        self._stream.write(CRLF)
        if request.body:
            for item in request.body:
                if isinstance(item, basestring):
                    self._stream.write(item)
                else:
                    self._stream.write_file(item)

        # Now, we wait for a response.
        self._stream.on_read = self._read_headers
        self._stream.read_delimiter = DOUBLE_CRLF


    def _on_connect_error(self, err):
        """ The Stream had an exception. Pass it along. """
        if not self._requests:
            return

        # Pop off the request that had an error, and clear its timeout.
        request = self._requests.pop(0)
        if request._timeout_timer:
            request._timeout_timer()

        # Do the error method.
        self._safely_call(request.session.on_error, request.response, err)

        # Kill the stream.
        if self._stream:
            self._want_close = True
            self._no_process = True
            self._stream.close(False)
            self._stream = None

        # Keep processing, if needed.
        self._process()


    def _on_close(self):
        """
        If we weren't expecting the stream to close, it's an error, otherwise,
        just process our requests.
        """

        # Are we reading forever?
        if self._reading_forever:
            self._reading_forever = False
            # Right, clean up then.
            if self._requests:
                # Get the request.
                request = self._requests[0]
                response = request.response

                # Clean out the decoder.
                if response._decoder:
                    response._receive(response._decoder.flush())
                    response._receive(response._decoder.unused_data)
                    response._decoder = None

                # Now, go to _on_response.
                self._want_close = False
                self._no_process = False
                self._on_response()
                return

        elif not self._want_close:
            # If it's not an expected close, check for an active request and
            # error it.
            self._want_close = False
            if self._requests:
                request = self._requests[0]
                self._no_process = False
                self._do_error(RequestClosed("The server closed the "
                                             "connection."))
                return

        # Keep processing, if needed.
        self._stream = None
        if self._no_process:
            self._no_process = False
        else:
            self._process()


    def _do_error(self, err):
        """
        There was some kind of exception. Close the stream, report it, and then
        keep processing.
        """
        self._want_close = True
        self._no_process = True
        self._stream.close(False)
        self._stream = None
        if not self._requests:
            return

        # Pop off the request that had an error, and clear its timeout.
        request = self._requests.pop(0)
        if request._timeout_timer:
            request._timeout_timer()

        self._safely_call(request.session.on_error, request.response, err)

        # Keep processing, if needed.
        self._process()


    def _read_headers(self, data):
        """
        Read the headers of an HTTP response from the socket into the current
        HTTPResponse object, and prepare to read the body. Or, if necessary,
        follow a redirect.
        """
        if not self._requests:
            return
        request = self._requests[0]
        response = request.response
        self._reset_timer()

        ind = data.find(CRLF)
        if ind == -1:
            initial_line = data
            data = ''
        else:
            initial_line = data[:ind]
            data = data[ind+2:]
        try:
            http_version, status, status_text = initial_line.split(' ', 2)
            status = int(status)
            if not http_version.startswith('HTTP/'):
                self._do_error(MalformedResponse("Invalid HTTP protocol "
                                                 "version %r." % http_version))
                return
        except ValueError:
            self._do_error(MalformedResponse("Invalid status line."))
            return

        # Parse the headers.
        headers = read_headers(data) if data else {}

        # Store what we've got so far on the response.
        response.http_version = http_version
        response.status_code = status
        response.status_text = status_text
        response.headers = headers

        # Load any cookies.
        if 'Set-Cookie' in headers:
            if not response.cookies:
                request.cookies = Cookie.SimpleCookie()
                response.cookies = request.session.cookies = request.cookies

            cookies = headers['Set-Cookie']
            if not isinstance(cookies, list):
                cookies = [cookies]
            for val in cookies:
                val_jar = Cookie.SimpleCookie()
                val_jar.load(val)
                for key in val_jar:
                    morsel = val_jar[key]
                    if not morsel['domain']:
                        morsel['domain'] = _hostname(request.url)
                    response.cookies.load(morsel.output(None, ''))

        # Are we dealing with a HEAD request?
        if request.method == 'HEAD':
            # Just be done.
            self._on_response()
            return

        # Do the on_headers callback.
        continue_request = self._safely_call(request.session.on_headers,
                                             response)
        if continue_request is False:
            # Abort the connection now.
            self._requests.pop(0)
            self._want_close = True
            self._no_process = False
            self._stream.close(False)
            return

        # Is there a Content-Length header?
        if 'Content-Length' in headers:
            response.length = int(headers['Content-Length'])
            response.remaining = response.length

            # If there's no length, immediately we've got a response.
            if not response.remaining:
                self._on_response()
                return

            self._stream.on_read = self._read_body
            self._stream.read_delimiter = min(CHUNK_SIZE, response.remaining)

        # What about Transfer-Encoding?
        elif 'Transfer-Encoding' in headers:
            if headers['Transfer-Encoding'] != 'chunked':
                self._do_error(MalformedResponse(
                                "Unable to handle Transfer-Encoding %r." %
                                headers['Transfer-Encoding']))
                return

            response.length = 0
            self._stream.on_read = self._read_chunk_head
            self._stream.read_delimiter = CRLF

        # Is this not a persistent connection? If so, read the whole body.
        elif not response._keep_alive:
            response.length = 0
            response.remaining = 0
            self._reading_forever = True
            self._stream.on_read = self._read_forever

            # We have to have a read_delimiter of None, otherwise our data
            # gets deleted when the connection is closed.
            self._stream.read_delimiter = None

        # There must not be a body, so go ahead and be done.
        else:
            # We've got a response.
            self._on_response()
            return

        # Do we have any Content-Encoding?
        if 'Content-Encoding' in headers:
            encoding = headers['Content-Encoding']
            if not encoding in CONTENT_ENCODING:
                self._do_error(MalformedResponse(
                           "Unable to handle Content-Encoding %r." % encoding))
                return
            response._decoder = CONTENT_ENCODING[encoding]()


    def _on_response(self):
        """
        A response has been completed. Send it on through.
        """
        if not self._requests:
            return
        request = self._requests.pop(0)
        response = request.response

        # Do we have Connection: close?
        if not response._keep_alive:
            self._want_close = True
            self._no_process = True
            self._stream.close(False)
            self._stream = None

        # Clear the existing timer.
        if request._timeout_timer:
            request._timeout_timer()

        # Check for a status code handler.
        handler = getattr(response, 'handle_%d' % response.status_code, None)
        if handler:
            response = self._safely_call(handler, self)
            if not response:
                return

        self._safely_call(request.session.on_response, response)
        # Keep processing, if needed.
        self._process()


    ##### Length-Based Responses ##############################################

    def _read_forever(self, data):
        """
        Read until the connection closes.
        """
        if not self._requests:
            return
        request = self._requests[0]
        response = request.response
        self._reset_timer()

        # Make note of how many bytes we've received.
        response.length += len(data)

        # Decode the received data.
        if response._decoder:
            data = response._decoder.decompress(data)

        # Now, store that.
        response._receive(data)

        # Do a progress.
        self._safely_call(request.session.on_progress, response,
                          response.length, 0)


    def _read_body(self, data):
        """
        Add the data we received to the response body, doing any necessary
        decompression and character set nonsense.
        """
        if not self._requests:
            return
        request = self._requests[0]
        response = request.response
        self._reset_timer()

        # Make note of how many bytes we've received.
        response.remaining -= len(data)
        self._stream.read_delimiter = min(CHUNK_SIZE, response.remaining)
        finished = not response.remaining and not response.remaining is False

        # Decode the received data.
        if response._decoder:
            data = response._decoder.decompress(data)
            if finished:
                data += response._decoder.flush()
                data += response._decoder.unused_data
                response._decoder = None

        # Now, store that.
        response._receive(data)

        # Do a progress.
        self._safely_call(request.session.on_progress, response,
                          response.length-response.remaining, response.length)

        # Do a finished?
        if finished:
            self._on_response()


    ##### Chunked Responses ###################################################

    def _read_additional_headers(self, data):
        """ Read additional headers for the response. """
        if not self._requests:
            return
        request = self._requests[0]
        response = request.response
        self._reset_timer()

        # Build the additional headers data.
        if data:
            response._additional_headers += data + CRLF
            return

        # We're done, so parse those.
        headers = read_headers(response._additional_headers)
        del response._additional_headers

        # Extend the original headers.
        for key, val in headers.iteritems():
            if not key in response.headers:
                response.headers[key] = val
            else:
                if not isinstance(response.headers[key], list):
                    response.headers[key] = [response.headers[key]]
                if isinstance(val, (tuple,list)):
                    response.headers[key].extend(val)
                else:
                    response.headers[key].append(val)

        # Finally, we can handle it.
        self._on_response()


    def _read_chunk_head(self, data):
        """ Read a chunk header. """
        if not self._requests:
            return
        request = self._requests[0]
        response = request.response
        self._reset_timer()

        # Chop off any chunk extension data. We don't care about it.
        if ';' in data:
            data, ext = data.split(';', 1)

        # Get the length of the chunk.
        length = int(data.strip(), 16)

        if not length:
            # We're finished! Flush the decompressor if we have one, and move
            # on to the additional headers.
            if response._decoder:
                response._receive(response._decoder.flush())
                response._receive(response._decoder.unused_data)
                response._decoder = None

            self._stream.on_read = self._read_additional_headers
            response._additional_headers = ''
            self._stream.read_delimiter = CRLF

        else:
            # Read the new chunk.
            length += 2
            self._stream.on_read = self._read_chunk_body
            response.remaining = length
            self._stream.read_delimiter = min(CHUNK_SIZE, length)


    def _read_chunk_body(self, data):
        """ Read a chunk body. """
        if not self._requests:
            return
        request = self._requests[0]
        response = request.response
        self._reset_timer()

        # Make note of how many bytes we've received.
        bytes = len(data)
        response.remaining -= bytes
        response.length += bytes
        self._stream.read_delimiter = min(CHUNK_SIZE, response.remaining)

        # Pass the data through our decoder.
        data = data[:-2]
        if response._decoder:
            data = response._decoder.decompress(data)

        # Store this data.
        response._receive(data)

        # Do a progress event.
        self._safely_call(request.session.on_progress, response,
                          response.length, 0)

        # If we're finished with this chunk, read a new header.
        if not response.remaining:
            self._stream.on_read = self._read_chunk_head
            self._stream.read_delimiter = CRLF


###############################################################################
# Session Class
###############################################################################

class Session(object):
    """
    The Session class is the heart of the HTTP client, making it easy to share
    state between multiple requests, and enabling the use of ``with`` syntax.
    They're responsible for determining everything about a request before
    handing it back to :class:`HTTPClient` to be executed.

    ===============  ==========  ============
    Argument         Default     Description
    ===============  ==========  ============
    client                       The :class:`HTTPClient` instance this Session is associated with.
    on_response                  *Optional.* A callable that will handle any received responses, rather than the HTTPClient's own :func:`on_response` method.
    on_headers                   *Optional.* A callable for when response headers have been received.
    on_progress                  *Optional.* A callable for progress notifications.
    on_ssl_error                 *Optional.* A callable responsible for handling SSL verification errors, if ``verify_ssl`` is True.
    on_error                     *Optional.* A callable that will handle any errors that occur.
    timeout          ``30``      *Optional.* The time to wait, in seconds, of no activity to allow before timing out.
    max_redirects    ``10``      *Optional.* The maximum number of times to follow a server-issued redirect.
    keep_alive       ``True``    *Optional.* Whether or not a single connection will be reused for multiple requests.
    auth             ``None``    *Optional.* An instance of :class:`AuthBase` for authenticating requests to the server.
    headers          ``None``    *Optional.* A dictionary of default headers to send with requests.
    verify_ssl       ``False``   *Optional.* Whether or not to attempt to check the certificate of the remote secure server against its hostname.
    ssl_options      ``None``    *Optional.* Options to use when initializing SSL. See :func:`Stream.startSSL` for more.
    ===============  ==========  ============
    """

    def __init__(self, client, on_response=None, on_headers=None,
                 on_progress=None, on_ssl_error=None, on_error=None,
                 timeout=None, max_redirects=None, keep_alive=None, auth=None,
                 headers=None, cookies=None, verify_ssl=None,
                 ssl_options=None):
        """ Initialize the Session. """
        # Store the client and parent.
        if isinstance(client, Session):
            self.parent = parent = client
            self.client = client = self.parent.client
        else:
            self.client = client
            parent = client._sessions[-1] if client._sessions else None
            self.parent = parent

        # Setup our default settings.
        if on_response is None:
            on_response = parent.on_response if parent else client.on_response
        if on_headers is None:
            on_headers = parent.on_headers if parent else client.on_headers
        if on_progress is None:
            on_progress = parent.on_progress if parent else client.on_progress
        if on_ssl_error is None:
            if parent:
                on_ssl_error = parent.on_ssl_error
            else:
                on_ssl_error = client.on_ssl_error
        if on_error is None:
            on_error = parent.on_error if parent else client.on_error
        if timeout is None:
            timeout = parent.timeout if parent else 30
        if max_redirects is None:
            max_redirects = parent.max_redirects if parent else 10
        if keep_alive is None:
            keep_alive = parent.keep_alive if parent else True
        if auth is None:
            auth = parent.auth if parent else None
        if headers is None:
            headers = {}
            if parent and parent.headers:
                headers.update(parent.headers)
        if verify_ssl is None:
            verify_ssl = parent.verify_ssl if parent else False
        if ssl_options is None:
            ssl_options = parent.ssl_options if parent else None

        # Do some logic about SSL verification.
        if verify_ssl:
            if not ssl_options:
                # This logic comes from requests.
                loc = None
                if verify_ssl is not True:
                    loc = verify_ssl
                if not loc:
                    loc = os.environ.get('PANTS_CA_BUNDLE')
                if not loc:
                    loc = os.environ.get('CURL_CA_BUNDLE')
                if not loc:
                    try:
                        import certifi
                        loc = certifi.where()
                    except ImportError:
                        pass
                if not loc:
                    raise RuntimeError("Cannot find certificates for SSL "
                                       "verification.")
                ssl_options = {'ca_certs': loc, 'cert_reqs': ssl.CERT_REQUIRED}

            # Make sure we've got backports.ssl_match_hostname
            if not match_hostname:
                raise RuntimeError("Cannot verify SSL certificates without "
                                   "the package backports.ssl_match_hostname.")

        # Ensure the cookies are a cookiejar.
        if cookies is None:
            cookies = Cookie.SimpleCookie()
        elif isinstance(cookies, dict):
            cookies = Cookie.SimpleCookie(cookies)

        # Store our settings now.
        self.on_response = on_response
        self.on_headers = on_headers
        self.on_progress = on_progress
        self.on_ssl_error = on_ssl_error
        self.on_error = on_error
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.keep_alive = keep_alive
        self.auth = auth
        self.headers = headers
        self.cookies = cookies
        self.verify_ssl = verify_ssl
        self.ssl_options = ssl_options


    ##### Session Generation ##################################################

    def session(self, *args, **kwargs):
        """ Create a new session. See :class:`Session` for details. """
        return Session(self, *args, **kwargs)


    ##### Request Making ######################################################

    def request(self, method, url, params=None, data=None, headers=None,
                cookies=None, files=None, auth=None, timeout=None,
                max_redirects=None, keep_alive=None):
        """
        Begin a request.

        ==============  ============
        Argument        Description
        ==============  ============
        method          The HTTP method of the request.
        url             The URL to request.
        params          *Optional.* A dictionary or string of query parameters to add to the request.
        data            *Optional.* A dictionary or string of content to send in the request body.
        headers         *Optional.* A dictionary of headers to send with the request.
        cookies         *Optional.* A dictionary or CookieJar of cookies to send with the request.
        files           *Optional.* A dictionary of file-like objects to upload with the request.
        auth            *Optional.* An instance of :class:`AuthBase` to use to authenticate the request.
        timeout         *Optional.* The time to wait, in seconds, of no activity to allow before timing out.
        max_redirects   *Optional.* The maximum number of times to follow a server-issued redirect.
        keep_alive      *Optional.* Whether or not to reuse the connection for multiple requests.
        ==============  ============
        """
        method = str(method).upper()

        # Parse the URL.
        parts = urlparse.urlparse(url)
        if not parts.scheme in ("http", "https"):
            raise ValueError("HTTPClient unable to serve request with scheme "
                             "%r." % parts.scheme)

        # Get default values from the session if necessary
        if timeout is None:
            timeout = self.timeout
        if max_redirects is None:
            max_redirects = self.max_redirects
        if keep_alive is None:
            keep_alive = self.keep_alive
        if auth is None:
            auth = self.auth
        if cookies is None:
            cookies = self.cookies
        elif isinstance(cookies, dict):
            cookies = Cookie.SimpleCookie(cookies)

        # Build the headers.
        if not headers:
            headers = {}

        # Update with all the default headers.
        for key in self.headers:
            if not key in headers:
                headers[key] = self.headers[key]

        # Add an extra header or two.
        if not 'Accept-Encoding' in headers:
            headers['Accept-Encoding'] = 'deflate, gzip'

        if not 'Date' in headers:
            headers['Date'] = date(datetime.utcnow())

        if not 'Host' in headers:
            headers['Host'] = _hostname(parts)
            port = _port(parts)
            if port:
                headers['Host'] += ':%d' % port

        if not 'User-Agent' in headers:
            headers['User-Agent'] = USER_AGENT

        if not 'Connection' in headers and not keep_alive:
            headers['Connection'] = 'close'

        # Determine the Content-Type of the request body.
        if files:
            hdr = headers.get('Content-Type')
            if hdr and not hdr.startswith("multipart/form-data"):
                raise ValueError("Cannot transmit files with Content-Type "
                                 "%r." % hdr)
            elif not hdr:
                headers['Content-Type'] = 'multipart/form-data'
        elif not 'Content-Type' in headers and data:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        # Construct the actual request body. This is a mess.
        if 'Content-Type' in headers:
            hdr = headers['Content-Type']
            if isinstance(data, bytes):
                body = [data]
                length = len(data)
            elif hdr.startswith('multipart/form-data'):
                ind = hdr.find('boundary=')
                if ind != -1:
                    boundary = hdr[ind+9:]
                else:
                    boundary = None

                boundary, body = encode_multipart(data or {}, files, boundary)
                headers['Content-Type'] = 'multipart/form-data; boundary=%s' \
                                            % boundary
                length = 0
                for item in body:
                    if isinstance(item, basestring):
                        length += len(item)
                    else:
                        item.seek(0, 2)
                        length += item.tell()
            elif hdr == 'application/x-www-form-urlencoded':
                if isinstance(data, dict):
                    body = [urllib.urlencode(data or {}, True)]
                    length = len(body[0])
                elif not data:
                    body = []
                    length = 0
                else:
                    body = [data]
                    length = len(body[0])
            else:
                raise ValueError("Unknown Content-Type %r." % hdr)
            headers['Content-Length'] = length
        else:
            body = None

        # Deal with the request parameters and the URL fragment.
        path = parts.path or '/'
        if params:
            new_params = urlparse.parse_qs(parts.query)
            for key, value in params.iteritems():
                if not key in new_params:
                    new_params[key] = []
                if isinstance(value, (tuple,list)):
                    new_params[key].extend(value)
                else:
                    new_params[key].append(value)

            # Update the URL parts.
            parts = parts._replace(query=urllib.urlencode(new_params,True))

        if parts.query:
            path += '?%s' % parts.query
        if parts.fragment:
            path += '#%s' % parts.fragment

        # Build our request.
        request = HTTPRequest(self, method, path, parts, headers, cookies,
                                body, timeout, max_redirects, keep_alive, auth)

        # Now, send it back to the client.
        self.client._requests.append(request)
        if not self.client._processing:
            self.client._process()

        # Not sure what you'll do with this, but there you have it.
        return request


    def delete(self, url, **kwargs):
        """ Begin a DELETE request. See :func:`request` for more details. """
        return self.request("DELETE", url, **kwargs)


    def get(self, url, params=None, **kwargs):
        """ Begin a GET request. See :func:`request` for more details. """
        return self.request("GET", url, params=params, **kwargs)


    def head(self, url, params=None, **kwargs):
        """ Begin a HEAD request. See :func:`request` for more details. """
        return self.request("HEAD", url, params=params, **kwargs)


    def options(self, url, **kwargs):
        """ Begin an OPTIONS request. See :func:`request` for more details. """
        return self.request("OPTIONS", url, **kwargs)


    def patch(self, url, data=None, **kwargs):
        """ Begin a PATCH request. See :func:`request` for more details. """
        return self.request("PATCH", url, data=data, **kwargs)


    def post(self, url, data=None, files=None, **kwargs):
        """ Begin a POST request. See :func:`request` for more details. """
        return self.request("POST", url, data=data, files=files, **kwargs)


    def put(self, url, data=None, **kwargs):
        """ Begin a PUT request. See :func:`request` for more details. """
        return self.request("PUT", url, data=data, **kwargs)


    def trace(self, url, **kwargs):
        """ Begin a TRACE request. See :func:`request` for more details. """
        return self.request("TRACE", url, **kwargs)


    ##### Context #############################################################

    def __enter__(self):
        self.client._sessions.append(self)
        return self


    def __exit__(self, *args):
        self.client._sessions.pop()


###############################################################################
# HTTPRequest Class
###############################################################################

class HTTPRequest(object):
    """ A very basic structure for storing HTTP request information. """

    response = None
    _timeout_timer = None

    def __init__(self, session, method, path, url, headers, cookies, body,
                 timeout, max_redirects, keep_alive, auth):
        self.session = session
        self.method = method
        self.path = path
        self.url = url
        self.headers = headers
        self.cookies = cookies
        self.body = body
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.keep_alive = keep_alive
        self.auth = auth


    def __repr__(self):
        return '<%s ["%s://%s%s"] at 0x%X>' % (
            self.__class__.__name__,
            self.url.scheme,
            self.url.netloc,
            self.path,
            id(self)
            )


###############################################################################
# HTTPResponse Class
###############################################################################

class HTTPResponse(object):
    """
    The HTTPResponse class represents a single HTTPResponse, and has all the
    available information about a response, including the redirect history and
    the original HTTPRequest.
    """

    total = None
    remaining = None
    http_version = None
    status_code = None
    status_text = None
    cookies = None
    headers = None

    _body_file = None
    _decoder = None
    _encoding = None

    def __init__(self, request):
        """ Initialize from the provided request. """
        self.request = request
        self.history = []

        # Store stuff about us.
        self.method = request.method
        self.url = urlparse.urlunparse(request.url)
        self.path = request.path

        # Make sure we're the request's response.
        if self.request.response:
            self.history.extend(self.request.response.history)
            self.history.insert(0, self.request.response)
        self.request.response = self

        # Set cookies.
        self.cookies = self.request.session.cookies


    @property
    def status(self):
        """ The status code and status text as a string. """
        if not self.status_code:
            return None
        if not self.status_text:
            return str(self.status_code)
        return "%d %s" % (self.status_code, self.status_text)


    def __repr__(self):
        return "<%s [%s] at 0x%X>" % (
            self.__class__.__name__,
            self.status,
            id(self)
            )


    @property
    def _keep_alive(self):
        conn = self.headers.get('Connection', '').lower()
        if self.http_version == 'HTTP/1.0':
            return conn == 'keep-alive'
        return conn != 'close'

    ##### Body Management #####################################################

    @property
    def encoding(self):
        """
        This is the detected character encoding of the response. You can also
        set this to a specific character set to have :attr:`text` decoded
        properly.

        Pants will attempt to fill this value from the Content-Type response
        header. If no value was available, it will be ``None``.
        """
        if not self._encoding:
            # Time to play guess the encoding! We don't try that hard.
            cset = self.headers.get('Content-Type').partition('charset=')[-1]
            if not cset:
                cset = None
            self._encoding = cset
        return self._encoding

    @encoding.setter
    def encoding(self, val):
        # Use codecs.lookup to make sure it's a valid way to decode text.
        if val is not None:
            codecs.lookup(val)
        self._encoding = val


    @property
    def text(self):
        """
        The content of the response, after being decoded into unicode with
        :attr:`encoding`. Be careful when using this with large responses, as
        it will load the entire response into memory. ``None`` if no data has
        been received.

        If :attr:`encoding` is ``None``, this will default to ``UTF-8``.

        """
        raw = self.content
        if not raw:
            return raw

        encoding = self.encoding
        if not encoding:
            encoding = 'utf-8'

        return raw.decode(encoding)


    def json(self, **kwargs):
        """
        The content of the response, having been interpreted as JSON. This
        uses the value of :attr:`encoding` if possible. If :attr:`encoding`
        is not set, it will default to ``UTF-8``.

        Any provided keyword arguments will be passed to :func:`json.loads`.

        """
        if not 'encoding' in kwargs:
            kwargs['encoding'] = self.encoding

        raw = self.content
        if not raw:
            return raw

        return json.loads(raw, **kwargs)


    @property
    def file(self):
        """
        The content of the response as a :class:`tempfile.SpooledTemporaryFile`.
        Pants uses temporary files to decrease memory usage for
        large responses. ``None`` if no data has been received.
        """
        return self._body_file

    # requests compatibility
    raw = file
    stream = True


    @property
    def content(self):
        """
        The content of the response as a byte string. Be careful when using
        this with large responses, as it will load the entire response into
        memory. ``None`` if no data has been received.
        """
        if not self._body_file:
            return None
        f = self._body_file._file
        if hasattr(f, 'getvalue'):
            return f.getvalue()

        current_pos = f.tell()
        f.seek(0)
        out = f.read()
        f.seek(current_pos)
        return out


    def iter_content(self, chunk_size=1, decode_unicode=False):
        """
        Iterate over the content of the response. Using this, rather than
        :attr:`content` or :attr:`text` can prevent the loading of large
        responses into memory in their entirety.

        ===============  ========  ============
        Argument         Default   Description
        ===============  ========  ============
        chunk_size       ``1``     The number of bytes to read at once.
        decode_unicode   False     Whether or not to decode the bytes into unicode using the response's :attr:`encoding`.
        ===============  ========  ============
        """
        f = self._body_file
        if not f:
            return

        if decode_unicode:
            codec = self.encoding or 'utf-8'
            decoder = codecs.getincrementaldecoder(codec)(errors='replace')
        else:
            decoder = None

        pos = 0
        while True:
            f.seek(pos)
            data = f.read(chunk_size)

            pos += len(data)
            if decoder:
                data = decoder.decode(data)

            if not data:
                if decoder:
                    final = decoder.decode(b'', final=True)
                    if final:
                        yield final
                return

            yield data


    def iter_lines(self, chunk_size=512, decode_unicode=False):
        """
        Iterate over the content of the response, one line at a time. By
        using this rather than :attr:`content` or :attr:`text` you can
        prevent loading of the entire response into memory. The two arguments
        to this method are passed directly to :meth:`iter_content`.
        """
        # This method's implementation shamelessly copied from requests.
        pending = None
        for chunk in self.iter_content(chunk_size=chunk_size,
                                       decode_unicode=decode_unicode):
            if pending:
                chunk = pending + chunk

            lines = chunk.splitlines()
            if lines and lines[-1] and chunk and lines[-1][-1] == chunk[-1]:
                pending = lines.pop()
            else:
                pending = None

            for line in lines:
                yield line

        if pending is not None:
            yield pending

    # Let people easily iterate over lines.
    __iter__ = iter_lines


    def _receive(self, data):
        if not self._body_file:
            self._init_body()
        self._body_file.write(data)


    def _init_body(self):
        self._body_file = tempfile.SpooledTemporaryFile(MAX_MEMORY_SIZE)


    ##### Status Code Handlers ################################################

    def handle_301(self, client):
        """ Handle the different redirect codes. """
        request = self.request
        if not request.max_redirects or not 'Location' in self.headers:
            return self

        # Get some useful things.
        status = self.status_code
        method = self.method
        body = request.body
        location = self.headers['Location']
        log.debug("Redirecting request %r to %r." % (request, location))

        # Update the request and send it again.
        try:
            # Update the URL.
            location = urlparse.urljoin(urlparse.urlunparse(request.url),
                                        location)
            parts = urlparse.urlparse(location)
            if not parts.scheme in ("http", "https"):
                raise MalformedResponse

            # Do special stuff for certain codes.
            if status == 301 and not method in ('GET', 'HEAD'):
                raise MalformedResponse
            elif status in (302, 303):
                method = 'GET'
                body = None

            host = _hostname(parts)
            port = _port(parts)
            if port:
                host += ':%d' % port

            # Update the request.
            request.url = parts
            request.path = parts.path or '/'
            request.method = method
            request.body = body
            request.headers['Host'] = host
            request.max_redirects -= 1

            # Make the new response, process it, and return.
            HTTPResponse(request)
            client._requests.insert(0, request)
            client._process()
            return
        except MalformedResponse:
            return self

    handle_302 = handle_303 = handle_307 = handle_301


    def handle_401(self, client):
        """ Handle authorization, if we know how. """
        request = self.request
        if not isinstance(request.auth, (list,tuple)) or \
                not 'WWW-Authenticate' in self.headers:
            return self

        auth_type, options = self.headers['WWW-Authenticate'].split(' ',1)
        if not auth_type.lower() in ('digest', 'basic'):
            return self

        # If it's basic, do that.
        if auth_type.lower() == 'basic':
            request.auth = BasicAuth(*request.auth)
        else:
            # TODO: Write Digest authentication.
            # request.auth = DigestAuth(*request.auth)
            return self

        # Now, resend.
        HTTPResponse(request)
        client._requests.insert(0, request)
        client._process()
