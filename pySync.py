#!/usr/bin/env python
#！-*-coding:utf-8 -*-
#!@Date    : 2019/6/17 0017 上午 9:44
#!@Author : Damon.guo
#!@File   : pySync.py
"""
用于文件分发，文件同步，文件拉取到本地
"""

import os
import sys
import datetime
from subprocess import PIPE, Popen
from optparse import OptionParser

class pySync():
    def __init__(self, node, action, soureDir, destDir):
        self.node = node
        self.action = action
        self.soureDir = soureDir
        self.destDir = destDir
        # self.serverDict = serverDict

    def execsh(self, cmd):
        try:
            print ("exec ssh command: %s" % cmd)
            p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        except Exception as e:
           print(e)
           sys.exit(1)
        stdout, stderr = p.communicate()
        # 需要转换byte to str
        stdout = stdout.decode()
        stderr = stderr.decode()
        return (stdout, stderr)

    def sync(self):
        """ 本地同步文件到远程服务器"""
        print """ 推送本地服务器到远程服务器"""
        syncCmd = "ansible %s -i %s -m synchronize -a 'src=%s dest=%s rsync_opts=--exclude=\.*' --sudo" % (
            self.node, ansibleHost, self.soureDir, self.destDir)
        stdout, stderr = self.execsh(syncCmd)
        if stdout:
            print stdout
        if stderr:
            print stderr

    def syncDel(self):
        print """ 推送本地服务器到远程服务器 打开删除"""
        syncCmd = "ansible %s -i %s -m synchronize -a 'src=%s dest=%s delete=yes rsync_opts=--exclude=\.*' --sudo" % (
            self.node, ansibleHost, self.soureDir, self.destDir)
        stdout, stderr = self.execsh(syncCmd)
        if stdout:
            print stdout
        if stderr:
            print stderr

    def pull(self):
        """将远程服务器单文件拉取到本地，防止把本地文件处理。"""
        pullCmd = "ansible %s -i %s -m synchronize -a 'src=%s dest=%s mode=pull rsync_opts=--exclude=\.*' --sudo" % (
            self.node, ansibleHost, self.soureDir, self.destDir)
        stdout, stderr = self.execsh(pullCmd)
        if stdout:
            print stdout
        if stderr:
            print stderr

def getOptions():
    # 作为镜像tag的以时间戳作为默认值
    date_now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
    parser = OptionParser()
    parser.add_option("-n", "--node", action="store",
                      dest="node",
                      default=False,
                      help="node to do")

    parser.add_option("-a", "--action", action="store",
                      dest="action",
                      default="sync",
                      help="action -a [sync,pull,push,pushd]")

    parser.add_option("-d", "--destfile ", action="store",
                      dest="dest",
                      default=False,
                      help="-s destfile dir defalut ")

    parser.add_option("-s", "--sourefile", action="store",
                      dest="soure",
                      default=False,
                      help="-s sourefile or dir")

    # jar 服务启动区分环境,作为参数传入镜像中作为启动参数
    parser.add_option("-e", "--envName", action="store",
                      dest="envName",
                      default="test",
                      help="-e envName")
    options, args = parser.parse_args()
    # print options, args
    return options, args

def main():
    options, args = getOptions()
    node = options.node
    action = options.action
    dest = options.dest
    soure = options.soure

    if not node:
        print "-n node"
        sys.exit(1)
    if not dest:
        print "-d destDir or destfile"
        sys.exit(1)
    if not soure:
        print "-s soureDir or sourefile"
        sys.exit(1)

    Rsync = pySync(node, action, soure, dest)

    if action == "sync":
        print temp.format(action=action,node=node,soure=soure,dest=dest)
        Rsync.sync()

    elif action == "syncD":
        print temp.format(action=action, node=node, soure=soure, dest=dest)
        Rsync.syncDel()

    elif action == "pull":
        print temp.format(action=action, node=node, soure=soure, dest=dest)
        Rsync.pull()
    else:
        print """源如果是 目录 需要以/ 结尾 不然会在目标路径从小新建目录同步，如果是文件在无需 / 结尾"""
        print """node 可以ansible 主机文件的组名可以是ip，如果使用pull 到本地 多个主机 最后执行的文件生效，"""
        print "sync 正常同步，syncD 带删除的同步，pull 从远程服务器拉到本地"
        print "sync,syncD,pull"

temp = """{action} {node} {soure} to {dest}"""

if __name__ == "__main__":
    ansibleHost = "/etc/ansible/hosts"
    """源如果是 目录 需要以/ 结尾 不然会在目标路径从小新建目录同步，如果是文件在无需 / 结尾"""
    main()

