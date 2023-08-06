# -*- coding: utf-8 -*-

from twisted.application import internet
from twisted.application.service import IService, Service, MultiService
from twisted.python import log
from zope.interface import implementer, Interface

from il2ds_middleware.ds_emulator.interfaces import ILineBroadcaster


class ILineParser(Interface):

    def parse_line(self, line):
        """
        Return True if line was successfully parsed, otherwise return False.
        """
        raise NotImplementedError


class _PropagatorMixin:

    propagate = False

    def _autopropagate(self, value=True):
        return False if self.propagate else value


@implementer(IService, ILineBroadcaster)
class _LineBroadcastingServiceMixin:

    broadcaster = None

    def broadcast_line(self, line):
        if self.broadcaster:
            self.broadcaster.broadcast_line(line)
        elif self.parent:
            self.parent.broadcast_line(line)
        else:
            log.msg("Broadcasting into nowhere: \"{0}\"".format(line))


@implementer(ILineParser)
class _DSServiceMixin(_LineBroadcastingServiceMixin, _PropagatorMixin):
    pass


class RootService(MultiService, _DSServiceMixin):

    """
    Top-level service.
    """

    def __init__(self, broadcaster):
        MultiService.__init__(self)
        self.broadcaster = broadcaster
        self._init_children()

    def _init_children(self):
        """
        Initialize children services.
        """
        PilotService().setServiceParent(self)
        MissionService().setServiceParent(self)

    def startService(self):
        self.broadcaster.service = self
        MultiService.startService(self)

    def stopService(self):
        self.broadcaster.service = None
        return MultiService.stopService(self)

    def parse_line(self, line):
        result = False
        for service in self.services:
            if not ILineParser.providedBy(service):
                continue
            result = service.parse_line(line)
            if result:
                break
        if not result:
            self.broadcast_line("Command not found: " + line)
        return self._autopropagate(result)


class PilotService(Service, _DSServiceMixin):

    name = "pilots"
    channel = 1
    channel_inc = 2
    port = 21000

    def __init__(self):
        self.pilots = []

    def parse_line(self, line):
        while True:
            if line.startswith("kick"):
                self._kick(callsign=line[4:].strip())
                break
            return self._autopropagate(False)
        return self._autopropagate()

    def join(self, callsign, ip):

        def create_pilot():
            pilot = {
                'callsign': callsign,
                'ip': ip,
                'channel': self.channel,
            }
            self.channel += self.channel_inc
            return pilot

        pilot = create_pilot()
        self.pilots.append(pilot)

        self.broadcast_line(
            "socket channel '{0}' start creating: ip {1}:{2}".format(
                pilot['channel'], pilot['ip'], self.port))
        self.broadcast_line(
            "Chat: --- {0} joins the game.".format(
                pilot['callsign']))
        self.broadcast_line(
            "socket channel '{0}', ip {1}:{2}, {3}, "
            "is complete created.".format(
                pilot['channel'], pilot['ip'], self.port, pilot['callsign']))

    def leave(self, callsign):
        self._leave(callsign)

    def _kick(self, callsign):
        self._leave(callsign, reason="You have been kicked from the server.")

    def _leave(self, callsign, reason=None):
        pilot = self._pilot_by_callsign(callsign)
        if pilot is None:
            return
        self.pilots.remove(pilot)

        line = "socketConnection with {0}:{1} on channel {2} lost.  " \
            "Reason: ".format(pilot['ip'], self.port, pilot['channel'])
        if reason:
            line += reason
        self.broadcast_line(line)
        self.broadcast_line("Chat: --- {0} has left the game.".format(
            pilot['callsign']))

    def _pilot_by_callsign(self, callsign):
        for p in self.pilots:
            if p['callsign'] == callsign:
                return p
        log.err("Pilot with callsign \"{0}\" not found.".format(callsign))
        return None

    def stopService(self):
        self.pilots = None
        return Service.stopService(self)


MISSION_NONE, MISSION_LOADED, MISSION_PLAYING = tuple(range(1, 4))


class MissionService(Service, _DSServiceMixin):

    name = "missions"
    status = MISSION_NONE
    mission = None

    def parse_line(self, line):
        if not line.startswith("mission"):
            return self._autopropagate(False)
        cmd = line[7:].strip()
        while True:
            if not cmd:
                self._send_status()
                break
            elif cmd.startswith("LOAD"):
                self._load_mission(mission=cmd[4:].lstrip())
                break
            elif cmd == "BEGIN":
                self._begin_mission()
                break
            elif cmd == "END":
                self._end_mission()
                break
            elif cmd == "DESTROY":
                self._destroy_mission()
                break
            return self._autopropagate(False)
        return self._autopropagate()

    def _load_mission(self, mission):
        self.mission = mission
        self.broadcast_line("Loading mission {0}...".format(self.mission))
        self.broadcast_line("Load bridges")
        self.broadcast_line("Load static objects")
        self.broadcast_line("##### House without collision "
            "(3do/Tree/Tree2.sim)")
        self.broadcast_line("##### House without collision "
            "(3do/Buildings/Port/Floor/live.sim)")
        self.broadcast_line("##### House without collision "
            "(3do/Buildings/Port/BaseSegment/live.sim)")
        self.status = MISSION_LOADED
        self._send_status()

    def _begin_mission(self):
        if self.status == MISSION_NONE:
            self._mission_not_loaded()
        else:
            self.status = MISSION_PLAYING
            self._send_status()

    def _end_mission(self):
        if self.status == MISSION_NONE:
            self._mission_not_loaded()
        else:
            self.status = MISSION_LOADED
            self._send_status()

    def _destroy_mission(self):
        if self.status == MISSION_NONE:
            self._mission_not_loaded()
        else:
            self.status = MISSION_NONE
            self.mission = None

    def _mission_not_loaded(self):
        self.broadcast_line("ERROR mission: Mission NOT loaded")

    def _send_status(self):
        if self.status == MISSION_NONE:
            self.broadcast_line("Mission NOT loaded")
        elif self.status == MISSION_LOADED:
            self.broadcast_line("Mission: {0} is Loaded".format(self.mission))
        elif self.status == MISSION_PLAYING:
            self.broadcast_line("Mission: {0} is Playing".format(self.mission))

    def stopService(self):
        self.mission = None
        return Service.stopService(self)
