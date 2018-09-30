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
# 当前时间
now_date = str(datetime.datetime.now()).split(' ')[0]

remove_log_dir = '/tmp/rm_logs/'  # 删除记录日志路径
rw_log = now_date + "_rw.log"   #文件名

# 设置 多个删除文件路径 和单独的天数设置
SerivceNameLogDict = {
                      #"/var/log/py/": 2,
                      "/var/log/": 3,
}
def _init():
    # 初始化，检查 应用路径是否正确，返回存在的应用日志路径。
    dictTmp={}
    if not os.path.exists(remove_log_dir):
        os.mkdir(remove_log_dir)
    for logPath, days in SerivceNameLogDict.iteritems():
        if os.path.exists(logPath):
            dictTmp[logPath] = days
        else:
            print "logPath:%s is not exits，please check path" % (logPath)
            continue
    return dictTmp


def listDirName(service_dir):
    # 列出 应用目录下的所以文件，返回列表
    fileList=[]
    for p, d, f in os.walk(service_dir):
        for i in f:
            fileList.append(os.path.join(p, i))
    return fileList

"""
判断文件是否为多天前文件 以修改时间为准
"""

def fileNameMtime(filename, days):
    mtime = time.ctime(os.path.getmtime(filename))
    ctime = time.ctime(os.path.getctime(filename))
    mtime_s = (os.path.getmtime(filename))
    ctime_s = (os.path.getctime(filename))
    # print "Last modified : %s, last created time: %s" % (mtime, ctime)
    now = datetime.datetime.now()
    daydelta = datetime.timedelta(days=days)
    days_ago = now - daydelta

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
    # 对文件大小 进行良好的显示
    fileSize = countFile(file)
    if 1 < fileSize < 1024:
        #print '%sB %s ' % (fileSize, file)
        return '%s B' % (fileSize)
    elif 1024 < fileSize < 1024 * 1024:
        #print '%.2fK %s' % (float(fileSize / 1024.0), file)
        return '%.2f K' % (float(fileSize / 1024.0))
    elif 1024 * 1024 < fileSize < 1024 * 1024 * 1024:
        #print '%.2fM %s' % (float(fileSize / 1024 / 1024.0), file)
        return '%.2f M' % (float(fileSize / 1024 / 1024.0))
    elif 1024 * 1024 * 1024 < fileSize < 1024 * 1024 * 1024 * 1024:
        #print '%.2fG %s' % (float(fileSize / 1024 / 1024 / 1024.0), file)
        return '%.2f G' % (float(fileSize / 1024 / 1024 / 1024.0))

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
            print remove_info
        except Exception,e:
            print e
            print'remove fail rewrite logfile'
    else:
        pass


def main():
    # 主函数调用
    serNameLogdict = _init()
    for logPath, days in serNameLogdict.iteritems():
        for filepath in listDirName(logPath):

            if fileNameMtime(filepath, days):

                #print printHuamSize(filepath)
                cleanLog(filepath)
            else:
                pass
                # print "%s not need to remove" % filepath

if __name__ == '__main__':
    main()





