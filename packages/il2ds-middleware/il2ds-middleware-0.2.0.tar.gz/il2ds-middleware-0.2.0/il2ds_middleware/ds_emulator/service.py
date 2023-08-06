# -*- coding: utf-8 -*-

import datetime
import os

from twisted.application import internet
from twisted.application.service import Service, MultiService
from twisted.python import log
from zope.interface import implementer

from il2ds_middleware.constants import (DEVICE_LINK_OPCODE as OPCODE,
    MISSION_STATUS, PILOT_STATE, OBJECT_STATE, )
from il2ds_middleware.interfaces import ILineParser
from il2ds_middleware.mixin import PropagatingLineParserMixing
from il2ds_middleware.ds_emulator.interfaces import (ILineBroadcaster,
    IPilotService, IMissionService, IStaticObjectService, IDeviceLinkService,
    IEventLogger, )


@implementer(ILineBroadcaster)
class _CommonServiceMixin(PropagatingLineParserMixing):

    evt_log = None
    parent = None
    broadcaster = None

    def broadcast_line(self, line):
        if self.broadcaster:
            self.broadcaster.broadcast_line(line)
        elif self.parent:
            self.parent.broadcast_line(line)
        else:
            log.msg("Broadcasting into nowhere: \"{0}\"".format(line))


class RootService(MultiService, _CommonServiceMixin):
    """
    Top-level service.
    """
    def __init__(self, broadcaster, log_path=None):
        MultiService.__init__(self)
        self.broadcaster = broadcaster
        self.evt_log = EventLoggingService(log_path)
        self._init_children()

    def _init_children(self):
        """
        Initialize children services.
        """
        pilots = PilotService()
        static = StaticService()
        dl = DeviceLinkService()
        missions = MissionService()

        dl.pilot_srvc = pilots
        dl.static_srvc = static
        missions.dl_srvc = dl

        for service in [pilots, static, missions, dl, ]:
            service.setServiceParent(self)
            service.evt_log = self.evt_log

    def startService(self):
        self.broadcaster.service = self
        MultiService.startService(self)

    def stopService(self):
        self.broadcaster.service = None
        self.evt_log.setServiceParent(self)
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


@implementer(IPilotService)
class PilotService(Service, _CommonServiceMixin):

    name = "pilots"
    channel = 1
    channel_inc = 2
    port = 21000

    def __init__(self):
        self.pilots = {}

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
                'ip': ip,
                'channel': self.channel,
                'state': PILOT_STATE.IDLE,
                'army': "None",
            }
            self.channel += self.channel_inc
            return pilot

        pilot = create_pilot()
        self.pilots[callsign] = pilot

        self.broadcast_line(
            "socket channel '{0}' start creating: ip {1}:{2}".format(
                pilot['channel'], pilot['ip'], self.port))
        self.broadcast_line("Chat: --- {0} joins the game.".format(callsign))
        self.broadcast_line(
            "socket channel '{0}', ip {1}:{2}, {3}, "
            "is complete created.".format(
                pilot['channel'], pilot['ip'], self.port, callsign))
        self.evt_log.enlog("{0} has connected".format(callsign))

    def leave(self, callsign):
        self._leave(callsign)

    def _kick(self, callsign):
        self._leave(callsign, reason="You have been kicked from the server.")

    def _leave(self, callsign, reason=None):
        pilot = self.pilots.get(callsign)
        if pilot is None:
            log.err("Pilot with callsign \"{0}\" not found.".format(callsign))
            return
        del self.pilots[callsign]

        line = "socketConnection with {0}:{1} on channel {2} lost.  " \
            "Reason: ".format(pilot['ip'], self.port, pilot['channel'])
        if reason:
            line += reason
        self.broadcast_line(line)
        self.broadcast_line("Chat: --- {0} has left the game.".format(
            callsign))
        self.evt_log.enlog("{0} has disconnected".format(callsign))

    def idle(self, callsign):
        pilot = self.pilots.get(callsign)
        if pilot is not None:
            pilot['state'] = PILOT_STATE.IDLE
            self.evt_log.enlog("{0} entered refly menu".format(callsign))

    def spawn(self, callsign, craft=None, pos=None):
        pilot = self.pilots.get(callsign)
        if pilot is not None:
            pilot['state'] = PILOT_STATE.SPAWNED
            pilot['pos'] = pos or {
                'x': 0, 'y': 0, 'z': 0, }
            pilot['craft'] = craft or {
                'name': "A6M2-21",
                'weapons': "1xdt",
                'fuel': "100",
            }
            self.evt_log.enlog(
                "{0}:{1}(0) seat occupied by {0} at {2} {3}".format(
                    callsign, pilot['craft']['name'],
                    pilot['pos']['x'], pilot['pos']['y']))
            self.evt_log.enlog(
                "{0}:{1} loaded weapons '{2}' fuel {3}%".format(
                    callsign, pilot['craft']['name'],
                    pilot['craft']['weapons'], pilot['craft']['fuel']))

    def kill(self, callsign):
        pilot = self.pilots.get(callsign)
        if pilot is not None:
            pilot['state'] = PILOT_STATE.DEAD
            self.evt_log.enlog(
                "{0}:{1}(0) was killed at {2} {3}".format(
                    callsign, pilot['craft']['name'],
                    pilot['pos']['x'], pilot['pos']['y']))

    def get_active(self):
        return [x for x in self.pilots.keys()
            if self.pilots[x]['state'] != PILOT_STATE.IDLE]

    def stopService(self):
        self.pilots = None
        return Service.stopService(self)


