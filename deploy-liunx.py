#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Author : gzq
# @date   : 2018/1/10 0010 16:30
# @file   : deploy-liunx.py

from subprocess import PIPE, Popen
import time
import os
import sys
import xml.dom.minidom
import signal
import codecs
import shutil
import zipfile
#import shlex
#import paramiko
#import SSH
import time
import ConfigParser

reload(sys)
sys.setdefaultencoding('utf-8')
serverConf = "server_liunx.conf" # 部署配置文件
jenkinsUploadDir = "/home/jenkinsUpload/"  # jenkins 上传基础目录
#jenkinsUploadDirBak = "/home/jenkinsUploadBak/"  # 打包上传的目录备份
#deploymentDirBak = "/home/deployDirBak/"
deploymentDir = "/home/deployDir/"  # 目录存放war包
deploymentAppSerDir = "/home/serverApp/"  # 部署工程目录存放tomcat
baseTomcat = "/home/apache-tomcat-7.0.64-/"
tomcatPrefix = "apache-tomcat-7.0.64-"

def _init():
    # 初始化基础目录
    if not os.path.exists(jenkinsUploadDir):
        os.makedirs(jenkinsUploadDir)
    if not os.path.exists(deploymentDir):
        os.makedirs(deploymentDir)
    if not os.path.exists(deploymentAppSerDir):
        os.makedirs(deploymentAppSerDir)
    if not os.path.exists(baseTomcat):
        print "Base tomcat File (%s) is not exists" % baseTomcat
        sys.exit()

def joinPathName(serverPath, serverName, *args):
    # 目录拼接　
    return os.path.join(serverPath, serverName, *args)  # % (baseDeploymentName, serverName)

def copyFile(sourfile,disfile):
    try:
        print "copy file:%s,to:%s" % (sourfile, disfile)
        shutil.copy2(sourfile, disfile)  # % ( disfile, time.strftime("%Y-%m-%d-%H%M%S"))
    except Exception, e:
        print e,
        sys.exit(1)

def reName():
    pass

def sendWarToNode(ip, serverName):
    loaclPath = os.path.join(jenkinsUploadDir, serverName)
    remotePath = os.path.join(jenkinsUploadDir, serverName)
    cmd = "scp  -C %s/ROOT.war  root@%s:%s/ROOT.war" % (loaclPath, ip, remotePath)
    execSh(cmd)

    # time.sleep(30)
def getPid(servername):
    deploymentPath = joinPathName(deploymentAppSerDir,"%s%s") % (tomcatPrefix, servername)
    #cmd = "pgrep -f %s" % servername
    cmd = "pgrep -f %s" % deploymentPath
    pid, stderr = execSh(cmd)
    if pid:
        #string(pid,)
        print "Get PID:%s" %pid
        return int(pid)

def execSh(cmd):
    # 执行SH命令
    try:
        print "exec ssh command %s" % cmd
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    except Exception, e:
        print e,
        sys.exit()
    return p.communicate()

def stopServe(serverName):
    pid = getPid(serverName)
    if pid:
        try:
            a = os.kill(pid, signal.SIGKILL)
            # a = os.kill(pid, signal.9) #　与上等效
            print 'Killed server:%s, pid:%s,reutrun code:%s' % (serverName, pid, a)
        except OSError, e:
            print 'No such as server!', e
           # sys.exit()

def stopMain(serverName):
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    serverConfPath = os.path.join(dirname, serverConf)
    if serverName:
        stopServe(serverName)
    else:
        serverNameList = readConf(serverConfPath)
        for serverNameDict in serverNameList:
            for serverName, portDict in serverNameDict.iteritems():
                if serverName == "conf":
                    # 如果是conf 的就略过，下一个服务，conf 是做为配置文件的配置
                    continue
                stopServe(serverName)

# 发布服务
def update(serverName):
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    serverConfPath = os.path.join(dirname, serverConf)
    war = readConf(serverConfPath,serverName)[serverName]["war"]
    deployWarPath = joinPathName(deploymentDir, "tomcat-%s/webapps/ROOT.war") % serverName
    deployWarPathRoot = joinPathName(deploymentDir, "tomcat-%s/webapps/ROOT") % serverName
    jenkinsUploadDirWar = joinPathName(jenkinsUploadDir,"%s") % war
    if os.path.exists(deployWarPath):
        backWar(serverName)
    copyFile(jenkinsUploadDirWar, deployWarPath)
    if serverName == "upload":
        cleanCachUpload(deployWarPathRoot)
    else:
        if os.path.exists(deployWarPathRoot):
            shutil.rmtree(deployWarPathRoot)
    unzipWar(deployWarPath, deployWarPathRoot)

