# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 01:30:27 2020

#Separating track points in Area 3
"""



#Area 3
test1 = test.drop(index=(test.loc[(test['lon']<=23.7312)].index))
test1 = test1.drop(index=(test1.loc[(test1['lon']>=23.7317)].index))
test1 = test1.drop(index=(test1.loc[(test1['lat']<=37.99185)].index))
test1 = test1.drop(index=(test1.loc[(test1['lon']*(5.3333)-88.574667>=test1['lat'])].index))
test1 = test1.drop(index=(test1.loc[(test1['lon']*(5.3333)-88.573767<=test1['lat'])].index))
test3 = test1.drop(index=(test1.loc[(test1['speed']>=1)].index))

test2 = test1.loc[(test1['time']<375)]
test2 = test2.loc[(test2['time']>300)]
