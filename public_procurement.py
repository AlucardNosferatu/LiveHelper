import os
import random
import time

import PyPDF2
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.print_page_options import PrintOptions
from base64 import b64decode

from tqdm import tqdm

keywords = None


def crawl_procurements(start_index=5, end_index=64, keyword='宁夏'):
    def into_position(u, d):
        d.get(u)
        time.sleep(random.random() + 1)
        d.find_element(By.ID, "procurement_notice_list").click()
        time.sleep(random.random() + 1)
        d.find_element(By.ID, "title").send_keys(keyword)
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
                # region load catalog per page
                driver.execute_script('gotoPage({})'.format(i + 1))
                time.sleep(random.random() + 1)
                html = driver.page_source
                soup = BeautifulSoup(html, "lxml")  # 解析网页
                # endregion
                # region read catalog
                p_list = soup.find_all("tbody")[2].contents
                p_list.pop(0)
                p_list.pop(0)
                p_dict = {}
                indices = [
                    '{} {}'.format(
                        p.contents[7].text,
                        p.contents[5].text.strip().replace('/', '\\').replace('\\', 'or')
                    ) for p in p_list if type(p) is Tag and keyword in p.text
                ]
                [
                    p_dict.__setitem__(
                        '{} {}'.format(
                            p.contents[7].text,
                            p.contents[5].text.strip().replace('/', '\\').replace('\\', 'or')
                        ),
                        p.attrs['onclick']
                    ) for p in p_list if type(p) is Tag and keyword in p.text
                ]
                # endregion
                assert len(indices) > 0
                for index in indices:
                    # region jump to print view
                    driver.get(
                        url_print_view.format(
                            p_dict[index].replace("selectResult('", '').replace("')", '')
                        )
                    )
                    # endregion
                    # region print PDF
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
                    # endregion
                    # region return catalog
                    driver.back()
                    time.sleep(random.random() + 1)
                    driver.find_element(By.ID, "search").send_keys(Keys.ENTER)
                    time.sleep(random.random() + 2)
                    driver.execute_script('gotoPage({})'.format(i + 1))
                    time.sleep(random.random() + 1)
                    # endregion
                finish = True
            except Exception as e:
                print(repr(e))
                into_position(url, driver)


def filter_procurements(files_folder='采购信息/宁夏', filter_func=None):
    files = os.listdir(files_folder)
    files = [os.path.join(files_folder, file) for file in files]
    doc_dict = {}
    for file in files:
        time.sleep(0.1)
        print('Now reading:', file)
        pdf_reader = PyPDF2.PdfReader(open(file, 'rb'))
        content = ''
        for i in tqdm(range(len(pdf_reader.pages))):
            content += (pdf_reader.pages[i].extract_text() + '\n')
        if filter_func is None or filter_func(content):
            doc_dict.__setitem__(file, content)
    return doc_dict


def has_key(content):
    global keywords
    if keywords is None:
        keywords = []
    window_size = 5
    for keyword in keywords:
        if keyword in content:
            content: str
            pos_start = content.index(keyword)
            pos_end = pos_start + len(keyword)
            sample_window = content[pos_start - window_size:pos_end + window_size]
            time.sleep(0.1)
            print('检测到关键词:', keyword, '所在语句:', sample_window)
            return True
    return False


def main():
    global keywords
    hint_str = '1.爬取移动采购平台上标题含有特定关键词的采购公告【输入crawl】\n2.过滤爬取结果中内容包含特定关键词对的PDF文档【输入filter】\n'
    while True:
        cmd = ''
        while cmd not in ['crawl', 'filter']:
            cmd = input(hint_str)
        try:
            if cmd == 'filter':
                files_folder = ''
                while len(files_folder.strip()) <= 0:
                    files_folder = input('请输入PDF文件所在路径')
                keywords_input = ''
                while len(keywords_input.strip()) <= 0:
                    keywords_input = input('请输入过滤文档用的关键词，多个关键词用#分隔')
                keywords = keywords_input.split('#')
                doc_dict = filter_procurements(files_folder=files_folder, filter_func=has_key)
                [print(key) for key in doc_dict.keys()]
            elif cmd == 'crawl':
                start_index = input('请输入起始页码，默认为1')
                if start_index == '':
                    start_index = 1
                else:
                    start_index = int(start_index)
                end_index = input('请输入结束页码，默认为16')
                if end_index == '':
                    end_index = 16
                else:
                    end_index = int(end_index)
                keyword = ''
                while len(keyword.strip()) <= 0:
                    keyword = input('请输入匹配标题用的关键词')
                crawl_procurements(
                    start_index=start_index,
                    end_index=end_index,
                    keyword=keyword
                )
            else:
                raise ValueError('cmd error!\ncmd should be "crawl" or "filter"')
        except Exception as e:
            print(repr(e))
        print('上一任务结束，开始下一任务')


if __name__ == '__main__':
    main()
