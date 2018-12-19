#!/usr/bin/env python
#！-*-coding:utf-8 -*-
#!@Date    : 2018/12/17 0017 上午 10:12
#!@Author : Damon.guo
#!@File   : export_mysql_report.py
import sys
# sys.setdefaultencoding('utf8')
sys.path.append("D:\Python27\Lib\site-packages")
# sys.path.append("d:\python27\lib")
import pymysql
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
import xlsxwriter
import calendar

host = '10.0.0.100'

# user = 'KILIMALL'
user = 'root'
dbpass = "123456"
port = 3306

#检查文件是否存在
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
    # print time.strftime("%Y-%m-%d", days_ago)

    #
    # if datetime.datetime.fromtimestamp(mtime_s) <= days_ago:
    #     print "sss"
    #     return True
    # else:
    #     return False

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

def execMysql(cursor, mysqlstr):
    # 获取游数据库标.
    cursor.execute('SET time_zone = "+3:00"')
    cursor.execute(mysqlstr)
    res = cursor.fetchall()
    return res

def getYesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    return yesterday

def sendMail(fileName,receiverlist):
    username = 'data_send@123.com'
    password = '123'
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
    strtext = """Hi,All, attachment file , kindly check it, thanks!
                 
                 """
    puretext = MIMEText(strtext)
    msg.attach(puretext)

    print("email content already")
    # 下面是附件部分 ，这里分为了好几个类型

    # 首先是xlsx类型的附件，全部销售数据
    for file in fileName:

        # 附件名称处理去掉全路径
        filename = file.split("\\")[-1]

        xlsxpart = MIMEApplication(open(file, 'rb').read())
    # xlsxpart.add_header('Content-Disposition', 'attachment', filename=today + "stock.csv")

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

def sub_main(dbname,filename,sql):
   # 执行sql 导出导文件
    today = str(datetime.date.today())
    conn, cur = connMysql(dbname)
    res = execMysql(cur, sql)

    result_list = list(res)
    # 设设置 数据格式str防止在execl 长的int 为乱码
    result = pd.DataFrame(result_list, dtype=str)
    # print cur.description

    if not result.empty:
        result.columns = [filed[0] for filed in cur.description]  # 列表生成式，所有字段 表头

    # export_path_file = os.path.join(exportpath, "%s-%s.xls") % (today, filename)

    # result.to_csv(export_tpath_file, index=False, encoding="utf-8", float_format="%.2f")

    result.to_excel(filename, index=False, encoding="utf-8")
    return filename


