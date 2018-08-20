#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Author : gzq
# @date   : 2018/6/21 0021 10:52
# @file   : dockerServer.py
from subprocess import PIPE, Popen
from optparse import OptionParser
import time
import os
import sys
import xml.dom.minidom
import signal
import codecs
import shutil
import zipfile
#import shlex
#import paramiko
#import SSH
import time
import ConfigParser
reload(sys)
sys.setdefaultencoding('utf-8')

workDir = "/root/home/jenkinsUpload"
serverConf = "/root/home/jenkinsUpload/server_liunx.conf"  # 部署配置文件
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
serverConfPath = os.path.join(dirname, serverConf)

serviceImagesMoble = """
# Dockfile for service
from tomcat7:base
MAINTAINER Guozq
ARG ServerNameDir
ARG WarName
COPY ${ServerNameDir}/${WarName}  /data/tomcat7/webapps/ROOT.war
CMD ["/data/tomcat7/bin/catalina.sh","run"]

"""

baseImagesMoble = """
# Dockfile for tomcat7:base
FROM centos
MAINTAINER GuoZQ
RUN mkdir -pv /data/java1.7.8
RUN mkdir -pv /data/tomcat7
COPY java1.7.8 /data/java1.7.8
COPY tomcat7 /data/tomcat7
RUN chmod +x /data/tomcat7/bin/*
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV JAVA_HOME=/data/java1.7.8
ENV JAVA_BIN=/data/java1.7.8/bin
ENV JRE_HOME=/data/java1.7.8/jre
ENV PATH=$JAVA_HOME/bin:$JAVA_HOME/jre/bin:$PATH
ENV CLASSPATH=$JAVA_HOME/jre/lib:$JAVA_HOME/lib:$JAVA_HOME/jre/lib/charsets.jar
ENV JAVA_OPTS="$JAVA_OPTS -Duser.timezone=Asia/Shanghai"
EXPOSE 8080
CMD ["/data/tomcat7/bin/catalina.sh","run"]
"""
# 读取配置文件
def readConf(confPath,serverNAME=""):
    cf = ConfigParser.ConfigParser()
    cf.read(confPath)
    serverNameDict = {}
    serverNameList = []
    portDict = {}
    if serverNAME:
        try:
            cf.options(serverNAME)
        except Exception, e:
            print e
            print "serverName:%s server is not exists" % serverNAME
            sys.exit(1)
        for optins in cf.options(serverNAME):
            if not confCheck(cf,serverNAME,optins):
                sys.exit()
            port = cf.get(serverNAME, optins)
            portDict[optins] = port
        serverNameDict[serverNAME] = portDict
        return serverNameDict
    else:
        for serverName in cf.sections():
            for optins in cf.options(serverName):
                # 取服务名下的对应的配置和参数
                if not confCheck(cf, serverName, optins):
                    sys.exit()
                port = cf.get(serverName, optins)
                portDict[optins] = port
            serverNameDict[serverName] = portDict
            serverNameList.append(serverNameDict)
            portDict={}
            serverNameDict ={}
        return serverNameList
# 配置文件检查
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
#执行ssh 命令
def execSh(cmd):
    # 执行SH命令
    try:
        print "exec ssh command %s" % cmd
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    except Exception, e:
        print e,
        sys.exit()
    return p.communicate()
# 构建服务镜像
def buildImages(imagesName, serverNameDir, WarName):
    buildImages = "docker build -t %s " \
                  "--build-arg ServerNameDir=%s " \
                  "--build-arg WarName=%s ." % (imagesName, serverNameDir, WarName)
    buildStdout, buildStderr = execSh(buildImages)
    if printOutErr(buildStdout, buildStderr):
        print "build images sucess:%s " % imagesName
        return True
    else:
        print "build images fail:%s " % imagesName
        sys.exit()
        #return False
# 推送镜像至私有仓库
def pushImages(imagesName):
    pushImage = "docker push %s" % imagesName
    pushStdout, pushStderr = execSh(pushImage)
    if printOutErr(pushStdout, pushStderr):
        print "push images sucess :%s " % imagesName
        return True
    else:
        print " push images fail :%s " % imagesName
        #return False
        sys.exit()
