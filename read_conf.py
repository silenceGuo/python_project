#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Author : gzq
# @date   : 2018/2/28 0028 14:22
# @file   : read_conf.py
import ConfigParser
import os
import sys
#部署服务和端口配置文件 server.conf
serverConf = "server.conf"
def readConf(type):
    import ConfigParser
    cf = ConfigParser.ConfigParser()
    cf.read(serverConf)
    serverNameDict = {}
    portDict = {}
    for serverName in cf.sections():
        #print 'serverName:%s' % serverName
        for optins in cf.options(serverName):
            # 取服务名下的对应的配置和参数
            port = cf.get(serverName, optins)
            portDict[optins] = port
        serverNameDict[serverName] = portDict
        portDict={}
    return serverNameDict

if __name__ == "__main__":
    # if not os.path.exists(os.path.join(os.getcwd(),serverConf)):
    #     print "serverconf is not exists,check serverconf"
    #     print """ %s like this:
    #                [servername]
    #                http_port = 8810
    #                ajp_port = 8820
    #                shutdown_port = 8830""" % serverConf
    #     sys.exit()
    print readConf(type)