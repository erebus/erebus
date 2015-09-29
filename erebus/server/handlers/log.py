"""
log handler
"""
import datetime
import time
import threading

from stem.response import events
from stem.util import conf, log, system

from erebus.util import tor_controller

try:
    # added in python 3.2
    from functools import lru_cache
except ImportError:
    from stem.util.lru_cache import lru_cache


def conf_handler(key, value):
    if key == 'log.prepopulate.limit':
        return max(0, value)
    elif key == 'log.cache.size':
        return max(20, value)


CONFIG = conf.config_dict('erebus', {
    'log.prepopulate.limit': 20,
    'log.cache.size': 20,
    'tor.chroot': '',
}, conf_handler)

TIMEZONE_OFFSET = time.altzone if time.localtime()[8] else time.timezone
TOR_RUNLEVELS = ['DEBUG', 'INFO', 'NOTICE', 'WARN', 'ERR']
TOR_EVENT_TYPES = {
    'd': 'DEBUG',
    'i': 'INFO',
    'n': 'NOTICE',
    'w': 'WARN',
    'e': 'ERR',

    'a': 'ADDRMAP',
    'f': 'AUTHDIR_NEWDESCS',
    'h': 'BUILDTIMEOUT_SET',
    'b': 'BW',
    'c': 'CIRC',
    'j': 'CLIENTS_SEEN',
    'k': 'DESCCHANGED',
    'g': 'GUARD',
    'l': 'NEWCONSENSUS',
    'm': 'NEWDESC',
    'p': 'NS',
    'q': 'ORCONN',
    's': 'STREAM',
    'r': 'STREAM_BW',
    't': 'STATUS_CLIENT',
    'u': 'STATUS_GENERAL',
    'v': 'STATUS_SERVER',
}

LOG_HANDLER = None


def log_handler():
    """
    Singleton for getting our log hander.

    :returns: :class:`~erebus.server.handlers.log.LogHandler`
    """
    return LOG_HANDLER

def init_log_handler(logged_events, listener):
    """
    """
    global LOG_HANDLER
    LOG_HANDLER = LogHandler(logged_events, listener)

def missing_event_types():
    """
    Provides the event types the current tor connection supports but erebus
    doesn't. This provides an empty list if no event types are missing or the
    GETINFO query fails.

    :returns: **list** of missing event types
    """
    response = None
    controller = tor_controller()
    response = controller.get_info('events/names', []) if controller else []

    tor_event_types = response.split(' ')
    recognized_types = TOR_EVENT_TYPES.values()
    return list(filter(lambda x: x not in recognized_types, tor_event_types))