# 创建 服务
def createService(serverName, port, imagesName):
    createService = "docker service create " \
                    "--replicas 1 " \
                    "--update-delay 10s " \
                    "--update-failure-action continue " \
                    "--network tomcat_net " \
                    "--constraint node.hostname!=centos1 " \
                    "--name %s  " \
                    "-p %s:8080 %s" % (serverName, port, imagesName)
    createStdout, creatStderr = execSh(createService)
    if printOutErr(createStdout, creatStderr):
        print "create service sucess :%s" % serverName
    else:
        print "create service fail :%s" % serverName
        sys.exit(1)
# 更新服务
def updateService(imagesName, serverName):
    updateService = "docker service update --image %s %s" % (imagesName, serverName)
    print "update service:%s" % serverName
    updateStdout, updateStderr = execSh(updateService)
    if printOutErr(updateStdout, updateStderr):
        print "update service sucess:%s" % serverName
        return True
    else:
        print "update service fail:%s" % serverName
        return False
        #sys.exit()
# 回滚服务
def rollBackService(serverName):
    rollbackService = "docker service update --rollback %s" % serverName
    print "rollback service"
    rollbackupdateStdout, rollbackStderr = execSh(rollbackService)
    if printOutErr(rollbackupdateStdout, rollbackStderr):
        print "rollback service sucess :%s " % serverName
    else:
        print "rollback service fail :%s " % serverName
        sys.exit()
# 检查服务是否存在
def checkService(serverName):
    checkServiceCMD = "docker service inspect %s" % serverName
    checkStdout, checkStderr = execSh(checkServiceCMD)
    if printOutErr(checkStdout, checkStderr):
        return True
    else:
        return False

# 检查 覆盖网络，创建覆盖网络
def createNetwork(networkName):
    creatNetworkCmd = "docker network create -d overlay %s" % networkName
    checkNetworkCmd = "docker network inspect %s " % networkName
    checkNetworkStdout, checkNetworkStderr = execSh(checkNetworkCmd)

    if printOutErr(checkNetworkStdout, checkNetworkStderr):
        return True
    else:
        checkStdout, checkStderr = execSh(creatNetworkCmd)
        if printOutErr(checkStdout, checkStderr):
            return True
        else:
            return False

#
def printOutErr(stdout, stderr):
    if stdout and len(stdout) > 3:
        print "stdout >>>", stdout
        return True
    if stderr:
        print "stderr >>>", stderr
        return False
# 主函数
def main(serverName,tag="latest"):
    # action = ""
    baseImages = "tomcat7:base"
    imagesName = "tomcat7-%s:%s" % (serverName, tag)
    serverNameDict = readConf(serverConf, serverName)
    WarName = serverNameDict[serverName]["war"]
    http_port = serverNameDict[serverName]["http_port"]
    jenkinsUploadDirServer = os.path.join(workDir, "%s") % serverName
    if not os.path.exists(workDir):
        os.makedirs(workDir)
    if not os.path.exists(jenkinsUploadDirServer):
        os.makedirs(jenkinsUploadDirServer)
    if not os.path.exists(os.path.join(workDir, "Dockerfile")):
        print "Dockerfile is not exists in %s" %workDir
        print serviceImagesMoble
        sys.exit(1)
    cmd = "docker inspect %s " % baseImages
    stdout, stderr = execSh(cmd)
    if stdout:
        print "%s is exists" % baseImages
    if stderr:
        print stderr
        print "tomcat7 base images: %s  is not exists" % baseImages
        print baseImagesMoble
        sys.exit(1)

    # 切换工作目录
    os.chdir(workDir)
    WarPath = os.path.join(workDir,serverName,WarName)
    if not os.path.exists(WarPath):
        print "%s is not exists" % WarPath
        sys.exit(1)
    buildImages(imagesName, serverName, WarName)
    pushImages(imagesName)
    if checkService(serverName):
        if not updateService(imagesName, serverName):
            rollBackService(serverName)
    else:
        createService(serverName, http_port, imagesName)

def opt():
    #时间戳做默认tag,参数函数
    tagDate = time.strftime("%Y%m%d%H%M%S")
    parser = OptionParser('usage:python %prog -s serverName | -t tag')
    parser.add_option('-s',
                      dest='serverName',
                      action='store',
                      help='serverName')
    parser.add_option('-t',
                      dest='tag',
                      action='store',
                      default=tagDate,
                      help='tag')
    options, args = parser.parse_args()
    return options, args
if __name__ == "__main__":
     options,args = opt()
     serverName = options.serverName
     tag = options.tag

     if serverName:
         main(serverName,tag)
     else:
         for serverDict in readConf(serverConfPath):
             for serverName, portdict in serverDict.items():
                main(serverName, tag=tag)
                time.sleep(5)

