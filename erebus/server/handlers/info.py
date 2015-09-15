"""
"""
from stem.control import State

from erebus.util import msg, tor_controller

def get_info():
    output = {'fingerprint': '--', 'nickname': '--', 'version': '--',
        'status': 'offline'}

    controller = tor_controller()
    if controller is not None:
        output['fingerprint'] = controller.get_info('fingerprint', 'Unknown')
        output['nickname'] = controller.get_conf('Nickname', '')
        output['version'] = str(controller.get_version('Unknown')).split()[0]
        output['status'] = 'online'

    return output

def get_status(state):
    return {'status': 'offline' if state == State.CLOSED else 'online'}
