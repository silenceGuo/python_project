#!/usr/bin/env python
#！-*-coding:utf-8 -*-
#!@Date    : 2019/6/19 0019 上午 11:25
#!@Author : Damon.guo
#!@File   : export_mysql_report_v2.py
"""用于自动连接sql数据库执行查询导出报表。根据不同任务文件路径下的sql模板执行不同任务，并发送到指定邮箱"""

import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
#sys.path.append("D:\Python27\Lib\site-packages")
# sys.path.append("d:\python27\lib")
#import pymysql
# import PyMySQL
import MySQLdb
import pandas as pd
import datetime
import time
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging
import calendar
import yaml
import xlsxwriter


# 检查文件是否存在
def fileExists(filePath):
    if not os.path.exists(filePath):
        print "文件：%s 不存在，请检查"  % filePath
        return False
    return True

def datedeltatime(days):
    now = datetime.datetime.now()
    daydelta = datetime.timedelta(days=days)
    enddaydelta = datetime.timedelta(days=1)

    print "daydelat", daydelta
    days_ago = now - daydelta
    onedays_ago = now - enddaydelta
    print "daysago", days_ago

    startdate = days_ago.strftime('%Y-%m-%d')
    enddate = onedays_ago.strftime('%Y-%m-%d')
    print startdate, enddate

    return startdate, enddate

def getlastweek():

    sevenday = datetime.timedelta(days=7)
    oneday = datetime.timedelta(days=1)
    today = datetime.datetime.now()
    lastweektoday = today - sevenday

    print "lastweektoday", lastweektoday.strftime('%Y-%m-%d')
    lastMonday = lastweektoday
    lastSunday = lastweektoday

    #取上上周星期一时间
    while lastMonday.weekday() != calendar.MONDAY:
        lastMonday -= oneday
    lastMonday = lastMonday.strftime('%Y-%m-%d')

    # 取上上周星期天时间
    while lastSunday.weekday() != calendar.SUNDAY:
        lastSunday += oneday
    lastSunday = lastSunday.strftime('%Y-%m-%d')


    print "lastweekdate:%s %s" % (lastMonday, lastSunday)
    #返回 上个星期一和星期天的具体日期
    return lastMonday, lastSunday


def getLastDayOfLastMonth():
    from datetime import datetime

    d = datetime.now()
    c = calendar.Calendar()
    year = d.year
    month = d.month

    if month == 1:
        month = 12
        year -= 1
    else:
        month -= 1
    days = calendar.monthrange(year, month)[1]
    """返回两个整数组成的元组，第一个是该月的第一天是星期几，第二个是该月的天数。（calendar.monthrange(year, month)： 
Returns weekday of first day of the month and number of days in month, for the specified year and month.——Python文档） 
ps：此处计算星期几是按照星期一为0计算。"""

    starlastMonth = (datetime(year, month, 1)).strftime('%Y-%m-%d')
    endlastMonth = (datetime(year, month, days)).strftime('%Y-%m-%d')
    print "lastMonth-startdata:%s" % starlastMonth
    print "lastMonth-enddate:%s" % endlastMonth
    return starlastMonth, endlastMonth

def getLastDayOfLasttwoMonth():
    # 罚金 要退后两个月
    from datetime import datetime

    d = datetime.now()
    c = calendar.Calendar()
    year = d.year
    month = d.month
    # month = 2
    if month == 1:
        month = 11
        year -= 1
    elif month == 2:
        month = 12
        year -= 1
    else:
        # month = 12
        month -= 2

    days = calendar.monthrange(year, month)[1]
    # print calendar.monthrange(year, month)
    """返回两个整数组成的元组，第一个是该月的第一天是星期几，第二个是该月的天数。（calendar.monthrange(year, month)： 
Returns weekday of first day of the month and number of days in month, for the specified year and month.——Python文档） 
ps：此处计算星期几是按照星期一为0计算。"""

    starlastMonth = (datetime(year, month, 1)).strftime('%Y-%m-%d')
    endlastMonth = (datetime(year, month, days)).strftime('%Y-%m-%d')
    print "lasttwoMonth-startdata:%s" % starlastMonth
    print "lasttwoMonth-enddate:%s" % endlastMonth
    return starlastMonth, endlastMonth

