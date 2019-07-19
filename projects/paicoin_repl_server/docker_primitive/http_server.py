import logging
import os
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application, RequestHandler

import routes
from term_manager import TermManager

define('port', default=8888, help='port to listen on')

clr = 'clear'
if os.name == 'nt':
    clr = 'cls'

LOGGER = logging.getLogger(__name__)


def create_app(shell, close_future=None):
    """Create and return a tornado Web Application instance."""
    settings = {"static_path": os.path.join(
        os.path.dirname(__file__), "static")}
    application = Application(routes.gen_routes(close_future),
                              debug=True,
                              serve_traceback=True,
                              autoreload=True, **settings)
    application.term_manager = TermManager(['python', shell])
    return application


def main(port, shell):
    """Create and setup a new tornado server."""
    print("Server is now at: 127.0.0.1:{}".format(port))
    print('Shell: {0}'.format(shell))
    application = create_app(shell)
    ioloop = IOLoop.instance()
    application.listen(port)
    try:
        ioloop.start()
    except KeyboardInterrupt:
        pass
    finally:
        LOGGER.info("Closing server...\n")
        application.term_manager.shutdown()
        IOLoop.instance().stop()


if __name__ == '__main__':
    main(8888, '/home/scripts/paicoin_repl.py')
