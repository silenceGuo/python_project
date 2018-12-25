#!/usr/bin/env python
#！-*-coding:utf-8 -*-
#!@Date    : 2018/11/9 0009 下午 17:08
#!@Author : Damon.guo
#!@File   : updateStandard.py

import os
import sys
import time
import ConfigParser
import back_kilimall as back
from optparse import OptionParser
from subprocess import PIPE,Popen
import json

reload(sys)
sys.setdefaultencoding('utf-8')
serverConf = "/python-project/standard1.conf"  # 部署配置文件路径
checktime = 3
#日志输出路径
logpath = "/logger/"


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


#初始化项目主应用可用于php部署，
def initProject(serverName):

    # 新机器 或者新目录项目部署
    print "master install:%s" % serverName
    deployDir = projectDict[serverName]["deploydir"]
    gitUrl = projectDict[serverName]["giturl"]
    if not os.path.exists(deployDir):
       os.mkdir(deployDir)
    os.chdir(deployDir)
    print "部署路径：",os.getcwd()
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
        print 80*"#"
        print "out:%s " % stdout
    if stderr:
        print 80*"#"
        print "err:%s" % stderr

def readStdin():
    input_str = raw_input("确认执行操作：Y/N")
    return input_str.strip().lower()

# 合并分支至master
def mergeBranch(serverName,branchName):

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

#检查配置文件
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

#读取配置文件
def readConf(serverConf):
    if not fileExists(serverConf):
        sys.exit()
    cf = ConfigParser.ConfigParser()
    try:
        cf.read(serverConf)
    except ConfigParser.ParsingError,e:
        print e
        print "请检查服务配置文件： %s" % serverConf
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
    jar = projectDict[serverName]["jar"]

    jarName = jar.split("/")[-1]
    deployjar = os.path.join(deployDir, jarName)

    # cmd = "pgrep -f %s" % deployDir
    cmd = "pgrep -f %s" % deployjar
    # cmd = "pgrep -f %s/war/" % deployDir
    pid, stderr = execSh(cmd)
    if pid:
        #string(pid,)
        print "取得 PID:%s" % pid
        return int(pid)

def stopServer(serverName):
    # 停止服务 先正常停止，多次检查后 强制杀死！
    deployDir = projectDict[serverName]["deploydir"]

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
            #os.kill(pid, signal.SIGKILL)
            print '停止服务:%s, pid:%s' % (serverName, pid)
        except OSError, e:
            print 'No such as server!', e
        for i in xrange(1, checktime+1):
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

    jar = serverNameDict["jar"]
    jarName = jar.split("/")[-1]

    deployjar = os.path.join(deploydir, jarName)
    if not os.path.exists(deployjar):
        print "%s is not exits" % deployjar
        # sys.exit()
        return False
    # conf = serverNameDict["conf"]
    try:
         xms = serverNameDict["xms"]
         xmx = serverNameDict["xmx"]
    except:
        print "配置文件中为配置java内存参数参数默认512m "
        xms = "512m"
        xmx = "512m"

    serverlogpath = os.path.join(logpath, serverName)
    if getPid(serverName):
        print "%s 已经启动,请先停止！ " % serverName
        return False
    else:
        print "启动服务：%s" % serverName
        cmd = "/usr/bin/nohup /app/jdk1.8.0_121/bin/java -Xms%s -Xmx%s -jar %s >%s.out 2>&1 &" % (xms, xmx, deployjar,serverlogpath)
        print cmd
        stdout,stderr = execSh(cmd)
        if stdout:
            print "stdout:%s" % stdout
        if stderr:
            print "ster:%s" % stderr
        for i in xrange(1, checktime+1):
            print "循环检查服务启动状态：%s 次" % i
            time.sleep(checktime)
            if getPid(serverName):
                pass
        if getPid(serverName):
            print "启动服务：%s 成功" % serverName
            return True
        else:
            print "启动服务： %s 失败" % serverName
            return False

