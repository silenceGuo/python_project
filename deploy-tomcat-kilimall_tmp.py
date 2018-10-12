#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Author : gzq
# @date   : 2018/1/10 0010 16:30
# @file   : deploy-liunx.py
# 该脚本部署在统一的目录下通过，实现本地及远程服务器上的服务部署，重启，发布,分发,回滚等操作
# 登陆远程服务器需提前配置好ssh密钥登陆
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

from optparse import OptionParser
reload(sys)
sys.setdefaultencoding('utf-8')
serverConf = "server_liunx.conf"  # 部署配置文件
#uploadConf = "upload_liunx.conf"  # 部署配置文件

deploymentAppDir = "/apps/"  # 部署工程目录存放tomcat
bakDir = "/apps/bak/"  # 备份上一次的应用目录
baseTomcat = "/apps/tomcat-base/"
tomcatPrefix = "tomcat-"

# pyFile ="/home/scripts/deploy-liunx.py" # 指远程服务器执行py脚本路径
checktime = 5  # 等待时间 和检查状态次数
keepBakNum = 2  # 备份war包保留版本数

# 取当前脚步的绝对路径，并拼装配置文件路径
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
serverConfPath = os.path.join(dirname, serverConf)

def getOptions():
    parser = OptionParser()
    parser.add_option("-a", "--action", action="store",
                      dest="action",
                      default=False,
                      help="action serverName")

    parser.add_option("-n", "--serverName", action="store",
                      dest="serverName",
                      default=False,
                      help="serverName to do")

    options, args = parser.parse_args()
    return options, args

def getDeploymentTomcatPath(serverName):
    deployServerDir = os.path.join(deploymentAppDir, "%s%s") % (tomcatPrefix, serverName)
    deployServerWarDir = os.path.join(deploymentAppDir, "%s%s/%s") % (tomcatPrefix, serverName, "war")
    deployServerTomcatDir = os.path.join(deploymentAppDir, "%s%s/%s") % (tomcatPrefix, serverName, "tomcat")
    deployServerXmlDir = os.path.join(deploymentAppDir, "%s%s/%s") % (tomcatPrefix, serverName,"tomcat/conf/server.xml")

    return {"deployServerDir":deployServerDir,
            "deployServerWarDir":deployServerWarDir,
            "deployServerTomcatDir":deployServerTomcatDir,
            "deployServerXmlDir":deployServerXmlDir
            }

def _init():
    # 初始化基础目录

    if not os.path.exists(deploymentAppDir):
        os.makedirs(deploymentAppDir)
    if not os.path.exists(bakDir):
        os.makedirs(bakDir)
    if not os.path.exists(serverConfPath):
        print "serverconf is not exists,check serverconf %s "% serverConfPath
        print """ %s like this:
                   [b2b-trade-api]
                    http_port = 8048
                    ajp_port = 8148
                    shutdown_port = 8248
                    war = com.hxh.xhw.upload.war
                    ip = 192.168.0.159,192.168.0.59""" % serverConf
        sys.exit()
    else:
        # 读配置文件 服务配置
        global serverNameList
        serverNameList = readConf(serverConfPath)

    if not os.path.exists(baseTomcat):
        print "Base tomcat File (%s) is not exists" % baseTomcat
        sys.exit()


#读取配置文件
def readConf(confPath):
    cf = ConfigParser.ConfigParser()
    try:
        cf.read(confPath)
    except ConfigParser.ParsingError,e:
        print e
        print "please check conf %s" % confPath
        sys.exit()
    serverNameList=[]
    serverNameDict = {}
    portDict = {}
    for serverName in cf.sections():
        # print 'serverName:%s' % serverName
        for optins in cf.options(serverName):
            # 取服务名下的对应的配置和参数
            if not confCheck(cf, serverName, optins):
                sys.exit()
            port = cf.get(serverName, optins)
            portDict[optins] = port
        serverNameDict[serverName] = portDict
        serverNameList.append(serverNameDict)
        # print serverNameDict
        portDict = {}
        serverNameDict = {}
    return serverNameList

def confCheck(cf, section, option):
    if not cf.options(section):
        print "no section: %s in conf file" % section
        sys.exit()
    try:
        options = cf.get(section, option)
    except ConfigParser.NoOptionError:
        print "no option in conf %s " % option
        sys.exit()
    if not options:
        print "options:(%s) is null in section:(%s)" % (option, section)
        return False
    else:
        return True
