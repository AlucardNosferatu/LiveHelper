import random
import time

from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.print_page_options import PrintOptions
from base64 import b64decode


def crawl_procurements(start_index=5, end_index=64, location='宁夏'):
    def into_position(u, d):
        d.get(u)
        time.sleep(random.random() + 1)
        d.find_element(By.ID, "procurement_notice_list").click()
        time.sleep(random.random() + 1)
        d.find_element(By.ID, "title").send_keys(location)
        d.find_element(By.ID, "search").send_keys(Keys.ENTER)
        time.sleep(random.random() + 1)

    url = 'https://b2b.10086.cn/b2b/main/preIndex.html'
    url_print_view = 'https://b2b.10086.cn/b2b/main/printView.html?noticeBean.id={}&noticeBean.appType=NOTICE'
    driver = webdriver.Chrome()
    into_position(url, driver)
    for i in range(start_index - 1, end_index):
        print('page:', i + 1)
        finish = False
        while not finish:
            try:
                driver.execute_script('gotoPage({})'.format(i + 1))
                time.sleep(random.random() + 1)
                html = driver.page_source
                soup = BeautifulSoup(html, "lxml")  # 解析网页
                p_list = soup.find_all("tbody")[2].contents
                p_list.pop(0)
                p_list.pop(0)
                p_dict = {}
                indices = [
                    '{} {}'.format(
                        p.contents[7].text,
                        p.contents[5].text.strip().replace('/', '\\').replace('\\', 'or')
                    ) for p in p_list if type(p) is Tag and location in p.text
                ]
                [
                    p_dict.__setitem__(
                        '{} {}'.format(
                            p.contents[7].text,
                            p.contents[5].text.strip().replace('/', '\\').replace('\\', 'or')
                        ),
                        p.attrs['onclick']
                    ) for p in p_list if type(p) is Tag and location in p.text
                ]
                assert len(indices) > 0
                for index in indices:
                    driver.get(
                        url_print_view.format(
                            p_dict[index].replace("selectResult('", '').replace("')", '')
                        )
                    )
                    time.sleep(random.random() + 1)
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
                    time.sleep(random.random() + 1)
                    driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
                    time.sleep(random.random() + 2)
                    driver.execute_script('gotoPage({})'.format(i + 1))
                    time.sleep(random.random() + 1)
                finish = True
            except Exception as e:
                print(repr(e))
                into_position(url, driver)


if __name__ == '__main__':
    crawl_procurements(
        start_index=1,
        end_index=16,
        location='甘肃'
    )
