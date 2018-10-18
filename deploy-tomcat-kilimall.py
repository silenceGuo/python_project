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
warDir = "/data/init/"  # war

# pyFile ="/home/scripts/deploy-liunx.py" # 指远程服务器执行py脚本路径
checktime = 5  # 等待时间 和检查状态次数
keepBakNum = 2  # 备份war包保留版本数

# 取当前脚步的绝对路径，并拼装配置文件路径
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
serverConfPath = os.path.join(dirname, serverConf)

def getOptions():
    parser = OptionParser()

    parser.add_option("-n", "--serverName", action="store",
                      dest="serverName",
                      default=False,
                      help="serverName to do")

    parser.add_option("-a", "--action", action="store",
                      dest="action",
                      default=False,
                      help="action -a [install,uninstall,reinstall,stop,start,restart,back,rollback,getback]")

    parser.add_option("-v", "--versionId", action="store",
                      dest="versionId",
                      default=False,
                      help="-v versionId")



    options, args = parser.parse_args()
    return options, args

def getDeploymentTomcatPath(serverName):
    deployServerDir = os.path.join(deploymentAppDir, "%s%s") % (tomcatPrefix, serverName)
    deployServerWarDir = os.path.join(deploymentAppDir, "%s%s/%s") % (tomcatPrefix, serverName, "war")
    deployServerTomcatDir = os.path.join(deploymentAppDir, "%s%s/%s") % (tomcatPrefix, serverName, "tomcat")
    deployServerXmlDir = os.path.join(deploymentAppDir, "%s%s/%s") % (tomcatPrefix, serverName,"tomcat/conf/server.xml")
    bakServerDir = os.path.join(bakDir, "%s%s") % (tomcatPrefix, serverName)
    return {"deployServerDir":deployServerDir,
            "deployServerWarDir":deployServerWarDir,
            "deployServerTomcatDir":deployServerTomcatDir,
            "deployServerXmlDir":deployServerXmlDir,
            "bakServerDir": bakServerDir
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
        global serverNameDictList
        serverNameDictList = readConf(serverConfPath)

        if not chekPort():
            sys.exit()

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
    serverNameList = []
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
        # print "%s is installed" % serverName
        return True
    else:
        # print "%s is not install" % serverName
        return False

# 检查端口占用
def chekPort():
    from collections import Counter
    portList=[]
    for serverNameDict in serverNameDictList:
        for serverName, portDict in serverNameDict.iteritems():
            shutdown_port = portDict["shutdown_port"]
            http_port = portDict["http_port"]
            ajp_port = portDict["ajp_port"]
            portList.append(http_port)
            portList.append(shutdown_port)
            portList.append(ajp_port)

    for port, num in Counter(portList).iteritems():
        if num > 1:
            print "%s is duplicated" % port
            print "check conf port"
            return False
    return True


# 注册服务

def installServer(serverName):
    serverList = []
    if not checkServer(serverName):
        for serverNameDict in serverNameDictList:
            #print serverNameDict
            for serName, optionsDict in serverNameDict.iteritems():
                serverList.append(serName)
       # print serverList
        if serverName in serverList:
            for serverNameDict in serverNameDictList:
                if serverNameDict.has_key(serverName):
                    optionsDict = serverNameDict[serverName]
                    try:
                        shutdown_port = optionsDict["shutdown_port"]
                        http_port = optionsDict["http_port"]
                        ajp_port = optionsDict["ajp_port"]
                    except KeyError, e:
                        # print e
                        print "please check conf file with :%s" % e
                        continue
                        #sys.exit(1)
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
                    print"%s install sucess" % serverName
                    break
        else:
            print "serverName:%s is errr" %serverName
    else:
        print "%s is installed" % serverName

def uninstallServer(serverName):
    # serverNameDictList = readConf(serverConfPath)
    if checkServer(serverName):
        for serverNameDict in serverNameDictList:

            if serverNameDict. has_key(serverName):
                stopServer(serverName)
                cleanDeployDir(serverName)
                print "%s is uninstall sucess!" % serverName
                break
    else:
        print "%s is not instell or is err" % serverName

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
    # for serverNameDict in serverNameDictList:
    #     for serverNam,portDict in serverNameDict.iteritems():
    #         if serverNam == serverName:
    #             war = portDict["war"]
    #             break

    deployDir = getDeploymentTomcatPath(serverName)["deployServerTomcatDir"]
    # deployServerDir = getDeploymentTomcatPath(serverName)["deployServerDir"]
    startSh = os.path.join(deployDir, "bin/startup.sh")
    cmd = "sudo su - tomcat -c '/bin/bash %s'" % startSh
    binDir = os.path.join(deployDir, "bin/*")

    deployServerWarDir = getDeploymentTomcatPath(serverName)["deployServerWarDir"]

    #deployWarPath = os.path.join(deployServerDir,"lipapay-web-1.0.war")

    # warDirPath = os.path.join(warDir, war)

    chmodCmd = "chmod 755 -R %s" % binDir
    # chmodCmd2 = "chmod 755 -R %s" % deployDir
    # chmodCmd3 = "chmod 755 -R %s" % deployServerWarDir

    chownCmd = "chown -R tomcat:tomcat %s" % deployDir
    chownCmd2 = "chown -R tomcat:tomcat %s" % binDir
    chownCmd3 = "chown -R tomcat:tomcat %s" % deployServerWarDir

    # cmd = "su - tomcat %s" % startSh
    #cmd = "su tomcat nohup %s &" % startSh
    pid = getPid(serverName)
    if not pid:
        print "Start Server:%s" % serverName

        execSh(chmodCmd)
        # execSh(chmodCmd2)
        # execSh(chmodCmd3)
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


def versionSort(list):
  #对版本号排序 控制版本的数量
    from distutils.version import LooseVersion
    vs = [LooseVersion(i) for i in list]
    vs.sort()
    return [i.vstring for i in vs]

def getVersion(serverName):

    bakdeployRoot = getDeploymentTomcatPath(serverName)["bakServerDir"]

    # getDeploymentTomcatPath(serverName)["bakServerDir"]
    versionIdList = []
    try:
       for i in os.listdir(bakdeployRoot):
           # print i
           if i.split(".")[0] == "war":
               versionId = i.split(".")[1]
               versionIdList.append(versionId)
    except:
        return []
    if not versionIdList:
        return []
    return versionSort(versionIdList)  # 返回版本号升序列表

def getBackVersionId(serverName):
    date = time.strftime("%Y-%m-%d")
    versionIdList = getVersion(serverName)
    # print versionIdList
    if not versionIdList:
        return 1
    else:
        # 同一日期下的最新版本+1
        if date != versionSort(versionIdList)[-1].split("-V")[0]:
            return 1
        else:
            return int(versionIdList[-1].split("-")[-1].split("V")[-1]) + int(1)

def TimeStampToTime(timestamp):
    # 时间戳转换为时间
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)

