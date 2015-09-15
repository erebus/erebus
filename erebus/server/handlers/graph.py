"""
"""
import time

from stem.util import log, str_tools, system

from erebus.util import msg, tor_controller

BW_HANDLER = None


def bw_handler():
    """
    Singleton for getting our bw hander.
    """
    return BW_HANDLER

def init_bw_handler():
    """
    """
    global BW_HANDLER
    BW_HANDLER = BWHandler()


class BWHandler():

    def __init__(self):
        self._start_time = system.start_time(tor_controller().get_pid(None))
    
    def get_cache(self):
        """
        """
        output = {'read_total': 0, 'write_total': 0, 'entries': []}

        controller = tor_controller()
        if controller is not None:
            bw_entries = controller.get_info('bw-event-cache', None)
            is_successful = True

            if bw_entries:
                for entry in bw_entries.split():
                    entry_comp = entry.split(',')

                    if len(entry_comp) != 2 or not entry_comp[0].isdigit() or not entry_comp[1].isdigit():
                        log.warn(msg('panel.graphing.bw_event_cache_malformed', response=bw_entries))
                        is_successful = False
                        break

                    output['entries'].append({
                        'read': entry_comp[0],
                        'written': entry_comp[1]
                    })

                if is_successful:
                    log.info(msg('panel.graphing.prepopulation_successful',
                            duration=str_tools.time_label(
                            len(bw_entries.split()), is_long=True)))

            read_total = controller.get_info('traffic/read', None)
            write_total = controller.get_info('traffic/written', None)

            if read_total and write_total:
                output['read_total'] = read_total
                output['write_total'] = write_total

        # Finally, set message's type
        output['reply'] = 'BW-CACHE'

        return output

    def get_info(self, event):
        """
        """
        output = {'read': event.read, 'written': event.written}

        controller = tor_controller()
        if controller is not None:
            read_total = controller.get_info('traffic/read', None)
            write_total = controller.get_info('traffic/written', None)

            if read_total and write_total:
                output['read_total'] = read_total
                output['write_total'] = write_total

                output['read_avg'] = float(read_total) / (time.time() - self._start_time)
                output['write_avg'] = float(write_total) / (time.time() - self._start_time)

            # start_time = system.start_time(controller.get_pid(None))
            bw_rate = controller.get_effective_rate(None)
            bw_burst = controller.get_effective_rate(None, burst=True)

            if bw_rate and bw_burst:
                output['limit'] = bw_rate
                output['burst'] = bw_burst

            my_router_status_entry = controller.get_network_status(default=None)
            measured_bw = getattr(my_router_status_entry, 'bandwidth', None)

            if measured_bw:
                output['measured'] = measured_bw
            else:
                my_server_descriptor = controller.get_server_descriptor(default=None)
                observed_bw = getattr(my_server_descriptor, 'observed_bandwidth', None)
                if observed_bw:
                    output['observed'] = observed_bw

        # Finally, set message's type
        output['reply'] = 'BW-EVENT'

        return output
