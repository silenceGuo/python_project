#!/usr/bin/env python
# ！-*-coding:utf-8 -*-
# !@Date    : 2018/12/17 0017 上午 10:12
# !@Author : Damon.guo
# !@File   : export_mysql_report.py
import sys
# sys.setdefaultencoding('utf8')
# sys.path.append("D:\Python27\Lib\site-packages")
# sys.path.append("d:\python27\lib")
# import pymysql
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
import xlsxwriter

host = '10.0.0.100'

# user = 'KILIMALL'
user = "root"

dbpass = "123456"

port = 3306


# 检查文件是否存在
def fileExists(filePath):
    if not os.path.exists(filePath):
        print "文件：%s 不存在，请检查" % filePath
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

    # 取上上周星期一时间
    while lastMonday.weekday() != calendar.MONDAY:
        lastMonday -= oneday
    lastMonday = lastMonday.strftime('%Y-%m-%d')

    # 取上上周星期天时间
    while lastSunday.weekday() != calendar.SUNDAY:
        lastSunday += oneday
    lastSunday = lastSunday.strftime('%Y-%m-%d')

    print "lastweekdate:%s %s" % (lastMonday, lastSunday)
    # 返回 上个星期一和星期天的具体日期
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


def sendMail(fileName, receiverlist):
    username = 'data_send@kilimall.com'
    password = '8Y9keikOOmWaaR9LA38d'
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
        # filename = file.split("\\")[-1]
        filename = file.split("/")[-1]

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
        # client.sendmail(sender, ['garcia.li@kilimall.com'], msg.as_string())
        # client.sendmail(sender, ['danni.wang@kilimall.com', 'vina.tang@kilimall.com', 'eason.yi@kilimall.com',
        #                          'garcia.li@kilimall.com', 'daisy.zeng@kilimall.com', 'jimmyscm@kilimall.com',
        #                          'lixia@kilimall.com', 'victor.ma@kilimall.com', 'sophia.li@kilimall.com'],
        #                 msg.as_string())
        #
        # client.sendmail(sender, ['516605659@qq.com', "damon.guo@kilimall.com"], msg.as_string())
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
    sqlDict = {}
    for i in listdir:
        if i.startswith("shuoming") or i.endswith(".csv") or i.endswith(".xls"):
            continue
        filname = i.split(".")[0]
        file = os.path.join(path, i)
        sqlDict[filname] = readMysql_fromFile(file)
        # sqllist.append(readMysql_fromFile(file))
    return sqlDict


def sub_main(dbname, filename, sql):
    # 执行sql 导出导文件
    today = str(datetime.date.today())
    conn, cur = connMysql(dbname)
    res = execMysql(cur, sql)

    result_list = list(res)
    # 设设置 数据格式str防止在execl 长的int 为乱码
    result = pd.DataFrame(result_list, dtype=str)
    # print cur.description
    # print result
    if not result.empty:
        result.columns = [filed[0] for filed in cur.description]  # 列表生成式，所有字段 表头
    # export_path_file = os.path.join(exportpath, "%s-%s.xls") % (today, filename)

    # result.to_csv(export_tpath_file, index=False, encoding="utf-8", float_format="%.2f")

    # result.to_excel(filename, index=False, encoding="utf-8")
    result.to_excel(filename, index=False, engine="xlsxwriter", encoding="utf-8")
    # result.to_csv(filename, index=False, encoding="utf-8")
    # result.to_xlss

    conn.close()
    return filename


