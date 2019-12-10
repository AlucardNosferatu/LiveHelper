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

def cityevents(city,event_type,time):
   eventInfo = []
   url = 'https://www.douban.com/location/'+city+'/events/'+time+'-'+event_type+'?start=0'
   activity = douban_local_activity()
   links = activity.changePage(url,10)
   for link in links:
       print('正在处理页面：' + link)
       html = activity.getSource(link)
       allEvents = activity.getAllEvents(html)
       #print(allEvents)
       for item in allEvents:
           entity = activity.getEntity(item)
           eventInfo.append(entity)
   activity.saveEntity(city,event_type,time,eventInfo)   

class douban_local_activity(object):
    def __init__(self):
        print('开始爬取内容')
	#获取单个连接html文本
    def getSource(self,url):
        html = requests.get(url)
        html.encoding = 'utf-8'
        return html.text
    #根据页数获取所有的链接
    def changePage(self,url,totalPage):
        startPageNum = int(re.search('start=(\d+)',url,re.S).group(1))
        pageGroup = []
        for i in range(startPageNum,totalPage+1):
            perLink = re.sub('start=\d+','start=%s' % (i*10),url,re.S)
            pageGroup.append(perLink)
        return pageGroup
    #抓取单页所有的活动信息
    
    #
    #getAllEvents这里有问题，在201906以后的内容都爬取不到，需要调
    #
    
    def getAllEvents(self,source):
        a = re.search('<ul class="events-list(.*?)<div class="paginator">', source, re.S)
        if a:
            biggerHtml = a.group(1)
            events = re.findall('(<li class="list-entry".*?</p>\s+</div>\s+</li>)', biggerHtml, re.S)
        else:
            events = []
        return events
    #获取每个活动的详细信息
    
    
    def getEntity(self,event):
        entity = {}
        entity['title'] = re.search('<span itemprop="summary">(.*?)</span>',event,re.S).group(1)
        entity['time'] = re.search('时间：</span>\s+(.*?)\s+<time',event,re.S).group(1)
        entity['position'] = re.search('<li title="(.*?)">\s+<span',event,re.S).group(1)
        entity['fee'] = re.search('<strong>(.*?)</strong>',event,re.S).group(1)
        return entity
    #将活动信息保存到文本文件中
    def saveEntity(self,city,event_type,time,eventInfo):
        if os.path.exists(path+'\\'+city+'\\'+event_type)==False:
            os.makedirs(path+'\\'+city+'\\'+event_type) 
        f = open(path+'/'+city+'/'+event_type+'/'+time+'.txt','a',encoding='utf-8')
        for event in eventInfo:
            f.writelines('title:' + event['title'] + '\n')
            f.writelines('time:' + event['time'] + '\n')
            f.writelines('position:' + event['position'] + '\n')
            f.writelines('fee:' + event['fee'] + '\n')
            f.writelines('\n')
        f.close()
        

        
if __name__ == '__main__':
    #citys=['beijing','tianjin','shenyang','changchun','haerbin','shanghai','nanjing','wuhan','guangzhou','chongqing','chengdu','xian']
    citys=['beijing']
    #events=['salon','exhibition','competition','course','others']
    events=['all']
    #times=['20190207','20190208','20190209']
    times=['20190609']
    for city in citys:
        for event in events:
            for time in times:
                cityevents(city,event,time)