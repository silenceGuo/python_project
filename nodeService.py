#!/usr/bin/env python
#！-*-coding:utf-8 -*-
#!@Date    : 2018/11/9 0009 下午 17:08
#!@Author : Damon.guo
#!@File   : updateStandard.py

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

def ReturnExec(cmd):
    stdout, stderr = execSh(cmd)
    if stdout:
        print 80*"#"
        print "out:%s " % stdout
    if stderr:
        print 80*"#"
        print "err:%s" % stderr


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
    projectNameDict = serverNameDict[serverName]
    # deployDir = serverNameDict["deploydir"]
    buildDir = projectNameDict["builddir"]

    os.chdir(buildDir)
    if not checkMaster():
        checkout_m_cmd = "git checkout master"
        print "切换至master分支"
        ReturnExec(checkout_m_cmd)

    print "获取 最新master分支"
    pull_m_cmd = "git pull"
    stdout, stderr = execSh(pull_m_cmd)
    if "error" or "fatal" in stdout:
        print stdout
        return False
    elif "error" or "fatal" in stderr:
        print stderr
        return False
    else:
        print "stdout:%s" % stdout
        print "stderr:%s" % stderr
        return True

def buildNode(serverName,env):
    cmd = "/app/node-v9.5.0-linux-x64/bin/npm install"
    """
    git pull
    /app/node-v9.5.0-linux-x64/bin/npm install
    /app/node-v9.5.0-linux-x64/bin/npm run debugbuild
    pid=`pgrep -f $dir$1/node_modules/.bin/nuxt`
    kill -9 $pid

    nohup /app/node-v9.5.0-linux-x64/bin/npm run start  >$1.out 2>&1 &
"""
    ReturnExec(cmd)

def startServer(serverName):
    logpath = os.path.join(logspath,serverName)
    cmd = "nohup %s run start >%s"

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
            #os.kill(pid, signal.SIGKILL)
            print '停止服务:%s, pid:%s' % (serverName, pid)
        except OSError, e:
            print 'No such as server!', e
        for i in xrange(1, checkTime+1):
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

def getPid(serverName):

    deployDir = projectDict[serverName]["deploydir"]

    # deployDir = os.path.join(deployDir, serverName)

    # cmd = "pgrep -f %s" % deployDir
    cmd = "pgrep -f %s/node_modules/.bin/nuxt" % deployDir
    # cmd = "pgrep -f %s/war/" % deployDir
    pid, stderr = execSh(cmd)
    if pid:
        #string(pid,)
        print "取得 PID:%s" % pid
        return int(pid)

#检查文件是否存在
def fileExists(filePath):
    if not os.path.exists(filePath):
        print "文件：%s 不存在，请检查" % filePath
        return False
    return True

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

def ansibleSyncDir(serverName):
    pass


def init(serverconf):
    if not fileExists(serverconf):
        sys.exit()
    global serverNameDict
    serverNameDict = readConf(serverconf)

def main():
    serverconf = "nodeServer.conf"
    init(serverconf)

if __name__ == "__main__":
    main()

