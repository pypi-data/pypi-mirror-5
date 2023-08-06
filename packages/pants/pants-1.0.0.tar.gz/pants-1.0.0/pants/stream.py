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
Streaming (TCP) connection implementation.

Streams are one of the two main types of channels in Pants - the other
being :mod:`servers <pants.server>`. Streams represent connections
between two endpoints. They may be used for both client and server
applications.

Streams
=======
To write a Pants application you will first need to subclass
:class:`~pants.stream.Stream`. Your :class:`~pants.stream.Stream`
subclass will contain the majority of your networking code in the form
of event handlers. Event handlers are methods beginning with ``on_`` and
can be safely overridden by your subclass.

Connecting
----------
Before a :class:`~pants.stream.Stream` instance can be used, it must
first be connected to a remote host. If you are writing a server
application, all new :class:`~pants.stream.Stream` instance created by
your :class:`~pants.server.Server` will be connected. Once they are
created by the :class:`~pants.server.Server`,
:meth:`~pants.stream.Stream.on_connect` will be called and your
:class:`~pants.engine.Engine` will begin dispatching events to your
:class:`~pants.stream.Stream` instance.

If you are writing a client application, you must first instantiate your
:class:`~pants.stream.Stream` subclass and then use the
:meth:`~pants.stream.Stream.connect` method to connect the channel to a
remote host. Once the connection has been successfully established, the
:meth:`~pants.stream.Stream.on_connect` event handler will be called and
your :class:`~pants.stream.Stream` instance will start receiving events.
Bear in mind that the connection will not be established until the
:class:`~pants.engine.Engine` is running. As such, a common pattern when
writing client applications with Pants is to call
:meth:`~pants.stream.Stream.connect`, start the engine and then put all
other initialization code in :meth:`~pants.stream.Stream.on_connect`.

Writing Data
------------
Once your :class:`~pants.stream.Stream` instance is connected to a
remote host, you can begin to write data to the channel. Use
:meth:`~pants.stream.Stream.write` to write string data to the channel,
:meth:`~pants.stream.Stream.write_file` to efficiently write data from
an open file and :meth:`~pants.stream.Stream.write_packed` to write
packed binary data. As you call these methods, Pants internally buffers
your outgoing data. Once the buffer is completely empty,
:meth:`~pants.stream.Stream.on_write` will be called. Be aware that if
you continuously write data to your :class:`~pants.stream.Stream` that
:meth:`~pants.stream.Stream.on_write` may not be called very frequently.
If you wish to bypass the internal buffering and attempt to write your
data immediately you can use the ``flush`` options present in the three
write methods or call the :meth:`~pants.stream.Stream.flush` method
yourself. This can help to improve your application's responsiveness but
calling it excessively can reduce overall performance. Generally
speaking, it is useful when you know with certainty that you have
finished writing one discrete chunk of data (i.e. an HTTP response).

Reading Data
------------
A connected :class:`~pants.stream.Stream` instance will automatically
receive all incoming data from the remote host. By default, all incoming
data is immediately passed to the :meth:`~pants.stream.Stream.on_read`
event handler for your code to process. The
:attr:`~pants.stream.Stream.read_delimiter` attribute can be used to
control this behaviour by causing Pants to buffer incoming data
internally, only forwarding it to :meth:`~pants.stream.Stream.on_read`
when a particular condition is met. If the condition is never met, the
internal buffer will eventually exceed the allowed
:attr:`~pants.stream.Stream.buffer_size` and the
:meth:`~pants.stream.Stream.on_overflow_error` handler method will be
called. :attr:`~pants.stream.Stream.read_delimiter` is extremely
powerful when used effectively.

Closing
-------
To close a :class:`~pants.stream.Stream` instance, simply call the
:meth:`~pants.stream.Stream.close` method. Once a stream has been closed
it should not be reused.

Handling Errors
---------------
Despite best efforts, errors will occasionally occur in asynchronous
code. Pants handles these errors by passing the resulting exception
object to one of a number of error handler methods. They are:
:meth:`~pants.stream.Stream.on_connect_error`,
:meth:`~pants.stream.Stream.on_overflow_error` and
:meth:`~pants.stream.Stream.on_error`. Additionally, 
:meth:`~pants.stream.Stream.on_ssl_handshake_error` and
:meth:`~pants.stream.Stream.on_ssl_error` exist to handle SSL-specific
errors.

