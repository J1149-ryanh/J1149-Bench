import term_rest_handler as rest
import term_web_handler as web
import term_websocket_handler as websockets

# Define new rest associations
REST = [
    (r"/api/terminals", rest.MainHandler),
    (r"/api/terminals/(.*)/size", rest.ResizeHandler)
]

# Define new websocket routes
WS = [
    (r"/terminals/(.*)", websockets.MainSocket)
]

# Define new web rendering route associations
WEB = [
    (r'/', web.MainHandler)
]

ROUTES = REST + WS + WEB


def gen_routes(close_future):
    """Return a list of HTML redirection routes."""
    if close_future is not None:
        ws = []
        for route in WS:
            ws.append((route[0], route[1],
                       dict(close_future=close_future)))
        return REST + ws + WEB
    return ROUTES