# 检查服务注册状态
def checkServer(serverName):

    if os.path.exists(getDeploymentTomcatPath(serverName)["deployServerDir"]):
        print "%s is installed" % serverName
        return True
    else:
        print "%s is not install" % serverName
        return False

# 检查端口占用
def chekPort(port):
    pass


# 注册服务
def installServer(serverName):

    serverNameDict = readConf(serverConfPath)
    if not serverNameDict.has_key(serverName):
        print "%s is err!" % serverName
    else:
        optionsDict = serverNameDict[serverName]
        shutdown_port = optionsDict["shutdown_port"]
        http_port = optionsDict["http_port"]
        ajp_port = optionsDict["ajp_port"]

        deployDir = getDeploymentTomcatPath(serverName)["deployServerDir"]  # 部署工程目录
        chownCmd = "chown -R tomcat:tomcat %s" % deployDir  # 目录权限修改
        # 从标准tomcat 复制到部署目录
        copyBaseTomcat(serverName)
        # 修改部署tomcat server.xml配置文件
        changeXml(serverName, shutdown_port=shutdown_port, http_port=http_port, ajp_port=ajp_port)
        stdout, stderr = execSh(chownCmd)
        if stdout:
            print stdout
        if stderr:
            print stderr

def uninstallServer(serverName):
    serverNameDict = readConf(serverConfPath)
    if not serverNameDict. has_key(serverName):
        print "%s is err!" % serverName
    else:
        if checkServer(serverName):
            stopServer(serverName)
            cleanDeployDir(serverName)


def getPid(serverName):
    deployDir = getDeploymentTomcatPath(serverName)["deployServerDir"]
    #cmd = "pgrep -f %s" % servername
    cmd = "pgrep -f %s" % deployDir
    pid, stderr = execSh(cmd)
    if pid:
        #string(pid,)
        print "Get PID:%s" %pid
        return int(pid)


def stopServer(serverName):
    # 停止服务 先正常停止，多次检查后 强制杀死！
    deployDir = getDeploymentTomcatPath(serverName)["deployServerTomcatDir"]
    shutdown = os.path.join(deployDir, "bin/shutdown.sh")
    cmd = "su tomcat %s" % shutdown
    pid = getPid(serverName)
    if not pid:
        print "Server:%s is down" % serverName
        return True
    else:
        stdout, stderr = execSh(cmd)  # 执行 shutdown命令
        if stdout:
            print "stdout:%s" % stdout
        if stderr:
            print "stderr:%s " % stderr

        for i in range(checktime):
            time.sleep(10)
            print "check servname :%s num:%s" % (serverName, i + 1)
            if not getPid(serverName):
                print "Server:%s,shutdown success" % serverName
                return True
    if getPid(serverName):
        print "Server:%s,shutdown fail pid:%s" % (serverName, getPid(serverName))
        try:
            os.kill(pid, signal.SIGKILL)
            # os.kill(pid, signal.9) #　与上等效
            print 'Killed server:%s, pid:%s' % (serverName, pid)
        except OSError, e:
            print 'No such as server!', e
        if getPid(serverName):
            print "shutdown fail,check server:%s" % serverName
            return False
    else:
        print "Server:%s,shutdown success" % serverName
        return True

def unzipWar(zipfilePath,unzipfilepath):
    f = zipfile.ZipFile(zipfilePath, 'r')
    print 'unzip file:%s >>>>>>to:%s' % (zipfilePath, unzipfilepath)
    for file in f.namelist():
        f.extract(file, unzipfilepath)

