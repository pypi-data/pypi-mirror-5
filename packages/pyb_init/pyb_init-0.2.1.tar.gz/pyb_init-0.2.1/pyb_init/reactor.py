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

from __future__ import absolute_import
import os

from pyb_init.tasks import ShellCommandTask, PreconditionTask
from pyb_init.vcs_tools import determine_project_name_from_git_url, determine_project_name_from_svn_url
from pyb_init.configuration import configuration


def for_local_initialization():
    reactor = TaskReactor()
    _add_common_tasks(reactor=reactor, command_prefix=None)
    return reactor


def for_github_clone(user, project):
    git_url = 'https://github.com/{0}/{1}'.format(user, project)
    return for_git_clone(git_url)


def for_svn_checkout(svn_url):
    reactor = TaskReactor()
    reactor.ensure_command_callable('svn')
    reactor.add_task(ShellCommandTask('svn checkout {0}'.format(svn_url)))
    project = determine_project_name_from_svn_url(svn_url)
    _add_common_tasks(reactor, 'cd {0} && '.format(project), project)
    return reactor


def for_git_clone(git_url):
    reactor = TaskReactor()
    reactor.ensure_command_callable('git')
    reactor.add_task(ShellCommandTask('git clone {0}'.format(git_url)))
    project = determine_project_name_from_git_url(git_url)
    _add_common_tasks(reactor=reactor,
                      command_prefix='cd {0} && '.format(project),
                      project=project)
    return reactor


def _add_common_tasks(reactor, command_prefix, project=None):
    _add_preconditions(reactor, project)
    virtualenv_name = configuration['virtualenv_name']
    virtualenv_command = _apply_configuration(virtualenv_name)
    commands = [virtualenv_command,
                'source {0}/bin/activate && pip install pybuilder'.format(virtualenv_name),
                'source {0}/bin/activate && pyb install_dependencies'.format(virtualenv_name),
                'source {0}/bin/activate && pyb -v'.format(virtualenv_name)]

    if command_prefix:
        expanded_commands = [command_prefix + command for command in commands]
    else:
        expanded_commands = commands
    for command in expanded_commands:
        reactor.add_task(ShellCommandTask(command))


def _apply_configuration(virtualenv_name):
    virtualenv_command = 'virtualenv {0} --clear'.format(virtualenv_name)
    virtualenv_command = _add_system_site_packages_switch_if_necessary(virtualenv_command)
    virtualenv_command = _add_python_interpreter_switch_if_necessary(virtualenv_command)
    return virtualenv_command


def _add_system_site_packages_switch_if_necessary(virtualenv_command):
    if configuration['virtualenv_use_system_site_packages']:
        virtualenv_command += ' --system-site-packages'
    return virtualenv_command


def _add_python_interpreter_switch_if_necessary(virtualenv_command):
    if configuration['virtualenv_path_to_python_interpreter']:
        virtualenv_command += ' -p {0}'.format(configuration['virtualenv_path_to_python_interpreter'])
    return virtualenv_command


def _add_preconditions(reactor, project):
    if project:
        reactor.add_task(PreconditionTask(lambda: os.path.exists('{0}/build.py'.format(project)),
                                          'Build descriptor ({0}/build.py) should exist'.format(project)))
    else:
        reactor.add_task(PreconditionTask(lambda: os.path.exists('build.py'),
                                          'Build descriptor (build.py) should exist'))

    reactor.ensure_command_callable('virtualenv')


class TaskReactor(object):

    def __init__(self):
        self.tasks = []

    def get_tasks(self):
        return self.tasks

    def add_task(self, task):
        self.tasks.append(task)

    def ensure_command_callable(self, command):
        command_available_if_0 = ShellCommandTask('command -v {0} > /dev/null 2>&1'.format(command),
                                                  ignore_failures=True).execute
        self.add_task(PreconditionTask(
            lambda: command_available_if_0() == 0,
            '{0} should be installed and callable'.format(command)))