def updateMain(serverName):
    # 更新新版本并
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    serverConfPath = os.path.join(dirname, serverConf)
    if serverName:
        stopServe(serverName)
        update(serverName)
        startMain(serverName)
    else:
        serverNameList = readConf(serverConfPath)
        for serverNameDict in serverNameList:
            for serverName, portDict in serverNameDict.iteritems():
                if serverName == "conf":
                    # 如果是conf 的就略过，下一个服务，conf 是做为配置文件的配置
                    continue
                stopServe(serverName)
                update(serverName)
                startMain(serverName)

def startServer(serverName):
    startSh = joinPathName(deploymentAppSerDir, "%s%s", "bin/startup.sh") % (tomcatPrefix,serverName)
    binDir = joinPathName(deploymentAppSerDir, "%s%s", "bin/*") % (tomcatPrefix,serverName)
    deployDir = joinPathName(deploymentAppSerDir, "%s%s") % (tomcatPrefix,serverName)
    deployWarPathRoot = joinPathName(deploymentDir, "tomcat-%s/webapps/ROOT") % serverName
    #cmd = "su - tomcat %s" %startSh
    chmodCmd = "chmod 755 -R %s" % binDir
    chmodCmd2 = "chmod 755 -R %s" % deployDir
    chmodCmd3 = "chmod 755 -R %s" % deployWarPathRoot
    chownCmd = "chown -R tomcat:tomcat %s" % deployDir
    chownCmd2 = "chown -R tomcat:tomcat %s" % binDir
    chownCmd3 = "chown -R tomcat:tomcat %s" % deployWarPathRoot


    # 授权
    #print "chmod dir 755 %s" % binDir
    execSh(chmodCmd)
    execSh(chmodCmd2)
    execSh(chmodCmd3)
    # 更改所属 组
    execSh(chownCmd)
    execSh(chownCmd2)
    execSh(chownCmd3)
    cmd = "su - tomcat %s" % startSh
   # "su - tomcat /usr/local/tomcat7_$element/bin/startup.sh"
    #cmd = "nohup %s &" % startSh
    """         chown -R tomcat:tomcat /usr/local/tomcat7_$element
                chown -R tomcat:tomcat /home/wwwroot/xhw-$element
                chmod -R 755 /usr/local/tomcat7_$element/bin/*
                chmod -R 755 /home/wwwroot/xhw-$element
    """
    if not getPid(serverName):
        print "Start Server:%s" % serverName
        execSh(cmd)
    time.sleep(10)
    if getPid(serverName):
        print "Server:%s,Sucess pid:%s" % (serverName, getPid(serverName))
    else:
        print "Server:%s,is not running" % serverName

def startMain(serverName):
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    serverConfPath = os.path.join(dirname, serverConf)
    if serverName:
        startServer(serverName)
    else:
        serverNameList = readConf(serverConfPath)
        for serverNameDict in serverNameList:
            for serverName, portDict in serverNameDict.iteritems():
                if serverName == "conf":
                    # 如果是conf 的就略过，下一个服务，conf 是做为配置文件的配置
                    continue
                startServer(serverName)

def cleanCachUpload(path):
    # 针对 upload 服务清除缓存，因为 上传的图片是软连接到其他目录的
    list = ["WEB-INF","META-INF","css","images","js","upload","index.jsp","crossdomain.xml"]
    for i in list:
        f = os.path.join(path,i)
        if os.path.exists(f):
            print "Clean %s" %f
            if os.path.isfile(f):
                # 删除文件
                os.remove(f)
            # 删除目录
            else:
                shutil.rmtree(f)
# 清除部署工程目录
def cleanDeployDir(serverName):
    deploymentAppPath = os.path.join(deploymentAppSerDir,"%s%s") % (tomcatPrefix,serverName)
    try:
        shutil.rmtree(deploymentAppPath)
        print "clean %s" % deploymentAppPath
    except Exception, e:
        print e
        sys.exit()

def unzipWar(zipfilePath,unzipfilepath):
    f = zipfile.ZipFile(zipfilePath, 'r')
    print 'unzip file:%s >>>>>>to:%s' % (zipfilePath, unzipfilepath)
    for file in f.namelist():
        f.extract(file, unzipfilepath)

def copyBaseTomcat(serverName):
    deploymentDirTmp = joinPathName(deploymentAppSerDir,"%s%s") % (tomcatPrefix,serverName)
    try:
        print "copy BaseTomcat Dir :%s to:%s" % (baseTomcat, deploymentDirTmp)
        shutil.copytree(baseTomcat, deploymentDirTmp)
    except Exception, e:
        print e, "dir is exists！"
        sys.exit(1)

