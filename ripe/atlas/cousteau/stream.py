# Copyright (c) 2016 RIPE NCC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from socketIO_client import SocketIO
from functools import partial


class AtlasStream(object):

    EVENT_NAME_RESULTS = "atlas_result"
    EVENT_NAME_SUBSCRIBE = "atlas_subscribe"
    EVENT_NAME_ERROR = "atlas_error"

    # Remove the following list when deprecation time expires
    CHANNELS = {
        "result": "atlas_result",
        "probe": "atlas_probestatus",
        "error": "atlas_error",
    }
    # -------------------------------------------------------

    def __init__(self, debug=False, server=False, proxies=None, headers=None):
        """Initialize stream"""
        self.iosocket_server = "atlas-stream.ripe.net"
        self.iosocket_resource = "/stream/socket.io"
        self.socketIO = None
        self.debug = debug
        self.error_callback = None
        self.proxies = proxies or {}
        self.headers = headers or {}

        if self.debug and server:
            self.iosocket_server = server

    def handle_error(self, error):
        if self.error_callback is not None:
            self.error_callback(error)
        else:
            print(error)

    def connect(self):
        """Initiate the channel we want to start streams from."""
        self.socketIO = SocketIO(
            host=self.iosocket_server,
            port=80,
            resource=self.iosocket_resource,
            proxies=self.proxies,
            headers=self.headers,
            transports=["websocket"]
        )

        self.socketIO.on(self.EVENT_NAME_ERROR, self.handle_error)

    def disconnect(self):
        """Exits the channel k shuts down connection."""
        self.socketIO.disconnect()
        self.socketIO.__exit__([])

    def unpack_results(self, callback, data):
        if isinstance(data, list):
            for result in data:
                callback(result)
        else:
            callback(data)

    def bind_channel(self, channel, callback):
        """Bind given channel with the given callback"""

        # Remove the following list when deprecation time expires
        if channel in self.CHANNELS:
            warning = (
                "The event name '{}' will soon be deprecated. Use "
                "the real event name '{}' instead."
            ).format(channel, self.CHANNELS[channel])

            self.handle_error(warning)
            channel = self.CHANNELS[channel]
        # -------------------------------------------------------

        if channel == self.EVENT_NAME_ERROR:
            self.error_callback = callback
        elif channel == self.EVENT_NAME_RESULTS:
            self.socketIO.on(channel, partial(self.unpack_results, callback))
        else:
            self.socketIO.on(channel, callback)

    def start_stream(self, stream_type, **stream_parameters):
        """Starts new stream for given type with given parameters"""
        if stream_type:
            self.subscribe(stream_type, **stream_parameters)
        else:
            self.handle_error("You need to set a stream type")

    def subscribe(self, stream_type, **parameters):
        """Subscribe to stream with give parameters."""
        parameters["stream_type"] = stream_type

        if (stream_type == "result") and ("buffering" not in parameters):
            parameters["buffering"] = True

        self.socketIO.emit(self.EVENT_NAME_SUBSCRIBE, parameters)

    def timeout(self, seconds=None):
        """
        Times out all streams after n seconds or wait forever if seconds is
        None
        """
        if seconds is None:
            self.socketIO.wait()
        else:
            self.socketIO.wait(seconds=seconds)
