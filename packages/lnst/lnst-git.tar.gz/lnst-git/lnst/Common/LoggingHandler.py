"""
Custom logging handlers we use.

LogBuffer
Handler used solely for temporarily storing messages so that they can be
retrieved later.

Copyright 2012 Red Hat, Inc.
Licensed under the GNU General Public License, version 2 as
published by the Free Software Foundation; see COPYING for details.
"""

__autor__ = """
olichtne@redhat.com (Ondrej Lichtner)
"""

import socket, struct, pickle
import logging
import xmlrpclib
from lnst.Common.ConnectionHandler import send_data

class LogBuffer(logging.Handler):
    """
    Handler used for buffering log messages. Compared to the BufferingHandler
    defined in Python it doesn't have a capacity. It is intended to be used
    solely as a temporary storage of logged messages so that they can be later
    retrieved.
    """
    def __init__(self):
        logging.Handler.__init__(self)
        self.buffer = []

    def makePickle(self, record):
        """
        Pickles the record so that it can be sent over the xmlrpc we use.
        """
        d = dict(record.__dict__)
        d['msg'] = record.getMessage()
        d['args'] = None
        d['exc_info'] = None
        s = pickle.dumps(d, 1)
        return xmlrpclib.Binary(s)

    def add_buffer(self, buf):
        for i in buf:
            self.buffer.append(i)

    def emit(self, record):
        s = self.makePickle(record)
        self.buffer.append(s)

    def flush(self):
        self.acquire()

        buf = list(self.buffer)
        self.buffer = []

        self.release()
        return buf

    def close(self):
        self.flush()
        logging.Handler.close(self)

class TransmitHandler(logging.Handler):
    def __init__(self, target):
        logging.Handler.__init__(self)
        self.target = target

    def emit(self, record):
        r = dict(record.__dict__)
        r['msg'] = record.getMessage()
        r['args'] = None
        r['exc_info'] = None

        data = {"type": "log", "record": r}

        send_data(self.target, data)

    def close(self):
        logging.Handler.close(self)
