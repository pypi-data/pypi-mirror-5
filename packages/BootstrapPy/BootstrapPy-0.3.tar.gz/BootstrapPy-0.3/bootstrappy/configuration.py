"""
    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    Software distributed under the License is distributed on an "AS IS"
    basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
    License for the specific language governing rights and limitations
    under the License.

    The Original Code is BootstrapPy.

    The Initial Developer of the Original Code is Noel Morgan,
    Copyright (c) 2012 Noel Morgan. All Rights Reserved.

    http://www.bootstrappy.org/

    You may not remove or alter the substance of any license notices (including
    copyright notices, patent notices, disclaimers of warranty, or limitations
    of liability) contained within the Source Code Form of the Covered Software,
    except that You may alter any license notices to the extent required to
    remedy known factual inaccuracies.
"""
import copy
import logging
import os
import sys

from paste.config import DispatchingConfig
from paste.deploy.converters import asbool
from webhelpers.mimehelper import MIMETypes

config = DispatchingConfig()

sys.setrecursionlimit(1500)


class BootstrapPyConfig(dict):
    '''Pylonsish/pastish config for global vars, setting up beaker cache, and
    environment defaults.
    '''

    defaults = {
            'debug': False,
            'bootstrappy.package': None,
            'bootstrappy.paths': {'root': None,
                             'controllers': None,
                             'templates': [],
                             'static': None},
            'bootstrappy.environ_config': dict(session='beaker.session',
                cache='beaker.cache'),
            'bootstrappy.app_globals': None,
            'bootstrappy.h': None,
            'bootstrappy.login_path': None
        }

    def init_defaults(self, global_conf, app_conf, package=None, paths=None):
        conf = global_conf.copy()
        conf.update(app_conf)
        conf.update(dict(app_conf=app_conf, global_conf=global_conf))
        conf.update(self.pop('environment_load', {}))

        if paths:
            conf['bootstrappy.paths'] = paths
        conf['bootstrappy.package'] = package
        conf['debug'] = asbool(conf.get('debug'))

        # Load the MIMETypes with its default types
        MIMETypes.init()

        for key, val in copy.deepcopy(self.defaults).iteritems():
            conf.setdefault(key, val)

        if 'cache_dir' in conf:
            conf.setdefault('beaker.session.data_dir',
                os.path.join(conf['cache_dir'], 'sessions'))
            conf.setdefault('beaker.cache.data_dir',
                os.path.join(conf['cache_dir'], 'cache'))

        conf['bootstrappy.cache_dir'] = conf.pop('cache_dir',
            conf['app_conf'].get('cache_dir'))

        # Save our errorware values
        # Pylons did this nicely... still thinking about it.
        # conf['bootstrappy.errorware'] = errorware

        self.update(conf)


# Push the config object down to the DC
bootstrappy_config = BootstrapPyConfig()
bootstrappy_config.update(copy.deepcopy(BootstrapPyConfig.defaults))
config.push_process_config(bootstrappy_config)