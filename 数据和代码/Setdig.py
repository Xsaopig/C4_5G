import pandas as pd
import DataProcessing as dp
import numpy as np
from spmf.mining import *
from CPT import *

file_path = 'C:\\Users\\xsaopig\\Desktop\\5G承载网项目\\5G承载网故障检测数据\\Data\\t_alarmloghist_1_1.csv'
output_path = '.\\output\\output.csv'
output_freqitems_path = '.\\output\\freqitems.csv'
output_assorules_path = '.\\output\\assorules.csv'


if __name__ == '__main__':
    data = dp.read_data(file_path)
    print('数据内部清洗前长度为',len(data))
    data = dp.Datacleaninside(data,300)
    print('数据内部清洗后长度为',len(data))

    ## locs,locToIndexOflocs,locstoneid
    locs,locToIndexOflocs,locstoneid = dp.getContextofLocs(data)

    ################################
    ###########频繁项集#############
    ################################

    ## 按告警时间生成所有项目集
    Itemsets = dp.Genitemsets(data)
    for i in range(len(Itemsets)):
        Itemsets[i] = list(set([locToIndexOflocs[x[5]] for x in Itemsets[i]])) # 项集中的项为 设备定位信息

    ## 频繁项集挖掘
    freqItemsets = Mining_FreItemsets(Itemsets,minsp=10.0/len(Itemsets),minpatternlen=1,maxpatternlen=100)
    # 保存挖掘出的频繁项集
    column_Itemsets = pd.Series([x[0] for x in freqItemsets],name='Itemsets')
    column_Itemsets_detailed = pd.Series([[locstoneid[locs[idxoflocs]] for idxoflocs in x[0]] for x in freqItemsets],name='Itemsets_detailed')
    column_sup = pd.Series([x[1] for x in freqItemsets],name='sup')
    con = pd.concat([column_Itemsets,column_Itemsets_detailed, column_sup],axis=1)
    con.to_csv(output_freqitems_path,index = True,sep=',',mode='w+',encoding='utf_8_sig')

    ## 关联规则挖掘
    AssociationRules = Mining_associationrules(Itemsets,30.0/len(Itemsets),minconf=0.5,max_antecedent_len=10,max_consequent_len=10)
    # 保存挖掘出的关联规则
    column_antecedent = pd.Series([x[0] for x in AssociationRules],name='antecedent')
    column_antecedent_detailed = pd.Series([[locstoneid[locs[idxoflocs]] for idxoflocs in x[0]] for x in AssociationRules],name='antecedent_detailed')
    column_consequent = pd.Series([x[1] for x in AssociationRules],name='consequent')
    column_consequent_detailed = pd.Series([[locstoneid[locs[idxoflocs]] for idxoflocs in x[1]] for x in AssociationRules],name='consequent_detailed')
    column_sup = pd.Series([x[2] for x in AssociationRules],name='sup')
    column_conf = pd.Series([x[3] for x in AssociationRules],name='conf')
    con = pd.concat([column_antecedent,column_antecedent_detailed, column_consequent,column_consequent_detailed, column_sup, column_conf],axis=1)
    con.to_csv(output_assorules_path,index = True,sep=',',mode='w+',encoding='utf_8_sig')


    
    


    
