# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
#
# The Initial Developer of the Original Code is the Mozilla Foundation.
# Portions created by the Initial Developer are Copyright (C) 2012
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Ben Bangert (bbangert@mozilla.com)
#
# ***** END LICENSE BLOCK *****
"""Common utilities"""
import sys

if 'gevent.monkey' in sys.modules:
    GEVENT_MONKEY = True
else:
    GEVENT_MONKEY = False

if GEVENT_MONKEY:
    from gevent import queue as Queue
else:
    import Queue  # NOQA

try:
    import simplejson as json
except:
    import json  # NOQA
