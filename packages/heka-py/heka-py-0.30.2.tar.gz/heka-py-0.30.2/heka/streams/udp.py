# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# The Initial Developer of the Original Code is the Mozilla Foundation.
# Portions created by the Initial Developer are Copyright (C) 2012
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Victor Ng (vng@mozilla.com)
#
# ***** END LICENSE BLOCK *****

from __future__ import absolute_import

# For UDP
from types import StringTypes
import socket


class UdpStream(object):
    """Sends heka messages out via a UDP socket."""
    def __init__(self, host, port):
        """Create UdpStream object.

        :param host: A string or sequence of strings representing the
                     hosts to which messages should be delivered.
        :param port: An integer or sequence of integers representing
                     the ports to which the messages should be
                     delivered. Will be zipped w/ the provided hosts to
                     generate host/port pairs. If there are extra
                     hosts, the last port in the sequence will be
                     repeated for each extra host. If there are extra
                     ports they will be truncated and ignored.

        """
        if isinstance(host, StringTypes):
            host = [host]
        if isinstance(port, int):
            port = [port]
        num_extra_hosts = len(host) - len(port)
        if num_extra_hosts > 0:
            port.extend(num_extra_hosts * [port[-1]])
        self._destinations = zip(host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def write(self, data):
        """Send bytes off to the heka listener(s).

        :param data: bytes to send to the listener

        """
        for host, port in self._destinations:
            self.socket.sendto(data, (host, port))

    def flush(self):
        pass
