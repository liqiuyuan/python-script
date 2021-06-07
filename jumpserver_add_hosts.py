#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import requests
import json
import logging
import sys
import time

day_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
logging.basicConfig(
    filename='jms_jenkins_batch_add_fail.log',
    level=logging.INFO,
    format='%(asctime)s %(message)s')


# 获取token
def get_token(jms_host):
    url = '%s/api/v1/authentication/auth/' % (jms_host)
    query_args = {
        "username": "admin",
        "password": "xxxxxxx"
    }
    response = requests.post(url, data=query_args)
    return json.loads(response.text)['token']


# 获取user_info
def get_user_info(token, jms_host):
    header_info = {"Authorization": 'Bearer ' + token}
    url = '%s/api/v1/assets/assets/' % (jms_host)
    response = requests.get(url, headers=header_info)
    print(json.loads(response.text))


# 获取admin_user_id
def get_admin_user(token, jms_host, name):
    header_info = {"Authorization": 'Bearer ' + token}
    url = '%s/api/v1/assets/admin-users/' % (jms_host)
    response = requests.get(url, headers=header_info)
    for i in json.loads(response.text):
        if i['name'] == name:
            return i['id']

# 获取网域id


def get_domains_id(token, jms_host, domain_name):
    header_info = {"Authorization": 'Bearer ' + token}
    url = '%s/api/v1/assets/domains/' % (jms_host)
    response = requests.get(url, headers=header_info)
    for i in response.json():
        if i['name'] == domain_name:
            return i['id']

# 获取admin_node_id


def get_node(token, jms_host, node):
    header_info = {"Authorization": 'Bearer ' + token}
    url = '%s/api/v1/assets/nodes/' % (jms_host)
    response = requests.get(url, headers=header_info)
    for i in json.loads(response.text):
        if i['full_value'].replace(' ', '') == str(node):
            return i['id']


# 新增资产
def assent_add(token, jms_host, assets, ip):
    r_headers = {'Content-Type': 'application/json',
                 'Accept': 'application/json',
                 'Authorization': 'Bearer %s' % (token)}
    r_uri = '%s/api/v1/assets/assets/' % (jms_host)
    gg = requests.post(r_uri, headers=r_headers, data=json.dumps(assets))
    if gg.status_code == 200 or gg.status_code == 201:
        print('*[sucess] %s' % ip)
    else:
        print('*[fail] %s' % ip)
        logging.info('%s' % (json.dumps(assets)))


jms_host = 'http://172.16.100.239:8080'
token = get_token(jms_host)
host_list = sys.argv[1].split(',')
admin_user = get_admin_user(token, jms_host, sys.argv[2])
admin_user_display = sys.argv[2]
node = get_node(token, jms_host, sys.argv[3])


for h in host_list:
    data = [
        dict(
            hostname=h,
            ip=h,
            protocols=['ssh/22'],
            is_active=True,
            admin_user=admin_user,
            admin_user_display=admin_user_display,
            platform='Linux',
            nodes=[node],
        )
    ]
    assent_add(token, jms_host, data, h)
