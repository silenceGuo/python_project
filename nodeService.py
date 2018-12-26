#!/usr/bin/env python
# ！-*-coding:utf-8 -*-
# !@Date    : 2018/11/9 0009 下午 17:08
# !@Author : Damon.guo
# !@File   : updateStandard.py

import ConfigParser
from optparse import OptionParser
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
import json

reload(sys)
sys.setdefaultencoding('utf-8')

# 配置文件模板
server_conf_str = """
# 配置通过 # 可以注释不生效

[conf]
# jar服务和node服务的配置文件
jarconf = /python-project/jar.conf
# 备份上一次的应用目录
bakdir = /app/bak/
# 备份文件控制版本数
keepBakNum = 5
# 服务检查次数
checktime = 3
# 日志路径
logpath = /data/logs/
#ansible 主机文件
ansibilehostfile = /etc/ansible/hosts
# maven 执行命令路径
maven_home = /app/apache-maven-3.5.0/bin/mvn
# java 执行命令路径
java_home = /app/jdk1.8.0_121/bin/java
# nohup 命令路径
nohup = /usr/bin/nohup
# node执行命令路径
node_home = /data/app/node-v8.12.0/bin/node
# 定义远程执行脚本路径
python_dir = /python-project/updateJarService.py
# pthon 执行命令路径
python_home = /usr/bin/python
"""
jar_conf_str = """
[1-activity-eureka]
deployDir = /kilimall/procjet/activity-cloud/activity-eureka/
deployGroupName = node1
jar = /kilimall/procjet/activity-cloud/activity-eureka/target/activity-eureka-1.0.1.jar
xms = 256m
xmx = 256m
"""


def getOptions():
    parser = OptionParser()
    parser.add_option("-n", "--serverName", action="store",
                      dest="serverName",
                      default=False,
                      help="serverName to do")
    parser.add_option("-a", "--action", action="store",
                      dest="action",
                      default=False,
                      help="action -a [checkout,pull,push,master,install]")
    #
    # parser.add_option("-v", "--versionId", action="store",
    #                   dest="versionId",
    #                   default=False,
    #                   help="-v versionId")

    parser.add_option("-b", "--branchName", action="store",
                      dest="branchName",
                      default=False,
                      help="-b branchName")
    # jar 服务启动区分环境 读取的配置不一样
    parser.add_option("-e", "--envName", action="store",
                      dest="envName",
                      default=False,
                      help="-e envName")

    options, args = parser.parse_args()
    return options, args


def execSh(cmd):
    # 执行SH命令
    try:
        print "执行ssh 命令 %s" % cmd
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    except Exception, e:
        print e,
        sys.exit()
    return p.communicate()


def checkMaster():
    # 获取项目分支是否为master
    cmd = "git branch"
    stdout, stderr = execSh(cmd)
    print "out:", stdout
    branch_list = [i.strip() for i in stdout.split("\n") if i]
    if "* master" in branch_list:
        print "已经在master 分支"
        return True
    print "err", stderr
    return False


# 初始化项目主应用可用于php部署，
def initProject(serverName):
    # 新机器 或者新目录项目部署
    print "master install:%s" % serverName
    if os.path.exists(nodeConf):
        projectDict = readConf(nodeConf)
        print projectDict
    else:
        print "%s is not exists" % nodeConf
        print jar_conf_str
        sys.exit()

    deployDir = projectDict[serverName]["builddir"]
    gitUrl = projectDict[serverName]["giturl"]
    if not os.path.exists(deployDir):
        os.mkdir(deployDir)
    os.chdir(deployDir)
    print "部署路径：", os.getcwd()
    stdout, stderr = execSh("git status .")
    if stdout:
        print"out：\n%s" % stdout
        print "当前目录：%s,已经存在git仓库请检查!" % deployDir
        return True
    if stderr:
        print "没有git仓库，下一步"
        print"out：%s" % stderr

    print "初始化本地仓库"
    ReturnExec("git init")

    print"本地git仓库当前项目认证"
    config_cmd = "git config --local credential.helper store"
    ReturnExec(config_cmd)

    print "拉取代码"
    pull_cmd = "git pull %s" % gitUrl
    ReturnExec(pull_cmd)

    print "添加远程仓库地址"
    add_remote_cmd = "git remote add origin %s" % gitUrl
    ReturnExec(add_remote_cmd)

    print "获取分支"
    fetch_cmd = "git fetch"
    ReturnExec(fetch_cmd)

    print "关联本地master分支与远程master"
    upstream_cmd = "git branch --set-upstream-to=origin/master master"
    ReturnExec(upstream_cmd)

    print "获取 最新master分支"
    pull_m_cmd = "git pull"
    ReturnExec(pull_m_cmd)


