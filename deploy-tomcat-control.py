#!/usr/bin/env python
#！-*-coding:utf-8 -*-
#!@Date    : 2019/7/1 0001 下午 16:06
#!@Author : Damon.guo
#!@File   : deploy-tomcat-control.py
import os
import sys
import time
import ConfigParser
from optparse import OptionParser
from subprocess import PIPE,Popen
import json
import yaml
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
    print " server:%s is %s now " % (serverName,action)
    # deploydir = serverNameDict["deploydir"]

    if env == "dev":
        deploynode = serverNameDict["devNodeName"][0]
    if env == "test":
        deploynode = serverNameDict["testNodeName"][0]
    if env == "pro":
        deploynode = serverNameDict["proNodeName"][0]

    cmd = "ansible %s -i %s -m shell -a '%s %s -a %s -n %s -e %s'" % (
        deploynode, ansibleHost, python, remote_py, action, serverName, env)

    stdout, stderr = execSh(cmd)

    if "FAILED" in stdout:
        print "stdout:%s" % stdout
        print "stderr:%s" % stderr
        print "%s %s False on %s " % (serverName, action, env)
        return False
    elif "FAILED" in stderr:
        print "stdout:%s" % stdout
        print "stderr:%s" % stderr
        print "%s %s False on %s " % (serverName, action, env)
        return False
    else:
        print "stdout:%s" % stdout
        print "stderr:%s" % stderr
        print "%s %s True on %s " % (serverName, action, env)
        return True

def getDeploymentTomcatPath(serverName):
    deployServerDir = os.path.join(deploymentAppDir, "%s%s") % (tomcatPrefix, serverName)
    deployServerWarDir = os.path.join(deploymentAppDir, "%s%s/%s") % (tomcatPrefix, serverName, "webapps/ROOT")
    deployServerWar = os.path.join(deploymentAppDir, "%s%s/%s") % (tomcatPrefix, serverName, "webapps")
    deployServerTomcatDir = os.path.join(deploymentAppDir, "%s%s") % (tomcatPrefix, serverName)
    deployServerXmlDir = os.path.join(deploymentAppDir, "%s%s/%s") % (tomcatPrefix, serverName,"conf/server.xml")
    bakServerDir = os.path.join(bakDir, "%s%s") % (tomcatPrefix, serverName)
    return {"deployServerDir":deployServerDir,
            "deployServerWarDir":deployServerWarDir,
            "deployServerTomcatDir":deployServerTomcatDir,
            "deployServerXmlDir":deployServerXmlDir,
            "bakServerDir": bakServerDir,
            "deployServerWar": deployServerWar
            }

def deploy_node(serverName,env):
    print "发送文件至远程节点 "
    serverDict = getDeploymentTomcatPath(serverName)
    deployServerWarDir = serverDict["deployServerWarDir"]
    serverNameDict = projectDict[serverName]

    if env == "dev":
        deploynode = serverNameDict["devNodeName"][0]
    if env == "test":
        deploynode = serverNameDict["testNodeName"][0]
    if env == "pro":
        deploynode = serverNameDict["proNodeName"][0]

    war = projectDict[serverName]["war"]

    copyFILE = 'ansible %s -i %s -m copy -a "src=%s dest=%s owner=tomcat group=tomcat backup=yes"' % (deploynode, ansibleHost, war, deployServerWarDir)
    ReturnExec(copyFILE)

def syncJarconf(deploynode,deployFile,deployDir):
    copyFILE = 'ansible %s -f 5 -i %s -m copy -a "src=%s dest=%s "' % (deploynode, ansibleHost, deployFile, deployDir)
    ReturnExec(copyFILE)

def execAnsibleTomcat(serverName,action,env):
    serverNameDict = projectDict[serverName]
    print " server:%s is %s now " % (serverName,action)
    deploydir = serverNameDict["deploydir"]
    if env == "dev":
        deploynode = serverNameDict["devnodename"]
    if env == "test":
        deploynode = serverNameDict["testnodename"]
    if env == "pro":
        deploynode = serverNameDict["pronodename"]


    cmd = "ansible %s -i %s -m shell -a '%s %s -a %s -n %s -e %s'" % (
        deploynode, ansibleHost, python, remote_py, action, serverName, env)
    stdout,stderr = execSh(cmd)
    if "FAILED" in stdout:
        print "stdout:%s" % stdout
        print "stderr:%s" % stderr
        print "%s %s False on %s " % (serverName, action, env)
        return False
    elif "FAILED" in stderr:
        print "stdout:%s" % stdout
        print "stderr:%s" % stderr
        print "%s %s False on %s " % (serverName, action, env)
        return False
    else:
        print "stdout:%s" % stdout
        print "stderr:%s" % stderr
        print "%s %s True on %s " % (serverName, action, env)
        return True


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

