# coding=utf-8
#
# pyb_init - pybuilder project initialization
#
# Copyright (C) 2013 Maximilien Riehl <maximilien.riehl@gmail.com>
#
#        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.

"""
Usage:
pyb-init local [options]
pyb-init github <user> : <project> [options]
pyb-init git <git_url> [options]
pyb-init (-h | --help)

Options:
-h --help                  Show this screen.
--virtualenv=<name>        Override the virtualenv name [default: venv]
-s --system-site-packages  Use system site packages for virtualenv creation
-p <path> --python=<path>  Do not use the system python interpreter, use <path> instead.
"""
from __future__ import absolute_import
__version__ = '0.1.18'

import logging
from docopt import docopt
from pyb_init import reactor
from pyb_init.configuration import set_configuration

logger = logging.getLogger('pyb_init')
logging.basicConfig(format='%(asctime)s | %(levelname)s - %(message)s')


def entry_point():
    parsed_command_line = docopt(doc=__doc__, version=__version__)
    try:
        set_configuration(parsed_command_line['--virtualenv'],
                          parsed_command_line.get('--system-site-packages', False),
                          parsed_command_line.get('--python', None))
        task_reactor = None
        if parsed_command_line['local']:
            task_reactor = reactor.for_local_initialization()
        if parsed_command_line['github']:
            task_reactor = reactor.for_github_clone(user=parsed_command_line['<user>'],
                                                    project=parsed_command_line['<project>'])
        if parsed_command_line['git']:
            task_reactor = reactor.for_git_clone(git_url=parsed_command_line['<git_url>'])

        for task in task_reactor.get_tasks():
            task.execute()
    except Exception as exception:
        logger.error(str(exception))
