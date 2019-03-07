#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
# sys.path.append("D:\Python27\Lib\site-packages")
import pandas as pd
# import xlrd
# import openpyxl
import os

# 以指定列名的值拆分Excel 以拆分列名的值输出Excel

def readExcel(File,sheetName):
    if not os.path.exists(File):
        print "%s is not exitis" % File
        sys.exit(1)
    read_temple = pd.ExcelFile(File, dtype=str)
    read_temple_sheet = read_temple.parse(sheetName.decode("utf-8"),dtype=str)
    return read_temple_sheet


# 一次性把execlsheet 都读取 返回一个字典
def readExcelSUB(File):
    if not os.path.exists(File):
        print "%s is not exitis" % File
        sys.exit(1)
    print "读取总账单数据 %s" % File
    read_temple = pd.ExcelFile(File, dtype=str)
    # read_temple = pd.ExcelFile(File, dtype=str, low_memory=False)
    sheets = read_temple.sheet_names

    sheetobjectDict = {}
    # sys.exit()
    for sheet in sheets:
        read_temple_sheet = read_temple.parse(sheet.decode("utf-8"))
        # if sheet == "账单明细".decode("utf-8"):
        #     read_temple_sheet['订单号'.decode("utf-8")] = read_temple_sheet['订单号'.decode("utf-8")].astype('str')
        sheetobjectDict[sheet] = read_temple_sheet
        # print read_temple_sheet
    print "读取完成，下一步拆分"
    return sheets, sheetobjectDict

# 拆分execl 已公司名称拆分
def writeExcel(sheetobjectDict,dstpath,sheetName,company_name):
    # 过滤条件
    filter_li = '公司名称'.decode("utf-8")

    path = os.path.join(dstpath, "%s_%s.xlsx".decode("utf-8")) % (souerFilename, company_name)

    writer = pd.ExcelWriter(path)

    for sheet in sheetName:
        read_temple_sheet = sheetobjectDict[sheet]
        try:
            # 过滤条件
            read_temple_sheet_filter = read_temple_sheet[read_temple_sheet[filter_li] == company_name]
        except KeyError, e:
            # print type(e)
            print e
            print "过滤列名:%s， 错误" % filter_li
            # print " 列名错误 err"
            sys.exit(1)
        read_temple_sheet_filter.to_excel(writer, sheet.decode("utf-8"), index=False)
    writer.save()


def getCompanyName(sheetobjectDict):
    # 获取总账单中的公司名 去重 返回公司列表
    company = sheetobjectDict["总账单".decode("utf-8")]["公司名称".decode("utf-8")]
    companylist = []
    for r in company:
        companylist.append(r)
    company_unique = list(set(companylist))

    return company_unique

def main(file,dstpath):
    # 读取execl 整个文件所有的sheet

    sheetlist,sheetobjectDict = readExcelSUB(file)

    CompanyList = getCompanyName(sheetobjectDict)
    # print "公司数量：%s" % len(CompanyList)
    for Company in CompanyList:
        print "开始拆分：%s 账单" % Company
        # print "拆分进度 %s"
        writeExcel(sheetobjectDict,dstpath,sheetlist, Company)
    print "拆分完成,输出目录：%s " % dstpath
    print "拆分公司账单数量：%s" % len(CompanyList)

if __name__ == "__main__":
    # 源文件 主要 要保证总账单清理多余的行 公司名称列与其他表格名称一直，
    # file = "D:/kilimall_report/break_report/2019年2月ke账单拆分.xlsx".decode("utf-8")
    file = "D:/kilimall_report/break_report/2019年2月乌干达账单拆分2.xlsx".decode("utf-8")

    # 把原文件名字取出来，作为目标目录名
    souerFilename = file.split("/")[-1].split(".")[0]
    print souerFilename
    # sys.exit()
    # 输出路径
    dir ="D:/kilimall_report/break_report/"

    dstpath = os.path.join(dir, souerFilename)

    if not os.path.exists(dstpath):
        os.makedirs(dstpath)
    main(file, dstpath)
