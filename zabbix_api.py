#!/usr/bin/env python3
# coding=utf-8
from pyzabbix import ZabbixAPI
import os
import sys
import time

basedir = os.path.dirname(os.path.abspath(__file__))
zapi = ZabbixAPI(f"http://ip/")
zapi.login("xxxxx", "xxxx")


def get_host_id(ip):
    # 通过主机IP, 获取主机id
    host_info = zapi.host.get(filter={'ip': ip})
    # hostinfo=zapi.hostinterface.get(output=['hostid'], filter={'ip': ip})
    hostid = host_info[0]['hostid']
    return hostid


def get_group_id(group_name):
    # 通过主机组, 获取组id
    group_info = zapi.hostgroup.get(filter={'name': group_name})
    groupid = group_info[0]['groupid']
    return groupid


def get_template_id(template_name):
    # 通过模板, 获取模板id
    template_info = zapi.template.get(filter={'host': template_name})
    template_id = template_info[0]['templateid']
    return template_id


def clear_template(hostid, templateid):
    # 清除主机模板
    zapi.host.update(hostid=hostid, templates_clear={"templateid": templateid})
    print(f'{hostid} clear template {templateid}')


def add_template(hostid, templateid):
    # 主机添加模板
    zapi.template.massadd(templates=templateid, hosts={"hostid": hostid})
    print(f"{hostid} add template {templateid}")


def add_host_to_group(groupid, hostid):
    # 主机加入组
    zapi.hostgroup.massadd({'groups': groupid, 'hosts': hostid})
    print(f'{hostid} add group {groupid}')


def delete_host(hostid):
    # zabbix中删除主机
    zapi.host.delete(hostid)
    print(f'delete host: {hostid}')


def disable_host(hostid):
    # zabbix中禁用主机
    zapi.host.update(status=1, hostid=hostid)
    print(f'disable {hostid}')


def enable_host(hostid):
    # zabbix中启用主机
    zapi.host.update(status=0, hostid=hostid)
    print(f'disable {hostid}')


#获取所有主机IP
# hosts = zapi.hostinterface.get()
# for i in hosts:
#     print(i['ip'])

old_template = 'Template OS Linux by Zabbix agent'
old_template_id = get_template_id(old_template)
new_template = 'Template OS Linux by Zabbix agent-p2'
new_template_id = get_template_id(new_template)

# 获取主机组下的主机ID
# hostinfo = zapi.hostgroup.get(filter={'groupid': 23}, selectHosts=['hostid'])
# for i in hostinfo[0]['hosts']:
#     hostid = i['hostid']
#     clear_template(hostid, old_template_id)
#     time.sleep(1)
#     add_template(hostid, new_template_id)

# hosts = zapi.host.get(selectInterfaces=[ "ip" ])
# for i in hosts:
#     print(i['interfaces'][0]['ip'])

if __name__ == '__main__':
    iplist = sys.argv[1].split(',')
    for hostip in iplist:
        try:
            hostid = get_host_id(hostip)
            delete_host(hostid)
        except BaseException as e:
            print(e)

    # with open(f'{basedir}/hostlist.txt', 'r') as f:
    #     content = f.readlines()
    # for line in content:
    #     hostip = line.split('\n')[0]
    #     try:
    #         hostid = get_host_id(hostip)
    #         delete_host(hostid)
    #     except BaseException as e:
    #         print(e)
