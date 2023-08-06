# -*- coding: utf-8 -*-

from twisted.internet import defer
from twisted.internet import error

from il2ds_middleware.tests.base import BaseMiddlewareTestCase


class ConsoleClientFactoryConnectionFailTestCase(BaseMiddlewareTestCase):

    console_server_port = 20000
    device_link_server_port = 10000

    def setUp(self):

        def on_connection_fail(err):
            if isinstance(err.value, error.ConnectionRefusedError):
                self.console_client_connector = None

        d = super(ConsoleClientFactoryConnectionFailTestCase, self).setUp()
        return d.addErrback(on_connection_fail)

    def test_connection_fail(self):
        self.assertNot(self.console_client_connector)

    @property
    def console_client_host_for_client(self):
        return self.console_server_host, self.console_server_port+1

    @property
    def device_link_host_for_client(self):
        return self.device_link_server_host, self.device_link_server_port+1


class ConsoleClientFactoryTestCase(BaseMiddlewareTestCase):

    def test_connection(self):
        self.assertTrue(self.console_client_connector)

    def test_wrong_rid(self):
        self.console_client_factory._process_responce_id("rid|0")

    def test_malformed_rid(self):
        self.console_client_factory._process_responce_id("rid/smth")
        self.console_client_factory._process_responce_id("rid|smth")

    def test_mission_status(self):

        srvc = self.service.getServiceNamed('missions')

        def do_test():
            d = self.console_client_factory.mission_status()
            d.addCallback(check_not_loaded)
            d.addCallback(do_load)
            return d

        def do_load(_):
            srvc.load("net/dogfight/test.mis")
            d = self.console_client_factory.mission_status()
            d.addCallback(check_loaded)
            d.addCallback(do_begin)
            return d

        def do_begin(_):
            srvc.begin()
            d = self.console_client_factory.mission_status()
            d.addCallback(check_playing)
            return d

        def check_not_loaded(response):
            self.assertIsInstance(response, list)
            self.assertEqual(len(response), 1)
            self.assertEqual(response[0], "Mission NOT loaded")

        def check_loaded(response):
            self.assertIsInstance(response, list)
            self.assertEqual(len(response), 1)
            self.assertEqual(
                response[0], "Mission: net/dogfight/test.mis is Loaded")

        def check_playing(response):
            self.assertIsInstance(response, list)
            self.assertEqual(len(response), 1)
            self.assertEqual(
                response[0], "Mission: net/dogfight/test.mis is Playing")

        return do_test()

    def test_server_info(self):

        def callback(response):
            self.assertIsInstance(response, list)
            self.assertEqual(len(response), 3)
            self.assertEqual(response[0], "Type: Local server")
            self.assertEqual(response[1], "Name: Server")
            self.assertEqual(response[2], "Description: ")

        d = self.console_client_factory.server_info()
        return d.addCallback(callback)

    def test_long_operation(self):
        d = self.console_client_factory._send_request("horus long operation")
        return self.assertFailure(d, defer.TimeoutError)

    def test_sending_line_error(self):

        class FakeError(Exception):
            pass

        def fake_sendLine(line):
            raise FakeError

        self.console_client_factory._client.sendLine = fake_sendLine

        d1 = self.console_client_factory._send_request("test")
        self.assertFailure(d1, FakeError)

        d2 = self.console_client_factory._send("test")
        self.assertFailure(d2, FakeError)

    def test_send(self):
        return self.console_client_factory._send("test")

    def test_manual_input(self):

        def do_test():
            results = [
                "mission",
                "Mission NOT loaded",
            ]
            d = defer.Deferred()
            self._set_console_expecting_receiver(results, d)
            self.service.manual_input("mission")
            return d.addCallback(wait_a_bit)

        def wait_a_bit(_):
            """Wait to receive <consoleN><0>"""
            d = defer.Deferred()
            from twisted.internet import reactor
            reactor.callLater(0.05, d.callback, None)
            return d

        return do_test()

    def test_mission_load(self):

        def callback(response):
            self.assertIsInstance(response, list)
            obligatory_responses = [
                "Loading mission net/dogfight/test.mis...",
                "Load bridges",
                "Load static objects",
                "Mission: net/dogfight/test.mis is Loaded",
            ]
            for obligatory_response in obligatory_responses:
                self.assertIn(obligatory_response, response)
                self.assertEqual(response.count(obligatory_response), 1)

        d = self.console_client_factory.mission_load("net/dogfight/test.mis")
        return d.addCallback(callback)

    def test_mission_begin(self):

        def do_test():
            d = self.console_client_factory.mission_load(
                "net/dogfight/test.mis")
            return d.addCallback(do_begin)

        def do_begin(_):
            d = self.console_client_factory.mission_begin()
            return d.addCallback(callback)

        def callback(response):
            self.assertIsInstance(response, list)
            self.assertEqual(len(response), 1)
            self.assertEqual(
                response[0], "Mission: net/dogfight/test.mis is Playing")

        return do_test()

    def test_mission_end(self):

        def do_test():
            d = self.console_client_factory.mission_load(
                "net/dogfight/test.mis")
            return d.addCallback(do_begin)

        def do_begin(_):
            d = self.console_client_factory.mission_begin()
            return d.addCallback(do_end)

        def do_end(_):
            d = self.console_client_factory.mission_end()
            return d.addCallback(callback)

        def callback(response):
            self.assertIsInstance(response, list)
            self.assertEqual(len(response), 1)
            self.assertEqual(
                response[0], "Mission: net/dogfight/test.mis is Loaded")

        return do_test()

    def test_mission_destroy(self):

        def do_test():
            d = self.console_client_factory.mission_load(
                "net/dogfight/test.mis")
            return d.addCallback(do_begin)

        def do_begin(_):
            d = self.console_client_factory.mission_begin()
            return d.addCallback(do_destroy)

        def do_destroy(_):
            d = self.console_client_factory.mission_destroy()
            return d.addCallback(callback)

        def callback(response):
            self.assertIsInstance(response, list)
            self.assertEqual(len(response), 1)
            self.assertEqual(response[0], "Mission NOT loaded")

        return do_test()