def ReturnExec(cmd):
    stdout, stderr = execSh(cmd)
    if stdout:
        print 80 * "#"
        print "out:%s " % stdout
    if stderr:
        print 80 * "#"
        print "err:%s" % stderr


def readStdin():
    input_str = raw_input("确认执行操作：Y/N")
    return input_str.strip().lower()


# 合并分支至master
def mergeBranch(serverName, branchName):
    deployDir = projectDict[serverName]["deploydir"]
    fetch_cmd = "git fetch origin %s" % branchName
    checkout_b_cmd = "git checkout %s" % branchName
    pull_cmd = "git pull"
    checkout_m_cmd = "git checkout master"
    merge_cmd = "git merge origin/%s" % branchName
    push_cmd = "git push origin master"
    try:
        print "切换工作目录"
        print deployDir
        os.chdir(deployDir)  # 切换工做目录
        print os.getcwd()
    except Exception, e:
        print e
        sys.exit()

    print "取分支"
    stdout, stderr = execSh(fetch_cmd)
    print stdout

    if "fatal" in stderr:
        print stderr
        print "检查分支 branchname:%s" % branchName
        sys.exit()

    # ReturnExec(fetch_cmd)

    # 更新分支
    print "更新本地 分支"
    ReturnExec(pull_cmd)

    # 切换至master分支
    if not checkMaster():
        print "切换至master分支"
        ReturnExec(checkout_m_cmd)

    # 更新master分支
    print "更新master分支"
    ReturnExec(pull_cmd)

    # 合并分支至master
    print "是否合并分支至master"
    ReturnExec(merge_cmd)

    # 提交合并的master 至源端git库
    # 需要加确认 文件修改，在判断是否推送源端
    print "是否提交合并的master 至源端git库"
    option = readStdin()
    if option != "y":
        sys.exit()
    ReturnExec(push_cmd)

    # 更新应用节点代码
    # print "是否更新应用节点代码"
    # option = readStdin()
    #
    # if option != "y":
    #     sys.exit()
    # updatecmd = 'ansible %s -m shell -a "cd %s;sudo git pull";' % (deployNodeName, deployDir)
    # ReturnExec(updatecmd)


# 检查配置文件
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


# 读取配置文件
def readConf(serverConf):
    if not fileExists(serverConf):
        sys.exit()
    cf = ConfigParser.ConfigParser()
    try:
        cf.read(serverConf)
    except ConfigParser.ParsingError, e:
        print e
        print "请检查服务配置文件： %s" % serverConf
        sys.exit()

    serverNameDict = {}
    optinsDict = {}
    for serverName in cf.sections():
        # print 'serverName:%s' % serverName
        for optins in cf.options(serverName):
            # 取服务名下的对应的配置和参数
            if not confCheck(cf, serverName, optins):
                sys.exit()
            value = cf.get(serverName, optins)
            optinsDict[optins] = value
        serverNameDict[serverName] = optinsDict
        optinsDict = {}
    return serverNameDict


# 本地安装项目初始化
def installServerName(serverName):
    serverNameDict = projectDict[serverName]
    deployDir = serverNameDict["deploydir"]
    # print projectDict
    if os.path.exists(deployDir):
        if dir_is_null(deployDir):
            print "%s 安装成功" % serverName
            return True
        else:
            print "%s 已经安装，请检查!" % serverName
            return False
    else:
        # os.mkdirs(deployDir)
        os.makedirs(deployDir)
        print "%s 安装成功" % serverName
        return True


def getPid(serverName):
    deployDir = projectDict[serverName]["deploydir"]

    cmd = "pgrep -f %snode_modules/.bin/nuxt" % deployDir
    # cmd = "pgrep -f %s/war/" % deployDir
    pid, stderr = execSh(cmd)
    if pid:
        # string(pid,)
        print "取得 PID:%s" % pid
        return int(pid)


