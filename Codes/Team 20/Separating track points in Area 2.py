# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 01:30:26 2020

#Separating track points in Area 2
"""


#Area 2
test1 = test.drop(index=(test.loc[(test['lon']<=23.7313)].index))
test1 = test1.drop(index=(test1.loc[(test1['lon']>=23.732)].index))
test1 = test1.drop(index=(test1.loc[(test1['lat']<=37.9907)].index))
test1 = test1.drop(index=(test1.loc[(test1['lat']>=37.9916)].index))
test1 = test1.drop(index=(test1.loc[(test1['lon']*(3.3333333)-41.112667<test1['lat'])].index))
test1 = test1.drop(index=(test1.loc[(test1['lon']*(0.76923)+19.73653<test1['lat'])].index))


test2 = test1.loc[(test1['time']<750)]
test2 = test2.loc[(test2['time']>650)]