def main(path,jobtype):
    startweekday,endweekday = getlastweek()
    stardmonthday,endmonthday = getLastDayOfLastMonth()

    today = datetime.datetime.now()
    today = today.strftime("%Y-%m-%d")
     # 定义的周执行的sql脚本
    dingdanwangcheng_week = """SELECT 
  o.order_sn,
  IFNULL(
    oc.voucher_price / o.goods_amount * g.goods_liquidate_amount,
    0
  ) AS voucher,
  oc.`voucher_type`,
  o.`order_amount`,
  o.`store_id`,
  o.`store_name`,
  FROM_UNIXTIME(o.`finnshed_time`) AS finnshed_time,
  FROM_UNIXTIME(o.`add_time`) AS add_time,
  o.`logistics_type`,
  g.`goods_id`,
  g.`goods_name`,
  (g.`goods_liquidate_amount`/g.`goods_num`)AS goods_price,
  g.`goods_num`,
  g.`goods_type`,
  g.`gc_id`,
  FROM_UNIXTIME(o.`payment_time`) AS payment_time,
  IFNULL(
    g.goods_liquidate_amount / o.goods_amount * o.`shipping_fee`,
    0
  ) AS shipping_fee,
  oc.cash_rewards
FROM
  nc_order_goods g 
  LEFT JOIN nc_order o 
    ON g.`order_id` = o.`order_id` 
  LEFT JOIN nc_order_common oc 
    ON o.`order_id` = oc.`order_id` 
WHERE  o.finnshed_time >= UNIX_TIMESTAMP('%s 00:00:00')
  AND o.finnshed_time <= UNIX_TIMESTAMP('%s 23:59:59');""" % (startweekday, endweekday)

    # 定义的月执行脚本
    dingdanwangcheng_month = """SELECT 
      o.order_sn,
      IFNULL(
        oc.voucher_price / o.goods_amount * g.goods_liquidate_amount,
        0
      ) AS voucher,
      oc.`voucher_type`,
      o.`order_amount`,
      o.`store_id`,
      o.`store_name`,
      FROM_UNIXTIME(o.`finnshed_time`) AS finnshed_time,
      FROM_UNIXTIME(o.`add_time`) AS add_time,
      o.`logistics_type`,
      g.`goods_id`,
      g.`goods_name`,
      (g.`goods_liquidate_amount`/g.`goods_num`)AS goods_price,
      g.`goods_num`,
      g.`goods_type`,
      g.`gc_id`,
      FROM_UNIXTIME(o.`payment_time`) AS payment_time,
      IFNULL(
        g.goods_liquidate_amount / o.goods_amount * o.`shipping_fee`,
        0
      ) AS shipping_fee,
      oc.cash_rewards
    FROM
      nc_order_goods g 
      LEFT JOIN nc_order o 
        ON g.`order_id` = o.`order_id` 
      LEFT JOIN nc_order_common oc 
        ON o.`order_id` = oc.`order_id` 
    WHERE  o.finnshed_time >= UNIX_TIMESTAMP('%s 00:00:00')
      AND o.finnshed_time <= UNIX_TIMESTAMP('%s 23:59:59');""" % (stardmonthday, endmonthday)

    tuihuanhuo = """SELECT 
  o.order_sn,
  IFNULL(
    oc.voucher_price / o.goods_amount * g.goods_liquidate_amount,
    0
  ) AS voucher,
  oc.`voucher_type`,
  o.`order_amount`,
  o.`store_id`,
  o.`store_name`,
  FROM_UNIXTIME(o.`finnshed_time`) AS finnshed_time,
  FROM_UNIXTIME(o.`add_time`) AS add_time,
  o.`logistics_type`,
  g.`goods_id`,
  g.`goods_name`,
  (rc.`refund_amount`/g.`goods_num`)AS goods_price,
  g.`goods_num`,
  g.`goods_type`,
  g.`gc_id`,
  FROM_UNIXTIME(o.`payment_time`) AS payment_time,
  IFNULL(
    g.goods_liquidate_amount / o.goods_amount * o.`shipping_fee`,
    0
  ) AS shipping_fee,
  rc.type
FROM
  nc_order_goods g 
  LEFT JOIN nc_order o 
    ON g.`order_id` = o.`order_id` 
  LEFT JOIN nc_order_common oc 
    ON o.`order_id` = oc.`order_id` 
    LEFT JOIN nc_returns rc
    ON rc.`order_id` = o.`order_id`
WHERE  rc.id IN (SELECT id FROM nc_returns WHERE `status` = 4) and rc.`type` in (1,2) AND rc.updated_at >= UNIX_TIMESTAMP('%s 00:00:00') AND rc.updated_at <= UNIX_TIMESTAMP('%s 23:59:59')
AND g.goods_id = rc.`goods_id` AND g.`order_id` = rc.`order_id`;""" % (stardmonthday, endmonthday)

    fajing = """SELECT 
  order_sn,o.store_id,store_name,order_amount, FROM_UNIXTIME(payment_time) AS payment_time,order_state,
  IF(bad_order_type = 1,FROM_UNIXTIME(o.`bi_updated_time`),0) AS cancel_time,
  IF(bad_order_type = 2 AND c.`transfer_warehouse_time` != 0,FROM_UNIXTIME(c.`transfer_warehouse_time`),0) AS transfer_warehouse_time,
  IF(bad_order_type = 2 AND c.`transfer_warehouse_time` != 0,(c.`transfer_warehouse_time` - o.`payment_time`)/(3600*24),0) AS spend_time,
  (
    IF(
      bad_order_type = 2,
      3,
      IF(bad_order_type = 1, 2, 0)
    )
  ) AS Fine 
FROM
  nc_order o LEFT JOIN nc_order_common c ON o.`order_id` = c.`order_id`
WHERE bad_order_type IN (1, 2) 
  AND payment_time > UNIX_TIMESTAMP('%s 00:00:00') 
  AND payment_time <= UNIX_TIMESTAMP('%s 23:59:59') ;""" % (stardmonthday, endmonthday)

    # 执行脚本 执行数据库 执行类型定义
    # 按周执行还是月执行的sql 已经需要执行的数据库名
    prodict = {
               "week": {
                   # 作为附件的文件名字
                   "dingdanwangcheng_week":
                       {
                           # 执行sql 已经数据库名
                        dingdanwangcheng_week: ["_kenya"]
                   }
                         },

               "month": {
                    "dingdanwangcheng_month":
                        {
                         dingdanwangcheng_month:
                             [
                               "_kenya",
                               "_nigeria",
                               "_uganda"
                             ]
                        },
                    "tuihuanhuo_month":
                        {
                          tuihuanhuo:
                             [
                               "_kenya",
                              "_nigeria",
                              "_uganda"]
                        },
                    "fajing_month":
                       {
                         fajing:
                             [
                             "_kenya",
                            "_nigeria",
                            "_uganda"]
                       },
                         }
               }

    if not prodict.has_key(jobtype):
        print "key is err"
        sys.exit()
    sqldict = prodict[jobtype]
    # 遍历字典 ，批量导出execl
    filnamelist = []
    for sqlname, dbdict in sqldict.items():

        for sql, dbnamelist in dbdict.items():
            for dbname in dbnamelist:
                print "exec sql name:%s " % sqlname
                print "exec database:%s" % dbname
                filname = os.path.join(path, "%s-%s-%s.xls") % (today, dbname, sqlname)
                sub_main(dbname, filname, sql)
                filnamelist.append(filname)
                print "export filename:%s" % filname
    # 邮件发送
    sendMail(filnamelist, receiverlist)

if __name__ == "__main__":
    #接受邮件列表
    receiverlist = ["guo@mall.com",]


    # 导出的文件路径
    path = "D:\kilimall_report\caiwu"
    try:
        # 作为 执行的任务类型
       jobtype = sys.argv[1]
    except :
        print "follow a ago [week ,month]"
        sys.exit()
    main(path, jobtype)
