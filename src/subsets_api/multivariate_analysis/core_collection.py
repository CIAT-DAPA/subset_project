""" 
This implementation of core collection is based on the ccChooser R package.
For the selection of core accessions, two methods are implemented: random sampling method and clustered sampling method.
"""

import pandas as pd
from sklearn.cluster import AgglomerativeClustering
import prince

""" def _pro(groups, size, newSize, clusterIds):
    
    newGrpSizes = [value if (value := round(newSize*(list(groups).count(id)/size))) != 0 else 1 for id in clusterIds]

    return newGrpSizes

def _alloc(df, groups, fraction):
    
    size = len(df)
    newSize = size*fraction
    
    clusterIds = sorted(list(set(groups)))

    newGrpSizes = _pro(groups, size, newSize, clusterIds)
    
    result = pd.DataFrame([clusterIds]+[newGrpSizes], index=['cluster_id','newSize']).T

    return result """

def stratcc(x, nb_entries, clustering=True):

    def _clustered_sampling(data, clGrpID, alloID):
        alloData = data.loc[clGrpID == alloID, ]
        result = alloData.sample(1, random_state=1)
        return result
    
    frames = []
        
    if clustering:
        if len(x.index) == 1:
            frames.append(x)
        else:
            """ apply hierarchical agglomerative clustering to x """
            numeric_colnames = [col for col in x.columns if 'value' in col or 'month' in col]
            cat_features = [col for col in x.columns if 'category' in col]
            numeric_data = x[numeric_colnames]

            if numeric_data.empty:
                #case of only categorical variables, apply MCA
                ind_data = x[cat_features]
                mca = prince.MCA(n_components=5,n_iter=3,copy=True,check_input=True,engine='auto',random_state=42)
                mca = mca.fit(ind_data)
                reduced_data = mca.transform(ind_data)
        
            else:
                if not cat_features:
                    #case of only numeric variables, apply PCA
                    ind_data = numeric_data
                    pca = prince.PCA(n_components=5,n_iter=3,rescale_with_mean=True,rescale_with_std=True,
                                    copy=True,check_input=True,engine='auto',random_state=42)
                    pca = pca.fit(numeric_data)
                    reduced_data = pca.transform(numeric_data)
                else:
                    #case of mixed variables, apply FAMD
                    for col in cat_features:
                        x[col] = x[col].astype('object')
                    
                    for col in numeric_colnames:
                        numeric_data[col] = numeric_data[col].astype('float64')

                    ind_data = pd.concat([numeric_data, x[cat_features]], axis=1)
                    famd = prince.FAMD(n_components=5,n_iter=3,copy=True,check_input=True,engine='auto',
                                    random_state=42)                                        
                    famd = famd.fit(ind_data)
                    reduced_data = famd.transform(ind_data)

            model = AgglomerativeClustering(n_clusters = nb_entries, affinity = 'euclidean',
                                            linkage = 'ward')
            model.fit(reduced_data)
            labels = model.labels_

            result_frames = [_clustered_sampling(x, labels, id) for id in range(0,nb_entries)]
            result_grpid = pd.concat(result_frames)
            frames.append(result_grpid)

    else:
        newData = x.sample(nb_entries, random_state=1)
        frames.append(newData)
    
    result = pd.concat(frames)
    
    return result

