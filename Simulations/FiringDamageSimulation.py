# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 12:39:24 2019

@author: Pranav Devarinti
"""

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import random
import numpy as np
size = int(input("Size?"))
samples = []
shots = int(input("Shots?"))
dead = 0
for i in range(0,size):
    past_damage = 0
    for i in range(0,shots):
        damage = np.random.normal(5,2.5)
        past_damage = damage+past_damage
    if past_damage>=100:
        dead = dead+1
    samples.append(past_damage)
plt.hist(samples,30)
print("Mean:"+str(np.mean(samples)))
print("Standard Deviation:"+str(np.std(samples)))
print("Tank Destroyed Probability:"+str(dead/size))