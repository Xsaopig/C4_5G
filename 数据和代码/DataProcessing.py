from datetime import datetime
import numpy as np
import functools
from queue import Queue
import operator
import random
from collections import defaultdict
import pandas as pd

def read_data(file_path):
    '''读取初始表数据，先转成csv格式'''
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
        low_memory=False,encoding="gbk")
    data = df.values
    return data

def getContextofLocs(data):
    '''返回：
    所有数据的clocationinfo信息列表locs
    反索引列表locToIndexOflocs
    loc对应的网元id、端口信息、定位信息列表locstoneid
    '''
    ## locs
    dataByloc = getdataByloc(data)
    locs=[key for key in dataByloc]
    print('共有'+str(len(locs))+'个定位点')
    
    ## locToIndexOflocs
    locToIndexOflocs = {}
    for i in range(len(locs)):
        locToIndexOflocs[locs[i]] = i

    ## locstoneid
    locstoneid={}
    for i in range(len(locs)):
        locstoneid[locs[i]]=[dataByloc[locs[i]][0][2],dataByloc[locs[i]][0][5],dataByloc[locs[i]][0][6]]
    return locs,locToIndexOflocs,locstoneid

def getdataByalarmcode(data):
    '''
    根据calarmcode划分数据
    '''
    dataByalarmcode={}
    for alarm in data:
        if dataByalarmcode.get(alarm[1])!=None:
            dataByalarmcode[alarm[1]].append(alarm)
        else:
            dataByalarmcode[alarm[1]]=[alarm]
    return dataByalarmcode

def getdataByloc(data):
    '''
    根据clocationinfo划分数据
    '''
    dataByloc={}
    for alarm in data:
        ele = alarm[5]
        if dataByloc.get(alarm[5])!=None:
            dataByloc[alarm[5]].append(alarm)
        else:
            dataByloc[alarm[5]]=[alarm]
    return dataByloc

def getdataByneid(data):
    '''
    根据cneid划分数据
    '''
    dataByneid={}
    for alarm in data:
        ele = alarm[2]
        if dataByneid.get(ele)!=None:
            dataByneid[ele].append(alarm)
        else:
            dataByneid[ele]=[alarm]
    return dataByneid

def getoccurtimelist(data):
    '''返回所有告警的告警时间列表'''
    timelist=[]
    for alarm in data:
        timelist.append(alarm[3])
    return timelist

def sortByoccurtime(data):
    '''
    根据告警发生时间排序
    '''
    # data.sort(key=lambda x : datetime.strptime(x[3],'%Y/%m/%d %H:%M'))
    data=sorted(data,key=lambda x : datetime.strptime(x[3],'%Y/%m/%d %H:%M'), reverse=False)
    return data

def sortBylogid(data):
    '''
    根据日志id排序
    '''
    data=sorted(data,key=lambda x : x[0], reverse=False)
    return data

def Datacleaninside(data,Max_Interval = 300):
    '''
    内部数据清洗，清理掉alarms中由同一告警引起的、时间上连续的告警数据
    '''
    dataByloc=getdataByloc(data)
    newdata=[]
    for loc in dataByloc:
        alarms=dataByloc[loc]
        alarmsByac = getdataByalarmcode(alarms)
        alarms.clear()
        for code in alarmsByac:
            alarmBysamecode=alarmsByac[code]
            alarmBysamecode=sortByoccurtime(alarmBysamecode)
            i = 0
            while i < len(alarmBysamecode):
                alarmcode_i = alarmBysamecode[i][1]
                occurtime_i = datetime.strptime(alarmBysamecode[i][3],'%Y/%m/%d %H:%M')
                j = i + 1
                while j < len(alarmBysamecode):
                    occurtime_j = datetime.strptime(alarmBysamecode[j][3],'%Y/%m/%d %H:%M')
                    occurtime_jsub1 = datetime.strptime(alarmBysamecode[j-1][3],'%Y/%m/%d %H:%M')
                    diff = occurtime_j - occurtime_jsub1
                    if diff.total_seconds() > Max_Interval:
                        break
                    else:
                        j += 1
                j -= 1
                while j > i:
                    del alarmBysamecode[j]
                    j -= 1
                i += 1
            alarms.extend(alarmBysamecode)
        newdata.extend(alarms)
    return newdata

