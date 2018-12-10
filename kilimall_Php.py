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
serverConf = "standard.conf"  # 部署配置文件路径
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
                      help="action -a [install,merge,update]for php project")
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
        print "Exec ssh command %s" % cmd
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


#初始化主节点
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
        print "check branchname:%s" % branchName
        sys.exit()

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

#读取ansibel host 文件解析
def readConfAnsible(file):
    cf = ConfigParser.ConfigParser(allow_no_value=True)
    cf.read(file)
    try:
        cf.read(file)
    except ConfigParser.ParsingError, e:
        print e
        print "please check conf %s" % file
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


def ansibleUpdateGit(serverName):
    groupName = projectDict[serverName]["deploygroupname"]
    deployDir = projectDict[serverName]["deploydir"]
    UpdateDir = 'ansible %s -i %s -m shell -a "cd %s;sudo git pull"' % (groupName, ansibileHostFile, deployDir)
    ReturnExec(UpdateDir)


def ansibleDirIsExists(ip,filepath):
    # 判断远程 文件或者目录是否存在
    cmd = "ansible %s -m stat -a 'path=%s' -o " % (ip, filepath)
    stdout, stederr = execSh(cmd)
    reslust = parseAnsibleOut(stdout)

    if reslust:
        print "%s is exists,on:%s" % (filepath,ip)
        return True
    elif reslust == None:
        print "%s is other err on: %s " % (filepath, ip)
        return None
    else:
        print "%s is not exists,on: %s " % (filepath, ip)
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

#检查 配置文件是否存在配置项错误
def _init(serverName):
    if not os.path.exists(serverConf):
        print "%s is not exist" % serverConf
        print """ %s like this:
                           [testgit22]
                           deployDir=/app/project/testgit22
                           gitUrl=git@10.0.1.131:root/testgit22.git
                           deployGroupName=node
                           deployFile=3.war""" % serverConf
    if serverName != "all":
        try:
           projectDict[serverName]
        except KeyError, e:
            print "please check servername: %s" % e
            sys.exit(1)
    else:
        return
    sub_dict = projectDict[serverName]

    try:
        deploygroupname = sub_dict["deploygroupname"]
        deploydir = sub_dict["deploydir"]
        giturl = sub_dict["giturl"]

    except KeyError, e:
        print "please check confile:%s servername:%s conf:%s" % (serverConf, serverName, e)
        sys.exit(1)

def main(serverName,branchName,action):

    _init(serverName)
    if action == "install":
        # 新服务器部署项目
        if serverName == "all":
            for serName, dict_sub in projectDict.iteritems():
                initProject(serName)
        else:
            initProject(serverName)

    elif action == "merge":
        # 合并分支至master
        mergeBranch(serverName, branchName)

    elif action == "update":
        mergeBranch(serverName, branchName)
        ansibleUpdateGit(serverName)

    elif action == "restart":
        pass
    else:
        print "action just [install,merge,update]"
        sys.exit()


if __name__ == "__main__":

    projectDict = readConf(serverConf)
    # ansibleHostDict = readConfAnsible(ansibileHostFile)

    options, args = getOptions()
    action = options.action
    # version = options.versionId
    serverName = options.serverName
    branchName = options.branchName
    if not action:
        print "please follow -a action"
        sys.exit(1)
    if not serverName:
        print "please follow -n servename"
        sys.exit(1)
    if not branchName:
        print "please  follow -b branchname"
        sys.exit(1)
    main(serverName, branchName, action)
