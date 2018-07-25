#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Author : gzq
# @date   : 2018/1/2 0002 15:45
# @file   : deployment_xhw.py
import shutil
#from xml.etree.ElementTree import ElementTree,Element,parse
import os
import sys
import time
"""
用于ｗｉｎｄｏｗｓ环境下ｔｏｍｃａｔ的自动部署的工具脚本实现　部署、发布，启动，停止，回滚
适用于ｔｏｍｃａｔ并注册为ｗｉｎｄｏｗｓ服务
"""
reload(sys)
sys.setdefaultencoding('utf-8')
#from xml.dom.minidom import parse
import xml.dom.minidom
import codecs
import ConfigParser
from subprocess import PIPE,Popen

# 默认部署工程目录，默认是webapps
deploydir = "webapps"
#部署服务和端口配置文件server.conf,在同一目录下
serverConf = "server.conf"
# 取配置文件的绝对路径
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
serverConfPath = os.path.join(dirname, serverConf)
# 检查时间
# checktime = 5
# 返回部署工程的目标目录
def deploymentTomcatName(serverName):
    return os.path.join(deploymentDir, "%s%s") % (tomcatPrefix, serverName)

def joinPathName(serverPath, serverName, *args):
    # 目录拼接　
    return os.path.join(serverPath, serverName, *args)  # % (baseDeploymentName, serverName)

# 从基础tomcat复制到目标工程目录
def copyBaseTomcat(serverName):
    try:
        shutil.copytree(baseTomcat, deploymentTomcatName(serverName))
    except Exception, e:
        print e, "目标目录异常！"
        sys.exit(1)

def cleanFile(serverName):
        path = os.path.join(baseTomcat, deploymentTomcatName(serverName))
        if os.path.exists(path):
            print "Clean %s" % path
            if os.path.isfile(path):
                # 删除文件
                os.remove(path)
            # 删除目录
            else:
                shutil.rmtree(path)
        else:
            print "%s is not exists" % path
# 读取xml 配置文件
def readXml(serverName):
    xmlPath = os.path.join(deploymentTomcatName(serverName), "conf/server.xml")
    domtree = xml.dom.minidom.parse(xmlPath)
    collection = domtree.documentElement
    service = collection.getElementsByTagName("Service")
    shutdown_port = str(collection.getAttribute("port"))  # shutdown port
    for i in service:
        connector = i.getElementsByTagName("Connector")
        http_port = str(connector[0].getAttribute("port"))  # http port
        ajp_port = str(connector[1].getAttribute("port"))  # ajp port
        # URIEconding= str(connector[0].getAttribute("URIEconding"))  # http port
    return {serverName: {"shutdown_port": shutdown_port, "http_port": http_port, "ajp_port": ajp_port}}

# 修改xml 配置文件
def changeXml(serverName,shutdown_port,http_port):
    xmlpath = os.path.join(deploymentTomcatName(serverName), "conf/server.xml")
    print xmlpath
    domtree = xml.dom.minidom.parse(xmlpath)
    collection = domtree.documentElement
    service = collection.getElementsByTagName("Service")
    collection.setAttribute("port", shutdown_port)  # shutdown port
    # URIEconding = "UTF-8"
    # useBodyEncodingForURI = "true"
    for i in service:
        #print i
        connector = i.getElementsByTagName("Connector")
        appdeploy = i.getElementsByTagName("Host")
        appdeploy[0].setAttribute("appBase", deploydir) #部署目录 默认为webapps
        connector[0].setAttribute("port", http_port)  # http port
        #connector[0].setAttribute("URIEnconding", "UTF-8")  # http port
        #connector[0].setAttribute("proxyPort", "443")  #proxyPort
        # connector[0].setAttribute("useBodyEncodingForURI", "true")  # http port
        #connector[1].setAttribute("port", ajp_port)  # ajp port
    outfile = file(xmlpath, 'w')
    write = codecs.lookup("utf-8")[3](outfile)
    domtree.writexml(write, addindent=" ", encoding='utf-8')
    write.close()

# 切换工作目录
def changDir(dirpath):
    os.chdir(dirpath)
# 执行windows 命令
def execCmd(cmd):
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    print 'Exec CMD :%s' % cmd
    return stdout, stderr

