import pickle

import jieba
import nltk

data = pickle.load(open('BOSSCrawler/job_info.pkl', 'rb'))
data = [jieba.lcut(' '.join(info)) for info in data]
data = [[info_ for info_ in info if len(info_.strip()) > 1] for info in data]
all_word = []
for info in data:
    all_word += info
blacklist = ['工程师']
all_word = [word for word in all_word if word not in blacklist]
freq_dist = nltk.FreqDist(all_word)
top10 = freq_dist.most_common(10)
pickle.dump(top10, open('BOSSCrawler/top10.pkl', 'wb'))
print('Done')
