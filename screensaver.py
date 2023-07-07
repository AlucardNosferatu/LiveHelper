import os.path
import time

from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
action_chains = ActionChains(driver)


def get_doc_list(page_index):
    url = 'https://pan.ruijie.com.cn/share/9991571a1f3f111ae858a04b3e?page_number={}'.format(page_index + 1)
    driver.get(url)
    time.sleep(2)
    if page_index == 0:
        input('login?')
    doc_list = driver.find_elements(by=By.CLASS_NAME, value='name')
    doc_list.pop(0)
    return doc_list


def get_screens_for_doc(document):
    title = document.text.split('.')
    f_type = title.pop(-1)
    if not os.path.exists('.'.join(title)):
        os.mkdir(os.path.join(os.getcwd(), '.'.join(title)))
    page_count = int(input('loaded? input page count:'))
    for j in range(page_count):
        j_str = str(j)
        while len(j_str) < len(str(page_count)):
            j_str = '0' + j_str
        ss_path = os.path.join('.'.join(title), 'ss_{}.png'.format(j_str))
        driver.save_screenshot(ss_path)
        if f_type == 'pdf':
            action_chains.send_keys(Keys.CONTROL, Keys.DOWN).perform()
        elif f_type in ['ppt', 'pptx']:
            action_chains.send_keys(Keys.DOWN).perform()
        else:
            raise ValueError('Fuck You')
        time.sleep(1)


if __name__ == '__main__':
    keywords = ['陕西', '甘肃', '宁夏', '青海']
    for i in range(4):
        saved = []
        while True:
            flag = True
            dl = get_doc_list(i)
            for doc in dl:
                for keyword in keywords:
                    if keyword in doc.text and doc.text not in saved:
                        saved.append(doc.text)
                        print('网盘第' + str(i + 1) + '页', doc.text)
                        action_chains.click(on_element=doc).perform()
                        get_screens_for_doc(doc)
                        flag = False
                    if not flag:
                        break
                if not flag:
                    break
            if flag:
                break
    print('fuck you, too')