# 注册或注销服务
def installServer(servername, installTag):
    bindir = os.path.join(deploymentTomcatName(servername),'bin') # 组装 TOMCAT bin 目录
    changDir(bindir) # 切换工作目录
    print 'chang workdir %s '% os.getcwd()
    install = "%s/service.bat install %s" % (bindir, servername)
    uninstall = "%s/service.bat uninstall %s" % (bindir, servername)
    if installTag == "install":
        execCmd(install)
    elif installTag == "uninstall":
        execCmd(uninstall)
    else:
        print "install or uninstall servername"
        # 切换工作目录 不然在删除会报错
    changDir(deploymentDir)

# 检查服务是否pid
def getPid(servername):
    cmd = "sc queryex %s" % servername
    stdout, stderr = execCmd(cmd)
    if "EnumQueryServicesStatus:OpenService" in stdout.split(" "):
        print 'service name :%s is not install' % servername
        return False
    else:
        try:
            #print [i.strip() for i in stdout.split('\n') if i.strip().split(":")][1:]
            pid = [i.strip() for i in stdout.split('\n') if i.strip()][8].split(":")[1].strip()
            #pid = [i.strip() for i in stdout.split('\n') if i.strip().split(":")][8].split(":")[1].strip()
        except:
            print 'sc query fail %s is not exists' % servername
            return False
        if pid:
            print 'net_pid :', pid
            return pid
        else:
             print "service:%s is stoped !" % servername
             return False

def checkServer(servername):
    # 检查服务是否注册
    cmd = "sc queryex %s" % servername
    print "check servername:%s " % servername
    stdout, stderr = execCmd(cmd)
    if "EnumQueryServicesStatus:OpenService" in stdout.split(" "):
        return False
    return True

def stopServer(servername):
    #停止服务
    pid = getPid(servername)
    #print pid
    if pid:
        cmd_task_kill = "taskkill /F /pid %s" % pid
        stdout, stderr = execCmd(cmd_task_kill)
        if stderr:
            print stderr
        print "kill %s,%s" % (servername, str(pid))
        time.sleep(checktime)
        pid = getPid(servername)
        if not pid:
            print 'kill service:%s sucees' % servername
            return True
        else:
            print "kill service:%s Fail,check!!" % servername
            return False
    # else:
    #     # print "service:%s stoped sucess!" % servername
    #     print "s"
    #     return True

def stopMain(serverName=""):

    if serverName:
        stopServer(serverName)
    else:
        for serNameDict in serverNameList:
            for serverName, Dict in serNameDict.iteritems():
                if serverName == "conf":
                    # 如果是conf 的就略过，下一个服务，conf 是做为配置文件的配置
                    continue
                stopServer(serverName)

def cleanCachUpload(path):
    # 针对 upload 服务清除缓存，因为 上传的图片是软连接到其他目录的
    list = ["WEB-INF","META-INF","css","images","js","upload","index.jsp","crossdomain.xml","clientaccesspolicy.xml"]
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
    import zipfile
    f = zipfile.ZipFile(zipfilePath, 'r')
    print 'unzip file:%s >>>>>>to:%s' % (zipfilePath, unzipfilepath)
    for file in f.namelist():
        f.extract(file, unzipfilepath)

def startServer(servername):
    # 启动服务
    for serverNameDict in serverNameList:
        for serverName, Dict in serverNameDict.iteritems():
            if serverName == "conf":
                # 如果是conf 的就略过，下一个服务，conf 是做为配置文件的配置
                continue
            elif serverName == servername:
                batpath = Dict["batpath"]
                call_bat = 'cmd.exe /c %s' % batpath
                stdout, stderr = execCmd(call_bat)
                print stdout
                if batpath in stderr:
                    print 'batpath name is err'
                    break
                break
