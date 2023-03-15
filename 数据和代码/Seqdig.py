import pandas as pd
import DataProcessing as dp
import numpy as np
import csv
from spmf.mining import *
from CPT import *
import operator
file_path = 'C:\\Users\\xsaopig\\Desktop\\5G承载网项目\\5G承载网故障检测数据\\Data\\t_alarmloghist_1_1.csv'
output_path = '.\\output\\predict_rusult.csv'
output_freseqs_path = '.\\output\\freseq.csv'
output_seqrules_path = '.\\output\\seqrules.csv'


if __name__ == '__main__':
    data = dp.read_data(file_path)
    print('数据内部清洗前长度为',len(data))
    # data = dp.Datacleaninside(data,300)
    # print('数据内部清洗后长度为',len(data))
    data = dp.Datacluster(data,eps=0.0005)
    print('数据按告警时间后长度为',len(data))

    ## locs,locToIndexOflocs,locstoneid
    locs,locToIndexOflocs,locstoneid = dp.getContextofLocs(data)

    ################################
    ###########频繁序列#############
    ################################


    ## 生成所有时间序列
    Seqs = dp.GenSeqs(data,500)
    print('共有'+str(len(Seqs))+'个序列')
    # 对序列进行字符串化,去除序列中每个项目集的重复项
    for i in range(len(Seqs)):
        for j in range(len(Seqs[i])):
            # Seqs[i][j] = list(set(map(lambda x,y:str(x)+'-'+str(y),[locToIndexOflocs[x[5]] for x in Seqs[i][j]],[x[1] for x in Seqs[i][j]]))) # 序列中项集中的项为 设备定位信息+告警代码
            # Seqs[i][j] = list(set(map(lambda x:str(x),[x[1] for x in Seqs[i][j]])))  # 序列中项集中的项为告警代码
            Seqs[i][j] = list(set(map(lambda x:x,[locToIndexOflocs[x[5]] for x in Seqs[i][j]])))  # 序列中项集中的项为设备定位信息
        Seqs[i] = dp.Seq_compression(Seqs[i])
    # 按序列长度排个序
    Seqs = sorted(Seqs,key = lambda x: len(x))
    maxseqlen = max([len(Seq) for Seq in Seqs])
    print(f'最长序列长度为{maxseqlen}')


    ## 频繁序列挖掘 SPAM
    freqSeqs = Mining_FreSeqPatterns(Seqs,minsp=3.0/len(Seqs),minpatternlen=2,maxpatternlen=10,maxgap=100)
    freqSeqs = sorted(freqSeqs,key = lambda x: x[-1])
    # 保存挖掘出的频繁序列
    column_Seq = pd.Series([x[0] for x in freqSeqs],name='Seq')
    column_Seq_detailed = pd.Series([[[locstoneid[locs[int(item)]] for item in items] for items in x[0]] for x in freqSeqs],name='Seq_detailed') #具体点的
    column_sup = pd.Series([x[1] for x in freqSeqs],name='sup')
    con = pd.concat([column_Seq,column_Seq_detailed,column_sup],axis=1)
    con.to_csv(output_freseqs_path,index = True,sep=',',mode='w+',encoding='utf_8_sig')

    
    # ## 序列规则挖掘 RuleGrowth
    # Seqrules = Mining_Seqrules(Seqs,minsp=10.0/len(Seqs),minconf=0.3,max_antecedent_len=10,max_consequent_len=10)
    # # 保存挖掘出的序列规则
    # column_antecedent = pd.Series([x[0] for x in Seqrules],name='antecedent')
    # column_antecedent_detailed = pd.Series([[locstoneid[locs[idx]] for idx in x[0]] for x in Seqrules],name='antecedent_detatiled')
    # column_consequent = pd.Series([x[1] for x in Seqrules],name='consequent')
    # column_consequent_detailed = pd.Series([[locstoneid[locs[idx]] for idx in x[1]] for x in Seqrules],name='consequent_detailed')
    # column_sup = pd.Series([x[2] for x in Seqrules],name='sup')
    # column_conf = pd.Series([x[3] for x in Seqrules],name='conf')
    # con = pd.concat([column_antecedent, column_antecedent_detailed, column_consequent, column_consequent_detailed, column_sup, column_conf],axis=1)
    # con.to_csv(output_seqrules_path,index = True,sep=',',mode='w+',encoding='utf_8_sig')
    
    

    ## 序列预测 CPT
    Seqs = dp.Seqs_dim_reduction(Seqs)
    # 筛掉只有长度为1的序列（长度都为1了还预测个啥QAQ）
    print(f'共生成{len(Seqs)}条序列')
    Seqs = [seq for seq in Seqs if len(seq)>1]
    print(f'筛掉只有长度为1的序列后，还有{len(Seqs)}条序列')
    model = CPT()
    # 划分一下数据集
    train,test = dp.data_split(Seqs,10000)
    train = Seqs
    # train = Seqs[:-10000]
    # test = Seqs[-10000:]
    truth = [[x[-1]] for x in test]
    test = [x[:-1] for x in test]
    model.train(train)
    # 开始预测
    p = model.predict(train,test,5,1)
    right,wrong = 0, 0
    for i in range(len(p)):
        if operator.eq(p[i],truth[i]):
            right+=1
        elif len(p[i])!=0:
            wrong+=1
        
    print(f'right = {right}/{right+wrong}, wrong = {wrong}/{right+wrong}')
    print(f'有{len(test)-right-wrong}条序列未作出预测')
    #保存一下预测结果
    column_test = pd.Series(test,name='Test')
    column_predict = pd.Series(p,name='Predict')
    column_real = pd.Series(truth,name='Real')
    con = pd.concat([column_test,column_predict,column_real],axis=1)
    con.to_csv(output_path,index = True,sep=',',mode='w+')


    
