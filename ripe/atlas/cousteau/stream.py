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


class AtlasStream(object):

    CHANNEL_RESULT = "atlas_result"
    CHANNEL_PROBE = "atlas_probe"
    CHANNEL_ERROR = "atlas_error"
    CHANNELS = {
        "result": CHANNEL_RESULT,
        "probe": CHANNEL_PROBE,
        "error": CHANNEL_ERROR,
    }

    def __init__(self):
        """Initialize stream"""

        self.iosocket_server = "atlas-stream.ripe.net"
        self.iosocket_resource = "/stream/socket.io"

        self.socketIO = None

    def connect(self):
        """Initiate the channel we want to start streams from."""
        self.socketIO = SocketIO(
            host=self.iosocket_server,
            port=80,
            resource=self.iosocket_resource,
            transports=["websocket"]
        )

    def disconnect(self):
        """Exits the channel k shuts down connection."""
        self.socketIO.disconnect()
        self.socketIO.__exit__([])

    def bind_stream(self, stream_type, callback):
        """Bind given type stream with the given callback"""
        try:
            self.socketIO.on(self.CHANNELS[stream_type], callback)
        except KeyError:
            print("The given stream type: <{0}> is not valid".format(stream_type))

    def start_stream(self, stream_type, **stream_parameters):
        """Starts new stream for given type with given parameters"""
        if stream_type in ("result", "probestatus"):
            self.subscribe(stream_type, **stream_parameters)
        else:
            print("Given stream type: <{0}> is not valid".format(stream_type))

    def subscribe(self, stream_type, **parameters):
        """Subscribe to stream with give parameters."""
        parameters.update({"stream_type": stream_type})
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