def TimeStampToTime(timestamp):
    # 时间戳转换为时间
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)

# 返回时间戳
def getTimeStamp(filePath):
    filePath = unicode(filePath, 'utf8')
    t = os.path.getmtime(filePath)
    # return t
    return TimeStampToTime(t)

def connMysql(dbname):
    # 建立数据库连接
    try:
        conn = MySQLdb.connect(host=host, user=user, passwd=dbpass, db=dbname, port=port, charset='utf8')
    except Exception, e:
        print e
        sys.exit()
    cur = conn.cursor()
    return conn, cur

def execMysql(cursor, mysqlstr,timezone):
    # 获取游数据库标.
    timezonesql = 'SET time_zone = "{timezone}"'.format(timezone=timezone)
    # cursor.execute('SET time_zone = "+3:00"')
    cursor.execute(timezonesql)
    cursor.execute(mysqlstr)
    res = cursor.fetchall()
    return res

def getYesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    return yesterday

def sendMail(fileName,receiverlist):

    sender = username
    # today = str(getYesterday())
    # today = str(datetime.date.today())
    today = datetime.datetime.now()
    today = today.strftime('%Y-%m-%d')
    # 如名字所示： Multipart就是多个部分
    msg = MIMEMultipart()
    msg['Subject'] = "%s-DATA FOR EXECL" % today
    msg['From'] = sender
    # msg['To'] = receivers

    # 下面是文字部分，也就是纯文本
    strtext = """Hi,All, this mail from program auto to send!attachment file , kindly check it, thanks!
            this mail is right for month data
               """
    puretext = MIMEText(strtext)
    msg.attach(puretext)

    print("email content already")
    # 下面是附件部分 ，这里分为了好几个类型
    # 首先是xlsx类型的附件，全部销售数据
    for file in fileName:

        # 附件名称处理去掉全路径
        filename = file.split("/")[-1]

        xlsxpart = MIMEApplication(open(file, 'rb').read())

        xlsxpart.add_header('Content-Disposition', 'attachment', filename=filename)

        msg.attach(xlsxpart)
    print("first attachment file already")

    try:
        # print("开始连接邮件服务器了")
        client = smtplib.SMTP()
        client.connect('imap.exmail.qq.com')
        client.login(username, password)

        client.sendmail(sender, receiverlist, msg.as_string())
        client.quit()
        print('today data already send.')
    except smtplib.SMTPRecipientsRefused:
        print('Recipient refused')
    except smtplib.SMTPAuthenticationError:
        print('Auth error')
    except smtplib.SMTPSenderRefused:
        print('Sender refused')
    except Exception as e:
        print(e)

def readMysql_fromFile(fileNAME):
    with open(fileNAME, "rb") as fd:
        sql = fd.read()
        # sql = sql.replace("\r\n", "").replace("\n", "")
        sql = sql.replace("\r", " ").replace("\n", " ")
        return sql

def listdir(path):
    listdir = os.listdir(path)
    sqllist = []
    sqlDict ={}
    for i in listdir:
        if i.startswith("shuoming") or i.endswith(".csv")or i.endswith(".xls") :
            continue
        filname = i.split(".")[0]
        file = os.path.join(path, i)
        sqlDict[filname] = readMysql_fromFile(file)
        # sqllist.append(readMysql_fromFile(file))
    return sqlDict

def sub_main(dbname,filename,sql,timezone):
   # 执行sql 导出导文件
    today = str(datetime.date.today())
    conn, cur = connMysql(dbname)
    res = execMysql(cur, sql,timezone)

    result_list = list(res)
    # 设设置 数据格式str防止在execl 长的int 为乱码
    result = pd.DataFrame(result_list, dtype=str)

    if not result.empty:
        result.columns = [filed[0] for filed in cur.description]  # 列表生成式，所有字段 表头
    result.to_excel(filename, index=False,engine="xlsxwriter", encoding="utf-8")

    conn.close()
    return filename

def getDir(dir):
    l1 = []
    for (root,dirs,files) in os.walk(dir, False):
        for filename in files:
            abs_path = os.path.join(root, filename)
            l1.append(abs_path)
    return l1

def readYml(file):
    with open(file)as fd:
       res = yaml.load(fd)
    return res

