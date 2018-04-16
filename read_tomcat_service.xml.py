# -*- coding: UTF-8 -*-
# by gzq
# date :2017/9/13 0013 16:49
import os
import sys
import shutil
#from xml.etree.ElementTree import ElementTree,Element,parse
import os
import sys
#from xml.dom.minidom import parse
import xml.dom.minidom
import codecs
from subprocess import PIPE,Popen
import re
#re_shutdown_
deploymentTomcatName="D:\\programfiles\\application\\"
def read_xml(file):
    if not os.path.exists(file):
        return False
    ser_dict = {}
    with open(file) as fd:
        for i in fd.readlines():
            # print i
            if i.startswith('<Server port='):
                # print i.split("")
                tmp_list = [i.strip() for i in i.split(" ")]
                # print tmp_list
                shutdown_ser = tmp_list[-1].split("=")[0]
                # print shutdown_ser
                shutdown_port = tmp_list[1].split("=")[-1]
                # print shutdown_port
                ser_dict[shutdown_ser] = shutdown_port
            if '<Connector port=' in i:
                tmp_list = [i.strip() for i in i.split(" ") if i][1:]
                # print tmp_list
                if 'protocol="HTTP/1.1"' in tmp_list:
                    ser_dict["HTTP/1.1"] = tmp_list[0].split("=")[-1]
                    # print  ser_dict["HTTP/1.1"]
                if 'protocol="AJP/1.3"' in tmp_list:
                    ser_dict["AJP/1.3"] = tmp_list[0].split("=")[-1]
                    # print ser_dict["AJP/1.3"]
        return ser_dict

def readXml(serverPath):

    xmlPath = os.path.join(serverPath, "conf/server.xml")
    #print xmlPath
    domtree = xml.dom.minidom.parse(xmlPath)
    collection = domtree.documentElement
    service = collection.getElementsByTagName("Service")
    shutdown_port = str(collection.getAttribute("port"))  # shutdown port
    for i in service:
        connector = i.getElementsByTagName("Connector")
        http_port = str(connector[0].getAttribute("port"))  # http port
        #ajp_port = str(connector[1].getAttribute("port"))  # ajp port
        #URIEconding= str(connector[0].getAttribute("URIEconding"))  # http port
    #return {"shutdown_port": shutdown_port, "http_port": http_port, "ajp_port": ajp_port,"URIEconding":URIEconding}
    #return {"shutdown_port": shutdown_port, "http_port": http_port, "ajp_port": ajp_port,}
    return {"shutdown_port": shutdown_port, "http_port": http_port,}

def list_dir(path):
    list = os.listdir(path)
    ser_dict = {}
    for i in list:
        if i.startswith("apache-tomcat-7.0.64-"):
            service_name = i.split("apache-tomcat-7.0.64-")[-1]
            service_name_path = os.path.join(path, i)
            ser_dict[service_name] = service_name_path
    #print ser_dict
    return ser_dict

# F:\gzq\work\application-bak-224\application-bak-224\apache-tomcat-7.0.64-activity-api\conf
def writeLog(log_file,loginfo):
    # 写日志函数
    if not os.path.exists(log_file):
        print log_file
        with open(log_file, 'w+') as fd:
            fd.write(loginfo)
    else:
        with open(log_file, 'w+')as fd:
            fd.write(loginfo)

def main(ser_dir):
    tmp_dict = {}
    for k, v in list_dir(ser_dir).iteritems():
        print k,v
        ser_name = k
        tmp_dict[ser_name] = readXml(v)
        # print
    return tmp_dict

if __name__ == "__main__":
    try:
       ser_dir = sys.argv[1]
    except:
        print "follow a tomcat deployment dir like D:\\programfiles\\application\\"
        sys.exit()
    logfile = "xml.tmp"
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    logPath = os.path.join(dirname, logfile)
    #ser_dir = "D:\\programfiles\\application\\"
    #path = "D:\\logs\\xml13.tmp"
    info = ""
    s= ""
    for k, v in main(ser_dir).iteritems():
        #print k, v
        for i,j in v.iteritems():
           # info += "[%s]\n%s,\n" % (k, v)
            #print k,i,j
            s += "%s = %s\n" %( i,j)
        info += "[%s]\n%swar = \n\n" % (k,s)
        s=""
    writeLog(logPath, info)