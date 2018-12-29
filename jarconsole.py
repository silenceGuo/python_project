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
import updateJarService
import back_kilimall as back
import json
reload(sys)
sys.setdefaultencoding('utf-8')
serverConf = "standard1.conf"  # 部署配置文件路径
checktime = 3
ansibileHostFile = "/etc/ansible/hosts" #ansible 主机文件
maven_home = "/app/apache-maven-3.5.0/bin/mvn"
# 定义源端python脚本路径 和执行花鸟卷
python_dir = "/python-project/updateJarService.py"
python_home = "/usr/bin/python"
#日志输出路径
logpath = "/logger/"

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
    print serverName
    print serverNameDict
    # deploydir = serverNameDict["deploydir"]
    deploynode = serverNameDict["deploygroupname"]

    cmd = "ansible %s -i %s -m shell -a '%s %s -a %s -n %s'" % (
    deploynode, ansibileHostFile, python_home, python_dir,action, serverName)
    print cmd
    ReturnExec(cmd)

def delpoy_install(serverName):

    serverNameDict = projectDict[serverName]
    deploydir = serverNameDict["deploydir"]
    deploynode = serverNameDict["deploygroupname"]

    cmd = "ansible %s -i %s -m shell -a '%s %s -a install -n %s'" % (deploynode,ansibileHostFile,python_home, python_dir, serverName)
    print cmd
    ReturnExec(cmd)
    # stdout stder =

    # execSh(cmd)

def deploy_node(serverName):
    print "发送文件至远程节点 "
    nodeName = projectDict[serverName]["deploygroupname"]
    deployDir = projectDict[serverName]["deploydir"]
    # print deployDir
    # sys.exit()
    deployFile = projectDict[serverName]["jar"]
    # deployFile = os.path.join(deployDir,deployFile)
    # if ansibleDirIsExists(nodeName)
    copyFILE = 'ansible %s -i %s -m copy -a "src=%s dest=%s "' % (nodeName, ansibileHostFile, deployFile, deployDir)
    ReturnExec(copyFILE)

def start_node(serverName):
    serverNameDict = projectDict[serverName]
    deploydir = serverNameDict["deploydir"]
    deploynode = serverNameDict["deploygroupname"]
    cmd = "ansible %s -i %s -m shell -a '%s %s -a start -n %s'" % (
    deploynode, ansibileHostFile, python_home, python_dir, serverName)
    print cmd
    ReturnExec(cmd)

def stop_node(serverName):
    serverNameDict = projectDict[serverName]
    deploydir = serverNameDict["deploydir"]
    deploynode = serverNameDict["deploygroupname"]
    cmd = "ansible %s -i %s -m shell -a '%s %s -a stop -n %s'" % (
        deploynode, ansibileHostFile, python_home, python_dir, serverName)
    print cmd
    ReturnExec(cmd)

def back_node(serverName):
    serverNameDict = projectDict[serverName]
    deploydir = serverNameDict["deploydir"]
    deploynode = serverNameDict["deploygroupname"]

    cmd = "ansible %s -i %s -m shell -a '%s %s -a back -n %s'" % (
        deploynode, ansibileHostFile, python_home, python_dir, serverName)
    print cmd
    ReturnExec(cmd)

def getback_node(serverName):
    serverNameDict = projectDict[serverName]
    deploydir = serverNameDict["deploydir"]
    deploynode = serverNameDict["deploygroupname"]

    cmd = "ansible %s -i %s -m shell -a '%s %s -a getback -n %s'" % (
        deploynode, ansibileHostFile, python_home, python_dir, serverName)
    print cmd
    ReturnExec(cmd)

def rollbakc_node(serverName):
    serverNameDict = projectDict[serverName]
    deploydir = serverNameDict["deploydir"]
    deploynode = serverNameDict["deploygroupname"]

    cmd = "ansible %s -i %s -m shell -a '%s %s -a rollback -n %s'" % (
        deploynode, ansibileHostFile, python_home, python_dir, serverName)
    print cmd
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