# 返回时间戳
def getTimeStamp(filePath):
    filePath = unicode(filePath, 'utf8')
    t = os.path.getmtime(filePath)
    # return t
    return TimeStampToTime(t)
#清理历史多余的备份文件
def cleanHistoryBak(serverName):
    bakServerDir = getDeploymentTomcatPath(serverName)["bakServerDir"]

    VersinIdList = getVersion(serverName)
    # print VersinIdList
    if VersinIdList:
        if len(VersinIdList) > int(keepBakNum):
            cleanVersionList = VersinIdList[0:abs(len(VersinIdList) - int(keepBakNum))]
            for i in cleanVersionList:
                bakWarPath = os.path.join(bakServerDir, "war.%s") % i
                if os.path.exists(bakWarPath):
                    print "clean history back WAR: %s" % bakWarPath
                    # os.remove(bakWarPath)
                    shutil.rmtree(bakWarPath)
        else:
            pass
    else:
        print "%s is not bak War" % serverName


def copyFile(sourfile,disfile):
    try:
        print "copy file:%s,to:%s" % (sourfile, disfile)
        shutil.copy2(sourfile, disfile)  # % ( disfile, time.strftime("%Y-%m-%d-%H%M%S"))
    except Exception, e:
        print e,
        sys.exit(1)

def copyDir(sourDir,disDir):
    try:
        print "copy Dir:%s,to:%s" % (sourDir,disDir)
        # shutil.copy2(sourDir, disDir)  # % ( disfile, time.strftime("%Y-%m-%d-%H%M%S"))
        shutil.copytree(sourDir,disDir)
    except Exception, e:
        print e,
        sys.exit(1)


