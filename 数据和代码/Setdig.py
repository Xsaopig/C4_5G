import pandas as pd
import DataProcessing as dp
import numpy as np
import Count
from DSU import UnionFind
import csv

file_path = 'C:\\Users\\xsaopig\\Desktop\\5G承载网项目\\5G承载网故障检测数据\\Data\\Shangrao.csv'
output_sets_path = 'output_sets.csv'
output_neidtoloc_path = 'neidtoloc.csv'
df = pd.read_csv(  \
        file_path,usecols = [0,6,8,16,18,21,22],  \
        dtype={ \
            'clogid':int,  \
            'calarmcode':int,   \
            'cneid':int,     \
            'coccuructime':object , \
            'ccleaructime':object , \
            'clocationinfo':object, \
            'clinport':object  \
        },  \
        low_memory=False)
# print(df.info())
data = df.values

def is_correlation(m1_hour_set, m2_hour_set):
    s1 = set(m1_hour_set)
    s2 = set(m2_hour_set)
    # print(len(s1), " ", len(s2))
    if len(s1) == 0 or len(s2) == 0:
        return 0
    res = set(set(m1_hour_set) & set(m2_hour_set))
    total = len((s1 - res) | s2)
    lift = (len(res) / total) / ((len(s1) / total) * (len(s2) / total))
    # print("lift is :", end=" ")
    # print(lift)
    if lift >= 1:
        return 1
    else:
        return 0
    
def relation_correlation(m1_min_set, m2_min_set):
    s1 = set(m1_min_set)
    s2 = set(m2_min_set)
    res = set(s1 & s2)
    total = len((s1 - res) | s2)
    support = len(res) / total
    confidence1 = float(len(res) / len(s1))
    confidence2 = float(len(res) / len(s2))
    # print("support is ", support)
    # print("c1 is ", confidence1)
    # print("c2 is ", confidence2)
    if support < 0.3:
        return 0
    if confidence1 < 0.7 and confidence2 < 0.7:
        return 0
    elif confidence1 >= 0.7 and confidence2 >= 0.7:
        return 1
    elif confidence1 >= 0.7 and confidence2 < 0.7:
        return 2
    else:
        return 3

def getoccurtimelist(data):
    timelist=[]
    for alarm in data:
        timelist.append(alarm[3])
    return timelist




if __name__ == '__main__':
    print('数据内部清洗前长度为',len(data))
    dataCleaned = dp.Datacleaninside(data)
    print('数据内部清洗后长度为',len(dataCleaned))
    dataByloc = dp.getdataByloc(dataCleaned)

    # 删除只发生一次的告警
    # cnt = 0
    # for key in list(dataByloc.keys()):
    #     if len(dataByloc[key]) <= 1:
    #         del dataByloc[key]
    #     else:
    #         cnt += len(dataByloc[key])
    # print('删除偶然事件后长度为',cnt)

    # 统计各端口告警次数并绘图
    # Count.CountAlarms(data,500)

    # 统计每种告警发生次数
    # Count.CountAlarmsByAlarmcode(data,100)

    ################################
    ###########关联分析#############
    ################################
    locs=[key for key in dataByloc]
    print('共有'+str(len(locs))+'个定位点')
    
    # 输出所有定位信息
    # fp=open('locs.txt',mode='w',encoding='utf-8')
    # for loc in locs:
    #     fp.write(loc+'\n')
    # fp.close()

    uf = UnionFind(len(locs)) #定义并查集

    relation_cnt=0
    # 判断两个loc之间是否有关联
    timelist=[]
    locstoneid={}
    for i in range(len(locs)):
        timelist.append(getoccurtimelist(dataByloc[locs[i]]))
        locstoneid[locs[i]]=[dataByloc[locs[i]][0][2],dataByloc[locs[i]][0][5],dataByloc[locs[i]][0][6]]

    # 写neid_loc_port表
    # with open(output_neidtoloc_path,"a") as csvfile: 
    #     writer = csv.writer(csvfile)
    #     for set in sets:
    #         for i in set:
    #             writer.writerow(locstoneid[locs[i]])

    for i in range(len(locs)):
        for j in range(len(locs)):
            if j==i : continue
            if  is_correlation(timelist[i],timelist[j]) and relation_correlation(timelist[i], timelist[j])==1 :
                # print(locs[i]+"  <->  " + locs[j])
                uf.union(i,j)
                relation_cnt+=1
            # elif (locstoneid[locs[i]][0]==locstoneid[locs[j]][0]):
            #     # print(locs[i]+"  <->  " + locs[j])
            #     uf.union(i,j)
            #     relation_cnt+=1
    print("两两关联数量为",relation_cnt)

    # 并查集进行聚类
    sets = uf.groups_big() 
    print(len(sets))
    print(sets)

    # with open(output_sets_path,"w",newline='') as csvfile: 
    #     writer = csv.writer(csvfile)
    #     for set in sets:
    #         l = [locs[i] for i in set]
    #         neids = [locstoneid[loc][0] for loc in l]
    #         ports = [locstoneid[loc][2] for loc in l]
    #         l.insert(0,'集合元素')
    #         neids.insert(0,'设备id')
    #         ports.insert(0,'对应端口')
    #         writer.writerow(l)
    #         writer.writerow(neids)
    #         writer.writerow(ports)
    #         writer.writerow([])


    

        
    


    
