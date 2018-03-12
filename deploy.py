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
        #print("pid-%d,pname-%s" % (pid, p.name()))
        if p.name() == serverName:
            print pid,p.name()
            return pid
def kill(pid):

    try:
        a = os.kill(pid, signal.SIGKILL)
        #a = os.kill(pid, signal.9) #　与上等效
        print '已杀死pid为%s的进程,　返回值是:%s' % (pid, a)
    except OSError, e:
        print '没有如此进程!!!'

if __name__ == "__main__":
    #main(sys.argv)
    getPid(serverName="cmd.exe")
    kill(6964)
    # p = psutil.Process()


   # print p