# Copyright (c) 2023 RIPE NCC
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

from urllib.parse import urlparse
import os
from typing import Dict, Callable, List, Tuple, Any, Optional, Iterator
from typing_extensions import TypeAlias
import json
import logging
import re
import socket
import time
import warnings
import select

import requests
import websocket

from .version import __version__

LOG = logging.getLogger("atlas-stream")
LOG.addHandler(logging.NullHandler())


class AtlasStream:
    # For the current list of events see:
    # https://atlas.ripe.net/docs/result-streaming/

    # Events you can listen to
    EVENT_NAME_ERROR = "atlas_error"
    EVENT_NAME_RESULTS = "atlas_result"
    EVENT_NAME_METADATA = "atlas_metadata"
    EVENT_NAME_PROBESTATUS = "atlas_probestatus"
    EVENT_NAME_SUBSCRIBED = "atlas_subscribed"
    EVENT_NAME_UNSUBSCRIBED = "atlas_unsubscribed"

    VALID_EVENTS = (
        EVENT_NAME_ERROR,
        EVENT_NAME_RESULTS,
        EVENT_NAME_METADATA,
        EVENT_NAME_PROBESTATUS,
        EVENT_NAME_SUBSCRIBED,
        EVENT_NAME_UNSUBSCRIBED,
    )

    # Events that you can emit
    EVENT_NAME_SUBSCRIBE = "atlas_subscribe"
    EVENT_NAME_UNSUBSCRIBE = "atlas_unsubscribe"

    # atlas_subscribe stream types
    STREAM_TYPE_RESULT = "result"
    STREAM_TYPE_PROBESTATUS = "probestatus"
    STREAM_TYPE_METADATA = "metadata"

    VALID_STREAM_TYPES = (
        STREAM_TYPE_RESULT,
        STREAM_TYPE_PROBESTATUS,
        STREAM_TYPE_METADATA,
    )

    StreamParams: TypeAlias = Dict[str, Any]

    def __init__(
        self,
        base_url: str = "https://atlas-stream.ripe.net",
        path: str = "/stream/",
        headers: Optional[Dict[str, str]] = None,
        proxies: Optional[Dict[str, str]] = None,
        transport: str = "websocket",
    ) -> None:
        """Initialize stream"""
        base_url = re.sub("^http", "ws", base_url)
        path = re.sub("socket.io/?$", "", path)
        self.url = base_url.rstrip("/") + "/" + path.lstrip("/")
        self.session = requests.Session()

        if transport != "websocket":
            warnings.warn(
                "Ignoring AtlasStream transport other than 'websocket'",
                DeprecationWarning,
            )

        headers = headers or {}
        if not headers.get("User-Agent", None):
            user_agent = "RIPE ATLAS Cousteau v{0}".format(__version__)
            headers["User-Agent"] = user_agent

        self.headers = headers
        self.proxies = proxies or {}

        self.callbacks: Dict[str, Callable] = {}
        self.subscriptions: List[Dict] = []

        self.ws: Optional[websocket.WebSocket] = None

    def _get_proxy_options(self):
        """
        Get websocket-client proxy options from requests-style self.proxies dict or
        http(x)_proxy env variables if present.
        """
        scheme = "https" if self.url.startswith("wss:") else "http"

        proxy_url = self.proxies.get(scheme)
        if not proxy_url:
            for key, value in os.environ.items():
                if key.lower() == f"{scheme}_proxy":
                    proxy_url = value
                    break

        if not proxy_url:
            return {}

        parsed = urlparse(proxy_url)
        return {
            "proxy_type": parsed.scheme,
            "http_proxy_host": parsed.hostname,
            "http_proxy_port": parsed.port,
        }

    def connect(self) -> None:
        while self.ws is None:
            try:
                self.ws = websocket.create_connection(
                    self.url, header=self.headers, **self._get_proxy_options()
                )
            except socket.error as exc:
                LOG.debug(f"{exc} while connecting to RIPE Atlas Stream")
                time.sleep(1)
                continue
            msg = "Connected to RIPE Atlas Stream"
            LOG.debug(msg)
            for subscription in self.subscriptions:
                self.send(self.ws, self.EVENT_NAME_SUBSCRIBE, subscription)

    def disconnect(self) -> None:
        """Removes the channel bindings and shuts down the connection."""
        if self.ws is not None:
            self.ws.close()
            self.ws = None
        self.callbacks = {}

    def bind(self, channel: str, callback: Callable) -> None:
        """Bind given channel with the given callback"""
        if channel not in self.VALID_EVENTS:
            raise ValueError("Invalid event channel")
        self.callbacks[channel] = callback

    bind_channel = bind

    def unbind(self, channel: str):
        self.callbacks.pop(channel, None)

    def subscribe(self, stream_type: str, **parameters: Any) -> None:
        """Requests new stream for given type and parameters"""
        if stream_type not in self.VALID_STREAM_TYPES:
            raise ValueError("You need to set a valid stream type")
        parameters = dict(parameters, stream_type=stream_type)
        self.subscriptions.append(parameters)
        if self.ws:
            self.send(self.ws, self.EVENT_NAME_SUBSCRIBE, parameters)

    start_stream = subscribe

    def unsubscribe(self, stream_type: str, **parameters: Any) -> None:
        """Unsubscribe from a previous subscription"""
        parameters = dict(parameters, stream_type=stream_type)
        if parameters not in self.subscriptions:
            return
        if self.ws:
            self.send(self.ws, self.EVENT_NAME_UNSUBSCRIBE, parameters)
        self.subscriptions.remove(parameters)

    def send(self, ws: websocket.WebSocket, msg_type: str, payload: Any) -> None:
        """
        Send a message to the server.
        """
        ws.send(json.dumps([msg_type, payload]))

    def recv(self, ws: websocket.WebSocket) -> Tuple[str, Any]:
        """
        Receive a single message from the server.
        """
        msg = ws.recv()
        event_name, payload = json.loads(msg)
        return event_name, payload

    def iter(self, seconds: Optional[float] = None) -> Iterator[Tuple[str, Any]]:
        """
        Yield incoming events for `seconds` if specified, or else forever.
        """
        t0 = time.perf_counter()
        while True:
            if seconds is not None:
                elapsed = time.perf_counter() - t0
                remaining = seconds - elapsed
                if remaining < 0:
                    break
                rlist, _, _ = select.select([self.ws], [], [], remaining)
                if not rlist:
                    break
            try:
                yield self.recv(self.ws)
            except Exception as exc:
                LOG.error(f"{exc} while reading from RIPE Atlas stream")
                if isinstance(exc, websocket.WebSocketException):
                    self.connect()
                    continue
                else:
                    break

    def timeout(self, seconds: Optional[float] = None) -> None:
        """
        Process events for `seconds` if specified, or else forever, calling
        a bound callback for each event if one is defined.
        """
        for event_name, payload in self.iter(seconds=seconds):
            callback = self.callbacks.get(event_name)
            if callback:
                callback(payload)

    def __iter__(self):
        """
        Yield incoming events.

        To stop iterating after a given timeout, see the `iter()` method.
        """
        return self.iter()
