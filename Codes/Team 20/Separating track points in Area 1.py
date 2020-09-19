# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 01:28:44 2020

#Separating track points in Area 1
"""

#area 1
test1 = test.drop(index=(test.loc[(test['lon']<=23.7315)].index))
test1 = test1.drop(index=(test1.loc[(test1['lon']>=23.7356)].index))
test1 = test1.drop(index=(test1.loc[(test1['lat']<=37.99107)].index))
test1 = test1.drop(index=(test1.loc[(test1['lat']>=37.9919)].index))
test1 = test1.drop(index=(test1.loc[(test1['lon']*(-0.1647)+41.90031>=test1['lat'])].index))
test1 = test1.drop(index=(test1.loc[(test1['lon']*(-0.1647)+41.900425<test1['lat'])].index))


#下1车道
test4 = test1.drop(index=(test1.loc[(test1['lon']*(-0.1647)+41.90039>=test1['lat'])].index))
#中间车道
test5 = test1.drop(index=(test1.loc[(test1['lon']*(-0.1647)+41.90036>=test1['lat'])].index))
test5 = test5.drop(index=(test5.loc[(test5['lon']*(-0.1647)+41.90039<test5['lat'])].index))
test5 = test5.drop(index=(test5.loc[(test5['time']>=600)].index))
test5 = test5.drop(index=(test5.loc[(test5['time']<=560)].index))
#上1车道
test6 = test1.drop(index=(test1.loc[(test1['lon']*(-0.1647)+41.90033>=test1['lat'])].index))
test6 = test6.drop(index=(test6.loc[(test6['lon']*(-0.1647)+41.90036<test6['lat'])].index))
test6 = test6.drop(index=(test6.loc[(test6['time']>=800)].index))
test6 = test6.drop(index=(test6.loc[(test6['time']<=650)].index))