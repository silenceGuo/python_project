#!/usr/bin/env python
#！-*-coding:utf-8 -*-
#!@Date    : 2018/11/9 0009 下午 17:08
#!@Author : Damon.guo
#!@File   : updateStandard.py

import os
import sys
import time
import ConfigParser
from optparse import OptionParser
from subprocess import PIPE,Popen
import json

reload(sys)
sys.setdefaultencoding('utf-8')
serverConf = "server_liunx.conf"  # 部署配置文件路径
checktime = 3
ansibileHostFile = "/etc/ansible/hosts" #ansible 主机文件

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
    stdout,stderr = execSh(cmd)
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
    stdout,stderr = execSh(fetch_cmd)
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

#读取ansibel host 文件解析
def readConfAnsible(file):
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

# 本地安装项目初始化
def installServerName(serverName):
    deployDir = projectDict[serverName]["deploydir"]

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
    nodeName = projectDict[serverName]["deploynodename"]
    deployDir = projectDict[serverName]["deploydir"]
    UpdateDir = 'ansible %s -i %s -m shell -a "cd %s;sudo git pull"' % (nodeName, ansibileHostFile, deployDir)
    ReturnExec(UpdateDir)

def ansibileCopyFile(serverName):
    print "发送文件至远程节点 "
    nodeName = projectDict[serverName]["deploynodename"]
    deployDir = projectDict[serverName]["deploydir"]
    deployFile = projectDict[serverName]["deployfile"]
    # deployFile = os.path.join(deployDir,deployFile)
    copyFILE = 'ansible %s -i %s -m copy -a "src=%s dest=%s owner=nobody group=nobody backup=yes"' % (nodeName, ansibileHostFile, deployFile, deployFile)
    ReturnExec(copyFILE)


def ansibileCopyZipFile(serverName):
    nodeName = projectDict[serverName]["deploynodename"]
    deployDir = projectDict[serverName]["deploydir"]
    deployFile = projectDict[serverName]["deployfile"]
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

def getPid(serverName):
    deployDir = projectDict[serverName]["deploydir"]
    cmd = "pgrep -f %s" % deployDir
    # cmd = "pgrep -f %s/war/" % deployDir
    pid, stderr = execSh(cmd)
    if pid:
        #string(pid,)
        print "取得 PID:%s" % pid
        return int(pid)

def stopServer(serverName):
    # 停止服务 先正常停止，多次检查后 强制杀死！
    deployDir = projectDict[serverName]["deploydir"]
    # shutdown = os.path.join(deployDir, "bin/shutdown.sh")
    # cmd = "sudo su - tomcat -c '/bin/bash %s'" % shutdown

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
    jar = serverNameDict["jar"]
    deploydir = serverNameDict["deploydir"]
    conf = serverNameDict["conf"]
    logpath = os.path.join(deploydir,serverName,)
    if getPid(serverName):
        print "%s 已经启动,请先停止！ " % serverName
        return False
    else:
        print "启动服务：%s" % serverName
        cmd = """
        nohup  java -Xms256m -Xmx256m -jar  -Dspring.config.location=%s,classpath:/application-dev.properties %s >%s.out 2>&1 & 
        """ % (jar, conf, logpath)
        print cmd
        for i in xrange(1, checktime+1):
            print "循环检查服务启动状态：%s 次" % i
            if getPid(serverName):
                pass
        if getPid(serverName):
            print "启动服务：%s 成功" % serverName
            return True
        else:
            print "启动服务： %s 失败" % serverName
            return False

# jar 文件mavn构建
def buildMaven(serverName):
    serverNameDict = projectDict[serverName]
    deployDir = serverNameDict["deploydir"]
     # = serverNameDict["deploydir"]
    cmd = "mvn "
    stdout ,stderr = execSh(cmd)
    if stdout:
        print stdout
    if stderr:
        print stderr

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

    elif action == "deploy":
        # 部署新的代码至源端机器 copy jar包至目标节点
        if serverName == "all":
            for serName, dict_sub in projectDict.iteritems():
                ansibileCopyFile(serName)
        else:
            ansibileCopyFile(serverName)

    elif action == "restart":
        stopServer(serverName)
    else:
        print "action just [init ,install ,merge,deploy,restart]"
        sys.exit()

# 输出服务配置文件中的服务名
def printServerName(projectDict):
    serverNameList = []
    for serverName, serverNameDict in projectDict.items():
        print "可执行为服务名：%s" %  serverName
        serverNameList.append(serverName)
    #返回服务名列表，可以在后期处理进行排序，考虑服务启动的顺序
    return serverNameList


if __name__ == "__main__":
    # 未完成 启动 调试。 备份 回滚 历史版本处理（可以使用back.py)

    projectDict = readConf(serverConf)
    ansibleHostDict = readConfAnsible(ansibileHostFile)
    options, args = getOptions()
    action = options.action
    # version = options.versionId
    serverName = options.serverName
    branchName = options.branchName
    if not action:
        print "参数执行操作 -a action [install,init,deploy,start,stop,restart]"
        sys.exit()
    elif not serverName:
        print "参数服务名 -n servername "
        printServerName(projectDict)
        sys.exit()
    else:
        # print "其他错误！"
        # sys.exit()
        if not projectDict.has_key(serverName):
            print "没有服务名：%s" % serverName
            printServerName(projectDict)
            sys.exit()
        main(serverName, branchName, action)