def main(path, jobtype):
    """还可以继续优化，根据jobtype 对传入的sql语句中的时间赋值 ,不需要一个语句根据day week 定义多个sql"""
      # if jobtype == "week":
      #     start = startweekday
      #     end = endweekday
      # elif jobtype =="day":
      #       start = Yesterday
      #       end = Yesterday
      #
    startweekday, endweekday = getlastweek()
    stardmonthday, endmonthday = getLastDayOfLastMonth()

    stardtwomonthday, endtwomonthday = getLastDayOfLasttwoMonth()

    today = datetime.datetime.now()
    monthstarday = today.strftime("%Y-%m-01")
    today = today.strftime("%Y-%m-%d")

    Yesterday = getYesterday()
    Yesterday = Yesterday.strftime("%Y-%m-%d")

    print "销量日期区间，%s - %s" % (monthstarday, Yesterday)
    # print Yesterday
    # sys.exit()
    # 定义的周执行的sql脚本
    dingdanwangcheng_week = """SELECT 
  CONCAT(',',o.order_sn),
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
  oc.cash_rewards,
 ( so.`commission_amount` + so.`tech_fee` ) AS goods_commission
FROM
  nc_order_goods g 
  LEFT JOIN nc_order o 
    ON g.`order_id` = o.`order_id` 
  LEFT JOIN nc_order_common oc 
    ON o.`order_id` = oc.`order_id` 
  LEFT JOIN nc_shop_orders so 
    ON (g.`order_id` = so.`order_id` and g.`goods_id` = so.`goods_id` )
WHERE  o.finnshed_time >= UNIX_TIMESTAMP('%s 00:00:00')
  AND o.finnshed_time <= UNIX_TIMESTAMP('%s 23:59:59');""" % (startweekday, endweekday)

    tuihuanhuo_week = """SELECT 
      CONCAT(',',o.order_sn),
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
      rc.type,
      rf.`cash_rewards`
    FROM
      nc_order_goods g 
      LEFT JOIN nc_order o 
        ON g.`order_id` = o.`order_id` 
      LEFT JOIN nc_order_common oc 
        ON o.`order_id` = oc.`order_id` 
        LEFT JOIN nc_returns rc
        ON rc.`order_id` = o.`order_id`
        LEFT JOIN nc_return_refunds rf
        ON rc.`id` = rf.return_id
    WHERE  rc.id IN (SELECT id FROM nc_returns WHERE `status` = 4) AND rc.`type` IN (1,2) AND rc.updated_at >= UNIX_TIMESTAMP('%s 00:00:00') AND rc.updated_at <= UNIX_TIMESTAMP('%s 23:59:59')
    AND g.goods_id = rc.`goods_id` AND g.`order_id` = rc.`order_id`;""" % (startweekday, endweekday)
    fajing_week = """SELECT 
      CONCAT(',',order_sn),
      o.store_id,store_name,order_amount, FROM_UNIXTIME(payment_time) AS payment_time,order_state,
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
      AND payment_time <= UNIX_TIMESTAMP('%s 23:59:59') ;""" % (startweekday, endweekday)

    # 定义的月执行脚本
    dingdanwangcheng_month = """
      SELECT 
  CONCAT(',',o.order_sn),
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
  oc.cash_rewards,
 ( so.`commission_amount` + so.`tech_fee` ) AS goods_commission
FROM
  nc_order_goods g 
  LEFT JOIN nc_order o 
    ON g.`order_id` = o.`order_id` 
  LEFT JOIN nc_order_common oc 
    ON o.`order_id` = oc.`order_id` 
  LEFT JOIN nc_shop_orders so 
    ON (g.`order_id` = so.`order_id` and g.`goods_id` = so.`goods_id` )
WHERE  o.finnshed_time >= UNIX_TIMESTAMP('%s 00:00:00')
  AND o.finnshed_time <= UNIX_TIMESTAMP('%s 23:59:59'); """ % (stardmonthday, endmonthday)

    tuihuanhuo_month = """SELECT 
      CONCAT(',',o.order_sn),
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
      rc.type,
      rf.`cash_rewards`
    FROM
      nc_order_goods g 
      LEFT JOIN nc_order o 
        ON g.`order_id` = o.`order_id` 
      LEFT JOIN nc_order_common oc 
        ON o.`order_id` = oc.`order_id` 
        LEFT JOIN nc_returns rc
        ON rc.`order_id` = o.`order_id`
        LEFT JOIN nc_return_refunds rf
        ON rc.`id` = rf.return_id
    WHERE  rc.id IN (SELECT id FROM nc_returns WHERE `status` = 4) AND rc.`type` IN (1,2) AND rc.updated_at >= UNIX_TIMESTAMP('%s 00:00:00') AND rc.updated_at <= UNIX_TIMESTAMP('%s 23:59:59')
    AND g.goods_id = rc.`goods_id` AND g.`order_id` = rc.`order_id`;""" % (stardmonthday, endmonthday)

    fajing_month = """SELECT 
  CONCAT(',',order_sn),o.store_id,store_name,order_amount, FROM_UNIXTIME(payment_time) AS payment_time,order_state,
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
  AND payment_time <= UNIX_TIMESTAMP('%s 23:59:59') ;""" % (stardtwomonthday, endtwomonthday)

    xiaoliang1 = """SELECT
ooo.goods_commonid,
 ooo.goods_id,
 ooo.goods_name,
 ooo.goods_storage,
 ooo.solditem,
 ooo.store_id,
 ooo.store_name,
 ooo.oaddtime,
CASE ooo.is_global WHEN 1 THEN 'global'
ELSE 'local' END AS storetype,
 ooo.timess,
 gc.gc_name,
 gc1.gc_name,
 gc2.gc_name,
 ooo.paymenttime,
ooo.leixing,
ooo.goods_price
FROM
 (
  SELECT
  gs.goods_commonid,
   og.goods_id,
   og.store_id,
   o.store_name,
   gs.gc_id_1,
   gs.gc_id_2,
   gs.gc_id_3,
   og.goods_name,
   og.goods_price,
  store.is_global,
   gs.goods_storage,
   FROM_UNIXTIME(gs.goods_addtime) AS timess,
   FROM_UNIXTIME(o.add_time) AS oaddtime,
   CASE o.payment_time
  WHEN 0 THEN
   0
  ELSE
   FROM_UNIXTIME(o.payment_time, '%%Y%%m%%d')
  END AS paymenttime,
 CASE o.logistics_type WHEN 1 THEN 'FBK'
WHEN 2 THEN 'GS'
WHEN 0 THEN 'DS'
END AS leixing,
  SUM(og.goods_num) AS solditem
 FROM
  nc_order_goods og
 INNER JOIN nc_order o ON og.order_id = o.order_id
 INNER JOIN nc_goods gs ON og.goods_id = gs.goods_id
INNER JOIN nc_store store ON og.store_id=store.store_id
 WHERE
FROM_UNIXTIME(o.add_time, '%%Y%%m%%d') =%s
OR FROM_UNIXTIME(o.payment_time, '%%Y%%m%%d') =%s
 GROUP BY
 gs.goods_commonid,
  og.goods_id,
   og.store_id,
   o.store_name,
   gs.gc_id_1,
   gs.gc_id_2,
   gs.gc_id_3,
   og.goods_name,
   og.goods_price, store.is_global,
   gs.goods_storage,timess,paymenttime,leixing
 ) AS ooo
INNER JOIN nc_goods_class gc ON ooo.gc_id_1 = gc.gc_id
INNER JOIN nc_goods_class gc1 ON ooo.gc_id_2 = gc1.gc_id
INNER JOIN nc_goods_class gc2 ON ooo.gc_id_3 = gc2.gc_id""" % (monthstarday, Yesterday)
    xiaoliang_day = """SELECT
ooo.goods_commonid,
 ooo.goods_id,
 ooo.goods_name,
 ooo.goods_storage,
 ooo.solditem,
 ooo.store_id,
 ooo.store_name,
CASE ooo.is_global WHEN 1 THEN 'global'
ELSE 'local' END AS storetype,
 ooo.timess,
 gc.gc_name,
 gc1.gc_name,
 gc2.gc_name,
 ooo.oaddtime,
 ooo.paymenttime,
ooo.leixing,
ooo.goods_price
FROM
 (
  SELECT
  gs.goods_commonid,
   og.goods_id,
   og.store_id,
   o.store_name,
   gs.gc_id_1,
   gs.gc_id_2,
   gs.gc_id_3,
   og.goods_name,
   og.goods_price,
  store.is_global,
   gs.goods_storage,

   FROM_UNIXTIME(gs.goods_addtime) AS timess,
   FROM_UNIXTIME(o.add_time, '%%Y%%m%%d') AS oaddtime,
   CASE o.payment_time
  WHEN 0 THEN
   0
  ELSE
   FROM_UNIXTIME(o.payment_time, '%%Y%%m%%d')
  END AS paymenttime,
 CASE o.logistics_type WHEN 1 THEN 'FBK'
WHEN 2 THEN 'GS'
WHEN 0 THEN 'DS'
END AS leixing,
  SUM(og.goods_num) AS solditem
 FROM
  nc_order_goods og
 INNER JOIN nc_order o ON og.order_id = o.order_id
 INNER JOIN nc_goods gs ON og.goods_id = gs.goods_id
INNER JOIN nc_store store ON og.store_id=store.store_id
 WHERE
o.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')
OR (o.payment_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59'))
 GROUP BY
 gs.goods_commonid,
  og.goods_id,
   og.store_id,
   o.store_name,
   gs.gc_id_1,
   gs.gc_id_2,
   gs.gc_id_3,
   og.goods_name,
   og.goods_price, store.is_global,
   gs.goods_storage,timess,paymenttime,leixing
 ) AS ooo
INNER JOIN nc_goods_class gc ON ooo.gc_id_1 = gc.gc_id
INNER JOIN nc_goods_class gc1 ON ooo.gc_id_2 = gc1.gc_id
INNER JOIN nc_goods_class gc2 ON ooo.gc_id_3 = gc2.gc_id""" % (Yesterday, Yesterday, Yesterday, Yesterday)
    xiaoliang_week = """SELECT
ooo.goods_commonid,
 ooo.goods_id,
 ooo.goods_name,
 ooo.goods_storage,
 ooo.solditem,
 ooo.store_id,
 ooo.store_name,
CASE ooo.is_global WHEN 1 THEN 'global'
ELSE 'local' END AS storetype,
 ooo.timess,
 gc.gc_name,
 gc1.gc_name,
 gc2.gc_name,
 ooo.oaddtime,
 ooo.paymenttime,
ooo.leixing,
ooo.goods_price
FROM
 (
  SELECT
  gs.goods_commonid,
   og.goods_id,
   og.store_id,
   o.store_name,
   gs.gc_id_1,
   gs.gc_id_2,
   gs.gc_id_3,
   og.goods_name,
   og.goods_price,
  store.is_global,
   gs.goods_storage,

   FROM_UNIXTIME(gs.goods_addtime) AS timess,
   FROM_UNIXTIME(o.add_time, '%%Y%%m%%d') AS oaddtime,
   CASE o.payment_time
  WHEN 0 THEN
   0
  ELSE
   FROM_UNIXTIME(o.payment_time, '%%Y%%m%%d')
  END AS paymenttime,
 CASE o.logistics_type WHEN 1 THEN 'FBK'
WHEN 2 THEN 'GS'
WHEN 0 THEN 'DS'
END AS leixing,
  SUM(og.goods_num) AS solditem
 FROM
  nc_order_goods og
 INNER JOIN nc_order o ON og.order_id = o.order_id
 INNER JOIN nc_goods gs ON og.goods_id = gs.goods_id
INNER JOIN nc_store store ON og.store_id=store.store_id
 WHERE
o.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')
OR (o.payment_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59'))
 GROUP BY
 gs.goods_commonid,
  og.goods_id,
   og.store_id,
   o.store_name,
   gs.gc_id_1,
   gs.gc_id_2,
   gs.gc_id_3,
   og.goods_name,
   og.goods_price, store.is_global,
   gs.goods_storage,timess,paymenttime,leixing
 ) AS ooo
INNER JOIN nc_goods_class gc ON ooo.gc_id_1 = gc.gc_id
INNER JOIN nc_goods_class gc1 ON ooo.gc_id_2 = gc1.gc_id
INNER JOIN nc_goods_class gc2 ON ooo.gc_id_3 = gc2.gc_id;""" % (startweekday, endweekday, startweekday, endweekday)
    xiaoliang_month = """SELECT
    ooo.goods_commonid,
     ooo.goods_id,
     ooo.goods_name,
     ooo.goods_storage,
     ooo.solditem,
     ooo.store_id,
     ooo.store_name,
    CASE ooo.is_global WHEN 1 THEN 'global'
    ELSE 'local' END AS storetype,
     ooo.timess,
     gc.gc_name,
     gc1.gc_name,
     gc2.gc_name,
     ooo.oaddtime,
     ooo.paymenttime,
    ooo.leixing,
    ooo.goods_price
    FROM
     (
      SELECT
      gs.goods_commonid,
       og.goods_id,
       og.store_id,
       o.store_name,
       gs.gc_id_1,
       gs.gc_id_2,
       gs.gc_id_3,
       og.goods_name,
       og.goods_price,
      store.is_global,
       gs.goods_storage,

       FROM_UNIXTIME(gs.goods_addtime) AS timess,
       FROM_UNIXTIME(o.add_time, '%%Y%%m%%d') AS oaddtime,
       CASE o.payment_time
      WHEN 0 THEN
       0
      ELSE
       FROM_UNIXTIME(o.payment_time, '%%Y%%m%%d')
      END AS paymenttime,
     CASE o.logistics_type WHEN 1 THEN 'FBK'
    WHEN 2 THEN 'GS'
    WHEN 0 THEN 'DS'
    END AS leixing,
      SUM(og.goods_num) AS solditem
     FROM
      nc_order_goods og
     INNER JOIN nc_order o ON og.order_id = o.order_id
     INNER JOIN nc_goods gs ON og.goods_id = gs.goods_id
    INNER JOIN nc_store store ON og.store_id=store.store_id
     WHERE
    o.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')
    OR (o.payment_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59'))
     GROUP BY
     gs.goods_commonid,
      og.goods_id,
       og.store_id,
       o.store_name,
       gs.gc_id_1,
       gs.gc_id_2,
       gs.gc_id_3,
       og.goods_name,
       og.goods_price, store.is_global,
       gs.goods_storage,timess,paymenttime,leixing
     ) AS ooo
    INNER JOIN nc_goods_class gc ON ooo.gc_id_1 = gc.gc_id
    INNER JOIN nc_goods_class gc1 ON ooo.gc_id_2 = gc1.gc_id
    INNER JOIN nc_goods_class gc2 ON ooo.gc_id_3 = gc2.gc_id;""" % (
    stardmonthday, endmonthday, stardmonthday, endmonthday)

    # 自营销售数据，所有的店铺和单独个人管理数据，按每天，每周，每月定时一起发送到日 周 月邮件列表
    ziyingxiaoshou_day = """SELECT
     CONCAT(',',t.order_sn),
     t.voucher,
     t.voucher_type,
     t.order_amount,
     t.manjian,
     t.store_id,
     t.store_name,
     t.finnshed_time,
     t.add_time,
     t.logistics_type,
     t.goods_id,
     t.goods_name,
     t.is_global,

    IF (
     t.voucher_type = 0,
     t.goods_price + t.manjian - t.voucher,
     t.goods_price + t.manjian
    ) goods_price,
     t.commis_rate,
     t.goods_num,
     t.goods_type,
     t.gc_id,
     t.refund_id,
     t.goods_storage,
     t.payment_time,
     t.goods_liquidate_price,
     t.goods_liquidate_amount,
    	t.dmember_mobile,
    t.dmember_name,
    t.goods_serial,
    t.order_amount
    FROM
     (
      SELECT
       a.order_sn,
       IFNULL(
        common.voucher_price / (a.goods_amount) * goods.goods_price,
        0
       ) AS voucher,
       common.voucher_type,
       a.order_amount,
       IFNULL(
        (
         a.order_amount - a.goods_amount - a.shipping_fee
        ) / (a.goods_amount) * goods.goods_price,
        0
       ) AS manjian, 
       a.store_id,
       s.store_name,
       s.is_global,
       FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
       FROM_UNIXTIME(a.add_time) AS add_time,
       a.logistics_type,
       goods.goods_id,
       goods.goods_name,
       goods.goods_price,
       goods.commis_rate,
       goods.goods_num,
       goods.goods_type,
       goods.gc_id,
       gs.goods_storage,
       n.refund_id,
       FROM_UNIXTIME(a.payment_time) payment_time,
       goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
       goods.goods_liquidate_amount,
    	 kili.dmember_name,
    		kili.dmember_mobile,
    		commons.goods_serial
      FROM
       nc_order a
      LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
      LEFT JOIN nc_order_common common ON common.order_id = a.order_id
      LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
      LEFT JOIN nc_store s ON s.store_id = a.store_id
      LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
      LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
      LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
      WHERE
       a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')

    AND a.store_id IN (2706,
2606,
2189,
829,
2195,
2475,
2499,
2476,
2498,
2905,
3087,
653,
3036,
3271,
3272,
2272,
3406,
3906,
2757,
4429,
2518,
1,
2391,
2977,
3007,
3248,
3257,
3243,
3479,
3972,
3258,
3251,
2628,
2610,
2609,
2607,
2617,
3192,
3191,
3187,
3190,
3186,
3182,
3189,
3185,
3181,
3184,
3255,
3478,
3485,
3490,
3499,
3511,
3554,
3507,
1312,
3730,
4436,
2336,
95,
2877,
2415,
2526,
2393,
3482,
3487,
3729,
3492,
3601,
3515,
3571,
3541,
3578,
2096,
2819,
2546,
2547,
3090,
2482,
2886,
3250,
3260,
3256,
3254,
3242,
3249,
3246,
3244,
3259,
3252,
3408,
3253,
2622,
2620,
2619,
2642,
2618,
2629,
2655,
2648,
2632,
2633,
2649,
2654,
2646,
2611,
2613,
2612,
2621,
2608,
2631,
2651,
2616,
2650,
2615,
2624,
2638,
2652,
2645,
2653,
2625,
2639,
2635,
2614,
2640,
2637,
2626,
2623,
2636,
2656,
2647,
2641,
2643,
2630,
2644,
2634,
2627,
3193,
3188,
3180,
3178,
3177,
3179,
3176,
3174,
3175,
3173,
3480,
3481,
3483,
3484,
3486,
3488,
3489,
3491,
3493,
3494,
3495,
3496,
3497,
3498,
3500,
3501,
3502,
3503,
3504,
3505,
3506,
3508,
3509,
3510,
3512,
3513,
3514,
3516,
3517,
3518,
3519,
3520,
3521,
3522,
3523,
3524,
3525,
3526,
3527,
3528,
3529,
3530,
3531,
3532,
3533,
3534,
3535,
3536,
3537,
3538,
3539,
3540,
3541,
3542,
3543,
3544,
3545,
3546,
3547,
3548,
3549,
3550,
3551,
3552,
3553,
3555,
3556,
3558,
3559,
3560,
3561,
3562,
3563,
3564,
3565,
3566,
3567,
3568,
3569,
3570,
3571,
3572,
3573,
3574,
3575,
3576,
3577,
3579,
3580,
3581,
3582,
3583,
3584,
3585,
3586,
3587,
3588,
3589,
3590,
3591,
3592,
3593,
3594,
3595,
3596,
3597,
3598,
3599,
3600,
3602,
3603,
3604,
3605,
3606,
3607,
3608,
3609,
3610,
3611,
3612,
3613,
3614,
3615,
3616,
3617,
3618,
3619,
3620,
3621,
3622,
3623,
3624,
3625,
3626,
3627,
3628,
3629,
3630,
3631,
3632,
3633,
3634,
3635,
3636,
3637,
3638,
3639,
3640,
3641,
3642,
3643,
3644,
3645,
3646,
3647,
3648,
3649,
3650,
3651,
3652,
3653,
3654,
3655,
3656,
3657,
3658,
3659,
3660,
3661,
3662,
3663,
3664,
3665,
3666,
3667,
3668,
3669,
3670,
3671,
3672,
3673,
3674,
3675,
3676,
3677,
3678,
3679,
3680,
3681,
3682,
3683,
3684,
3685,
3686,
3687,
3688,
3689,
3690,
3691,
3692,
3693,
3694,
3695,
3696,
3697,
3698,
3699,
3700,
3701,
3702,
3703,
3704,
3705,
3706,
3707,
3708,
3709,
3710,
3711,
3712,
3713,
3714,
3715,
3716,
3717,
3718,
3719,
3720,
3721,
3722,
3723,
3724,
3725,
3726,
3727,
3728,
3731,
3732,
3733,
3734,
3735,
3736,
3737,
3738,
3739,
3740,
3741,
3742,
3743,
3744,
3745,
3746,
3747,
3748,
3749,
3750,
3751,
3752,
3753,
3754,
3755,
3756,
3757,
2442,
1888,
2053,
2137,
3075,
3076,
3077,
2118,
3056,
3407,
3397,
767,
2977))t""" % (Yesterday, Yesterday)
    ziyingxiaoshou_day_cathy = """SELECT
         CONCAT(',',t.order_sn),
         t.voucher,
         t.voucher_type,
         t.order_amount,
         t.manjian,
         t.store_id,
         t.store_name,
         t.finnshed_time,
         t.add_time,
         t.logistics_type,
         t.goods_id,
         t.goods_name,
         t.is_global,

        IF (
         t.voucher_type = 0,
         t.goods_price + t.manjian - t.voucher,
         t.goods_price + t.manjian
        ) goods_price,
         t.commis_rate,
         t.goods_num,
         t.goods_type,
         t.gc_id,
         t.refund_id,
         t.goods_storage,
         t.payment_time,
         t.goods_liquidate_price,
         t.goods_liquidate_amount,
        	t.dmember_mobile,
        t.dmember_name,
        t.goods_serial,
        t.order_amount
        FROM
         (
          SELECT
           a.order_sn,
           IFNULL(
            common.voucher_price / (a.goods_amount) * goods.goods_price,
            0
           ) AS voucher,
           common.voucher_type,
           a.order_amount,
           IFNULL(
            (
             a.order_amount - a.goods_amount - a.shipping_fee
            ) / (a.goods_amount) * goods.goods_price,
            0
           ) AS manjian, 
           a.store_id,
           s.store_name,
           s.is_global,
           FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
           FROM_UNIXTIME(a.add_time) AS add_time,
           a.logistics_type,
           goods.goods_id,
           goods.goods_name,
           goods.goods_price,
           goods.commis_rate,
           goods.goods_num,
           goods.goods_type,
           goods.gc_id,
           gs.goods_storage,
           n.refund_id,
           FROM_UNIXTIME(a.payment_time) payment_time,
           goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
           goods.goods_liquidate_amount,
        	 kili.dmember_name,
        		kili.dmember_mobile,
        		commons.goods_serial
          FROM
           nc_order a
          LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
          LEFT JOIN nc_order_common common ON common.order_id = a.order_id
          LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
          LEFT JOIN nc_store s ON s.store_id = a.store_id
          LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
          LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
          LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
          WHERE
           a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')

        AND a.store_id IN (2518,
2391,
2977,
3007,
3248,
3257,
3243,
3479,
3972,
3258,
3251,
2628,
2610,
2609,
2607,
2617,
3192,
3191,
3187,
3190,
3186,
3182,
3189,
3185,
3181,
3184,
3255,
3478,
3485,
3490,
3499,
3511,
3554,
3507,
1312,
3730,
4436,
2336,
95
))t""" % (Yesterday, Yesterday)
    ziyingxiaoshou_day_garcia = """SELECT
            CONCAT(',',t.order_sn),
            t.voucher,
            t.voucher_type,
            t.order_amount,
            t.manjian,
            t.store_id,
            t.store_name,
            t.finnshed_time,
            t.add_time,
            t.logistics_type,
            t.goods_id,
            t.goods_name,
            t.is_global,

           IF (
            t.voucher_type = 0,
            t.goods_price + t.manjian - t.voucher,
            t.goods_price + t.manjian
           ) goods_price,
            t.commis_rate,
            t.goods_num,
            t.goods_type,
            t.gc_id,
            t.refund_id,
            t.goods_storage,
            t.payment_time,
            t.goods_liquidate_price,
            t.goods_liquidate_amount,
           	t.dmember_mobile,
           t.dmember_name,
           t.goods_serial,
           t.order_amount
           FROM
            (
             SELECT
              a.order_sn,
              IFNULL(
               common.voucher_price / (a.goods_amount) * goods.goods_price,
               0
              ) AS voucher,
              common.voucher_type,
              a.order_amount,
              IFNULL(
               (
                a.order_amount - a.goods_amount - a.shipping_fee
               ) / (a.goods_amount) * goods.goods_price,
               0
              ) AS manjian, 
              a.store_id,
              s.store_name,
              s.is_global,
              FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
              FROM_UNIXTIME(a.add_time) AS add_time,
              a.logistics_type,
              goods.goods_id,
              goods.goods_name,
              goods.goods_price,
              goods.commis_rate,
              goods.goods_num,
              goods.goods_type,
              goods.gc_id,
              gs.goods_storage,
              n.refund_id,
              FROM_UNIXTIME(a.payment_time) payment_time,
              goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
              goods.goods_liquidate_amount,
           	 kili.dmember_name,
           		kili.dmember_mobile,
           		commons.goods_serial
             FROM
              nc_order a
             LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
             LEFT JOIN nc_order_common common ON common.order_id = a.order_id
             LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
             LEFT JOIN nc_store s ON s.store_id = a.store_id
             LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
             LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
             LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
             WHERE
              a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')

           AND a.store_id IN (2706,1,
2606,
2189,
829,
2195,
2475,
2499,
2476,
2498,
2905,
3087,
653,
3036,
3271,
3272,
2272,
3406,
3906,
2757,
4429)) t""" % (Yesterday, Yesterday)
    ziyingxiaoshou_day_shenzhen = """SELECT
            CONCAT(',',t.order_sn),
            t.voucher,
            t.voucher_type,
            t.order_amount,
            t.manjian,
            t.store_id,
            t.store_name,
            t.finnshed_time,
            t.add_time,
            t.logistics_type,
            t.goods_id,
            t.goods_name,
            t.is_global,

           IF (
            t.voucher_type = 0,
            t.goods_price + t.manjian - t.voucher,
            t.goods_price + t.manjian
           ) goods_price,
            t.commis_rate,
            t.goods_num,
            t.goods_type,
            t.gc_id,
            t.refund_id,
            t.goods_storage,
            t.payment_time,
            t.goods_liquidate_price,
            t.goods_liquidate_amount,
           	t.dmember_mobile,
           t.dmember_name,
           t.goods_serial,
           t.order_amount
           FROM
            (
             SELECT
              a.order_sn,
              IFNULL(
               common.voucher_price / (a.goods_amount) * goods.goods_price,
               0
              ) AS voucher,
              common.voucher_type,
              a.order_amount,
              IFNULL(
               (
                a.order_amount - a.goods_amount - a.shipping_fee
               ) / (a.goods_amount) * goods.goods_price,
               0
              ) AS manjian, 
              a.store_id,
              s.store_name,
              s.is_global,
              FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
              FROM_UNIXTIME(a.add_time) AS add_time,
              a.logistics_type,
              goods.goods_id,
              goods.goods_name,
              goods.goods_price,
              goods.commis_rate,
              goods.goods_num,
              goods.goods_type,
              goods.gc_id,
              gs.goods_storage,
              n.refund_id,
              FROM_UNIXTIME(a.payment_time) payment_time,
              goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
              goods.goods_liquidate_amount,
           	 kili.dmember_name,
           		kili.dmember_mobile,
           		commons.goods_serial
             FROM
              nc_order a
             LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
             LEFT JOIN nc_order_common common ON common.order_id = a.order_id
             LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
             LEFT JOIN nc_store s ON s.store_id = a.store_id
             LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
             LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
             LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
             WHERE
              a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')

           AND a.store_id IN (2442,
1888,
2053,
2137,
3075,
3076,
3077,
2118,
3056,
3407,
3397,
767,
2977)) t""" % (Yesterday, Yesterday)
    ziyingxiaoshou_day_lucy = """SELECT
            CONCAT(',',t.order_sn),
            t.voucher,
            t.voucher_type,
            t.order_amount,
            t.manjian,
            t.store_id,
            t.store_name,
            t.finnshed_time,
            t.add_time,
            t.logistics_type,
            t.goods_id,
            t.goods_name,
            t.is_global,

           IF (
            t.voucher_type = 0,
            t.goods_price + t.manjian - t.voucher,
            t.goods_price + t.manjian
           ) goods_price,
            t.commis_rate,
            t.goods_num,
            t.goods_type,
            t.gc_id,
            t.refund_id,
            t.goods_storage,
            t.payment_time,
            t.goods_liquidate_price,
            t.goods_liquidate_amount,
           	t.dmember_mobile,
           t.dmember_name,
           t.goods_serial,
           t.order_amount
           FROM
            (
             SELECT
              a.order_sn,
              IFNULL(
               common.voucher_price / (a.goods_amount) * goods.goods_price,
               0
              ) AS voucher,
              common.voucher_type,
              a.order_amount,
              IFNULL(
               (
                a.order_amount - a.goods_amount - a.shipping_fee
               ) / (a.goods_amount) * goods.goods_price,
               0
              ) AS manjian, 
              a.store_id,
              s.store_name,
              s.is_global,
              FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
              FROM_UNIXTIME(a.add_time) AS add_time,
              a.logistics_type,
              goods.goods_id,
              goods.goods_name,
              goods.goods_price,
              goods.commis_rate,
              goods.goods_num,
              goods.goods_type,
              goods.gc_id,
              gs.goods_storage,
              n.refund_id,
              FROM_UNIXTIME(a.payment_time) payment_time,
              goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
              goods.goods_liquidate_amount,
           	 kili.dmember_name,
           		kili.dmember_mobile,
           		commons.goods_serial
             FROM
              nc_order a
             LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
             LEFT JOIN nc_order_common common ON common.order_id = a.order_id
             LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
             LEFT JOIN nc_store s ON s.store_id = a.store_id
             LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
             LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
             LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
             WHERE
              a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')

           AND a.store_id IN (2877,
2415,
2526,
2393,
3482,
3487,
3729,
3492,
3601,
3515,
3571,
3541,
3578,
2096,
2819,
2546,
2547,
3090,
2482,
2886,
3250,
3260,
3256,
3254,
3242,
3249,
3246,
3244,
3259,
3252,
3408,
3253,
2622,
2620,
2619,
2642,
2618,
2629,
2655,
2648,
2632,
2633,
2649,
2654,
2646,
2611,
2613,
2612,
2621,
2608,
2631,
2651,
2616,
2650,
2615,
2624,
2638,
2652,
2645,
2653,
2625,
2639,
2635,
2614,
2640,
2637,
2626,
2623,
2636,
2656,
2647,
2641,
2643,
2630,
2644,
2634,
2627,
3193,
3188,
3180,
3178,
3177,
3179,
3176,
3174,
3175,
3173,
3480,
3481,
3483,
3484,
3486,
3488,
3489,
3491,
3493,
3494,
3495,
3496,
3497,
3498,
3500,
3501,
3502,
3503,
3504,
3505,
3506,
3508,
3509,
3510,
3512,
3513,
3514,
3516,
3517,
3518,
3519,
3520,
3521,
3522,
3523,
3524,
3525,
3526,
3527,
3528,
3529,
3530,
3531,
3532,
3533,
3534,
3535,
3536,
3537,
3538,
3539,
3540,
3541,
3542,
3543,
3544,
3545,
3546,
3547,
3548,
3549,
3550,
3551,
3552,
3553,
3555,
3556,
3558,
3559,
3560,
3561,
3562,
3563,
3564,
3565,
3566,
3567,
3568,
3569,
3570,
3571,
3572,
3573,
3574,
3575,
3576,
3577,
3579,
3580,
3581,
3582,
3583,
3584,
3585,
3586,
3587,
3588,
3589,
3590,
3591,
3592,
3593,
3594,
3595,
3596,
3597,
3598,
3599,
3600,
3602,
3603,
3604,
3605,
3606,
3607,
3608,
3609,
3610,
3611,
3612,
3613,
3614,
3615,
3616,
3617,
3618,
3619,
3620,
3621,
3622,
3623,
3624,
3625,
3626,
3627,
3628,
3629,
3630,
3631,
3632,
3633,
3634,
3635,
3636,
3637,
3638,
3639,
3640,
3641,
3642,
3643,
3644,
3645,
3646,
3647,
3648,
3649,
3650,
3651,
3652,
3653,
3654,
3655,
3656,
3657,
3658,
3659,
3660,
3661,
3662,
3663,
3664,
3665,
3666,
3667,
3668,
3669,
3670,
3671,
3672,
3673,
3674,
3675,
3676,
3677,
3678,
3679,
3680,
3681,
3682,
3683,
3684,
3685,
3686,
3687,
3688,
3689,
3690,
3691,
3692,
3693,
3694,
3695,
3696,
3697,
3698,
3699,
3700,
3701,
3702,
3703,
3704,
3705,
3706,
3707,
3708,
3709,
3710,
3711,
3712,
3713,
3714,
3715,
3716,
3717,
3718,
3719,
3720,
3721,
3722,
3723,
3724,
3725,
3726,
3727,
3728,
3731,
3732,
3733,
3734,
3735,
3736,
3737,
3738,
3739,
3740,
3741,
3742,
3743,
3744,
3745,
3746,
3747,
3748,
3749,
3750,
3751,
3752,
3753,
3754,
3755,
3756,
3757
)) t""" % (Yesterday, Yesterday)

    ziyingxiaoshou_week = """SELECT
         CONCAT(',',t.order_sn),
         t.voucher,
         t.voucher_type,
         t.order_amount,
         t.manjian,
         t.store_id,
         t.store_name,
         t.finnshed_time,
         t.add_time,
         t.logistics_type,
         t.goods_id,
         t.goods_name,
         t.is_global,

        IF (
         t.voucher_type = 0,
         t.goods_price + t.manjian - t.voucher,
         t.goods_price + t.manjian
        ) goods_price,
         t.commis_rate,
         t.goods_num,
         t.goods_type,
         t.gc_id,
         t.refund_id,
         t.goods_storage,
         t.payment_time,
         t.goods_liquidate_price,
         t.goods_liquidate_amount,
        	t.dmember_mobile,
        t.dmember_name,
        t.goods_serial,
        t.order_amount
        FROM
         (
          SELECT
           a.order_sn,
           IFNULL(
            common.voucher_price / (a.goods_amount) * goods.goods_price,
            0
           ) AS voucher,
           common.voucher_type,
           a.order_amount,
           IFNULL(
            (
             a.order_amount - a.goods_amount - a.shipping_fee
            ) / (a.goods_amount) * goods.goods_price,
            0
           ) AS manjian, 
           a.store_id,
           s.store_name,
           s.is_global,
           FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
           FROM_UNIXTIME(a.add_time) AS add_time,
           a.logistics_type,
           goods.goods_id,
           goods.goods_name,
           goods.goods_price,
           goods.commis_rate,
           goods.goods_num,
           goods.goods_type,
           goods.gc_id,
           gs.goods_storage,
           n.refund_id,
           FROM_UNIXTIME(a.payment_time) payment_time,
           goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
           goods.goods_liquidate_amount,
        	 kili.dmember_name,
        		kili.dmember_mobile,
        		commons.goods_serial
          FROM
           nc_order a
          LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
          LEFT JOIN nc_order_common common ON common.order_id = a.order_id
          LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
          LEFT JOIN nc_store s ON s.store_id = a.store_id
          LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
          LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
          LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
          WHERE
           a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')

        AND a.store_id IN (2706,
    2606,
    2189,
    829,
    2195,
    2475,
    2499,
    2476,
    2498,
    2905,
    3087,
    653,
    3036,
    3271,
    3272,
    2272,
    3406,
    3906,
    2757,
    4429,
    2518,
    1,
    2391,
    2977,
    3007,
    3248,
    3257,
    3243,
    3479,
    3972,
    3258,
    3251,
    2628,
    2610,
    2609,
    2607,
    2617,
    3192,
    3191,
    3187,
    3190,
    3186,
    3182,
    3189,
    3185,
    3181,
    3184,
    3255,
    3478,
    3485,
    3490,
    3499,
    3511,
    3554,
    3507,
    1312,
    3730,
    4436,
    2336,
    95,
    2877,
    2415,
    2526,
    2393,
    3482,
    3487,
    3729,
    3492,
    3601,
    3515,
    3571,
    3541,
    3578,
    2096,
    2819,
    2546,
    2547,
    3090,
    2482,
    2886,
    3250,
    3260,
    3256,
    3254,
    3242,
    3249,
    3246,
    3244,
    3259,
    3252,
    3408,
    3253,
    2622,
    2620,
    2619,
    2642,
    2618,
    2629,
    2655,
    2648,
    2632,
    2633,
    2649,
    2654,
    2646,
    2611,
    2613,
    2612,
    2621,
    2608,
    2631,
    2651,
    2616,
    2650,
    2615,
    2624,
    2638,
    2652,
    2645,
    2653,
    2625,
    2639,
    2635,
    2614,
    2640,
    2637,
    2626,
    2623,
    2636,
    2656,
    2647,
    2641,
    2643,
    2630,
    2644,
    2634,
    2627,
    3193,
    3188,
    3180,
    3178,
    3177,
    3179,
    3176,
    3174,
    3175,
    3173,
    3480,
    3481,
    3483,
    3484,
    3486,
    3488,
    3489,
    3491,
    3493,
    3494,
    3495,
    3496,
    3497,
    3498,
    3500,
    3501,
    3502,
    3503,
    3504,
    3505,
    3506,
    3508,
    3509,
    3510,
    3512,
    3513,
    3514,
    3516,
    3517,
    3518,
    3519,
    3520,
    3521,
    3522,
    3523,
    3524,
    3525,
    3526,
    3527,
    3528,
    3529,
    3530,
    3531,
    3532,
    3533,
    3534,
    3535,
    3536,
    3537,
    3538,
    3539,
    3540,
    3541,
    3542,
    3543,
    3544,
    3545,
    3546,
    3547,
    3548,
    3549,
    3550,
    3551,
    3552,
    3553,
    3555,
    3556,
    3558,
    3559,
    3560,
    3561,
    3562,
    3563,
    3564,
    3565,
    3566,
    3567,
    3568,
    3569,
    3570,
    3571,
    3572,
    3573,
    3574,
    3575,
    3576,
    3577,
    3579,
    3580,
    3581,
    3582,
    3583,
    3584,
    3585,
    3586,
    3587,
    3588,
    3589,
    3590,
    3591,
    3592,
    3593,
    3594,
    3595,
    3596,
    3597,
    3598,
    3599,
    3600,
    3602,
    3603,
    3604,
    3605,
    3606,
    3607,
    3608,
    3609,
    3610,
    3611,
    3612,
    3613,
    3614,
    3615,
    3616,
    3617,
    3618,
    3619,
    3620,
    3621,
    3622,
    3623,
    3624,
    3625,
    3626,
    3627,
    3628,
    3629,
    3630,
    3631,
    3632,
    3633,
    3634,
    3635,
    3636,
    3637,
    3638,
    3639,
    3640,
    3641,
    3642,
    3643,
    3644,
    3645,
    3646,
    3647,
    3648,
    3649,
    3650,
    3651,
    3652,
    3653,
    3654,
    3655,
    3656,
    3657,
    3658,
    3659,
    3660,
    3661,
    3662,
    3663,
    3664,
    3665,
    3666,
    3667,
    3668,
    3669,
    3670,
    3671,
    3672,
    3673,
    3674,
    3675,
    3676,
    3677,
    3678,
    3679,
    3680,
    3681,
    3682,
    3683,
    3684,
    3685,
    3686,
    3687,
    3688,
    3689,
    3690,
    3691,
    3692,
    3693,
    3694,
    3695,
    3696,
    3697,
    3698,
    3699,
    3700,
    3701,
    3702,
    3703,
    3704,
    3705,
    3706,
    3707,
    3708,
    3709,
    3710,
    3711,
    3712,
    3713,
    3714,
    3715,
    3716,
    3717,
    3718,
    3719,
    3720,
    3721,
    3722,
    3723,
    3724,
    3725,
    3726,
    3727,
    3728,
    3731,
    3732,
    3733,
    3734,
    3735,
    3736,
    3737,
    3738,
    3739,
    3740,
    3741,
    3742,
    3743,
    3744,
    3745,
    3746,
    3747,
    3748,
    3749,
    3750,
    3751,
    3752,
    3753,
    3754,
    3755,
    3756,
    3757,
    2442,
    1888,
    2053,
    2137,
    3075,
    3076,
    3077,
    2118,
    3056,
    3407,
    3397,
    767,
    2977))t""" % (startweekday, endweekday)
    ziyingxiaoshou_week_cathy = """SELECT
             CONCAT(',',t.order_sn),
             t.voucher,
             t.voucher_type,
             t.order_amount,
             t.manjian,
             t.store_id,
             t.store_name,
             t.finnshed_time,
             t.add_time,
             t.logistics_type,
             t.goods_id,
             t.goods_name,
             t.is_global,

            IF (
             t.voucher_type = 0,
             t.goods_price + t.manjian - t.voucher,
             t.goods_price + t.manjian
            ) goods_price,
             t.commis_rate,
             t.goods_num,
             t.goods_type,
             t.gc_id,
             t.refund_id,
             t.goods_storage,
             t.payment_time,
             t.goods_liquidate_price,
             t.goods_liquidate_amount,
            	t.dmember_mobile,
            t.dmember_name,
            t.goods_serial,
            t.order_amount
            FROM
             (
              SELECT
               a.order_sn,
               IFNULL(
                common.voucher_price / (a.goods_amount) * goods.goods_price,
                0
               ) AS voucher,
               common.voucher_type,
               a.order_amount,
               IFNULL(
                (
                 a.order_amount - a.goods_amount - a.shipping_fee
                ) / (a.goods_amount) * goods.goods_price,
                0
               ) AS manjian, 
               a.store_id,
               s.store_name,
               s.is_global,
               FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
               FROM_UNIXTIME(a.add_time) AS add_time,
               a.logistics_type,
               goods.goods_id,
               goods.goods_name,
               goods.goods_price,
               goods.commis_rate,
               goods.goods_num,
               goods.goods_type,
               goods.gc_id,
               gs.goods_storage,
               n.refund_id,
               FROM_UNIXTIME(a.payment_time) payment_time,
               goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
               goods.goods_liquidate_amount,
            	 kili.dmember_name,
            		kili.dmember_mobile,
            		commons.goods_serial
              FROM
               nc_order a
              LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
              LEFT JOIN nc_order_common common ON common.order_id = a.order_id
              LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
              LEFT JOIN nc_store s ON s.store_id = a.store_id
              LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
              LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
              LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
              WHERE
               a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')

            AND a.store_id IN (2518,
    2391,
    2977,
    3007,
    3248,
    3257,
    3243,
    3479,
    3972,
    3258,
    3251,
    2628,
    2610,
    2609,
    2607,
    2617,
    3192,
    3191,
    3187,
    3190,
    3186,
    3182,
    3189,
    3185,
    3181,
    3184,
    3255,
    3478,
    3485,
    3490,
    3499,
    3511,
    3554,
    3507,
    1312,
    3730,
    4436,
    2336,
    95
    ))t""" % (startweekday, endweekday)
    ziyingxiaoshou_week_garcia = """SELECT
                CONCAT(',',t.order_sn),
                t.voucher,
                t.voucher_type,
                t.order_amount,
                t.manjian,
                t.store_id,
                t.store_name,
                t.finnshed_time,
                t.add_time,
                t.logistics_type,
                t.goods_id,
                t.goods_name,
                t.is_global,

               IF (
                t.voucher_type = 0,
                t.goods_price + t.manjian - t.voucher,
                t.goods_price + t.manjian
               ) goods_price,
                t.commis_rate,
                t.goods_num,
                t.goods_type,
                t.gc_id,
                t.refund_id,
                t.goods_storage,
                t.payment_time,
                t.goods_liquidate_price,
                t.goods_liquidate_amount,
               	t.dmember_mobile,
               t.dmember_name,
               t.goods_serial,
               t.order_amount
               FROM
                (
                 SELECT
                  a.order_sn,
                  IFNULL(
                   common.voucher_price / (a.goods_amount) * goods.goods_price,
                   0
                  ) AS voucher,
                  common.voucher_type,
                  a.order_amount,
                  IFNULL(
                   (
                    a.order_amount - a.goods_amount - a.shipping_fee
                   ) / (a.goods_amount) * goods.goods_price,
                   0
                  ) AS manjian, 
                  a.store_id,
                  s.store_name,
                  s.is_global,
                  FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
                  FROM_UNIXTIME(a.add_time) AS add_time,
                  a.logistics_type,
                  goods.goods_id,
                  goods.goods_name,
                  goods.goods_price,
                  goods.commis_rate,
                  goods.goods_num,
                  goods.goods_type,
                  goods.gc_id,
                  gs.goods_storage,
                  n.refund_id,
                  FROM_UNIXTIME(a.payment_time) payment_time,
                  goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
                  goods.goods_liquidate_amount,
               	 kili.dmember_name,
               		kili.dmember_mobile,
               		commons.goods_serial
                 FROM
                  nc_order a
                 LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
                 LEFT JOIN nc_order_common common ON common.order_id = a.order_id
                 LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
                 LEFT JOIN nc_store s ON s.store_id = a.store_id
                 LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
                 LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
                 LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
                 WHERE
                  a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')

               AND a.store_id IN (2706,1,
    2606,
    2189,
    829,
    2195,
    2475,
    2499,
    2476,
    2498,
    2905,
    3087,
    653,
    3036,
    3271,
    3272,
    2272,
    3406,
    3906,
    2757,
    4429)) t""" % (startweekday, endweekday)
    ziyingxiaoshou_week_shenzhen = """SELECT
                CONCAT(',',t.order_sn),
                t.voucher,
                t.voucher_type,
                t.order_amount,
                t.manjian,
                t.store_id,
                t.store_name,
                t.finnshed_time,
                t.add_time,
                t.logistics_type,
                t.goods_id,
                t.goods_name,
                t.is_global,

               IF (
                t.voucher_type = 0,
                t.goods_price + t.manjian - t.voucher,
                t.goods_price + t.manjian
               ) goods_price,
                t.commis_rate,
                t.goods_num,
                t.goods_type,
                t.gc_id,
                t.refund_id,
                t.goods_storage,
                t.payment_time,
                t.goods_liquidate_price,
                t.goods_liquidate_amount,
               	t.dmember_mobile,
               t.dmember_name,
               t.goods_serial,
               t.order_amount
               FROM
                (
                 SELECT
                  a.order_sn,
                  IFNULL(
                   common.voucher_price / (a.goods_amount) * goods.goods_price,
                   0
                  ) AS voucher,
                  common.voucher_type,
                  a.order_amount,
                  IFNULL(
                   (
                    a.order_amount - a.goods_amount - a.shipping_fee
                   ) / (a.goods_amount) * goods.goods_price,
                   0
                  ) AS manjian, 
                  a.store_id,
                  s.store_name,
                  s.is_global,
                  FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
                  FROM_UNIXTIME(a.add_time) AS add_time,
                  a.logistics_type,
                  goods.goods_id,
                  goods.goods_name,
                  goods.goods_price,
                  goods.commis_rate,
                  goods.goods_num,
                  goods.goods_type,
                  goods.gc_id,
                  gs.goods_storage,
                  n.refund_id,
                  FROM_UNIXTIME(a.payment_time) payment_time,
                  goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
                  goods.goods_liquidate_amount,
               	 kili.dmember_name,
               		kili.dmember_mobile,
               		commons.goods_serial
                 FROM
                  nc_order a
                 LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
                 LEFT JOIN nc_order_common common ON common.order_id = a.order_id
                 LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
                 LEFT JOIN nc_store s ON s.store_id = a.store_id
                 LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
                 LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
                 LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
                 WHERE
                  a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')

               AND a.store_id IN (2442,
    1888,
    2053,
    2137,
    3075,
    3076,
    3077,
    2118,
    3056,
    3407,
    3397,
    767,
    2977)) t""" % (startweekday, endweekday)
    ziyingxiaoshou_week_lucy = """SELECT
                CONCAT(',',t.order_sn),
                t.voucher,
                t.voucher_type,
                t.order_amount,
                t.manjian,
                t.store_id,
                t.store_name,
                t.finnshed_time,
                t.add_time,
                t.logistics_type,
                t.goods_id,
                t.goods_name,
                t.is_global,

               IF (
                t.voucher_type = 0,
                t.goods_price + t.manjian - t.voucher,
                t.goods_price + t.manjian
               ) goods_price,
                t.commis_rate,
                t.goods_num,
                t.goods_type,
                t.gc_id,
                t.refund_id,
                t.goods_storage,
                t.payment_time,
                t.goods_liquidate_price,
                t.goods_liquidate_amount,
               	t.dmember_mobile,
               t.dmember_name,
               t.goods_serial,
               t.order_amount
               FROM
                (
                 SELECT
                  a.order_sn,
                  IFNULL(
                   common.voucher_price / (a.goods_amount) * goods.goods_price,
                   0
                  ) AS voucher,
                  common.voucher_type,
                  a.order_amount,
                  IFNULL(
                   (
                    a.order_amount - a.goods_amount - a.shipping_fee
                   ) / (a.goods_amount) * goods.goods_price,
                   0
                  ) AS manjian, 
                  a.store_id,
                  s.store_name,
                  s.is_global,
                  FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
                  FROM_UNIXTIME(a.add_time) AS add_time,
                  a.logistics_type,
                  goods.goods_id,
                  goods.goods_name,
                  goods.goods_price,
                  goods.commis_rate,
                  goods.goods_num,
                  goods.goods_type,
                  goods.gc_id,
                  gs.goods_storage,
                  n.refund_id,
                  FROM_UNIXTIME(a.payment_time) payment_time,
                  goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
                  goods.goods_liquidate_amount,
               	 kili.dmember_name,
               		kili.dmember_mobile,
               		commons.goods_serial
                 FROM
                  nc_order a
                 LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
                 LEFT JOIN nc_order_common common ON common.order_id = a.order_id
                 LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
                 LEFT JOIN nc_store s ON s.store_id = a.store_id
                 LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
                 LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
                 LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
                 WHERE
                  a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')

               AND a.store_id IN (2877,
    2415,
    2526,
    2393,
    3482,
    3487,
    3729,
    3492,
    3601,
    3515,
    3571,
    3541,
    3578,
    2096,
    2819,
    2546,
    2547,
    3090,
    2482,
    2886,
    3250,
    3260,
    3256,
    3254,
    3242,
    3249,
    3246,
    3244,
    3259,
    3252,
    3408,
    3253,
    2622,
    2620,
    2619,
    2642,
    2618,
    2629,
    2655,
    2648,
    2632,
    2633,
    2649,
    2654,
    2646,
    2611,
    2613,
    2612,
    2621,
    2608,
    2631,
    2651,
    2616,
    2650,
    2615,
    2624,
    2638,
    2652,
    2645,
    2653,
    2625,
    2639,
    2635,
    2614,
    2640,
    2637,
    2626,
    2623,
    2636,
    2656,
    2647,
    2641,
    2643,
    2630,
    2644,
    2634,
    2627,
    3193,
    3188,
    3180,
    3178,
    3177,
    3179,
    3176,
    3174,
    3175,
    3173,
    3480,
    3481,
    3483,
    3484,
    3486,
    3488,
    3489,
    3491,
    3493,
    3494,
    3495,
    3496,
    3497,
    3498,
    3500,
    3501,
    3502,
    3503,
    3504,
    3505,
    3506,
    3508,
    3509,
    3510,
    3512,
    3513,
    3514,
    3516,
    3517,
    3518,
    3519,
    3520,
    3521,
    3522,
    3523,
    3524,
    3525,
    3526,
    3527,
    3528,
    3529,
    3530,
    3531,
    3532,
    3533,
    3534,
    3535,
    3536,
    3537,
    3538,
    3539,
    3540,
    3541,
    3542,
    3543,
    3544,
    3545,
    3546,
    3547,
    3548,
    3549,
    3550,
    3551,
    3552,
    3553,
    3555,
    3556,
    3558,
    3559,
    3560,
    3561,
    3562,
    3563,
    3564,
    3565,
    3566,
    3567,
    3568,
    3569,
    3570,
    3571,
    3572,
    3573,
    3574,
    3575,
    3576,
    3577,
    3579,
    3580,
    3581,
    3582,
    3583,
    3584,
    3585,
    3586,
    3587,
    3588,
    3589,
    3590,
    3591,
    3592,
    3593,
    3594,
    3595,
    3596,
    3597,
    3598,
    3599,
    3600,
    3602,
    3603,
    3604,
    3605,
    3606,
    3607,
    3608,
    3609,
    3610,
    3611,
    3612,
    3613,
    3614,
    3615,
    3616,
    3617,
    3618,
    3619,
    3620,
    3621,
    3622,
    3623,
    3624,
    3625,
    3626,
    3627,
    3628,
    3629,
    3630,
    3631,
    3632,
    3633,
    3634,
    3635,
    3636,
    3637,
    3638,
    3639,
    3640,
    3641,
    3642,
    3643,
    3644,
    3645,
    3646,
    3647,
    3648,
    3649,
    3650,
    3651,
    3652,
    3653,
    3654,
    3655,
    3656,
    3657,
    3658,
    3659,
    3660,
    3661,
    3662,
    3663,
    3664,
    3665,
    3666,
    3667,
    3668,
    3669,
    3670,
    3671,
    3672,
    3673,
    3674,
    3675,
    3676,
    3677,
    3678,
    3679,
    3680,
    3681,
    3682,
    3683,
    3684,
    3685,
    3686,
    3687,
    3688,
    3689,
    3690,
    3691,
    3692,
    3693,
    3694,
    3695,
    3696,
    3697,
    3698,
    3699,
    3700,
    3701,
    3702,
    3703,
    3704,
    3705,
    3706,
    3707,
    3708,
    3709,
    3710,
    3711,
    3712,
    3713,
    3714,
    3715,
    3716,
    3717,
    3718,
    3719,
    3720,
    3721,
    3722,
    3723,
    3724,
    3725,
    3726,
    3727,
    3728,
    3731,
    3732,
    3733,
    3734,
    3735,
    3736,
    3737,
    3738,
    3739,
    3740,
    3741,
    3742,
    3743,
    3744,
    3745,
    3746,
    3747,
    3748,
    3749,
    3750,
    3751,
    3752,
    3753,
    3754,
    3755,
    3756,
    3757
    )) t""" % (startweekday, endweekday)

    ziyingxiaoshou_month = """SELECT
         CONCAT(',',t.order_sn),
         t.voucher,
         t.voucher_type,
         t.order_amount,
         t.manjian,
         t.store_id,
         t.store_name,
         t.finnshed_time,
         t.add_time,
         t.logistics_type,
         t.goods_id,
         t.goods_name,
         t.is_global,

        IF (
         t.voucher_type = 0,
         t.goods_price + t.manjian - t.voucher,
         t.goods_price + t.manjian
        ) goods_price,
         t.commis_rate,
         t.goods_num,
         t.goods_type,
         t.gc_id,
         t.refund_id,
         t.goods_storage,
         t.payment_time,
         t.goods_liquidate_price,
         t.goods_liquidate_amount,
        	t.dmember_mobile,
        t.dmember_name,
        t.goods_serial,
        t.order_amount
        FROM
         (
          SELECT
           a.order_sn,
           IFNULL(
            common.voucher_price / (a.goods_amount) * goods.goods_price,
            0
           ) AS voucher,
           common.voucher_type,
           a.order_amount,
           IFNULL(
            (
             a.order_amount - a.goods_amount - a.shipping_fee
            ) / (a.goods_amount) * goods.goods_price,
            0
           ) AS manjian, 
           a.store_id,
           s.store_name,
           s.is_global,
           FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
           FROM_UNIXTIME(a.add_time) AS add_time,
           a.logistics_type,
           goods.goods_id,
           goods.goods_name,
           goods.goods_price,
           goods.commis_rate,
           goods.goods_num,
           goods.goods_type,
           goods.gc_id,
           gs.goods_storage,
           n.refund_id,
           FROM_UNIXTIME(a.payment_time) payment_time,
           goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
           goods.goods_liquidate_amount,
        	 kili.dmember_name,
        		kili.dmember_mobile,
        		commons.goods_serial
          FROM
           nc_order a
          LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
          LEFT JOIN nc_order_common common ON common.order_id = a.order_id
          LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
          LEFT JOIN nc_store s ON s.store_id = a.store_id
          LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
          LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
          LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
          WHERE
           a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')

        AND a.store_id IN (2706,
    2606,
    2189,
    829,
    2195,
    2475,
    2499,
    2476,
    2498,
    2905,
    3087,
    653,
    3036,
    3271,
    3272,
    2272,
    3406,
    3906,
    2757,
    4429,
    2518,
    1,
    2391,
    2977,
    3007,
    3248,
    3257,
    3243,
    3479,
    3972,
    3258,
    3251,
    2628,
    2610,
    2609,
    2607,
    2617,
    3192,
    3191,
    3187,
    3190,
    3186,
    3182,
    3189,
    3185,
    3181,
    3184,
    3255,
    3478,
    3485,
    3490,
    3499,
    3511,
    3554,
    3507,
    1312,
    3730,
    4436,
    2336,
    95,
    2877,
    2415,
    2526,
    2393,
    3482,
    3487,
    3729,
    3492,
    3601,
    3515,
    3571,
    3541,
    3578,
    2096,
    2819,
    2546,
    2547,
    3090,
    2482,
    2886,
    3250,
    3260,
    3256,
    3254,
    3242,
    3249,
    3246,
    3244,
    3259,
    3252,
    3408,
    3253,
    2622,
    2620,
    2619,
    2642,
    2618,
    2629,
    2655,
    2648,
    2632,
    2633,
    2649,
    2654,
    2646,
    2611,
    2613,
    2612,
    2621,
    2608,
    2631,
    2651,
    2616,
    2650,
    2615,
    2624,
    2638,
    2652,
    2645,
    2653,
    2625,
    2639,
    2635,
    2614,
    2640,
    2637,
    2626,
    2623,
    2636,
    2656,
    2647,
    2641,
    2643,
    2630,
    2644,
    2634,
    2627,
    3193,
    3188,
    3180,
    3178,
    3177,
    3179,
    3176,
    3174,
    3175,
    3173,
    3480,
    3481,
    3483,
    3484,
    3486,
    3488,
    3489,
    3491,
    3493,
    3494,
    3495,
    3496,
    3497,
    3498,
    3500,
    3501,
    3502,
    3503,
    3504,
    3505,
    3506,
    3508,
    3509,
    3510,
    3512,
    3513,
    3514,
    3516,
    3517,
    3518,
    3519,
    3520,
    3521,
    3522,
    3523,
    3524,
    3525,
    3526,
    3527,
    3528,
    3529,
    3530,
    3531,
    3532,
    3533,
    3534,
    3535,
    3536,
    3537,
    3538,
    3539,
    3540,
    3541,
    3542,
    3543,
    3544,
    3545,
    3546,
    3547,
    3548,
    3549,
    3550,
    3551,
    3552,
    3553,
    3555,
    3556,
    3558,
    3559,
    3560,
    3561,
    3562,
    3563,
    3564,
    3565,
    3566,
    3567,
    3568,
    3569,
    3570,
    3571,
    3572,
    3573,
    3574,
    3575,
    3576,
    3577,
    3579,
    3580,
    3581,
    3582,
    3583,
    3584,
    3585,
    3586,
    3587,
    3588,
    3589,
    3590,
    3591,
    3592,
    3593,
    3594,
    3595,
    3596,
    3597,
    3598,
    3599,
    3600,
    3602,
    3603,
    3604,
    3605,
    3606,
    3607,
    3608,
    3609,
    3610,
    3611,
    3612,
    3613,
    3614,
    3615,
    3616,
    3617,
    3618,
    3619,
    3620,
    3621,
    3622,
    3623,
    3624,
    3625,
    3626,
    3627,
    3628,
    3629,
    3630,
    3631,
    3632,
    3633,
    3634,
    3635,
    3636,
    3637,
    3638,
    3639,
    3640,
    3641,
    3642,
    3643,
    3644,
    3645,
    3646,
    3647,
    3648,
    3649,
    3650,
    3651,
    3652,
    3653,
    3654,
    3655,
    3656,
    3657,
    3658,
    3659,
    3660,
    3661,
    3662,
    3663,
    3664,
    3665,
    3666,
    3667,
    3668,
    3669,
    3670,
    3671,
    3672,
    3673,
    3674,
    3675,
    3676,
    3677,
    3678,
    3679,
    3680,
    3681,
    3682,
    3683,
    3684,
    3685,
    3686,
    3687,
    3688,
    3689,
    3690,
    3691,
    3692,
    3693,
    3694,
    3695,
    3696,
    3697,
    3698,
    3699,
    3700,
    3701,
    3702,
    3703,
    3704,
    3705,
    3706,
    3707,
    3708,
    3709,
    3710,
    3711,
    3712,
    3713,
    3714,
    3715,
    3716,
    3717,
    3718,
    3719,
    3720,
    3721,
    3722,
    3723,
    3724,
    3725,
    3726,
    3727,
    3728,
    3731,
    3732,
    3733,
    3734,
    3735,
    3736,
    3737,
    3738,
    3739,
    3740,
    3741,
    3742,
    3743,
    3744,
    3745,
    3746,
    3747,
    3748,
    3749,
    3750,
    3751,
    3752,
    3753,
    3754,
    3755,
    3756,
    3757,
    2442,
    1888,
    2053,
    2137,
    3075,
    3076,
    3077,
    2118,
    3056,
    3407,
    3397,
    767,
    2977))t""" % (stardmonthday, endmonthday)
    ziyingxiaoshou_month_cathy = """SELECT
             CONCAT(',',t.order_sn),
             t.voucher,
             t.voucher_type,
             t.order_amount,
             t.manjian,
             t.store_id,
             t.store_name,
             t.finnshed_time,
             t.add_time,
             t.logistics_type,
             t.goods_id,
             t.goods_name,
             t.is_global,

            IF (
             t.voucher_type = 0,
             t.goods_price + t.manjian - t.voucher,
             t.goods_price + t.manjian
            ) goods_price,
             t.commis_rate,
             t.goods_num,
             t.goods_type,
             t.gc_id,
             t.refund_id,
             t.goods_storage,
             t.payment_time,
             t.goods_liquidate_price,
             t.goods_liquidate_amount,
            	t.dmember_mobile,
            t.dmember_name,
            t.goods_serial,
            t.order_amount
            FROM
             (
              SELECT
               a.order_sn,
               IFNULL(
                common.voucher_price / (a.goods_amount) * goods.goods_price,
                0
               ) AS voucher,
               common.voucher_type,
               a.order_amount,
               IFNULL(
                (
                 a.order_amount - a.goods_amount - a.shipping_fee
                ) / (a.goods_amount) * goods.goods_price,
                0
               ) AS manjian, 
               a.store_id,
               s.store_name,
               s.is_global,
               FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
               FROM_UNIXTIME(a.add_time) AS add_time,
               a.logistics_type,
               goods.goods_id,
               goods.goods_name,
               goods.goods_price,
               goods.commis_rate,
               goods.goods_num,
               goods.goods_type,
               goods.gc_id,
               gs.goods_storage,
               n.refund_id,
               FROM_UNIXTIME(a.payment_time) payment_time,
               goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
               goods.goods_liquidate_amount,
            	 kili.dmember_name,
            		kili.dmember_mobile,
            		commons.goods_serial
              FROM
               nc_order a
              LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
              LEFT JOIN nc_order_common common ON common.order_id = a.order_id
              LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
              LEFT JOIN nc_store s ON s.store_id = a.store_id
              LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
              LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
              LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
              WHERE
               a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')

            AND a.store_id IN (2518,
    2391,
    2977,
    3007,
    3248,
    3257,
    3243,
    3479,
    3972,
    3258,
    3251,
    2628,
    2610,
    2609,
    2607,
    2617,
    3192,
    3191,
    3187,
    3190,
    3186,
    3182,
    3189,
    3185,
    3181,
    3184,
    3255,
    3478,
    3485,
    3490,
    3499,
    3511,
    3554,
    3507,
    1312,
    3730,
    4436,
    2336,
    95
    ))t""" % (stardmonthday, endmonthday)
    ziyingxiaoshou_month_garcia = """SELECT
                CONCAT(',',t.order_sn),
                t.voucher,
                t.voucher_type,
                t.order_amount,
                t.manjian,
                t.store_id,
                t.store_name,
                t.finnshed_time,
                t.add_time,
                t.logistics_type,
                t.goods_id,
                t.goods_name,
                t.is_global,

               IF (
                t.voucher_type = 0,
                t.goods_price + t.manjian - t.voucher,
                t.goods_price + t.manjian
               ) goods_price,
                t.commis_rate,
                t.goods_num,
                t.goods_type,
                t.gc_id,
                t.refund_id,
                t.goods_storage,
                t.payment_time,
                t.goods_liquidate_price,
                t.goods_liquidate_amount,
               	t.dmember_mobile,
               t.dmember_name,
               t.goods_serial,
               t.order_amount
               FROM
                (
                 SELECT
                  a.order_sn,
                  IFNULL(
                   common.voucher_price / (a.goods_amount) * goods.goods_price,
                   0
                  ) AS voucher,
                  common.voucher_type,
                  a.order_amount,
                  IFNULL(
                   (
                    a.order_amount - a.goods_amount - a.shipping_fee
                   ) / (a.goods_amount) * goods.goods_price,
                   0
                  ) AS manjian, 
                  a.store_id,
                  s.store_name,
                  s.is_global,
                  FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
                  FROM_UNIXTIME(a.add_time) AS add_time,
                  a.logistics_type,
                  goods.goods_id,
                  goods.goods_name,
                  goods.goods_price,
                  goods.commis_rate,
                  goods.goods_num,
                  goods.goods_type,
                  goods.gc_id,
                  gs.goods_storage,
                  n.refund_id,
                  FROM_UNIXTIME(a.payment_time) payment_time,
                  goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
                  goods.goods_liquidate_amount,
               	 kili.dmember_name,
               		kili.dmember_mobile,
               		commons.goods_serial
                 FROM
                  nc_order a
                 LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
                 LEFT JOIN nc_order_common common ON common.order_id = a.order_id
                 LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
                 LEFT JOIN nc_store s ON s.store_id = a.store_id
                 LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
                 LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
                 LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
                 WHERE
                  a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')

               AND a.store_id IN (2706,1,
    2606,
    2189,
    829,
    2195,
    2475,
    2499,
    2476,
    2498,
    2905,
    3087,
    653,
    3036,
    3271,
    3272,
    2272,
    3406,
    3906,
    2757,
    4429)) t""" % (stardmonthday, endmonthday)
    ziyingxiaoshou_month_shenzhen = """SELECT
                CONCAT(',',t.order_sn),
                t.voucher,
                t.voucher_type,
                t.order_amount,
                t.manjian,
                t.store_id,
                t.store_name,
                t.finnshed_time,
                t.add_time,
                t.logistics_type,
                t.goods_id,
                t.goods_name,
                t.is_global,

               IF (
                t.voucher_type = 0,
                t.goods_price + t.manjian - t.voucher,
                t.goods_price + t.manjian
               ) goods_price,
                t.commis_rate,
                t.goods_num,
                t.goods_type,
                t.gc_id,
                t.refund_id,
                t.goods_storage,
                t.payment_time,
                t.goods_liquidate_price,
                t.goods_liquidate_amount,
               	t.dmember_mobile,
               t.dmember_name,
               t.goods_serial,
               t.order_amount
               FROM
                (
                 SELECT
                  a.order_sn,
                  IFNULL(
                   common.voucher_price / (a.goods_amount) * goods.goods_price,
                   0
                  ) AS voucher,
                  common.voucher_type,
                  a.order_amount,
                  IFNULL(
                   (
                    a.order_amount - a.goods_amount - a.shipping_fee
                   ) / (a.goods_amount) * goods.goods_price,
                   0
                  ) AS manjian, 
                  a.store_id,
                  s.store_name,
                  s.is_global,
                  FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
                  FROM_UNIXTIME(a.add_time) AS add_time,
                  a.logistics_type,
                  goods.goods_id,
                  goods.goods_name,
                  goods.goods_price,
                  goods.commis_rate,
                  goods.goods_num,
                  goods.goods_type,
                  goods.gc_id,
                  gs.goods_storage,
                  n.refund_id,
                  FROM_UNIXTIME(a.payment_time) payment_time,
                  goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
                  goods.goods_liquidate_amount,
               	 kili.dmember_name,
               		kili.dmember_mobile,
               		commons.goods_serial
                 FROM
                  nc_order a
                 LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
                 LEFT JOIN nc_order_common common ON common.order_id = a.order_id
                 LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
                 LEFT JOIN nc_store s ON s.store_id = a.store_id
                 LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
                 LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
                 LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
                 WHERE
                  a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')

               AND a.store_id IN (2442,
    1888,
    2053,
    2137,
    3075,
    3076,
    3077,
    2118,
    3056,
    3407,
    3397,
    767,
    2977)) t""" % (stardmonthday, endmonthday)
    ziyingxiaoshou_month_lucy = """SELECT
                CONCAT(',',t.order_sn),
                t.voucher,
                t.voucher_type,
                t.order_amount,
                t.manjian,
                t.store_id,
                t.store_name,
                t.finnshed_time,
                t.add_time,
                t.logistics_type,
                t.goods_id,
                t.goods_name,
                t.is_global,

               IF (
                t.voucher_type = 0,
                t.goods_price + t.manjian - t.voucher,
                t.goods_price + t.manjian
               ) goods_price,
                t.commis_rate,
                t.goods_num,
                t.goods_type,
                t.gc_id,
                t.refund_id,
                t.goods_storage,
                t.payment_time,
                t.goods_liquidate_price,
                t.goods_liquidate_amount,
               	t.dmember_mobile,
               t.dmember_name,
               t.goods_serial,
               t.order_amount
               FROM
                (
                 SELECT
                  a.order_sn,
                  IFNULL(
                   common.voucher_price / (a.goods_amount) * goods.goods_price,
                   0
                  ) AS voucher,
                  common.voucher_type,
                  a.order_amount,
                  IFNULL(
                   (
                    a.order_amount - a.goods_amount - a.shipping_fee
                   ) / (a.goods_amount) * goods.goods_price,
                   0
                  ) AS manjian, 
                  a.store_id,
                  s.store_name,
                  s.is_global,
                  FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
                  FROM_UNIXTIME(a.add_time) AS add_time,
                  a.logistics_type,
                  goods.goods_id,
                  goods.goods_name,
                  goods.goods_price,
                  goods.commis_rate,
                  goods.goods_num,
                  goods.goods_type,
                  goods.gc_id,
                  gs.goods_storage,
                  n.refund_id,
                  FROM_UNIXTIME(a.payment_time) payment_time,
                  goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
                  goods.goods_liquidate_amount,
               	 kili.dmember_name,
               		kili.dmember_mobile,
               		commons.goods_serial
                 FROM
                  nc_order a
                 LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
                 LEFT JOIN nc_order_common common ON common.order_id = a.order_id
                 LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
                 LEFT JOIN nc_store s ON s.store_id = a.store_id
                 LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
                 LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
                 LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
                 WHERE
                  a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')

               AND a.store_id IN (2877,
    2415,
    2526,
    2393,
    3482,
    3487,
    3729,
    3492,
    3601,
    3515,
    3571,
    3541,
    3578,
    2096,
    2819,
    2546,
    2547,
    3090,
    2482,
    2886,
    3250,
    3260,
    3256,
    3254,
    3242,
    3249,
    3246,
    3244,
    3259,
    3252,
    3408,
    3253,
    2622,
    2620,
    2619,
    2642,
    2618,
    2629,
    2655,
    2648,
    2632,
    2633,
    2649,
    2654,
    2646,
    2611,
    2613,
    2612,
    2621,
    2608,
    2631,
    2651,
    2616,
    2650,
    2615,
    2624,
    2638,
    2652,
    2645,
    2653,
    2625,
    2639,
    2635,
    2614,
    2640,
    2637,
    2626,
    2623,
    2636,
    2656,
    2647,
    2641,
    2643,
    2630,
    2644,
    2634,
    2627,
    3193,
    3188,
    3180,
    3178,
    3177,
    3179,
    3176,
    3174,
    3175,
    3173,
    3480,
    3481,
    3483,
    3484,
    3486,
    3488,
    3489,
    3491,
    3493,
    3494,
    3495,
    3496,
    3497,
    3498,
    3500,
    3501,
    3502,
    3503,
    3504,
    3505,
    3506,
    3508,
    3509,
    3510,
    3512,
    3513,
    3514,
    3516,
    3517,
    3518,
    3519,
    3520,
    3521,
    3522,
    3523,
    3524,
    3525,
    3526,
    3527,
    3528,
    3529,
    3530,
    3531,
    3532,
    3533,
    3534,
    3535,
    3536,
    3537,
    3538,
    3539,
    3540,
    3541,
    3542,
    3543,
    3544,
    3545,
    3546,
    3547,
    3548,
    3549,
    3550,
    3551,
    3552,
    3553,
    3555,
    3556,
    3558,
    3559,
    3560,
    3561,
    3562,
    3563,
    3564,
    3565,
    3566,
    3567,
    3568,
    3569,
    3570,
    3571,
    3572,
    3573,
    3574,
    3575,
    3576,
    3577,
    3579,
    3580,
    3581,
    3582,
    3583,
    3584,
    3585,
    3586,
    3587,
    3588,
    3589,
    3590,
    3591,
    3592,
    3593,
    3594,
    3595,
    3596,
    3597,
    3598,
    3599,
    3600,
    3602,
    3603,
    3604,
    3605,
    3606,
    3607,
    3608,
    3609,
    3610,
    3611,
    3612,
    3613,
    3614,
    3615,
    3616,
    3617,
    3618,
    3619,
    3620,
    3621,
    3622,
    3623,
    3624,
    3625,
    3626,
    3627,
    3628,
    3629,
    3630,
    3631,
    3632,
    3633,
    3634,
    3635,
    3636,
    3637,
    3638,
    3639,
    3640,
    3641,
    3642,
    3643,
    3644,
    3645,
    3646,
    3647,
    3648,
    3649,
    3650,
    3651,
    3652,
    3653,
    3654,
    3655,
    3656,
    3657,
    3658,
    3659,
    3660,
    3661,
    3662,
    3663,
    3664,
    3665,
    3666,
    3667,
    3668,
    3669,
    3670,
    3671,
    3672,
    3673,
    3674,
    3675,
    3676,
    3677,
    3678,
    3679,
    3680,
    3681,
    3682,
    3683,
    3684,
    3685,
    3686,
    3687,
    3688,
    3689,
    3690,
    3691,
    3692,
    3693,
    3694,
    3695,
    3696,
    3697,
    3698,
    3699,
    3700,
    3701,
    3702,
    3703,
    3704,
    3705,
    3706,
    3707,
    3708,
    3709,
    3710,
    3711,
    3712,
    3713,
    3714,
    3715,
    3716,
    3717,
    3718,
    3719,
    3720,
    3721,
    3722,
    3723,
    3724,
    3725,
    3726,
    3727,
    3728,
    3731,
    3732,
    3733,
    3734,
    3735,
    3736,
    3737,
    3738,
    3739,
    3740,
    3741,
    3742,
    3743,
    3744,
    3745,
    3746,
    3747,
    3748,
    3749,
    3750,
    3751,
    3752,
    3753,
    3754,
    3755,
    3756,
    3757
    )) t""" % (stardmonthday, endmonthday)

    ziyingxiaoshou_month_mable = """SELECT
 CONCAT(',',t.order_sn),
 t.voucher,
 t.voucher_type,
 t.order_amount,
 t.manjian,
 t.store_id,
 t.store_name,
 t.finnshed_time,
 t.add_time,
 t.logistics_type,
 t.goods_id,
 t.goods_name,
 t.is_global,

IF (
 t.voucher_type = 0,
 t.goods_price + t.manjian - t.voucher,
 t.goods_price + t.manjian
) goods_price,
 t.commis_rate,
 t.goods_num,
 t.goods_type,
 t.gc_id,
 t.refund_id,
 t.goods_storage,
 t.payment_time,
 t.goods_liquidate_price,
 t.goods_liquidate_amount,
	t.dmember_mobile,
t.dmember_name,
t.goods_serial
FROM
 (
  SELECT
   a.order_sn,
   IFNULL(
    common.voucher_price / (a.goods_amount) * goods.goods_price,
    0
   ) AS voucher,
   common.voucher_type,
   a.order_amount,
   IFNULL(
    (
     a.order_amount - a.goods_amount - a.shipping_fee
    ) / (a.goods_amount) * goods.goods_price,
    0
   ) AS manjian, 
   a.store_id,
   s.store_name,
   s.is_global,
   FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
   FROM_UNIXTIME(a.add_time) AS add_time,
   a.logistics_type,
   goods.goods_id,
   goods.goods_name,
   goods.goods_price,
   goods.commis_rate,
   goods.goods_num,
   goods.goods_type,
   goods.gc_id,
   gs.goods_storage,
   n.refund_id,
   FROM_UNIXTIME(a.payment_time) payment_time,
   goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
   goods.goods_liquidate_amount,
	 kili.dmember_name,
		kili.dmember_mobile,
		commons.goods_serial
  FROM
   nc_order a
  LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
  LEFT JOIN nc_order_common common ON common.order_id = a.order_id
  LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
  LEFT JOIN nc_store s ON s.store_id = a.store_id
  LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
  LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
  LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
  WHERE
   #FROM_UNIXTIME(a.add_time, '%%Y%%m%%d')

   a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')
   # NET GMV
   # a.payment_time BETWEEN UNIX_TIMESTAMP('2018-12-01 00:00:00') AND UNIX_TIMESTAMP('2018-12-31 23:59:59')
   AND a.order_state > 0

AND a.store_id IN (2415,2757,2526,2393,2877,2096,2518,1,2499,2189,2606,2706,2476,2475,2819,2905,829,2977,3007,2391,3087,3090,2610,2622,2620,2609,2619,2617,2642,2618,2629,2655,2648,2632,2633,2649,2654,2646,2611,2628,2613,2612,2621,2608,2631,2651,2616,2650,2615,2624,2638,2652,2645,2607,2653,2625,2639,2635,2614,2640,2637,2626,2623,2636,2656,2647,2641,2643,2630,2644,2634,2627,3192,3191,3187,3190,3186,3182,3189,3185,3181,3184,3193,3188,3180,3178,3177,3179,3176,3174,3175,3173,2195,2336,2498,2118,2482,2251,3090,3087,653,3152,3036,3272,3406,3397,3271,3407,2140,3250,3260,3256,3254,3242,3249,3246,3244,3259,2886,3248,3257,3243,3729,3730,3906,3478,3479,3480,3481,3482,3483,3484,3485,3486,3487,3488,3489,3490,3491,3492,3493,3494,3495,3496,3497,3498,3499,3500,3501,3502,3503,3504,3505,3506,3507,3508,3509,3510,3511,3512,3513,3514,3515,3516,3517,3518,3519,3520,3521,3522,3523,3524,3525,3526,3527,3528,3529,3530,3531,3532,3533,3534,3535,3536,3537,3538,3539,3540,3541,3542,3543,3544,3545,3546,3547,3548,3549,3550,3551,3552,3553,3554,3555,3556,3558,3559,3560,3561,3562,3563,3564,3565,3566,3567,3568,3569,3570,3571,3572,3573,3574,3575,3576,3577,3578,3579,3580,3581,3582,3583,3584,3585,3586,3587,3588,3589,3590,3591,3592,3593,3594,3595,3596,3597,3598,3599,3600,3601,3602,3603,3604,3605,3606,3607,3608,3609,3610,3611,3612,3613,3614,3615,3616,3617,3618,3619,3620,3621,3622,3623,3624,3625,3626,3627,3628,3629,3630,3631,3632,3633,3634,3635,3636,3637,3638,3639,3640,3641,3642,3643,3644,3645,3646,3647,3648,3649,3650,3651,3652,3653,3654,3655,3656,3657,3658,3659,3660,3661,3662,3663,3664,3665,3666,3667,3668,3669,3670,3671,3672,3673,3674,3675,3676,3677,3678,3679,3680,3681,3682,3683,3684,3685,3686,3687,3688,3689,3690,3691,3692,3693,3694,3695,3696,3697,3698,3699,3700,3701,3702,3703,3704,3705,3706,3707,3708,3709,3710,3711,3712,3713,3714,3715,3716,3717,3718,3719,3720,3721,3722,3723,3724,3725,3726,3727,3728,3729,3730,3731,3732,3733,3734,3735,3736,3737,3738,3739,3740,3741,3742,3743,3744,3745,3746,3747,3748,3749,3750,3751,3752,3753,3754,3755,3756,3757,2877,2393
,3252
,3408
,3253
,2620
,2642
,2618
,2655
,2648
,2632
,2633
,2649
,2654
,2646
,2613
,2608
,2616
,2615
,2624
,2645
,2625
,2639
,2637
,2636
,2656
,2647
,2641
,2630
,2644
,2634
,3188
,3180
,3173
,3732
,3739
,3746
,3741
,3748
,3258
,2628
,2607
,3192
,3191
,3255
,3251
,3972
,2475
,2499
,2518
,2819
,3056
,1888
,1312
,2053
,2137
,2546
,2547
,3075
,3077
,3076
)
 ) t""" % (stardmonthday, endmonthday)
    ziyingxiaoshou_week_mable = """SELECT
 CONCAT(',',t.order_sn),
 t.voucher,
 t.voucher_type,
 t.order_amount,
 t.manjian,
 t.store_id,
 t.store_name,
 t.finnshed_time,
 t.add_time,
 t.logistics_type,
 t.goods_id,
 t.goods_name,
 t.is_global,

IF (
 t.voucher_type = 0,
 t.goods_price + t.manjian - t.voucher,
 t.goods_price + t.manjian
) goods_price,
 t.commis_rate,
 t.goods_num,
 t.goods_type,
 t.gc_id,
 t.refund_id,
 t.goods_storage,
 t.payment_time,
 t.goods_liquidate_price,
 t.goods_liquidate_amount,
	t.dmember_mobile,
t.dmember_name,
t.goods_serial
FROM
 (
  SELECT
   a.order_sn,
   IFNULL(
    common.voucher_price / (a.goods_amount) * goods.goods_price,
    0
   ) AS voucher,
   common.voucher_type,
   a.order_amount,
   IFNULL(
    (
     a.order_amount - a.goods_amount - a.shipping_fee
    ) / (a.goods_amount) * goods.goods_price,
    0
   ) AS manjian, 
   a.store_id,
   s.store_name,
   s.is_global,
   FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
   FROM_UNIXTIME(a.add_time) AS add_time,
   a.logistics_type,
   goods.goods_id,
   goods.goods_name,
   goods.goods_price,
   goods.commis_rate,
   goods.goods_num,
   goods.goods_type,
   goods.gc_id,
   gs.goods_storage,
   n.refund_id,
   FROM_UNIXTIME(a.payment_time) payment_time,
   goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
   goods.goods_liquidate_amount,
	 kili.dmember_name,
		kili.dmember_mobile,
		commons.goods_serial
  FROM
   nc_order a
  LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
  LEFT JOIN nc_order_common common ON common.order_id = a.order_id
  LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
  LEFT JOIN nc_store s ON s.store_id = a.store_id
  LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
  LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
  LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
  WHERE
   #FROM_UNIXTIME(a.add_time, '%%Y%%m%%d')

   a.add_time BETWEEN UNIX_TIMESTAMP('%s 00:00:00') AND UNIX_TIMESTAMP('%s 23:59:59')
   # NET GMV
   # a.payment_time BETWEEN UNIX_TIMESTAMP('2018-12-01 00:00:00') AND UNIX_TIMESTAMP('2018-12-31 23:59:59')
   AND a.order_state > 0

AND a.store_id IN (2415,2757,2526,2393,2877,2096,2518,1,2499,2189,2606,2706,2476,2475,2819,2905,829,2977,3007,2391,3087,3090,2610,2622,2620,2609,2619,2617,2642,2618,2629,2655,2648,2632,2633,2649,2654,2646,2611,2628,2613,2612,2621,2608,2631,2651,2616,2650,2615,2624,2638,2652,2645,2607,2653,2625,2639,2635,2614,2640,2637,2626,2623,2636,2656,2647,2641,2643,2630,2644,2634,2627,3192,3191,3187,3190,3186,3182,3189,3185,3181,3184,3193,3188,3180,3178,3177,3179,3176,3174,3175,3173,2195,2336,2498,2118,2482,2251,3090,3087,653,3152,3036,3272,3406,3397,3271,3407,2140,3250,3260,3256,3254,3242,3249,3246,3244,3259,2886,3248,3257,3243,3729,3730,3906,3478,3479,3480,3481,3482,3483,3484,3485,3486,3487,3488,3489,3490,3491,3492,3493,3494,3495,3496,3497,3498,3499,3500,3501,3502,3503,3504,3505,3506,3507,3508,3509,3510,3511,3512,3513,3514,3515,3516,3517,3518,3519,3520,3521,3522,3523,3524,3525,3526,3527,3528,3529,3530,3531,3532,3533,3534,3535,3536,3537,3538,3539,3540,3541,3542,3543,3544,3545,3546,3547,3548,3549,3550,3551,3552,3553,3554,3555,3556,3558,3559,3560,3561,3562,3563,3564,3565,3566,3567,3568,3569,3570,3571,3572,3573,3574,3575,3576,3577,3578,3579,3580,3581,3582,3583,3584,3585,3586,3587,3588,3589,3590,3591,3592,3593,3594,3595,3596,3597,3598,3599,3600,3601,3602,3603,3604,3605,3606,3607,3608,3609,3610,3611,3612,3613,3614,3615,3616,3617,3618,3619,3620,3621,3622,3623,3624,3625,3626,3627,3628,3629,3630,3631,3632,3633,3634,3635,3636,3637,3638,3639,3640,3641,3642,3643,3644,3645,3646,3647,3648,3649,3650,3651,3652,3653,3654,3655,3656,3657,3658,3659,3660,3661,3662,3663,3664,3665,3666,3667,3668,3669,3670,3671,3672,3673,3674,3675,3676,3677,3678,3679,3680,3681,3682,3683,3684,3685,3686,3687,3688,3689,3690,3691,3692,3693,3694,3695,3696,3697,3698,3699,3700,3701,3702,3703,3704,3705,3706,3707,3708,3709,3710,3711,3712,3713,3714,3715,3716,3717,3718,3719,3720,3721,3722,3723,3724,3725,3726,3727,3728,3729,3730,3731,3732,3733,3734,3735,3736,3737,3738,3739,3740,3741,3742,3743,3744,3745,3746,3747,3748,3749,3750,3751,3752,3753,3754,3755,3756,3757,2877,2393
,3252
,3408
,3253
,2620
,2642
,2618
,2655
,2648
,2632
,2633
,2649
,2654
,2646
,2613
,2608
,2616
,2615
,2624
,2645
,2625
,2639
,2637
,2636
,2656
,2647
,2641
,2630
,2644
,2634
,3188
,3180
,3173
,3732
,3739
,3746
,3741
,3748
,3258
,2628
,2607
,3192
,3191
,3255
,3251
,3972
,2475
,2499
,2518
,2819
,3056
,1888
,1312
,2053
,2137
,2546
,2547
,3075
,3077
,3076
)
 ) t""" % (startweekday, endweekday)

    netgmv_month = """SELECT
 CONCAT(',',t.order_sn),
 t.voucher,
 t.voucher_type,
 t.order_amount,
 t.manjian,
 t.store_id,
 t.store_name,
 t.finnshed_time,
 t.add_time,
 t.logistics_type,
 t.goods_id,
 t.goods_name,
 t.is_global,

IF (
 t.voucher_type = 0,
 t.goods_price + t.manjian - t.voucher,
 t.goods_price + t.manjian
) goods_price,
 t.commis_rate,
 t.goods_num,
 t.goods_type,
 t.gc_id,
 t.refund_id,
 t.goods_storage,
 t.payment_time,
 t.goods_liquidate_price,
 t.goods_liquidate_amount,
	t.dmember_mobile,
t.dmember_name,
t.goods_serial
FROM
 (
  SELECT
   a.order_sn,
   IFNULL(
    common.voucher_price / (a.goods_amount) * goods.goods_price,
    0
   ) AS voucher,
   common.voucher_type,
   a.order_amount,
   IFNULL(
    (
     a.order_amount - a.goods_amount - a.shipping_fee
    ) / (a.goods_amount) * goods.goods_price,
    0
   ) AS manjian, 
   a.store_id,
   s.store_name,
   s.is_global,
   FROM_UNIXTIME(a.finnshed_time) AS finnshed_time,
   FROM_UNIXTIME(a.add_time) AS add_time,
   a.logistics_type,
   goods.goods_id,
   goods.goods_name,
   goods.goods_price,
   goods.commis_rate,
   goods.goods_num,
   goods.goods_type,
   goods.gc_id,
   gs.goods_storage,
   n.refund_id,
   FROM_UNIXTIME(a.payment_time) payment_time,
   goods.goods_liquidate_amount / goods_num AS goods_liquidate_price,
   goods.goods_liquidate_amount,
	 kili.dmember_name,
		kili.dmember_mobile,
		commons.goods_serial
  FROM
   nc_order a
  LEFT JOIN nc_order_goods goods ON goods.order_id = a.order_id 
  LEFT JOIN nc_order_common common ON common.order_id = a.order_id
  LEFT JOIN nc_refund_return_new n ON n.order_id = a.order_id
  LEFT JOIN nc_store s ON s.store_id = a.store_id
  LEFT JOIN nc_delivery_kilimall kili ON a.order_id=kili.order_id
  LEFT JOIN nc_goods gs ON gs.goods_id=goods.goods_id
  LEFT JOIN nc_goods_common commons ON gs.goods_commonid=commons.goods_commonid
  WHERE
    a.payment_time >= UNIX_TIMESTAMP('%s 00:00:00')
  AND a.payment_time <= UNIX_TIMESTAMP('%s 23:59:59')   
 ) t;""" % (stardmonthday, endmonthday)

    fbkstock = """SELECT
gs.goods_commonid AS 'Listing ID',
gs.goods_id AS 'Goods ID',
gs.goods_name AS 'Goods Name',
gs.store_id AS 'Store ID',
gs.store_name AS 'Store Name',
gs.goods_storage AS 'Stock',
CASE store.is_global WHEN 1 THEN 'International Shop'
WHEN 0 THEN 'Local Shop' END AS 'SellerAttributes',
gc.gc_name AS 'L1',
gc1.gc_name AS 'L2',
gc2.gc_name AS 'L3',
gs.goods_price AS 'goodsprice',
CASE gs.goods_logistics_type WHEN 1 THEN 'FBK'
WHEN 2 THEN 'GS'
WHEN 0 THEN 'DS'
END AS 'typeee',
grade.sg_name AS 'level'
FROM nc_goods gs
INNER JOIN nc_goods_common common ON gs.goods_commonid=common.goods_commonid
INNER JOIN nc_goods_class gc ON gs.gc_id_1=gc.gc_id
INNER JOIN nc_goods_class gc1 ON gs.gc_id_2=gc1.gc_id
INNER JOIN nc_goods_class gc2 ON gs.gc_id=gc2.gc_id
INNER JOIN nc_store store ON gs.store_id=store.store_id
LEFT JOIN nc_store_grade grade ON grade.sg_id=store.grade_id
WHERE gs.goods_logistics_type=1
AND gs.goods_state=1
AND gs.goods_storage>0"""
    storeshop = """SELECT
store.store_id,
store.store_name,
CASE store.is_global WHEN 1 THEN 'International shop'
ELSE 'Local shop' END AS 'Seller Model',
joinn.company_name,
FROM_UNIXTIME(store.store_time),
CASE store.store_state WHEN 1 THEN '开启'
ELSE '关闭' END AS storestate,
codeuse.`code`
FROM nc_store store
LEFT JOIN nc_invite_code_use codeuse ON store.member_id=codeuse.seller_member_id
LEFT JOIN nc_store_joinin joinn ON store.member_id=joinn.member_id"""

    local_shop_stock = """SELECT
gs.goods_commonid AS 'Listing ID',
gs.goods_id AS 'Goods ID',
gs.goods_name AS 'Goods Name',
gs.store_id AS 'Store ID',
gs.store_name AS 'Store Name',
gs.goods_storage AS 'Stock',
CASE store.is_global WHEN 1 THEN 'International Shop'
WHEN 0 THEN 'Local Shop' END AS 'SellerAttributes',
gc.gc_name AS 'L1',
gc1.gc_name AS 'L2',
gc2.gc_name AS 'L3',
gs.goods_price AS 'goodsprice',
CASE gs.goods_logistics_type WHEN 1 THEN 'FBK'
WHEN 2 THEN 'GS'
WHEN 0 THEN 'DS'
END AS 'typeee',
FROM_UNIXTIME(o.payment_time, '%Y-%m-%d %H:%i') AS 'Last Payment Time'
FROM nc_goods gs
INNER JOIN nc_goods_common common ON gs.goods_commonid=common.goods_commonid
INNER JOIN nc_goods_class gc ON gs.gc_id_1=gc.gc_id
INNER JOIN nc_goods_class gc1 ON gs.gc_id_2=gc1.gc_id
INNER JOIN nc_goods_class gc2 ON gs.gc_id=gc2.gc_id
INNER JOIN nc_store store ON gs.store_id=store.store_id
LEFT JOIN nc_order_goods og ON og.goods_id = gs.goods_id
LEFT JOIN nc_order o ON o.order_id = og.order_id AND o.payment_time > 0 AND o.order_state != 0
WHERE store.is_global = 0
AND gs.goods_state=1"""

    tuikuaichengong_month = """SELECT r.id,CONCAT(',', o.order_sn),s.store_id,s.store_name,r.refund_amount,
FROM_UNIXTIME(r.created_at, '%%Y%%-%%m%%-%%d%% %%H%%:%%i') refund_create,FROM_UNIXTIME(r.updated_at, '%%Y%%-%%m%%-%%d%% %%H%%:%%i') refund_date
FROM nc_refund r
LEFT JOIN nc_order o ON o.order_id = r.order_id
LEFT JOIN nc_order_goods og ON og.order_id = r.order_id
LEFT JOIN nc_store s ON s.store_id = og.store_id
WHERE r.refund_state = 1 
AND r.updated_at >= UNIX_TIMESTAMP('%s 00:00:00') AND r.updated_at <= UNIX_TIMESTAMP('%s 23:59:59')
GROUP BY s.store_id 
ORDER BY r.id ASC;""" % (stardmonthday, endmonthday)
    # 按照任务区分不同收件人列表
    sendmaildict = {
        "day": [

            "damon.guo@kilimall.com",

        ],
        "local_shop_stock": [

            "damon.guo@kilimall.com",


        ],
        "week": [
            "damon.guo@kilimall.com",

        ],
        "month": [
            "damon.guo@kilimall.com",

        ],
        "other": [

            'damon.guo@kilimall.com',
        ],

        "ziying_day": [

            "damon.guo@kilimall.com",

        ],
        "ziying_week": [

            "damon.guo@kilimall.com",

        ],
        "ziying_month": [

            "damon.guo@kilimall.com",

        ],

        "ziyingxiaoshou_month_mable": [

            "damon.guo@kilimall.com",
        ],
        "ziyingxiaoshou_week_mable": [

            "damon.guo@kilimall.com",
        ],
        "netgmv_month": [
            "damon.guo@kilimall.com",

        ]

    }

    # 执行脚本 执行数据库 执行类型定义
    prodict = {
        "day": {
            "xiaoliang_day": {
                xiaoliang_day: [
                    "kilimall_kenya",
                ]
            },
            "fbkstock": {
                fbkstock: [
                    "kilimall_kenya",
                ]
            }

        },
        "local_shop_stock": {
            "local_shop_stock": {
                local_shop_stock: [
                    "kilimall_kenya",
                ]
            },
        },
        "other": {
            "xiaoliang_week":
                {
                    xiaoliang_week: [
                        "kilimall_kenya"
                    ]
                },
        },
        "ziying_day":
            {
                "ziyingxiaoshou_day": {
                    ziyingxiaoshou_day: ["kilimall_kenya",
                                         ]
                },
                "ziyingxiaoshou_day_garcia": {
                    ziyingxiaoshou_day_garcia: ["kilimall_kenya",
                                                ]
                },
                "ziyingxiaoshou_day_lucy": {
                    ziyingxiaoshou_day_lucy: ["kilimall_kenya",
                                              ]
                },
                "ziyingxiaoshou_day_shenzhen": {
                    ziyingxiaoshou_day_shenzhen: ["kilimall_kenya",
                                                  ]
                },
                "ziyingxiaoshou_day_cathy": {
                    ziyingxiaoshou_day_cathy: ["kilimall_kenya",
                                               ]
                },

            },

        "ziying_week":
            {
                "ziyingxiaoshou_week": {
                    ziyingxiaoshou_week: ["kilimall_kenya",
                                          ]
                },
                "ziyingxiaoshou_week_garcia": {
                    ziyingxiaoshou_week_garcia: ["kilimall_kenya",
                                                 ]
                },
                "ziyingxiaoshou_week_lucy": {
                    ziyingxiaoshou_week_lucy: ["kilimall_kenya",
                                               ]
                },
                "ziyingxiaoshou_week_shenzhen": {
                    ziyingxiaoshou_week_shenzhen: ["kilimall_kenya",
                                                   ]
                },
                "ziyingxiaoshou_week_cathy": {
                    ziyingxiaoshou_week_cathy: ["kilimall_kenya",
                                                ]
                }

            },

        "ziying_month":
            {
                "ziyingxiaoshou_month": {
                    ziyingxiaoshou_month: ["kilimall_kenya",
                                           # "kilimall_nigeria",
                                           # "kilimall_uganda",
                                           ]
                },
                "ziyingxiaoshou_month_garcia": {
                    ziyingxiaoshou_month_garcia: ["kilimall_kenya",
                                                  # "kilimall_nigeria",
                                                  # "kilimall_uganda",
                                                  ]
                },
                "ziyingxiaoshou_month_lucy": {
                    ziyingxiaoshou_month_lucy: ["kilimall_kenya",
                                                # "kilimall_nigeria",
                                                # "kilimall_uganda",
                                                ]
                },
                "ziyingxiaoshou_month_shenzhen": {
                    ziyingxiaoshou_month_shenzhen: ["kilimall_kenya",
                                                    # "kilimall_nigeria",
                                                    # "kilimall_uganda",
                                                    ]
                },
                "ziyingxiaoshou_month_cathy": {
                    ziyingxiaoshou_month_cathy: ["kilimall_kenya",
                                                 # "kilimall_nigeria",
                                                 # "kilimall_uganda",
                                                 ]
                },

            },

        "ziyingxiaoshou_month_mable":
            {
                "ziyingxiaoshou_month_mable": {
                    ziyingxiaoshou_month_mable: [
                        "kilimall_kenya",
                        # "kilimall_nigeria",
                        # "kilimall_uganda",
                    ]
                }
            },
        "ziyingxiaoshou_week_mable":
            {
                "ziyingxiaoshou_week_mable": {
                    ziyingxiaoshou_week_mable: [
                        "kilimall_kenya",
                        # "kilimall_nigeria",
                        # "kilimall_uganda",
                    ]
                }
            },

        "netgmv_month":
            {
                "netgmv_month": {
                    netgmv_month: [
                        "kilimall_kenya",
                        # "kilimall_nigeria",
                        # "kilimall_uganda",
                    ]
                }
            },
        "week": {
            "dingdanwangcheng_week":
                {
                    dingdanwangcheng_week: ["kilimall_kenya"],

                },
            "xiaoliang_week":
                {
                    xiaoliang_week: ["kilimall_kenya"]
                },

            "tuihuanhuo_week":
                {
                    tuihuanhuo_week:
                        [
                            "kilimall_kenya",
                        ]
                },
            "fajing_week":
                {
                    fajing_week:
                        [
                            "kilimall_kenya",
                        ]
                },
        },

        "month": {
            "dingdanwangcheng_month":
                {
                    dingdanwangcheng_month:
                        [
                            "kilimall_kenya",
                            "kilimall_nigeria",
                            "kilimall_uganda"
                        ]
                },
            "tuihuanhuo_month":
                {
                    tuihuanhuo_month:
                        [
                            "kilimall_kenya",
                            "kilimall_nigeria",
                            "kilimall_uganda"]
                },
            "fajing_month":
                {
                    fajing_month:
                        [
                            "kilimall_kenya",
                            "kilimall_nigeria",
                            "kilimall_uganda"]
                },
            "store_month": {
                storeshop: [
                    "kilimall_kenya",
                    "kilimall_nigeria",
                    "kilimall_uganda",
                ]
            },
            "xiaoliang_month":
                {
                    xiaoliang_month: ["kilimall_kenya",
                                      "kilimall_nigeria",
                                      "kilimall_uganda",
                                      ]
                },
            "tuikuaichengong_month":
                {
                    tuikuaichengong_month: [
                        "kilimall_kenya"
                    ]
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
            # print sql
            # sys.exit()
            for dbname in dbnamelist:
                print "exec sql name:%s " % sqlname
                print "exec database:%s" % dbname
                # filname = os.path.join(path, "%s-%s-%s.csv") % (today, dbname, sqlname)
                # 格式 也xlsx结尾 如果数据超过65535 将报错

                dirname = os.path.join(path, jobtype)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

                filname = os.path.join(dirname, "%s-%s-%s.xlsx") % (today, dbname, sqlname)
                sub_main(dbname, filname, sql)
                filnamelist.append(filname)
                print "export filename:%s" % filname
    # 邮件发送
    # print filnamelist
    # sendMail(filnamelist,["damon.guo@kilimall.com"])
    sendMail(filnamelist, sendmaildict[jobtype])


if __name__ == "__main__":
    # print listdir("/root/caiwu1")
    receiverlist = ["damon.guo@kilimall.com", ]
    # 导出的文件路径
    # path = "D:\kilimall_report\caiwu"
    path = "/data/auto_export_report/caiwu"
    # jobtype = "week"
    # jobtype = "month"
    # path = "/root/caiwu"

    try:
        jobtype = sys.argv[1]
    except:
        print "follow a ago [day,week ,month]"
        sys.exit()
    main(path, jobtype)
    sys.exit()