@implementer(IMissionService)
class MissionService(Service, _CommonServiceMixin):

    name = "missions"
    status = MISSION_STATUS.NOT_LOADED
    mission = None
    dl_srvc = None

    def parse_line(self, line):
        if not line.startswith("mission"):
            return self._autopropagate(False)
        cmd = line[7:].strip()
        while True:
            if not cmd:
                self._send_status()
                break
            elif cmd.startswith("LOAD"):
                self.load(mission=cmd[4:].lstrip())
                break
            elif cmd == "BEGIN":
                self.begin()
                break
            elif cmd == "END":
                self.end()
                break
            elif cmd == "DESTROY":
                self.destroy()
                break
            return self._autopropagate(False)
        return self._autopropagate()

    def load(self, mission):
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
        self.status = MISSION_STATUS.LOADED
        self._send_status()

    def begin(self):
        if self.status == MISSION_STATUS.NOT_LOADED:
            self._mission_not_loaded()
        else:
            self.evt_log.start_log()
            self.status = MISSION_STATUS.PLAYING
            self._send_status()
            self.evt_log.enlog("Mission: {0} is Playing".format(self.mission))
            self.evt_log.enlog("Mission BEGIN")

    def end(self):
        if self.status == MISSION_STATUS.NOT_LOADED:
            self._mission_not_loaded()
        else:
            self.status = MISSION_STATUS.LOADED
            self._send_status()
            self.evt_log.enlog("Mission END")
            self.evt_log.stop_log()

    def destroy(self):
        if self.status == MISSION_STATUS.NOT_LOADED:
            self._mission_not_loaded()
        else:
            self.status = MISSION_STATUS.NOT_LOADED
            self.mission = None
            if self.dl_srvc:
                self.dl_srvc.forget_everything()

    def _mission_not_loaded(self):
        self.broadcast_line("ERROR mission: Mission NOT loaded")

    def _send_status(self):
        if self.status == MISSION_STATUS.NOT_LOADED:
            self.broadcast_line("Mission NOT loaded")
        elif self.status == MISSION_STATUS.LOADED:
            self.broadcast_line("Mission: {0} is Loaded".format(self.mission))
        elif self.status == MISSION_STATUS.PLAYING:
            self.broadcast_line("Mission: {0} is Playing".format(self.mission))

    def stopService(self):
        self.mission = None
        return Service.stopService(self)


@implementer(IStaticObjectService)
class StaticService(Service):

    name = "static"
    objects = None

    def __init__(self):
        self.objects = {}

    def spawn(self, name, pos=None):
        self.objects[name] = {
            'pos': pos or {
                'x': 0, 'y': 0, 'z': 0, },
            'state': OBJECT_STATE.ALIVE,
        }

    def destroy(self, name, attacker_name='landscape'):
        obj = self.objects[name]
        obj['state'] = OBJECT_STATE.DESTROYED
        self.evt_log.enlog("{0} destroyed by {1} at {2} {3}".format(
            name, attacker_name, obj['pos']['x'], obj['pos']['y']))

    def get_active(self):
        return [x for x in self.objects.keys()
            if self.objects[x]['state'] != OBJECT_STATE.DESTROYED]


