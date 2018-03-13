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

reload(sys)
sys.setdefaultencoding('utf-8')
#from xml.dom.minidom import parse
import xml.dom.minidom
import codecs
from subprocess import PIPE,Popen

# 部署的目录
deploymentDir = 'D:\\programfiles\\application\\'

# 部署目录的前缀
baseDeploymentName = "apache-tomcat-7.0.64-"
# 基础tomcat
baseTomcat = "D:\\programfiles\\apache-tomcat-7.0.64-\\"

#部署服务和端口配置文件 server.conf
serverConf = "server.conf"
# 返回部署工程的目标目录
def deploymentTomcatName(serverName):
    return os.path.join(deploymentDir, "%s%s") % (baseDeploymentName, serverName)

# 从基础tomcat复制到目标工程目录
def copyBaseTomcat(serverName):
    try:
        shutil.copytree(baseTomcat, deploymentTomcatName(serverName))
    except Exception, e:
        print e, "目标目录已经存在！"
        sys.exit(1)

def cleanFile(serverName):
        path = os.path.join(baseTomcat, deploymentTomcatName(serverName))
        print path
        if os.path.exists(path):
            print "Clean %s" % path
            if os.path.isfile(path):
                # 删除文件
                os.remove(path)
            # 删除目录
            else:
                shutil.rmtree(path)
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
def changeXml(serverName,shutdown_port,http_port,ajp_port,deploydir="webapps"):
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
        connector[1].setAttribute("port", ajp_port)  # ajp port
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
    print 'Eexec CMD :%s' %cmd
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
        #print 'service name is not install'
        return False
    try:
        #print [i.strip() for i in stdout.split('\n') if i.strip().split(":")][1:]
        pid = [i.strip() for i in stdout.split('\n') if i.strip()][8].split(":")[1].strip()
       #pid = [i.strip() for i in stdout.split('\n') if i.strip().split(":")][8].split(":")[1].strip()
    except:
        print 'sc query fail %s is not exists' % servername
        return False
    print 'net_pid :', pid
    if pid:
        return pid

def checkServer(servername):
    # 检查服务是否注册
    cmd = "sc queryex %s" % servername
    stdout, stderr = execCmd(cmd)
    if "EnumQueryServicesStatus:OpenService" in stdout.split(" "):
        return False
    return True

def stopServerName(servername):
    #停止服务
    pid = getPid(servername)
    #print "ss",pid
    if pid:
        cmd_task_kill = "taskkill /F /pid %s" % pid
        stdout, stderr = execCmd(cmd_task_kill)
        print "kill %s,%s" % (servername, pid)
        pid = getPid(servername)
        if not pid:
            print 'kill service:%s sucees' % servername
            return True
        else:
            return False
    else:
        print "service:%s stop sucess!" % servername
        return True

def startServerName(servername,filename):
    # 启动服务
    call_bat = 'cmd.exe /c %s' % filename
    print 'call bat %s' % filename
    # stdout, stderr = exe_cmd_ssh(ssh, call_bat)
    stdout, stderr =execCmd(call_bat)
    if filename in stdout:
        print 'bat name is err'
        sys.exit(1)

def conn(ip, username, passwd,):
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

def writeLog(log_file,loginfo):
    # 写日志函数
    if not os.path.exists(log_file):
        print log_file
        with open(log_file, 'w+') as fd:
            fd.write(loginfo)
    else:
        with open(log_file, 'w+')as fd:
            fd.write(loginfo)

# 读取配置文件设置需要部署的服务
def readConf():
    import ConfigParser
    cf = ConfigParser.ConfigParser()
    cf.read(serverConf)
    serverNameDict = {}
    portDict = {}
    for serverName in cf.sections():
        #print 'serverName:%s' % serverName
        for optins in cf.options(serverName):
            # 取服务名下的对应的配置和参数
            port = cf.get(serverName, optins)
            #print optins, port
            portDict[optins] = port
        serverNameDict[serverName] = portDict
    return serverNameDict

