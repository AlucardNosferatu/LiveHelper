# BeautifulSoup用于处理获取的网页数据
# 导入正则表达式，绘图，时间，随机模块
import threading
import time
import urllib

from bs4 import BeautifulSoup
# 数据分析必备类库
# 绘图模块
from selenium import webdriver

driver = None
cmd_pool = []
flag = True


def crawl_entry(keyword):
    global driver
    if driver is None:
        driver = webdriver.Chrome()
    related_entries = []
    url = 'https://baike.c114.com.cn/view.asp?word={}'.format(urllib.parse.quote(keyword, encoding='gbk'))
    driver.get(url)
    time.sleep(1)
    if '用户登录' not in driver.title:
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")  # 解析网页
        entry = soup.find_all("div", class_="box2")[0]
        for _ in range(5):
            entry.contents.pop(-1)
        lines = []
        for line in entry.contents:
            line_text = line.text.strip()
            if len(line_text) > 0:
                lines.append(line_text)
            else:
                lines.append('。')
        lines = ''.join(lines)
        while '。。' in lines:
            lines = lines.replace('。。', '。')
        lines = lines.replace('。', '。\n')
        lines = [line + '\n' for line in lines.split('\n') if len(line.strip()) > 0]
        related = soup.find_all("div", class_="ref")[0]
        if '相关词条：' in related.text:
            for related_entry in related.contents:
                if hasattr(related_entry, 'attrs'):
                    if 'target' in related_entry.attrs.keys() and related_entry.attrs['target'] == '_blank':
                        related_entries.append(related_entry.text)
                    elif 'class' in related_entry.attrs.keys() and related_entry.attrs['class'] == ['disti']:
                        break
            lines.append('相关词条：' + ' '.join(related_entries) + '\n')
        if '/' in keyword:
            lines.insert(0, '同义词：' + keyword)
            keyword = keyword.replace('/', 'or')
        open(keyword.lower() + '.txt', 'w', encoding='utf-8').writelines(lines)
    elif ' ' in keyword:
        related_entries = keyword.split(' ')
    return related_entries


def search_now(keywords, depth=100):
    if type(keywords) is str:
        keywords = [keyword for keyword in keywords.split('#') if len(keyword.strip()) > 0]
    while depth > 0:
        ks_tmp = []
        for k in keywords:
            re = crawl_entry(keyword=k)
            ks_tmp += re
        depth -= 1
        keywords = list(set(ks_tmp))


def consumer(depth=5):
    print('线程:', threading.currentThread().getName(), '已启动')
    inner_flag = True
    while flag:
        while inner_flag and len(cmd_pool) <= 0:
            time.sleep(0.1)
            inner_flag = flag
        if not inner_flag:
            break
        print('线程:', threading.currentThread().getName(), '开始抓取作业，当前任务队列长度:', len(cmd_pool))
        keywords = cmd_pool.pop(0)
        print('线程:', threading.currentThread().getName(), '作业参数:', keywords)
        search_now(keywords, depth=depth)
        print('线程:', threading.currentThread().getName(), '完成抓取作业，当前任务队列长度:', len(cmd_pool))
    print('线程:', threading.currentThread().getName(), '已结束')


if __name__ == '__main__':
    c_thread = threading.Thread(target=consumer, args=(5,))
    c_thread.start()
    while flag:
        cmd = input()
        if cmd != 'stop':
            cmd_pool.append(cmd)
        else:
            flag = False
            c_thread.join()