def GenSeqs(data,Max_Interval):
    '''
    生成所有时间序列
    Max_Interval：判断一个告警是否属于上一个序列的最长间隔时间,单位秒，此参数越长，生成的时间序列越长
    Return: Seqs    如[[data[0],data[1]],data[2],...]
    '''
    data = sortByoccurtime(data)
    Seqs=[]
    i,curtime = 0,datetime.strptime('0001/1/1 00:00','%Y/%m/%d %H:%M')
    for i in range(len(data)):
        occurtime_i = datetime.strptime(data[i][3],'%Y/%m/%d %H:%M')
        diff = occurtime_i-curtime
        if diff.total_seconds()>Max_Interval:
            Seqs.append([[data[i]]]) 
        elif diff.total_seconds()<=Max_Interval:
            if diff.total_seconds()>0:
                Seqs[-1].append([data[i]])
            else:
                Seqs[-1][-1].append(data[i])
        curtime = occurtime_i
    return Seqs

def GenSeqs_2d(data,Max_Interval):
    '''
    生成所有时间序列
    Max_Interval：判断一个告警是否属于上一个序列的最长间隔时间,单位秒，此参数越长，生成的时间序列越长
    在时间上同时发生的告警按日志id排序
    Return: Seqs    如[data[0],data[1],data[2],...]
    '''
    Seqs = GenSeqs(data,Max_Interval)
    for i in range(len(Seqs)):
        tmp = []
        for j in range(len(Seqs[i])):
            if len(Seqs[i][j])>1:
                Seqs[i][j] = sortBylogid(Seqs[i][j])
                for k in Seqs[i][j]:
                    tmp.append(k)
                pass
            else:
                tmp.append(Seqs[i][j][0])
        Seqs[i]=tmp
    return Seqs

def GenSeqs_3d(data,Max_Interval):
    '''
    生成所有时间序列
    Max_Interval：判断一个告警是否属于上一个序列的最长间隔时间,单位秒，此参数越长，生成的时间序列越长
    在时间上同时发生的告警按日志id排序
    Return: Seqs    如[[data[0]],[data[1]],[data[2]],...]
    '''
    Seqs = GenSeqs_2d(data,Max_Interval)
    Seqs = Seqs_2dto3d(Seqs)
    return Seqs

def Seqs_2dto3d(Seqs):
    '''2d序列转3d序列'''
    for i in range(len(Seqs)):
        for j in range(len(Seqs[i])):
            Seqs[i][j] = [Seqs[i][j]]
    return Seqs

def Seqs_3dto2d(Seqs):
    '''3d序列转2d序列'''
    for i in range(len(Seqs)):
        for j in range(len(Seqs[i])):
            Seqs[i][j] = Seqs[i][j][0]
    return Seqs


def Seq_compression(seq):
    '''
    压缩序列
    a,b,b,b,b,c  =>    a,b,c
    '''
    i = 1
    while(i < len(seq)):
        if operator.eq(seq[i],seq[i-1]):
            del seq[i]
        else:
            i += 1
    return seq

