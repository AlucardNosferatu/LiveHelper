import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


class DummyObj:
    def __init__(self):
        self.location = {'x': 0, 'y': 0}


unfold_labels = {
    '接口·交换·路由': '2',
    'DHCP·IP地址分配': '2',
    '日志对接网管': '2',
    '防环': '2',
    'ping/tracert': '4',
    '一键信息收集': '4',
    '设备基础配置': '4',
    '重启设备': '4',
    '设备升级': '4',
    '配置管理': '4',
    '设备恢复出厂配置': '4',
    'Web控制台': '4',
    'License授权': '5',
    '管理员帐号': '5',
    '证书与备案': '5',
    '操作日志': '5',
    '数据备份和导入': '5',
    'Interfaced · Switches · Routers': '2',
    'DHCP · IP Address Assignment': '2',
    'Log docking network management': '2',
    'Loop Guard': '2',
    'One-Click Collect': '4',
    'Basic Config': '4',
    'Restart': '4',
    'Upgrade': '4',
    'Configuration Management': '4',
    'Restore Factory Settings': '4',
    'Web Console': '4',
    'License': '5',
    'Admin Account': '5',
    'Certificates and Registration': '5',
    'Operation Log': '5',
    'Data Backup and Import': '5'
}

url = 'https://10.52.25.9/app/index'
driver = webdriver.Chrome()
driver.get(url)
input('等待手动登录:')
viewed = ['1']
results = []
before_jump = None
max_refresh = 8
refresh_count = 0
while True:
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    items = soup.find_all('li', class_='el-menu-item')
    items += soup.find_all('button', class_='el-button el-button--text')
    items += soup.find_all('button', class_='el-button el-button--text el-button--small')
    items = [item for item in items if item.attrs['id'] != '1']
    for i in range(len(items)):
        try:
            target = driver.find_element(by=By.ID, value=items[i].attrs['id'])
            loc = target.location
            set_none = items[i].text.strip() not in unfold_labels.keys()
            set_none = set_none and not loc['x'] == loc['y'] == 0
            if set_none:
                items[i] = None
        except Exception as e:
            _ = e
            items[i] = None
    items = [item for item in items if item is not None]
    # noinspection PyUnresolvedReferences
    ids = [item.attrs['id'] for item in items]
    next_hop_id = '1'
    i = 0
    while next_hop_id in viewed and i < len(ids):
        next_hop_id = ids[i]
        i += 1
    if next_hop_id in viewed:
        close_dialog = driver.find_elements(by=By.CLASS_NAME, value='el-dialog__headerbtn')
        close_dialog = [cd for cd in close_dialog if cd.accessible_name == 'Close']
        if len(close_dialog) > 0:
            close_dialog[0].click()
        if before_jump is not None and before_jump == driver.current_url:
            refresh_count += 1
            print('refresh_count:', refresh_count)
            if refresh_count >= max_refresh:
                print('Job done.')
                break
        else:
            refresh_count = 0
        before_jump = driver.current_url
        driver.back()
    else:
        if items[i - 1].text.strip() in unfold_labels.keys():
            unfold_label = driver.find_element(by=By.ID, value=unfold_labels[items[i - 1].text.strip()])
            unfold_label.click()
            time.sleep(0.5)
        sub_page_entry = driver.find_element(by=By.ID, value=next_hop_id)
        if items[i - 1].text.strip() in unfold_labels.keys():
            driver.find_elements(by=By.CLASS_NAME, value='user-logo')[0].click()
            time.sleep(0.5)
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        results.append('ruijie' in soup.text.lower())
        viewed.append(next_hop_id)
        tabs = soup.find_all('div', class_='el-tabs__item is-top')
        for tab in tabs:
            driver.find_elements(
                by=By.ID,
                value=tab.attrs['id']
            )[0].click()
            time.sleep(5)
            html = driver.page_source
            soup = BeautifulSoup(html, "lxml")
            results.append('ruijie' in soup.text.lower())
            viewed.append(next_hop_id)
        if items[i - 1].text.strip() in unfold_labels.keys():
            unfold_label = driver.find_element(by=By.ID, value=unfold_labels[items[i - 1].text.strip()])
            unfold_label.click()
            time.sleep(0.5)
        try:
            sub_page_entry.click()
        except Exception as e:
            print(repr(e))
    time.sleep(1)
print('Done')
