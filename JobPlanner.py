import pickle

import jieba
import nltk


def get_job_popular():
    blacklist = [
        '工程师', '开发', '实施', 'cad', '专业', '经验', 'bim', '计算机相关', '设备', '电气工程师', '工艺', '算法',
        '技术', 'python', 'solidworks', '五险', 'proe', '射频', '相关', '工程', '设计', '机械', '电气', '经理', '人事',
        '招聘者', '专员', '主管', '招聘', 'hr', '计算机软件', '智慧', '智能', '互联网', '项目', '售前', '销售', '服务',
        '质量', '工业', '管理', '电子商务', '人事主管', '环保', '仪器仪表', '电子', '检测', '半导体', '集成电路',
        '配置', '总监', '其他', '加工', '自动化', '测试', '硬件'
    ]
    data = pickle.load(open('BOSSCrawler/job_popular.pkl', 'rb'))
    data = [jieba.lcut(' '.join(info)) for info in data]
    data = [[info_.lower() for info_ in info if len(info_.strip()) > 1] for info in data]
    all_word = []
    for info in data:
        all_word += info
    all_word = [word for word in all_word if word not in blacklist]
    freq_dist = nltk.FreqDist(all_word)
    top_k = freq_dist.most_common(20)
    pickle.dump(top_k, open('BOSSCrawler/top_k_popular.pkl', 'wb'))
    print('Done')


def get_job_complex():
    def parse_title(title_):
        count = 0
        title_keyword = ['高级', '资深']
        for keyword in title_keyword:
            if keyword in title_:
                count += 1
        return count / len(title_keyword)

    def parse_salary(salary_):
        threshold = 20.0 * 12
        if 'K' in salary_:
            month_count = 12
            if '薪' in salary_:
                month_count = int(salary_.split('·')[1].replace('薪', ''))
            s_per_m = salary_.split('K')[0].split('-')
            s_per_m = (float(s_per_m[0]) + float(s_per_m[1])) / 2
            s = s_per_m * month_count
            return min(1.0, s / threshold)
        else:
            return 0.0

    def parse_exp(exp_):
        threshold = 10
        if '年' in exp_:
            if '以内' in exp_:
                return 0.5 / threshold
            elif '以上' in exp_:
                return 1.0
            else:
                exp_ = exp_.replace('年', '').split('-')
                exp_ = (float(exp_[0]) + float(exp_[1])) / 2
                return min(1.0, exp_ / threshold)
        else:
            return 0.0

    def parse_edu(edu_):
        edu_list = ['学历不限', '初中及以下', '中专/中技', '高中', '大专', '本科', '硕士', '博士']
        return edu_list.index(edu_) / (len(edu_list) - 1)

    blacklist = []
    top_k = []
    k = 5
    data = pickle.load(open('BOSSCrawler/job_complex.pkl', 'rb'))
    detail = pickle.load(open('BOSSCrawler/job_popular.pkl', 'rb'))
    for i in range(len(data)):
        job = data[i]
        title = job[0]
        title_list = jieba.lcut(title)
        process_this = True
        for title_word in title_list:
            if title_word in blacklist:
                process_this = False
                break
        if process_this:
            title_score = parse_title(title)
            salary = job[1]
            salary_score = parse_salary(salary)
            exp = job[2]
            exp_score = parse_exp(exp)
            edu = job[3]
            edu_score = parse_edu(edu)
            total_score = title_score + salary_score + exp_score + edu_score
            data[i] += [total_score, title_score, salary_score, exp_score, edu_score, i]
        else:
            total_score = -4.0
            data[i] += [total_score, -1.0, -1.0, -1.0, -1.0, i]
        inserted = False
        for j in range(len(top_k)):
            if data[i][4] <= top_k[j][4]:
                top_k.insert(j, data[i])
                inserted = True
                break
        if not inserted:
            top_k.append(data[i])
        if len(top_k) > k:
            top_k.pop(0)
    for i in range(len(top_k)):
        index = top_k[i][-1]
        extra_info = detail[index]
        top_k[i].append(extra_info)
    pickle.dump(top_k, open('BOSSCrawler/top_k_complex.pkl', 'wb'))
    print('Done')


if __name__ == '__main__':
    get_job_popular()
    get_job_complex()
