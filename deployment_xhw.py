#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Author : gzq
# @date   : 2018/1/2 0002 15:45
# @file   : deployment_xhw.py
import shutil
#from xml.etree.ElementTree import ElementTree,Element,parse
import os
import sys
import time

reload(sys)
sys.setdefaultencoding('utf-8')
#from xml.dom.minidom import parse
import xml.dom.minidom
import codecs
import ConfigParser
from subprocess import PIPE,Popen

# # 部署的目录
# deploymentDir = 'D:\\programfiles\\application\\'
# # 部署目录的前缀
# baseDeploymentName = "apache-tomcat-7.0.64-"
# # 基础tomcat
# baseTomcat = "D:\\programfiles\\apache-tomcat-7.0.64-\\"

# 默认部署工程目录，默认是webapps
deploydir = "webapps"
#部署服务和端口配置文件 server.conf
serverConf = "server.conf"
# 启动服务顺序配置文件
serverStartConf = "serverStart.conf"

# 返回部署工程的目标目录
def deploymentTomcatName(serverName):
    return os.path.join(deploymentDir, "%s%s") % (baseDeploymentName, serverName)

# 从基础tomcat复制到目标工程目录
def copyBaseTomcat(serverName):
    try:
        shutil.copytree(baseTomcat, deploymentTomcatName(serverName))
    except Exception, e:
        print e, "目标目录异常！"
        sys.exit(1)

def cleanFile(serverName):
        path = os.path.join(baseTomcat, deploymentTomcatName(serverName))
        print path
        if os.path.exists(path):
            print "Clean %s" % path
            if os.path.isfile(path):
                # 删除文件
                os.remove(path)
            # 删除目录
            else:
                shutil.rmtree(path)
# 读取xml 配置文件
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
def changeXml(serverName,shutdown_port,http_port,ajp_port):
    xmlpath = os.path.join(deploymentTomcatName(serverName), "conf/server.xml")
    print xmlpath
    domtree = xml.dom.minidom.parse(xmlpath)
    collection = domtree.documentElement
    service = collection.getElementsByTagName("Service")
    collection.setAttribute("port", shutdown_port)  # shutdown port
    # URIEconding = "UTF-8"
    # useBodyEncodingForURI = "true"
    for i in service:
        #print i
        connector = i.getElementsByTagName("Connector")
        appdeploy = i.getElementsByTagName("Host")
        appdeploy[0].setAttribute("appBase", deploydir) #部署目录 默认为webapps
        connector[0].setAttribute("port", http_port)  # http port
        #connector[0].setAttribute("URIEnconding", "UTF-8")  # http port
        #connector[0].setAttribute("proxyPort", "443")  #proxyPort
        # connector[0].setAttribute("useBodyEncodingForURI", "true")  # http port
        connector[1].setAttribute("port", ajp_port)  # ajp port
    outfile = file(xmlpath, 'w')
    write = codecs.lookup("utf-8")[3](outfile)
    domtree.writexml(write, addindent=" ", encoding='utf-8')
    write.close()

# 切换工作目录
def changDir(dirpath):
    os.chdir(dirpath)
# 执行windows 命令
def execCmd(cmd):
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    print 'Eexec CMD :%s' %cmd
    return stdout, stderr

# 注册或注销服务
def installServer(servername, installTag):
    bindir = os.path.join(deploymentTomcatName(servername),'bin') # 组装 TOMCAT bin 目录
    changDir(bindir) # 切换工作目录
    print 'chang workdir %s '% os.getcwd()
    install = "%s/service.bat install %s" % (bindir, servername)
    uninstall = "%s/service.bat uninstall %s" % (bindir, servername)
    if installTag == "install":
        execCmd(install)
    elif installTag == "uninstall":
        execCmd(uninstall)
    else:
        print "install or uninstall servername"
        # 切换工作目录 不然在删除会报错
    changDir(deploymentDir)

# 检查服务是否pid
def getPid(servername):
    cmd = "sc queryex %s" % servername
    stdout, stderr = execCmd(cmd)
    if "EnumQueryServicesStatus:OpenService" in stdout.split(" "):
        #print 'service name is not install'
        return False
    try:
        #print [i.strip() for i in stdout.split('\n') if i.strip().split(":")][1:]
        pid = [i.strip() for i in stdout.split('\n') if i.strip()][8].split(":")[1].strip()
       #pid = [i.strip() for i in stdout.split('\n') if i.strip().split(":")][8].split(":")[1].strip()
    except:
        print 'sc query fail %s is not exists' % servername
        return False
    print 'net_pid :', pid
    if pid:
        return pid

def checkServer(servername):
    # 检查服务是否注册
    cmd = "sc queryex %s" % servername
    stdout, stderr = execCmd(cmd)
    if "EnumQueryServicesStatus:OpenService" in stdout.split(" "):
        return False
    return True

