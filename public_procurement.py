import random
import time

from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.print_page_options import PrintOptions
from base64 import b64decode

url = 'https://b2b.10086.cn/b2b/main/preIndex.html'
driver = webdriver.Chrome()
driver.get(url)
time.sleep(random.random()+1)
driver.find_element(By.ID, "procurement_notice_list").click()
time.sleep(random.random()+1)
driver.find_element(By.ID, "title").send_keys('宁夏')
driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
time.sleep(random.random()+1)
for i in range(4, 64):
    driver.execute_script('gotoPage({})'.format(i + 1))
    time.sleep(random.random()+1)
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")  # 解析网页
    p_list = soup.find_all("tbody")[2].contents
    p_list.pop(0)
    p_list.pop(0)
    p_dict = {}
    indices = [p.contents[5].text.strip() + ' ' + p.contents[7].text for p in p_list if type(p) is Tag]
    [
        p_dict.__setitem__(
            p.contents[5].text.strip() + ' ' + p.contents[7].text,
            p.attrs['onclick']
        ) for p in p_list if type(p) is Tag
    ]
    for index in indices:
        driver.get(
            'https://b2b.10086.cn/b2b/main/printView.html?noticeBean.id={}&noticeBean.appType=NOTICE'.format(
                p_dict[index].replace("selectResult('", '').replace("')", '')
            )
        )
        time.sleep(random.random()+1)
        print_options = PrintOptions()
        print_options.page_height = 8.5
        print_options.page_width = 11
        print_options.scale = 0.3
        pdf_base64 = driver.print_page(print_options)
        pdf_bytes = b64decode(pdf_base64, validate=True)
        if pdf_bytes[0:4] != b'%PDF':
            raise ValueError('Missing the PDF file signature')
        f = open(index + '.pdf', 'wb')
        f.write(pdf_bytes)
        f.close()
        driver.back()
        time.sleep(random.random()+1)
        driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
        time.sleep(random.random()+20)
