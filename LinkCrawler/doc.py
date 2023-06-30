# BeautifulSoup用于处理获取的网页数据
# 导入正则表达式，绘图，时间，随机模块
import time

from bs4 import BeautifulSoup
# 数据分析必备类库
# 绘图模块
from selenium import webdriver

if __name__ == '__main__':
    driver = webdriver.Chrome()
    titles = []
    page_index = {}
    for i in range(4):
        url = 'https://pan.ruijie.com.cn/share/9991571a1f3f111ae858a04b3e?page_number={}'.format(i + 1)
        driver.get(url)
        time.sleep(2)
        if i == 0:
            input('login?')
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")  # 解析网页
        doc_list = soup.find_all("div", class_="name")
        keywords = ['陕西', '甘肃', '宁夏', '青海']
        doc_list.pop(0)
        for doc in doc_list:
            title = doc.contents[1]
            for keyword in keywords:
                if keyword in title:
                    titles.append(title)
                    page_index.__setitem__(title, str(i + 1))
    [print('网盘第' + page_index[title] + '页', title) for title in titles]