##
def startServerPy(servername):
    # 启动服务
    if checkServer(servername):
        war = readConf(serverConfPath, servername)[servername]["war"]
        deployWarPath = joinPathName(deploymentDir, "%s%s/webapps/ROOT.war") % (tomcatPrefix, servername)
        deployWarPathRoot = joinPathName(deploymentDir, "%s%s/webapps/ROOT") % (tomcatPrefix, servername)
        jenkinsUploadDirWar = joinPathName(jenkinsUploadDir, "%s") % war
        # 考虑到现在生产环境的情况，tomcat 下的 工程下会自动解war包，该问题是需要重新部署ｔｏｍｃａｔ　修改server.xml
        # <Host appBase="webapps" autoDeploy="true" name="localhost" unpackWARs="true">
        # 修改为<Host appBase="webapps" autoDeploy="false" name="localhost" unpackWARs="true">
        # 在不变更部署工程的情况下，将发布war与启动函数合并
        if not getPid(servername):
            if servername == "upload":
                # 待需要代码优化，此处是针对upload 服务的 上传的图片 做特殊处理，
                # 对部署ROOT 下的资源图片不删除，通过手动解压war包
                cleanCachUpload(deployWarPathRoot)
                updateMain(servername)
                unzipWar(deployWarPath, deployWarPathRoot)
                time.sleep(checktime)
                call_bat = 'net start %s' % servername
                stdout, stderr = execCmd(call_bat)
                if stdout:
                    print stdout
                if stderr:
                    print stderr
                time.sleep(checktime)
                for i in xrange(1, checktime):
                    print "check server:%s Number:%s " % (servername, i)
                    time.sleep(checktime)
                    if getPid(servername):
                        print "start %s sucess" % servername
                        break
                if not getPid(servername):
                    print "start server:%s fail" % servername
                else:
                    print "start %s sucess" % servername
            else:
                updateMain(servername)
                if os.path.exists(deployWarPathRoot):
                    time.sleep(2)
                    print "clean %s " % deployWarPathRoot
                    try:
                        shutil.rmtree(deployWarPathRoot, True)
                    except:
                        rmbat = "rd /s /q %s" % deployWarPathRoot
                        stdout, stderr = execCmd(rmbat)
                        if stdout:
                            print stdout
                        if stderr:
                            print stderr

                call_bat = 'net start %s' % servername
                stdout, stderr = execCmd(call_bat)
                if stdout:
                    print stdout
                if stderr:
                    print stderr
                time.sleep(checktime)
                for i in xrange(1,checktime):
                    print "check server:%s Number:%s " % (servername, i)
                    time.sleep(checktime)
                    if getPid(servername):
                            print "start %s sucess" % servername
                            break
                if not getPid(servername):
                    print "start server:%s fail" % servername
                else:
                    print "start %s sucess" % servername
        else:
            print "server: %s is started" % servername
    else:
        print "server name is err :%s" %servername

def startMain(serverName=""):
    if serverName:
        startServerPy(serverName)
    else:
        for serverNameDict in serverNameList:
            for serverName, portDict in serverNameDict.iteritems():
                if serverName == "conf":
                    # 如果是conf 的就略过，下一个服务，conf 是做为配置文件的配置
                    continue
                startServerPy(serverName)

def writeLog(log_file,loginfo):
    # 写日志函数
    if not os.path.exists(log_file):
        print log_file
        with open(log_file, 'w+') as fd:
            fd.write(loginfo)
    else:
        with open(log_file, 'w+')as fd:
            fd.write(loginfo)

# 读取配置文件和启动服务文件设置需要部署的服务以及设置服务顺序 默认读取配置文件部署所有服务，
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

# 检查配置文件
def confCheck(cf,section,option):
    if not cf.options(section):
        print "no section: %s in conf file" % section
        sys.exit()
    try:
        options = cf.get(section, option)
    except ConfigParser.NoOptionError:
        print "no option in conf %s " % option
        sys.exit()
    if not options:
        print "options:(%s) is null in section:(%s)" % (option,section)
        return False
    else:
        return True

