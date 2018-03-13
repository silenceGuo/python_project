#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Author : gzq
# @date   : 2018/1/10 0010 16:30
# @file   : deploy-liunx.py

from subprocess import PIPE, Popen
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

reload(sys)
sys.setdefaultencoding('utf-8')

jenkinsUploadDir = "/home/jenkinsUpload/"  # jenkins 上传目录
jenkinsUploadDirBak = "/home/jenkinsUploadBak/"  # 打包上传的目录备份
deploymentDirBak = "/home/deployDirBak/"
deploymentDir = "/home/deployDir/"  # 部署目录
deploymentAppSerDir = "/home/server_app/"  # 部署工程目录
tomcatPrefix = "apache-tomcat-7.0.64-"

def joinPathName(serverPath, serverName, *args):
    # 目录拼接　
    return os.path.join(serverPath, serverName, *args)  # % (baseDeploymentName, serverName)

def copyFile(sourfile,disfile):
    try:
        print "copy file:%s,to:%s" % (sourfile, disfile)
        shutil.copy2(sourfile, disfile)  # % ( disfile, time.strftime("%Y-%m-%d-%H%M%S"))
    except Exception, e:
        print e,
        sys.exit(1)

def reName():
    pass

def sendNode():
    pass

def getPid(servername):
    deploymentPath = joinPathName(deploymentAppSerDir,"%s%s") % (tomcatPrefix, servername)
    #cmd = "pgrep -f %s" % servername
    cmd = "pgrep -f %s" % deploymentPath
    pid, stderr = execSh(cmd)
    if pid:
        #string(pid,)
        print "Get PID:%s" %pid
        return int(pid)

def execSh(cmd):
    # 执行SH命令
    try:
        print "exec ssh command %s" % cmd
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    except Exception, e:
        print e,
        sys.exit()
    return p.communicate()

def stopServer(serverName):
    pid = getPid(serverName)
    print pid,type(pid)
    if pid:
        try:
            a = os.kill(pid, signal.SIGKILL)
            # a = os.kill(pid, signal.9) #　与上等效
            print 'Killed server:%s, pid:%s,reutrun code:%s' % (serverName,pid, a)
        except OSError, e:
            print 'No such as server!', e
            sys.exit()
def startServer(serverName):
    startSh = joinPathName(deploymentAppSerDir, "%s%s", "bin/startup.sh") % (tomcatPrefix,serverName)
    binDir = joinPathName(deploymentAppSerDir, "%s%s", "bin/*") % (tomcatPrefix,serverName)
    deployDir = joinPathName(deploymentAppSerDir, "%s%s") % (tomcatPrefix,serverName)
    #cmd = "su - tomcat %s" %startSh

    chmodCmd = "chmod 755 -R %s" % binDir
    chownCmd = "chown -R tomcat:tomcat %s" % deployDir
    # 授权
    #print "chmod dir 755 %s" % binDir
    execSh(chmodCmd)
    # 更改所属 组
    execSh(chownCmd)
    #cmd = "su - tomcat %s" % startSh
    #cmd = "nohup %s &" % startSh
    print startSh
    cmd = "%s &" % startSh
    #print cmd

    if not getPid(serverName):
        print "Start Server:%s" % serverName
        execSh(cmd)
    time.sleep(10)
    if getPid(serverName):
        print "Server:%s,Sucess pid:%s" % (serverName, getPid(serverName))
    else:
        print "Server:%s,is not running" % serverName

def cleanCachUpload(path):
    # 针对 upload 服务清除缓存，因为 上传的图片是软连接到其他目录的
    list = ["WEB-INF","META-INF","css","images","js","upload","index.jsp","crossdomain.xml"]
    for i in list:
        f = os.path.join(path,i)
        if os.path.exists(f):
            print "Clean %s" %f
            if os.path.isfile(f):
                # 删除文件
                os.remove(f)
            # 删除目录
            else:
                shutil.rmtree(f)

def unzipWar(zipfilePath,unzipfilepath):
    f = zipfile.ZipFile(zipfilePath, 'r')
    print 'unzip file:%s >>>>>>to:%s' % (zipfilePath, unzipfilepath)
    for file in f.namelist():
        f.extract(file, unzipfilepath)

def copyBaseTomcat(serverName):
    baseTomcat = joinPathName(deploymentAppSerDir,tomcatPrefix)
    #print baseTomcat
    deploymentDirTmp = joinPathName(deploymentAppSerDir,"%s%s") % (tomcatPrefix,serverName)
   # print deploymentDirTmp
    try:
        print "copy dir :%s to:%s" % (baseTomcat, deploymentDirTmp)
        shutil.copytree(baseTomcat, deploymentDirTmp)
    except Exception, e:
        print e, "dir is exists！"
        sys.exit(1)

# 修改xml 配置文件
def changeXml(serverName,shutdown_port="8128",http_port="8083",ajp_port="8218"):
    deploymentDirTmp = joinPathName(deploymentAppSerDir, "%s%s") % (tomcatPrefix, serverName)
    deploydir = joinPathName(deploymentDir,"%s%s")% ("tomcat-",serverName)
    xmlpath = os.path.join(deploymentDirTmp, "conf/server.xml")
    print xmlpath
    domtree = xml.dom.minidom.parse(xmlpath)
    collection = domtree.documentElement
    service = collection.getElementsByTagName("Service")
    collection.setAttribute("port", shutdown_port)  # shutdown port
    for i in service:
        connector = i.getElementsByTagName("Connector")
        appdeploy = i.getElementsByTagName("Host")
        appdeploy[0].setAttribute("appBase", deploydir) #部署目录 默认为webapps
        connector[0].setAttribute("port", http_port)  # http port
        connector[1].setAttribute("port", ajp_port)  # ajp port
    outfile = file(xmlpath, 'w')
    write = codecs.lookup("utf-8")[3](outfile)
    domtree.writexml(write, addindent=" ", encoding='utf-8')
    write.close()
