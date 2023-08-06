# -*- coding: utf-8 -*-

from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver

from il2ds_middleware.protocol import DeviceLinkProtocol
from il2ds_middleware.ds_emulator.protocol import ConsoleFactory


class ConsoleServerFactory(ConsoleFactory):

    def __init__(self):
        ConsoleFactory.__init__(self)
        self.on_connection_lost = Deferred()

    def client_left(self, client):
        ConsoleFactory.client_left(self, client)
        self.on_connection_lost.callback(client)


class ConsoleClientProtocol(LineReceiver):

    def connectionMade(self):
        self.factory.client_joined(self)

    def connectionLost(self, reason):
        self.factory.client_left(self)

    def lineReceived(self, line):
        self.factory.got_line(line)


class ConsoleClientFactory(ClientFactory):

    protocol = ConsoleClientProtocol
    receiver = None

    def __init__(self):
        self.clients = []
        self.on_connection_made = Deferred()
        self.on_connection_lost = Deferred()

    def client_joined(self, client):
        self.on_connection_made.callback(client)
        self.clients.append(client)

    def client_left(self, client):
        self.on_connection_lost.callback(client)
        self.clients.remove(client)

    def got_line(self, line):
        if self.receiver is not None:
            self.receiver(line)

    def message(self, message):

        def do_message(message):
            for client in self.clients:
                client.sendLine(message)

        from twisted.internet import reactor
        reactor.callLater(0, do_message, message)


class DeviceLinkClientProtocol(DeviceLinkProtocol):

    receiver = None

    def answers_received(self, answers, address):
        if self.receiver is not None:
            line = "A/" + self._format(answers)
            self.receiver(line)