# 部署单函数 配置文件所有的服务部署
def deployForServer(Tag, serverName, portDict):
    shutdown_port = portDict["shutdown_port"]
    http_port = portDict["http_port"]
    #ajp_port = portDict["ajp_port"]
    if Tag == "reinstall":
        # 清理老的部署文件，重新部署
        if checkServer(serverName):
            stopServer(serverName)
            time.sleep(1)
            cleanFile(serverName)
            # 从标准tomcat 复制到部署目录
            copyBaseTomcat(serverName)
            # 修改部署tomcat server.xml配置文件
            changeXml(serverName, shutdown_port=shutdown_port, http_port=http_port)
            installServer(serverName, 'install')
        else:
            print "%s is not installed" % serverName
            print "First install %s" % serverName
    elif Tag == "install":
        # 检查服务是否注册，
        if not checkServer(serverName):
            # 从标准tomcat 复制到部署目录
            copyBaseTomcat(serverName)
            # 修改部署tomcat server.xml配置文件
            changeXml(serverName, shutdown_port=shutdown_port, http_port=http_port)
            installServer(serverName, 'install')
            if checkServer(serverName):
                print "server:%s install Sucess" % serverName
            else:
                print "server:%s install Fail" % serverName
        else:
            print "%s is installed" % serverName
    elif Tag == "uninstall":
        if checkServer(serverName):
            stopServer(serverName)
            installServer(serverName, 'uninstall')
            cleanFile(serverName)  # 清理老的部署文件，注销服务
            if not checkServer(serverName):
                print "server:%s uninstall Sucess" % serverName
            else:
                print "server:%s uninstall fail" % serverName
        else:
            print "server:%s not install!" % serverName
    else:
        pass

# 部署主函数 配置文件所有的服务部署
def deploy(Tag,serverNAME=""):
    # dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    # serverConfPath = os.path.join(dirname, serverConf)

    # 读取配置文件需要部署的服务名，根据设置的端口部署服务
    if serverNAME:
        serverNameDict = readConf(serverConfPath,serverNAME)
        deployForServer(Tag,serverNAME, serverNameDict[serverNAME])
        # shutdown_port = serverNameDict[serverNAME]["shutdown_port"]
        # http_port = serverNameDict[serverNAME]["http_port"]
        # ajp_port = serverNameDict[serverNAME]["ajp_port"]
        sys.exit()
    for serverNameDict in serverNameList:
        # print serverNameDict
        for serverName, portDict in serverNameDict.iteritems():
            if serverName == "conf":
                # 如果是conf 的就略过，下一个服务，conf 是做为配置文件的配置
                continue
            deployForServer(Tag,serverName,portDict)

def sshCmd(Tag, ip, serverName):
    import paramiko
    try:
        cmd = "python %s %s %s" % (pyFile, Tag, serverName)  # 调用远程服务器上的执行脚本 和传入参数
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #pkey_file = '/root/.ssh/id_rsa'
        pkey_file = '/root/.ssh/id_rsa'
        key = paramiko.RSAKey.from_private_key_file(pkey_file)  # 生成秘钥对
        ssh.connect(hostname=ip, username='root', pkey=key)
        print "Connect to ", ip, " with "
        stdin, stdout, stderr = ssh.exec_command(cmd)
    except:
        print "Connect fail to ", ip, " with "
        sys.exit(1)
    # stdin, stdout, stderr = ssh.exec_command("cat /etc/sysconfig/network-scripts/ifcfg-eth0")
    stdout = stdout.read()
    stderr = stderr.read()
    print stdout, stderr
    ssh.close()

def sshCmdMain(Tag, serverName):
    # 远程调用主函数
    # if not os.path.exists(serverConfPath):
    #     print "serverconf is not exists,check serverconf %s " % serverConfPath
    #     print """ %s like this:
    #                    [servername]
    #                    http_port = 8810
    #                    shutdown_port = 8830
    #                    war = com.hxh.xhw.upload.war
    #                    ip = 192.168.0.159,192.168.0.59""" % serverConf
    #     sys.exit()
    if serverName:
        try:
            ipList = [i for i in readConf(serverConfPath, serverName)[serverName]["ip"].split(",") if i]
        except:
            print "Check Config File"
            sys.exit()
        for ip in ipList:
            sshCmd(Tag, ip, serverName)
    else:
       for serverNameDict in serverNameList:
           for serverName, portDict in serverNameDict.iteritems():
               if serverName == "conf":
                   # 如果是conf 的就略过，下一个服务，conf 是做为配置文件的配置
                   continue
               try:
                   ipList = [i for i in readConf(serverConfPath, serverName)[serverName]["ip"].split(",") if i]
               except:
                   print "Check Config File"
                   sys.exit()
               for ip in ipList:
                   sshCmd(Tag, ip, serverName)

