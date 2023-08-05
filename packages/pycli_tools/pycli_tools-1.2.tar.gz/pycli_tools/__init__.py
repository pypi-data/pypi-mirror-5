# -*- coding: utf-8 -*-
"""
pycli_tools is a python module that wraps the ArgumentParser class from
the build-in argparse module.
If you use it in your command line scripts you will get some defaults
options added to your application such as --verbose and --quiet to
control the verbosity of your application (using the python logging
module).  Also there is the --config option that gives you the ability
to read command line arguments from a configuration file to save users
of your application a lot of typing

Copyright (c) 2013 Nico Di Rocco.
License: MIT (see LICENSE for details)
"""

import logging
import sys
from os import path

from argparse import ArgumentParser



__version__ = '1.2'
__author__ = 'Nico Di Rocco'
__license__ = 'MIT'

log = logging.getLogger(__name__)


class SuperArgParser(ArgumentParser):
    remaining_args = None
    _parser_defaults = None

    def parse_args(self, *args, **kwargs):
        if self._parser_defaults:
            self.set_defaults(**self._parser_defaults)

        if self.remaining_args:
            return super(SuperArgParser, self).parse_args(self.remaining_args)
        else:
            return super(SuperArgParser, self).parse_args(*args, **kwargs)


def get_main_parser(prog, default_config_file):
    parser = ArgumentParser(prog=prog, add_help=False)
    parser.add_argument('-c', '--config', dest='config_file',
                        help='path to the config file',
                        default=default_config_file)
    parser.add_argument('-v', '--verbose', default=0, action='count',
                        help='output more verbose')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='surpress all output')
    return parser



def parse_config_defaults(parser, section):
    if parser.has_section(section):
        return dict(parser.items(section))
    else:
        log.debug('Section %s not found. Ignoring.', section)
        return {}



def get_argparser(*args, **kwargs):
    prog = kwargs.get('prog')
    version = kwargs.pop('version', '')
    default_config_file = kwargs.pop('default_config', None)

    mainparser = get_main_parser(prog, default_config_file)
    main_args, remaining_args = mainparser.parse_known_args()

    if main_args.quiet:
        loglevel = 100
    else:
        loglevel = max(30 - main_args.verbose * 10, 10)

    logging.basicConfig(level=loglevel, format='%(message)s')

    if main_args.config_file:
        config_file = path.expanduser(main_args.config_file)
    else:
        config_file = None

    if config_file:
        if path.isfile(config_file):
            log.info('Reading default configuration from %s', config_file)
            from ConfigParser import ConfigParser
            config = ConfigParser()
            config.read(config_file)
            default_config = parse_config_defaults(config, prog)
        else:
            log.debug('Ignoring non-existent config file: %s', config_file)
            config = None
            default_config = {}
    else:
        config = None
        default_config = {}


    parser = SuperArgParser(prog=prog, parents=[mainparser])
    parser.remaining_args = remaining_args
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s ' + version)

    default_config['prog'] = prog
    default_config['version'] = version
    default_config['default_config_file'] = default_config_file
    default_config['config_file'] = config_file
    default_config['loglevel'] = loglevel
    default_config['verbose'] = main_args.verbose
    default_config['quiet'] = main_args.quiet
    parser._parser_defaults = default_config

    return parser