def backWar(serverName):
    # 部署的war包
    deployWar = getDeploymentTomcatPath(serverName)["deployServerWarDir"]
    # 备份war包路径
    bakServerDir = getDeploymentTomcatPath(serverName)["bakServerDir"]
    versionId = getBackVersionId(serverName)  # 同一日期下的最新版本
    # print versionId
    try:
        lastVersinId = getVersion(serverName)[-1]
    except:
        # 获取 备份文件列表 如果没有备份 返回备份起始版本1
        lastVersinId = [time.strftime("%Y-%m-%d-")+"V1"][-1]
        # print lastVersinId
    bakdeployRootWar = os.path.join(bakServerDir,"war.%sV%s") % (time.strftime("%Y-%m-%d-"), versionId)
    # print bakdeployRootWar
    lastbakdeployRootWar = os.path.join(bakServerDir,"war.%s") % (lastVersinId)
    # print lastbakdeployRootWar

    if not os.path.exists(deployWar):
        os.mkdir(deployWar)
    if os.path.exists(deployWar):
        if not os.path.exists(lastbakdeployRootWar):
            print "back %s >>> %s" % (deployWar, bakdeployRootWar)
            # copyFile(deployWar, bakdeployRootWar)
            copyDir(deployWar, bakdeployRootWar)
        else:
            # 判断 最后一次备份和现在的文件是否 修改不一致，如果一致就不备份，
            if not getTimeStamp(deployWar) == getTimeStamp(lastbakdeployRootWar):
                print "back %s >>> %s" % (deployWar, bakdeployRootWar)
                copyDir(deployWar, bakdeployRootWar)
                cleanHistoryBak(serverName)
                if os.path.exists(bakdeployRootWar):
                    print "back %s sucess" % bakdeployRootWar
                else:
                    print "back %s fail" % deployWar
            else:
                # print getVersion(serverName)
                print "File:%s is not modify,not need back" % deployWar
    else:
        print "file %s or %s is not exists" % (deployWar,bakdeployRootWar)

def rollBack(serverName,versionId=""):
    dirDict = getDeploymentTomcatPath(serverName)
    versionList = getVersion(serverName)

    # print versionList
    if not versionList:
        print "Not Back war File :%s" % serverName
    else:
        if not versionId:
            versionId = versionList[-1]

        bakdeployWar = os.path.join(dirDict["bakServerDir"],"war.%s") % ( versionId)

        deployRootWar = dirDict["deployServerWarDir"]

        if not os.path.exists(deployRootWar):
            print "File:%s is not exits" % bakdeployWar

        if os.path.exists(deployRootWar):
            # os.removedirs(deployRootWar)
            shutil.rmtree(deployRootWar)
            print "clean history file: %s " % deployRootWar
        copyDir(bakdeployWar, deployRootWar)
        if os.path.exists(deployRootWar):
            print "RollBack Sucess,update serverName:%s" % serverName
            print "Rollback Version:%s " % versionId
        else:
            print "check File:%s ,rollback Faile" % deployRootWar


def main(action,serverName,version):
    # action = action.lower()
    # print action
    if action =="install":
        installServer(serverName)
    elif action == "uninstall":
        uninstallServer(serverName)
        #stopServer(serverName)
    elif action == "stop":
        stopServer(serverName)
    elif action == "start":
        startServer(serverName)
    elif action == "restart":
        stopServer(serverName)
        startServer(serverName)
    elif action == "reinstall":
        uninstallServer(serverName)
        installServer(serverName)
    elif action == "back":
        backWar(serverName)
    elif action == "rollback":
        stopServer(serverName)
        rollBack(serverName,version)
        startServer(serverName)
    elif action == "getback":
        versionlist = getVersion(serverName)
        if not versionlist:
            print "%s not back" % serverName
        else:
            print "%s has back version:%s" % (serverName,versionlist)
    else:
        print "action is -a [install,uninstall,reinstall,stop,start,restart,back,rollback,getback] -n servername [all]"
        sys.exit(1)


if __name__ == "__main__":

    _init()
    options, args = getOptions()
    action = options.action
    version = options.versionId
    serverName = options.serverName
    # print options,args
    # print version
    # rollBack(serverName,version)
    if serverName == "all":
        for serverNameDict in serverNameDictList:
            for seName,portDict in serverNameDict.iteritems():
                 main(action, seName, version)
    else:
        main(action, serverName, version)