def main(path,jobtype):
    startweekday,endweekday = getlastweek()
    stardmonthday,endmonthday = getLastDayOfLastMonth()

    stardtwomonthday,endtwomonthday = getLastDayOfLasttwoMonth()

    today = datetime.datetime.now()
    monthstarday = today.strftime("%Y-%m-01")
    today = today.strftime("%Y-%m-%d")

    Yesterday = getYesterday()
    Yesterday = Yesterday.strftime("%Y-%m-%d")

    print "销量日期区间，%s - %s" % (monthstarday, Yesterday)

    yaml_list = getDir(os.path.join(sql_temp_dir, jobtype))
    yaml_list = [i for i in yaml_list if i.endswith(".yaml")]

    filnamelist = []
    for yml in yaml_list:
        ymldict = readYml(yml)
        sqlname = ymldict["sqlName"]
        # 邮件接受列表
        sendlist = ymldict["send"]
        sqltmp = ymldict["sqltmp"]
        dblist = ymldict["db"]
        """ 配置每个 任务脚本的 需要使用的日期类型，"""
        rate = ymldict["rate"]
        timezone = ymldict['timezone']

        if rate == "day":
            start_time = Yesterday
            end_time = Yesterday
            sql = sqltmp.format(start_time=start_time, end_time=end_time)
        elif rate == "week":
            start_time = startweekday
            end_time = endweekday
            sql = sqltmp.format(start_time=start_time, end_time=end_time)
        elif rate == "month":
            start_time = stardmonthday
            end_time = endmonthday
            # 罚金 特殊 是用的上上个月的数据
            if sqlname == "fajing_month":
                sql = sqltmp.format(start_time=stardtwomonthday, end_time=endtwomonthday)
            else:
                sql = sqltmp.format(start_time=start_time, end_time=end_time)
        else:
            print "follow a ago [day,week ,month]"
            sys.exit(1)

        for dbname in dblist:
            print "exec sql name:%s " % sqlname
            print "exec database:%s" % dbname
            # 格式 也xlsx结尾 如果数据超过65535 将报错
            dirname = os.path.join(path, jobtype)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            filname = os.path.join(dirname, "%s-%s-%s.xlsx") % (today, dbname, sqlname)
            # print sql
            sub_main(dbname, filname, sql,timezone)
            filnamelist.append(filname)
            print "export filename:%s" % filname
    "每个任务文件夹下的发送邮件的收件列表，会以最后执行的yaml 文件中的邮件列表生效。所以需要保持同一个任务文件下的yml文件中的send值是一样的"
    sendMail(filnamelist, sendlist)
    # 执行脚本 执行数据库 执行类型定义

# yml sql模板
"""
---
sqlName: weichengyunfei_month
db:
- kilimall_kenya
- kilimall_nigeria
- kilimall_uganda
timezone: +3:00
rate: day
send:
- damon.guo@kilimall.com
#- nick.wen@kilimall.com
#- garcia.li@kilimall.com
#- victor.ma@kilimall.com
#- jimmyscm@kilimall.com
#- kefeng.zhu@kilimall.com
#- henry.han@kilimall.com
#- ruby.chen@kilimall.com
#- cindy.liu@kilimall.com
sqltmp: "SELECT 
  order_sn,store_id,store_name,liquidate_shipping_fee,
  FROM_UNIXTIME(finnshed_time) AS 'finnshed time','尾程运费' AS 'fee type'
FROM nc_order 
WHERE order_state = 40 AND liquidate_shipping_fee > 0 
AND finnshed_time > UNIX_TIMESTAMP('{start_time} 00:00:00') AND finnshed_time <= UNIX_TIMESTAMP('{end_time} 23:59:59');"
"""
if __name__ == "__main__":
    # 数据库连接信息
    host = ''
    user = ""
    dbpass = ""
    port = 3306
    # 发送邮件用户信息
    username = ''
    password = ''
    # sql yaml 路径
    #sql_temp_dir = "D:\\kilimall_report\\sql"
    sql_temp_dir = "/data/auto_export_report/sqltmp"

    #报表导出的路径
    #path = "D:\kilimall_report\caiwu"
    path = "/data/auto_export_report/caiwu"

    try:
        jobtype = sys.argv[1]
    except:
        print "follow a ago [day,week ,month]"
        sys.exit()
    main(path, jobtype)
    sys.exit()
