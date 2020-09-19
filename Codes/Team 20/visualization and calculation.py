# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 01:34:52 2020

#visualization and calculation
"""


import matplotlib.pyplot as plt
import math


#visualization

ps = dict(list(test.groupby(['track_id']))) 
plt.grid(linestyle='-.')
for i in ps.keys():
    temp = ps.get(i)
    #plt.scatter(temp['lon'], temp['lat'], c=temp['speed'], s=0.01)
    plt.scatter(temp['time'], temp['lat'], c=temp['speed'], s=0.01)
#plt.colorbar()
plt.gca().invert_yaxis()
plt.xlabel('time/s')
plt.ylabel('lon')
plt.show()


#calculation length

def getDistance(lon1, lon2, lat1, lat2):
     r = 6378137
     x1 = lon1 * math.pi / 180
     x2 = lon2 * math.pi / 180
     y1 = lat1 * math.pi / 180
     y2 = lat2 * math.pi / 180
     dx = abs(x1 - x2)
     dy = abs(y1 - y2)
     p = pow(math.sin(dx / 2), 2) + math.cos(x1) * math.cos(x2) * math.pow(math.sin(dy / 2), 2)
     d= r * 2 * math.asin(math.sqrt(p))
     return d

lat1 = 37.992
lon1 = 23.7314
lat2 = 37.9928
lon2 = 23.7315
print(getDistance(lon1, lon2, lat1, lat2))