def stopServer(serverName):
    # 停止服务 先正常停止，多次检查后 强制杀死！
    pid = getPid(serverName)

    if pid:
        print "服务:%s,即将停止 pid:%s" % (serverName, pid)
        try:
            cmd = "sudo kill -9 %s" % pid
            killstdout, killsterr = execSh(cmd)
            if killstdout:
                print killstdout
            if killsterr:
                print killsterr
            # os.kill(pid, signal.SIGKILL)
            print '停止服务:%s, pid:%s' % (serverName, pid)
        except OSError, e:
            print 'No such as server!', e
        for i in xrange(1, checkTime + 1):
            print "检查服务是否停止， num:%s" % i
            if not getPid(serverName):
                print "服务:%s,停止成功" % serverName
                return True
        if getPid(serverName):
            print "服务:%s 停止失败，请检查服务" % serverName
            return False
    else:
        print "服务:%s,成功停止" % serverName
        return True


def startServer(serverName):
    serverNameDict = projectDict[serverName]
    deploydir = serverNameDict["deploydir"]
    if not os.path.exists(deploydir):
        print "%s is not exits" % deploydir
        # sys.exit()
        return False
    serverlogpath = os.path.join(logsPath, serverName)
    if getPid(serverName):
        print "%s 已经启动,请先停止！ " % serverName
        return False
    else:

        os.chdir(deploydir)
        print "workdir：%s" % os.getcwd()
        print "启动服务：%s" % serverName
        cmd = "%s %s run start >%s.out 2>&1 &" % (nohup,npm, serverlogpath)
        # cmd = "%s %s run start " % (nohup,npm)
        # cmd = "%s %s -Xms%s -Xmx%s -jar %s  >%s.out 2>&1 &" % (nohup,java,xms, xmx, deployjar,serverlogpath)
        print cmd
        # sys.exit()
        stdout, stderr = execSh(cmd)
        if stdout:
            print "stdout:%s" % stdout
        if stderr:
            print "ster:%s" % stderr
        for i in xrange(1, checkTime + 1):
            print "循环检查服务启动状态：%s 次" % i
            time.sleep(checkTime)
            if getPid(serverName):
                pass
        if getPid(serverName):
            # 需要目标服务器 在env 环境找到node执行命令 否则会报错。无法执行远程启动
            print "目标服务尝试执行 'ln /opt/node-v9.5.0-linux-x64/bin/node /usr/bin/node' 在重试"
            print "启动服务：%s 成功" % serverName
            return True
        else:
            print "启动服务： %s 失败" % serverName
            return False


def versionSort(list):
    # 对版本号排序 控制版本的数量
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
    # import unicode
    filePath = unicode(filePath, 'utf8')
    t = os.path.getmtime(filePath)
    # return t
    return TimeStampToTime(t)


# 清理历史多余的备份文件
def cleanHistoryBak(serverName):
    # bakServerDir = getDeploymentTomcatPath(serverName)["bakServerDir"]

    bakServerDir = os.path.join(bakDir, serverName)
    VersinIdList = getVersion(serverName)
    # print VersinIdList
    if VersinIdList:
        if len(VersinIdList) > int(bakNum):
            cleanVersionList = VersinIdList[0:abs(len(VersinIdList) - int(bakNum))]
            for i in cleanVersionList:
                bakWarPath = os.path.join(bakServerDir, "%s.%s") % (serverName, i)
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


def copyFile(sourfile, disfile):
    try:
        print "copy file:%s,to:%s" % (sourfile, disfile)
        shutil.copy2(sourfile, disfile)  # % ( disfile, time.strftime("%Y-%m-%d-%H%M%S"))
    except Exception, e:
        print e,
        sys.exit(1)


def copyDir(sourDir, disDir):
    try:
        print "copy Dir:%s,to:%s" % (sourDir, disDir)
        # shutil.copy2(sourDir, disDir)  # % ( disfile, time.strftime("%Y-%m-%d-%H%M%S"))
        # shutil.copytree(sourDir, disDir)
        cmd = "cp -ar %s %s " %(sourDir, disDir)
        ReturnExec(cmd)
    except Exception, e:
        print e,
        sys.exit(1)


def checkServer(serverName):
    deployDir = projectDict[serverName]["deploydir"]
    if os.path.exists(deployDir):
        return True
    else:
        return False


# 判断目录是否为空
def dir_is_null(path):
    # print os.listdir(path)
    if os.path.exists(path):
        if os.listdir(path):
            # 不为空 False
            return False
    # 是空返回True
    return True


def backWar(serverName):
    # 部署的包
    # init(serverconf)
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
        lastVersinId = [time.strftime("%Y-%m-%d-") + "V1"][-1]

    bakdeployRootWar = os.path.join(bakServerDir, "%s.%sV%s") % (serverName, time.strftime("%Y-%m-%d-"), versionId)

    lastbakdeployRootWar = os.path.join(bakServerDir, "%s.%s") % (serverName, lastVersinId)

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
            print "path %s is null or %s is not exists" % (deployWar, bakdeployRootWar)