def conn(ip, username, passwd, ):
        # ssh连接函数
        import paramiko
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, 22, username, passwd, timeout=5)
            print "Connect to ", ip, " with ", username
            global curr_prompt
            curr_prompt = username + "@" + ip + ">>"
            return ssh
        except:
            print "Connect fail to ", ip, " with ", username
            sys.exit(1)

def exe_cmd_ssh(ssh, cmd):
    # ssh连接成功，执行cmd命令
    if (ssh == None):
        print "Didn't connect to a server. Use '!conn' to connect please."
        return
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout = stdout.read()
        stderr = stderr.read()
        print 'out:', stdout
        print 'err:', stderr
        return stdout, stderr
    except:
        print 'command is err'
        sys.exit(1)

def copyFile(sourfile,disfile):
    try:
        print "copy file:%s,to:%s" % (sourfile, disfile)
        shutil.copy2(sourfile, disfile)  # % ( disfile, time.strftime("%Y-%m-%d-%H%M%S"))
    except Exception, e:
        print e,
        sys.exit(1)

def versionSort(list):
  #对版本号排序 控制版本的数量
    from distutils.version import LooseVersion
    vs = [LooseVersion(i) for i in list]
    vs.sort()
    return [i.vstring for i in vs]

def getVersion(serverName):
    bakdeployRoot = joinPathName(bakWarDir, "bak-%s%s") % (tomcatPrefix,serverName)
    versionIdList = []
    try:
       for i in os.listdir(bakdeployRoot):
           if i.split(".")[0] == "ROOT":
               versionId = i.split(".")[1]
               versionIdList.append(versionId)
    except:
        return []
    if not versionIdList:
        return []
    return versionSort(versionIdList)  # 返回版本号升序列表

def getBackVersionId(serverName):
    date = time.strftime("%Y-%m-%d")
    versionIdList = getVersion(serverName)
    if not versionIdList:
        return 1
    else:
        # 同一日期下的最新版本+1
        if date != versionSort(versionIdList)[-1].split("-V")[0]:
            return 1
        else:
            return int(versionIdList[-1].split("-")[-1].split("V")[-1]) + int(1)

def cleanHistoryBak(serverName):
    # 清除历史备份war包
    bakdeployRoot = joinPathName(bakWarDir, "bak-%s%s") % (tomcatPrefix, serverName)
    VersinIdList = getVersion(serverName)
    if VersinIdList:
        if len(VersinIdList) > int(keepBakNum):
            cleanVersionList = VersinIdList[0:abs(len(VersinIdList) - int(keepBakNum))]
            for i in cleanVersionList:
                bakWarPath = os.path.join(bakdeployRoot, "ROOT.%s.war") % i
                if os.path.exists(bakWarPath):
                    print "clean history back WAR: %s" % bakWarPath
                    os.remove(bakWarPath)
                    #shutil.rmtree(bakWarPath)
        else:
            pass
    else:
        print "%s is not bak War" % serverName

