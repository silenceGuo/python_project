#!/usr/bin/python
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
import time
import ConfigParser

serverConf = "/python-project/standard1.conf"  # 部署配置文件
bakDir = "/app/bak/"  # 备份上一次的应用目录
# bakDir = "D:\\bat"  # 备份上一次的应用目录
keepBakNum = 5  # 备份包保留版本数。

"""
对项目目录和文件进行备份回滚，历史版本管理自动清理，
"""
from optparse import OptionParser
reload(sys)
sys.setdefaultencoding('utf-8')

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

    # bakdeployRoot = getDeploymentTomcatPath(serverName)["bakServerDir"]
    bakdeployRoot = os.path.join(bakDir, serverName)

    versionIdList = []
    try:
       for i in os.listdir(bakdeployRoot):

           if i.split(".")[0] == serverName:
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
    # bakServerDir = getDeploymentTomcatPath(serverName)["bakServerDir"]

    bakServerDir = os.path.join(bakDir, serverName)
    VersinIdList = getVersion(serverName)
    # print VersinIdList
    if VersinIdList:
        if len(VersinIdList) > int(keepBakNum):
            cleanVersionList = VersinIdList[0:abs(len(VersinIdList) - int(keepBakNum))]
            for i in cleanVersionList:
                bakWarPath = os.path.join(bakServerDir, "%s.%s") % (serverName,i)
                if os.path.exists(bakWarPath):
                    print "clean history back WAR: %s" % bakWarPath
                    # os.remove(bakWarPath)
                    if os.path.isdir(bakWarPath):
                        shutil.rmtree(bakWarPath)
                    elif os.path.isfile(bakWarPath):
                        os.remove(bakWarPath)
                    else:
                        print "othe err"
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

def checkServer(serverName):
    deployDir = projectDict[serverName]["deploydir"]
    if os.path.exists(deployDir):
        return True
    else:
        return False

#判断目录是否为空
def dir_is_null(path):
    # print os.listdir(path)
    if os.path.exists(path):
        if os.listdir(path):
            # 不为空 False
            return False
    #是空返回True
    return True

def backWar(serverName):
    # 部署的包
    init()
    # deployDir = serverNameDict[serverName]["deploydir"]
    # print projectDict
    try:
        deployWar = projectDict[serverName]["deployFile"]
        # deployWar = os.path.join(deployDir, deployFile)
    except:
        deployWar = projectDict[serverName]["deploydir"]

    # 备份包路径
    bakServerDir = os.path.join(bakDir, serverName)

    versionId = getBackVersionId(serverName)  # 同一日期下的最新版本

    try:
        lastVersinId = getVersion(serverName)[-1]
    except:
        # 获取 备份文件列表 如果没有备份 返回备份起始版本1
        lastVersinId = [time.strftime("%Y-%m-%d-")+"V1"][-1]

    bakdeployRootWar = os.path.join(bakServerDir,"%s.%sV%s") % (serverName,time.strftime("%Y-%m-%d-"), versionId)

    lastbakdeployRootWar = os.path.join(bakServerDir,"%s.%s") % (serverName,lastVersinId)


    if not checkServer(serverName):
        print "%s is not install" % serverName
    else:

        if os.path.exists(deployWar) and not dir_is_null(deployWar):

            if not os.path.exists(lastbakdeployRootWar):
                print "back %s >>> %s" % (deployWar, bakdeployRootWar)
                # copyFile(deployWar, bakdeployRootWar)
                if os.path.isdir(deployWar):
                    copyDir(deployWar, bakdeployRootWar)
                elif os.path.isfile(deployWar):
                    copyFile(deployWar, bakdeployRootWar)
            else:
                # 判断 最后一次备份和现在的文件是否 修改不一致，如果一致就不备份，
                if not getTimeStamp(deployWar) == getTimeStamp(lastbakdeployRootWar):
                    print "back %s >>> %s" % (deployWar, bakdeployRootWar)
                    if os.path.isdir(deployWar):
                        copyDir(deployWar, bakdeployRootWar)
                    elif os.path.isfile(deployWar):
                        copyFile(deployWar, bakdeployRootWar)

                    cleanHistoryBak(serverName)
                    if os.path.exists(bakdeployRootWar):
                        print "back %s sucess" % bakdeployRootWar
                    else:
                        print "back %s fail" % deployWar
                else:
                    # print getVersion(serverName)
                    print "File:%s is not modify,not need back" % deployWar
        else:
            print "path %s is null or %s is not exists" % (deployWar,bakdeployRootWar)

def rollBack(serverName,versionId=""):
    # 为方便调用需要出示化服务字典，目前暂无优化，待优化，结合部署脚本使用
    init()

    # dirDict = getDeploymentTomcatPath(serverName)
    dirDict = projectDict[serverName]
    versionList = getVersion(serverName)

    # print versionList
    if not versionList:
        print "Not Back war File :%s" % serverName
    else:
        if not versionId:
            versionId = versionList[-1]

        # bakdeployWar = os.path.join(dirDict["bakServerDir"],"%s.%s") % (serverName,versionId)
        bakdeployWar = os.path.join(bakDir,serverName,"%s.%s") % (serverName,versionId)
        # os.path.join(bakDir,serverName)

        # deployRootWar = dirDict["deploydir"]

        try:
            deployRootWar = dirDict["deployFile"]
            # deployRootWar = os.path.join(deployRootWar, deployFile)
        except:
            deployRootWar = dirDict["deploydir"]

        if not os.path.exists(bakdeployWar):
            print "File:%s is not exits" % bakdeployWar
            sys.exit()
        if os.path.exists(deployRootWar):
            # os.removedirs(deployRootWar)
            print "clean history file: %s " % deployRootWar
        if os.path.isdir(bakdeployWar):
            shutil.rmtree(deployRootWar)
            copyDir(bakdeployWar, deployRootWar)
        elif os.path.isfile(bakdeployWar):
            os.remove(deployRootWar)
            copyFile(bakdeployWar, deployRootWar)
        # chown_cmd = "sudo chown ec2-user.ec2-user -R %s" % deployRootWar
        # stdout, stderr = execSh(chown_cmd)
        # if stdout:
        #     print "stdout：%s" % stdout
        # if stderr:
        #     print "stederr： %s" % stderr
        if os.path.exists(deployRootWar):
            print "RollBack Sucess,update serverName:%s" % serverName
            print "Rollback Version:%s " % versionId
        else:
            print "check File:%s ,rollback Faile" % deployRootWar

