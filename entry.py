# BeautifulSoup用于处理获取的网页数据
# 导入正则表达式，绘图，时间，随机模块
import time
import urllib

from bs4 import BeautifulSoup
# 数据分析必备类库
# 绘图模块
from selenium import webdriver

driver = None


def crawl_entry(keyword):
    global driver
    if driver is None:
        driver = webdriver.Chrome()
    related_entries = []
    url = 'https://baike.c114.com.cn/view.asp?word={}'.format(urllib.parse.quote(keyword, encoding='gbk'))
    driver.get(url)
    time.sleep(1)
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
    return related_entries


if __name__ == '__main__':
    dep = 100
    ks = ['SPN', '网络', '运营商', 'SDN', '5G']
    while dep > 0:
        ks_tmp = []
        for k in ks:
            re = crawl_entry(keyword=k)
            ks_tmp += re
        dep -= 1
        ks = ks_tmp