def checkMaster(branchName):
    # 获取项目分支是否为master
    cmd = "git branch"
    stdout, stderr = execSh(cmd)
    print "out:", stdout
    branch_list = [i.strip() for i in stdout.split("\n") if i]
    branchName_str = "* %s" % branchName
    if branchName_str in branch_list:
        print "%s 分支" % branchName
        return True
    print "err", stderr
    return False


def isNoErr(stdout, stderr):
    # 有错误返回false
    errlist = ["error","fatal","error"]

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

def gitupdate(serverName,branchName):
    serverNameDict = projectDict[serverName]
    # deployDir = serverNameDict["deploydir"]
    buildDir = serverNameDict["buildDir"]

    os.chdir(buildDir)
    if not checkMaster(branchName):
        checkout_m_cmd = "git checkout %s" % branchName
        print "切换至%s分支" % branchName
        ReturnExec(checkout_m_cmd)

    print "获取 最新%s分支" % branchName
    pull_m_cmd = "git pull"
    stdout, stderr = execSh(pull_m_cmd)
    # 判断是否有git 执行错误
    return isNoErr(stdout, stderr)

# jar 文件mavn构建
def buildMaven(serverName,branchName):

    serverNameDict = projectDict[serverName]

    buildDir = serverNameDict["buildDir"]

    if not gitupdate(serverName,branchName):
        print "git update is err"
        sys.exit(1)
    # sonar(serverName)
    os.chdir(buildDir)
    print "workdir : %s" % os.getcwd()

    cmd = "%(mvn)s clean && %(mvn)s install -Dmaven.test.skip=true -P dev" % {"mvn": mvn}

    print "构建服务：%s" % serverName
    # sys.exit()
    stdout, stderr = execSh(cmd)

    if "BUILD FAILURE" in stdout:
        print "stdout:%s" % stdout
        return False
    elif "BUILD FAILURE" in stderr:
        print "stderr:%s" % stderr
        return False
    else:
        if stdout:
            print stdout
        if stderr:
            print stderr
        return True


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

def readYml(file):
    with open(file)as fd:
       res = yaml.load(fd)
    return res

# 初始化项目主应用可用于php部署，
def initProject(serverName):
    # 新机器 或者新目录项目部署

    print "master install:%s" % serverName
    # print projectDict
    builddir = projectDict[serverName]["builddir"]
    if not os.path.exists(builddir):
        os.makedirs(builddir)
    try:
        gitUrl = projectDict[serverName]["giturl"]
    except:
        pass
    if not gitUrl:
        return False

    if not os.path.exists(builddir):
        os.mkdir(builddir)
    os.chdir(builddir)
    print "部署路径：", os.getcwd()
    stdout, stderr = execSh("git status .")
    if stdout:
        print"out：\n%s" % stdout
        print "当前目录：%s,已经存在git仓库请检查!" % builddir
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

def sonar(serverName):
    cmd = """mvn sonar:sonar \
  -Dsonar.projectKey={serverName} \
  -Dsonar.host.url=http://10.0.1.133:9002 \
  -Dsonar.login=aa4ef6b616e1ba20d9c45ce3d05caafdb9a65bee""".format(serverName=serverName)


    cmd1 = "mvn -X sonar:sonar -P dev"

    builddir = projectDict[serverName]["builddir"]
    os.chdir(builddir)

    stdout, stderr = execSh(cmd1)

    if "BUILD FAILURE" in stdout:
        print "stdout:%s" % stdout
        return False
    elif "BUILD FAILURE" in stderr:
        print "stderr:%s" % stderr
        return False
    else:
        if stdout:
            print stdout
        if stderr:
            print stderr
        return True



def main(serverName,branchName,action,envName,version,typeName):

    if action == "init":
        # 主服务项目部署 用代码分支合并，mvn 构建，在主服务器上
        initProject(serverName)
    elif action == "merge":
        # 主服务项目合并分支至master
        mergeBranch(serverName, branchName)
    elif action == "install":
        # 用于远端机器部署项目
        execAnsible(serverName, action, envName)
    elif action == "uninstall":
        # 用于远端机器部署项目
        execAnsible(serverName, action, envName)
    elif action == "reinstall":
        # 用于远端机器部署项目
        execAnsible(serverName, action, envName)
    elif action == "sync":
        # 用于同步配置文件到生产远端机器部署项目
        # execAnsible(serverName, action, envName)
        ansibileSyncDir("","")
        syncJarconf("activity", "/data/activity/jar-prod.conf", "/app/activity-test/jar.conf")
        syncJarconf("activity", "/data/activity/server-prod.conf", "/app/activity-test/server.conf")
        syncJarconf("activity", "/data/activity/JarService-prod.py", "/app/activity-test/JarService.py")
    elif action == "build":
        buildMaven(serverName, branchName)
    elif action == "deploy":
        if not buildMaven(serverName, branchName):
            print "build false"
            sys.exit(1)
        execAnsible(serverName, "stop", envName)
        execAnsible(serverName, "back", envName)
        #清理部署root目录 历史部署文件
        execAnsible(serverName, "cleanRoot", envName)

        # 部署新包至目标节点
        deploy_node(serverName, envName)
        if not execAnsible(serverName, "start", envName):
            sys.exit(1)
    elif action == "send":
        deploy_node(serverName, envName)

    elif action == "restart":
        execAnsible(serverName, "stop", envName)

        if not execAnsible(serverName, "start", envName):
            sys.exit(1)
    elif action == "start":
       if not execAnsible(serverName, action, envName):
           sys.exit(1)

    elif action == "stop":
        execAnsible(serverName, action, envName)
    elif action == "sonar":
        sonar(serverName)
    elif action == "back":
        execAnsible(serverName, action, envName)
    elif action == "getback":
        execAnsible(serverName, action, envName)
    elif action == "rollback":
        execAnsible(serverName, action, envName)
    elif action == "status":
        execAnsible(serverName, action, envName)
    else:
        print "action just [install,init,back,rollback，getback，start,stop,restart]"
        sys.exit(1)