class LogHandler():

    def __init__(self, logged_events, listener):
        self._event_log = LogGroup(CONFIG['log.cache.size'], group_by_day=True)
        self._tor_events = self._get_tor_events(logged_events)
        self._erebus_events = self._get_erebus_events(logged_events)
        self._logged_events = self._get_all_events()

        self._init_erebus_log(listener)

    def _get_erebus_events(self, events):
        events = set(events)
        erebus_events = events.intersection(
            set(['EREBUS_%s' % runlevel for runlevel in TOR_RUNLEVELS])
        )
        return sorted(erebus_events)

    def _get_tor_events(self, events):
        events = set(events)
        tor_events = events.intersection(set(TOR_EVENT_TYPES.values()))
        # adds events unrecognized by erebus if we're listening to the
        # 'UNKNOWN' type
        if 'UNKNOWN' in events:
            tor_events.update(set(missing_event_types()))
        return sorted(tor_events)

    def _get_all_events(self):
        erebus_events = set(self._erebus_events)
        tor_events = set(self._tor_events)
        return sorted(tor_events.union(erebus_events))

    def _tor_event(self, event):
        msg = ' '.join(str(event).split(' ')[1:])

        if isinstance(event, events.BandwidthEvent):
            msg = 'READ: %i, WRITTEN: %i' % (event.read, event.written)
        elif isinstance(event, events.LogEvent):
            msg = event.message

        return self._event(LogEntry(event.arrived_at, event.type, msg))

    def _erebus_event(self, record):
        # 'EREBUS_%s' % record.levelname
        return self._event(LogEntry(int(record.created), record.levelname, record.msg))

    def _event(self, event):
        if event.type not in self._logged_events:
            return
        self._event_log.add(event)
        return {'header': 'LOG-ENTRY', 'time': event.readable_time,
                'type': event.type.lower(), 'message': event.message}

    def _init_erebus_log(self, listener):
        """
        Configures erebus to notify a function of its events.

        :param function listener: listener to be notified
        """

        stem_log = log.get_logger()
        erebus_log = log.LogBuffer(log.Runlevel.DEBUG, yield_records=True)
        stem_log.addHandler(erebus_log)

        for event in erebus_log:
            if event in list(self._erebus_events):
                listener(event)
        erebus_log.emit = listener

    def init_tor_log(self, listener):
        """
        Configures tor to notify a function of its events.
        """
        controller = tor_controller()
        if controller is not None:
            controller.remove_event_listener(listener)
            for event_type in self._tor_events:
                try:
                    controller.add_event_listener(listener, event_type)
                except stem.ProtocolError:
                    self._event_types.remove(event_type)
            self._prepopulate()

    def _prepopulate(self):
        """
        Prepopulate log
        """
        log_location = log_file_path()
        if log_location:
            try:
                for entry in reversed(list(read_tor_log(log_location, CONFIG['log.prepopulate.limit']))):
                    if entry.type in self._logged_events:
                        self._event_log.add(entry)
            except IOError as exc:
                log.info('Unable to read log located at %s: %s' % (log_location, exc))
            except ValueError as exc:
                log.info(str(exc))

    def get_cache(self):
        """
        Return list of log entries that we have in memory
        (Could be the log prepolation or the log entries we've stored
        during execution of erebus)
        """
        output = {'header': 'LOG-CACHE', 'entries': []}
        for entry in list(self._event_log):
            output['entries'].insert(0, {'time': entry.readable_time,
                                        'message': entry.message,
                                        'type': entry.type.lower()})
        return output


class LogGroup(object):
    """
    Thread safe collection of LogEntry instances, which maintains a
    certain size.
    """

    def __init__(self, max_size, group_by_day=False):
        self._max_size = max_size
        self._entries = []
        self._lock = threading.RLock()

    def add(self, entry):
        with self._lock:
            self._entries.insert(0, entry)
            while len(self._entries) > self._max_size:
                self.pop()

    def pop(self):
        with self._lock:
            last_entry = self._entries.pop()

    def __len__(self):
        with self._lock:
            return len(self._entries)

    def __iter__(self):
        with self._lock:
            for entry in self._entries:
                yield entry


class LogEntry(object):
    """
    Individual tor or erebus log entry.

    **Note:** Tor doesn't include the date in its timestamps so the year
    component may be inaccurate. (:trac:`15607`)

    :var int timestamp: unix timestamp for when the event occured
    :var str type: event type
    :var str message: event's message
    """

    def __init__(self, timestamp, type, message):
        self.timestamp = timestamp
        self.type = type
        self.message = message
        entry_time = time.localtime(self.timestamp)
        self.readable_time = '%02i:%02i:%02i' % (entry_time[3],
                                                entry_time[4],
                                                entry_time[5])

    def __eq__(self, other):
        if isinstance(other, LogEntry):
            return hash(self) == hash(other)
        else:
            return False

    def __hash__(self):
        return hash(self.display_message)


def log_file_path():
    """
    Provides the path where tor's log file resides, if one exists.

    :params stem.control.Controller controller: tor controller connection

    :returns: **str** with the absolute path of our log file, or **None**
    if one doesn't exist
    """
    controller = tor_controller()
    if controller is not None:
        for log_entry in controller.get_conf('Log', [], True):
            entry_comp = log_entry.split()
            # looking for an entry like:
            # notice file /var/log/tor/notices.log
            if entry_comp[1] == 'file':
                return CONFIG['tor.chroot'] + entry_comp[2]