def Seqs_dim_reduction(Seqs):
    '''
    输入：三维序列库（每个序列由若干项目集组成，项目集之间有时间先后关系；项目集内的项目间无时间先后关系）
    [  [[a,b],[c],[d]],  [[a],[d]]      ]                            
    ---------------------------
    输出：二维序列库（每个序列由项目组成，每个项目之间有时间先后关系）
    [   [a,c,d],[b,c,d],    [a,d]       ]
    PS:执行时间随序列的项目集大小、长度指数级增长
    '''
    def SeqtoSeqs(seq):
        #估计产生的序列数
        estimate = 1
        for items in seq:
            estimate *= len(items)
        #为了加速产生序列，会对预计产生超大序列库的序列进行二分
        if estimate >= 100000:
            x = len(seq)
            return SeqtoSeqs(seq[:int(x/2)])+SeqtoSeqs(seq[int(x/2):])
            # return SeqtoSeqs(seq[int(x/2):])
        res = []
        que = Queue()
        que.put(seq)
        while que.empty()==False:
            s = que.get()
            flag = True
            for i,items in enumerate(s):
                if len(items)>1:
                    flag = False
                    for item in items:
                        que.put(s[:i]+[[item]]+s[i+1:])
                    break
            if flag == True:
                 res.append(list(map(lambda x:x[0],s)))
        return res
    res = []
    for i,Seq in enumerate(Seqs):
        res += SeqtoSeqs(Seq)
        if i%100 == 0 :
            print(f'生成二维序列库中：{i+1}/{len(Seqs)}',end='\r')
    res = [list(x) for x in list(set([tuple(x) for x in res]))]
    return res

def data_split(data,num_test):
    '''
    从data中均匀分布地、随机拆出num_test条测试集，其余的作为训练集
    返回: train,test
    '''
    test,train = [],[]
    x = len(data)
    if num_test>=x: return [],data
    cylce = int(x/num_test)
    remainder = x%num_test
    i = 0
    while(i < x-remainder):
        pos = random.randint(i,i+cylce-1)
        test.append(data[pos])
        train += data[i:pos] + data[pos+1:i+cylce]
        i+=cylce
    train += data[i:]
    return train,test

def Genitemsets(data):
    '''
    按告警时间生成所有项目集合
    '''
    timeToitemsets = defaultdict(list)
    for i in range(len(data)):
        timeToitemsets[data[i][3]].append(data[i])
    return list(timeToitemsets.values())

def Datacluster(data,eps=0.001,min_samples=1):
    '''
    同一网元的告警数据按告警时间聚类，使用DBSCAN算法进行聚类，结果中每类取时间最早的那一个告警数据
    '''
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    dataByloc=getdataByloc(data)
    newdata=[]
    for loc in dataByloc:
        alarms=dataByloc[loc]
        alarmsByac = getdataByalarmcode(alarms)
        for code in alarmsByac:
            alarmBysamecode=alarmsByac[code]
            alarmBysamecode=sortByoccurtime(alarmBysamecode)
            X=[[datetime.strptime(i[3],'%Y/%m/%d %H:%M')] for i in alarmBysamecode]
            X = pd.DataFrame(X)
            scaler = StandardScaler()
            X = scaler.fit_transform(X)
            db = DBSCAN(eps=eps, min_samples=min_samples)
            db.fit(X)
            labelTodata = defaultdict(list)
            # labelTomaxdiff = defaultdict(int)
            for i in range(len(db.labels_)):
                labelTodata[db.labels_[i]].append(alarmBysamecode[i])
                # labelTomaxdiff[db.labels_[i]] = datetime.strptime(labelTodata[db.labels_[i]][-1][3],'%Y/%m/%d %H:%M') - datetime.strptime(labelTodata[db.labels_[i]][0][3],'%Y/%m/%d %H:%M')
                # labelTomaxdiff[db.labels_[i]] = labelTomaxdiff[db.labels_[i]].total_seconds()
            for label in labelTodata:
                newdata.append(labelTodata[label][0])
            pass
    return newdata

if __name__ == '__main__':
    file_path = 'C:\\Users\\xsaopig\\Desktop\\5G承载网项目\\5G承载网故障检测数据\\Data\\t_alarmloghist_1_1.csv'
    data = read_data(file_path)
    print('数据内部清洗前长度为',len(data))
    data = Datacluster(data)
    print('数据内部清洗后长度为',len(data))