# 读取启动服务顺序文件
def readfile(file):
    if not os.path.exists(file):
        return False
    with open(file) as fd:
        for i in fd.readlines():
            if i:
                return [i.strip().split(":")[1], i.strip().split(":")[0]]
            return False

# 写启动服务顺序文件
def writhfile(file,info):
    if not os.path.exists(file):
        print file
        with open(file, 'w+') as fd:
            fd.write(info)
    else:
        with open(file, 'w+')as fd:
            fd.write(info)

# 清理启动服务顺序文件
def cleanfile(file):
    with open(file, 'w+') as fd:
        fd.write("")

def getOptions():
    parser = OptionParser()

    parser.add_option("-n", "--serverName", action="store",
                      dest="serverName",
                      default=False,
                      help="serverName to do")

    parser.add_option("-a", "--action", action="store",
                      dest="action",
                      default=False,
                      help="action -a [deploy,install,uninstall,reinstall,stop,start,restart,back,rollback,getback]")

    parser.add_option("-v", "--versionId", action="store",
                      dest="versionId",
                      default=False,
                      help="-v versionId")
    parser.add_option("-e", "--envName", action="store",
                      dest="envName",
                      default=False,
                      help="-e envName")
    parser.add_option("-t", "--typeName", action="store",
                      dest="typeName",
                      default=False,
                      help="-t typeName")
    parser.add_option("-b", "--branchName", action="store",
                      dest="branchName",
                      default=False,
                      help="-b branchName")
    options, args = parser.parse_args()
    return options, args

# 输出服务配置文件中的服务名
def printServerName(projectDict):

    serverlist = sorted(projectDict.keys())
    for serverName in serverlist:
        print "可执行服务名：%s" % serverName
    return serverlist

if __name__ == "__main__":
    # serverconf = "server.conf"
    serverconf = "serverConf.yml"
    confDict = readYml(serverconf)

    mvn = confDict["mvn"]
    remote_py = confDict["remotePy"]
    python = confDict["python"]
    java = confDict["java"]
    nohup = confDict["nohup"]
    deploymentAppDir = confDict["deploymentAppDir"]
    startConf = confDict["startServer"]
    ansibleHost = confDict["ansibileHost"]
    warConf = confDict["warConf"]
    tomcatPrefix = confDict["tomcatPrefix"]
    bakDir = confDict["bakDir"]

    projectDict = readYml(warConf)

    options, args = getOptions()
    action = options.action
    version = options.versionId
    serverName = options.serverName
    branchName = options.branchName
    typeName = options.typeName
    envName = options.envName
    if not action:
        print "参数执行操作 -a action [install,init,back,rollback，getback，start,stop,restart]"
        sys.exit(1)
    elif not serverName:
        print "参数服务名 -n servername "
        printServerName(projectDict)
        sys.exit(1)
    elif not envName:
        print "参数执行操作 -e envName [dev,test,pro]"
        sys.exit(1)
    else:

        if serverName == "all":
            if readfile(startConf):
                serName, point = readfile(startConf)
            else:
                point = 0
            # 进行升序排列
            serverlist = sorted(projectDict.keys())

            # 从上次执行失败的位置开始执行
            for serName in serverlist[int(point):]:
                ser_index = serverlist.index(serName)
                info = "%s:%s" % (ser_index, serName)
                writhfile(startConf, info)
                main(serName, branchName, action, envName, version,typeName)
            cleanfile(startConf)

        else:
            if not projectDict.has_key(serverName):
                print "没有服务名：%s" % serverName
                printServerName(projectDict)
                sys.exit(1)
            main(serverName, branchName, action, envName, version, typeName)
