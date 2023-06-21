# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 22:45:48 2019

@author: Scrooge
"""

import re
import requests
import os
import sys

path = os.path.abspath(os.path.dirname(sys.argv[0]))


def job_ads():
    url = 'https://www.zhipin.com/web/geek/job?city=101230100'
    activity = BossLocalJob()
    activity.change_page(url, 10)
    activity.get_source()
    activity.get_all_events()
    activity.get_entity()
    activity.save_entity()


class BossLocalJob(object):
    def __init__(self):
        self.entities = []
        self.events = []
        self.page_group = None
        self.html_texts = []
        print('开始爬取内容')

    # 获取单个连接html文本
    def get_source(self):
        self.html_texts.clear()
        for url in self.page_group:
            html = requests.get(url)
            html.encoding = 'utf-8'
            self.html_texts.append(html.text)

    # 根据页数获取所有的链接
    def change_page(self, url, total_page):
        start_page_num = int(re.search('start=(\d+)', url, re.S).group(1))
        page_group = []
        for i in range(start_page_num, total_page + 1):
            per_link = re.sub('start=\d+', 'start=%s' % (i * 10), url, re.S)
            page_group.append(per_link)
        self.page_group = page_group

    def get_all_events(self):
        for html_text in self.html_texts:
            a = re.search('<ul class="events-list(.*?)<div class="paginator">', html_text, re.S)
            if a:
                bigger_html = a.group(1)
                events = re.findall('(<li class="list-entry".*?</p>\s+</div>\s+</li>)', bigger_html, re.S)
            else:
                events = []
            self.events.append(events)

    # 获取每个活动的详细信息
    def get_entity(self):
        for events in self.events:
            for event in events:
                entity = {
                    'title': re.search('<span itemprop="summary">(.*?)</span>', event, re.S).group(1),
                    'time': re.search('时间：</span>\s+(.*?)\s+<time', event, re.S).group(1),
                    'position': re.search('<li title="(.*?)">\s+<span', event, re.S).group(1),
                    'fee': re.search('<strong>(.*?)</strong>', event, re.S).group(1)
                }
                self.entities.append(entity)

    # 将活动信息保存到文本文件中
    def save_entity(self):
        f = open(os.path.join(path, '.txt'), 'a', encoding='utf-8')
        for event in self.entities:
            f.writelines('title:' + event['title'] + '\n')
            f.writelines('time:' + event['time'] + '\n')
            f.writelines('position:' + event['position'] + '\n')
            f.writelines('fee:' + event['fee'] + '\n')
            f.writelines('\n')
        f.close()


if __name__ == '__main__':
    job_ads()
