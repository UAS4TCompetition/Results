# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 01:15:42 2020

#data preprocessing
"""

strlist_former = ['']
result = []

import csv
import pandas as pd

csv.field_size_limit(500 * 1024 * 1024)

val =  [' Car', ' Taxi', ' Bus', ' Medium Vehicle', ' Heavy Vehicle', ' Motorcycle']

with open('competition_dataset2.csv', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    j = 1
    for line in reader:  
        temp = str(line.values()).split("'")[1].split(';')# 用逗号分割str字符串，并保存到列表
        if j == 1:
            break
    j = 2
    for line in reader:  
        strlist = str(line.values()).split("'")[1].split(';')# 用逗号分割str字符串，并保存到列表
        if strlist[1] not in val:#合并同一track_id的不同行
            strlist_former = str(strlist_former).split("']")[0] + str(temp).split("['")[1]     
        else:   
            if strlist_former != ['']:    
                temp = str(strlist_former).split("']")[0] + str(temp).split("['")[1]
                strlist_former = ['']
                temp = temp.split("['")[1].split("', '")
            else:
                del(temp[-1])
            result.append(temp[0:10])
            for t in range(0,int((len(temp)-4)/6)-1):
                result.append(temp[0:4]+temp[10+t*6:16+t*6])
            j = j + 1
        temp = strlist
        if j == 2308:
            break


column=['track_id','type', 'traveled_d', 'avg_speed', 'lat', 'lon', 'speed', 'lon_acc', 'lat_acc', 'time'] # 列表对应每列的列名
test=pd.DataFrame(columns=column,data=result)
test.loc[test['type'] == ' Car','type'] = 1
test.loc[test['type'] == ' Taxi','type'] = 2
test.loc[test['type'] == ' Bus','type'] = 3
test.loc[test['type'] == ' Medium Vehicle','type'] = 4
test.loc[test['type'] == ' Heavy Vehicle','type'] = 5
test.loc[test['type'] == ' Motorcycle','type'] = 6
test = test.loc[:].astype(float)

