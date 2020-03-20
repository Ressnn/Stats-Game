# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 22:12:03 2019

@author: Pranav Devarinti
"""
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import random
import numpy as np
p = float(input("p?"))
size = int(input("Size?"))

def geometricpdf(x,p):
    return ((1-p)**(x-1))*p
vl = []
vc = []
for i in range(1,20):
    vc.append(i)
    vl.append(geometricpdf(i,.3))


#Variable Setup Here:

num_list = []

for i in range(size):
    ct = 1
    while random.choice([True,True,True,True,True,True,True,False,False,False]):
        ct = ct+1
    num_list.append(ct)
x = num_list
num_bins = 35
n, bins, patches = plt.hist(x, num_bins, facecolor='blue', alpha=0.5)
print("Mean:"+str(np.mean(x)))
print("Standard Deviation:"+str(np.std(x)))
plt.plot(vc,np.array(vl)*size)

plt.show()