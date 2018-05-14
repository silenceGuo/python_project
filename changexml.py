#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Author : gzq
# @date   : 2018/5/14 0014 10:33
# @file   : changexml.py

import xml.dom.minidom
import os
import sys
import codecs
# 读取xml 配置文件
path = "D:\\logs\\SVN-maven"
changfile = "ehcache.xml"
fileType = "ehcache.xml"
changxmlname = "accessTokenCache"
list = []
def listDir(path):
    #list = []
    lsdir = os.listdir(path)
    dirs = [i for i in lsdir if os.path.isdir(os.path.join(path, i))]
    files = [i for i in lsdir if os.path.isfile(os.path.join(path, i))]
    if files:
        for f in files:
            if f == changfile:
                list.append(os.path.join(path, f))
    if dirs:
        for d in dirs:
            listDir(os.path.join(path, d))
    return list

def readXml(serverName):
    xmlPath = os.path.join(deploymentTomcatName(serverName), "conf/server.xml")
    domtree = xml.dom.minidom.parse(xmlPath)
    collection = domtree.documentElement
    service = collection.getElementsByTagName("Service")
    shutdown_port = str(collection.getAttribute("port"))  # shutdown port
    for i in service:
        connector = i.getElementsByTagName("Connector")
        http_port = str(connector[0].getAttribute("port"))  # http port
        ajp_port = str(connector[1].getAttribute("port"))  # ajp port
        # URIEconding= str(connector[0].getAttribute("URIEconding"))  # http port
    return {serverName: {"shutdown_port": shutdown_port, "http_port": http_port, "ajp_port": ajp_port}}

# 修改xml 配置文件
def changeXml(xmlpath,selection,attribute):
    xmlpath ="D:\\logs\\SVN-maven\\ybdev\\activity-oss\\sys4.0\\ehcache.xml"
    #xmlpath = os.path.join(deploymentTomcatName(serverName), "conf/server.xml")
    print xmlpath
    domtree = xml.dom.minidom.parse(xmlpath)
    #print domtree
    collection = domtree.documentElement
    #print collection
    caches = collection.getElementsByTagName("cache")
    for cache in caches:
        if cache.hasAttribute("name") :
            if cache.getAttribute("name") == changxmlname:
                print cache.getAttribute("name")
                print cache.getAttribute("maxElementsInMemory")
            #print cache.setAttribute("name","test")

            #cache.
    #print cache
    #collection.setAttribute("port", shutdown_port)  # shutdown port
    # URIEconding = "UTF-8"
    # useBodyEncodingForURI = "true"
    # for i in service:
    #     #print i
    #     connector = i.getElementsByTagName("Connector")
    #     appdeploy = i.getElementsByTagName("Host")
    #     appdeploy[0].setAttribute("appBase", deploydir) #部署目录 默认为webapps
    #     connector[0].setAttribute("port", http_port)  # http port
    #     #connector[0].setAttribute("URIEnconding", "UTF-8")  # http port
    #     #connector[0].setAttribute("proxyPort", "443")  #proxyPort
    #     # connector[0].setAttribute("useBodyEncodingForURI", "true")  # http port
    #     #connector[1].setAttribute("port", ajp_port)  # ajp port

    # outfile = file(xmlpath, 'w')
    # write = codecs.lookup("utf-8")[3](outfile)
    # domtree.writexml(write, addindent=" ", encoding='utf-8')
    # write.close()
xmlpath,selection,attribute = "","",""
changeXml(xmlpath,selection,attribute)