#判断目录是否为空
def dir_is_null(path):
    # print os.listdir(path)
    if os.listdir(path):
        # 不为空 False
        return False
    #是空返回True
    return True

def main(serverName,branchName,action):

    if action == "init":
        # 主服务项目部署 用代码分支合并，mvn 构建，在主服务器上
        if serverName == "all":
            for serName, dict_sub in projectDict.iteritems():
                initProject(serName)
        else:
            initProject(serverName)

    elif action == "merge":
        # 主服务项目合并分支至master
        mergeBranch(serverName, branchName)

    elif action == "install":
        # 用于远端机器部署项目
        if serverName == "all":
            for serName, dict_sub in projectDict.iteritems():
                installServerName(serName)
        else:
             installServerName(serverName)

    elif action == "restart":
        if serverName == "all":
            for serName, dict_sub in projectDict.iteritems():
                stopServer(serName)
                startServer(serName)
        else:
            stopServer(serverName)
            startServer(serverName)

    elif action == "start":
        if serverName == "all":
            for serName, dict_sub in projectDict.iteritems():
                startServer(serName)
        else:
            startServer(serverName)

    elif action == "stop":
        if serverName == "all":
            for serName, dict_sub in projectDict.iteritems():
                stopServer(serName)
        else:
            stopServer(serverName)

    elif action == "back":
        # 调用单独的备份脚本
        if serverName == "all":
            for serName, dict_sub in projectDict.iteritems():
                back.backWar(serName)
        else:
            back.backWar(serverName)
    elif action == "getback":
        # 调用单独的备份脚本
        if serverName == "all":
            for serName, dict_sub in projectDict.iteritems():
                versionlist = back.getVersion(serName)
                if not versionlist:
                    print "%s not back" % serName
                else:
                    print "%s has back version:%s" % (serName, versionlist)
        else:
            versionlist = back.getVersion(serverName)
            if not versionlist:
                print "%s not back" % serverName
            else:
                print "%s has back version:%s" % (serverName, versionlist)
    elif action == "rollback":
        if serverName == "all":
            for serName, dict_sub in projectDict.iteritems():
                back.rollBack(serName)
        else:
            back.rollBack(serverName)
    else:
        print "action just [install,init,back,rollback，getback，start,stop,restart]"
        sys.exit()

# 输出服务配置文件中的服务名
def printServerName(projectDict):
    serverNameList = []
    # print projectDict
    for serverName, serverNameDict in projectDict.items():
        if serverName == "startServerList" or serverName == "conf":
            continue
        print "可执行服务名：%s" %  serverName
        serverNameList.append(serverName)
    #返回服务名列表，可以在后期处理进行排序，考虑服务启动的顺序
    return serverNameList

#检查文件是否存在
def fileExists(filePath):
    if not os.path.exists(filePath):
        print "文件：%s 不存在，请检查" % filePath
        return False
    return True


def init():
    if not os.path.exists(logpath):
        print "初始化日志目录"
        os.makedirs(logpath)

if __name__ == "__main__":
    # 备份 回滚 历史版本处理（可以使用调用back.py)
    init()
    # back_kilimall.backWA
    projectDict = readConf(serverConf)
    # ansibleHostDict = readConfAnsible(ansibileHostFile)

    options, args = getOptions()
    action = options.action
    # version = options.versionId
    serverName = options.serverName
    branchName = options.branchName
    if not action:
        print "参数执行操作 -a action [install,init,back,rollback，getback，start,stop,restart]"
        sys.exit()
    elif not serverName:
        print "参数服务名 -n servername "
        printServerName(projectDict)
        sys.exit()
    else:

        startlist = projectDict["startServerList"]
        if serverName == "all":
            for serName in startlist:
                main(serName, branchName, action)

            # for serName, serverNameDict in projectDict.items():
            #
            #     main(serName, branchName, action)

        else:
            if not projectDict.has_key(serverName):
                print "没有服务名：%s" % serverName
                printServerName(projectDict)
                sys.exit()
            main(serverName, branchName, action)
