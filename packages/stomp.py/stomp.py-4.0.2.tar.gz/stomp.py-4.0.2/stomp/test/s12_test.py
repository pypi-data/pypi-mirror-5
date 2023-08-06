import os
import signal
import time
import unittest

import stomp
from stomp import exception

from testutils import *


class Test12Connect(unittest.TestCase):

    def setUp(self):
        conn = stomp.Connection12(get_standard_host())
        listener = TestListener()
        conn.set_listener('', listener)
        conn.start()
        conn.connect('admin', 'password', wait=True)
        self.conn = conn
        self.listener = listener
        
    def tearDown(self):
        if self.conn:
            self.conn.disconnect()
       
    def testsend12(self):
        self.conn.subscribe(destination='/queue/test', id=1, ack='auto')

        self.conn.send(body='this is a test using protocol 1.2', destination='/queue/test')

        time.sleep(3)

        self.assert_(self.listener.connections == 1, 'should have received 1 connection acknowledgement')
        self.assert_(self.listener.messages == 1, 'should have received 1 message')
        self.assert_(self.listener.errors == 0, 'should not have received any errors')