@implementer(IDeviceLinkService)
class DeviceLinkService(Service):

    name = "dl"
    pilot_srvc = None
    static_srvc = None

    def __init__(self):
        self.forget_everything()

    def forget_everything(self):
        self.known_air = []
        self.known_static = []

    def got_requests(self, requests, address, peer):
        answers = []
        for request in requests:
            cmd = request['command']
            answer = None
            try:
                opcode = OPCODE.lookupByValue(cmd)
            except ValueError as e:
                log.err("Unknown command: {0}".format(cmd))
            else:
                args = request.get('args')
                if opcode == OPCODE.RADAR_REFRESH:
                    self._refresh_radar()
                elif opcode == OPCODE.PILOT_COUNT:
                    answer = self._pilot_count()
                elif opcode == OPCODE.PILOT_POS:
                    answer = self._pilot_pos(args)
                elif opcode == OPCODE.STATIC_COUNT:
                    answer = self._static_count()
                elif opcode == OPCODE.STATIC_POS:
                    answer = self._static_pos(args)
                if answer is not None:
                    answers.append(answer)
        if answers:
            peer.send_answers(answers, address)

    def _refresh_radar(self):
        self.known_air = self.pilot_srvc.get_active()
        self.known_static = self.static_srvc.get_active()

    def _pilot_count(self):
        result = len(self.known_air)
        return OPCODE.PILOT_COUNT.make_command(result)

    def _pilot_pos(self, args):
        data = self._pos(
            known_container=self.known_air,
            primary_container=self.pilot_srvc.pilots,
            invalid_states=[PILOT_STATE.IDLE, PILOT_STATE.DEAD, ],
            args=args)
        return OPCODE.PILOT_POS.make_command(data) if data else None

    def _static_count(self):
        result = len(self.known_static)
        return OPCODE.STATIC_COUNT.make_command(result)

    def _static_pos(self, args):
        data = self._pos(
            known_container=self.known_static,
            primary_container=self.static_srvc.objects,
            invalid_states=[OBJECT_STATE.DESTROYED, ],
            args=args)
        return OPCODE.STATIC_POS.make_command(data) if data else None

    def _pos(self, known_container, primary_container, invalid_states, args):
        if not args:
            return None
        idx = args[0]
        try:
            key = known_container[int(idx)]
        except Exception:
            data = 'BADINDEX'
        else:
            handler = primary_container[key]
            if handler['state'] in invalid_states:
                data = 'INVALID'
            else:
                pos = handler['pos']
                data = ';'.join([str(_)
                    for _ in [key, pos['x'], pos['y'], pos['z'], ]])
        finally:
            return ':'.join([idx, data, ])


@implementer(IEventLogger)
class EventLoggingService(Service):

    def __init__(self, log_path=None, keep_log=True):
        self.log_path = log_path
        self.keep_log = keep_log
        self.log_file = None
        self.last_evt_time = None

    def enlog(self, line):
        if self.log_file is not None:
            self._do_log(line)
        else:
            log.msg("Logging event into nowhere: \"{0}\"".format(line))

    def _do_log(self, line):
        evt_time = datetime.datetime.now()
        timestamp = self._get_formated_time(evt_time)
        _line = "[{0}] {1}\n".format(timestamp, line)
        self.log_file.write(_line)
        self.last_evt_time = evt_time

    def _get_formated_time(self, timestamp):
        """
        We do not need leading zero before hours, so we will replace it
        if it is present. To find it we use symbol '-'.
        """
        format = "-%I:%M:%S %p"
        if self._day_differs(timestamp):
            format = "%b %d, %Y " + format
        return timestamp.strftime(format).replace('-0', '').replace('-', '')

    def _day_differs(self, timestamp):
        return timestamp.day != self.last_evt_time.day \
            if self.last_evt_time is not None else True

    def start_log(self):
        self.stop_log()
        if self.log_path is not None:
            self.log_file = open(self.log_path, 'a' if self.keep_log else 'w')

    def stop_log(self):
        if self.log_file is not None:
            self.log_file.close()
            self.log_file = None

    def stopService(self):
        self.stop_log()
        if self.log_path is not None and os.path.isfile(self.log_path):
            os.remove(self.log_path)
        return Service.stopService(self)
