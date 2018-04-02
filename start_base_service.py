# -*- coding: UTF-8 -*-
# by gzq
# date :2017/9/22 0022 19:34

import time
import re
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
# 自动登陆jenkins 点击指定视图下的打包任务　
from selenium import webdriver
# import scrapy
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.wait import WebDriverWait
# 自动执行jenkins 点击指定视图中job
web_site = "http://192.168.0.223:8080/view/%E5%BC%80%E5%8F%91%E7%8E%AF%E5%A2%834.0-AUTO/"
web_login = "http://192.168.0.223:8080/login?from=%2F"
#　驱动游览器　
# browser = webdriver.Firefox()
browser = webdriver.Chrome()

# 正则匹配试图中的job 名字
re_job_id = re.compile(r'<tr id="(job_.*?)" class="',re.M)

# 黑名单任务不执行　
backJobDict = {"备份测试环境V4.0.0-AUTO":
             [
             "job_备份测试环境-OSS-COMMON-V4.0.0-AUTO",
             "job_备份测试环境-MODEL-ANNOTATION-V4.0.0-AUTO",
             "job_备份测试环境-OSS-XCODE-V4.0.0-AUTO",
             "job_备份测试环境-APP-H5-XCODE-V4.0.0-AUTO",
             "job_备份测试环境-API-XCODE-V4.0.0-AUTO",
             "job_备份测试环境-APP-H5-OSS-XCODE-V4.0.0-AUTO",
             "job_备份测试环境-MODEL-ANNOTATION-V4.0.0-AUTO",
             "job_备份测试环境-UPLOAD-V4.0.0-AUTO",
             ],
    "测试环境4.0-AUTO":
             [
             "job_测试环境-OSS-COMMON-V4.0.0-AUTO",
             # "job_测试环境-OSS-TMS-OPEN-V4.0.0-AUTO",
             # "job_测试环境-OSS-TMS-H5-V4.0.0-AUTO",
             # "job_测试环境-OSS-STORE-V4.0.0-AUTO",
             # "job_测试环境-API-SMS-V4.0.0-AUTO",
             # "job_测试环境-API-POS-BILL-V4.0.0-AUTO",
             # "job_测试环境-API-POS-V4.0.0-AUTO",
             # "job_测试环境-OSS-POS-V4.0.0-AUTO",
             # "job_测试环境-APP-H5-OSS-POS-V4.0.0-AUTO",
             "job_测试环境-MODEL-ANNOTATION-V4.0.0-AUTO",
             "job_测试环境-OSS-XCODE-V4.0.0-AUTO",
             "job_测试环境-APP-H5-XCODE-V4.0.0-AUTO",
             "job_测试环境-API-XCODE-V4.0.0-AUTO",
             "job_测试环境-APP-H5-OSS-XCODE-V4.0.0-AUTO",
             "job_测试环境-MODEL-ANNOTATION-V4.0.0-AUT",
             "job_测试环境-Restart_ALLService-V4.0.0-AUTO",
             "job_restart-测试环境（IP225）- 服务名--服务所在服务器",
             "job_restart-测试环境（ip221）- 服务名--服务名所在服务器",
             "job_测试环境-UPLOAD-V4.0.0-AUTO",
             # "job_测试环境-OSS-SMS-V4.0.0-AUTO",
             ],
    "开发环境4.0-AUTO":[
             "job_开发环境-OSS-COMMON-V4.0.0-AUTO",
             "job_开发环境-MODEL-ANNOTATION-V4.0.0-AUTO",
             "job_开发环境-OSS-XCODE-V4.0.0-AUTO",
             "job_开发环境-APP-H5-XCODE-V4.0.0-AUTO",
             "job_开发环境-API-XCODE-V4.0.0-AUTO",
             "job_开发环境-APP-H5-OSS-XCODE-V4.0.0-AUTO",
             "job_开发环境-MODEL-ANNOTATION-V4.0.0-AUT",
             "job_开发环境-Restart_ALLService-V4.0.0-AUTO",
             "job_restart-开发环境- 服务名--服务名所在服务器",
             "job_开发环境-UPLOAD-V4.0.0-AUTO",
             "job_开发环境-API-XCODE-V4.0.0-AUTO"

    ]
}

def login(username,passwd):
    #登陆函数
    browser.get(web_login)
    browser.find_element_by_id("j_username").clear()
    browser.find_element_by_id("j_username").send_keys(username)
    browser.find_element_by_name("j_password").clear()
    browser.find_element_by_name("j_password").send_keys(passwd)
    browser.find_element_by_id("yui-gen1-button").click()

def click_job(jobViewName):
    # 切换job试图
    browser.find_element_by_link_text(jobViewName).click()
    # 获取网页内容
    content = browser.page_source
    job_list_tmp = re_job_id.findall(content)
    job_list =[]
    for i in job_list_tmp:
        job_name = i.encode("utf-8")
        backJoblist = backJobDict[jobViewName]
        if job_name not in backJoblist:
            job = '//*[@id="%s"]/td[7]/a/img' %job_name
            browser.find_element_by_xpath(job).click()
            time.sleep(5)
            print job_name


if __name__ == "__main__":
    username = "guozhiquan"
    passwd = "123456"
    login(username,passwd)
    tag = sys.argv[1]
    if tag == "dev":
        click_job("开发环境4.0-AUTO")
        browser.quit()
        sys.exit()
    elif tag == "test":
        click_job("测试环境4.0-AUTO")
        browser.quit()
        sys.exit()
    elif tag == "bktest":
      click_job("备份测试环境V4.0.0-AUTO")
      browser.quit()
      sys.exit()
    elif tag =="offic":
        pass
    else:
        pass


