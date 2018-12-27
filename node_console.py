#!/usr/bin/env python
#！-*-coding:utf-8 -*-
#!@Date    : 2018/12/20 0020 下午 17:05
#!@Author : Damon.guo
#!@File   : jarconsole.py.py
import os
import sys
import time
import ConfigParser
from optparse import OptionParser
from subprocess import PIPE,Popen
import nodeService
import json
reload(sys)
sys.setdefaultencoding('utf-8')

def ReturnExec(cmd):
    stdout, stderr = execSh(cmd)
    if stdout:
        print 80*"#"
        print "out:%s " % stdout
    if stderr:
        print 80*"#"
        print "err:%s" % stderr

def execSh(cmd):
    # 执行SH命令
    try:
        print "执行ssh 命令 %s" % cmd
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    except Exception, e:
        print e,
        sys.exit()
    return p.communicate()

def execAnsible(serverName,action,env):
    serverNameDict = projectDict[serverName]
    print " server:%s is %s on %s now" % (serverName, env, action)
    # deploydir = serverNameDict["deploydir"]
    if env == "dev":
        deploynode = serverNameDict["devnodename"]
    if env == "test":
        deploynode = serverNameDict["testnodename"]
    if env == "pro":
        deploynode = serverNameDict["pronodename"]

    cmd = "ansible %s -i %s -m shell -a '%s %s -a %s -n %s -e %s'" % (deploynode, ansibleHost, python, remote_py, action, serverName, env)

    ReturnExec(cmd)



#读取ansibel host 文件解析
def readConfAnsible(file):
    if not fileExists(file):
        sys.exit()
    cf = ConfigParser.ConfigParser(allow_no_value=True)
    cf.read(file)
    try:
        cf.read(file)
    except ConfigParser.ParsingError, e:
        print e
        print "请检查ansible服务主机文件 %s" % file
        sys.exit()
    groupNameDict = {}
    for groupName in cf.sections():
        iplist = []
        # print cf.options(groupName)
        for ipstr in cf.options(groupName):
            ip = ipstr.split(" ansible_ssh_user")[0]
            iplist.append(ip)
            print groupName, ip
        groupNameDict[groupName] = iplist
    return groupNameDict

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

def gitupdate(serverName):
    serverNameDict = projectDict[serverName]
    # deployDir = serverNameDict["deploydir"]
    buildDir = serverNameDict["builddir"]

    os.chdir(buildDir)
    if not checkMaster():
        checkout_m_cmd = "git checkout master"
        print "切换至master分支"
        ReturnExec(checkout_m_cmd)

    print "获取 最新master分支"
    pull_m_cmd = "git pull"
    stdout, stderr = execSh(pull_m_cmd)
    # 判断是否有git 执行错误
    return isNoErr(stdout, stderr)


def isNoErr(stdout, stderr):
    # 有错误返回false
    if not "error" or "fatal" in stdout:
        print "stdout:%s" % stdout

        return False
    elif not "error" or "fatal" in stderr:
        print "stderr:%s" % stderr
        return False
    else:
        print "stdout:%s" % stdout
        print "stderr:%s" % stderr
        return True

# jar 文件mavn构建
def buildNode(serverName,env):

    serverNameDict = projectDict[serverName]
    # deployDir = serverNameDict["deploydir"]
    buildDir = serverNameDict["builddir"]
    print gitupdate(serverName)
    if not gitupdate(serverName):
        print 'git is updata err'
        sys.exit()
    os.chdir(buildDir)
    print "workdir : %s" % os.getcwd()
    cmd_install = "%s install" % npm
    stdout, stderr = execSh(cmd_install)

    if not isNoErr(stdout, stderr):
        print "%s exc err" % cmd_install
        sys.exit()

    cmd = "%s run %s" % (npm, env)

    print "构建服务：%s" % serverName
    # sys.exit()
    stdout, stderr = execSh(cmd)
    return isNoErr(stdout, stderr)
# 将构建完成的文件同步到目标服务器
def delployDir(serverName,env):
    serverNameDict = projectDict[serverName]
    deployDir = serverNameDict["deploydir"]
    buildDir = serverNameDict["builddir"]
    if env == "dev":
        deploynode = serverNameDict["devnodename"]
    if env == "test":
        deploynode = serverNameDict["testnodename"]
    if env == "pro":
        deploynode = serverNameDict["pronodename"]

    copyFILE = "ansible %s -i %s -m synchronize -a 'src=%s dest=%s delete=yes'" % (deploynode, ansibleHost, buildDir, deployDir)
    ReturnExec(copyFILE)

#读取ansibel host 文件解析
def readConfAnsible(file):
    if not fileExists(file):
        sys.exit()
    cf = ConfigParser.ConfigParser(allow_no_value=True)
    cf.read(file)
    try:
        cf.read(file)
    except ConfigParser.ParsingError, e:
        print e
        print "请检查ansible服务主机文件 %s" % file
        sys.exit()
    groupNameDict = {}
    for groupName in cf.sections():
        iplist = []
        # print cf.options(groupName)
        for ipstr in cf.options(groupName):
            ip = ipstr.split(" ansible_ssh_user")[0]
            iplist.append(ip)
            print groupName, ip
        groupNameDict[groupName] = iplist
    return groupNameDict

# 解析 ansible 输出
def parseAnsibleOut(stdout):
    try:
        splitList = stdout.split("SUCCESS => ")
        d = splitList[1].strip()
        t = json.loads(d)
        exists = t["stat"]["exists"]
        return exists
    except:
        pass

