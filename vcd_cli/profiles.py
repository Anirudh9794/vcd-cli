# vCloud CLI 0.1
#
# Copyright (c) 2014 VMware, Inc. All Rights Reserved.
#
# This product is licensed to you under the
# Apache License, Version 2.0 (the "License").
# You may not use this product except in compliance with the License.
#
# This product may include a number of subcomponents with
# separate copyright notices and license terms. Your use of the source
# code for the these subcomponents is subject to the terms and
# conditions of the subcomponent's license, as noted in the LICENSE file.
#

import click
import json
import os
import traceback
import yaml

PROFILE_PATH = '~/.vcd-cli.yaml'

class Profiles(object):

    def __init__(self):
        self.path = None
        self.data = None

    @staticmethod
    def load(path=PROFILE_PATH):
        profile_path = os.path.expanduser(path)
        p = Profiles()
        p.data = {'active': None}
        try:
            with open(profile_path, 'r') as f:
                p.data = yaml.load(f)
        except:
            pass
            # logger.error(traceback.format_exc())
        p.path = profile_path
        return p

    def save(self):
        try:
            stream = file(self.path, 'w')
            yaml.dump(self.data, stream, default_flow_style=False)
        except:
            pass
            # logger.error(traceback.format_exc())

    def update(self, host, org, user, token, api_version, wkep, verify,
               disable_warnings, debug, name='default'):
        if self.data is None:
            self.data = {}
        if 'profiles' not in self.data:
            self.data['profiles'] = []
        profile = {}
        profile['name'] = str(name)
        profile['host'] = str(host)
        profile['org'] = str(org)
        profile['user'] = str(user)
        profile['token'] = str(token)
        profile['api_version'] = str(api_version)
        profile['verify'] = verify
        profile['debug'] = debug
        profile['disable_warnings'] = disable_warnings
        profile['wkep'] = wkep
        tmp = [profile]
        for p in self.data['profiles']:
            if p['name'] != name:
                tmp.append(p)
        self.data['profiles'] = tmp
        self.data['active'] = str(name)
        self.save()

    def get(self, prop, name='default'):
        value = None
        for p in self.data['profiles']:
            if p['name'] == name:
                value = p[prop]
        return value

    def set(self, prop, value, name='default'):
        value = None
        for p in self.data['profiles']:
            if p['name'] == name:
                p[prop] = value
                self.save()
                break
