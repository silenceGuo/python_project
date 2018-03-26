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
serverConf = "server_liunx.conf"  # 部署配置文件
uploadConf = "upload_liunx.conf"  # 部署配置文件
jenkinsUploadDir = "/home/jenkinsUpload/"  # jenkins 上传基础目录
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

# 上传分发 方法 前提是设置好目标服务器无密码登录
def sendWarToNode(serverName):
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    serverConfPath = os.path.join(dirname, serverConf)
    warName = readConf(serverConfPath, serverName)[serverName]["war"]
    # ipList = [i for i in readConf(serverConfPath, serverName)[serverName]["ip"].split(",") if i]
    try :
        ipList = [i for i in readConf(serverConfPath, serverName)[serverName]["ip"].split(",") if i]
    except:
        print "Check Config File"
        sys.exit()
    loaclPath = os.path.join(jenkinsUploadDir, serverName,warName)
    remotePath = os.path.join(jenkinsUploadDir, serverName)
    if not os.path.exists(remotePath):
        os.mkdir(remotePath)
#    cmd = "scp  -C %s root@%s:%s" % (loaclPath, ip, remotePath)
    if not os.path.exists(loaclPath):
        print " File:%s is not exits" % loaclPath
        sys.exit()
    for ip in ipList:
        cmd = "scp  -C %s root@%s:%s" % (loaclPath, ip, remotePath)
        stdout, stderr = execSh(cmd)
        if stderr:
            print stderr
            print "check local path,or remote path!"
            continue
            #sys.exit(1)
        # time.sleep(30)

def sendWarToNodeMain(serverName):
    ser_list = readConf(serverConf)
    #print ser_list
    if serverName:
        sendWarToNode(serverName)
    else:
        for dict in ser_list:
            for serName, portDict in dict.iteritems():
                print serName
                sendWarToNode(serName)

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
    deployWarPath = joinPathName(deploymentDir, "tomcat7-%s/webapps/ROOT.war") % serverName
    deployWarPathRoot = joinPathName(deploymentDir, "tomcat7-%s/webapps/ROOT") % serverName
    jenkinsUploadDirWar = joinPathName(jenkinsUploadDir,"%s","%s") % (serverName,war)
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
    deployWarPathRoot = joinPathName(deploymentDir, "tomcat7-%s/webapps/ROOT") % serverName
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
    pid = getPid(serverName)
    if not pid:
        print "Start Server:%s" % serverName
        execSh(cmd)
        time.sleep(10)
        if getPid(serverName):
            print "Server:%s,Sucess pid:%s" % (serverName, getPid(serverName))
        else:
            print "Server:%s,is not running" % serverName
    else:
        print "Server:%s,Sucessed pid:%s" % (serverName, pid)

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
def changeXml(serverName,shutdown_port="8128",http_port="8083"):
    deploymentDirTmp = joinPathName(deploymentAppSerDir, "%s%s") % (tomcatPrefix, serverName)
    deploydir = joinPathName(deploymentDir,"%s%s","webapps/")% ("tomcat7-",serverName)
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
        #connector[1].setAttribute("port", ajp_port)  # ajp port
    outfile = file(xmlpath, 'w')
    write = codecs.lookup("utf-8")[3](outfile)
    domtree.writexml(write, addindent=" ", encoding='utf-8')
    write.close()

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
    #ajp_port = portDict["ajp_port"]
    jenkinsUploadDirServer = joinPathName(jenkinsUploadDir,"%s") % serverName
    deployDir = joinPathName(deploymentAppSerDir, "%s%s") % (tomcatPrefix, serverName)  # 部署工程目录
    deployRoot = joinPathName(deploymentDir, "tomcat7-%s", "webapps/") % serverName
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
            changeXml(serverName, shutdown_port=shutdown_port, http_port=http_port)
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
            changeXml(serverName, shutdown_port=shutdown_port, http_port=http_port)
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

def listDirFile(path):
    os.listdir(path)

def getVersion(path):
    versionIdList = []
    for i in os.listdir(path):
        if i.split(".")[0] == "ROOT":
            versionId = i.split(".")[1]
            versionIdList.append(versionId)
    if not versionIdList:
        return ["0"]
    return versionSort(versionIdList)  # 返回版本号 升序列表