def backWar(serverName):
    # 部署的war包
    deployRootWar = joinPathName(deploymentDir, "%s%s", "webapps","ROOT.war") % (tomcatPrefix,serverName)
    # 备份war包路径
    bakdeployRoot = joinPathName(bakWarDir, "bak-%s%s") % (tomcatPrefix, serverName)
    versionId = getBackVersionId(serverName)  # 同一日期下的最新版本
    try:
        lastVersinId = getVersion(serverName)[-1]
    except:
        # 获取 备份文件列表 如果没有备份 返回备份起始版本1
        lastVersinId = [time.strftime("%Y-%m-%d-")+"V1"][-1]
    #bakdeployRootWar = joinPathName(deploymentDir, "%s%s", "bak-%s%s", "ROOT.%sV%s.war") % (tomcatPrefix,serverName,tomcatPrefix, serverName, time.strftime("%Y-%m-%d-"), versionId)
    bakdeployRootWar = joinPathName(bakWarDir, "bak-%s%s", "ROOT.%sV%s.war") % (tomcatPrefix,serverName, time.strftime("%Y-%m-%d-"), versionId)
    lastbakdeployRootWar = joinPathName(bakWarDir, "bak-%s%s", "ROOT.%s.war") % (tomcatPrefix,serverName,lastVersinId)
    if not os.path.exists(bakdeployRoot):
        os.mkdir(bakdeployRoot)
    if os.path.exists(deployRootWar):
        if not os.path.exists(lastbakdeployRootWar):
            print "back %s >>> %s" % (deployRootWar, bakdeployRootWar)
            copyFile(deployRootWar, bakdeployRootWar)
        else:
            # 判断最后一次备份和现在的文件是否修改不一致，如果一致就不备份，
            if not getTimeStamp(deployRootWar) == getTimeStamp(lastbakdeployRootWar):
                copyFile(deployRootWar, bakdeployRootWar)
                if os.path.exists(bakdeployRootWar):
                    print "back %s sucess" % bakdeployRootWar
                    cleanHistoryBak(serverName)
                else:
                    print "back %s fail" % deployRootWar
            else:
                print "File is not modify not need back"
    else:
        print "File %s is not exists" % (deployRootWar)
        print "Back %s fail" % (deployRootWar)

def backWarMain(serverNAME):
    if serverNAME:
       backWar(serverNAME)
    else:
        for serverNameDict in serverNameList:
            for serverName, portDict in serverNameDict.iteritems():
                if serverName == "conf":
                    # 如果是conf 的就略过，下一个服务，conf 是做为配置文件的配置
                    continue
                backWar(serverName)

def rollBack(versionId, serverName):
    versionList = getVersion(serverName)
    war = readConf(serverConfPath, serverName)[serverName]["war"]
    if not versionList:
        print "Not Back war File :%s" % serverName
    else:
        bakdeployRootWar = joinPathName(bakWarDir, "bak-%s%s", "ROOT.%s.war") % (tomcatPrefix,serverName, versionId)
        # 回滚到备份war包到发布目录
        deployRootWar = joinPathName(deploymentDir, "%s%s", "webapps", "ROOT.war") % (tomcatPrefix,serverName)
        # 因为现在启动每次都会重新从jenkins上传目录复制war到发布目录，所有，回滚直接将备份war复制到上传目录即可实现
        # 回滚重启的连续操作
        jenkinsUploadDirWar = joinPathName(jenkinsUploadDir, "%s") % war
        deployWarPathRoot = joinPathName(deploymentDir, "%s%s/webapps/ROOT") % (tomcatPrefix, serverName)
        if not os.path.exists(bakdeployRootWar):
            print "File:%s is not exits" % bakdeployRootWar
        if os.path.exists(jenkinsUploadDirWar):
            os.remove(jenkinsUploadDirWar)
            print "clean %s file" % jenkinsUploadDirWar
        copyFile(bakdeployRootWar, jenkinsUploadDirWar)
        if os.path.exists(jenkinsUploadDirWar):
            print "RollBack Sucess,update serverName:%s" % serverName
            print "Rollback Version:%s " % versionId
            #stopMain(serverName)
            # if serverName == "upload":
            #     pass
            #     #cleanCachUpload(deployWarPathRoot)
            # else:
            #     if os.path.exists(deployWarPathRoot):
            #         shutil.rmtree(deployWarPathRoot)
        else:
            print "check File:%s ,rollback Fail" % jenkinsUploadDirWar

def rollBackMain(serverNAME):
    # 默认回滚发布前上一个版本
    if serverNAME:
        lastVersinId = getVersion(serverNAME)[-1]
        rollBack(lastVersinId, serverNAME)
    else:
        for serverNameDict in serverNameList:
            for serverName, portDict in serverNameDict.iteritems():
                if serverName == "conf":
                    # 如果是conf 的就略过，下一个服务，conf 是做为配置文件的配置
                    continue
                versionList = getVersion(serverName)
                if not versionList:
                    print "Not Back war File:%s" % serverName
                    continue
                lastVersinId = getVersion(serverName)[-1]
                rollBack(lastVersinId, serverName)

