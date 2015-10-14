# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Erebus, a web dashboard for tor relays.
#
# :copyright:   (c) 2015, The Tor Project, Inc.
#               (c) 2015, Damian Johnson
#               (c) 2015, Cristobal Leiva
#
# :license: See LICENSE for licensing information.

"""
Bandwidth-related functions, including read/written (current, avg, total)
bytes, limit, burst, etc.
"""

import time

from stem.util import log, str_tools, system

from erebus.util import msg, tor_controller

BW_HANDLER = None


def bw_handler():
    """
    Provides the BW_HANDLER singleton.

    :returns: :class:`~erebus.server.handlers.graph.BWHandler`
    """

    return BW_HANDLER


def init_bw_handler():
    """
    Initializes the bandwidth handler instance, which needs to be tracked
    by the websockets controller.
    """

    global BW_HANDLER
    BW_HANDLER = BWHandler()


class BWHandler():
    """
    Bandwidth handler.
    """

    def __init__(self):
        """
        Saves start time of tor controll connection, so we can further
        calculate average values during time.
        """

        self._start_time = system.start_time(tor_controller().get_pid(None))

    def get_cache(self):
        """
        Retrieve bandwidth cache, if available.

        :returns: dictionary with bandwidth cache entries.
        """

        output = {
            'header': 'BW-CACHE',
            'read_total': 0,
            'write_total': 0,
            'entries': []
        }

        controller = tor_controller()
        if controller is not None:
            bw_entries = controller.get_info('bw-event-cache', None)
            is_successful = True

            if bw_entries:
                for entry in bw_entries.split():
                    entry_comp = entry.split(',')
                    # Check for malformed cache entries
                    if len(entry_comp) != 2 or not entry_comp[0].isdigit() \
                            or not entry_comp[1].isdigit():
                        log.warn(msg('bw.cache_malformed', output=bw_entries))
                        is_successful = False
                        break
                    output['entries'].append({
                        'read': entry_comp[0],
                        'written': entry_comp[1]})

            if is_successful:
                log.info(msg('bw.cache_success', duration=str_tools.time_label(
                    len(bw_entries.split()), is_long=True)))

            read_total = controller.get_info('traffic/read', None)
            write_total = controller.get_info('traffic/written', None)

            if read_total and write_total:
                output['read_total'] = read_total
                output['write_total'] = write_total

        return output

    def get_info(self, event):
        """
        Receive bandwidth event and retrieve useful info.

        :param Class event: :class:`~stem.response.events.Event`
          delivered by stem.

        :returns: dictionary with bandwidth information.
        """

        output = {
            'header': 'BW-EVENT',
            'read': event.read,
            'written': event.written
        }

        controller = tor_controller()

        read_total = controller.get_info('traffic/read', None)
        write_total = controller.get_info('traffic/written', None)

        if read_total and write_total:
            output['read_total'] = read_total
            output['write_total'] = write_total

            time_window = (time.time() - self._start_time)
            output['read_avg'] = float(read_total) / time_window
            output['write_avg'] = float(write_total) / time_window

        bw_rate = controller.get_effective_rate(None)
        bw_burst = controller.get_effective_rate(None, burst=True)

        if bw_rate and bw_burst:
            output['limit'] = bw_rate
            output['burst'] = bw_burst

        router_status_entry = controller.get_network_status(default=None)
        measured_bw = getattr(router_status_entry, 'bandwidth', None)

        if measured_bw:
            output['measured'] = measured_bw
        else:
            server_desc = controller.get_server_descriptor(default=None)
            observed_bw = getattr(server_desc, 'observed_bandwidth', None)
            if observed_bw:
                output['observed'] = observed_bw

        return output
