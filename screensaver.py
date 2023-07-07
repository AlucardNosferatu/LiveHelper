import time

from selenium import webdriver
from selenium.webdriver import ActionChains

driver = webdriver.Chrome()
action_chains = ActionChains(driver)
url = 'https://pan.ruijie.com.cn/share/9991571a1f3f111ae858a04b3e?isCurrent=1&isopen=1&page_number=1&preview=275019366758&preview_side_active=1&redirect=%2Fshare%2F9991571a1f3f111ae858a04b3e%3Fpage_number%3D1&scenario=share'
driver.get(url)
input('fuck you')
page_count = 28
for i in range(page_count):
    i_str = str(i)
    while len(i_str) < len(str(page_count)):
        i_str = '0' + i_str
    driver.save_screenshot('ss_{}.png'.format(i_str))
    page = driver.find_elements(by='id', value='share')[0]
    action_chains.click(on_element=page).perform()
    time.sleep(0.1)
print('fuck you, too')