def backWar(serverName):
    # 部署的war包
    deployRootWar = joinPathName(deploymentDir, "tomcat7-%s", "webapps","ROOT.war") % serverName
    # 备份war包路径
    bakdeployRoot = joinPathName(deploymentDir, "tomcat7-%s", "bak-tomcat7-%s") % (serverName, serverName)
    # versionId = int(getVersion(bakdeployRoot)[-1])+int(1)
    versionId = int(getVersion(bakdeployRoot)[-1].split("-")[-1].split("V")[-1])+int(1) # 同一日期下的最新版本+1
    #bakdeployRootWar = joinPathName(deploymentDir, "tomcat7-%s","bak-tomcat7-%s", "ROOT.%s.war") % (serverName,serverName, time.strftime("%Y-%m-%d-%H%M%S"))
    bakdeployRootWar = joinPathName(deploymentDir, "tomcat7-%s", "bak-tomcat7-%s", "ROOT.%sV%s.war") % (serverName, serverName, time.strftime("%Y-%m-%d-"), versionId)
    #print bakdeployRootWar
    if os.path.exists(deployRootWar):
        copyFile(deployRootWar, bakdeployRootWar)
        if os.path.exists(bakdeployRootWar):
            print "back %s sucess" % deployRootWar

def rollBack(versionId, serverName):
    bakdeployRootWar = joinPathName(deploymentDir, "tomcat7-%s", "bak-tomcat7-%s", "ROOT.%s.war") % (serverName, serverName, versionId)
    deployRootWar = joinPathName(deploymentDir, "tomcat7-%s", "webapps", "ROOT.war") % serverName
    #deployWarPath = joinPathName(deploymentDir, "tomcat7-%s/webapps/ROOT.war") % serverName
    deployWarPathRoot = joinPathName(deploymentDir, "tomcat7-%s/webapps/ROOT") % serverName
    if not os.path.exists(bakdeployRootWar):
        print "File:%s is not exits" % bakdeployRootWar
    if os.path.exists(deployRootWar):
        os.remove(deployRootWar)
        print "clean %s file" % deployRootWar
    copyFile(bakdeployRootWar, deployRootWar)
    if os.path.exists(deployRootWar):
        print "RollBack Sucess,update serverName:%s" % serverName
        stopMain(serverName)
        if serverName == "upload":
            cleanCachUpload(deployWarPathRoot)
        else:
            if os.path.exists(deployWarPathRoot):
                shutil.rmtree(deployWarPathRoot)
        unzipWar(deployRootWar, deployWarPathRoot)
        startMain(serverName)

        #updateMain(serverName)
    else:
        print "check File ,rollback Faile"


def versionSort(list):
  #对版本号排序 控制版本的数量
    from distutils.version import LooseVersion
    vs = [LooseVersion(i) for i in list]
    vs.sort()
    return [i.vstring for i in vs]

def rollBackMain(serverName):
    pass

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
    if Tag == "stop":  # 停服务
        stopMain(serverNAME)
    elif Tag == "start":  # 启动服务
        startMain(serverNAME)
    elif Tag == "restart":  # 重启服务
        stopMain(serverNAME)
        startMain(serverNAME)
    elif Tag == "update":  # 更新发布新版本
        updateMain(serverNAME)
    elif Tag in ["install", "uninstall", "reinstall"]:  # 部署tomcat 环境
        deploy(Tag, serverNAME)
    elif Tag == "send":  # 分发方法
        sendWarToNodeMain(serverNAME)

if __name__ == "__main__":
    try:
        Tag = sys.argv[1]
        #servername = sys.argv[2]
    except:
        print "Follow"
        sys.exit()
    if len(sys.argv) == 2:
        Tag = sys.argv[1]
        Main(Tag)
    elif len(sys.argv) == 3:
        Tag = sys.argv[1]
        serName = sys.argv[2]
        Main(Tag, serName)
    else:
        print """Follow One or Two agrs," \
               install|uninstall|reinstall:
               update:
               start|stop|restart:
               send:
               rollback"""

    #backWar("b2b-trade-api")
    # rollBack("2018-03-22-V4", "upload")
    # rollBack("2018-03-26-V1", "upload")


             #print i

    # sendWarToNodeMain()
    #sendWarToNode("upload")
     # sendWarToNodeMain("upload")
    #sendWarToNode("192.168.0.159","upload")
    # serverName =""
    # serverName =""
    # sendWarToNodeMain(serverName)

