import pickle

import jieba
import nltk

data = pickle.load(open('BOSSCrawler/job_info.pkl', 'rb'))
data = [jieba.lcut(' '.join(info)) for info in data]
data = [[info_.lower() for info_ in info if len(info_.strip()) > 1] for info in data]
all_word = []
for info in data:
    all_word += info
blacklist = [
    '工程师', '开发', '实施', 'cad', '专业', '经验', 'bim', '计算机相关', '设备', '电气工程师', '工艺', '算法', '技术',
    'python', 'solidworks', '五险', 'proe', '射频', '相关', '工程', '设计'
]
all_word = [word for word in all_word if word not in blacklist]
freq_dist = nltk.FreqDist(all_word)
top_k = freq_dist.most_common(20)
pickle.dump(top_k, open('BOSSCrawler/top_k.pkl', 'wb'))
print('Done')
