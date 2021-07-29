import json
from flatten_json import flatten
import pandas as pd
from scipy import stats
import statistics
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.cluster import AgglomerativeClustering
import hdbscan
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
    data_list = data.values.tolist()
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
        years = data['period'].unique()
        df_merge_years = pd.DataFrame([])
        for year in years:
            grp_year = (sub_pref.groupby(['period'])).get_group(year)
            cell_ids = grp_year['cellid'].unique()
            df_by_cellids = pd.DataFrame([])

            for cell_id in cell_ids:
                grp_cell = (grp_year.groupby(['cellid'])).get_group(cell_id)
                grp_cell.drop(labels=['cellid'], axis="columns", inplace=True)                
                out = grp_cell.set_index(['period','pref_indicator']).stack()                
                out.index = out.index.map('_'.join)
                result = out.to_frame().T
                result.insert(loc=0, column='cellid', value=cell_id)
                df_by_cellids = df_by_cellids.append(result)
            
            if df_merge_years.empty:
                df_merge_years = df_by_cellids
            else:
                df_merge_years = pd.merge(df_merge_years, df_by_cellids)

        res = data_to_slope_sd_mean(df_merge_years, n_months, n_years)
        df = pd.DataFrame(res, columns=['cellid','slope_'+pref,'mean_'+pref, 'sd_'+pref])
    
        if trnsformed_res.empty:
            trnsformed_res = df
        else:
            trnsformed_res = pd.merge(trnsformed_res, df)

    return trnsformed_res

def dbscan_func(scaled_data, eps = 20, minPts = 10):
    db = DBSCAN(eps = eps, min_samples = minPts).fit(scaled_data)
    labels = db.labels_
    return labels

def agglomerative_func(scaled_data, n_clusters = 5):
    model = AgglomerativeClustering(n_clusters = n_clusters, affinity = 'euclidean', linkage = 'ward')
    model.fit(scaled_data)
    labels = model.labels_
    return labels

def hdbscan_func(scaled_data, min_cluster_size = 10):
    clusterer = hdbscan.HDBSCAN(min_cluster_size = min_cluster_size)
    clusterer.fit(scaled_data)
    labels = clusterer.labels_
    return labels


def clustering_analysis(algorithms, data, n_months, n_years, **kwargs):
    #flatten data to a dataframe
    #indicators = [crop_str_to_arr(x) for x in data]
    df = pd.DataFrame([flatten(x) for x in data])
    df.drop(labels=['indicator'], axis="columns", inplace=True)
    analysis_res = pd.DataFrame([])
    #group df by crop name
    crops = df['crop'].unique()
    for crop in crops:
        gr = (df.groupby(['crop'])).get_group(crop)
        gr.drop(labels=['crop'], axis="columns", inplace=True)
        
        transformed_gr = transform_data(gr, n_months, n_years)
        #indicators data without cellid
        ind_data = transformed_gr.iloc[: , 1:] 
        #scale indicators data
        scaled_data = pd.DataFrame(StandardScaler().fit_transform(ind_data), columns=ind_data.columns)
        
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
            scaled_data["cluster_aggolmerative"] = agglo_labels     

        scaled_data["crop_name"] = crop
        result = pd.concat([transformed_gr['cellid'], scaled_data], axis=1)
        analysis_res = analysis_res.append(result)
        analysis_res.reindex(columns=sorted(analysis_res.columns))

    return analysis_res