def stopServerName(servername):
    #停止服务
    pid = getPid(servername)
    #print "ss",pid
    if pid:
        cmd_task_kill = "taskkill /F /pid %s" % pid
        stdout, stderr = execCmd(cmd_task_kill)
        print "kill %s,%s" % (servername, pid)
        pid = getPid(servername)
        if not pid:
            print 'kill service:%s sucees' % servername
            return True
        else:
            return False
    else:
        print "service:%s stop sucess!" % servername
        return True

def startServerName(servername,filename):
    # 启动服务
    call_bat = 'cmd.exe /c %s' % filename
    print 'call bat %s' % filename
    # stdout, stderr = exe_cmd_ssh(ssh, call_bat)
    stdout, stderr =execCmd(call_bat)
    if filename in stdout:
        print 'bat name is err'
        sys.exit(1)

def conn(ip, username, passwd,):
        # ssh连接函数
        import paramiko
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, 22, username, passwd, timeout=5)
            print "Connect to ", ip, " with ", username
            global curr_prompt
            curr_prompt = username + "@" + ip + ">>"
            return ssh
        except:
            print "Connect fail to ", ip, " with ", username
            sys.exit(1)

def exe_cmd_ssh(ssh, cmd):
        # ssh连接成功，执行cmd命令
        if (ssh == None):
            print "Didn't connect to a server. Use '!conn' to connect please."
            return
        try:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout = stdout.read()
            stderr = stderr.read()
            print 'out:', stdout
            print 'err:', stderr
            return stdout, stderr
        except:
            print 'command is err'
            sys.exit(1)

def writeLog(log_file,loginfo):
    # 写日志函数
    if not os.path.exists(log_file):
        print log_file
        with open(log_file, 'w+') as fd:
            fd.write(loginfo)
    else:
        with open(log_file, 'w+')as fd:
            fd.write(loginfo)

#读取配置文件和启动服务文件设置需要部署的服务以及设置服务顺序 默认读取配置文件部署所有服务，
def readConf(confPath,serverNAME=""):
    cf = ConfigParser.ConfigParser()
    cf.read(confPath)
    serverNameDict = {}
    serverNameList = []
    portDict = {}
    if serverNAME:
        try:
            cf.options(serverNAME)
        except Exception, e:
            print e
            print "serverName:%s server is not exists" %serverNAME
            sys.exit(1)
        for optins in cf.options(serverNAME):
            port = cf.get(serverNAME, optins)
            portDict[optins] = port
        serverNameDict[serverNAME] = portDict
        return serverNameDict
    else:
        for serverName in cf.sections():
            #print 'serverName:%s' % serverName
            for optins in cf.options(serverName):
                # 取服务名下的对应的配置和参数
                port = cf.get(serverName, optins)
                portDict[optins] = port
            serverNameDict[serverName] = portDict
            serverNameList.append(serverNameDict)
            #print serverNameDict
            portDict={}
            serverNameDict ={}
        return serverNameList

# 部署针对单个服务的操作 ，且配置文件中存在
def deployForServer(Tag,serverName,portDict):
    shutdown_port = portDict["shutdown_port"]
    http_port = portDict["http_port"]
    ajp_port = portDict["ajp_port"]
    if Tag == "reinstall":
        # 清理老的部署文件，重新部署
        if checkServer(serverName):
            stopServerName(serverName)
            time.sleep(1)
            cleanFile(serverName)
            # 从标准tomcat 复制到部署目录
            copyBaseTomcat(serverName)
            # 修改部署tomcat server.xml配置文件
            changeXml(serverName, shutdown_port=shutdown_port, http_port=http_port, ajp_port=ajp_port)
            # 检查服务是否注册，
        if not checkServer(serverName):
            installServer(serverName, 'uninstall')
            installServer(serverName, 'install')
        else:
            print "%s is installed" % serverName
    elif Tag == "install":
        # 检查服务是否注册，
        if not checkServer(serverName):
            # 从标准tomcat 复制到部署目录
            copyBaseTomcat(serverName)
            # 修改部署tomcat server.xml配置文件
            changeXml(serverName, shutdown_port=shutdown_port, http_port=http_port, ajp_port=ajp_port)
            installServer(serverName, 'install')
            if checkServer(serverName):
                print "server:%s install Sucess" % serverName
            else:
                print "server:%s install Fail" % serverName
        else:
            print "%s is installed" % serverName
    elif Tag == "uninstall":
        if checkServer(serverName):
            stopServerName(serverName)
            installServer(serverName, 'uninstall')
            cleanFile(serverName)  # 清理老的部署文件，注销服务
            if not checkServer(serverName):
                print "server:%s uninstall Sucess" % serverName
            else:
                print "server:%s uninstall fail" % serverName
        else:
            print "server:%s not install!" % serverName
    else:
        pass