def ansibileSyncDir(node,sourceDir,destDir):

    SyncDir = "ansible %s -m synchronize -a 'src=%s dest=%s delete=yes'" % (node, sourceDir, destDir)

    """
    ansible test -m synchronize -a 'src=/etc/yum.repos.d/epel.repo dest=/tmp/epel.repo' -k                  # rsync 传输文件
    ansible test -m synchronize -a 'src=/tmp/123/ dest=/tmp/456/ delete=yes' -k                             # 类似于 rsync --delete
    ansible test -m synchronize -a 'src=/tmp/123/ dest=/tmp/test/ rsync_opts="-avz,--exclude=passwd"' -k    # 同步文件，添加rsync的参数-avz，并且排除passwd文件
    ansible test -m synchronize -a 'src=/tmp/test/abc.txt dest=/tmp/123/ mode=pull' -k                      # 把远程的文件，拉到本地的/tmp/123/目录下　　
    """
    ReturnExec(SyncDir)

def ansibleDirIsExists(ip,filepath):
    # 判断远程 文件或者目录是否存在
    cmd = "ansible %s -m stat -a 'path=%s' -o " % (ip, filepath)
    stdout, stederr = execSh(cmd)
    reslust = parseAnsibleOut(stdout)

    if reslust:
        print "%s 已经存在:%s" % (filepath,ip)
        return True
    elif reslust == None:
        print "%s 其他错误在: %s " % (filepath, ip)
        return None
    else:
        print "%s 不存在: %s " % (filepath, ip)
        return False

#检查文件是否存在
def fileExists(filePath):
    if not os.path.exists(filePath):
        print "文件：%s 不存在，请检查" % filePath
        return False
    return True
# 初始化项目主应用可用于php部署，
def initProject(serverName):
    # 新机器 或者新目录项目部署

    print "master install:%s" % serverName
    print projectDict
    builddir = projectDict[serverName]["builddir"]
    if not os.path.exists(builddir):
        os.makedirs(builddir)
    gitUrl = projectDict[serverName]["giturl"]
    if not os.path.exists(builddir):
        os.mkdir(builddir)
    os.chdir(builddir)
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

def readStdin():
    input_str = raw_input("确认执行操作：Y/N")
    return input_str.strip().lower()
# 合并分支至master
def mergeBranch(serverName, branchName):

    builddir = projectDict[serverName]["builddir"]
    fetch_cmd = "git fetch origin %s" % branchName
    checkout_b_cmd = "git checkout %s" % branchName
    pull_cmd = "git pull"
    checkout_m_cmd = "git checkout master"
    merge_cmd = "git merge origin/%s" % branchName
    push_cmd = "git push origin master"
    try:
        print "切换工作目录"
        print builddir
        os.chdir(builddir)  # 切换工做目录
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

def main(serverName,branchName,action,env):

    if action == "init":
        # 主服务项目部署 用代码分支合并，mvn 构建，在主服务器上
        initProject(serverName)
    elif action == "merge":
        # 主服务项目合并分支至master
        mergeBranch(serverName, branchName)
    elif action == "install":
        # 用于远端机器部署项目
        execAnsible(serverName, action, env)
    elif action == "build":
         buildNode(serverName,env)
    elif action == "deploy":
        buildNode(serverName, env)

        execAnsible(serverName, "stop", env)
        execAnsible(serverName, "back", env)
        # 部署新包至目标节点
        delployDir(serverName, env)
        execAnsible(serverName, "start", env)
    elif action == "restart":
        execAnsible(serverName, action, env)
    elif action == "start":
        execAnsible(serverName, action,env)
    elif action == "stop":
        execAnsible(serverName, action, env)
    elif action == "back":
        execAnsible(serverName, action, env)
    elif action == "getback":
        execAnsible(serverName, action, env)
    elif action == "rollback":
        execAnsible(serverName, action, env)
    else:
        print "action just [install,init,back,rollback，getback，start,stop,restart]"
        sys.exit()

if __name__ == "__main__":
    serverconf = "nodeServer.conf"
    confDict = nodeService.init(serverconf)["conf"]
    # print confDict
    global mvn, java, nohup,ansibleHost,python,remote_py

    npm = confDict["npm"]
    remote_py = confDict["remote_py"]
    python = confDict["python"]
    nohup = confDict["nohup"]
    ansibleHost = confDict["ansibile_host"]
    nodeConf = confDict["node_conf"]
    projectDict = nodeService.readConf(nodeConf)
    options, args = nodeService.getOptions()
    action = options.action
    # version = options.versionId
    serverName = options.serverName
    branchName = options.branchName
    envName = options.envName
    if not action:
        print "参数执行操作 -a action [install,init,back,rollback，getback，start,stop,restart]"
        sys.exit()
    elif not serverName:
        print "参数服务名 -n servername "
        nodeService.printServerName(projectDict)
        sys.exit()
    elif not envName:
        print "参数执行操作 -e envName [dev,test,pro]"
        sys.exit()
    else:
        if not envName in ["dev","test","pro"]:
            print "参数执行操作 -e envName [dev,test,pro]"
            sys.exit()
        if serverName == "all":
            # 进行升序排列
            serverlist = sorted(projectDict.keys())
            for serName in serverlist:
                main(serName, branchName, action, envName)
        else:
            if not projectDict.has_key(serverName):
                print "没有服务名：%s" % serverName
                nodeService.printServerName(projectDict)
                sys.exit()
            main(serverName, branchName, action, envName)