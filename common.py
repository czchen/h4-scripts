#!/usr/bin/env python
# coding:utf8
#
# Author: Chun-Yu Lee (Mat) <matlinuxer2@gmail.com>
# Copyright: Chun-Yu Lee (Mat) <matlinuxer2@gmail.com>
# License: MIT
#

from __future__ import print_function

import datetime

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Header import Header

import os
import ConfigParser

from BeautifulSoup import BeautifulSoup

import tempfile

import re
import sys

root_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(root_path, '3rd'))
sys.path.append(os.path.join(root_path, '3rd', 'gdata-python-client', 'src'))

import html2text  # pip version decode error, using 3rd-party instead
import GoogleSpreadsheetAPI


def thisThursday():
    delta_days = 4 - datetime.date.today().isoweekday()
    this_thursday = datetime.date.today() + datetime.timedelta(days=delta_days)
    return this_thursday.isoformat()


def thisThursday_fb_format():
    delta_days = 4 - datetime.date.today().isoweekday()
    this_thursday = datetime.date.today() + datetime.timedelta(days=delta_days)
    return this_thursday.strftime('X%m/X%d/X%Y').replace('X0', 'X').replace('X', '')


def nextThursday(this_thursday_str):
    this_thursday = datetime.datetime.strptime(this_thursday_str, "%Y-%m-%d")
    next_thursday = this_thursday + datetime.timedelta(days=7)
    result = next_thursday.date().isoformat()
    return result


def prevThursday(this_thursday_str):
    this_thursday = datetime.datetime.strptime(this_thursday_str, "%Y-%m-%d")
    prev_thursday = this_thursday + datetime.timedelta(days=-7)
    result = prev_thursday.date().isoformat()
    return result


def isThursday(date_str):
    this_day = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    result = (this_day.isoweekday() == 4)
    return result


def isFuture(date_str):
    this_day = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    today = datetime.date.today()
    if today >= this_day:
        return False
    else:
        return True


