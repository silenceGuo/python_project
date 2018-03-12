#!/usr/bin/env python
# -*- coding: utf-8 -*-
#@Time: 2018/3/12 19:50
#@Authore : gzq
#@File: deploy.py
import os
import sys
import string
import psutil
import platform
import signal

def getPid(serverName):
    # python 方式获取 服务名称或者进程名字的pid
    for pid in psutil.pids():
        p = psutil.Process(pid)
        #print p.name()
        if p.name() == serverName:
            print "Pid:%s,PidName:%s " % (pid,p.name())
            return pid
    print "Not Find Servername:%s" % serverName
    #return None

def kill(pid):
    try:
       # a = os.kill(pid, signal.SIGKILL)
        a = os.kill(pid,9)
        #a = os.kill(pid, signal.9) #　与上等效
        print '已杀死pid为%s的进程,　返回值是:%s' % (pid, a)
    except OSError, e:
        print '没有如此进程!!!'
        sys.exit()

def TestPlatform():
    print ("----------Operation System--------------------------")
    #Windows will be : (32bit, WindowsPE)
    #Linux will be : (32bit, ELF)
    print(platform.architecture())

    #Windows will be : Windows-XP-5.1.2600-SP3 or Windows-post2008Server-6.1.7600
    #Linux will be : Linux-2.6.18-128.el5-i686-with-redhat-5.3-Final
    print(platform.platform())

    #Windows will be : Windows
    #Linux will be : Linux
    print(platform.system())

    print ("--------------Python Version-------------------------")
    #Windows and Linux will be : 3.1.1 or 3.1.3
    print(platform.python_version())

def UsePlatform():
  sysstr = platform.system()
  if(sysstr =="Windows"):
    print ("Call Windows tasks")
  elif(sysstr == "Linux"):
    print ("Call Linux tasks")
  else:
    print ("Other System tasks")

if __name__ == "__main__":

    pid = getPid(serverName="cmd.exe")
    #kill(pid)
    TestPlatform()


   # print p