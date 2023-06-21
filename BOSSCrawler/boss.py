import pickle
import random
import threading
import time

# BeautifulSoup用于处理获取的网页数据
# 导入正则表达式，绘图，时间，随机模块
from bs4 import BeautifulSoup
# 数据分析必备类库
# 绘图模块
from selenium import webdriver
from tqdm import tqdm

# 自动化控制浏览器模块

job = '工程师'  # 设置需要爬取的职业信息
page = 100  # 设置爬取页数
htmls_list = []  # 建立网页信息存储列表
drivers_ = []
status = []
for i in range(8):
    drivers_.append(webdriver.Chrome())
    status.append(False)


def crawl_source(worker_id, drivers):
    for num in range(1, page + 1, 1):
        d_index = num % len(drivers)
        if d_index == worker_id:
            url = "https://www.zhipin.com/web/geek/job?city=101230100&page={}".format(num)
            if job is not None:
                url += '&query={}'.format(job)
            print('Now crawling:', url)
            drivers[worker_id].get(url)  # 自动化运行页面
            time.sleep(10)
            page_source = drivers[d_index].page_source  # 获取页面信息

            htmls_list.append(str(page_source))  # 将获取页面信息添加至网页存储列表
            ran_time = random.randint(1, 5)  # 随机生成停顿时间
            time.sleep(ran_time)  # 程序休眠
    status[worker_id] = True


threads = []
for i in range(len(drivers_)):
    threads.append(threading.Thread(target=crawl_source, args=(i, drivers_)))
for i in range(len(threads)):
    threads[i].start()
while False in status:
    time.sleep(1)
for driver in drivers_:
    driver.close()  # 关闭浏览器

info_list = []  # 建立获取职位信息存储列表
soup = None
for htmls in tqdm(htmls_list):
    soup = BeautifulSoup(htmls, "lxml")  # 解析网页
    job_list = soup.find_all("li", class_="job-card-wrapper")
    for i in job_list:
        body = list(i.children)[0]
        footer = list(i.children)[1]
        job = list(body.children)[0]  # 获取招聘岗位信息
        company = list(body.children)[1]
        skills = list(footer.children)[0]
        title = list(list(job.children)[0].children)[0].text
        skills_list = [skill.text for skill in list(skills.children)]
        skills_list.insert(0, title)
        info_list.append(skills_list)
pickle.dump(info_list, open('job_info.pkl', 'wb'))
print('Done')
