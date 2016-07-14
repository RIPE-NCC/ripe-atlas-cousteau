# Copyright (c) 2015 RIPE NCC
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

    CHANNEL_RESULT = "atlas_result"
    CHANNEL_PROBE = "atlas_probestatus"
    CHANNEL_ERROR = "atlas_error"
    CHANNELS = {
        "result": CHANNEL_RESULT,
        "probe": CHANNEL_PROBE,
        "error": CHANNEL_ERROR,
    }

    def __init__(self, log_errors=True, debug=False, server=False):
        """Initialize stream"""

        self.iosocket_server = "atlas-stream.ripe.net"
        self.iosocket_resource = "/stream/socket.io"
        self.socketIO = None
        self.log_errors = log_errors
        self.error_callback = None
        self.debug = debug

        if self.debug and server:
            self.iosocket_server = server


    def report_errors(self, error):
        if self.error_callback:
            self.error_callback(error)
        elif self.log_errors:
            print(error)

    def connect(self):
        """Initiate the channel we want to start streams from."""
        self.socketIO = SocketIO(
            host=self.iosocket_server,
            port=80,
            resource=self.iosocket_resource,
            transports=["websocket"]
        )

        self.bind_channel("error", self.report_errors)

    def on_error(self, callback):
        """Explicit error handling expressed by the user."""
        self.error_callback = callback

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
        try:
            if channel == "result":
                self.socketIO.on(self.CHANNELS[channel], partial(self.unpack_results, callback))
            else:
                self.socketIO.on(self.CHANNELS[channel], callback)

        except KeyError:
            print("The given channel: <{0}> is not valid".format(channel))

    def start_stream(self, stream_type, **stream_parameters):
        """Starts new stream for given type with given parameters"""
        if stream_type:
            self.subscribe(stream_type, **stream_parameters)
        else:
            print("You need to set a stream type")

    def subscribe(self, stream_type, **parameters):
        """Subscribe to stream with give parameters."""
        parameters["stream_type"] = stream_type

        if stream_type == "result" and "buffering" not in parameters:
            parameters["buffering"] = True

        self.socketIO.emit('atlas_subscribe', parameters)

    def timeout(self, seconds=None):
        """
        Times out all streams after n seconds or wait forever if seconds is
        None
        """
        if seconds is None:
            self.socketIO.wait()
        else:
            self.socketIO.wait(seconds=seconds)