def rollBack(serverName, versionId=""):
    # 为方便调用需要出示化服务字典，目前暂无优化，待优化，结合部署脚本使用
    # init(serverconf)

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
        bakdeployWar = os.path.join(bakDir, serverName, "%s.%s") % (serverName, versionId)
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
            if os.path.exists(deployRootWar):
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


# 判断目录是否为空
def dir_is_null(path):
    # print os.listdir(path)
    if os.listdir(path):
        # 不为空 False
        return False
    # 是空返回True
    return True


def main(serverName, branchName, action):
    if action == "init":
        # 主服务项目部署 用代码分支合并，mvn 构建，在主服务器上
        initProject(serverName)

    elif action == "merge":
        # 主服务项目合并分支至master
        mergeBranch(serverName, branchName)

    elif action == "install":
        # 用于远端机器部署项目
        installServerName(serverName)
    elif action == "restart":
        stopServer(serverName)
        startServer(serverName)
    elif action == "start":
        startServer(serverName)
    elif action == "stop":
        stopServer(serverName)
    elif action == "back":
        stopServer(serverName)
        backWar(serverName)
    elif action == "getback":
        versionlist = getVersion(serverName)
        if not versionlist:
            print "%s not back" % serverName
        else:
            print "%s has back version:%s" % (serverName, versionlist)
    elif action == "rollback":
        stopServer(serverName)
        rollBack(serverName)
        startServer(serverName)
    else:
        print "action just [install,init,back,rollback，getback，start,stop,restart]"
        sys.exit()

# 输出服务配置文件中的服务名
def printServerName(projectDict):
    serverNameList = []
    # print projectDict
    for serverName, serverNameDict in projectDict.items():
        print "可执行服务名：%s" % serverName
        serverNameList.append(serverName)
    # 返回服务名列表，可以在后期处理进行排序，考虑服务启动的顺序
    return serverNameList


# 检查文件是否存在
def fileExists(filePath):
    if not os.path.exists(filePath):
        print "文件：%s 不存在，请检查" % filePath
        return False
    return True


def init(serverconf):
    if os.path.exists(serverconf):
        confDict = readConf(serverconf)
        return confDict
    else:
        print "%s is not exists" % serverconf
        print server_conf_str
        sys.exit()



if __name__ == "__main__":

    serverconf = "/python-project/nodeServer.conf"
    # print os.getcwd()
    # sys.exit()
    confDict = init(serverconf)["conf"]
    options, args = getOptions()
    action = options.action
    # version = options.versionId
    serverName = options.serverName
    branchName = options.branchName
    envName = options.envName
    try:
        nodeConf = confDict["node_conf"]
        global bakDir, bakNum, checkTime, logsPath, mvn, java, nohup ,npm
        bakDir = confDict["bak_dir"]
        bakNum = int(confDict["bak_num"])
        checkTime = int(confDict["check_time"])
        logsPath = confDict["logs_path"]
        mvn = confDict["mvn"]
        nohup = confDict["nohup"]
        npm = confDict["npm"]
        # node = confDict["node"]
    except Exception, e:
        print "%s 错误" % e
        sys.exit()
    if not os.path.exists(logsPath):
        os.makedirs(logsPath)
    if not os.path.exists(bakDir):
        os.makedirs(bakDir)
    if os.path.exists(nodeConf):
        projectDict = readConf(nodeConf)
        # print projectDict
    else:
        print "%s is not exists" % nodeConf
        print jar_conf_str
        sys.exit()
    if not action:
        print "参数执行操作 -a action [install,init,back,rollback，getback，start,stop,restart]"
        sys.exit()
    elif not serverName:
        print "参数服务名 -n servername "
        printServerName(projectDict)
        sys.exit()

    else:
        # if action == "start" or action == "restart" or action == "rollback":
        #     if not envName:
        #         print "参数执行操作 -e envName [dev,test,pro]"
        #         sys.exit()

        if serverName == "all":
            # 进行升序排列
            serverlist = sorted(projectDict.keys())
            for serName in serverlist:
                main(serName, branchName, action)
        else:
            if not projectDict.has_key(serverName):
                print "没有服务名：%s" % serverName
                printServerName(projectDict)
                sys.exit()
            main(serverName, branchName, action)