#部署主函数 配置文件所有的服务部署
def deploy(Tag,serverNAME=""):
    serverConfPath = os.path.join(os.getcwd(),serverConf)
    #print serverConfPath
    if not os.path.exists(serverConfPath):
        print "serverconf is not exists,check serverconf %s "% serverConfPath
        print """ %s like this:
                   [servername]
                   http_port = 8810
                   ajp_port = 8820
                   shutdown_port = 8830""" % serverConf
        sys.exit()
    # 读取配置文件需要部署的服务名，根据设置的端口部署服务
    if serverNAME:
        serverNameDict = readConf(serverConfPath,serverNAME)
        deployForServer(Tag,serverNAME, serverNameDict[serverNAME])
        # shutdown_port = serverNameDict[serverNAME]["shutdown_port"]
        # http_port = serverNameDict[serverNAME]["http_port"]
        # ajp_port = serverNameDict[serverNAME]["ajp_port"]
        sys.exit()
    serverNameList = readConf(serverConfPath)
    #print serverNameList
    for serverNameDict in serverNameList:
        # print serverNameDict
        for serverName, portDict in serverNameDict.iteritems():
            if serverName == "conf":
                # 如果是conf 的就略过，下一个服务，conf 是做为配置文件的配置
                continue
            deployForServer(Tag,serverName,portDict)
            # shutdown_port = portDict["shutdown_port"]
            # http_port = portDict["http_port"]
            # ajp_port = portDict["ajp_port"]
            # if Tag == "reinstall":
            #     #清理老的部署文件，重新部署
            #     if checkServer(serverName):
            #          stopServerName(serverName)
            #          time.sleep(1)
            #          cleanFile(serverName)
            #          # 从标准tomcat 复制到部署目录
            #          copyBaseTomcat(serverName)
            #          # 修改部署tomcat server.xml配置文件
            #          changeXml(serverName, shutdown_port=shutdown_port, http_port=http_port, ajp_port=ajp_port)
            #          # 检查服务是否注册，
            #     if not checkServer(serverName):
            #         installServer(serverName, 'uninstall')
            #         installServer(serverName, 'install')
            #     else:
            #         print "%s is installed" %serverName
            # elif Tag =="install":
            #     # 检查服务是否注册，
            #     if not checkServer(serverName):
            #         # 从标准tomcat 复制到部署目录
            #         copyBaseTomcat(serverName)
            #         # 修改部署tomcat server.xml配置文件
            #         changeXml(serverName, shutdown_port=shutdown_port, http_port=http_port, ajp_port=ajp_port)
            #         installServer(serverName, 'install')
            #         if checkServer(serverName):
            #             print "server:%s install Sucess" % serverName
            #         else:
            #             print "server:%s install Fail" % serverName
            #     else:
            #         print "%s is installed" % serverName
            # elif Tag == "uninstall":
            #     if checkServer(serverName):
            #         stopServerName(serverName)
            #         installServer(serverName, 'uninstall')
            #         cleanFile(serverName) # 清理老的部署文件，注销服务
            #         if not checkServer(serverName):
            #             print "server:%s uninstall Sucess" % serverName
            #         else:
            #             print "server:%s uninstall fail" % serverName
            #     else:
            #         print "server:%s not install!" % serverName
            # else:
            #     pass

# 初始化 读取配置文件配置部署目录和基础部署文件的设置
def _init():
    #serverConfPath = os.path.join(os.getcwd(), serverConf)
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    serverConfPath = os.path.join(dirname, serverConf)
    serverConfList = readConf(serverConfPath)
    _serverConf = serverConfList[0]
    deploymentDir = _serverConf["conf"]["deploymentdir"]
    baseDeploymentName = _serverConf["conf"]["basedeploymentname"]
    baseTomcat = _serverConf["conf"]["basetomcat"]
    # serverConf = _serverConf["conf"]["serverConf"]
    return deploymentDir, baseDeploymentName, baseTomcat

def list_dir(path):
    list = os.listdir(path)
    ser_dict = {}
    for i in list:
        if i.startswith("apache-tomcat-7.0.64-"):
            service_name = i.split("apache-tomcat-7.0.64-")[-1]
            service_name_path = os.path.join(path, i)
            ser_dict[service_name] = service_name_path
    return ser_dict

if __name__ == "__main__":
    # 读取配置文件信息
    #print readStartServerConf()
    #print readConf(serverConf)

    deploymentDir, baseDeploymentName, baseTomcat = _init()
    if len(sys.argv) == 2:
        tag = sys.argv[1]
        print tag
        if tag in ["install", "uninstall", "reinstall"]:
            pass
            # deploy(tag)
        else:
            print " only install,uninstall,reinstall"
    elif len(sys.argv) == 3:
        tag = sys.argv[1]
        serverName = sys.argv[2]
        if tag in ["install", "uninstall", "reinstall"]:
            deploy(tag, serverName)
        else:
            print " only install,uninstall,reinstall"
    else:
        print "Follow One agrs,install|uninstall|reinstall"
        print "Follow Two agrs,ServerNAME install|uninstall|reinstall"
        sys.exit()



