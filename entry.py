# BeautifulSoup用于处理获取的网页数据
# 导入正则表达式，绘图，时间，随机模块
import json
import threading
import time
import urllib

import jieba
import nltk
from PyDictionary import PyDictionary
from bs4 import BeautifulSoup
from pystopwords import stopwords

from selenium import webdriver
from docx import Document

driver = None
cmd_pool = []
flag = True
stopwords_cn = stopwords()
stopwords_en = nltk.corpus.stopwords.words('english')
# "ci.json" comes from https://github.com/pwxcoo/chinese-xinhua/blob/master/data/ci.json
stopwords_cn2 = json.load(open('ci.json', 'r', encoding='utf-8'))
stopwords_cn2 = [word['ci'] for word in stopwords_cn2]
stopwords_en2 = PyDictionary()
pd_lock = threading.Lock()
cp_lock = threading.Lock()


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


def crawl_entries(keywords, depth=100):
    if type(keywords) is str:
        keywords = [keyword for keyword in keywords.split('#') if len(keyword.strip()) > 0]
    while depth > 0:
        ks_tmp = []
        for k in keywords:
            try:
                re = crawl_entry(keyword=k)
            except Exception as e:
                print(repr(e))
                re = []
            ks_tmp += re
        depth -= 1
        keywords = list(set(ks_tmp))


def crawl_entries_consumer(depth=5):
    print('线程:', threading.currentThread().getName(), '已启动')
    while flag:
        cp_lock.acquire()
        empty_q = len(cmd_pool) <= 0
        if not empty_q:
            print('线程:', threading.currentThread().getName(), '开始抓取作业，当前任务队列长度:', len(cmd_pool))
            keywords = cmd_pool.pop(0)
            cp_lock.release()
            print('线程:', threading.currentThread().getName(), '作业参数:', keywords)
            crawl_entries(keywords, depth=depth)
            print('线程:', threading.currentThread().getName(), '完成抓取作业，当前任务队列长度:', len(cmd_pool))
        else:
            cp_lock.release()
        time.sleep(0.1)
    print('线程:', threading.currentThread().getName(), '已结束')


def crawl_entries_producer():
    global flag
    c_thread = threading.Thread(target=crawl_entries_consumer, args=(5,))
    c_thread.start()
    d_threads = []
    while flag:
        cmd = input()
        if cmd != 'stop':
            if cmd.startswith('digest#'):
                if cmd.endswith('.txt'):
                    d_threads.append(threading.Thread(target=digest_txt, args=(cmd.replace('digest#', ''),)))
                elif cmd.endswith('.docx'):
                    d_threads.append(threading.Thread(target=digest_docx, args=(cmd.replace('digest#', ''),)))
                else:
                    continue
                d_threads[-1].start()
            else:
                cp_lock.acquire()
                cmd_pool.append(cmd)
                cp_lock.release()
        else:
            flag = False
            c_thread.join()
        i = 0
        while i < len(d_threads):
            if not d_threads[i].is_alive():
                d_threads.pop(i)
            else:
                i += 1


def digest_docx(docx_path):
    print('线程:', threading.currentThread().getName(), '已启动')
    print('线程:', threading.currentThread().getName(), '开始提取词条，词条文档所在路径:', docx_path)
    words = []
    document = Document(docx=docx_path)
    for paragraph in document.paragraphs:
        for run in paragraph.runs:
            if run.font.highlight_color is not None:
                words.append(run.text)
    print('线程:', threading.currentThread().getName(), '完成提取词条，提取相关词条个数:', len(words))
    cp_lock.acquire()
    cmd_pool.append('#'.join(words))
    cp_lock.release()
    print('线程:', threading.currentThread().getName(), '已结束')
    return words


def digest_txt(txt_path):
    print('线程:', threading.currentThread().getName(), '已启动')
    print('线程:', threading.currentThread().getName(), '开始提取词条，词条文档所在路径:', txt_path)
    file = open(txt_path, 'r', encoding='utf-8')
    lines = file.readlines()
    lines = ''.join(lines)
    words = jieba.lcut(lines)
    freq_dist = nltk.FreqDist(words)
    words = freq_dist.most_common()
    words = [word[0] for word in words if word[0] not in stopwords_cn]
    words = [word for word in words if len(word.strip()) >= 2]
    words = [word for word in words if word not in stopwords_cn2]
    words = [word for word in words if word.lower() not in stopwords_en]
    temp = []
    for word in words:
        print('线程:', threading.currentThread().getName(), '过滤英文词汇，当前检测词语:', word)
        pd_lock.acquire()
        meaning = stopwords_en2.meaning(word, disable_errors=True)
        pd_lock.release()
        if meaning is None:
            temp.append(word)
    words = temp
    print('线程:', threading.currentThread().getName(), '完成提取词条，提取相关词条个数:', len(words))
    cp_lock.acquire()
    cmd_pool.append('#'.join(words))
    cp_lock.release()
    print('线程:', threading.currentThread().getName(), '已结束')
    return words


if __name__ == '__main__':
    crawl_entries_producer()