# 修改xml 配置文件
def changeXml(serverName,shutdown_port="8128",http_port="8083",ajp_port="8218"):
    deploymentDirTmp = joinPathName(deploymentAppSerDir, "%s%s") % (tomcatPrefix, serverName)
    deploydir = joinPathName(deploymentDir,"%s%s","webapps")% ("tomcat-",serverName)
    xmlpath = os.path.join(deploymentDirTmp, "conf/server.xml")
    # print xmlpath
    domtree = xml.dom.minidom.parse(xmlpath)
    collection = domtree.documentElement
    service = collection.getElementsByTagName("Service")
    collection.setAttribute("port", shutdown_port)  # shutdown port
    for i in service:
        connector = i.getElementsByTagName("Connector")
        appdeploy = i.getElementsByTagName("Host")
        appdeploy[0].setAttribute("appBase", deploydir) #部署目录 默认为webapps
        connector[0].setAttribute("port", http_port)  # http port
        connector[1].setAttribute("port", ajp_port)  # ajp port
    outfile = file(xmlpath, 'w')
    write = codecs.lookup("utf-8")[3](outfile)
    domtree.writexml(write, addindent=" ", encoding='utf-8')
    write.close()
#
# def main(serverName, serverNameWar,**port):
#
#     # 部署tomcat 工程 目录
#     deploymentAppDir = joinPathName(deploymentAppSerDir, "%s%s") % (tomcatPrefix, serverName)
#
#     # 部署的war包
#     deployRootWar = joinPathName(deploymentDir, "tomcat-%s", "ROOT.war") % serverName
#     deployRoot = joinPathName(deploymentDir, "tomcat-%s") % serverName
#
#     if not os.path.exists(deployRoot):
#         os.makedirs(deployRoot)
#     # 备份war包路径
#     bakdeployRootWar = joinPathName(deploymentDirBak, serverName, "ROOT.%s.war") % (time.strftime("%Y-%m-%d-%H%M%S"))
#     bakdeployRoot = joinPathName(deploymentDirBak, serverName)
#
#     # jenkins 上传目录
#     if not os.path.exists(joinPathName(jenkinsUploadDir,serverName)):
#         os.makedirs(joinPathName(jenkinsUploadDir,serverName))
#
#     uploadDeployWar = joinPathName(jenkinsUploadDir,serverName, serverNameWar)
#     # 部署路径
#     deployDir = joinPathName(deploymentDir, "tomcat-%s", "ROOT/") % serverName
#     # 备份原部署文件
#     if not os.path.exists(bakdeployRoot):
#         # 创建备份目录
#         print "creat bak dir"
#         os.makedirs(bakdeployRoot)
#     if os.path.exists(deployRootWar):
#         print "bak war"
#         copyFile(deployRootWar, bakdeployRootWar)
#     # 部署新的工程目录
#     if not os.path.exists(deploymentAppDir):
#         print "init deployment dir"
#         os.makedirs(deploymentAppSerDir)
#         copyBaseTomcat(serverName)
#         changeXml(serverName, **port)
#     # 复制新war包到部署目录
#     copyFile(uploadDeployWar, deployRootWar)
#     stopServer(serverName)
#     # 清理部署工程缓存 针对upload特殊处理 除resouces 其他都清理，resouces是软连接 到其他目录的
#     if serverName == "upload":
#         cleanCachUpload(deployDir)
#     else:
#         if os.path.exists(deployDir):
#             shutil.rmtree(deployDir)
#     unzipWar(deployRootWar, deployDir)
#     startServer(serverName)

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

# 检查工程是否部署
def checkServer(serverName):
    serverNameDeployPath = os.path.join(deploymentAppSerDir,"%s%s") % (tomcatPrefix, serverName)
    #print serverNameDeployPath
    if os.path.exists(serverNameDeployPath):
        return True
    else:
        return False

