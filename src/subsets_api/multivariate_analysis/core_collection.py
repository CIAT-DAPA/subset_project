""" 
This implementation of core collection is based on the ccChooser R package.
It uses the proportional method for allocation and the random sampling method for selection.
"""
import pandas as pd


def _pro(groups, size, newSize, clusterIds):
    
    newGrpSizes = [round(newSize*(list(groups).count(id)/size)) for id in clusterIds]

    return newGrpSizes

def _alloc(df, groups, fraction):
    
    size = len(df)
    newSize = size*fraction
    
    clusterIds = sorted(list(set(groups)))

    newGrpSizes = _pro(groups, size, newSize, clusterIds)
    
    result = pd.DataFrame([clusterIds]+[newGrpSizes], index=['cluster_id','newSize']).T

    return result

def stratcc(x, groups, fraction = 0.2):

    allocated = _alloc(x, groups, fraction)
    grpIDs = list(set(groups))
    
    frames = []
    for id in grpIDs:
        grpData = x.loc[groups == id, ]
        newData = grpData.sample(allocated.loc[allocated['cluster_id']==id,'newSize'].values[0])
        frames.append(newData)
    result = pd.concat(frames)
    
    return result