#读取配置文件
def readConf(serverConf):

    cf = ConfigParser.ConfigParser()
    try:
        cf.read(serverConf)
    except ConfigParser.ParsingError,e:
        print e
        print "please check conf %s" % serverConf
        sys.exit()

    serverNameDict = {}
    optinsDict = {}
    for serverName in cf.sections():
        #print 'serverName:%s' % serverName
        for optins in cf.options(serverName):
            # 取服务名下的对应的配置和参数

            if not confCheck(cf, serverName, optins):
                sys.exit()
            value = cf.get(serverName, optins)
            optinsDict[optins] = value
        serverNameDict[serverName] = optinsDict
        optinsDict={}

    return serverNameDict

def confCheck(cf, section, option):
    if not cf.options(section):
        print "no section: %s in conf file" % section
        sys.exit(2)
    try:
        options = cf.get(section, option)
    except ConfigParser.NoOptionError:
        print "no option in conf %s " % option
        sys.exit(2)
    if not options:
        print "options:(%s) is null in section:(%s)" % (option, section)
        return False
    else:
        return True

def init():
    # 初始化基础目录
    # if not os.path.exists(deploymentAppDir):
    #     os.makedirs(deploymentAppDir)
    if not os.path.exists(bakDir):
        os.makedirs(bakDir)
    if not os.path.exists(serverConf):
        print "serverconf is not exists,check serverconf %s " % serverConfPath
        print """ %s like this:
                   [testgit]
                   deployDir=/app/project/testgit/war/
                   gitUrl=git@10.0.1.131:root/testgit.git
                   deployGroupName=node1
                   deployFile=/app/project/testgit/war/2.war
                    """ % serverConf
        sys.exit(2)
    else:
        # 读配置文件 服务配置
        global projectDict
        projectDict = readConf(serverConf)

def main(action, serverName, version):
    # action = action.lower()
    # print action

    if action == "back":
        backWar(serverName)
    elif action == "rollback":
        rollBack(serverName, version)
    elif action == "getback":
        versionlist = getVersion(serverName)
        if not versionlist:
            print "%s not back" % serverName
        else:
            print "%s has back version:%s" % (serverName, versionlist)
    else:
        print "action is -a [back,rollback, getback] -n servername [all]"
        sys.exit(1)


def getOptions():
    parser = OptionParser()

    parser.add_option("-n", "--serverName", action="store",
                      dest="serverName",
                      default=False,
                      help="serverName to do")

    parser.add_option("-a", "--action", action="store",
                      dest="action",
                      default=False,
                      help="action -a [back,rollback,getback]")

    parser.add_option("-v", "--versionId", action="store",
                      dest="versionId",
                      default=False,
                      help="-v versionId")

    # parser.add_option("-g", "--groupName", action="store",
    #                   dest="groupName",
    #                   default=False,
    #                   help="-g groupName")

    options, args = parser.parse_args()
    return options, args

#检查文件是否存在
def fileExists(filePath):
    if not os.path.exists(filePath):
        print "文件：%s 不存在，请检查" % filePath
        return False
    return True

# 输出服务配置文件中的服务名
def printServerName(projectDict):
    serverNameList = []
    for serverName, serverNameDict in projectDict.items():
        print "可执行为服务名：%s" %  serverName
        serverNameList.append(serverName)
    #返回服务名列表，可以在后期处理进行排序，考虑服务启动的顺序
    return serverNameList
if __name__ == "__main__":
    # serverConfPath = "standard1.conf"  # 部署配置文件
    # bakDir = "/app/bak/"  # 备份上一次的应用目录
    # # bakDir = "D:\\bat"  # 备份上一次的应用目录
    # keepBakNum = 5  # 备份包保留版本数。
    init()
    options, args = getOptions()
    action = options.action
    version = options.versionId
    serverName = options.serverName
    if not action:
        print "follow -a action[back ,getback,rollback]"
        sys.exit()
    elif not serverName:
        print "follow -n servername"
        sys.exit()
    else:
        if serverName == "all":
            #批量操作
            for serverName,dict in projectDict.iteritems():
                main(action, serverName, version)
        elif not projectDict.has_key(serverName):
            print "没有服务名：%s" % serverName
            printServerName(projectDict)
            sys.exit()
        else:
            main(action, serverName, version)

    # 批量执行所有操作。安全性注释
    # if serverName == "all":
    #     for serverName,dict in serverNameDict.iteritems():
    #         main(action, serverName, version)
    # else:
    # try:
    #     dict = serverNameDict[serverName]
    # except Exception, e:
    #     print e
    #     print "severname:%s is err" % serverName
    #     sys.exit(1)
    # main(action, serverName, version)