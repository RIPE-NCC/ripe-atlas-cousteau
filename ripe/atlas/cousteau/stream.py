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
import warnings
import os
import logging
from functools import partial

import requests
import socketio

from .version import __version__


from logging import NullHandler

LOG = logging.getLogger("atlas-stream")
LOG.addHandler(NullHandler())

client = socketio.Client()


class AtlasNamespace:
    """
    socket.io event handlers for handling automatic resubscription and populating
    the atlas-stream debug log.

    These are overidden by whatever the user supplies to AtlasStream.bind_channel().
    """

    SUBSCRIPTIONS = {}

    def on_connect(self, *args):
        LOG.debug("Connected to RIPE Atlas Stream")
        for subscription in self.SUBSCRIPTIONS.values():
            LOG.debug("(Re)subscribing to {}".format(subscription))
            self.emit("atlas_subscribe", subscription)

    def on_disconnect(self, *args):
        LOG.debug("Disconnected from RIPE Atlas Stream")

    def trigger_event(self, event, *args):
        handler_name = "on_" + event
        if hasattr(self, handler_name):
            return getattr(self, handler_name)(*args)
        else:
            return self.on_unbound_event(event, *args)

    def on_unbound_event(self, event, *args):
        LOG.debug(f"Received '{event}' event but no handler is set")

    def on_atlas_subscribed(self, params):
        """
        Keep track of subscriptions so that they can be resumed on reconnect.
        """
        LOG.debug("Subscribed to params: {}".format(params))
        self.SUBSCRIPTIONS[str(params)] = params

    def on_atlas_unsubscribed(self, params):
        """
        Remove this subscription from the state so we don't try to resubscribe.
        """
        LOG.debug("Unsubscribed from params: {}".format(params))
        del self.SUBSCRIPTIONS[str(params)]

    def on_atlas_error(self, *args):
        LOG.error("Got an error from stream server: {}".format(args[0]))


class AtlasClientNamespace(AtlasNamespace, socketio.ClientNamespace):
    pass


class AtlasStream(object):
    # For the current list of events see:
    # https://atlas.ripe.net/docs/result-streaming/

    # Events you can listen to
    EVENT_NAME_ERROR = "atlas_error"
    EVENT_NAME_RESULTS = "atlas_result"
    EVENT_NAME_METADATA = "atlas_metadata"
    EVENT_NAME_PROBESTATUS = "atlas_probestatus"
    EVENT_NAME_SUBSCRIBED = "atlas_subscribed"
    EVENT_NAME_UNSUBSCRIBED = "atlas_unsubscribed"
    EVENT_NAME_REPLAY_FINISHED = "atlas_replay_finished"

    # Events that you can emit
    EVENT_NAME_SUBSCRIBE = "atlas_subscribe"
    EVENT_NAME_UNSUBSCRIBE = "atlas_unsubscribe"

    # atlas_subscribe stream types
    STREAM_TYPE_RESULT = "result"
    STREAM_TYPE_PROBE = "probe"
    STREAM_TYPE_METADATA = "metadata"

    # These were deprecated long ago but were still documented before 1.5.0.
    # There isn't much overhead to having them so we can keep them for a while longer.
    DEPRECATED_CHANNELS = {
        "result": EVENT_NAME_RESULTS,
        "probe": EVENT_NAME_PROBESTATUS,
        "error": EVENT_NAME_ERROR,
    }

    Client = socketio.Client
    Namespace = AtlasClientNamespace

    def __init__(
        self,
        base_url="https://atlas-stream.ripe.net",
        path="/stream/socket.io/",
        proxies=None,
        headers=None,
        transport="websocket",
    ):
        """Initialize stream"""
        self.base_url = base_url
        self.path = path
        self.session = requests.Session()
        self.socketIO = self.Client(http_session=self.session)

        self.namespace = self.Namespace()
        self.socketIO.register_namespace(self.namespace)
        self.transport = transport

        proxies = proxies or {}
        headers = headers or {}

        if not headers or not headers.get("User-Agent", None):
            user_agent = "RIPE ATLAS Cousteau v{0}".format(__version__)
            headers["User-Agent"] = user_agent

        # Force polling if http_proxy or https_proxy point to a SOCKS URL
        for scheme in "http", "https":
            proxy = proxies.get(scheme)
            if not proxy:
                proxy = os.environ.get(f"{scheme}_proxy")
            if proxy and proxy.startswith("socks"):
                warnings.warn(
                    "SOCKS proxies do not currently work with the websocket transport, forcing polling"
                )
                self.transport = "polling"
                break

        self.session.headers.update(headers)
        self.session.proxies.update(proxies)

    def connect(self):
        """Initiate the channel we want to start streams from."""

        return self.socketIO.connect(
            self.base_url, socketio_path=self.path, transports=[self.transport]
        )

    def disconnect(self):
        """Removes the channel bindings and shuts down the connection."""
        self.socketIO.disconnect()

    def unpack_results(self, callback, data):
        if isinstance(data, list):
            for result in data:
                callback(result)
        else:
            callback(data)

    def bind_channel(self, channel, callback):
        """Bind given channel with the given callback"""
        channel = self.DEPRECATED_CHANNELS.get(channel, channel)

        if channel == self.EVENT_NAME_RESULTS:
            self.socketIO.on(channel, partial(self.unpack_results, callback))
        else:
            self.socketIO.on(channel, callback)

    def start_stream(self, stream_type, **stream_parameters):
        """Starts new stream for given type with given parameters"""
        if stream_type:
            self.subscribe(stream_type, **stream_parameters)
        else:
            self.handle_error("You need to set a stream type")

    def _get_stream_params(self, stream_type, parameters):
        parameters["stream_type"] = stream_type
        if stream_type == self.STREAM_TYPE_RESULT and "buffering" not in parameters:
            parameters["buffering"] = True
        return parameters

    def subscribe(self, stream_type, **parameters):
        """Subscribe to stream with give parameters."""
        self.socketIO.emit(
            self.EVENT_NAME_SUBSCRIBE, self._get_stream_params(stream_type, parameters)
        )

    def unsubscribe(self, stream_type, **parameters):
        """Unsubscribe from a previous subscription"""
        self.socketIO.emit(
            self.EVENT_NAME_UNSUBSCRIBE,
            self._get_stream_params(stream_type, parameters),
        )

    def timeout(self, seconds=None):
        """
        Times out all streams after n seconds or wait forever if seconds is
        None
        """
        if seconds is None:
            self.socketIO.wait()
        else:
            self.socketIO.sleep(seconds)