def deploy(Tag):
    if not os.path.exists(os.path.join(os.getcwd(),serverConf)):
        print "serverconf is not exists,check serverconf"
        print """ %s like this:
                   [servername]
                   http_port = 8810
                   ajp_port = 8820
                   shutdown_port = 8830""" % serverConf
        sys.exit()
    # 读取配置文件需要部署的服务名，根据设置的端口部署服务
    serverNameDict = readConf()
    # s = {
    #      'b2b-trade-api':{'http_port': '8048', 'shutdown_port': '8248', 'ajp_port': '8148'},
    #      'goods-gtin-goods-api':{'http_port': '8061', 'shutdown_port': '8805', 'ajp_port': '8008'},
    #      'b2b-activity-oss':{'http_port': '8044', 'shutdown_port': '8244', 'ajp_port': '8144'},
    #      'tms-api':{'http_port': '8031', 'shutdown_port': '8513', 'ajp_port': '8413'},
    #      'goods-gtin-api':{'http_port': '8059', 'shutdown_port': '8705', 'ajp_port': '8007'},
    #      'b2b-shop':{'http_port': '8040', 'shutdown_port': '8240', 'ajp_port': '8140'},
    #      'pos-h5-oss':{'http_port': '8086', 'shutdown_port': '8005', 'ajp_port': '8019'},
    #      'upload':{'http_port': '8080', 'shutdown_port': '8345', 'ajp_port': '8009'},
    #      'b2b-shop-oss':{'http_port': '8042', 'shutdown_port': '8242', 'ajp_port': '8142'},
    #      'finance-api':{'http_port': '8056', 'shutdown_port': '8305', 'ajp_port': '8003'},
    #      'finance-oss':{'http_port': '8065', 'shutdown_port': '8274', 'ajp_port': '8174'},
    #      'open':{'http_port': '8888', 'shutdown_port': '8011', 'ajp_port': '8111'},
    #      'member-api':{'http_port': '8092', 'shutdown_port': '8125', 'ajp_port': '8211'},
    #      'dts-api':{'http_port': '8010', 'shutdown_port': '8053', 'ajp_port': '8033'},
    #      'b2b-goods-api':{'http_port': '8047', 'shutdown_port': '8247', 'ajp_port': '8147'},
    #      'goods-channel-api':{'http_port': '8066', 'shutdown_port': '8505', 'ajp_port': '8335'},
    #      'goods-channel-oss':{'http_port': '8054', 'shutdown_port': '8605', 'ajp_port': '8006'},
    #      'b2b-shop-h5-oss':{'http_port': '8045', 'shutdown_port': '8245', 'ajp_port': '8445'},
    #      'main-oss':{'http_port': '8081', 'shutdown_port': '8213', 'ajp_port': '8113'},
    #      'help-api':{'http_port': '8072', 'shutdown_port': '8272', 'ajp_port': '8172'},
    #      'member-h5':{'http_port': '8073', 'shutdown_port': '8273', 'ajp_port': '8273'},
    #      'tms-oss':{'http_port': '8043', 'shutdown_port': '8143', 'ajp_port': '8243'},
    #      'shopcart-api':{'http_port': '8032', 'shutdown_port': '8532', 'ajp_port': '8532'},
    #      'goods-shop-api':{'http_port': '8088', 'shutdown_port': '8115', 'ajp_port': '8110'},
    #      'store-oss':{'http_port': '8094', 'shutdown_port': '8185', 'ajp_port': '8017'},
    #      'xcode-oss':{'http_port': '8064', 'shutdown_port': '8555', 'ajp_port': '8015'},
    #      'xcode-h5':{'http_port': '7070', 'shutdown_port': '8225', 'ajp_port': '8020'},
    #      'common-oss':{'http_port': '8096', 'shutdown_port': '8655', 'ajp_port': '8355'},
    #      'job':{'http_port': '8585', 'shutdown_port': '8014', 'ajp_port': '8214'},
    #      'shop-h5-oss':{'http_port': '8051', 'shutdown_port': '8105', 'ajp_port': '8217'},
    #      'bmhc-api':{'http_port': '8099', 'shutdown_port': '8333', 'ajp_port': '8021'},
    #      'sso':{'http_port': '9999', 'shutdown_port': '8395', 'ajp_port': '8210'},
    #      'pos-oss':{'http_port': '8085', 'shutdown_port': '8035', 'ajp_port': '8049'},
    #      'help-h5':{'http_port': '8067', 'shutdown_port': '8252', 'ajp_port': '8152'},
    #      'pos-bill-api':{'http_port': '8057', 'shutdown_port': '8145', 'ajp_port': '8013'},
    #      'xcode-api':{'http_port': '8098', 'shutdown_port': '8215', 'ajp_port': '8219'},
    #      'job-console':{'http_port': '8356', 'shutdown_port': '8256', 'ajp_port': '8156'},
    #      'xcode-h5-oss':{'http_port': '8052', 'shutdown_port': '8235', 'ajp_port': '8018'},
    #      'tms-h5-oss':{'http_port': '8046', 'shutdown_port': '8246', 'ajp_port': '8146'},
    #      'gbsi-api':{'http_port': '8060', 'shutdown_port': '8906', 'ajp_port': '8315'},
    #      'finance-flows-api':{'http_port': '8058', 'shutdown_port': '8405', 'ajp_port': '8004'},
    #      'gtin-oss':{'http_port': '8063', 'shutdown_port': '8905', 'ajp_port': '8109'},
    #      'activity-api':{'http_port': '8095', 'shutdown_port': '8205', 'ajp_port': '8001'},
    #      'store-api':{'http_port': '8074', 'shutdown_port': '8175', 'ajp_port': '8016'},
    #      'sms-oss':{'http_port': '8041', 'shutdown_port': '8241', 'ajp_port': '8141'},
    #      'help-oss':{'http_port': '8062', 'shutdown_port': '8262', 'ajp_port': '8162'},
    #      'trade-api':{'http_port': '8090', 'shutdown_port': '8195', 'ajp_port': '8118'},
    #      'shop-h5':{'http_port': '8083', 'shutdown_port': '8155', 'ajp_port': '8314'},
    #      'activity-oss':{'http_port': '8055', 'shutdown_port': '8325', 'ajp_port': '8002'},
    #      'sms-api':{'http_port': '8030', 'shutdown_port': '8230', 'ajp_port': '8130'},
    #      'b2b-activity-api':{'http_port': '8039', 'shutdown_port': '8239', 'ajp_port': '8139'},
    #      'pos-api':{'http_port': '8093', 'shutdown_port': '8135', 'ajp_port': '8012'},
    #      'shop-oss':{'http_port': '8084', 'shutdown_port': '8165', 'ajp_port': '8515'},}
    info = ""
    for serverName, portDict in serverNameDict.iteritems():
        shutdown_port = portDict["shutdown_port"]
        http_port = portDict["http_port"]
        ajp_port = portDict["ajp_port"]
        if Tag == "reinstall":
            #清理老的部署文件，重新部署
            if checkServer(serverName):
                 stopServerName(serverName)
                 time.sleep(1)
                 cleanFile(serverName)
                 # 从标准tomcat 复制到部署目录
                 copyBaseTomcat(serverName)
                 # 修改部署tomcat server.xml配置文件
                 changeXml(serverName, shutdown_port=shutdown_port, http_port=http_port, ajp_port=ajp_port)
                 # 检查服务是否注册，
            if not checkServer(serverName):
                installServer(serverName, 'uninstall')
                installServer(serverName, 'install')
            else:
                print "%s is installed" %serverName

        elif Tag =="install":
            # 检查服务是否注册，
            if not checkServer(serverName):
                # 从标准tomcat 复制到部署目录
                copyBaseTomcat(serverName)
                # 修改部署tomcat server.xml配置文件
                changeXml(serverName, shutdown_port=shutdown_port, http_port=http_port, ajp_port=ajp_port)
                installServer(serverName, 'install')
                if checkServer(serverName):
                    print "server:%s install Sucess" % serverName
                else:
                    print "server:%s install Fail" % serverName
            else:
                print "%s is installed" % serverName
        elif Tag == "uninstall":
            if checkServer(serverName):
                stopServerName(serverName)
                installServer(serverName, 'uninstall')
                cleanFile(serverName) # 清理老的部署文件，注销服务
                if not checkServer(serverName):
                    print "server:%s uninstall Sucess" % serverName
                else:
                    print "server:%s uninstall fail" % serverName
            else:
                print "server:%s not install!" % serverName


def list_dir(path):
    list = os.listdir(path)
    ser_dict = {}
    for i in list:
        if i.startswith("apache-tomcat-7.0.64-"):
            service_name = i.split("apache-tomcat-7.0.64-")[-1]
            service_name_path = os.path.join(path, i)
            ser_dict[service_name] = service_name_path
    return ser_dict

serdict = {
    "test1":
               {
                   "shutdown_port":"1288881",
                   "http_port":"1299991",
                   "ajp_port":"1277771",
                 },
    "test2":
               {
                   "shutdown_port":"1288882",
                   "http_port":"1299992",
                   "ajp_port":"1277772",
                 },
    "test3":
               {
                   "shutdown_port":"1288883",
                   "http_port":"1299993",
                   "ajp_port":"1277773",
                 },
"test11":
               {
                   "shutdown_port":"1288883",
                   "http_port":"1299993",
                   "ajp_port":"1277773",
                 }
}

if __name__ == "__main__":
    tag = "reinstall"
    deploy(tag)