@lru_cache()
def condense_runlevels(*events):
    """
    Provides runlevel events with condensed. For example...

    >>> condense_runlevels('DEBUG', 'NOTICE', 'WARN', 'ERR',
    'EREBUS_NOTICE', 'EREBUS_WARN', 'EREBUS_ERR', 'BW')
    ['TOR/EREBUS NOTICE-ERROR', 'DEBUG', 'BW']

    :param list events: event types to be condensed

    :returns: **list** of the input events, with condensed runlevels
    """

    def ranges(runlevels):
        ranges = []

        while runlevels:
            # provides the (start, end) for a contiguous range
            start = end = runlevels[0]

            for r in TOR_RUNLEVELS[TOR_RUNLEVELS.index(start):]:
                if r in runlevels:
                    runlevels.remove(r)
                    end = r
                else:
                    break

            ranges.append((start, end))

    return ranges

    events = list(events)
    tor_runlevels, erebus_runlevels = [], []

    for r in TOR_RUNLEVELS:
        if r in events:
            tor_runlevels.append(r)
            events.remove(r)

        if 'EREBUS_%s' % r in events:
            erebus_runlevels.append(r)
            events.remove('EREBUS_%s' % r)

    tor_ranges = ranges(tor_runlevels)
    erebus_ranges = ranges(erebus_runlevels)

    result = []

    for runlevel_range in tor_ranges:
        if runlevel_range[0] == runlevel_range[1]:
            range_label = runlevel_range[0]
        else:
            range_label = '%s-%s' % (runlevel_range[0], runlevel_range[1])

        if runlevel_range in erebus_ranges:
            result.append('TOR/EREBUS %s' % range_label)
            erebus_ranges.remove(runlevel_range)
        else:
            result.append(range_label)

    for runlvl_range in erebus_ranges:
        if runlvl_range[0] == runlvl_range[1]:
            result.append('EREBUS %s' % runlvl_range[0])
        else:
            result.append('EREBUS %s-%s' % (runlvl_range[0], runlvl_range[1]))

    return result + events

def read_tor_log(path, read_limit=None):
    """
    Provides logging messages from a tor log file, from newest to oldest.

    :param str path: logging location to read from
    :param int read_limit: maximum number of lines to read from the file

    :returns: **iterator** for **LogEntry** for the file's contents

    :raises:
    * **ValueError** if the log file has unrecognized content
    * **IOError** if unable to read the file
    """

    start_time = time.time()
    count, isdst = 0, time.localtime().tm_isdst

    for line in system.tail(path, read_limit):
        # entries look like:
        # Jul 15 18:29:48.806 [notice] Parsing GEOIP file.

        line_comp = line.split()

        # Checks that we have all the components we expect. This could
        # happen if we're either not parsing a tor log or in weird edge
        # cases (like being out of disk space).

        if len(line_comp) < 4:
            raise ValueError("Log located at %s has a line that doesn't match the format we expect: %s" % (path, line))
        elif len(line_comp[3]) < 3 or line_comp[3][1:-1].upper() not in TOR_RUNLEVELS:
            raise ValueError('Log located at %s has an unrecognized runlevel: %s' % (path, line_comp[3]))

        runlevel = line_comp[3][1:-1].upper()
        msg = ' '.join(line_comp[4:])
        current_year = str(datetime.datetime.now().year)

        # Pretending it's the current year. We don't know the actual
        # year (#15607) and this may fail due to leap years when picking
        # Feb 29th (#5265).

        try:
            timestamp_str = current_year + ' ' + ' '.join(line_comp[:3])
            # drop fractional seconds
            timestamp_str = timestamp_str.split('.', 1)[0]
            timestamp_comp = list(time.strptime(
                timestamp_str, '%Y %b %d %H:%M:%S'))
            timestamp_comp[8] = isdst
            # converts local to unix time
            timestamp = int(time.mktime(tuple(timestamp_comp)))

            if timestamp > time.time():
                # log entry is from before a year boundary
                timestamp_comp[0] -= 1
                timestamp = int(time.mktime(timestamp_comp))
        except ValueError:
            raise ValueError("Log located at %s has a timestamp we don't recognize: %s" % (path, ' '.join(line_comp[:3])))

        count += 1
        yield LogEntry(timestamp, runlevel, msg)

        if 'opening log file' in msg:
            break  # this entry marks the start of this tor instance

    #log.info('log.read_from_log_file', count=count, path=path,
    #        read_limit=read_limit if read_limit else 'none',
    #        runtime='%0.3f' % (time.time() - start_time))
