#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 18-6-6 下午2:25
# @Author  : system
# @Email   : system@stormorai.com
# @File    : urlCheck.py
# @Software: PyCharm

import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 第三方 SMTP 服务
mail_host = "smtp.exmail.qq.com"  # 设置服务器
mail_user = "system@stormorai.com"  # 用户名
mail_pass = "Tipdm2016"  # 口令

sender = 'system@stormorai.com'
receiver = ['fangxing@stormorai.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱


def getUrlList(filename):
    urlist= []
    with open(filename, 'r') as f:
        content = f.readlines()
    for line in content:
        urlist.append(line.strip())
    return urlist

def getUrlStatus(url):
    status=requests.get(url).status_code
    return status

def sendmail(sender, receiver, mail_host, mail_user, mail_pass, url, code):

    content = "url: %s 访问状态码: %s！请注意检查" % (url, code)
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = "%s" % sender
    print(message['From'])
    message['To'] = ",".join(receiver)
    print(message['To'])
    message['Subject'] = 'Url 状态码检测'

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receiver, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print("Error: ", e)

if __name__ == "__main__":
    urlList = getUrlList('url.txt')
    for url in urlList:
        urlStatus = getUrlStatus(url)
        # if urlStatus != 200:
        sendmail(sender, receiver, mail_host, mail_user, mail_pass, url, str(urlStatus))


