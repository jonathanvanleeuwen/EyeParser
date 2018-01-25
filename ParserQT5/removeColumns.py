# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 23:05:10 2018

@author: JonLee
"""

import pandas as pd
#loc = 'D:\Work\PhD Vu\Project 6 - PredictingMovement\DataExp1\ParsedData\\'
#fn = 'PP4S2Parsed.p'
#data = pd.read_pickle(loc+fn)

fn = 'C:/Work/PhD Vu/Project 6 - PredictingMovement/DataExp1/FilteredData/PredictJumpMerged.p'
data = pd.read_pickle(fn)

keys = data.keys()
print len(keys)

deleteColumns = ['VALIDATE','!CAL','!MODE','ELCL','RECCFG','GAZE_COORDS',\
                 'DISPLAY_COORDS','THRESHOLDS']

def filterDF(df, deleteKeys):
    keys = df.keys()   
    for key in keys:
        for delKey in deleteKeys:
            if delKey in key:
                del df[key]
    return df

data = filterDF(data, deleteColumns)

  
keys = data.keys()
print len(keys)
print keys


fn = 'C:/Work/PhD Vu/Project 6 - PredictingMovement/DataExp1/FilteredData/PredictJumpMerged2.p'
data.to_pickle(fn)
