# -*- coding: utf-8 -*-
# Copyright 2012 Rackspace
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
serverherald announces when new Rackspace NextGen cloud server become ACTIVE.
"""
import os
import yaml
import sys
import argparse

import serverherald.notifiers
from serverherald import ServerHerald

""" Want a new notification type?
1. Make a new python file in notifiers/
2. Subclass ServerHeraldNotifyBase
3. Override notify() and validate_config() as needed.
4. Import it notifiers/__init__.py.
5. Add a new notification type keyword by appending to the notifiers dict in
   main()"""


def main():
    description = """serverherald announces when new Rackspace NextGen cloud
server become ACTIVE.
---------------------------------------------------------------------------"""

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-s', '--silent', action='store_true', default=False,
                        help='Run silently, not sending any notification '
                             'emails. Useful for the initial run to build '
                             'a baseline of current servers')
    parser.add_argument('-c', '--config', type=str, default=None,
                        help='Configuration file path')

    args = parser.parse_args()

    # A user can specify a configuration file or we will go hunting for one
    config_file = args.config
    if config_file is None:
        possible_locations = ['serverherald.yaml', '~/.serverherald.yaml',
                              '~/.serverherald/serverherald.yaml',
                              '/etc/serverherald.yaml',
                              '/etc/serverherald/serverherald.yaml']
        for location in possible_locations:
            if os.path.exists(os.path.expanduser(location)):
                config_file = os.path.expanduser(location)
                break

        if config_file is None:
            print 'No configuration file found.'
            sys.exit(1)
    else:
        if not os.path.exists(os.path.expanduser(config_file)):
            print 'Configuration file %s does not exist.' % config_file
            sys.exit(1)

    with open(config_file, 'r') as f:
        config = yaml.load(f)

    if not 'method' in config:
        print '%s does not specify a notification method' % config_file
        sys.exit(1)

    # Dynamically determine the proper class for the notification method
    notifiers = {'smtp': 'ServerHeraldNotifySMTP',
                 'mailgun': 'ServerHeraldNotifyMailgun',
                 'sendgrid': 'ServerHeraldNotifySendgrid',
                 'prowl': 'ServerHeraldNotifyProwl',
                 'webhook': 'ServerHeraldNotifyWebhook',
                 'pagerduty': 'ServerHeraldNotifyPagerduty',
                 'twilio': 'ServerHeraldNotifyTwilio',
                 'nexmo': 'ServerHeraldNotifyNexmo',
                 'pushover': 'ServerHeraldNotifyPushover'}
    notifier = getattr(serverherald.notifiers,
                       notifiers[config['method']])

    herald = ServerHerald(config, notifier=notifier, silent=args.silent)
    try:
        herald.check_servers()
    except KeyboardInterrupt:
        print 'Stopping...'
        herald.logger.warning('Stopped by keyboard interrupt')
        herald.cleanup()

if __name__ == '__main__':
    main()
