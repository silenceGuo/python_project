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

import os

def getPid(serverName):
    # python 方式获取 服务名称或者进程名字的pid
    for pid in psutil.pids():
        p = psutil.Process(pid)
        #print p.name()
        if p.name() == serverName:
            print "Pid:%s,PidName:%s " % (pid, p.name())
            return pid
    print "Not Find Servername:%s" % serverName
    #return None

def kill(pid):
    try:
       # a = os.kill(pid, signal.SIGKILL)
        a = os.kill(pid,9)
        #a = os.kill(pid, signal.9) #　与上等效
        print'已杀死pid为%s的进程,　返回值是:%s' % (pid, a)
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

import time
from functools import wraps

def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %s seconds" %
               (function.func_name, str(t1-t0))
               )
        return result
    return function_timer

@fn_timer
def test():
    a = 43.85
    # a = 54.64
    import itertools
    import time
    list1 = [28.77, 24.45, 15.08, 11.20, 11.82, 11.39, 8.91, 9.06, ]#12.57, 13.91,14.41, 14.20]
    #list1 = [28.77,24.45,15.08,]
    tot = 0
    list2 = []
    for i in xrange(1, len(list1) + 1):
        iter = itertools.permutations(list1, i)
        # print iter
        list2.append(list(iter))
        # print list(iter)
        time.sleep(1)
    #print  list2
    for i in list2:
        for j in i:
            #print j
            for t in j:
                tot = tot +t
            #print tot
            if tot == a:
                print j
                sys.exit(1)
            else:
                pass
import sys

def writeLog(log_file, loginfo):
    # 写日志函数
    if not os.path.exists(log_file):
        tot = 0
        print "%s" % log_file
        with open(log_file, 'w+') as fd:
            fd.write(loginfo)
    else:
        with open(log_file, 'w+')as fd:
            fd.write(loginfo)
if __name__ == "__main__":
    log_file = "D:\\tag.txt"
    loginfo = sys.argv[1]
    # import multiprocessing
    # for i in xrange(2):
    #    p = multiprocessing.Process(target=test)  # 进程实现
    # p.start()
    writeLog(log_file, loginfo)
   # # pid = getPid(serverName="cmd.exe")
   #  pid = getPid(serverName="upload")
   #  #kill(pid)
   #  TestPlatform()
   #  UsePlatform()


