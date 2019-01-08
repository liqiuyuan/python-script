#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import MySQLdb

"""
脚本连接数据库构建如下主机组
{
    "all": {
        "children": [
            "GS",
            "LS"
        ]
    },
    "GS": {
        "hosts": [
            "gs1",
            "gs2"
        ]
    },
    "_meta": {
        "hostvars": {
            "gs1": {
                "ansible_ssh_host": "192.168.33.10"
            },
            "gs2": {
                "ansible_ssh_host": "192.168.33.11"
            },
            "ls": {
                "ansible_ssh_host": "192.168.1.3"
            }
        }
    },
    "LS": {
        "hosts": [
            "ls"
        ]
    }
}
"""


def dynamic_inventory(conn):
    """
    build hostinfo json from mysql
    """
    inventory = {'all': {'children': []}, '_meta': {'hostvars': {}}}

    cur = conn.cursor()
    cur.execute("SELECT server_purpose, server_name, private_addr FROM polls_server")
    for row in cur.fetchall():
        # ansible all groups
        if row[0] not in inventory['all']['children']:
            inventory['all']['children'].append(row[0])
        # ansilbe hosts alias name in groups
        inventory.setdefault(row[0], {}).setdefault('hosts', []).append(row[1])
        # ansilbe hosts ip variable
        inventory['_meta']['hostvars'].setdefault(row[1], {}).setdefault('ansible_ssh_host', row[2])

    cur.close()

    print(json.dumps(inventory, indent=4))


if __name__ == '__main__':
    con = MySQLdb.connect(host='192.168.33.10', port=3306, user='root', passwd='123.com', db='mysite')
    dynamic_inventory(con)
