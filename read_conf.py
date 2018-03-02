#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Author : gzq
# @date   : 2018/2/28 0028 14:22
# @file   : read_conf.py
import ConfigParser
import os
import sys
#os.chdir("F:\\gzq\python_project")
cf = ConfigParser.ConfigParser()
cf.read("server.conf")
serverNameDict = {}
portDict = {}
for serverName in cf.sections():
    print 'serverName:%s' %serverName
    for optins in cf.options(serverName):
        # 取服务名下的对应的配置和参数
        port = cf.get(serverName, optins)
        print optins,port
        portDict[optins] = port
    serverNameDict[serverName] = portDict
print serverNameDict
#print sys.path()
print os.getcwd()
if os.path.exists(os.path.join(os.getcwd(), "server.conf")):
    print os.path.join(os.getcwd(), "server.conf")
    print "serverconf is not exists,check serverconf"
    print """ moment :
            [servername]
            http_port = 8810
            ajp_port = 8820
            shutdown_port = 8830"""