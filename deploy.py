#!/usr/bin/env python
# -*- coding: utf-8 -*-
#@Time: 2018/3/12 19:50
#@Authore : gzq
#@File: deploy.py
import os
import sys
import string
import psutil
import re
import signal

def getPid(serverName):
    for pid in psutil.pids():
        p = psutil.Process(pid)
        #print p.name()
        if p.name() == serverName:
            print "Pid:%s,PidName:%s " % (pid,p.name())
            return pid
    print "Not Find Servername:%s" % serverName
    return None

def kill(pid):
    try:
       # a = os.kill(pid, signal.SIGKILL)
        a = os.kill(pid,9)
        #a = os.kill(pid, signal.9) #　与上等效
        print '已杀死pid为%s的进程,　返回值是:%s' % (pid, a)
    except OSError, e:
        print '没有如此进程!!!'
        sys.exit()

if __name__ == "__main__":

    pid = getPid(serverName="cmd.exe")
    kill(pid)


   # print p