def startServer(serverName):
    deployDir = getDeploymentTomcatPath(serverName)["deployServerTomcatDir"]
    deployServerDir = getDeploymentTomcatPath(serverName)["deployServerDir"]
    startSh = os.path.join(deployDir, "bin/startup.sh")
    cmd = "sudo su - tomcat -c '/bin/bash %s'" % startSh
    binDir = os.path.join(deployDir, "bin/*")
    deployServerWarDir = getDeploymentTomcatPath(serverName)["deployServerWarDir"]
    deployWarPath = os.path.join(deployServerDir,"lipapay-web-1.0.war")
    deployWarPath1 = os.path.join("/apps","lipapay-web-1.0.war")
    chmodCmd = "chmod 755 -R %s" % binDir
    chmodCmd2 = "chmod 755 -R %s" % deployDir
    chmodCmd3 = "chmod 755 -R %s" % deployServerWarDir

    chownCmd = "chown -R tomcat:tomcat %s" % deployDir
    chownCmd2 = "chown -R tomcat:tomcat %s" % binDir
    chownCmd3 = "chown -R tomcat:tomcat %s" % deployServerWarDir

    # cmd = "su - tomcat %s" % startSh
    #cmd = "su tomcat nohup %s &" % startSh
    pid = getPid(serverName)
    if not pid:
        print "Start Server:%s" % serverName
        # 清历史缓存数据
        if os.path.exists(deployServerWarDir):
            shutil.rmtree(deployServerWarDir)
        unzipWar(deployWarPath1, deployServerWarDir)
        # 授权
        # print "chmod dir 755 %s" % binDir
        execSh(chmodCmd)
        execSh(chmodCmd2)
        execSh(chmodCmd3)
        # 更改所属 组
        execSh(chownCmd)
        execSh(chownCmd2)
        execSh(chownCmd3)
        stdout, stderr = execSh(cmd)  # 执行 启动服务命令
        if stdout:
            print "stdout:%s" % stdout
        if stderr:
            print "stderr:%s " % stderr

        for i in range(checktime):
            time.sleep(10)
            print "check servname :%s num:%s" % (serverName, i + 1)
            pidtmp = getPid(serverName)
            if pidtmp:
                print "Server:%s,start success pid:%s" % (serverName, pidtmp)
                return True
        pidtmp = getPid(serverName)
        if getPid(serverName):
            print "Server:%s,Sucess pid:%s" % (serverName, pidtmp)
        else:
            print "Server:%s,is not running" % serverName
            return False
    else:
        print "Server:%s,Sucessed pid:%s" % (serverName, pid)

def cleanDeployDir(serverName):

    deploymentAppPath = getDeploymentTomcatPath(serverName)["deployServerDir"]
    try:
        shutil.rmtree(deploymentAppPath)
        print "clean %s" % deploymentAppPath
    except Exception, e:
        print e
        sys.exit()

def copyBaseTomcat(serverName):

    deploymentDirTmp = getDeploymentTomcatPath(serverName)["deployServerDir"]
    try:
        print "copy BaseTomcat Dir :%s to:%s" % (baseTomcat, deploymentDirTmp)
        shutil.copytree(baseTomcat, deploymentDirTmp)
    except Exception, e:
        print e, "dir is exists！"
        sys.exit(1)

# 修改xml 配置文件
def changeXml(serverName,shutdown_port="8128",http_port="8083",ajp_port="8091"):
    deployPath = getDeploymentTomcatPath(serverName)
    warDir = deployPath["deployServerWarDir"]  # 解压的war 目录
    xmlpath = deployPath["deployServerXmlDir"]
    domtree = xml.dom.minidom.parse(xmlpath)
    collection = domtree.documentElement
    service = collection.getElementsByTagName("Service")
    collection.setAttribute("port", shutdown_port)  # shutdown port
    context = collection.getElementsByTagName("Context")  # 设置网站目录
    context[0].setAttribute("docBase", warDir)
    for i in service:
        connector = i.getElementsByTagName("Connector")
        appdeploy = i.getElementsByTagName("Host")
        appdeploy[0].setAttribute("appBase", "webapps") #部署目录 默认为webapps
        connector[0].setAttribute("port", http_port)  # http port
        connector[1].setAttribute("port", ajp_port)  # ajp port
    outfile = file(xmlpath, 'w')
    write = codecs.lookup("utf-8")[3](outfile)
    domtree.writexml(write, addindent=" ", encoding='utf-8')
    write.close()

def execSh(cmd):
    # 执行SH命令
    try:
        print "Exec ssh command %s" % cmd
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    except Exception, e:
        print e,
        sys.exit()
    return p.communicate()

def main():

    _init()
    options, args = getOptions()
    action = options.action
    serverName = options.serverName

    if action =="install":
        if serverName:
           installServer(serverName)
        elif serverName == "all":
            print serverNameList

    elif action == "uninstall":
        stopServer(serverName)
    elif action == "stop":
        stopServer(serverName)
    elif action == "start":
        startServer(serverName)
    elif action == "restart":
        if serverName == "all":
            print serverNameList
        elif serverName:
            print serverNameList
            stopServer(serverName)
            startServer(serverName)

    #print readConf(serverConfPath)[options.serverName]

if __name__ == "__main__":
    main()