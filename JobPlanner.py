# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 23:10:22 2019

@author: Scrooge
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets.samples_generator import make_blobs
from sklearn.cluster import KMeans
# X为样本特征，Y为样本簇类别， 共1000个样本，每个样本2个特征，共4个簇，簇中心在[-1,-1], [0,0],[1,1], [2,2]， 簇方差分别为[0.4, 0.2, 0.2]
X, y = make_blobs(
        n_samples=1000,
        n_features=2,
        centers=[[-1,-1], [0,0], [1,1], [2,2]],
        cluster_std=[0.4, 0.2, 0.2, 0.2],
        random_state =9)

X_random=np.random.rand(1000,2)

f=open("D:\\XY.txt","r")
X_real=[[]]
temp=[]
line=f.readline()
line=line[:-1]
for each in line.split("#*#"):
                       temp.append(int(each))
X_real[0]=temp

while line:
    temp=[]
    line=f.readline()
    line=line[:-1]
    if(len(line)>0):
        for each in line.split("#*#"):
            temp.append(int(each))
        X_real.append(temp)
f.close()

for each in X_real:
    for params in each:
        print(params)
    print("\r")

X_real=np.array(X_real)

y_pred = KMeans(n_clusters=6, random_state=9).fit_predict(X_real)
plt.scatter(X_real[:, 0], X_real[:, 1], c=y_pred)
plt.show()