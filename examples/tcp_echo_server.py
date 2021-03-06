# -*- coding: utf-8 -*-
"""
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Pluggable, TLS interception capable proxy server focused on
    Network monitoring, controls & Application development, testing, debugging.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
"""
import time
import socket
import selectors

from typing import Dict

from proxy.core.acceptor import AcceptorPool, Work
from proxy.common.flags import Flags
from proxy.common.types import Readables, Writables


class EchoServerHandler(Work):
    """EchoServerHandler implements Work interface.

    An instance of EchoServerHandler is created for each client
    connection.  EchoServerHandler lifecycle is controlled by
    Threadless core using asyncio.  Implementation must provide
    get_events and handle_events method.  Optionally, also implement
    intialize, is_inactive and shutdown method.
    """

    def get_events(self) -> Dict[socket.socket, int]:
        # We always want to read from client
        # Register for EVENT_READ events
        events = {self.client.connection: selectors.EVENT_READ}
        # If there is pending buffer for client
        # also register for EVENT_WRITE events
        if self.client.has_buffer():
            events[self.client.connection] |= selectors.EVENT_WRITE
        return events

    def handle_events(
            self,
            readables: Readables,
            writables: Writables) -> bool:
        """Return True to shutdown work."""
        if self.client.connection in readables:
            data = self.client.recv()
            if data is None:
                # Client closed connection, signal shutdown
                return True
            # Queue data back to client
            self.client.queue(data)

        if self.client.connection in writables:
            self.client.flush()

        return False


def main() -> None:
    # This example requires `threadless=True`
    pool = AcceptorPool(
        flags=Flags(num_workers=1, threadless=True),
        work_klass=EchoServerHandler)
    try:
        pool.setup()
        while True:
            time.sleep(1)
    finally:
        pool.shutdown()


if __name__ == '__main__':
    main()
