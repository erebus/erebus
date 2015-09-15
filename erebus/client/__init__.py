"""
"""
import os.path

import stem.util.enum

from erebus.client import handlers

BASE_DIR = os.path.sep.join(__file__.split(os.path.sep)[:-2])

ClientHandlers = stem.util.enum.Enum(('DASHBOARD', r"/"))

CLIENT_HANDLERS = [
    (ClientHandlers.DASHBOARD, handlers.DashboardHandler),
]

CLIENT_SETTINGS = {
    'template_path': os.path.join(BASE_DIR, 'client/templates'),
    'static_path': os.path.join(BASE_DIR, 'client/static'),
    'autoescape': None
}
