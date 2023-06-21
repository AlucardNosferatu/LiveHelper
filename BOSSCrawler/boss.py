import random
import re
import time

# BeautifulSoup用于处理获取的网页数据
import pandas as pd
# 导入正则表达式，绘图，时间，随机模块
from bs4 import BeautifulSoup
# 数据分析必备类库
# 绘图模块
from selenium import webdriver

# 自动化控制浏览器模块

job = "数据分析"  # 设置需要爬取的职业信息
page = 3  # 设置爬取页数
htmls_list = []  # 建立网页信息存储列表
for num in range(1, page, 1):
    url = "https://www.zhipin.com/c101010100/?query={}&page=1&ka=page-{}".format(job, num)
    driver = webdriver.Chrome()  # 初始化webdriver
    driver.get(url)  # 自动化运行页面
    htmls = driver.page_source  # 获取页面信息
    htmls_list.append(str(htmls))  # 将获取页面信息添加至网页存储列表
    driver.close()  # 关闭浏览器
    ran_time = random.randint(1, 5)  # 随机生成停顿时间
    time.sleep(ran_time)  # 程序休眠

info_list = []  # 建立获取职位信息存储列表
soup = None
for htmls in htmls_list:
    soup = BeautifulSoup(htmls, parser="lxml")  # 解析网页
    for i in soup.find_all("div", class_="job-primary"):
        job = i.find_all("a")  # 获取招聘岗位信息
        area = i.find_all('span', class_='job-area')  # 获取工作地点
        salary = i.find_all('span', class_='red')  # 获取薪酬信息
        title = i.find_all("h3")[1].get_text()  # 获取企业名称
        industry = i.find_all('a', class_="false-link")[0].get_text()  # 获取所属行业
        edu = i.find_all('p')[0].text  # 获取学历要求
        scale = i.find_all('p')[1].text  # 获取条件信息
        url = "https://www.zhipin.com/" + i.find_all("div", class_="primary-box")[0]['href']  # 获取详情页信息
        # 将所有信息保存至列
        info_list.append([title, industry, job[0]['title'], area[0].get_text(), edu, scale, salary[0].get_text(), url])
        data = pd.DataFrame(info_list,
                            columns=['企业名称', '所属行业', '招聘岗位', '工作地点', '条件', '企业信息', '薪资', 'URL'])
        # 将所有内容保存为DataFrame格式。
        data = data.drop_duplicates(subset='企业名称', keep='first')
        # 将数据按照招聘企业去重处理
        data['max_salary'] = data['薪资'].map(lambda x: re.findall(r"-(\d.*?)K", x)[0])
        data['max_salary'] = data['max_salary'].astype(int) * 1000
        # 通过正则表达式获取薪资的最大值，并整理为数值型

        data['min_salary'] = data['薪资'].map(lambda x: re.findall(r"(\d.*?)-", x)[0])
        data['min_salary'] = data['min_salary'].astype(int) * 1000
        # 通过正则表达式获取薪资的最小值，并整理为数值型

        data.head()
        # 看一下数据的基本情况
