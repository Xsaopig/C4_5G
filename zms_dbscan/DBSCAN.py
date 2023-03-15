# -*- coding: utf-8 -*-
# @Time : 2023/3/13 13:48
# @Author : Zhangmiaosong
# 使用DBSCAN进行数据聚类
from datetime import datetime

from sklearn.cluster import DBSCAN
import pandas as pd
import datetime as dt

from sklearn.preprocessing import StandardScaler

read_path = 'C:\\Users\\u2020\\Desktop\\C4_5G\\数据和代码\\t_alarmlogcur.csv'

file_path = 'C:\\Users\\u2020\\Desktop\\C4_5G\\数据和代码\\t_alarmlogcur.xlsx'
output_path = '.\\output.csv'
#读取数据

#
if __name__ == '__main__':
    data = pd.read_excel(file_path)

    # 将时间转化为时间戳
    data[" coccurutctime"] = data[" coccurutctime"].apply(lambda x: x.timestamp())

    # 对数据进行标准化
    scaler = StandardScaler()
    X = scaler.fit_transform(data[["cneid", "calarmcode", " coccurutctime"]])
    data[" coccurutctime"] =  pd.to_datetime(data[" coccurutctime"], unit='s')
    # 使用DBSCAN算法聚类数据
    db = DBSCAN(eps=0.001, min_samples=1)
    db.fit(X)
    print(db.labels_)
    #参数，聚类半径（如果是按照告警时间进行聚类的话那就是时间差，多种类的欧式距离）为10，最小样本数量为1
    data["result"] = db.labels_  # 在数据集最后一列加上经过DBSCAN聚类后的结果
    data.sort_values('result')
    data.to_csv(output_path)