def unzipWar(zipfilePath,unzipfilepath):
    import zipfile
    f = zipfile.ZipFile(zipfilePath, 'r')
    print 'unzip file:%s >>>>>>to:%s' % (zipfilePath, unzipfilepath)
    for file in f.namelist():
        f.extract(file, unzipfilepath)

# 发布服务
def update(serverName):
    war = readConf(serverConfPath,serverName)[serverName]["war"]
    deployWarPath = joinPathName(deploymentDir, "%s%s/webapps/ROOT.war") % (tomcatPrefix, serverName)
    deployWarPathRoot = joinPathName(deploymentDir, "%s%s/webapps/ROOT") % (tomcatPrefix, serverName)
    # jenkinsUploadDirWar = joinPathName(jenkinsUploadDir,"%s","%s") % (serverName, war)
    jenkinsUploadDirWar = joinPathName(jenkinsUploadDir,"%s") % war
    jenkinsUploadDirPath = joinPathName(jenkinsUploadDir,"%s") % serverName
    if not os.path.exists(jenkinsUploadDirPath):
        os.mkdir(jenkinsUploadDirPath)
    if os.path.exists(deployWarPath):
        backWar(serverName)
    if os.path.exists(jenkinsUploadDirWar):
        copyFile(jenkinsUploadDirWar, deployWarPath)
    else:
        print "File:%s is not exists" % jenkinsUploadDirWar
        #sys.exit(1)

def updatePy(serverName):
    # 更新版本 服务 只是将war包复制到工程目录并 重命名
    if checkServer(serverName):
        war = readConf(serverConfPath, serverName)[serverName]["war"]
        deployWarPath = joinPathName(deploymentDir, "%s%s/webapps/ROOT.war") % (tomcatPrefix, serverName)
        jenkinsUploadDirWar = joinPathName(jenkinsUploadDir, "%s") % war
        if os.path.exists(jenkinsUploadDirWar):
             backWar(serverName)
             if os.path.exists(deployWarPath):
                  os.remove(deployWarPath)
             if not os.path.exists(deployWarPath):
                 print "clean history war  %s sucess" % deployWarPath
                 if os.path.exists(jenkinsUploadDirWar):
                     copyFile(jenkinsUploadDirWar, deployWarPath)
                     time.sleep(2)
                     if os.path.exists(deployWarPath):
                         print "update %s sucess" % deployWarPath
                     else:
                         print "update %s fail" % deployWarPath
                 else:
                     print "file:%s  is not exists" % jenkinsUploadDirWar
             else:
                 print "clean history war  %s fail" % deployWarPath
        else:
            print "war:%s is not exists" % jenkinsUploadDirWar

def updateMain(serverName):
    # 更新版本 服务 只是将war包复制到工程目录并 重命名
    if serverName:
        updatePy(serverName)
    else:
        for serverNameDict in serverNameList:
            for serverName, portDict in serverNameDict.iteritems():
                if serverName == "conf":
                    # 如果是conf 的就略过，下一个服务，conf 是做为配置文件的配置
                    continue
                updatePy(serverName)
def md5File(file):
    import hashlib
    md5 = hashlib.md5()
    with open(file) as fd:
         while True:
             data= fd.read(4096)
             if data:
                 md5.update(data)
             else:
                 break
    return md5.hexdigest()

def TimeStampToTime(timestamp):
    # 时间戳转换为时间
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S',timeStruct)

def getTimeStamp(filePath):
    # 返回修改时间时间戳
    filePath = unicode(filePath, 'utf8')
    t = os.path.getmtime(filePath)
    # return t
    return TimeStampToTime(t)

def Main(Tag,serverName=""):
    _init()
    # 读取配置文件需要部署的服务名，根据设置的端口部署服务
    if Tag == "stop":  # 停服务
        stopMain(serverName)
    elif Tag == "start":  # 启动服务
        startMain(serverName)
    elif Tag == "restart":  # 重启服务
        stopMain(serverName)
        #updateMain(serverName)
        startMain(serverName)
    elif Tag == "update":  # 更新发布新版本
        updateMain(serverName)
        #startMain(serverName)
    elif Tag in ["install", "uninstall", "reinstall"]:  # 部署tomcat 环境
        deploy(Tag, serverName)
    elif Tag == "send":  # 分发方法
        print "is not work"
        #sendWarToNodeMain(serverName)
    elif Tag == "rollback":
        rollBackMain(serverName)
        stopMain(serverName)
        startMain(serverName)

    elif Tag == "back":
        backWarMain(serverName)
    else:
        print """Follow One or Two agrs,
                           install|uninstall|reinstall:
                           update:
                           back:
                           start|stop|restart:
                           send:
                           rollback:"""

