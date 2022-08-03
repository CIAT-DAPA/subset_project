import json
from flatten_json import flatten
import pandas as pd
from scipy import stats
import statistics
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import DBSCAN
from sklearn.cluster import AgglomerativeClustering
import hdbscan
from sklearn.metrics import silhouette_score
import numpy as np
import inspect
from .gower import gower_distances
import prince


def dbscan_func(X, epsilon = 0.2, minpts = 10):
    db = DBSCAN(eps = epsilon, min_samples = minpts).fit(X)
    labels = db.labels_
    return labels

def agglomerative_func(X, max_cluster, min_cluster = 2):
    #set the number of clusters range for silhouette method
    #the max_cluster should not be greater than n_samples - 1
    n_samples = len(X)
    if max_cluster >= n_samples:
        max_cluster = n_samples - 1
    
    range_n_clusters = list(range(min_cluster, max_cluster + 1))
    
    #apply silhouette method
    avg_silhouette_values = []
    for n_clusters in range_n_clusters:
        model = AgglomerativeClustering(n_clusters = n_clusters, affinity = 'euclidean', linkage = 'ward')
        model.fit(X)
        labels = model.labels_

        # The silhouette_score gives the average value for all the samples
        silhouette_avg = silhouette_score(X, labels)
        avg_silhouette_values.append(silhouette_avg)

    # the optimal number of clusters has the max avg silhouette score
    idx_max_avg = np.argmax(avg_silhouette_values)
    n_optimum = range_n_clusters[idx_max_avg]
    
    model = AgglomerativeClustering(n_clusters = n_optimum, affinity = 'euclidean', linkage = 'ward')
    model.fit(X)
    labels = model.labels_    
    return labels

def hdbscan_func(X, min_cluster_size = 10):
    clusterer = hdbscan.HDBSCAN(min_cluster_size = min_cluster_size)
    clusterer.fit(X)
    labels = clusterer.labels_
    return labels

def clustering_analysis(data, algorithms = ['agglomerative'], **kwargs):
    """ data: should contain cellids and indicators data.
    algorithms: the list of the clustering algorithms to use. Three options can be provided: 'agglomerative' for HAC,
    'dbscan' for DBSCAN and 'hdbscan' for HDBSCAN
    **kwargs: parameters to pass to the clustering functions: dbscan_func, agglomerative_func and hdbscan_func;
    to define custom values for their hyperparameters """

    #flatten data to a dataframe
    df = pd.DataFrame([flatten(x) for x in data])
    df = df.drop_duplicates()
    df.drop(labels = ['indicator'], axis = "columns", inplace = True)
    
    months_colnames = [col for col in df.columns if 'month' in col]
    value_colname = [col for col in df.columns if 'value' in col]
    category_colname = [col for col in df.columns if 'category' in col]
    
    #dataframe that will hold the analysis result
    analysis_res = pd.DataFrame([])

    #perform clustering per crop
    crops = df['crop'].unique()
    for crop in crops:
        gr = (df.groupby(['crop'])).get_group(crop)
        gr.drop(labels = ['crop'], axis = "columns", inplace = True)
        
        merged_slices = pd.DataFrame([])

        months_slice = gr.loc[:, ['cellid','pref_indicator']+months_colnames].copy()
        value_slice = gr.loc[:, ['cellid','pref_indicator']+value_colname].copy()
        category_slice = gr.loc[:, ['cellid','pref_indicator']+category_colname].copy()

        for s in [months_slice, value_slice, category_slice]:
            s = s.dropna()
            s = s.pivot(index = 'cellid', columns = ['pref_indicator'])
            s = s.swaplevel(0, 1, axis = 1)
            s.columns = s.columns.map('_'.join)
            s = s.reset_index()

            if merged_slices.empty:
                merged_slices = s
            else:
                merged_slices = s.merge(merged_slices, on='cellid')

        merged_slices.dropna(inplace=True)
        merged_slices.reset_index(drop=True, inplace=True)
        gr = merged_slices          
        
        numeric_colnames = [col for col in gr.columns if 'value' in col or 'month' in col]
        numeric_data = gr[numeric_colnames]
        cat_features = [col for col in gr.columns if 'category' in col]

        if numeric_data.empty:
            #case of only categorical variables, apply MCA
            ind_data = gr[cat_features]
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
                    gr[col] = gr[col].astype('object')
                
                ind_data = pd.concat([numeric_data, gr[cat_features]], axis=1)
                famd = prince.FAMD(n_components=5,n_iter=3,copy=True,check_input=True,engine='auto',
                                    random_state=42)
                famd = famd.fit(ind_data)
                reduced_data = famd.transform(ind_data)
        
        if "dbscan" in algorithms:
            dbscan_args = [k for k, v in inspect.signature(dbscan_func).parameters.items()]
            dbscan_dict = {k: kwargs[k] for k in dict(kwargs) if k in dbscan_args}
            
            dbscan_labels = dbscan_func(reduced_data, **dbscan_dict)
            reduced_data["cluster_dbscan"] = dbscan_labels
        
        if "hdbscan" in algorithms:
            hdbscan_args = [k for k, v in inspect.signature(hdbscan_func).parameters.items()]
            hdbscan_dict = {k: kwargs[k] for k in dict(kwargs) if k in hdbscan_args}

            hdbscan_labels = hdbscan_func(reduced_data, **hdbscan_dict)
            reduced_data["cluster_hdbscan"] = hdbscan_labels
        
        if "agglomerative" in algorithms:
            agglo_args = [k for k, v in inspect.signature(agglomerative_func).parameters.items()]
            agglo_dict = {k: kwargs[k] for k in dict(kwargs) if k in agglo_args}

            agglo_labels = agglomerative_func(reduced_data, **agglo_dict)
            reduced_data["cluster_hac"] = agglo_labels

        reduced_data["crop_name"] = crop
        clust_colnames = [col for col in reduced_data.columns if 'cluster' in str(col)]
        cluster_data = reduced_data[clust_colnames+['crop_name']]
        result = pd.concat([gr['cellid'], ind_data, cluster_data], axis=1)
        
        analysis_res = analysis_res.append(result)

    return analysis_res
    