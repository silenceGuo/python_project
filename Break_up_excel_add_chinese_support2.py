#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("D:\Python27\Lib\site-packages")
import pandas as pd
import xlrd
import openpyxl
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
    read_temple = pd.ExcelFile(File, dtype=str)
    wb = openpyxl.load_workbook(File)
    sheets = wb.get_sheet_names()
    sheetobjectDict = {}

    for sheet in sheets:
        read_temple_sheet = read_temple.parse(sheet.decode("utf-8"))
        sheetobjectDict[sheet] = read_temple_sheet

    return sheetobjectDict

# 拆分execl 已公司名称拆分
def writeExcel(sheetobjectDict,dstpath,sheetName,company_name):
    # 过滤条件
    filter_li = '公司名称'.decode("utf-8")

    path = os.path.join(dstpath, "%s_%s.xlsx".decode("utf-8")) % (company_name, "账单")

    writer = pd.ExcelWriter(path)

    for sheet in sheetName:

        read_temple_sheet = sheetobjectDict[sheet]
        try:
            # 过滤条件
            read_temple_sheet_filter = read_temple_sheet[read_temple_sheet[filter_li] == company_name]
        except KeyError, e:
            # print type(e)
            print "过滤列名:%s， 错误" % filter_li
            # print " 列名错误 err"
            sys.exit(1)
        read_temple_sheet_filter.to_excel(writer, sheet.decode("utf-8"), index=False)
    writer.save()


def getCompanyName(File,sheetobjectDict):
    # 获取总账单中的公司名 去重 返回公司列表
    company = sheetobjectDict["总账单".decode("utf-8")]["公司名称".decode("utf-8")]
    companylist = []
    for r in company:
        companylist.append(r)
    company_unique = list(set(companylist))

    # 获取sheetname 列表
    wb = openpyxl.load_workbook(File)
    sheets = wb.get_sheet_names()
    return sheets, company_unique

def main(file,dstpath):
    # 读取execl 整个文件所有的sheet

    sheetobjectDict = readExcelSUB(file)

    sheetlist, CompanyList = getCompanyName(file, sheetobjectDict)

    for Company in CompanyList:
        print Company
        writeExcel(sheetobjectDict,dstpath,sheetlist, Company)

if __name__ == "__main__":
    # 源文件
    file = "D:/kilimall_report/break_report/12ng1-副本.xlsx".decode("utf-8")

    # 输出路径
    dstpath = "D:/kilimall_report/break_report/ke"

    main(file, dstpath)