SSL
===
Pants streams have SSL support. If you are writing a server application,
use :meth:`Server.startSSL <pants.server.Server.startSSL>` to enable SSL
on your server. Each :class:`~pants.stream.Stream` created by your
server from that point forward will be SSL-enabled. If you are writing a
client application, call
:meth:`Stream.startSSL <pants.stream.Stream.startSSL>` before calling
:meth:`~pants.stream.Stream.connect`. Alternatively, you can pass a
dictionary of SSL options to the :class:`~pants.stream.Stream`
constructor which will then enable SSL on the instance. When SSL is
enabled on a :class:`~pants.stream.Stream`, an SSL handshake occurs
between the local and remote ends of the connection. Once the SSL
handshake is complete, :meth:`~pants.stream.Stream.on_ssl_handshake`
will be called. If it fails,
:meth:`~pants.stream.Stream.on_ssl_handshake_error` will be called.

If you are writing an SSL-enabled application you should read the
entirety of Python's :mod:`ssl` documentation. Pants does not override
any of Python's SSL defaults unless clearly stated in this documentation.
"""

###############################################################################
# Imports
###############################################################################

import errno
import functools
import os
import re
import socket
import ssl
import struct

from pants._channel import _Channel, HAS_IPV6, sock_type
from pants.engine import Engine


try:
    from netstruct import NetStruct as _NetStruct
except ImportError:
    # Create the fake class because isinstance expects a class.
    class _NetStruct(object):
        def __init__(self, *a, **kw):
            raise NotImplementedError


###############################################################################
# Constants
###############################################################################

RegexType = type(re.compile(""))
Struct = struct.Struct


###############################################################################
# Logging
###############################################################################

import logging
log = logging.getLogger("pants")


###############################################################################
# Stream Class
###############################################################################

class Stream(_Channel):
    """
    The stream-oriented connection channel.

    A :class:`~pants.stream.Stream` instance represents either a local
    connection to a remote server or a remote connection to a local
    server over a streaming, connection-oriented protocol such as TCP.

    =================  ================================================
    Keyword Argument   Description
    =================  ================================================
    engine             *Optional.* The engine to which the channel
                       should be added. Defaults to the global engine.
    socket             *Optional.* A pre-existing socket to wrap. This
                       can be a regular :py:obj:`~socket.socket` or an
                       :py:obj:`~ssl.SSLSocket`. If a socket is not
                       provided, a new socket will be created for the
                       channel when required.
    ssl_options        *Optional.* If provided,
                       :meth:`~pants.stream.Stream.startSSL` will be
                       called with these options once the stream is
                       ready. By default, SSL will not be enabled.
    =================  ================================================
    """
    SEND_STRING = 0
    SEND_FILE = 1
    SEND_SSL_HANDSHAKE = 2

    def __init__(self, **kwargs):
        sock = kwargs.get("socket", None)
        if sock and sock_type(sock) != socket.SOCK_STREAM:
            raise TypeError("Cannot create a %s with a socket type other than SOCK_STREAM."
                    % self.__class__.__name__)

        _Channel.__init__(self, **kwargs)

        # Socket
        self._remote_address = None
        self._local_address = None

        # I/O attributes
        self._read_delimiter = None
        self._recv_buffer = ""
        self._recv_buffer_size_limit = self._buffer_size
        self._send_buffer = []

        # Channel state
        self.connected = False
        self.connecting = False
        self._closing = False

        # SSL state
        self.ssl_enabled = False
        self._ssl_enabling = False
        self._ssl_socket_wrapped = False
        self._ssl_handshake_done = False
        self._ssl_call_on_connect = False
        if isinstance(kwargs.get("socket", None), ssl.SSLSocket):
            self._ssl_socket_wrapped = True
            self.startSSL()
        elif kwargs.get("ssl_options", None) is not None:
            self.startSSL(kwargs["ssl_options"])

    ##### Properties ##########################################################

    @property
    def remote_address(self):
        """
        The remote address to which the channel is connected.

        By default, this will be the value of ``socket.getpeername`` or
        None. It is possible for user code to override the default
        behaviour and set the value of the property manually. In order
        to return the property to its default behaviour, user code then
        has to delete the value. Example::

            # default behaviour
            channel.remote_address = custom_value
            # channel.remote_address will return custom_value now
            del channel.remote_address
            # default behaviour
        """
        if self._remote_address is not None:
            return self._remote_address
        elif self._socket:
            try:
                return self._socket.getpeername()
            except socket.error:
                return None
        else:
            return None

    @remote_address.setter
    def remote_address(self, val):
        self._remote_address = val

    @remote_address.deleter
    def remote_address(self):
        self._remote_address = None

    @property
    def local_address(self):
        """
        The address of the channel on the local machine.

        By default, this will be the value of ``socket.getsockname`` or
        None. It is possible for user code to override the default
        behaviour and set the value of the property manually. In order
        to return the property to its default behaviour, user code then
        has to delete the value. Example::

            # default behaviour
            channel.local_address = custom_value
            # channel.local_address will return custom_value now
            del channel.local_address
            # default behaviour
        """
        if self._local_address is not None:
            return self._local_address
        elif self._socket:
            try:
                return self._socket.getsockname()
            except socket.error:
                return None
        else:
            return None

    @local_address.setter
    def local_address(self, val):
        self._local_address = val

    @local_address.deleter
    def local_address(self):
        self._local_address = None

    @property
    def read_delimiter(self):
        """
        The magical read delimiter which determines how incoming data is
        buffered by the stream.

        As data is read from the socket, it is buffered internally by
        the stream before being passed to the :meth:`on_read` callback. The
        value of the read delimiter determines when the data is passed to the
        callback. Valid values are ``None``, a byte string, an integer/long,
        a compiled regular expression, an instance of :class:`struct.Struct`,
        or an instance of :class:`netstruct.NetStruct`.

        When the read delimiter is ``None``, data will be passed to
        :meth:`on_read` immediately after it is read from the socket. This is
        the default behaviour.

        When the read delimiter is a byte string, data will be buffered
        internally until that string is encountered in the incoming
        data. All data up to but excluding the read delimiter is then
        passed to :meth:`on_read`. The segment matching the read delimiter
        itself is discarded from the buffer.

        When the read delimiter is an integer or a long, it is treated
        as the number of bytes to read before passing the data to
        :meth:`on_read`.

        When the read delimiter is a :class:`struct.Struct` instance, the
        Struct's ``size`` is fully buffered and the data is unpacked using the
        Struct before its sent to :meth:`on_read`. Unlike other types of read
        delimiters, this can result in more than one argument being passed to
        :meth:`on_read`, as in the following example::

            import struct
            from pants import Stream

            class Example(Stream):
                def on_connect(self):
                    self.read_delimiter = struct.Struct("!LLH")

                def on_read(self, packet_type, length, id):
                    pass

        When the read delimiter is an instance of :class:`netstruct.NetStruct`,
        the NetStruct's :attr:`~netstruct.NetStruct.minimum_size` is buffered
        and unpacked with the NetStruct, and additional data is buffered as
        necessary until the NetStruct can be completely unpacked. Once ready,
        the data will be passed to :meth:`on_read`. Using Struct and NetStruct
        are *very* similar.

        When the read delimiter is a compiled regular expression
        (:class:`re.RegexObject`), there are two possible behaviors that you
        may switch between by setting the value of :attr:`regex_search`. If
        :attr:`regex_search` is True, as is the default, the delimiter's
        :meth:`~re.RegexObject.search` method is used and, if a match is found,
        the string before that match is passed to :meth:`on_read`. The segment
        that was matched by the regular expression will be discarded.

        If :attr:`regex_search` is False, the delimiter's
        :meth:`~re.RegexObject.match` method is used instead and, if a match
        is found, the match object itself will be passed to :meth:`on_read`,
        giving you access to the capture groups. Again, the segment that was
        matched by the regular expression will be discarded from the buffer.

        Attempting to set the read delimiter to any other value will
        raise a :exc:`TypeError`.

        The effective use of the read delimiter can greatly simplify the
        implementation of certain protocols.
        """
        return self._read_delimiter

    @read_delimiter.setter
    def read_delimiter(self, value):
        if value is None or isinstance(value, basestring) or \
                isinstance(value, RegexType):
            self._read_delimiter = value
            self._recv_buffer_size_limit = self._buffer_size

        elif isinstance(value, (int, long)):
            self._read_delimiter = value
            self._recv_buffer_size_limit = max(self._buffer_size, value)

        elif isinstance(value, Struct):
            self._read_delimiter = value
            self._recv_buffer_size_limit = max(self._buffer_size, value.size)

        elif isinstance(value, _NetStruct):
            self._read_delimiter = value
            self._recv_buffer_size_limit = max(self._buffer_size,
                                               value.minimum_size)

        else:
            raise TypeError("Attempted to set read_delimiter to a value with an invalid type.")

        # Reset NetStruct state when we change the read delimiter.
        self._netstruct_iter = None
        self._netstruct_needed = None

    # Setting these at the class level makes them easy to override on a
    # per-class basis.
    regex_search = True
    _buffer_size = 2 ** 16  # 64kb

    @property
    def buffer_size(self):
        """
        The maximum size, in bytes, of the internal buffer used for
        incoming data.

        When buffering data it is important to ensure that inordinate
        amounts of memory are not used. Setting the buffer size to a
        sensible value can prevent coding errors or malicious use from
        causing your application to consume increasingly large amounts
        of memory. By default, a maximum of 64kb of data will be stored.

        The buffer size is mainly relevant when using a string value for
        the :attr:`~pants.stream.Stream.read_delimiter`. Because you
        cannot guarantee that the string will appear, having an upper
        limit on the size of the data is appropriate.

        If the read delimiter is set to a number larger than the buffer
        size, the buffer size will be increased to accommodate the read
        delimiter.

        When the internal buffer's size exceeds the maximum allowed, the
        :meth:`~pants.stream.Stream.on_overflow_error` callback will be
        invoked.

        Attempting to set the buffer size to anything other than an
        integer or long will raise a :exc:`TypeError`.
        """
        return self._buffer_size

    @buffer_size.setter
    def buffer_size(self, value):
        if not isinstance(value, (long, int)):
            raise TypeError("buffer_size must be an int or a long")
        self._buffer_size = value
        if isinstance(self._read_delimiter, (int, long)):
            self._recv_buffer_size_limit = max(value, self._read_delimiter)
        elif isinstance(self._read_delimiter, Struct):
            self._recv_buffer_size_limit = max(value,
                                               self._read_delimiter.size)
        elif isinstance(self._read_delimiter, _NetStruct):
            self._recv_buffer_size_limit = max(value,
                                            self._read_delimiter.minimum_size)
        else:
            self._recv_buffer_size_limit = value

    ##### Control Methods #####################################################

    def startSSL(self, ssl_options={}):
        """
        Enable SSL on the channel and perform a handshake at the next
        opportunity.

        SSL is only enabled on a channel once all currently pending data
        has been written. If a problem occurs at this stage,
        :meth:`~pants.stream.Stream.on_ssl_error` is called. Once SSL
        has been enabled, the SSL handshake begins - this typically
        takes some time and may fail, in which case
        :meth:`~pants.stream.Stream.on_ssl_handshake_error` will be
        called. When the handshake is successfully completed,
        :meth:`~pants.stream.Stream.on_ssl_handshake` is called and the
        channel is secure.

        Typically, this method is called before
        :meth:`~pants.stream.Stream.connect`. In this case,
        :meth:`~pants.stream.Stream.on_ssl_handshake` will be called
        before :meth:`~pants.stream.Stream.on_connect`. If
        :meth:`~pants.stream.Stream.startSSL` is called after
        :meth:`~pants.stream.Stream.connect`, the reverse is true.

        It is possible, although unusual, to start SSL on a channel that
        is already connected and active. In this case, as noted above,
        SSL will only be enabled and the handshake performed after all
        currently pending data has been written.

        The SSL options argument will be passed through to
        :func:`ssl.wrap_socket` as keyword arguments - see the
        :mod:`ssl` documentation for further information. You will
        typically want to provide the ``keyfile``, ``certfile`` and
        ``ca_certs`` options. The ``do_handshake_on_connect`` option
        **must** be ``False``, or a :exc:`ValueError` will be raised.

        Attempting to enable SSL on a closed channel or a channel that
        already has SSL enabled on it will raise a :exc:`RuntimeError`.

        Returns the channel.

        ============ ===================================================
        Arguments    Description
        ============ ===================================================
        ssl_options  *Optional.* Keyword arguments to pass to
                     :func:`ssl.wrap_socket`.
        ============ ===================================================
        """
        if self.ssl_enabled or self._ssl_enabling:
            raise RuntimeError("startSSL() called on SSL-enabled %r" % self)

        if self._closed or self._closing:
            raise RuntimeError("startSSL() called on closed %r" % self)

        if ssl_options.setdefault("do_handshake_on_connect", False) is not False:
            raise ValueError("SSL option 'do_handshake_on_connect' must be False.")

        self._ssl_enabling = True
        self._send_buffer.append((Stream.SEND_SSL_HANDSHAKE, ssl_options))

        if self.connected:
            self._process_send_buffer()

        return self

    def connect(self, address):
        """
        Connect the channel to a remote socket.

        The given ``address`` is resolved and used by the channel to
        connect to the remote server. If an error occurs at any stage in
        this process, :meth:`~pants.stream.Stream.on_connect_error` is
        called. When a connection is successfully established,
        :meth:`~pants.stream.Stream.on_connect` is called.

        Addresses can be represented in a number of different ways. A
        single string is treated as a UNIX address. A single integer is
        treated as a port and converted to a 2-tuple of the form
        ``('', port)``. A 2-tuple is treated as an IPv4 address and a
        4-tuple is treated as an IPv6 address. See the :mod:`socket`
        documentation for further information on socket addresses.

        If no socket exists on the channel, one will be created with a
        socket family appropriate for the given address.

        An error will occur during the connection if the given address
        is not of a valid format or of an inappropriate format for the
        socket (e.g. if an IP address is given to a UNIX socket).

        Calling :meth:`connect()` on a closed channel or a channel that
        is already connected will raise a :exc:`RuntimeError`.

        Returns the channel.

        ===============  ===============================================
        Arguments        Description
        ===============  ===============================================
        address          The remote address to connect to.
        ===============  ===============================================
        """
        if self.connected or self.connecting:
            raise RuntimeError("connect() called on active %r." % self)

        if self._closed or self._closing:
            raise RuntimeError("connect() called on closed %r." % self)

        self.connecting = True

        address, family, resolved = self._format_address(address)

        if resolved:
            self._do_connect(address, family)
        else:
            try:
                result = socket.getaddrinfo(address[0], address[1], family)
            except socket.error as err:
                self.close(flush=False)
                e = StreamConnectError(err.errno, err.strerror)
                self._safely_call(self.on_connect_error, e)
                return self

            # We only care about the first result.
            result = result[0]
            self._do_connect(result[-1], result[0])

        return self

    def close(self, flush=True):
        """
        Close the channel.
        """
        if self._closed:
            return

        if flush and self._send_buffer:
            self._closing = True
            return

        self.read_delimiter = None
        self._recv_buffer = ""
        self._send_buffer = []

        self.connected = False
        self.connecting = False

        self.ssl_enabled = False
        self._ssl_enabling = False
        self._ssl_socket_wrapped = False
        self._ssl_handshake_done = False
        self._ssl_call_on_connect = False

        self._safely_call(self.on_close)

        self._remote_address = None
        self._local_address = None

        _Channel.close(self)

        self._closing = False

    ##### I/O Methods #########################################################

    def write(self, data, flush=False):
        """
        Write data to the channel.

        Data will not be written immediately, but will be buffered
        internally until it can be sent without blocking the process.

        Calling :meth:`write()` on a closed or disconnected channel will
        raise a :exc:`RuntimeError`.

        ==========  ===================================================
        Arguments   Description
        ==========  ===================================================
        data        A string of data to write to the channel.
        flush       *Optional.* If True, flush the internal write
                    buffer. See :meth:`~pants.stream.Stream.flush` for
                    details.
        ==========  ===================================================
        """
        if self._closed or self._closing:
            raise RuntimeError("write() called on closed %r." % self)

        if not self.connected:
            raise RuntimeError("write() called on disconnected %r." % self)

        if self._send_buffer and self._send_buffer[-1][0] == Stream.SEND_STRING:
            data_type, existing_data = self._send_buffer.pop(-1)
            data = existing_data + data

        self._send_buffer.append((Stream.SEND_STRING, data))

        if flush:
            self._process_send_buffer()
        else:
            self._start_waiting_for_write_event()

    def write_file(self, sfile, nbytes=0, offset=0, flush=False):
        """
        Write a file to the channel.

        The file will not be written immediately, but will be buffered
        internally until it can be sent without blocking the process.

        Calling :meth:`write_file()` on a closed or disconnected channel
        will raise a :exc:`RuntimeError`.

        ==========  ====================================================
        Arguments   Description
        ==========  ====================================================
        sfile       A file object to write to the channel.
        nbytes      *Optional.* The number of bytes of the file to
                    write. If 0, all bytes will be written.
        offset      *Optional.* The number of bytes to offset writing
                    by.
        flush       *Optional.* If True, flush the internal write
                    buffer. See :meth:`~pants.stream.Stream.flush` for
                    details.
        ==========  ====================================================
        """
        if self._closed or self._closing:
            raise RuntimeError("write_file() called on closed %r." % self)

        if not self.connected:
            raise RuntimeError("write_file() called on disconnected %r." % self)

        self._send_buffer.append((Stream.SEND_FILE, (sfile, offset, nbytes)))

        if flush:
            self._process_send_buffer()
        else:
            self._start_waiting_for_write_event()

    def write_packed(self, *data, **kwargs):
        """
        Write packed binary data to the channel.

        If the current :attr:`read_delimiter` is an instance of
        :class:`struct.Struct` or :class:`netstruct.NetStruct` the format will
        be read from that Struct, otherwise you will need to
        provide a ``format``.

        ==========  ====================================================
        Argument    Description
        ==========  ====================================================
        \*data      Any number of values to be passed through
                    :mod:`struct` and written to the remote host.
        flush       *Optional.* If True, flush the internal write
                    buffer. See :meth:`~pants.stream.Stream.flush`
                    for details.
        format      *Optional.* A formatting string to pack the
                    provided data with. If one isn't provided, the read
                    delimiter will be used.
        ==========  ====================================================
        """
        format = kwargs.get("format")
        if format:
            self.write(struct.pack(format, *data), kwargs.get("flush", False))
        elif not isinstance(self._read_delimiter, (Struct, _NetStruct)):
            raise ValueError("No format is available for writing packed data.")
        else:
            self.write(self._read_delimiter.pack(*data),
                       kwargs.get("flush", False))

    def flush(self):
        """
        Attempt to immediately write any internally buffered data to the
        channel without waiting for a write event.

        This method can be fairly expensive to call and should be used
        sparingly.

        Calling :meth:`flush()` on a closed or disconnected channel will
        raise a :exc:`RuntimeError`.
        """
        if self._closed or self._closing:
            raise RuntimeError("flush() called on closed %r." % self)

        if not self.connected:
            raise RuntimeError("flush() called on disconnected %r." % self)

        if not self._send_buffer:
            return

        self._stop_waiting_for_write_event()
        self._process_send_buffer()

    ##### Public Event Handlers ###############################################

    def on_ssl_handshake(self):
        """
        Placeholder. Called after the channel has finished its SSL
        handshake.
        """
        pass

    ##### Public Error Handlers ###############################################

    def on_ssl_handshake_error(self, exception):
        """
        Placeholder. Called when an error occurs during the SSL
        handshake.

        By default, logs the exception and closes the channel.

        ==========  ============
        Argument    Description
        ==========  ============
        exception   The exception that was raised.
        ==========  ============
        """
        log.exception(exception)
        self.close(flush=False)

    def on_ssl_error(self, exception):
        """
        Placeholder. Called when an error occurs in the underlying SSL
        implementation.

        By default, logs the exception and closes the channel.

        ==========  ============
        Argument    Description
        ==========  ============
        exception   The exception that was raised.
        ==========  ============
        """
        log.exception(exception)
        self.close(flush=False)

    ##### Internal Methods ####################################################

    def _do_connect(self, address, family, error=None):
        """
        A callback method to be used with
        :meth:`~pants._channel._Channel._resolve_addr` - either connects
        immediately or notifies the user of an error.

        =========  =====================================================
        Argument   Description
        =========  =====================================================
        address    The address to connect to or None if address
                   resolution failed.
        family     The detected socket family or None if address
                   resolution failed.
        error      *Optional.* Error information or None if no error
                   occurred.
        =========  =====================================================
        """
        if not address:
            self.connecting = False
            e = StreamConnectError(*error)
            self._safely_call(self.on_connect_error, e)
            return

        if self._socket:
            if self._socket.family != family:
                self.engine.remove_channel(self)
                self._socket_close()
                self._closed = False

        sock = socket.socket(family, socket.SOCK_STREAM)
        self._socket_set(sock)
        self.engine.add_channel(self)

        try:
            connected = self._socket_connect(address)
        except socket.error as err:
            self.close(flush=False)
            e = StreamConnectError(err.errno, err.strerror)
            self._safely_call(self.on_connect_error, e)
            return

        if connected:
            self._handle_connect_event()

    ##### Internal Event Handler Methods ######################################

    def _handle_read_event(self):
        """
        Handle a read event raised on the channel.
        """
        if self.ssl_enabled and not self._ssl_handshake_done:
            self._ssl_do_handshake()
            return

        while True:
            try:
                data = self._socket_recv()
            except socket.error as err:
                self._safely_call(self.on_read_error, err)
                return

            if not data:
                break
            else:
                self._recv_buffer += data

                if len(self._recv_buffer) > self._recv_buffer_size_limit:
                    # Try processing the buffer to reduce its length.
                    self._process_recv_buffer()

                    # If the buffer's still too long, overflow error.
                    if len(self._recv_buffer) > self._recv_buffer_size_limit:
                        e = StreamBufferOverflow("Buffer length exceeded upper limit on %r." % self)
                        self._safely_call(self.on_overflow_error, e)
                        return

        self._process_recv_buffer()

        # This block was moved out of the above loop to address issue #41.
        if data is None:
            self.close(flush=False)

    def _handle_write_event(self):
        """
        Handle a write event raised on the channel.
        """
        if self.ssl_enabled and not self._ssl_handshake_done:
            self._ssl_do_handshake()
            return

        if not self.connected:
            self._handle_connect_event()

        if not self._send_buffer:
            return

        self._process_send_buffer()

    def _handle_error_event(self):
        """
        Handle an error event raised on the channel.
        """
        if self.connecting:
            # That's no moon...
            self._handle_connect_event()
        else:
            _Channel._handle_error_event(self)

    def _handle_connect_event(self):
        """
        Handle a connect event raised on the channel.
        """
        self.connecting = False
        err, errstr = self._get_socket_error()
        if err == 0:
            self.connected = True
            if self._ssl_enabling:
                self._ssl_call_on_connect = True
                self._process_send_buffer()
            else:
                self._safely_call(self.on_connect)
        else:
            # ... it's a space station!
            e = StreamConnectError(err, errstr)
            self._safely_call(self.on_connect_error, e)

    ##### Internal Processing Methods #########################################

    def _process_recv_buffer(self):
        """
        Process the :attr:`~pants.stream.Stream._recv_buffer`, passing
        chunks of data to :meth:`~pants.stream.Stream.on_read`.
        """
        while self._recv_buffer:
            delimiter = self.read_delimiter

            if delimiter is None:
                data = self._recv_buffer
                self._recv_buffer = ""
                self._safely_call(self.on_read, data)

            elif isinstance(delimiter, (int, long)):
                if len(self._recv_buffer) < delimiter:
                    break
                data = self._recv_buffer[:delimiter]
                self._recv_buffer = self._recv_buffer[delimiter:]
                self._safely_call(self.on_read, data)

            elif isinstance(delimiter, basestring):
                mark = self._recv_buffer.find(delimiter)
                if mark == -1:
                    break
                data = self._recv_buffer[:mark]
                self._recv_buffer = self._recv_buffer[mark + len(delimiter):]
                self._safely_call(self.on_read, data)

            elif isinstance(delimiter, Struct):
                if len(self._recv_buffer) < delimiter.size:
                    break
                data = self._recv_buffer[:delimiter.size]
                self._recv_buffer = self._recv_buffer[delimiter.size:]

                # Safely unpack it. This should *probably* never error.
                try:
                    data = delimiter.unpack(data)
                except struct.error:
                    log.exception("Unable to unpack data on %r." % self)
                    self.close()
                    break

                # Unlike most on_read calls, this one sends every variable of
                # the parsed data as its own argument.
                self._safely_call(self.on_read, *data)

            elif isinstance(delimiter, _NetStruct):
                if not self._netstruct_iter:
                    # We need to get started.
                    self._netstruct_iter = delimiter.iter_unpack()
                    self._netstruct_needed = next(self._netstruct_iter)

                if len(self._recv_buffer) < self._netstruct_needed:
                    break

                data = self._netstruct_iter.send(
                    self._recv_buffer[:self._netstruct_needed])
                self._recv_buffer = self._recv_buffer[self._netstruct_needed:]

                if isinstance(data, (int,long)):
                    self._netstruct_needed = data
                    continue

                # Still here? Then we've got our object. Delete the NetStruct
                # state and send the data.
                self._netstruct_needed = None
                self._netstruct_iter = None

                self._safely_call(self.on_read, *data)

            elif isinstance(delimiter, RegexType):
                # Depending on regex_search, we could do this two ways.
                if self.regex_search:
                    match = delimiter.search(self._recv_buffer)
                    if not match:
                        break

                    data = self._recv_buffer[:match.start()]
                    self._recv_buffer = self._recv_buffer[match.end():]

                else:
                    # Require the match to be at the beginning.
                    data = delimiter.match(self._recv_buffer)
                    if not data:
                        break

                    self._recv_buffer = self._recv_buffer[data.end():]

                # Send either the string or the match object.
                self._safely_call(self.on_read, data)

            else:
                # The safeguards in the read delimiter property should
                # prevent this from happening unless people start
                # getting too crafty for their own good.
                err = InvalidReadDelimiterError("Invalid read delimiter on %r." % self)
                self._safely_call(self.on_error, err)
                break

            if self._closed or not self.connected:
                break

    def _process_send_buffer(self):
        """
        Process the :attr:`~pants.stream.Stream._send_buffer`, passing
        outgoing data to :meth:`~pants._channel._Channel._socket_send`
        or :meth:`~pants._channel._Channel._socket_sendfile` and calling
        :meth:`~pants.stream.Stream.on_write` when sending has finished.
        """
        while self._send_buffer:
            data_type, data = self._send_buffer.pop(0)

            if data_type == Stream.SEND_STRING:
                bytes_sent = self._process_send_string(data)
            elif data_type == Stream.SEND_FILE:
                bytes_sent = self._process_send_file(*data)
            elif data_type == Stream.SEND_SSL_HANDSHAKE:
                bytes_sent = self._process_send_ssl_handshake(data)

            if bytes_sent == 0:
                break

        if not self._closed and not self._send_buffer:
            self._safely_call(self.on_write)

            if self._closing:
                self.close(flush=False)

    def _process_send_string(self, data):
        """
        Send data from a string to the remote socket.
        """
        try:
            bytes_sent = self._socket_send(data)
        except socket.error as err:
            self._safely_call(self.on_write_error, err)
            return 0

        if len(data) > bytes_sent:
            self._send_buffer.insert(0, (Stream.SEND_STRING, data[bytes_sent:]))

        return bytes_sent

    def _process_send_file(self, sfile, offset, nbytes):
        """
        Send data from a file to the remote socket.
        """
        try:
            bytes_sent = self._socket_sendfile(sfile, offset, nbytes)
        except socket.error as err:
            self._safely_call(self.on_write_error, err)
            return 0

        offset += bytes_sent

        if nbytes > 0:
            if nbytes - bytes_sent > 0:
                nbytes -= bytes_sent
            else:
                # Reached the end of the segment.
                return bytes_sent

        # TODO This is awful. Find a better way.
        if os.fstat(sfile.fileno()).st_size - offset <= 0:
            # Reached the end of the file.
            return bytes_sent

        self._send_buffer.insert(0, (Stream.SEND_FILE, (sfile, offset, nbytes)))

        return bytes_sent

    def _process_send_ssl_handshake(self, ssl_options):
        """
        Enable SSL and begin the handshake.
        """
        self._ssl_enabling = False

        if not self._ssl_socket_wrapped:
            try:
                self._socket = ssl.wrap_socket(self._socket, **ssl_options)
            except ssl.SSLError as err:
                self._ssl_enabling = True
                self._safely_call(self.on_ssl_error, err)
                return 0
            else:
                self._ssl_socket_wrapped = True

        self.ssl_enabled = True

        try:
            bytes_sent = self._ssl_do_handshake()
        except Exception as err:
            self._safely_call(self.on_ssl_handshake_error, err)
            return 0

        # Unlike strings and files, the SSL handshake is not re-added to
        # the queue. This is because the stream's state has been
        # modified and the handshake will continue until it's complete.
        return bytes_sent

    ##### SSL Implementation ##################################################

    def _socket_recv(self):
        """
        Receive data from the socket.

        Returns a string of data read from the socket. The data is None if
        the socket has been closed.

        Overrides :meth:`pants._channel._Channel._socket_recv` to handle
        SSL-specific behaviour.
        """
        try:
            return _Channel._socket_recv(self)
        except ssl.SSLError as err:
            if err.args[0] == ssl.SSL_ERROR_WANT_READ:
                return ''
            else:
                raise

    def _socket_send(self, data):
        """
        Send data to the socket.

        Returns the number of bytes that were sent to the socket.

        Overrides :meth:`pants._channel._Channel._socket_send` to handle
        SSL-specific behaviour.

        =========  ============
        Argument   Description
        =========  ============
        data       The string of data to send.
        =========  ============
        """
        try:
            bytes_sent = _Channel._socket_send(self, data)
        except ssl.SSLError as err:
            if err.args[0] == ssl.SSL_ERROR_WANT_WRITE:
                self._start_waiting_for_write_event()
                return 0
            else:
                raise

        # SSLSocket.send() can return 0 rather than raise an exception
        # if it needs a write event.
        if self.ssl_enabled and bytes_sent == 0:
            self._start_waiting_for_write_event()
        return bytes_sent

    def _socket_sendfile(self, sfile, offset, nbytes):
        """
        Send data from a file to a remote socket.

        Returns the number of bytes that were sent to the socket.

        Overrides :meth:`pants._channel._Channel._socket_sendfile` to
        handle SSL-specific behaviour.

        =========  ============
        Argument   Description
        =========  ============
        sfile      The file to send.
        offset     The number of bytes to offset writing by.
        nbytes     The number of bytes of the file to write. If 0, all bytes will be written.
        =========  ============
        """
        return _Channel._socket_sendfile(self, sfile, offset, nbytes, self.ssl_enabled)

    def _ssl_do_handshake(self):
        """
        Perform an asynchronous SSL handshake.
        """
        try:
            self._socket.do_handshake()
        except ssl.SSLError as err:
            if err.args[0] == ssl.SSL_ERROR_WANT_READ:
                return 0
            elif err.args[0] == ssl.SSL_ERROR_WANT_WRITE:
                self._start_waiting_for_write_event()
                return 0
            elif err.args[0] in (ssl.SSL_ERROR_EOF, ssl.SSL_ERROR_ZERO_RETURN):
                self.close(flush=False)
                return 0
            elif err.args[0] == ssl.SSL_ERROR_SSL:
                self._safely_call(self.on_ssl_handshake_error, err)
                return 0
            else:
                raise
        except socket.error as err:
            if err.args[0] in (errno.ECONNRESET, errno.EPIPE):
                self.close(flush=False)
                return 0
            else:
                raise
        else:
            self._ssl_handshake_done = True
            self._safely_call(self.on_ssl_handshake)
            if self._ssl_call_on_connect:
                self._safely_call(self.on_connect)
            return None


###############################################################################
# Exceptions
###############################################################################

class StreamBufferOverflow(Exception):
    """
    Raised when a stream's internal buffer has exceeded its maximum
    allowed size.
    """
    pass

class StreamConnectError(Exception):
    """
    Raised when an error has occurred during an attempt to connect a
    stream to a remote host.
    """
    pass

class InvalidReadDelimiterError(Exception):
    """
    Raised when a channel tries to process incoming data with an
    invalid read delimiter.
    """
    pass