#
# send_gmail("matlinuxer2@gmail.com", "matlinuxer2@gmail.com", "Hello from python!", "<hr/><h1>hello from python</h1><hr/>", "USERNAME", "PASSWORD")
#
def send_gmail(sender, recipient, subject, text, html, username, passwd):
    msg = MIMEMultipart("alternative")

    msg['Subject'] = Header(subject, "utf-8")
    msg['From'] = sender
    msg['To'] = recipient

    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(username, passwd)
    mailServer.sendmail(sender, recipient, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()


##################
## Settings
##################
if os.name == "posix":
    settings_file = os.path.join(os.getenv('HOME'), ".h4notifier.ini")
else:
    settings_file = None

volatile_settings = {
    'username': 'USERNAME',
    'password': 'PASSWORD',
    'who': 'who@gmail.com',
    'email_address': 'hackingthursday@googlegroups.com',
    'wikidot_api_user': 'WIKIDOT_API_USER',
    'wikidot_api_key': 'WIKIDOT_API_KEY',
    'facebook_user': 'FB_USER',
    'facebook_password': 'FB_PASS',
    'facebook_api_key': 'FB_API_KEY',
    'facebook_secret': 'FB_SECRET',
    'facebook_gid': '############',
    'bbs_user': 'guest',
    'bbs_pass': '',
    'googledoc_email': '',
    'googledoc_password': '',
}

def config_get( sec, opt ):
    result = ""
    if os.access(settings_file, os.R_OK):
        config = ConfigParser.RawConfigParser()
        config.read(settings_file)
        try:
            result = config.get( sec, opt )
        except:
            pass

    return result

def read_settings_from_file():
        # Section: gmail
        volatile_settings['username'] = config_get('gmail', 'username')
        volatile_settings['password'] = config_get('gmail', 'password')

        # Section: hackingthursday
        volatile_settings['who'] = config_get('hackingthursday', 'who')
        volatile_settings['email_address'] = config_get('hackingthursday', 'email_address')

        # Section: wikidot
        volatile_settings['wikidot_api_user'] = config_get('wikidot', 'wikidot_api_user')
        volatile_settings['wikidot_api_key'] = config_get('wikidot', 'wikidot_api_key')

        # Section: facebook
        volatile_settings['facebook_password'] = config_get('facebook', 'password')
        volatile_settings['facebook_user'] = config_get('facebook', 'username')
        volatile_settings['facebook_api_key'] = config_get('facebook', 'facebook_api_key')
        volatile_settings['facebook_secret'] = config_get('facebook', 'facebook_secret')
        volatile_settings['facebook_gid'] = config_get('facebook', 'facebook_gid')

        # Section: bbs
        volatile_settings['bbs_user'] = config_get('bbs', 'user')
        volatile_settings['bbs_pass'] = config_get('bbs', 'pass')

        # Section: googledoc
        volatile_settings['googledoc_email'] = config_get('googledoc', 'email')
        volatile_settings['googledoc_password'] = config_get('googledoc', 'password')
        volatile_settings['googledoc_spreadsheet'] = config_get('googledoc', 'spreadsheet')
        volatile_settings['googledoc_worksheet'] = config_get('googledoc', 'worksheet')

        value = config_get('googledoc', 'dryrun')
        value = value.strip().lower()
        if value in ["yes", "y", "true", "on"]:
            value = True
        else:
            value = False
        volatile_settings['googledoc_dryrun'] = value


##################
## Contents
##################
mail_content_header = '''
這個是昨天的聚會手記，感謝大家的心得分享～

'''

mail_content_footer = '''
----
主網站: http://www.hackingthursday.org/
Google論譠: http://groups.google.com/group/hackingthursday/
Facebook群組: http://www.facebook.com/groups/hackingday/
'''


def file2string(path):
    result = ""
    f = open(path)
    for line in f:
        result += line

    f.close()

    return result


def string2file(string, path):
    f = open(path, 'w')
    f.write(string)
    f.close()


def html2xml(the_html):
    result = ""
    htmlfile = tempfile.mktemp()
    xmlfile = tempfile.mktemp()
    string2file(the_html, htmlfile)
    os.system("tidy -q -asxhtml -numeric -utf8 < " + htmlfile + " > " + xmlfile)
    result = file2string(xmlfile)
    os.system("rm " + htmlfile)
    os.system("rm " + xmlfile)

    return result


def html2txt(the_html):
    result = html2text.html2text(the_html.decode('utf-8'), '').encode('utf-8')
    return result


def get_wikidot_content_body(URL):
    xmlfile = tempfile.mktemp()
    htmlfile = tempfile.mktemp()

    os.system("wget -O " + htmlfile + " " + URL)
    the_html = file2string(htmlfile)
    os.system("rm " + htmlfile)

    soup = BeautifulSoup(the_html)
    div = soup.findAll('div', attrs={'id': 'page-content'})
    res_txt = ""
    for d in div:
        res_txt += d.prettify()

    os.system("rm " + xmlfile)
    result = res_txt

    return result


def get_etherpad_content_body(URL):
    htmlfile = tempfile.mktemp()

    ret = os.system("wget -O " + htmlfile + " " + URL)
    if ret == 0:
        the_html = file2string(htmlfile)
    else:
        the_html = None
    os.system("rm " + htmlfile)

    result = the_html

    return result


def fetch_googledoc_spreadsheet(email, password, spreadsheet_name, worksheet_name):
    res_ary = []
    col_mapping = {}
    result_ary = {}

    # 取得列表內容
    spr = GoogleSpreadsheetAPI.Spreadsheet(email, password, spreadsheet_name)
    work = GoogleSpreadsheetAPI.Spreadsheet.Worksheet(spr, worksheet_name)
    feed = work.getCells()

    for i, entry in enumerate(feed.entry):
        #print (i, entry.title.text, entry.content.text)
        pattern = r"(\w)(\d+)"
        matches = re.findall(pattern, entry.title.text)
        #print matches
        col_idx = matches[0][0]
        row_idx = matches[0][1]

        res_ary.append((row_idx, col_idx, entry.content.text))

    # 取得欄位名稱對應
    for item in res_ary:
        row_idx = item[0]
        col_idx = item[1]
        value = item[2]

        if row_idx == "1":
            col_mapping[col_idx] = value.strip()

    # 處理並產生回傳陣列
    for item in res_ary:
        row_idx = item[0]
        col_idx = item[1]
        value = item[2]

        if row_idx != '1':
            if not row_idx in result_ary:
                result_ary[row_idx] = {}
                for col_name in col_mapping.values():
                    result_ary[row_idx][col_name] = ''

            col_name = col_mapping[col_idx]

            # 修正手機的格式
            if col_name == "Mobile" and value.__len__() == 9:
                value = "0" + value

            result_ary[row_idx][col_name] = value

    return result_ary


def convert_spreadsheet_to_userdata(sprd_data):
    result = []

    for k in sprd_data.keys():
        row = sprd_data[k]

        alias = row['筆名'].split('||')
        url_name = row['url_name']
        rel_name = row['Name'].lower().strip()
        email = row['E-Mail']
        notify = row['notify']

        result.append({
            "alias": alias,
            "url_name": url_name,
            "rel_name": rel_name,
            "email": email,
            "notify": notify,
        })

    return result


def search_userdata(sprd_data, keyword):
    result = {}
    for k in sprd_data.keys():
        row = sprd_data[k]
        for value in row.values():
            if value.find(keyword) >= 0:
                result[k] = row

    return result


def show_userdata(sprd_data_row):
    field00 = sprd_data_row['url_name']
    field01 = sprd_data_row['Name']
    field02 = sprd_data_row['Full Name']
    field03 = sprd_data_row['E-Mail']
    field04 = sprd_data_row['Mobile']
    field05 = sprd_data_row['筆名']
    field06 = sprd_data_row['notify']
    field07 = sprd_data_row['備註']

    print("ID".rjust(10), ":", field00)
    print("Nick".rjust(10), ":", field01)
    print("姓名".rjust(12), ":", field02)
    print("E-mail".rjust(10), ":", field03)
    print("手機".rjust(12), ":", field04)
    print("筆名".rjust(12), ":", field05.replace('||', ', '))
    print("notify".rjust(10), ":", field06)
    print("備註".rjust(12), ":", field07)