# jar 文件mavn构建
def buildMaven(serverName):

    serverNameDict = projectDict[serverName]
    deployDir = serverNameDict["deploydir"]
    os.chdir(deployDir)
    print os.getcwd()
     # = serverNameDict["deploydir"]
    cmd = "%(maven_home)s clean && %(maven_home)s install -Dmaven.test.skip=true" % {"maven_home": maven_home}
    print cmd
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
        updateJarService.initProject(serverName)
    elif action == "merge":
        # 主服务项目合并分支至master
        updateJarService.mergeBranch(serverName, branchName)
    elif action == "install":
        # 用于远端机器部署项目
        execAnsible(serverName, action)
    elif action == "build":
        buildMaven(serverName)
    elif action == "deploy":
        execAnsible(serverName, "back")
        # 部署新包至目标节点
        deploy_node(serverName)
        execAnsible(serverName, "stop")
        execAnsible(serverName, "start")
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
def remoteExec(servername,action):
    serverNameDict = projectDict[serverName]
    # jar = serverNameDict["jar"]
    deploydir = serverNameDict["deploydir"]
    deploydir = "/data/init/"

    nodeName = projectDict[serverName]["deploygroupname"]

    # print deployDir
    # sys.exit()
    deployFile = projectDict[serverName]["jar"]

    if action == 'back':
        cmd = ''' ansible %s -i %s -m shell -a 'cd %s;sudo ./updateJarService.py -n %s -a back' --sudo ''' % (nodeName, ansibileHostFile, deploydir, servername)
        stdout,stderr = execSh(cmd)
        if stdout:
            print stdout
        if stderr:
            print stderr
    elif action == 'rollback':
        cmd = ''' ansible %s -i %s -m shell -a 'cd %s;sudo ./updateJarService.py -n %s -a rollback' --sudo ''' % (nodeName, ansibileHostFile, deploydir, servername)
        stdout, stderr = execSh(cmd)
        if stdout:
            print stdout
        if stderr:
            print stderr
    elif action == 'getback':
        cmd = ''' ansible %s -i %s -m shell -a 'cd %s;sudo ./updateJarService.py -n %s -a getback' ''' % (nodeName, ansibileHostFile, deploydir, servername)
        stdout, stderr = execSh(cmd)
        if stdout:
            print stdout
        if stderr:
            print stderr
    elif action == 'deploy':
        cmd_back = ''' ansible %s -i %s -m shell -a 'cd %s;sudo ./updateJarService.py -n %s -a back' --sudo ''' % (nodeName, ansibileHostFile, deploydir, servername)
        stdout, stderr = execSh(cmd_back)
        if stdout:
            print stdout
        if stderr:
            print stderr
        stop_cmd = ''' ansible %s -i %s -m shell -a 'cd %s;sudo ./updateJarService.py -n %s -g %s -a stop' ''' % (nodeName, ansibileHostFile, deploydir, servername)
        stdout, stderr = execSh(stop_cmd)
        if stdout:
            print stdout
        if stderr:
            print stderr
        start_cmd = ''' ansible %s -i %s -m shell -a 'cd %s;sudo ./updateJarService.py -n %s -g %s -a start' ''' % (nodeName, ansibileHostFile, deploydir, servername)
        stdout, stderr = execSh(start_cmd)
        if stdout:
            print stdout
        if stderr:
            print stderr
    else:
        pass



if __name__ == "__main__":
    # 备份 回滚 历史版本处理（可以使用调用back.py) back.py 可以在目标服务器单独执行
    projectDict = updateJarService.readConf(serverConf)
    options, args = updateJarService.getOptions()
    action = options.action
    # version = options.versionId
    serverName = options.serverName
    branchName = options.branchName
    if not action:
        print "参数执行操作 -a action [install,init,back,rollback，getback，start,stop,restart]"
        sys.exit()
    elif not serverName:
        print "参数服务名 -n servername "
        updateJarService.printServerName(projectDict)
        sys.exit()
    else:
        # print "其他错误！"
        startlist = projectDict["startServerList"]
        print startlist
        sys.exit()
        if serverName == "all":
            for serName in startlist:
                main(serName, branchName, action)

        # if serverName == "all":
        #     for serName, serverNameDict in projectDict.items():
        #         main(serName, branchName, action)
        else:
            if not projectDict.has_key(serverName):
                print "没有服务名：%s" % serverName
                updateJarService.printServerName(projectDict)
                sys.exit()
            main(serverName, branchName, action)