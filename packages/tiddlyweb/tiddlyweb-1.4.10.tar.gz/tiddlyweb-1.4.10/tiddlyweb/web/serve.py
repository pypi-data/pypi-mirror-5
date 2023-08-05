"""
Functions and Classes for running a TiddlyWeb server, including
optionally a built in web server.
"""
import logging

from selector import Selector

from tiddlyweb.util import std_error_message, initialize_logging


LOGGER = logging.getLogger(__name__)


def load_app(app_prefix=None, dirname=None):
    """
    Create our application from a series of layers. The innermost
    layer is a selector application based on urls_map in config. This
    is surround by wrappers, which either set something in the
    environment, modify the request, or transform output.
    """
    from tiddlyweb.config import config
    if dirname:
        config['root_dir'] = dirname

    # If the logger is not already initialized (from twanager),
    # let's initialize it.
    if LOGGER.parent.name is not 'tiddlyweb':
        initialize_logging(config, server=True)

    mapfile = config['urls_map']
    if app_prefix is not None:
        prefix = app_prefix
    else:
        prefix = config['server_prefix']
    app = Selector(mapfile=mapfile, prefix=prefix)
    config['selector'] = app

    try:
        plugins = config['system_plugins']
        for plugin in plugins:
            LOGGER.debug('attempt to import system plugin %s', plugin)
            # let the import fail with error if it does
            imported_module = __import__(plugin, {}, {}, ['init'])
            imported_module.init(config)
    except KeyError:
        pass  # no plugins

    wrappers = []
    wrappers.extend(reversed(config['server_request_filters']))
    wrappers.append(RequestLogger)  # required as the first app
    wrappers.append(Configurator)  # required as the second app
    wrappers.extend(config['server_response_filters'])
    if wrappers:
        for wrapper in wrappers:
            LOGGER.debug('wrapping app with %s', wrapper)
            if wrapper == Configurator:
                app = wrapper(app, config=config)
            else:
                app = wrapper(app)
    return app


def start_cherrypy(config):
    """
    Start a CherryPy webserver to run our app.
    """
    from cherrypy.wsgiserver import CherryPyWSGIServer
    hostname = config['server_host']['host']
    port = int(config['server_host']['port'])
    scheme = config['server_host']['scheme']
    app = load_app()
    server = CherryPyWSGIServer((hostname, port), app)
    try:
        LOGGER.debug('starting CherryPy at %s://%s:%s',
                scheme, hostname, port)
        std_error_message("Starting CherryPy at %s://%s:%s"
                % (scheme, hostname, port))
        server.start()
    except KeyboardInterrupt:
        server.stop()


class RequestLogger(object):
    """
    WSGI middleware that logs basic request information
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        LOGGER.debug('starting %s request with URI "%s", script_name "%s"'
                ', path_info "%s" and query "%s"',
                environ.get('REQUEST_METHOD', None),
                environ.get('REQUEST_URI', None),
                environ.get('SCRIPT_NAME', None),
                environ.get('PATH_INFO', None),
                environ.get('QUERY_STRING', None))
        return self.application(environ, start_response)


class Configurator(object):
    """
    WSGI middleware to handle setting a config dict
    for every request.
    """

    def __init__(self, application, config):
        self.application = application
        self.config = config

    def __call__(self, environ, start_response):
        environ['tiddlyweb.config'] = self.config
        return self.application(environ, start_response)
