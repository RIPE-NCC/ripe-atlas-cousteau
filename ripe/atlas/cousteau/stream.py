from socketIO_client import SocketIO


class AtlasStream(object):
    def __init__(self, **kwargs):
        """Initialize stream"""
        self.iosocket_server = "atlas-stream.ripe.net"
        self.iosocket_resource = "/stream/socket.io"
        self.result_channel = "atlas_result"
        self.probe_channel = "atlas_probestatus"
        self.result_stream_type = "result"
        self.probe_stream_type = "probestatus"

    def connect(self):
        """Initiate the channel we want to start streams from."""
        self.socketIO = SocketIO(
            host=self.iosocket_server,
            port=80,
            resource=self.iosocket_resource
        )

    def disconnect(self):
        """Exits the channel k shuts down connection."""
        self.socketIO.disconnect()
        self.socketIO.__exit__([])

    def bind_stream(self, stream_type, callback):
        """Bind given type stream with the given callback"""
        if stream_type == "result":
            self.socketIO.on(self.result_channel, callback)
        elif stream_type == "probestatus":
            self.socketIO.on(self.probe_channel, callback)
        else:
            print "Given stream type: <%s> is not valid" % stream_type

    def start_stream(self, stream_type, **stream_parameters):
        """Starts new stream for given type with given parameters"""
        if stream_type == "result":
            self.subscribe(self.result_stream_type, **stream_parameters)
        elif stream_type == "probestatus":
            self.subscribe(self.probe_stream_type, **stream_parameters)
        else:
            print "Given stream type: <%s> is not valid" % stream_type

    def subscribe(self, stream_type, **parameters):
        """Subscribe to stream with give parameters."""
        parameters.update({"stream_type": stream_type})
        self.socketIO.emit('atlas_subscribe', parameters)

    def timeout(self, seconds=None):
        "Times out all streams after X seconds or wait for ever if seconds is None"""
        if seconds is None:
            self.socketIO.wait()
        else:
            self.socketIO.wait(seconds=seconds)
