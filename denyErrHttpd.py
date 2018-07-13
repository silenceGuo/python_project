#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Author : gzq
# @date   : 2017/12/20 0020 19:16
# @file   : denyErrHttpd.py
# 该脚本用于根据centos 版本检查/var/log/sercue ，/var/log/httpd/errlog 中的恶意ip进行封禁
import sys
from subprocess import Popen, PIPE
import os
""""""
limit = 30  # 错误访问次数上限!
def filerev(fn):
    buffer = 256
    f = open(fn)
    f.seek(0, 2)
    size = f.tell()
    rem = size % buffer
    offset = max(0,size - (buffer +rem))
    line = ''
    while True:
         if offset < 0:
            yield line
            break
         else:
             f.seek(offset)
             d = f.read(buffer +rem)
             rem = 0
             offset -=buffer
             if '\n' in d:
                 for c in reversed(d):
                    if c != '\n':
                       line = c+line
                    else:
                        if line:
                           yield line
                        line = ''
             else:
                 line = d +line
    f.close()

"""get ip in line"""
def getErrIp(line):
    ip = line.split(" ")[9].split(":")[0]
    if isIP(ip):
        return ip

""""""
def isIP(line):
    import re
    reip = re.compile(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])')
    if reip.findall(line):
        return reip.findall(line)
    return None

"""执行 centos7 firewalld command """
def execFiredCmd(ip):
    cmd = "firewall-cmd --permanent --add-rich-rule='rule family=ipv4 source address=\"%s\" drop'" % ip
    exeShell(cmd)

"""exec centos6 iptables command """
def execIptablesCmd(ip):
    cmd = "iptables -I INPUT -s %s -j DROP" % ip
    exeShell(cmd)

"""exec shell command"""
def exeShell(cmd):
    p = Popen(cmd, stderr=PIPE, stdout=PIPE, shell=True)
    stderr, stdout = p.communicate()
    print stderr,
    print stdout,

"""检查iptables中是否存在规则"""
def checkIptable():
    fn =filerev('/etc/sysconfig/iptables')
    iptablesList = []
    for i in fn:
        if isIP(i):
            iptablesList.append(isIP(i)[0])
    return iptablesList

def backIp(fn,logType="",keyword="",whiteKey=""):
    dictip = {}
    for i in filerev(fn):
        #print i
        if logType == "SSHD":
            if keyword in i:
                ip = isIP(i)[0]
                if not dictip.has_key(ip):
                    dictip[ip] = 1
                else:
                    dictip[ip] += 1
        elif logType == "HTTPD":
            ip = getErrIp(i)
            if not dictip.has_key(ip):
                dictip[ip] = 1
            else:
                dictip[ip] += 1
        else:
            #print i
            if whiteKey in i:
                #print i
                ip = isIP(i)[0]
                #print ip
                if not dictip.has_key(ip):
                    dictip[ip] = 1
                else:
                    dictip[ip] += 1

                continue
           # print i
           #  elif keyword in i:
           #      ip = isIP(i)[0]
           #      if not dictip.has_key(ip):
           #          dictip[ip] = 1
           #      else:
           #          dictip[ip] += 1
    print dictip
    return dictip

def sumDict(k):
    dict = {}
    if not dict.has_key(k):
        dict[k] = 1
    else:
        dict[k] += 1

""" main func for iptables"""
def iptables(fn):
    dictip = backIp(fn,logType='SSHD',keyword="Failed password")
    for k, y in dictip.items():
        iptablesList = checkIptable()
        if k is not None:
            if y >= limit and k not in iptablesList:
                """执行centos 6 iptables 命令"""
                print "Exec iptables CMD"
                execIptablesCmd(k)
    print "save iptables rules >>>>>"
    exeShell("service iptables save")
    print "restart iptables >>>>>"
    exeShell("service iptables restart")

"""main firewalld func """
def firedWalld(fn,logType,keyword=""):
    #fn = "C:\\Users\\Administrator\\Desktop\\123\secure"
    #fn = "/var/log/secure"
    dictip = backIp(fn,logType,keyword)
    """sshd bad user ip """
    for k, y in dictip.items():
        if k is not None:
            if y >= limit:
                print "Exec Firewalld CMD"
                execFiredCmd(k)
    "reload firewalld rules"
    print "firewalld reload >>>>"
    exeShell("firewall-cmd --reload")

"""检查系统版本"""
def checkOS():
    fn = "/etc/redhat-release"
    for line in filerev(fn):
       """ return centos version """
       return [i for i in line.split(" ") if i][-2].split(".")[0]

def fileIsExists(fn):
    if os.path.exists(fn):
        return True
    return False

def writeWafBackIp(ip,backipfile):
    with open(backipfile, "a") as fd:
        #print fd.tell()
        fd.seek(0, 2)
        if fd.tell() == 0:
            fd.write(ip)
        else:
           #fd.seek(0,2)
           print fd.tell()
           fd.write("\n"+ip)
        #fd.write(ip)

        print "write ip:%s in backipFiLe:%s " %(ip, backipfile)

def checkWafBackIp(ip,backipfile):
    # 检查黑名单是否存在
    backList = []
    for line in filerev(backipfile):
        backList.append(line)
    if ip in backList:
        print "ip:%s is in file" % ip
        return True
    else:
        return False

def checkBackKey():
    pass

def checkWhiteKey():

    pass

if __name__ == '__main__':
    #osVersion = checkOS()
    backkeyList = []
    whiteKeyList = ["upload.js"]
    whiteKeyList2 = ["jquery.uploadify.min.js"]
    import time
    date = time.strftime("%Y-%m-%d")
    # if osVersion == "6":
    #     fn = "/var/log/secure"
    #     fn2 = "/var/log/httpd/access.log"  # httpd 访问错误日志
    #     if fileIsExists(fn):
    #         iptables(fn)
    #     else:
    #         print "%s is not exists" % fn
    #     if fileIsExists(fn2):
    #         iptables(fn2)
    #     else:
    #         print "%s is not exists" % fn2
    # elif osVersion == "7":
    #     fn = "/var/log/httpd/error_log"  # httpd 访问错误日志
    #     fn2 = "/var/log/secure"  # ssh 登陆失败日志
    #     if fileIsExists(fn):
    #         firedWalld(fn,logType='HTTPD')
    #     if fileIsExists(fn2):
    #         firedWalld(fn2,logType='SSHD',keyword="Failed password")
    #
    # else:
    #     print "check file log"
    # 结合OpenResty的web waf 将cc攻击ip添加到黑名单
    # fn = sys.argv[1]
    fn1 = "%s_waf.log" % date
    fn2 = "C:\Users\\Administrator\Desktop\\apk\\2018-07-13_waf.log"
    backIp(fn2, keyword="CC_Attack", whiteKey="jquery.uploadify.min.js")
    backIp(fn2, keyword="CC_Attack", whiteKey="upload.js")
    # for whiteKey in whiteKeyList:
    #      backIp(fn2, keyword="CC_Attack", whiteKey=whiteKey)

    # fn3 = "C:\Users\\Administrator\Desktop\\apk\\access.log"
    # #backipfile = "/usr/local/nginx/conf/waf/rule-config/blackip.rule"
    # backipfile = "C:\Users\Administrator\Desktop\\apk\\blackip.rule"
    # for ip, num in backIp(fn2, keyword="CC_Attack").iteritems():
    #     print num
    #     if int(num) > int(10):
    #         if not checkWafBackIp(ip, backipfile):
    #
    #             writeWafBackIp(ip, backipfile)




