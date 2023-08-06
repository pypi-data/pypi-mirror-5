#!/usr/bin/env python
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
#   Rob Miller (rmiller@mozilla.com)
#
# ***** END LICENSE BLOCK *****
from datetime import datetime
from docopt import docopt
import json
import socket

from heka.config import client_from_dict_config, client_from_stream_config

mb_doc = """mb: HekaBench, blast messages at a Heka router.

Usage:
  mb HOST PORT [--hekacfg=<ini_file>] [--raw]

Arguments:
  HOST             Hostname or IP address of heka router to test
  PORT             Port on which heka router is listening

Options:
  --hekacfg=<ini file>        Path to heka client config file
  --raw                         Raw send of static text directly over UDP
                                instead of using heka client
"""


def mb():
    arguments = docopt(mb_doc)
    host = arguments.get('HOST')
    port = int(arguments.get('PORT'))

    DEFAULT_CONFIG = {'logger': 'mb',
                      'sender': {'class': 'heka.senders.udp.UdpSender',
                                 'args': (host, port),
                                 },
                      }

    if arguments.get('--raw'):
        udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        utcnow = datetime.utcnow()
        if utcnow.microsecond == 0:
            timestamp = "%s.000000Z" % utcnow.isoformat()
        else:
            timestamp = "%sZ" % utcnow.isoformat()
        msg = {"severity": 6, "timestamp": timestamp,
               "heka_hostname": "spire",
               "fields": {"userid": 25, "req_time": 4}, "heka_pid": 34328,
               "logger": "syncstorage", "type": "services", "payload": "foo",
               "env_version": "0.8"}
        json_msg = json.dumps(msg)
        while True:
            udpsock.sendto(json_msg, (host, port))

    if arguments.get('--hekacfg'):
        with open(arguments['--hekacfg']) as cfgfile:
            client = client_from_stream_config(cfgfile, 'heka')
    else:
        client = client_from_dict_config(DEFAULT_CONFIG)

    while True:
        client.heka('MBTEST', payload='MBTEST')
