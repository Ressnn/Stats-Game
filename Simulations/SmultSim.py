# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 20:54:12 2019

@author: ASUS
"""

import numpy as np
import matplotlib.pyplot as plt

size = int(input("Size?"))
initalvalue = int(input("Inital Value"))
def smultupdate(smult):
    sstand = (smult-15)/5
    
    smult = np.random.normal(15-sstand*4,3)                
    if smult>20:
        smult = 20
    if smult<10:
        smult = 10
    return smult

smult_list = []

for i in range(0,size):
    smult = 13
    for i in range(0,initalvalue):
        smult = smultupdate(smult)
    smult_list.append(smult)
plt.hist(smult_list)