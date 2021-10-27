import json
from flatten_json import flatten
import pandas as pd
from scipy import stats
import statistics
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.cluster import AgglomerativeClustering
import hdbscan
from sklearn.metrics import silhouette_score
import numpy as np
import inspect


# transform time series data to slope, sd and mean
def slope_sd_mean(row, n_months, n_years):
    if(n_months == 12):
        x = list(range(1, n_months*n_years+1))
        lr_res = stats.linregress(x, row[1:])
        slope = lr_res.slope
    else:
        season = list(range(1, n_months+1))
        i = 1
        slope_season = []
        while i < len(row):
            lr_season = stats.linregress(season, row[i:i+n_months])
            i += n_months
            slope_season.append(lr_season.slope)
        slope = statistics.mean(slope_season)
    
    mean = statistics.mean(row[1:])
    sd = statistics.stdev(row[1:])
    results = [row[0], slope, mean, sd]
    
    return results


def data_to_slope_sd_mean(data, n_months, n_years):
    data_list = data.reset_index().values.tolist()
    data_list_result = [slope_sd_mean(elt, n_months, n_years) for elt in data_list]
    return data_list_result


""" def crop_str_to_arr(elt):
    elt['indicator_period']['indicator']['crop'] = json.loads(elt['indicator_period']['indicator']['crop'])
    return elt """


def transform_data(data, n_months, n_years):

    indicator_prefs = data['pref_indicator'].unique()
    trnsformed_res = pd.DataFrame([])

    for pref in indicator_prefs:
        sub_pref = (data.groupby(['pref_indicator'])).get_group(pref)
        sub_pref.drop(labels=['pref_indicator'], axis="columns", inplace=True)
        df_pivoted = sub_pref.pivot(index='cellid', columns=['period'])
        df_pivoted = df_pivoted.swaplevel(0,1, axis=1).sort_index(axis=1)         

        df_pivoted.dropna(inplace=True)

        if df_pivoted.empty:
            raise ValueError('Empty dataframe after removing NA values for indicator '+ pref)
        
        res = data_to_slope_sd_mean(df_pivoted, n_months, n_years)
        df = pd.DataFrame(res, columns=['cellid','slope_'+pref,'mean_'+pref, 'sd_'+pref])
    
        if trnsformed_res.empty:
            trnsformed_res = df
        else:
            #inner merge on cellid
            trnsformed_res = pd.merge(trnsformed_res, df, on = 'cellid')

    return trnsformed_res


def dbscan_func(scaled_data, eps = 20, minPts = 10):
    db = DBSCAN(eps = eps, min_samples = minPts).fit(scaled_data)
    labels = db.labels_
    return labels

def agglomerative_func(scaled_data, max_cluster, min_cluster = 2):
    #set the number of clusters range for silhouette method
    #the max_cluster should not be greater than n_samples - 1
    n_samples = len(scaled_data.index)
    if max_cluster >= n_samples:
        max_cluster = n_samples - 1
    
    range_n_clusters = list(range(min_cluster, max_cluster + 1))
    #apply silhouette method
    avg_silhouette_values = []

    for n_clusters in range_n_clusters:
        model = AgglomerativeClustering(n_clusters = n_clusters, affinity = 'euclidean', linkage = 'ward')
        labels = model.fit_predict(scaled_data)

        # The silhouette_score gives the average value for all the samples
        silhouette_avg = silhouette_score(scaled_data, labels)
        avg_silhouette_values.append(silhouette_avg)

    # the optimal number of clusters has the max avg silhouette score
    idx_max_avg = np.argmax(avg_silhouette_values)
    n_optimum = range_n_clusters[idx_max_avg]
    """ print(n_optimum) """
    model = AgglomerativeClustering(n_clusters = n_optimum, affinity = 'euclidean', linkage = 'ward')
    model.fit(scaled_data)
    labels = model.labels_
    
    return labels

def hdbscan_func(scaled_data, min_cluster_size = 10):
    clusterer = hdbscan.HDBSCAN(min_cluster_size = min_cluster_size)
    clusterer.fit(scaled_data)
    labels = clusterer.labels_
    return labels


# data: should contain indicators data. They can be the multi-year average of each specific month values, 
# or the values of specific months in specifc years
# algorithms: the list of the clustering algorithms to use. Three options can be provided: 'agglomerative' for HAC,
# 'dbscan' for DBSCAN and 'hdbscan' for HDBSCAN
# summary: if True data should be the multi-year average for each month.
# n_months: if summary = True, n_months is None. If summary = False, n_months should be provided
# n_years: if summary = True, n_years is None. If summary = False, n_years should be provided
# **kwargs: parameters to pass to the clustering functions: dbscan_func, agglomerative_func and hdbscan_func;
# to define custom values for their default parameters

def clustering_analysis(data, algorithms = ['agglomerative'], summary = True, n_months = None, n_years = None, **kwargs):
    
    #flatten data to a dataframe
    df = pd.DataFrame([flatten(x) for x in data])
    
    df = df.drop_duplicates()
    df.drop(labels = ['indicator'], axis = "columns", inplace = True)
    
    #dataframe that will hold the analysis result
    analysis_res = pd.DataFrame([])

    #perform clustering per crop
    crops = df['crop'].unique()
    for crop in crops:
        gr = (df.groupby(['crop'])).get_group(crop)
        gr.drop(labels = ['crop'], axis = "columns", inplace = True)
        
        if summary:
            gr = gr.pivot(index = 'cellid', columns = ['pref_indicator'])
            gr = gr.swaplevel(0, 1, axis = 1)
            gr.columns = gr.columns.map('_'.join)
            gr = gr.reset_index()
            gr.dropna(inplace=True)            
        
        else:
            gr['period'] = gr['period'].apply(str)
            gr = transform_data(gr, n_months, n_years)
        
        #indicators data without cellid
        ind_data = gr.iloc[:, 1:]

        #scale indicators data
        scaled_data = pd.DataFrame(StandardScaler().fit_transform(ind_data), columns = ind_data.columns)
        
        if "dbscan" in algorithms:
            dbscan_args = [k for k, v in inspect.signature(dbscan_func).parameters.items()]
            dbscan_dict = {k: kwargs[k] for k in dict(kwargs) if k in dbscan_args}
            
            dbscan_labels = dbscan_func(scaled_data, **dbscan_dict)
            scaled_data["cluster_dbscan"] = dbscan_labels
        
        if "hdbscan" in algorithms:
            hdbscan_args = [k for k, v in inspect.signature(hdbscan_func).parameters.items()]
            hdbscan_dict = {k: kwargs[k] for k in dict(kwargs) if k in hdbscan_args}

            hdbscan_labels = hdbscan_func(scaled_data, **hdbscan_dict)
            scaled_data["cluster_hdbscan"] = hdbscan_labels
        
        if "agglomerative" in algorithms:
            agglo_args = [k for k, v in inspect.signature(agglomerative_func).parameters.items()]
            agglo_dict = {k: kwargs[k] for k in dict(kwargs) if k in agglo_args}

            agglo_labels = agglomerative_func(scaled_data, **agglo_dict)
            scaled_data["cluster_hac"] = agglo_labels     

        scaled_data["crop_name"] = crop
        #return unscaled data
        cluster_data = scaled_data.iloc[: , len(ind_data.columns):]
        result = pd.concat([gr['cellid'], ind_data, cluster_data], axis=1)
        
        analysis_res = analysis_res.append(result)

    return analysis_res
    