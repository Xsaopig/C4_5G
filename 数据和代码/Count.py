import matplotlib.pyplot as plt
import seaborn as sns
import DataProcessing as dp
import numpy as np

#统计设备告警次数cnt，并统计告警频繁设备的各端口告警次数(只显示次数大于cnt/10的端口)
def CountAlarms(data,min_times):
    dataByneid = dp.getdataByneid(data)
    cnt = []
    for key in dataByneid:
        cnt.append([str(key),len(dataByneid[key])])
    cnt.sort(key = lambda x:x[1],reverse = True)
    namelist = []
    numlist = []
    for i in cnt:
        if i[1] >= min_times:
            namelist.append(i[0])
            numlist.append(i[1])

    sns.set_style({'font.sans-serif':['simhei','Arial']})
    plt.bar(x = np.arange(len(namelist)), height = numlist, tick_label = namelist)
    plt.xticks(rotation=270)
    plt.ylabel("告警计数/次(不小于"+str(min_times)+")")
    plt.xlabel("cneid")
    plt.savefig('C:\\Users\\xsaopig\\Desktop\\5G承载网项目\\5G承载网故障检测数据\\Data\\picture\\CountAlarms.png', bbox_inches='tight')
    # plt.show()

    # 统计具体设备的端口告警次数
    for i in range(len(namelist)):
        name=namelist[i]
        databyneidAndloc = dp.getdataByloc(dataByneid[int(name)])
        cnt = []
        for key in databyneidAndloc:
            cnt.append([str(key),len(databyneidAndloc[key])])
        cnt.sort(key = lambda x:x[1],reverse = True)
        x = []
        y = []
        for j in cnt:
            x.append(j[0])
            y.append(j[1])
        plt.clf()
        sns.set_style({'font.sans-serif':['simhei','Arial']})
        plt.bar(x = np.arange(len(x)), height = y, tick_label = x)
        plt.xticks(rotation=270)
        plt.ylabel("告警计数/次")
        plt.xlabel('cneid:'+name)
        plt.savefig('C:\\Users\\xsaopig\\Desktop\\5G承载网项目\\5G承载网故障检测数据\\Data\\picture\\'+name+'.png', bbox_inches='tight')



#根据alarmcode统计每种告警发生次数
def CountAlarmsByAlarmcode(data,min_times):
    databyalarmcode=dp.getdataByalarmcode(data)
    cnt = []
    for key in databyalarmcode:
        cnt.append([str(key),len(databyalarmcode[key])])
    cnt.sort(key = lambda x:x[1],reverse = True)
    x = []
    y = []
    for i in cnt:
        if i[1] >= min_times:
            x.append(i[0])
            y.append(i[1])
    sns.set_style({'font.sans-serif':['simhei','Arial']})
    plt.bar(x = np.arange(len(x)), height = y, tick_label = x)
    plt.xticks(rotation=270)
    plt.ylabel("告警计数/次(不小于"+str(min_times)+"次)")
    plt.xlabel("calarmcode")
    plt.savefig('C:\\Users\\xsaopig\\Desktop\\5G承载网项目\\5G承载网故障检测数据\\Data\\picture\\CountAlarmcode.png', bbox_inches='tight')
