#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
@file: hoserver.py
@time: 2017/10/22 15:58
"""

import os
import sys
import time
import commands
import socket
import re
from datetime import datetime

# 后台程序监控游戏服时间间隔
sleeptime = 300

# basedir = os.path.abspath('.')
basedir = os.path.dirname(os.path.realpath(__file__))
# 游戏服jar包
main_program = '%s/HTGame.jar' % basedir
# 游戏服启动脚本
main_daemon = os.path.realpath(__file__)
# 游戏服配置文件
CONFFILE = '%s/config.prop' % basedir

def getCmd():
    # 启动参数，如果存在游戏目录存在javaopt.conf，则java参数从这个文件获取
    # 否则从javaop.py读取，主要是中心服java参数
    if os.path.exists('%s/javaopt.conf' % basedir):
        with open('%s/javaopt.conf' % basedir, 'r') as f:
            content = f.read()
            JAVA_OPTS = re.match('JAVA_OPTS\s*=\s*\"(.+)\"', content).group(1)
            # JAVA_OPTS = ''.join(re.findall(r'(?<=").*?(?=")', content))
            # 游戏服启动命令
            cmd = """cd {0};
                  source /etc/profile;
                  export LD_LIBRARY_PATH={0};
                  nohup java {1} -jar {2} -config {3} 1>>{0}/tmp.log 2>>{0}/tmp_error.log & """.format(
                basedir, JAVA_OPTS, main_program, CONFFILE)
            return cmd
    else:
        # 游戏服启动命令
        JAVA_OPTS = "-Xms256m -Xmx4096m -XX:MaxNewSize=1024m -XX:PermSize=128m -XX:MaxPermSize=256m"
        JAVA_OPTS += " -Xloggc:gc.log"
        JAVA_OPTS += " -XX:+PrintGCTimeStamps"
        JAVA_OPTS += " -XX:+PrintGCDetails"
        JAVA_OPTS += " -verbose:gc"
        cmd = """cd {0};
              source /etc/profile;
              export LD_LIBRARY_PATH={0};
              nohup java {1} -jar {2} -config {3} 1>>{0}/tmp.log 2>>{0}/tmp_error.log & """.format(
            basedir, JAVA_OPTS, main_program, CONFFILE)
        return cmd


def getNowTime():
    # 获取当前时间
    result = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return result


def getProgramPid():
    # 获取游戏进程pid
    result = commands.getoutput("ps aux | grep %s | grep -v grep | awk '{print $2}'" % main_program)
    return result


def getDaemonPid():
    # 获取守护进程pid
    result = commands.getoutput("ps aux | grep python \
        | grep '%s monitor' | grep -v grep | awk '{print $2}'" % main_daemon)
    return result


def getPortStatus():
    # 获取游戏服端口状态
    with open('%s' % CONFFILE, 'r') as f:
        content = f.readlines()
    for line in content:
        if line.startswith('server.tcpAddr'):
            port = int(line.split(':')[1])
            ip = line.split('=')[1].split(':')[0]
            if ip == '0':
                sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sk.connect(('127.0.0.1', port))
                    sk.shutdown(2)
                    return True
                except Exception as e:
                    print(e)
                    return False
            else:
                sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sk.connect((ip, port))
                    sk.shutdown(2)
                    return True
                except Exception as e:
                    print(e)
                    return False


def startProgram(status):
    # 启动游戏服
    # status为Ture 游戏服启动时检查端口信息，为Flase则不检查端口信息
    p_pid = getProgramPid()
    if p_pid != '':
        print('%s It seems %s program is already running...' % (getNowTime(), main_program))
        sys.exit()
    else:
        print('\033[1;32;40m %s Starting program %s \033[0m' % (getNowTime(), main_program))
        try:
            if os.system(getCmd()) == 0:
                p_pid = getProgramPid()
                # 检查游戏服端口状态
                if status:
                    while True:
                        if getPortStatus():
                            print('\033[1;32;40m %s start program %s successfully and pid is %s \033[0m' % (getNowTime(), main_program, p_pid))
                            break
                        else:
                            print('\033[1;34;40m waiting for port ready..... \033[0m')
                            time.sleep(1)
        except Exception as e:
            print(e)


def startDaemon():
    # 启动守护进程
    d_pid = getDaemonPid()
    if d_pid != '':
        print(' %s It seems this daemon is already running...' % getNowTime())
    else:
        print('Starting daemon...')
        try:
            if os.system('nohup /usr/bin/python -u %s monitor >> %s/logs/daemon.log 2>&1 &' % (main_daemon, basedir)) == 0:
                print('%s start daemon successfully and pid is %s' % (getNowTime(), getDaemonPid()))
        except Exception as e:
            print(e)


def stopProgram():
    # 停止游戏进程
    p_pid = getProgramPid()
    if p_pid == '':
        print('%s It seems %s was down...' % (getNowTime(), main_program))
    else:
        if os.system('kill -15 ' + p_pid) == 0:
            print('\033[1;33;40m %s %s program stopped \033[0m' % (getNowTime(), main_program))
        else:
            print('\033[1;33;40m %s stop %s failed, will be kill enforced!!!!!!! \033[0m' % (getNowTime(), main_program))
            os.system('kill -9 ' + p_pid)


def stopDaemon():
    # 停止守护进程
    d_pid = getDaemonPid()
    if d_pid == '':
        print('It seems daemon is not running...')
    else:
        os.system('kill -9 ' + d_pid)
        print('Stopped daemon...')


def monitor():
    # 监控游戏进程
    while True:
        time.sleep(sleeptime)
        p_pid = getProgramPid()
        if p_pid == '':
            print('%s It seems %s game program is not running. Start it now!' % (getNowTime(), main_program))
            startProgram(False)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        args = sys.argv[1]
    else:
        args = input('Enter args: ')

    # 后台程序日志
    logPath = os.path.curdir + os.sep + 'logs'
    if not os.path.exists(logPath):
        os.mkdir(logPath)

    if args == 'start':
        startProgram(True)
        startDaemon()
    elif args == 'stop':
        stopDaemon()
        stopProgram()
    elif args == 'restart':
        stopDaemon()
        stopProgram()
        time.sleep(3)
        startProgram(True)
        startDaemon()
    elif args == 'monitor':
        monitor()
    else:
        print('usage: %s (start|stop|restart)' % os.path.basename(__file__))
