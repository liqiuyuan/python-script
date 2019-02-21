#!/usr/bin/env python
# -*- coding: utf8 -*-
# ansible 自定义模块

import sys
import json
import os
import commands
from ansible.module_utils.basic import *
from novaclient.v1_1 import client


def main():
    module = AnsibleModule(
        argument_spec=dict(
            username=dict(default='admin', type='str'),
            password=dict(default='password', type='str'),
            tenant=dict(default='admin.', type='str'),
            authurl=dict(default='http://127.0.0.1/v2.0', type='str')
        ),
        supports_check_mode=True
    )

    USER, PASS, TENANT, AUTH_URL = (module.params['username'], module.params['password'], module.params['tenant'], module.params['authurl'])
    openstack = client.Client(USER, PASS, TENANT, AUTH_URL, service_type="compute")

    ips = []
    for i in openstack.floating_ips.list():
        if i.fixed_ip is None:
            ips.append(i.ip)
    floating_ip = str(ips[0])

    if not floating_ip:
        print(json.dumps({
            "failed": True,
            "msg": "not have floating_ip"
        }))
        sys.exit(1)
    print(json.dumps({
        "res": floating_ip,
        "changed": True
    }))
    sys.exit(0)


main()
