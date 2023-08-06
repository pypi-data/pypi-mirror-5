# -*- coding: utf-8 -*-

from twisted.internet import defer
from twisted.trial.unittest import TestCase

from il2ds_middleware.protocol import ConsoleClientFactory

from il2ds_middleware.ds_emulator.service import RootService as DSService
from il2ds_middleware.ds_emulator.protocol import (ConsoleServerFactory,
    DeviceLinkServerProtocol, )


class BaseTestCase(TestCase):

    ConsoleClient = None
    DeviceLinkClient = None
    LogWatcher = None

    console_server_host = "127.0.0.1"
    console_server_port = 0
    device_link_server_host = "127.0.0.1"
    device_link_server_port = 0
    log_path = None

    log_watcher_interval = 0.1
    timeout_value = 0.05

    def setUp(self):
        self._set_log_watcher()
        self._listen_server()
        return self._connect_client()

    def _set_log_watcher(self):
        self.log_watcher = self.LogWatcher(
            self.log_path, self.log_watcher_interval
        ) if self.LogWatcher else None

    def _listen_server(self):
        self._listen_console_server()
        self._listen_device_link_server()
        self.service = DSService(self.console_server_factory, self.log_path)
        self.service.startService()

        self.console_server_factory.receiver = self.service.parse_line
        self.dl_server.on_requests = self.service.getServiceNamed('dl'
            ).got_requests

    def _listen_console_server(self):
        self.console_server_factory = ConsoleServerFactory()

        from twisted.internet import reactor
        self.console_server_listener = reactor.listenTCP(
            self.console_server_port, self.console_server_factory,
            interface=self.console_server_host)

    def _listen_device_link_server(self):
        self.dl_server = DeviceLinkServerProtocol()

        from twisted.internet import reactor
        self.dl_server_listener = reactor.listenUDP(
            self.device_link_server_port, self.dl_server,
            interface=self.device_link_server_host)

    def _connect_client(self):
        self._connect_device_link_client()
        return self._connect_console_client()

    def _connect_console_client(self):
        if self.ConsoleClient is None:
            self.console_client_connector = None
            return defer.succeed(_)

        self.console_client_factory = self.ConsoleClient()
        host, port = self.console_client_host_for_client

        from twisted.internet import reactor
        self.console_client_connector = reactor.connectTCP(
            host, port, self.console_client_factory)

        return self.console_client_factory.on_connecting

    def _connect_device_link_client(self):
        if self.DeviceLinkClient is None:
            self.dl_client_connector = None
            return

        self.dl_client = self.DeviceLinkClient(
            self.device_link_host_for_client)

        from twisted.internet import reactor
        self.dl_client_connector = reactor.listenUDP(0, self.dl_client)

    def tearDown(self):
        dlist = [self.service.stopService(), ]
        if self.log_watcher is not None:
            dlist.append(self.log_watcher.stopService())
        dlist.extend(self._stop_server())
        dlist.extend(self._stop_client())
        return defer.gatherResults(dlist)

    def _stop_server(self):
        results = []
        results.extend(self._stop_console_server())
        results.append(self._stop_device_link_server())
        return results

    def _stop_console_server(self):
        self.console_server_factory.on_data = None
        results = [
            defer.maybeDeferred(self.console_server_listener.stopListening),
        ]
        if self.console_client_connector is not None:
            results.append(self.console_server_factory.on_connection_lost)
        return results

    def _stop_device_link_server(self):
        self.dl_server.on_request = None
        return defer.maybeDeferred(self.dl_server_listener.stopListening)

    def _stop_client(self):
        results = []
        console_result = self._stop_console_client()
        if console_result is not None:
            results.append(console_result)
        dl_result = self._stop_device_link_client()
        if dl_result is not None:
            results.append(dl_result)
        return results

    def _stop_console_client(self):
        self.console_client_factory.receiver = None
        if self.console_client_connector is not None:
            self.console_client_connector.disconnect()
            return self.console_client_factory.on_connection_lost
        else:
            return None

    def _stop_device_link_client(self):
        if self.dl_client_connector is not None:
            self.dl_client.receiver = None
            return defer.maybeDeferred(self.dl_client_connector.stopListening)
        else:
            return None

    def _make_timeout(self, callback):
        from twisted.internet import reactor
        return reactor.callLater(self.timeout_value, callback, None)

    def _get_unexpecting_line_receiver(self, d):

        def got_line(line):
            timeout.cancel()
            from twisted.trial.unittest import FailTest
            d.errback(FailTest("Unexpected data:\n\t{0}.".format(line)))

        timeout = self._make_timeout(d.callback)
        return got_line

    def _get_expecting_line_receiver(self, expected_lines, d):

        def got_line(line):
            try:
                self.assertEqual(line, expected_lines.pop(0))
            except Exception as e:
                timeout.cancel()
                d.errback(e)
            else:
                if expected_lines:
                    return
                timeout.cancel()
                d.callback(None)

        def on_timeout(_):
            from twisted.trial.unittest import FailTest
            d.errback(FailTest(
                'Timed out, remaining lines:\n\t'+'\n\t'.join(expected_lines)))

        timeout = self._make_timeout(on_timeout)
        return got_line

    def _set_console_expecting_receiver(self, expected_lines, d):
        self.console_client_factory.got_line = \
            self._get_expecting_line_receiver(expected_lines, d)

    def _set_dl_expecting_receiver(self, expected_lines, d):
        self.dl_client.receiver = \
            self._get_expecting_line_receiver(expected_lines, d)

    def _set_event_log_expecting_receiver(self, expected_lines, d):
        self.log_watcher.receiver = \
            self._get_expecting_line_receiver(expected_lines, d)

    def console_message(self, msg):
        self.console_client_factory.message(msg)

    @property
    def console_client_host_for_client(self):
        if self.console_server_listener is None:
            return (None, None)
        endpoint = self.console_server_listener.getHost()
        return endpoint.host, endpoint.port

    @property
    def device_link_host_for_client(self):
        if self.dl_server_listener is None:
            return (None, None)
        endpoint = self.dl_server_listener.getHost()
        return endpoint.host, endpoint.port


class BaseMiddlewareTestCase(BaseTestCase):

    ConsoleClient = ConsoleClientFactory
