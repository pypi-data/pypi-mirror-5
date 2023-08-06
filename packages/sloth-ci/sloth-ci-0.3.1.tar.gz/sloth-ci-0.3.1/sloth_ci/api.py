"""
************
sloth_ci.api
************

This module implements the sloth API.
"""


from importlib import import_module

from argparse import ArgumentParser

import cherrypy
from configs import load

from .sloth import Sloth


def make_listener(sloth):

    @cherrypy.expose
    def listener(*args, **kwargs):
        """Listens to requests.

        :param payload: payload
        """

        sloth.logger.info('Payload received from %s - %s' % (cherrypy.request.headers['Remote-Addr'], cherrypy.request.headers['User-Agent']))

        try:
            validator = import_module(
                '.validators.%s' % sloth.config['provider'],
                package=__package__
            )
        except ImportError as e:
            sloth.logger.critical('No matching validator found: %s' % e)
            raise cherrypy.HTTPError(500)

        payload_valid, validation_message, params = validator.validate(cherrypy.request, sloth.config['provider_data'])

        sloth.logger.info(validation_message.format_map(params))

        if not payload_valid:
            raise cherrypy.HTTPError(400)

        if not sloth.is_queue_locked():
            sloth.queue.append(params)

    return listener


def run(host, port, log_dir, sloths):
    """Runs CherryPy loop to listen for payload."""


    from os.path import abspath, join

    cherrypy.config.update(
        {
            'server.socket_host': host,
            'server.socket_port': port,
            'log.access_file': abspath(join(log_dir, 'access.log')),
            'log.error_file': abspath(join(log_dir, 'error.log'))
        }
    )

    for sloth in sloths:
        cherrypy.tree.mount(make_listener(sloth), sloth.config['listen_to'])

        sloth.logger.info('Mounted at %s' % sloth.config['listen_to'])

        cherrypy.engine.autoreload.files.add(sloth.config.config_full_path)

        cherrypy.engine.subscribe('stop', sloth.stop)

    cherrypy.engine.start()
    cherrypy.engine.block()


def main():
    """Main API function"""

    parser = ArgumentParser()
    parser.add_argument('--sconfig')
    parser.add_argument('--host')
    parser.add_argument('--port', type=int)
    parser.add_argument('--log_dir')
    parser.add_argument('config', nargs='+')

    parsed_args = parser.parse_args()

    sconfig_file = parsed_args.sconfig
    sconfig = load(sconfig_file)

    host = parsed_args.host or sconfig.get('host')
    port = parsed_args.port or sconfig.get('port')
    log_dir = parsed_args.log_dir or sconfig.get('log_dir')

    config_files = parsed_args.config

    sloths = [Sloth(load(config_file, defaults={'log_dir': log_dir})) for config_file in config_files]

    if not (host or port or log_dir):
        raise RuntimeError('Missing server param.')

    run(host, port, log_dir, sloths)
