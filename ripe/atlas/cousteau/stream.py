from socketIO_client import SocketIO


class AtlasStream(object):
    def __init__(self, **kwargs):
        """Initialize stream"""
        self.iosocket_server = "atlas-stream.ripe.net"
        self.iosocker_resource = "/stream/socket.io"
        self.result_channel = "atlas_result"
        self.probe_channel = "atlas_probestatus"
        self.result_stream_type = "result"
        self.probe_stream_type = "probestatus"

    def connect(self):
        """Initiate the channel we want to start streams from."""
        self.socketIO = SocketIO(
            host=self.iosocket_server,
            port=80,
            resource=self.iosocker_resource
        )

    def disconnect(self):
        """Exits the channel k shuts down connection."""
        self.socketIO.disconnect()
        self.socketIO.__exit__([])

    def bind_probe_stream(self, callback):
        """Bind probes stream with the given callback"""
        self.socketIO.on(self.probe_channel, callback)

    def bind_result_stream(self, callback):
        """Bind results stream with the given callback"""
        self.socketIO.on(self.result_channel, callback)

    def start_result_stream(self, **stream_parameters):
        """Starts new result stream with given parameters"""
        self.subscribe(self.result_stream_type, **stream_parameters)

    def start_probe_stream(self, **stream_parameters):
        """Starts new probe stream with given parameters"""
        self.subscribe(self.probe_stream_type, **stream_parameters)

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
