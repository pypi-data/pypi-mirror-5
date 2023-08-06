# vim: set fileencoding=utf-8 :
#
# Copyright (c) 2013 Daniel Truemper <truemped at googlemail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
'''The :class:`Environment` is a container for request handlers, managed
objects and other runtime settings as well as the
:class:`tornado.web.Application` settings.

There are two cases where you will need to work with the it: during the
bootstrapping phase you may change paths to look for configuration files and
you will add the request handlers to the environment.  In addition to that you
can also use it from within a request handler in and access managed objects,
such as HTTP clients that can be used accross a number of client libraries for
connection pooling, e.g.
'''
from __future__ import absolute_import, division, print_function, with_statement

from collections import namedtuple
import logging

from tornado.web import Application as _TAPP


__all__ = ['Environment']


Handler = namedtuple('Handler', ['host_pattern', 'path', 'handler_class',
                                 'init_dict', 'name'])


class Application(_TAPP):
    '''Overwrite :class:`tornado.web.Application` in order to give access to
    environment and configuration instances.'''

    def __init__(self, environment, config, **kwargs):
        '''Initialize the tornado Application and add the config and
        environment.
        '''
        self.environment = environment
        self.config = config
        super(Application, self).__init__(**kwargs)


class Environment(object):
    '''Environment for **supercell** processes.
    '''

    def __init__(self):
        '''Initialize the handlers and health checks variables.'''
        self._handlers = []
        self._managed_objects = {}
        self._health_checks = {}
        self._finalized = False

    def add_handler(self, path, handler_class, init_dict, name=None,
            host_pattern='.*$'):
        '''Add a handler to the :class:`tornado.web.Application`.

        The environment will manage the available request handlers and managed
        objects. So in the :py:func:`Service.run()` method you will add the
        handlers::

            class MyService(s.Service):

                def run():
                    self.environment.add_handler('/', Handler, {})

        :param path: The regular expression for the URL path the handler should
                     be bound to.
        :type path: str or re.pattern

        :param handler_class: The request handler class
        :type handler_class: supercell.api.RequestHandler

        :param init_dict: The initialization dict that is passed to the
                          `RequestHandler.initialize()` method.
        :type init_dict: dict

        :param name: If set the handler and its URL will be available in the
                     `RequestHandler.reverse_url()` method.
        :type name: str

        :param host_pattern: A regular expression for matching the hostname the
                             handler will be bound to. By default this will
                             match all hosts ('.*$')
        :type host_pattern: str
        '''
        assert not self._finalized, 'Do not change the environment at runtime'
        handler = Handler(host_pattern=host_pattern, path=path,
                          handler_class=handler_class, init_dict=init_dict,
                          name=name)
        self._handlers.append(handler)

    def add_managed_object(self, name, instance):
        '''Add a managed instance to the environment.

        A managed object is identified by a name and you can then access it
        from the environment as an attribute, so in your request handler you
        may::

            class MyService(s.Service):

                def run(self):
                    managed = HeavyObjectFactory.get_heavy_object()
                    self.environment.add_managed_object('managed', managed)

            class MyHandler(s.RequestHandler):

                def get(self):
                    self.environment.managed

        :param name: The managed object identifier
        :type name: str

        :param instance: Some arbitrary instance
        :type instance: object
        '''
        assert not self._finalized
        assert name not in self._managed_objects
        self._managed_objects[name] = instance

    def _finalize(self):
        '''When called it is not possible to add more managed objects.

        When the `Service.main()` method starts, it will call `_finalize()`
        in order to not be able to change the environment with respect to
        managed objects and request handlers.'''
        self._finalized = True

    def __getattr__(self, name):
        '''Retrieve a managed object from `self._managed_objects`.'''
        if name not in self._managed_objects:
            raise AttributeError('%s not a managed object' % name)
        return self._managed_objects[name]

    def add_health_check(self, name, check):
        '''Add a health check to the API.

        :param name: The name for the health check to add
        :type name: str

        :param check: The request handler performing the health check
        :type check: A :class:`supercell.api.RequestHandler`
        '''
        assert not self._finalized
        assert name not in self._health_checks
        self._health_checks[name] = check

    @property
    def health_checks(self):
        '''Simple property access for health checks.'''
        return self._health_checks

    @property
    def config_file_paths(self):
        '''The list containing all paths to look for config files.

        In order to manipulate the paths looked for configuration files just
        manipulate this list::

            class MyService(s.Service):

                def bootstrap(self):
                    self.environment.config_file_paths.append('/etc/myservice/')
                    self.environment.config_file_paths.append('./etc/')
        '''
        if not hasattr(self, '_config_file_paths'):
            self._config_file_paths = []
        return self._config_file_paths

    @property
    def tornado_settings(self):
        '''The dictionary passed to the :class:`tornado.web.Application`
        containing all relevant tornado server settings.'''
        if not hasattr(self, '_tornado_settings'):
            self._tornado_settings = {}
        return self._tornado_settings

    def _application(self, config):
        '''Create the tornado application.

        :param config: The configuration that will be added to the app
        '''
        if not hasattr(self, '_app'):
            self._app = Application(self, config,
                                    **self.tornado_settings)

            for handler in self._handlers:
                self._app.add_handlers(handler.host_pattern,
                                            [(handler.path,
                                                handler.handler_class,
                                                handler.init_dict)])
        return self._app

    @property
    def config_name(self):
        '''Determine the configuration file name for the machine this
        application is running on.

        The filenames are generated using a combination of username and
        machine name. If you deploy the application as user **webapp** on host
        **fe01.local.dev** the configuration name would be
        **webapp_fe01.local.dev.cfg**.
        '''
        if not hasattr(self, '_config_name'):
            import getpass
            import socket
            self._config_name = '%s_%s.cfg' % (getpass.getuser(),
                                               socket.gethostname())
        return self._config_name

    def get_logger(self, name):
        '''Get a logger with the given name.'''
        logger = logging.getLogger(name)
        return logger
