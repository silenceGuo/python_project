# -*- coding: UTF-8 -*-
# by gzq
# date :2017/9/22 0022 10:28
# -*- coding: UTF-8 -*-
# by gzq
# date :2017/8/7
import subprocess
import time
import os
import sys
import datetime
import re
import optparse

import shutil

reload(sys)
sys.setdefaultencoding('utf-8')
"""
日志三天 或者 日志文件大于1G 清理
"""
s = 'rewrite logs'
#log_size_max = 1 * (1024 * 1024)  # 1G 最大上限
log_size_max = 50 * (1024 * 1024)  # 50M 最大上限
# log_size_max = 10*(1024*1024) #10G 最大上限

now_date = str(datetime.datetime.now()).split(' ')[0]
days = 1  # 设置删除几天前的日志
remove_log_dir = '/tmp/rm_logs/'  # 删除记录日志路径
rw_log = now_date + "_rw.log"   #文件名

fileType = [".log", ""]

# 设置 多个删除文件路径
SerivceNameLogDict = {
    "test": "/var/log/",
    "test1": "/tmp2/logs",
}
def _init():
    dictTmp={}
    if not os.path.exists(remove_log_dir):
        os.mkdir(remove_log_dir)
    for serviceName,logPath in SerivceNameLogDict.iteritems():
        if os.path.exists(logPath):
            dictTmp[serviceName]=logPath
        else:
            print "serviceName:%s,logPath:%s is not exits" % (serviceName, logPath)
            continue
    return dictTmp


def listDirName(service_dir):
    fileList=[]
    for p, d, f in os.walk(service_dir):
        for i in f:
            fileList.append(os.path.join(p, i))
    return fileList

"""
判断文件是否为三天前文件 修改时间
"""

def fileNameMtime(filename):
    mtime = time.ctime(os.path.getmtime(filename))
    ctime = time.ctime(os.path.getctime(filename))
    mtime_s = (os.path.getmtime(filename))
    ctime_s = (os.path.getctime(filename))
    # print "Last modified : %s, last created time: %s" % (mtime, ctime)
    now = datetime.datetime.now()
    daydelta = datetime.timedelta(days=days)
    days_ago = now - daydelta
    # print 'now',now
    # print 'three day ago', threeday_ago
    # print 'mtime',datetime.datetime.fromtimestamp(mtime_s)
    # print 'ctime',datetime.datetime.fromtimestamp(ctime_s)
    # print threeday_ago
    # print datetime.datetime.fromtimestamp(mtime_s)
    if datetime.datetime.fromtimestamp(mtime_s) < days_ago:
        return True
    else:
        return False

"""
获取文件大小
"""
def countFile(file):
    if os.path.exists(file):
        fileSize = os.path.getsize(file)
    return fileSize

def printHuamSize(file):
    fileSize = countFile(file)
    if 1 < fileSize < 1024:
        #print '%sB %s ' % (fileSize, file)
        return '%sB %s ' % (fileSize, file)
    elif 1024 < fileSize < 1024 * 1024:
        #print '%.2fK %s' % (float(fileSize / 1024.0), file)
        return '%.2fK' % (float(fileSize / 1024.0))
    elif 1024 * 1024 < fileSize < 1024 * 1024 * 1024:
        #print '%.2fM %s' % (float(fileSize / 1024 / 1024.0), file)
        return '%.2fM' % (float(fileSize / 1024 / 1024.0))
    elif 1024 * 1024 * 1024 < fileSize < 1024 * 1024 * 1024 * 1024:
        #print '%.2fG %s' % (float(fileSize / 1024 / 1024 / 1024.0), file)
        return '%.2fG' % (float(fileSize / 1024 / 1024 / 1024.0))

"""
删除 重新 日志操作记录 
"""
def writeLog(info, file):
    if os.path.exists(file):
        with open(file, 'a')as fd:
            fd.write(info)
    else:
        with open(file, 'w') as fd:
            fd.write(info)

"""
删除 日志 将操作记录写入文件
"""
def cleanLog(filename):
    now = datetime.datetime.now()
    fileSize = printHuamSize(filename)
    if os.path.exists(filename):
        try:
            print 'clean log file %s' % filename
            os.remove(filename)
            remove_info = 'remove file:%s size:%s remove at time:%s;\n' % (filename,fileSize, now)
            remove_log = os.path.join(remove_log_dir, rw_log)
            writeLog(remove_info, remove_log)
            print remove_log
        except:
            print'remove fail rewrite logfile'
    else:
        pass


def main():
    serNameLogdict = _init()
    for serviceName, logPath in serNameLogdict.iteritems():
        for filepath in listDirName(logPath):
            if fileNameMtime(filepath):
                printHuamSize(filepath)
                cleanLog(filepath)
            else:
                pass
                # print "%s not need to remove" % filepath



if __name__ == '__main__':
    main()