# 初始化读取配置文件配置部署目录和基础部署文件的设置
def _init():
    if not os.path.exists(serverConfPath):
        print "serverconf is not exists,check serverconf %s " % serverConfPath
        print """ %s like this:
                   [b2b-trade-api]
                   http_port = 8048
                   ajp_port = 8148
                   shutdown_port = 8248
                   war = com.hxh.xhw.upload.war
                   ip = 192.168.0.159,192.168.0.59""" % serverConf
        sys.exit()
    else:
        global deploymentDir, baseTomcat, tomcatPrefix, pyFile, \
               bakWarDir, jenkinsUploadDir, serverNameList,checktime,keepBakNum
        serverNameList = readConf(serverConfPath)
        _serverConf = serverNameList[0]
        try:
             deploymentDir = _serverConf["conf"]["deploymentdir"]  # 工程部署目录
             tomcatPrefix = _serverConf["conf"]["tomcatprefix"]  # tomcat 前缀
             baseTomcat = _serverConf["conf"]["basetomcat"]  # 基础 tomcat 路径
             pyFile = _serverConf["conf"]["pyfile"]  # 远程脚本路径
             bakWarDir = _serverConf["conf"]["bakwardir"]  # 备份 war包路径
             jenkinsUploadDir = _serverConf["conf"]["jenkinsuploaddir"]  # jenkins 上传路径
             checktime = int(_serverConf["conf"]["checktime"])  # 等待时间 和检查状态次数
             keepBakNum = int(_serverConf["conf"]["keepbaknum"])  # 备份war包保留版本数

        except KeyError, E:
            print "conf is not %s" % E
            sys.exit()
        if not os.path.exists(deploymentDir):
            os.makedirs(deploymentDir)
        if not os.path.exists(bakWarDir):
            os.makedirs(bakWarDir)
        if not os.path.exists(jenkinsUploadDir):
            os.makedirs(jenkinsUploadDir)

def list_dir(path):
    list = os.listdir(path)
    ser_dict = {}
    for i in list:
        if i.startswith("apache-tomcat-7.0.64-"):
            service_name = i.split("apache-tomcat-7.0.64-")[-1]
            service_name_path = os.path.join(path, i)
            ser_dict[service_name] = service_name_path
    return ser_dict

if __name__ == "__main__":
    #serverConfPath
    # _init()
    # conf(serverConfPath,"conf","bakwardir")
    # 读取配置文件信息
    try:
        Tag = sys.argv[1]
    except:
        print """Follow Agrs,
               install|uninstall|reinstall:
               update:
               back:
               start|stop|restart:
               send:
               rollback:[serverName] [remote]"""
        sys.exit(1)
    if len(sys.argv) == 2:
        print ""
        Tag = sys.argv[1]
        Main(Tag)
    elif len(sys.argv) == 3:
        Tag = sys.argv[1]
        serName = sys.argv[2]
        if not Tag in ["install", "uninstall", "reinstall"]:
           if not checkServer(serName):
               print "serverName is worry,please check"
               sys.exit(1)
        Main(Tag, serName)
    # 远程调用 目前windows 都是公网连接 不需要远程调用
    # elif len(sys.argv) == 4:
    #     Tag = sys.argv[1]
    #     serName = sys.argv[2]
    #     remote = sys.argv[3]
    #     if remote == "remote":
    #         sshCmdMain(Tag, serName)  # 执行远程 调用脚本的
    #     else:
    #         print """Follow Agrs,
    #                        install|uninstall|reinstall:
    #                        update:
    #                        start|stop|restart:
    #                        send:
    #                        rollback [serverName] [remote]"""
    else:
        print """Follow Agrs,
               install|uninstall|reinstall:
               update:
               back:
               start|stop|restart:
               send:
               rollback [serverName] [remote]"""
        sys.exit(1)


