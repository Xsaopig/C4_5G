import pandas as pd
import DataProcessing as dp
import numpy as np
import csv
from spmf.mining import *

file_path = 'C:\\Users\\xsaopig\\Desktop\\5G承载网项目\\5G承载网故障检测数据\\Data\\t_alarmloghist_1_1.csv'
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


if __name__ == '__main__':
    print('数据内部清洗前长度为',len(data))
    data = dp.Datacleaninside(data,300)
    print('数据内部清洗后长度为',len(data))
    dataByloc = dp.getdataByloc(data)

    ################################
    ###########频繁序列#############
    ################################


    ## locs
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

    # 生成所有时间序列
    Seqs = dp.GenSeqs(data,300)
    print('共有'+str(len(Seqs))+'个序列')
    # 对序列进行字符串化,去除序列中每个项目集的重复项
    maxseqlen = 0
    for i in range(len(Seqs)):
        for j in range(len(Seqs[i])):
            Seqs[i][j] = list(set(map(lambda x,y:str(x)+'-'+str(y),[locToIndexOflocs[x[5]] for x in Seqs[i][j]],[x[1] for x in Seqs[i][j]]))) # 序列中项集中的项为 设备定位信息+告警代码
            # Seqs[i][j] = list(set(map(lambda x:str(x),[x[1] for x in Seqs[i][j]])))  # 序列中项集中的项为告警代码
            # Seqs[i][j] = list(set(map(lambda x:str(x),[locToIndexOflocs[x[5]] for x in Seqs[i][j]])))  # 序列中项集中的项为设备定位信息
        Seqs[i] = dp.Seq_compression(Seqs[i])
        maxseqlen = max(maxseqlen,len(Seqs[i]))
    print(f'最长序列长度为{maxseqlen}')

    Seqs = sorted(Seqs,key = lambda x: len(x))


    # 频繁序列挖掘 SPAM
    # freqSeqs = Mining_FreSeqPatterns(Seqs,minsp=20.0/len(Seqs),minpatternlen=2,maxpatternlen=10,maxgap=100)
    # freqSeqs = sorted(freqSeqs,key = lambda x: x[-1])
    # # for seq in freqSeqs:
    # #     print(seq[:-1],'sup=',seq[-1])
    # with open('freqseqs.txt','w+',encoding='utf-8') as fp:
    #     for line in freqSeqs:
    #         sup = line[1]
    #         seq = line[0]
    #         for i in range(len(seq)):
    #             for j in range(len(seq[i])):
    #                 seq[i][j] = seq[i][j].split('-')
    #                 seq[i][j][0] = locs[int(seq[i][j][0])]
    #         line = f"sup = {sup} : {seq}\n"
    #         fp.write(line)
    # fp.close()

    
    # 序列规则挖掘 RuleGrowth
    Seqrules = Mining_Seqrules(Seqs,minsp=10.0/len(Seqs),minconf=0.5,min_antecedent_len=10,max_consequent_len=10)
    for rule in Seqrules:
        print(rule[0],'==>',rule[1],'sup=',rule[2],'conf=',rule[3])
    
    # 序列预测 CPT
    # Seqs = dp.Seqs_dim_reduction(Seqs)
    # print(Seqs)



    