def getpidPy(serverName):
    import psutil
    # process_list = psutil.get_process_list()
    # print process_list
    pids = psutil.pids()
    #pidList = psutil.pids()
    for pid in pids:
        p = psutil.Process(pid)
        #pidDictionary = psutil.Process(pid).as_dict(attrs=['pid', 'name', 'username', 'exe', 'create_time']);
        pidDictionary = psutil.Process(pid).as_dict(attrs=['pid', 'name']);
        for keys in pidDictionary.keys():
            print keys
            #tempText = keys + ':' + str(pidDictionary[keys]) + '\n'
            print tempText
    #print("pid-%d,pname-%s" % (pid, p.name()))


def get_pid(name):
    import os
    import sys
    import string
    import psutil
    #psutil.get_process_list()
    import re
    process_list = psutil.get_process_list()
    regex = "pid=(\d+),\sname=\'" + name + "\'"
    print regex
    pid = 0
    for line in process_list:
        process_info = str(line)
        ini_regex = re.compile(regex)
        result = ini_regex.search(process_info)
        if result != None:
            pid = string.atoi(result.group(1))
            print result.group()
            break



def main(serverName, serverNameWar,**port):
    # 初始化工程目录

    # 部署tomcat 工程 目录
    deploymentAppDir = joinPathName(deploymentAppSerDir, "%s%s") % (tomcatPrefix, serverName)

    # 部署的war包
    deployRootWar = joinPathName(deploymentDir, "tomcat-%s", "ROOT.war") % serverName
    deployRoot = joinPathName(deploymentDir, "tomcat-%s") % serverName

    if not os.path.exists(deployRoot):
        os.makedirs(deployRoot)
    # 备份war包路径
    bakdeployRootWar = joinPathName(deploymentDirBak, serverName, "ROOT.%s.war") % (time.strftime("%Y-%m-%d-%H%M%S"))
    bakdeployRoot = joinPathName(deploymentDirBak, serverName)

    # jenkins 上传目录
    uploadDeployWar = joinPathName(jenkinsUploadDir, serverNameWar)
    # 部署路径
    deployDir = joinPathName(deploymentDir, "tomcat-%s", "ROOT/") % serverName
    # 备份原部署文件
    if not os.path.exists(bakdeployRoot):
        # 创建备份目录
        print "creat bak dir"
        os.makedirs(bakdeployRoot)
    if os.path.exists(deployRootWar):
        print "bak war"
        copyFile(deployRootWar, bakdeployRootWar)
    # 部署新的工程目录
    if not os.path.exists(deploymentAppDir):
        print "init deployment dir"
        os.makedirs(deploymentAppSerDir)
        copyBaseTomcat(serverName)
        changeXml(serverName, **port)
    # 复制新war包到部署目录
    copyFile(uploadDeployWar, deployRootWar)
    stopServer(serverName)
    # 清理部署工程缓存 针对upload特殊处理 除resouces 其他都清理，resouces是软连接 到其他目录的
    if serverName == "upload":
        cleanCachUpload(deployDir)
    else:
        if os.path.exists(deployDir):
            shutil.rmtree(deployDir)
    unzipWar(deployRootWar, deployDir)
    startServer(serverName)
server_dict = {
    "help-h5":
        {"com.hmyun.h5.oss.help.war":
             {"shutdown_port": "8158", "http_port": "8058", "ajp_port": "8258"}},
    "upload":
        {"com.hxh.xhw.upload.war":
             {"shutdown_port": "8148", "http_port": "8048", "ajp_port": "8248"}}

 }
if __name__ == "__main__":

    # ssh = SSH.SSHConnection("192.168.0.159", 22, "root", "123456")
    # #SSH.SSHConnection()
    # ssh.connect()
    # ssh.cmd("ls")
    # ssh.upload(os.path.join(jenkinsUploadDir, "com.hxh.xhw.upload.war"), os.path.join(jenkinsUploadDir,"com.hxh.xhw.upload.war"))
    # #ssh.download('/tmp/sendmail.log', 'D:\\programfiles\\1.txt', )
    # ssh.cmd("df")
    # ssh.close()
    servername = sys.argv[1]
   # servername = "help-h5"
    #getPid(servername)
    #getpidPy(servername)

    #get_pid(servername)
    getpidPy(servername)
    # if server_dict. has_key(servername):
    #     for war,portdict in server_dict[servername].iteritems():
    #         print war,portdict
    #         main(servername,war,**portdict)
    # else:
    #     print "NO such as server，please check:%s" % servername

    #dict = {"shutdown_port": "8148", "http_port": "8048", "ajp_port": "8248"}
    #main(servername, "com.hxh.xhw.upload.war",shutdown_port="8138",http_port="8038",ajp_port="8238")
    #main(servername, "com.hxh.xhw.upload.war", **dict)  # 传值 和上都可以
    #startServer(sername)
    #print getPid(sername)
   # print joinPathName(deploymentDir,'ss','asdf')
   # main(sername, "com.hxh.xhw.upload.war")