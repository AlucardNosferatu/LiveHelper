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

drivers_ = []
status = []
htmls_list = []  # 建立网页信息存储列表


def crawl_source(worker_id, drivers, page=10, job_searched='工程师'):
    for num in range(1, page + 1, 1):
        d_index = num % len(drivers)
        if d_index == worker_id:
            url = "https://www.zhipin.com/web/geek/job?city=101230100&page={}".format(num)
            if job_searched is not None:
                url += '&query={}'.format(job_searched)
            print('Now crawling:', url)
            drivers[worker_id].get(url)  # 自动化运行页面
            time.sleep(10)
            page_source = drivers[d_index].page_source  # 获取页面信息

            htmls_list.append(str(page_source))  # 将获取页面信息添加至网页存储列表
            ran_time = random.randint(1, 5)  # 随机生成停顿时间
            time.sleep(ran_time)  # 程序休眠
    status[worker_id] = True


def fire_tasks(t_count=4, page=10, job_searched='后端工程师'):
    for i in range(t_count):
        drivers_.append(webdriver.Chrome())
        status.append(False)
    threads = []
    for i in range(len(drivers_)):
        threads.append(threading.Thread(target=crawl_source, args=(i, drivers_, page, job_searched)))
    for i in range(len(threads)):
        threads[i].start()
        time.sleep(1)
    while False in status:
        time.sleep(1)
    for driver in drivers_:
        driver.close()  # 关闭浏览器


def parse_html():
    most_popular_jobs = []  # 建立获取职位信息存储列表
    most_complex_jobs = []
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
            salary = list(list(job.children)[1].children)[0].text
            exp = list(list(list(job.children)[1].children)[1])[0].text
            edu = list(list(list(job.children)[1].children)[1])[3].text

            employer = list(list(list(job.children)[1])[2])[1].text
            trade = list(list(list(company.children)[1])[1])[0].text

            skills_list = [skill.text for skill in list(skills.children)]
            skills_list.insert(0, title)
            skills_list += [employer, trade]
            most_popular_jobs.append(skills_list)
            most_complex_jobs.append([title, salary, exp, edu])
    pickle.dump(most_popular_jobs, open('job_popular.pkl', 'wb'))
    pickle.dump(most_complex_jobs, open('job_complex.pkl', 'wb'))
    print('Done')


if __name__ == '__main__':
    fire_tasks(t_count=5, page=10, job_searched='运维工程师')
    parse_html()
