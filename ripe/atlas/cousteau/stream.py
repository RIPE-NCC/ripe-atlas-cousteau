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

    def __init__(self, **kwargs):
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
            print "The given stream type: <{}> is not valid".format(stream_type)

    def start_stream(self, stream_type, **stream_parameters):
        """Starts new stream for given type with given parameters"""
        if stream_type in ("result", "probestatus"):
            self.subscribe(stream_type, **stream_parameters)
        else:
            print "Given stream type: <%s> is not valid" % stream_type

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