# 部署针对单个服务的操作 ，且配置文件中存在
def deployForServer(Tag, serverName, portDict):
    shutdown_port = portDict["shutdown_port"]
    http_port = portDict["http_port"]
    ajp_port = portDict["ajp_port"]
    jenkinsUploadDirServer = joinPathName(jenkinsUploadDir,"%s") % serverName
    deployDir = joinPathName(deploymentAppSerDir, "%s%s") % (tomcatPrefix, serverName)  # 部署工程目录
    deployRoot = joinPathName(deploymentDir, "tomcat7-%s", "webapps") % serverName
    bakdeployRoot = joinPathName(deploymentDir, "tomcat7-%s", "bak-tomcat7-%s") % (serverName, serverName)  # 备份目录
    if not os.path.exists(deployRoot):
        os.makedirs(deployRoot)
    if not os.path.exists(bakdeployRoot):
        os.makedirs(bakdeployRoot)
    if not os.path.exists(jenkinsUploadDirServer):
        os.makedirs(jenkinsUploadDirServer)

    chownCmd = "chown -R tomcat:tomcat %s" % deployDir
    if Tag == "reinstall":
        # 清理老的部署文件，重新部署
        if checkServer(serverName):
            stopServe(serverName)
            time.sleep(1)
            cleanDeployDir(serverName)
            # 从标准tomcat 复制到部署目录
            copyBaseTomcat(serverName)
            # 修改部署tomcat server.xml配置文件
            changeXml(serverName, shutdown_port=shutdown_port, http_port=http_port, ajp_port=ajp_port)
            execSh(chownCmd)
        else:
            print "%s is not installed" % serverName
            print "First install %s" % serverName
    elif Tag == "install":
        # 检查服务是否注册，
        if not checkServer(serverName):
            # 从标准tomcat 复制到部署目录
            copyBaseTomcat(serverName)
            # 修改部署tomcat server.xml配置文件
            changeXml(serverName, shutdown_port=shutdown_port, http_port=http_port, ajp_port=ajp_port)
            execSh(chownCmd)
            if checkServer(serverName):
                print "server:%s install Sucess" % serverName
            else:
                print "server:%s install Fail" % serverName
        else:
            print "%s is installed" % serverName
    elif Tag == "uninstall":
        if checkServer(serverName):
            stopServe(serverName)
            cleanDeployDir(serverName)  # 清理老的部署文件，注销服务
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
    _init()
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    serverConfPath = os.path.join(dirname, serverConf)
    if not os.path.exists(serverConfPath):
        print "serverconf is not exists,check serverconf %s "% serverConfPath
        print """ %s like this:
                   [servername]
                   http_port = 8810
                   ajp_port = 8820
                   shutdown_port = 8830
                   war = com.hxh.xhw.upload.war""" % serverConf
        sys.exit()
    # 读取配置文件需要部署的服务名，根据设置的端口部署服务
    if serverNAME:
        serverNameDict = readConf(serverConfPath,serverNAME)
        deployForServer(Tag,serverNAME, serverNameDict[serverNAME])
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

def backWar(serverName):
    # 部署的war包
    deployRootWar = joinPathName(deploymentDir, "tomcat-%s", "webapps","ROOT.war") % serverName
    # 备份war包路径
    bakdeployRootWar = joinPathName(deploymentDir, "tomcat-%s","bak-tomcat-%s", "ROOT.%s.war") % (serverName,serverName, time.strftime("%Y-%m-%d-%H%M%S"))
    copyFile(deployRootWar, bakdeployRootWar)

def Main(Tag,serverNAME=""):
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    serverConfPath = os.path.join(dirname, serverConf)
    if not os.path.exists(serverConfPath):
        print "serverconf is not exists,check serverconf %s " % serverConfPath
        print """ %s like this:
                       [servername]
                       http_port = 8810
                       ajp_port = 8820
                       shutdown_port = 8830
                       war = com.hxh.xhw.upload.war""" % serverConf
        sys.exit()
        # 读取配置文件需要部署的服务名，根据设置的端口部署服务
    if Tag == "stop":# 停服务
        stopMain(serverNAME)
    elif Tag == "start": # 启动服务
        startMain(serverNAME)
    elif Tag == "restart": # 重启服务
        stopMain(serverNAME)
        startMain(serverNAME)
        #startServer(serverNAME)
    elif Tag == "update": # 更新发布新版本
        updateMain(serverNAME)
    elif Tag in ["install","uninstall","reinstall"]: # 部署tomcat 环境
        deploy(Tag, serverNAME)

if __name__ == "__main__":
    #
    # servername = sys.argv[1]
    #
    # if server_dict. has_key(servername):
    #     for war,portdict in server_dict[servername].iteritems():
    #         print war,portdict
    #         main(servername,war,**portdict)
    # else:
    #     print "NO such as server，please check:%s" % servername

    # try:
    #     Tag = sys.argv[1]
    #     #servername = sys.argv[2]
    # except:
    #     print "follow"
    #     sys.exit()
    # if len(sys.argv) == 2:
    #     Tag = sys.argv[1]
    #     Main(Tag)
    # elif len(sys.argv) == 3:
    #     Tag = sys.argv[1]
    #     serName = sys.argv[2]
    #     Main(Tag, serName)
    sendWarToNode("192.168.0.159","upload")

