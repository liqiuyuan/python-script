#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
@file: all_server_restart.py
@time: 2017/4/24 9:54
"""
# 多线程重启游戏服
# 传一个整数,且小于（sid总数/分组）个线程
import json
import re
import paramiko
import urllib
import threading
from datetime import datetime
import time
import logging
import sys
import signal


# 登录服务器IP或者域名
ls_ip = '10.27.97.23'
ssh_port = 22

privatekey = '/home/support/.ssh/id_rsa'
key = paramiko.RSAKey.from_private_key_file(privatekey)

# loger
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] [%(threadName)s] %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')

handler = logging.FileHandler("all_server_restart.log")
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)

logger.addHandler(handler)
logger.addHandler(console)


def getSid():
    # 通过登录服务器serverlist获取需要重启的服务器id列表
    res = urllib.urlopen('http://{0}/serverlist/server_cfg.json'.format(ls_ip))
    response = res.read()
    responseJSON = json.loads(response)
    server_list = responseJSON['server_list']

    sid = []
    for line in server_list:
        gameid = int(line['id'])
        ip = re.findall(r'(\d+.\d+.\d+.\d+)', line['tcp'])
        port = re.findall(r'([0-9]{5})', line['tcp'])
        # 列表转字符串
        ip = "".join(ip)
        port = "".join(port)
        serverid = int(port) - 20000
        # 避免合服区服重启多次
        if gameid == serverid:
            sid.append(serverid)
        else:
            continue
    return sid


# 按照步长(服务器id)均分列表,即分组长度
def listGroups(init_list, childern_list_len):
    listGroups = zip(*(iter(init_list),) *childern_list_len)
    end_list = [list(i) for i in listGroups]
    count = len(init_list) % childern_list_len
    end_list.append(init_list[-count:]) if count != 0 else end_list
    # 将[[1, 2, 3], [4, 5]] 转为[(1, 4), (2, 5), (3, None)]类型
    return map(None, *end_list)


class ParakimoClient:

    def __init__(self, hostname, username, port, privatekey):
        self.hostname = hostname
        self.username = username
        self.port = port
        self.privatekey = privatekey
        self.pkey = paramiko.RSAKey.from_private_key_file(self.privatekey)
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        try:
            self.ssh.connect(hostname=self.hostname,
                             username=self.username,
                             port=self.port,
                             pkey=self.pkey)
        except Exception as e:
            logger.error(e, exec_info=True)
            self.ssh.close()

    def run_cmd(self, cmd_str, timeout):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(cmd_str, timeout)
            for line in stdout:
                print(line.strip("\n"))
        except Exception as e:
            logger.error('commnad:%s failed！ reason: %s' % (cmd_str, e), exc_info=True)
            self.ssh.close()


def restartGameServer(sid, ip_id):
    for gs in ip_id:
        if gs.endswith(str(sid)):
            gs_ip = gs.split(':')[0]
            gs_sid = gs.split(':')[1][4:]
            # 避免1、11服因为sid都以1结尾，游戏服会重启多次
            if int(gs_sid) == int(sid):
                sshclient = ParakimoClient(hostname=gs_ip, username='support', port=ssh_port, privatekey=privatekey)
                sshclient.connect()
                try:
                    command = '''
                    source /home/support/rsync_install/gs/java_profie.txt;
                    cd /data/game{0};
                    chmod +x *.py;
                    ./hoserver.py restart;
                    '''.format(str(sid))
                    starttime = datetime.now()
                    logger.info('Starting >>> restart IP:{0} game{1}'.format(gs_ip, sid))
                    sshclient.run_cmd(command)
                    endtime = datetime.now()
                    logger.info("Exiting >>> IP:{0} game{1} restart success! Take time {2}s!".format(gs_ip, sid, (endtime - starttime).seconds))
                except Exception as e:
                    logging.error(e)
                    sys.exit(-1)


def quit(signum, frame):
    print('You choose to stop me.')
    sys.exit()


if __name__ == "__main__":
    # 通过gs.conf 获取游戏服内网IP和sid
    new_gs = []
    with open('/home/support/rsync_game/gs.conf', 'r') as f:
        content = f.readlines()
        for gs in content:
            if gs.startswith('#'):
                continue
            else:
                gs_list = re.findall(r'(\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\:game\d+\b)', gs)
                gs_list = "".join(gs_list)
                new_gs.append(gs_list)

    gs_sid = getSid()

    if int(sys.argv[1]):
        # 按照子分组长度分组
        if 20 >= int(sys.argv[1]) > 1:
            gs_sid = listGroups(gs_sid, int(sys.argv[1]))

            logger.info("Begin to restart all game server!")
            logger.info("The SID group like: %s" % gs_sid)
            for i in gs_sid:
                # 线程池
                threadspool = []
                try:
                    signal.signal(signal.SIGINT, quit)
                    signal.signal(signal.SIGTERM, quit)
                    for j in i:
                        if not j:
                            continue
                        else:
                            th = threading.Thread(target=restartGameServer, args=(j, new_gs))
                            threadspool.append(th)

                    for th in threadspool:
                        th.start()
                        time.sleep(0.3)

                    for th in threadspool:
                        th.join()

                    while True:
                        pass
                except Exception as exc:
                    print(exc)
            logger.info("the all game server restart success!")
        else:
            print('Parameter error！Incoming parameter is not int')

