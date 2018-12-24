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
import JarService
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

def execAnsible(serverName,action):
    serverNameDict = projectDict[serverName]
    print " server:%s is %s now " % (serverName,action)
    # deploydir = serverNameDict["deploydir"]
    deploynode = serverNameDict["deploygroupname"]

    cmd = "ansible %s -i %s -m shell -a '%s %s -a %s -n %s -e %s'" % (
        deploynode, ansibleHost, python, remote_py, action, serverName, envName)
    print cmd
    ReturnExec(cmd)

def deploy_node(serverName):
    print "发送文件至远程节点 "
    nodeName = projectDict[serverName]["deploygroupname"]
    deployDir = projectDict[serverName]["deploydir"]
    buildDir = projectDict[serverName]["builddir"]
    # print deployDir
    # sys.exit()
    deployFile = projectDict[serverName]["jar"]

    # deployFile = os.path.join(deployDir,deployFile)
    # if ansibleDirIsExists(nodeName)
    copyFILE = 'ansible %s -i %s -m copy -a "src=%s dest=%s "' % (nodeName, ansibleHost, deployFile, deployDir)
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

# jar 文件mavn构建
def buildMaven(serverName):

    serverNameDict = projectDict[serverName]
    # deployDir = serverNameDict["deploydir"]
    buildDir = serverNameDict["builddir"]
    os.chdir(buildDir)
    print "workdir : %s" % os.getcwd()
     # = serverNameDict["deploydir"]
    cmd = "%(mvn)s clean && %(mvn)s install -Dmaven.test.skip=true" % {"mvn": mvn}
    print cmd
    print "构建服务：%s" %serverName
    # sys.exit()
    stdout, stderr = execSh(cmd)
    if stdout:
        print stdout
    if stderr:
        print stderr



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

def ansibileSyncDir(ip,sourceDir,destDir):
    SyncDir = "ansible %s -m synchronize -a 'src=%s dest=%s'" % (ip, sourceDir, destDir)

    """
    ansible test -m synchronize -a 'src=/etc/yum.repos.d/epel.repo dest=/tmp/epel.repo' -k                  # rsync 传输文件
    ansible test -m synchronize -a 'src=/tmp/123/ dest=/tmp/456/ delete=yes' -k                             # 类似于 rsync --delete
    ansible test -m synchronize -a 'src=/tmp/123/ dest=/tmp/test/ rsync_opts="-avz,--exclude=passwd"' -k    # 同步文件，添加rsync的参数-avz，并且排除passwd文件
    ansible test -m synchronize -a 'src=/tmp/test/abc.txt dest=/tmp/123/ mode=pull' -k                      # 把远程的文件，拉到本地的/tmp/123/目录下　　
    """
    ReturnExec(SyncDir)

# 更新远程节点的代码适用php
def ansibleUpdateGit(serverName):
    print "更新主代码git代码"
    nodeName = projectDict[serverName]["deploygroupname"]
    deployDir = projectDict[serverName]["deploydir"]
    UpdateDir = 'ansible %s -i %s -m shell -a "cd %s;sudo git pull"' % (nodeName, ansibileHostFile, deployDir)
    ReturnExec(UpdateDir)

def ansibileCopyZipFile(serverName):
    nodeName = projectDict[serverName]["deploygroupname"]
    deployDir = projectDict[serverName]["deploydir"]

    deployFile = projectDict[serverName]["jar"]
    CopyZipFile = "ansible %s -i %s -m unarchive -a 'src=%s dest=%s copy=yes owner=tomcat group=tomcat backup=yes'" % (nodeName, ansibileHostFile, deployFile, deployDir)
    ReturnExec(CopyZipFile)

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

def main(serverName,branchName,action):

    if action == "init":
        # 主服务项目部署 用代码分支合并，mvn 构建，在主服务器上
        JarService.initProject(serverName)
    elif action == "merge":
        # 主服务项目合并分支至master
        JarService.mergeBranch(serverName, branchName)
    elif action == "install":
        # 用于远端机器部署项目
        execAnsible(serverName, action)
    elif action == "build":
        buildMaven(serverName)
    elif action == "deploy":
        execAnsible(serverName, "back")
        # 部署新包至目标节点
        deploy_node(serverName)
        execAnsible(serverName, action)
    elif action == "restart":
        execAnsible(serverName, action)
    elif action == "start":
        execAnsible(serverName, action)
    elif action == "stop":
        execAnsible(serverName, action)
    elif action == "back":
        execAnsible(serverName, action)
    elif action == "getback":
        execAnsible(serverName, action)
    elif action == "rollback":
        execAnsible(serverName, action)
    else:
        print "action just [install,init,back,rollback，getback，start,stop,restart]"
        sys.exit()

if __name__ == "__main__":
    serverconf = "server.conf"
    confDict = JarService.init(serverconf)["conf"]
    # print confDict
    global mvn, java, nohup,ansibleHost,python,remote_py
    # bakDir = confDict["bak_dir"]
    # bakNum = confDict["bak_num"]
    # checkTime = confDict["check_time"]
    # logsPath = confDict["logs_path"]
    mvn = confDict["mvn"]
    remote_py = confDict["remote_py"]
    python = confDict["python"]
    java = confDict["java"]
    nohup = confDict["nohup"]
    ansibleHost = confDict["ansibile_host"]
    jarConf = confDict["jar_conf"]
    projectDict = JarService.readConf(jarConf)
    options, args = JarService.getOptions()
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
        JarService.printServerName(projectDict)
        sys.exit()

    else:
        if action == "start" or action == "restart" or action == "rollback":
            if not envName:
                print "参数执行操作 -e envName [dev,test,pro]"
                sys.exit()
            # else:
            #     print "ll5"
        if serverName == "all":
            # 进行升序排列
            serverlist = sorted(projectDict.keys())
            for serName in serverlist:
                main(serName, branchName, action)
        else:
            if not projectDict.has_key(serverName):
                print "没有服务名：%s" % serverName
                JarService.printServerName(projectDict)
                sys.exit()
            main(serverName, branchName, action)