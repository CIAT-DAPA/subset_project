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


def dbscan_func(dist_matrix, epsilon = 20, minpts = 10):
    db = DBSCAN(eps = epsilon, min_samples = minpts, metric = "precomputed").fit(dist_matrix)
    labels = db.labels_
    return labels

def agglomerative_func(dist_matrix, max_cluster, min_cluster = 2):
    #set the number of clusters range for silhouette method
    #the max_cluster should not be greater than n_samples - 1
    n_samples = len(dist_matrix)
    if max_cluster >= n_samples:
        max_cluster = n_samples - 1
    
    range_n_clusters = list(range(min_cluster, max_cluster + 1))
    
    #apply silhouette method
    avg_silhouette_values = []
    for n_clusters in range_n_clusters:
        model = AgglomerativeClustering(n_clusters = n_clusters, affinity = 'precomputed', linkage = 'complete')
        model.fit(dist_matrix)
        labels = model.labels_

        # The silhouette_score gives the average value for all the samples
        silhouette_avg = silhouette_score(dist_matrix, labels)
        avg_silhouette_values.append(silhouette_avg)

    # the optimal number of clusters has the max avg silhouette score
    idx_max_avg = np.argmax(avg_silhouette_values)
    n_optimum = range_n_clusters[idx_max_avg]
    
    model = AgglomerativeClustering(n_clusters = n_optimum, affinity = 'precomputed', linkage = 'complete')
    model.fit(dist_matrix)
    labels = model.labels_
    return labels

def hdbscan_func(dist_matrix, min_cluster_size = 10):
    clusterer = hdbscan.HDBSCAN(min_cluster_size = min_cluster_size, metric = "precomputed")
    clusterer.fit(dist_matrix)
    labels = clusterer.labels_
    return labels

def clustering_analysis(data, algorithms = ['agglomerative'], summary = True, n_months = None, n_years = None, **kwargs):
    """ data: should contain indicators data. They can be the multi-year average of each specific month values, 
    or the values of specific months in specifc years
    algorithms: the list of the clustering algorithms to use. Three options can be provided: 'agglomerative' for HAC,
    'dbscan' for DBSCAN and 'hdbscan' for HDBSCAN
    summary: if True data should be the multi-year average for each month.
    n_months: if summary = True, n_months is None. If summary = False, n_months should be provided
    n_years: if summary = True, n_years is None. If summary = False, n_years should be provided
    **kwargs: parameters to pass to the clustering functions: dbscan_func, agglomerative_func and hdbscan_func;
    to define custom values for their default parameters """

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
        print(crop)
        gr = (df.groupby(['crop'])).get_group(crop)
        gr.drop(labels = ['crop'], axis = "columns", inplace = True)
        
        if summary:
            merged_slices = pd.DataFrame([])

            months_slice = gr.loc[:, ['cellid','pref_indicator']+months_colnames].copy()
            value_slice = gr.loc[:, ['cellid','pref_indicator']+value_colname].copy()
            category_slice = gr.loc[:, ['cellid','pref_indicator']+category_colname].copy()

            for slice in [months_slice, value_slice, category_slice]:
                slice.dropna(inplace=True)
                slice = slice.pivot(index = 'cellid', columns = ['pref_indicator'])
                slice = slice.swaplevel(0, 1, axis = 1)
                slice.columns = slice.columns.map('_'.join)
                slice = slice.reset_index()

                if merged_slices.empty:
                    merged_slices = slice
                else:
                    merged_slices = slice.merge(merged_slices, on='cellid')

            merged_slices.dropna(inplace=True)
            merged_slices.reset_index(drop=True, inplace=True)
            gr = merged_slices          
        
        else:
            gr['period'] = gr['period'].apply(str)
            gr = transform_data(gr, n_months, n_years)
        
        numeric_colnames = [col for col in gr.columns if 'value' in col or 'month' in col]
        numeric_data = gr[numeric_colnames]

        #min-max scale indicators data
        scaled_data = pd.DataFrame(MinMaxScaler().fit_transform(numeric_data), columns = numeric_data.columns)
        
        cat_features = [col for col in gr.columns if 'category' in col]
        ind_data = pd.concat([scaled_data, gr[cat_features]], axis=1)
        
        gower_dist = gower_distances(ind_data, categorical_features=cat_features, scale=False)
        
        if "dbscan" in algorithms:
            dbscan_args = [k for k, v in inspect.signature(dbscan_func).parameters.items()]
            dbscan_dict = {k: kwargs[k] for k in dict(kwargs) if k in dbscan_args}
            
            dbscan_labels = dbscan_func(gower_dist, **dbscan_dict)
            ind_data["cluster_dbscan"] = dbscan_labels
        
        if "hdbscan" in algorithms:
            hdbscan_args = [k for k, v in inspect.signature(hdbscan_func).parameters.items()]
            hdbscan_dict = {k: kwargs[k] for k in dict(kwargs) if k in hdbscan_args}

            hdbscan_labels = hdbscan_func(gower_dist, **hdbscan_dict)
            ind_data["cluster_hdbscan"] = hdbscan_labels
        
        if "agglomerative" in algorithms:
            agglo_args = [k for k, v in inspect.signature(agglomerative_func).parameters.items()]
            agglo_dict = {k: kwargs[k] for k in dict(kwargs) if k in agglo_args}

            agglo_labels = agglomerative_func(gower_dist, **agglo_dict)
            ind_data["cluster_hac"] = agglo_labels     

        ind_data["crop_name"] = crop
        #return unscaled data
        clust_colnames = [col for col in ind_data.columns if 'cluster' in col]
        cluster_data = ind_data[cat_features+clust_colnames+['crop_name']]
        result = pd.concat([gr['cellid'], numeric_data, cluster_data], axis=1)
        
        analysis_res = analysis_res.append(result)

    return analysis_res
    