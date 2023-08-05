# -*- coding: utf-8 -*-
import mock
import unittest

from beaver.config import BeaverConfig

try:
    from beaver.transport.zmq_transport import ZmqTransport
    skip = False
except ImportError, e:
    if e.message == 'No module named zmq':
        skip = True


@unittest.skipIf(skip, 'zmq not installed')
class ZmqTests(unittest.TestCase):

    def setUp(self):
        self.beaver_config = BeaverConfig(mock.Mock(config=None))

    def test_pub(self):
        self.beaver_config.set('zeromq_address', 'tcp://localhost:2120')
        transport = ZmqTransport(self.beaver_config)
        transport.interrupt()
        #assert not transport.zeromq_bind

    def test_bind(self):
        self.beaver_config.set('zeromq_bind', 'bind')
        self.beaver_config.set('zeromq_address', 'tcp://localhost:2120')
        ZmqTransport(self.beaver_config)
        #assert transport.zeromq_bind
