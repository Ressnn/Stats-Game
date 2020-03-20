# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 16:37:41 2019

@author: Pranav Devarinti
"""

import numpy as np
import matplotlib.pyplot as plt
#from scipy.stats import skew 
sample_size = int(input("sample_size?"))
splits = int(input("samples?"))
vs = []

for i in range(0,sample_size*splits):
    vs.append(np.random.rayleigh(2))
vr = np.split(np.array(vs),splits)
vr = np.mean(vr,1)
plt.hist(vr,50)

print(np.std(vr))

#print("Skew:"+str(skew(vr)))


