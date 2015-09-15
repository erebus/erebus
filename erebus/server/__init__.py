"""
"""
import stem.util.enum

from erebus.server import websockets

ServerHandlers = stem.util.enum.Enum(
    ('BANDWIDTH', r"/bandwidth"),
    ('LOG', r"/log"),
    ('INFO', r"/info"),
)

SERVER_HANDLERS = [
    (ServerHandlers.BANDWIDTH, websockets.BandwidthWSHandler),
    (ServerHandlers.LOG, websockets.LogWSHandler),
    (ServerHandlers.INFO, websockets.InfoWSHandler),
]

SERVER_SETTINGS = {}
