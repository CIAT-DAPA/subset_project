""" 
This implementation of core collection is based on the ccChooser R package.
The proportional method is used to identify the number of entries per group.
For the selection of core accessions, two methods are implemented: random sampling method and clustered sampling method.
"""

import pandas as pd
from .gower import gower_distances
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import AgglomerativeClustering

def _pro(groups, size, newSize, clusterIds):
    
    newGrpSizes = [value if (value := round(newSize*(list(groups).count(id)/size))) != 0 else 1 for id in clusterIds]

    return newGrpSizes

def _alloc(df, groups, fraction):
    
    size = len(df)
    newSize = size*fraction
    
    clusterIds = sorted(list(set(groups)))

    newGrpSizes = _pro(groups, size, newSize, clusterIds)
    
    result = pd.DataFrame([clusterIds]+[newGrpSizes], index=['cluster_id','newSize']).T

    return result

def stratcc(x, groups, nb_entries=None, fraction=None, clustering=True):
    
    def _clustered_sampling(data, clGrpID, alloID):
        alloData = data.loc[clGrpID == alloID, ]
        result = alloData.sample(1)
        return result
    
    grpIDs = list(set(groups))

    if fraction and nb_entries:
        raise ValueError('Please provide value for one argument: nb_entries or fraction!')
    
    elif fraction and not nb_entries:
        allocated = _alloc(x, groups, fraction)
    
    elif nb_entries and not fraction:
        if len(grpIDs)>1:
            raise ValueError('Please provide the fraction value not the nb_entries value: Data contain more than one group!')
        else:
            allocated = pd.DataFrame(grpIDs+[nb_entries], index=['cluster_id','newSize']).T
    #print(allocated)
    
    frames = []
    for id in grpIDs:
        grpData = x.loc[groups == id, ]
        nb_entries = allocated.loc[allocated['cluster_id']==id,'newSize'].values[0]
        #print('nb_entries...', nb_entries)
        
        if clustering:
            if len(grpData.index) == 1:
                frames.append(grpData)
            else:
                #apply hierarchical clustering to grpData
                numeric_colnames = [col for col in grpData.columns if 'value' in col or 'month' in col]
                numeric_data = grpData[numeric_colnames]
                
                #min-max scale indicators data
                scaled_data = pd.DataFrame(MinMaxScaler().fit_transform(numeric_data),index=numeric_data.index, columns = numeric_data.columns)
                cat_features = [col for col in grpData.columns if 'category' in col or 'cluster' in col]
            
                ind_data = pd.concat([scaled_data, grpData[cat_features]], axis=1)
            
                gower_dist = gower_distances(ind_data, categorical_features=cat_features, scale=False)
                model = AgglomerativeClustering(n_clusters = nb_entries, affinity = 'precomputed', linkage = 'complete')
                model.fit(gower_dist)
                labels = model.labels_
            
                result_frames = [_clustered_sampling(grpData, labels, id) for id in range(0,nb_entries)]
                result_grpid = pd.concat(result_frames)
                frames.append(result_grpid)

        else:
            newData = grpData.sample(nb_entries)
            frames.append(newData)
    
    result = pd.concat(frames)
    
    return result

