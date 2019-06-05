#!/usr/bin/python3
# -*- coding: utf8 -*-


import os
import sys
import time
import atexit
import signal
import subprocess


class Daemon:
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null', homedir='.', umask='022', verbose=1):
        self.pidfile = pidfile
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.homedir = homedir
        self.umask = umask
        self.verbose = verbose

    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

            # decouple from parent environment
        os.chdir(self.homedir)
        os.setsid()
        os.umask(int(self.umask))

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

            # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()

        with open(self.stdin, 'r') as si:
            os.dup2(si.fileno(), sys.stdin.fileno())
        with open(self.stdout, 'a+') as so:
            os.dup2(so.fileno(), sys.stdout.fileno())
        with open(self.stderr, 'a+') as se:
            os.dup2(se.fileno(), sys.stderr.fileno())

        def sig_handler(signum, frame):
            self.daemon_alive = False

        signal.signal(signal.SIGTERM, sig_handler)
        signal.signal(signal.SIGINT, sig_handler)

        if self.verbose >= 1:
            print('daemon process started ...')

        atexit.register(self.del_pid)
        pid = str(os.getpid())
        with open(self.pidfile, 'w+') as f:
            f.write('%s\n' % pid)

    def getNowTime(self):
        # 获取当前时间
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def get_pid(self):
        try:
            with open(self.pidfile, 'r') as f:
                pid = int(f.read().strip())
        except IOError:
            pid = None
        except SystemExit:
            pid = None
        return pid

    def del_pid(self):
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)

    def start(self, status):
        if self.verbose >= 1:
            print('ready to starting ......')
        # check for a pid file to see if the daemon already runs
        pid = self.get_pid()
        if pid:
            msg = 'pid file %s already exists, is it already running?\n'
            sys.stderr.write(msg % self.pidfile)
            sys.exit(1)
        # start the daemon
        self.daemonize()
        self.startProgram(status)

    def stop(self):
        if self.verbose >= 1:
            print('stopping ...')
        pid = self.get_pid()
        if not pid:
            msg = 'pid file [%s] does not exist. Not running?\n' % self.pidfile
            sys.stderr.write(msg)
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)
            return
        # try to kill the daemon process
        try:
            i = 0
            while True:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
                i = i + 1
                if i % 10 == 0:
                    os.kill(pid, signal.SIGHUP)
        except OSError as err:
            err = str(err)
            if err.find('No such process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err))
                sys.exit(1)
            if self.verbose >= 1:
                print('Stopped!')

        # stop app
        self.stopPrograme()

    def restart(self):
        self.stop()
        self.start(True)


    def is_running(self):
        pid = self.get_pid()
        # print(pid)
        return pid and os.path.exists('/proc/%d' % pid)

    def startProgram(self, status):
        """NOTE: override the method in subclass"""
        print('base class run()')

    def stopPrograme(self):
        print("stop ")


class AppDaemon(Daemon):

    def __init__(self, name, pidfile, stdin=os.devnull, stdout=os.devnull, stderr=os.devnull, home_dir='.', umask='022', verbose=1):
        Daemon.__init__(self, pidfile, stdin, stdout, stderr, home_dir, umask, verbose)
        self.name = name  # 派生守护进程类的名称

    def startProgram(self,status):
        pass

    def stopPrograme(self):
        pass

if __name__ == '__main__':
    basePath = os.path.dirname(os.path.abspath(__file__))
    appName = os.path.split(basePath)[-1]

    pidfile = '{0}/{1}.pid'.format(basePath, appName)

    logPath = '{}/logs/'.format(basePath)
    logFile = '{}/daemon.log'.format(logPath)

    if not os.path.exists(logPath):
        os.mkdir(logPath)
        if not os.path.exists(logFile):
            os.system('touch {}'.format(logFile))

    daemon = AppDaemon(appName, pidfile, stdout=logFile, stderr=logPath)

    if len(sys.argv) != 2:
        print('Usage: {} [start|stop|restart]'.format(sys.argv[0]))
        raise SystemExit(1)
    elif len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start(True)
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif sys.argv[1] == 'status':
            alive = daemon.is_running()
            if alive:
                print('process [%s] is running ......' % daemon.get_pid())
            else:
                print('daemon process [%s] stopped' % daemon.name)
        else:
            print('unknown command')
            sys.exit(1)
    else:
        print('usage: %s [start|stop|restart]' % sys.argv[0])
        sys.exit(2)
