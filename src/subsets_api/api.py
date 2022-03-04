import sys
from pandas._libs.missing import NA
from pandas.core import groupby
import requests
from flask import Flask, request, jsonify, make_response
from flask_cors import cross_origin, CORS
import werkzeug
import numpy as np

from mongoengine import *
from models_subsets import *
from mongoengine.queryset.visitor import Q
from functools import reduce
import operator
import json
from multivariate_analysis.clustering_analysis import clustering_analysis
import pandas as pd
from itertools import groupby
import time
from multivariate_analysis.core_collection import stratcc

app = Flask(__name__)


@app.route('/api/v1/accessions', methods=['GET', 'POST'])
@cross_origin()
def accessions_list():
    # get the input parameters
    data = request.get_json()
    month_fields = ['month1','month2', 'month3', 'month4', 'month5', 'month6', 'month7', 'month8', 'month9',
                'month10', 'month11', 'month12']
    start = time.time()
    filter_clauses = [Q(**{filter + "__in": data[filter]})
                      for filter in data if len(data[filter]) > 0]
    print(filter_clauses)
    #accessions = Accession.objects((Q(crop__in = data["crop"])) & (Q(country_name__in = data["country_name"]))).select_related()
    # Filter accessions by clauses
    accessions = Accession.objects(reduce(operator.and_, filter_clauses)).select_related()
    rows = len(accessions)
    end = time.time()
    print("Accessions: " + str(rows) + " time: " + str((end-start)*1000.0))

    # Fixing accessions to the json format
    start = time.time()
    result = pd.DataFrame([{"name": x.name,
               "number": x.number,
               "acq_date": x.acq_date,
               "coll_date": x.coll_date,
               "country_name": x.country_name,
               "institute_fullname": x.institute_fullname,
               "institute_acronym": x.institute_acronym,
               "id": x.id,
               "crop": x.crop.name,
               "geo_lon": x.geo_lon,
               "geo_lat": x.geo_lat,
               "geo_ele": x.geo_ele,
               "taxonomy_genus": x.taxonomy_genus,
               "taxonomy_sp_author": x.taxonomy_sp_author,
               "taxonomy_species": x.taxonomy_species,
               "taxonomy_taxon_name": x.taxonomy_taxon_name,
               "cellid": x.cellid
               }
              for x in accessions])
    
    #rows = len(result)
    rows = result.shape[0]
    end = time.time()
    print("Result " + str(rows) + " time: " + str((end-start)*1000.0))
    
    # Calculate range of values
    #cell_ids = [x.cellid for x in accessions if x.cellid]
    #cell_ids = list(set(cell_ids))

    ind_period = IndicatorPeriod.objects(period__in=['min', 'max', 'mean']).select_related()    
    ind_periods_ids = []
    ind_periods_ids.extend(x.id for x in ind_period)
    print('periods', str(len(ind_period)))

    #ind_values = IndicatorValue.objects(indicator_period__in=ind_periods_ids, cellid__in=cell_ids).select_related()
    ind_values = IndicatorValue.objects(indicator_period__in=ind_periods_ids, cellid__in=result.loc[result["cellid"].notnull(),:]["cellid"].unique()).select_related()
    min_max = []    
    df = pd.DataFrame([{
            "indicator": x.indicator_period.indicator.name,
            "month1": x.month1,
            "month2": x.month2,
            "month3": x.month3,
            "month4": x.month4,
            "month5": x.month5,
            "month6": x.month6,
            "month7": x.month7,
            "month8": x.month8,
            "month9": x.month9,
            "month10": x.month10,
            "month11": x.month11,
            "month12": x.month12,
            "value": x.value,
            "cellid": x.cellid}
            for x in ind_values])
    df_grouped = df.groupby(['indicator'])
    for indx, group in enumerate(df_grouped):
        min = group[1][month_fields + ["value"]].min(skipna=True).min(skipna=True)
        max = group[1][month_fields + ["value"]].max(skipna=True).max(skipna=True)
        print(group[0] ,  'min: ', str(min), 'max: ', str(max))
        ob = {'indicator': group[0], 'min': min, 'max':max}        
        min_max.append(ob)
        # Calculate bins
        #bin_range = (max - min) / 20
        #avg = group[1][['month1','month2', 'month3', 'month4', 'month5', 'month6', 'month7', 'month8', 'month9',
        #        'month10', 'month11', 'month12']].mean()
    # 
    df_bins = df.groupby(['indicator','cellid'],as_index=False)[month_fields + ["value"]].mean()    
    df_bins["cellid"] = df_bins["cellid"].astype(int).astype(str)
    df_bins["mean"] = df_bins.mean(axis=1)
    #df_bins.to_csv('D:\\CIAT\\Code\\Modelling\\subsets_genebank_accessions\\src\\subsets_api\\bins1.csv', index=False)
    result2 = result.loc[:,["cellid","crop"]]
    result2 = result2.loc[result2["cellid"].notnull(),:]
    result2["cellid"] = result2["cellid"].astype(int).astype(str)
    df_bins = pd.merge(df_bins,result2,how='inner',on='cellid')    
    df_bins = df_bins.groupby(['indicator','mean'],as_index=False).size()
    #df_bins.to_csv('D:\\CIAT\\Code\\Modelling\\subsets_genebank_accessions\\src\\subsets_api\\bins1.csv', index=False)
    #print("Size",df_bins.shape[0])
    df_bins['quantile'] = df_bins.groupby(['indicator'])['mean'].transform(lambda x:pd.qcut(x, q=10, precision=0))
    #df_bins.to_csv('D:\\CIAT\\Code\\Modelling\\subsets_genebank_accessions\\src\\subsets_api\\bins.csv', index=False)
    df_bins = df_bins.groupby(['indicator','quantile'], as_index=False)['size'].sum()
    df_bins["quantile"] = df_bins["quantile"].astype(str)
    #df_bins.to_csv('D:\\CIAT\\Code\\Modelling\\subsets_genebank_accessions\\src\\subsets_api\\bins.csv', index=False)
    #print("Quantile",df_bins.shape[0])
    #print(df_bins.head())
    content = {
        'accessions':json.loads(result.to_json(orient='records')),
        'min_max': min_max,
        'quantile':  json.loads(df_bins.to_json(orient='records'))
    }


    return jsonify(content)


@app.route('/api/v1/indicators-range', methods=['GET', 'POST'])
@cross_origin()
def ranges_bins():
    # get the input parameters
    data = request.get_json()
    month_fields = ['month1','month2', 'month3', 'month4', 'month5', 'month6', 'month7', 'month8', 'month9',
                'month10', 'month11', 'month12']
    #t1 = time.time()
    ind_period_obj = IndicatorPeriod.objects(period__in=['mean']).only('id').select_related() 
    #t2=time.time()
    #print("ind periods..", t2-t1)
    ind_periods_ids = []
    ind_periods_ids.extend(x.id for x in ind_period_obj)
    #print(len(ind_periods_ids))

    cellids = [int(cell) for cell in data['cellid_list'] if cell]
    distinct_cellids = list(set(cellids))
    
    ind_values = IndicatorValue.objects(indicator_period__in=ind_periods_ids, cellid__in=distinct_cellids).select_related() 
    #t3=time.time()
    #print("ind values..", t3-t2)
    min_max = []

    df = pd.DataFrame([{
            "indicator": x.indicator_period.indicator.name,
            "month1": x.month1,
            "month2": x.month2,
            "month3": x.month3,
            "month4": x.month4,
            "month5": x.month5,
            "month6": x.month6,
            "month7": x.month7,
            "month8": x.month8,
            "month9": x.month9,
            "month10": x.month10,
            "month11": x.month11,
            "month12": x.month12,
            "value": x.value,
            "category": x.value_c,
            "cellid": x.cellid}
            for x in ind_values])
    
    #t4=time.time()
    #print("df..", t4-t3)
    df_grouped = df.groupby(['indicator'])
    for indx, group in enumerate(df_grouped):
        if not group[1]['category'].isnull().all():
            continue
        min = group[1][month_fields + ["value"]].min(skipna=True).min(skipna=True)
        max = group[1][month_fields + ["value"]].max(skipna=True).max(skipna=True)
        print(group[0] ,  'min: ', str(min), 'max: ', str(max))
        ob = {'indicator': group[0], 'min': min, 'max':max}        
        min_max.append(ob)

    #t5=time.time()
    #print("min max..", t5-t4)
    df_bins = df.groupby(['indicator','cellid'],as_index=False)[month_fields + ["value"]].mean()    
    df_bins["cellid"] = df_bins["cellid"].astype(int).astype(str)
    df_bins["mean"] = df_bins.mean(axis=1)
    #t6=time.time()
    #print("mean..", t6-t5)
    cellids_df = pd.DataFrame(cellids, columns=['cellid'])
    cellids_df["cellid"] = cellids_df["cellid"].astype(int).astype(str)
    df_bins = pd.merge(df_bins, cellids_df, how='inner', on='cellid')    
    df_bins = df_bins.groupby(['indicator','mean'], as_index=False).size()

    df_bins['quantile'] = df_bins.groupby(['indicator'])['mean'].transform(lambda x:pd.cut(x, bins=10, precision=0))
    df_bins = df_bins.groupby(['indicator','quantile'], as_index=False)['size'].sum()
    df_bins["quantile"] = df_bins["quantile"].astype(str)
    #t7=time.time()
    #print("bins..", t7-t6)
    proportions = df.groupby(['indicator'])['category'].value_counts(normalize = True).rename('proportion')
    proportions = pd.DataFrame(proportions).reset_index()
    #t8=time.time()
    #print("proportions..", t8-t7)
    content = {
        'min_max': min_max,
        'quantile': json.loads(df_bins.to_json(orient='records')),
        'proportion': json.loads(proportions.to_json(orient='records'))
    }
    
    return jsonify(content)



@app.route('/api/v1/crops', methods=['GET'])
@cross_origin()
def crop_list():
    # Crop query
    crops = Crop.objects.all()
    # Taxon name query
    tax = Accession.objects.all().distinct("taxonomy_taxon_name")
    # Institute name query
    institute = Accession.objects.all().distinct("institute_fullname")


    ins_res = [x for x in institute]
    tax_res = [x for x in tax]

    start = time.time()
    result = [{"name": x.name, "id": x.id}
              for x in crops]
    for x in result:
        access = Accession.objects(crop=x['id']).count()
        x['count_accessions'] = access
    # print(result)
    rows = len(result)
    end = time.time()
    print("Result " + str(rows) + " time: " + str((end-start)*1000.0))

    content = {
        "crops": result,
        "taxs": tax_res,
        "institute": ins_res
    }

    return json.dumps(content, default=str)

# define a fuction for key
def key_func(k):
    return k['category']

"""Get indicators"""
@app.route('/api/v1/indicators', methods=['GET'])
@cross_origin()
def indicator_list():
    indicator = Indicator.objects.all().select_related()

    start = time.time()
    result = [{"name": x.name,
                "id": x._id, 
                "pref": x.pref, 
                "indicator_type": x.indicator_type.name, 
                "crop": x.crop.name, 
                "category": x.category.name, 
                "checked": False,
                "unit": x.unit}
              for x in indicator]
    rows = len(result)
    end = time.time()
    print("Result " + str(rows) + " time: " + str((end-start)*1000.0))
    result = sorted(result, key=key_func)
    indicators_list = []
    for key, value in groupby(result, key_func):
        ls = {"category": key, "checked": False,"indicators": list(value)}
        indicators_list.append(ls)

    return json.dumps(indicators_list, default=str)


"""Get indicator_period objects"""

@app.route('/api/v1/indicator-period', methods=['GET'])
@cross_origin()
def indicator_period_list():
    indicator_period = IndicatorPeriod.objects().select_related()
    result = [{"id": x.id, "indicator": x.indicator._id, "period": x.period}
              for x in indicator_period]

    return json.dumps(result, default=str)

def getAccessionByCrop(crop, data):
    """ Function returned an accession list from a crop """
    lst_cellids = [x.cellid for x in data if str(crop) in x.crop.name]
    cell_ids = list(set(lst_cellids))
    return cell_ids

def getNameIndicatorByPref(pref):
    indicator = Indicator.objects(pref=pref).first()
    print(indicator)

def filterData(crops, cell_ids, indicators_params):
    subset = []
    
    for indicator in indicators_params:
        # Indicator periods ids
        periods_ids = indicator["indicator"]
        months_filter_range = indicator["months"]
        if months_filter_range:
            months_filter = list(range(months_filter_range[0], months_filter_range[1]+1))
        range_values = indicator["range"]

        if indicator['type'] == 'generic':
            print(indicator['name'])
            # Clauses to get the indicators data subset
            indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cell_ids})]            
            gte_months_clause = map(lambda kv: Q(**{'month{}__gte'.format(kv): range_values[0]}), months_filter)
            lte_months_clause = map(lambda kv: Q(**{'month{}__lte'.format(kv): range_values[1]}), months_filter)

            query_clause = indicator_periods_clauses + list(gte_months_clause) + list(lte_months_clause)
            #get filtered indicator value objects
            indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, query_clause)).select_related()
            if indicator_periods_values:
                #loop for each crop present in the request params
                for crop in crops:
                    # Dict to multivariate analysis
                    cell_id_crop = [cell for x in crops for cell in x['cellids'] if crop['crop'].lower() == x['crop'].lower()]
                    subset.extend([{
                        **{"crop": crop['crop'].lower(),
                        "pref_indicator": x.indicator_period.indicator.pref,
                        "indicator": x.indicator_period.indicator.name,
                        "cellid": x.cellid},
                        **{f"month_{month}": getattr(x, f"month{month}") for month in months_filter},
                        **{"period": x.indicator_period.period}}
                        for x in indicator_periods_values if x.cellid in cell_id_crop])
            else:
                raise ValueError('No accessions matching the filters applied to the indicator: '+ indicator['name'])
        elif indicator['type'] == 'specific':
            print(indicator['name'])
            crp = indicator['crop'].lower()
            cell_id_crop = [cell for x in crops for cell in x['cellids'] if crp == x['crop'].lower()]

            indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cell_id_crop})]
            gte_months_clause = map(lambda kv: Q(**{'month{}__gte'.format(kv): range_values[0]}), months_filter)
            lte_months_clause = map(lambda kv: Q(**{'month{}__lte'.format(kv): range_values[1]}), months_filter)
            query_clause = indicator_periods_clauses + list(gte_months_clause) + list(lte_months_clause)

            #print(query_clause)
            indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, query_clause)).select_related()
            
            if indicator_periods_values:
                subset.extend([{
                    **{"crop": crp,
                    "pref_indicator": x.indicator_period.indicator.pref,
                    "indicator": x.indicator_period.indicator.name,
                    "cellid": x.cellid},
                    **{f"month_{month}": getattr(x, f"month{month}") for month in months_filter},
                    **{"period": x.indicator_period.period}}
                    for x in indicator_periods_values if x.cellid in cell_id_crop])
            else:
                raise ValueError('No accessions matching the filters applied to the indicator: '+ indicator['name'])
        
        elif indicator['type'] == 'extracted':
            print(indicator['name'])
            indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cell_ids})]
            gte_value_clause = [Q(**{'value__gte': range_values[0]})]
            lte_value_clause = [Q(**{'value__lte': range_values[1]})]
            query_clause = indicator_periods_clauses + gte_value_clause + lte_value_clause

            indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, query_clause)).select_related()
            if indicator_periods_values:
                # loop for each crop present in the query
                for crop in crops:
                    cell_id_crop = [cell for x in crops for cell in x['cellids'] if crop['crop'].lower() == x['crop'].lower()]
                    subset.extend([{
                        "crop": crop['crop'].lower(),
                        "pref_indicator": x.indicator_period.indicator.pref,
                        "indicator": x.indicator_period.indicator.name,
                        "cellid": x.cellid,
                        "value": x.value,
                        "period": x.indicator_period.period}
                        for x in indicator_periods_values if x.cellid in cell_id_crop])
            else:
                raise ValueError('No accessions matching the filters applied to the indicator: '+ indicator['name'])
        elif indicator['type'] == 'categorical':
            print(indicator['name'])
            indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cell_ids})]
            value_in_clause = [Q(**{'value_c__in': range_values})]
            query_clause = indicator_periods_clauses + value_in_clause

            indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, query_clause)).select_related()
            if indicator_periods_values:
                # loop for each crop present in the query
                for crop in crops:
                    cell_id_crop = [cell for x in crops for cell in x['cellids'] if crop['crop'].lower() == x['crop'].lower()]
                    subset.extend([{
                        "crop": crop['crop'].lower(),
                        "pref_indicator": x.indicator_period.indicator.pref,
                        "indicator": x.indicator_period.indicator.name,
                        "cellid": x.cellid,
                        "category": x.value_c,
                        "period": x.indicator_period.period}
                        for x in indicator_periods_values if x.cellid in cell_id_crop])
            else:
                raise ValueError('No accessions matching the filters applied to the indicator: '+ indicator['name'])
    
    return subset

def getAccessionsFiltered(crops,cell_ids,indicators_params):
    """ Query to filter accessions in order to indicators params """
    # getAccessionByCrop('African yam bean')
    multivariate_values = []
    for indicator in indicators_params:

        # Indicator periods ids
        periods_ids = indicator["indicator"]
        # Clauses to get data for multivariate analysis
        if indicator['type'] == 'generic':
            indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cell_ids})]
             # Filtering values of indicator to multivariate analysis
            indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, indicator_periods_clauses)).select_related()

            # loop for each crop present in the query
            for crop in crops:
                cell_id_crop = [cell for x in crops for cell in x['cellids'] if crop['crop'] == x['crop']]
                # Dict to multivariate analysis
                multivariate_values.extend([{
                    "crop": crop['crop'],
                    "pref_indicator": x.indicator_period.indicator.pref,
                    "indicator": x.indicator_period.indicator.name,
                    "cellid": x.cellid,
                    "month1": x.month1,
                    "month2": x.month2,
                    "month3": x.month3,
                    "month4": x.month4,
                    "month5": x.month5,
                    "month6": x.month6,
                    "month7": x.month7,
                    "month8": x.month8,
                    "month9": x.month9,
                    "month10": x.month10,
                    "month11": x.month11,
                    "month12": x.month12,
                    "period": x.indicator_period.period}
                    for x in indicator_periods_values if  x.cellid in cell_id_crop])
        
        elif indicator['type'] == 'specific':
            crp = indicator['crop'].lower()
            cell_id_crop = [cell for x in crops for cell in x['cellids'] if crp == x['crop'].lower()]
            indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cell_id_crop})]

            indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, indicator_periods_clauses)).select_related()
            # Dict to multivariate analysis
            multivariate_values.extend([{
                "crop": indicator['crop'],
                "pref_indicator": x.indicator_period.indicator.pref,
                "indicator": x.indicator_period.indicator.name,
                "cellid": x.cellid,
                "month1": x.month1,
                "month2": x.month2,
                "month3": x.month3,
                "month4": x.month4,
                "month5": x.month5,
                "month6": x.month6,
                "month7": x.month7,
                "month8": x.month8,
                "month9": x.month9,
                "month10": x.month10,
                "month11": x.month11,
                "month12": x.month12,
                "period": x.indicator_period.period}
                for x in indicator_periods_values if  x.cellid in cell_id_crop])

        elif indicator['type'] == 'extracted':
            print(indicator['name'])
            indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cell_ids})]
            # Filtering values of indicator to multivariate analysis
            indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, indicator_periods_clauses)).select_related()
            # loop for each crop present in the query
            for crop in crops:
                cell_id_crop = [cell for x in crops for cell in x['cellids'] if crop['crop'] == x['crop']]
                # Dict to multivariate analysis
                multivariate_values.extend([{
                    "crop": crop['crop'],
                    "pref_indicator": x.indicator_period.indicator.pref,
                    "indicator": x.indicator_period.indicator.name,
                    "cellid": x.cellid,
                    "value": x.value,
                    "period": x.indicator_period.period}
                    for x in indicator_periods_values if  x.cellid in cell_id_crop])
        
        elif indicator['type'] == 'categorical':
            print(indicator['name'])
            indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cell_ids})]
            indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, indicator_periods_clauses)).select_related()
            
            # loop for each crop present in the query
            for crop in crops:
                cell_id_crop = [cell for x in crops for cell in x['cellids'] if crop['crop'] == x['crop']]
                multivariate_values.extend([{
                    "crop": crop['crop'],
                    "pref_indicator": x.indicator_period.indicator.pref,
                    "indicator": x.indicator_period.indicator.name,
                    "cellid": x.cellid,
                    "category": x.value_c,
                    "period": x.indicator_period.period}
                    for x in indicator_periods_values if x.cellid in cell_id_crop])

    return multivariate_values



""" Service to get subsets of accessions """
@app.route('/api/v1/subset', methods=['GET', 'POST'])
@cross_origin()
@app.errorhandler(werkzeug.exceptions.BadRequest)
def subset():
    data = request.get_json()
   
    cellid_ls = data['cellid_list']
    cellids = [int(cell) for x in cellid_ls for cell in x['cellids']]
    cellids = list(set(cellids))
    
    # Indicators params
    indicators_params = data['data']

    content = {}

    try:
        #start_time_subsets = time.time()
        result = filterData(crops = cellid_ls, cell_ids = cellids, indicators_params = indicators_params)
        #result = getAccessionsFiltered(crops=cellid_ls,cell_ids=cellids,indicators_params=indicators_params)
        #end_time_subsets = time.time()
        #print('filtering time: ',end_time_subsets-start_time_subsets)
  
        if result:
            univariate_data = pd.DataFrame([s for s in result])

            univariate_data_crop = univariate_data.groupby(['crop'])

            subset_dfs = []
            for crop_grouped in univariate_data_crop:
                frames_ind = [gr[1] for gr in crop_grouped[1].groupby(['indicator'])]
                #get the intersection between the indicators data frames_ind
                df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['cellid','crop'],
                                            how='inner'), frames_ind)
    
                ind_data_dfs = [df.loc[lambda df: df['cellid'].isin(df_merged['cellid'].values)] for df in frames_ind]
                subset_dfs.extend(ind_data_dfs)
        
            filtered_data = pd.concat(subset_dfs)
            if filtered_data.empty:
                raise ValueError('No data matching the selected filters!')
        
            colnames = filtered_data.columns.values.tolist()
        
            months = [k for k in colnames if "month" in str(k)]
            value = [k for k in colnames if "value" in str(k)]
            category = [k for k in colnames if 'category' in str(k)]

            filtered_cellids = (filtered_data.groupby(['crop'])['cellid']
            .apply(lambda x: list(set(x.to_list())))
            .reset_index().to_json(orient='records'))

            #univariate_result = univariate_data.to_json(orient = "records")
            #univariate_parsed = json.loads(univariate_result)

            #if univariate_parsed:
            #df = pd.DataFrame([s for s in univariate_parsed])
            
            df_grouped_indicator = filtered_data.groupby(['indicator', 'period', 'crop'])

            lst_box_data = []
            proportion_data = []
            it = []
            for group in df_grouped_indicator:
                it = months
                if category and not group[1]['category'].isnull().all():
                    proportions = group[1]['category'].value_counts(normalize = True).rename('proportion')
                    proportions.index.name = 'category'
                    proportions = pd.DataFrame(proportions).reset_index()
                    proportion_dict = dict(zip(proportions.category, proportions.proportion))
                    proportion_obj = {'indicator': group[0][0], 'period': group[0][1], 'crop': group[0][2], 'proportion': proportion_dict}
                    proportion_data.append(proportion_obj)
                    continue
                if value and not group[1]['value'].isnull().all():
                    it = value
                for month in it:
                    df_groupby = group[1][[month]].quantile([0.25,0.5,0.75])
                    # Whisker low
                    whisker_low = group[1][[month]].min()
                    # Whisker low
                    whisker_high = group[1][[month]].max()
                    # convert quantile index to quantile column
                    df_groupby.reset_index(inplace=True)
                    df_groupby.columns = ['quantile', month]

                    quantile_list = list(df_groupby[month].tolist())

                    obj = {'Q1': quantile_list[0], 'Q2': quantile_list[1], 'Q3': quantile_list[2], 'month': month, 'indicator': group[0][0],
                    'period':group[0][1], 'crop':group[0][2], 'whisker_low': whisker_low[0], 'whisker_high': whisker_high[0]}
                    lst_box_data.append(obj)

            df_quantiles = pd.DataFrame([s for s in lst_box_data])
            
            lst_field_quantiles = ['Q1', 'Q2', 'Q3', 'month', 'whisker_low', 'whisker_high']
            df_quantiles_grouped = (df_quantiles.groupby(['indicator','period', 'crop'])[lst_field_quantiles]
            .apply(lambda x: x.to_dict('r'))
            .reset_index(name='data')
            .to_json(orient='records'))

            quantile_data = json.loads(df_quantiles_grouped)

    except ValueError as ve:
        return('Bad request! '+str(ve), 400)

    content = {
        'filtered_cellids': json.loads(filtered_cellids),
        'quantile': quantile_data,
        'proportion': proportion_data
        }

    return jsonify(content)


""" Service to create clusters """
@app.route('/api/v1/cluster', methods=['GET', 'POST'])
@cross_origin()
def generate_clusters():
    data = request.get_json()
    #Passport paramns
    cellid_ls = data['cellid_list']
    cellids = [int(cell) for x in cellid_ls for cell in x['cellids']]
    cellids = list(set(cellids))
    # Indicators params
    indicators_params = data['data']
    # Multivariate params
    analysis_params = data['analysis']

    months_filter_range = data['months']

    if months_filter_range:
        months_filter = list(range(months_filter_range[0], months_filter_range[1]+1))
    # Algorithms list to use
    algorithms = analysis_params['algorithm']
    # hyperparameters to the multivariate analysis
    hyperparameters = analysis_params['hyperparameter']
    
    hyperparameters={"max_cluster" if k == 'n_clusters' else k:v for k,v in hyperparameters.items()}    
    
    first_time = time.time()
    content = {}

    multivariate_values = []
    for indicator in indicators_params:
        # Indicator periods ids
        periods_ids = indicator["indicator"]
        # Clauses to get data for multivariate analysis
        if indicator['type'] == 'generic':
            print(indicator['name'])
            indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cellids})]
            # Filtering values of indicator to multivariate analysis
            indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, indicator_periods_clauses)).select_related()
            # loop for each crop present in the query
            for crop in cellid_ls:
                    
                multivariate_values.extend([{
                    **{"crop": crop['crop'].lower(),
                    "pref_indicator": x.indicator_period.indicator.pref,
                    "indicator": x.indicator_period.indicator.name,
                    "cellid": x.cellid},
                    **{f"month{month}": getattr(x, f"month{month}") for month in months_filter}}
                    for x in indicator_periods_values if  x.cellid in crop['cellids']])
            
        elif indicator['type'] == 'specific':
            print(indicator['name'])
            crp = indicator['crop'].lower()
            cell_id_crop = [cell for x in cellid_ls for cell in x['cellids'] if crp == x['crop'].lower()]
            indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cell_id_crop})]

            indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, indicator_periods_clauses)).select_related()
            # Dict to multivariate analysis
            multivariate_values.extend([{
                **{"crop": crp,
                "pref_indicator": x.indicator_period.indicator.pref,
                "indicator": x.indicator_period.indicator.name,
                "cellid": x.cellid},
                **{f"month{month}": getattr(x, f"month{month}") for month in months_filter}}
                for x in indicator_periods_values if  x.cellid in cell_id_crop])
            
        elif indicator['type'] == 'extracted':
            print(indicator['name'])
            indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cellids})]
            # Filtering values of indicator to multivariate analysis
            indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, indicator_periods_clauses)).select_related()
            # loop for each crop present in the query
            for crop in cellid_ls:
                # Dict to multivariate analysis
                multivariate_values.extend([{
                    "crop": crop['crop'].lower(),
                    "pref_indicator": x.indicator_period.indicator.pref,
                    "indicator": x.indicator_period.indicator.name,
                    "cellid": x.cellid,
                    "value": x.value}
                    for x in indicator_periods_values if  x.cellid in crop['cellids']])
            
        elif indicator['type'] == 'categorical':
            print('categorical: ', indicator['name'])
            indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cellids})]
            # Filtering values of indicator to multivariate analysis
            indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, indicator_periods_clauses)).select_related()
            # loop for each crop present in the query
            for crop in cellid_ls:
                # Dict to multivariate analysis
                multivariate_values.extend([{
                    "crop": crop['crop'].lower(),
                    "pref_indicator": x.indicator_period.indicator.pref,
                    "indicator": x.indicator_period.indicator.name,
                    "cellid": x.cellid,
                    "category": x.value_c}
                    for x in indicator_periods_values if  x.cellid in crop['cellids']])
        
    # Create a df from multivariate analysis dict
    if multivariate_values:
        try:
            lst_calculates = []
            lst_summary = []
            lst_indicators = []
            lst_months = []
            cluster_columns = []
            category_columns = []
                
            analysis = clustering_analysis(algorithms=algorithms,data=multivariate_values,
                                        **hyperparameters)
                
            # from df to dict
            response_analysis = analysis.to_json(orient='records')

            for k,col in enumerate(analysis.columns):
                if 'month' in col or 'value' in col:
                    """ fields = col.split('_')
                    
                    if len(fields) >= 3:
                        lst_indicators.append(fields[0] + '_' + fields[1])
                        lst_months.append(fields[2])
                    
                    else:
                        lst_indicators.append(fields[0])
                        lst_months.append(fields[1]) """
                    lst_indicators.append(col.rsplit('_',1)[0])
                    lst_months.append(col.rsplit('_',1)[1])
                
                elif 'cluster' in col:
                    cluster_columns.append(col)
                
                elif 'category' in col:
                    lst_indicators.append(col.rsplit('_',1)[0])
                    category_columns.append(col)
                
            lst_indicators = list(set(lst_indicators))
            lst_months = list(set(lst_months))
            lst_months_quantiles = list(set(lst_months))
            lst_months.sort()

            analysis_columns = [col for col in analysis.columns]

            # transform cluster columns to rows
            analysis_wide2long = analysis.melt(id_vars= list(set(analysis_columns) - set(cluster_columns)),
                                            value_vars=cluster_columns,
                                            var_name='method', value_name='cluster')
                
            df = analysis_wide2long.groupby(['method','cluster','crop_name'])
            proportion_data = []
                
            for group in df:
                for indicator in lst_indicators:
                    
                    if indicator+'_category' in analysis_columns:
                        proportions =(group[1][indicator+'_category']
                        .value_counts(normalize = True)
                        .rename('proportion'))
                        
                        proportions.index.name = 'category'
                        proportions = pd.DataFrame(proportions).reset_index()
                        proportion_dict = dict(zip(proportions.category, proportions.proportion))
                        
                        proportion_obj = {'indicator': indicator, 'crop': group[0][2], 
                                        group[0][0]:int(group[0][1]), 'proportion': proportion_dict}
                        proportion_data.append(proportion_obj)
                        continue
                    
                    else:
                        if any(indicator+'_month' in col for col in analysis_columns):
                            lst_months_val = [x for x in lst_months if 'month' in x]
                    
                        elif indicator+'_value' in analysis_columns:
                            lst_months_val = [x for x in lst_months if 'value' in x]
                        
                        if lst_months_val:
                            # Get min
                            mini = group[1][[indicator +  '_' + x for x in lst_months_val]].min()
                            maxi = group[1][[indicator +  '_' + x for x in lst_months_val]].max()
                            
                            # if data for that group (indicator,crop) are null, skip to next iteration
                            if np.isnan(mini).all() and np.isnan(maxi).all():
                                continue
                            
                            obj_min = {x: mini[i] for i,x in enumerate(lst_months_val)}
                            obj_min['operator'] = 'Minimum'
                            obj_min[group[0][0]] = int(group[0][1])
                            obj_min['indicator'] = indicator
                            obj_min['crop'] = group[0][2]
                            lst_calculates.append(obj_min)
                            
                            obj_max = {x: maxi[i] for i,x in enumerate(lst_months_val)}
                            obj_max['operator'] = 'Maximum'
                            obj_max[group[0][0]] = int(group[0][1])
                            obj_max['indicator'] = indicator
                            obj_max['crop'] = group[0][2]
                            lst_calculates.append(obj_max)
                            # Get mean
                            mean = group[1][[indicator +  '_' + x for x in lst_months_val]].mean()
                            obj_mean = {x: mean[i] for i,x in enumerate(lst_months_val)}
                            obj_mean['operator'] = 'Mean'
                            obj_mean[group[0][0]] = int(group[0][1])
                            obj_mean['indicator'] = indicator
                            obj_mean['crop'] = group[0][2]
                            lst_calculates.append(obj_mean)
                            # Get sd
                            sd = group[1][[indicator +  '_' + x for x in lst_months_val]].std()
                            obj_sd = {x: sd[i] for i,x in enumerate(lst_months_val)}
                            obj_sd['operator'] = 'Standard deviation'
                            obj_sd[group[0][0]] = int(group[0][1])
                            obj_sd['indicator'] = indicator
                            obj_sd['crop'] = group[0][2]
                            lst_calculates.append(obj_sd)

                            obj_summary = {"mean":mean.mean(), "min":mini.min(), 
                                        "max":maxi.max(), group[0][0]:int(group[0][1]), "crop":group[0][2], 
                                        "indicator": indicator}
                            
                            lst_summary.append(obj_summary)
                
            if lst_calculates:
                df_multivariate = pd.DataFrame([s for s in lst_calculates])
                
                df_multivariate = df_multivariate[['indicator','crop', 'operator']+cluster_columns+lst_months]
                
                df_calculate = (df_multivariate.groupby(['indicator','operator', 'crop'])[lst_months+cluster_columns]
                .apply(lambda x: x.stack().groupby(level=0).agg(lambda y : y.reset_index(level=0,drop=True).to_dict()).tolist())
                .reset_index(name='data')
                .to_json(orient='records'))
                
                min_max_mean_sd = json.loads(df_calculate)
                
            else:
                min_max_mean_sd = []
                
            summary_json = json.dumps(lst_summary)
            # converting string to json
            final_dictionary = json.loads(summary_json)
            response_analysis_json = json.loads(response_analysis)
  
            # # # Calculate quantiles by month
            obj_list_quantiles = []
                
            for group in df:
                for indicator in lst_indicators:                    
                    if indicator+'_category' in analysis_columns:
                        continue
                    
                    elif any(indicator+'_month' in col for col in analysis_columns):
                        lst_months_quantiles = [x for x in lst_months if 'month' in x]

                    elif indicator+'_value' in analysis_columns:
                        lst_months_quantiles = [x for x in lst_months if 'value' in x]

                    if lst_months_quantiles:
                        for month in lst_months_quantiles:
                            # indicator_month = indicator + "_month1"
                            df_groupby_indicator = group[1][[indicator + "_" + month]].quantile([0.25,0.5,0.75])
                            # Whisker low
                            whisker_low = group[1][[indicator + "_" + month]].min()
                            # Whisker low
                            whisker_high = group[1][[indicator + "_" + month]].max()
                            # convert quantile index to quantile column
                            df_groupby_indicator.reset_index(inplace=True)
                            df_groupby_indicator.columns = ['quantile', month]

                            quantile_list = list(df_groupby_indicator[month].tolist())
                            obj = {'Q1': quantile_list[0], 'Q2': quantile_list[1], 'Q3': quantile_list[2],
                                'month': month, 'indicator': indicator, group[0][0]: int(group[0][1]),
                                'whisker_low': whisker_low[0], 'whisker_high': whisker_high[0],
                                'crop': group[0][2]}

                            obj_list_quantiles.append(obj)

            if obj_list_quantiles:
                df_quantiles = pd.DataFrame([s for s in obj_list_quantiles])
                lst_field_quantiles = ['Q1', 'Q2', 'Q3', 'month', 'whisker_low', 'whisker_high']
                
                df_quantiles_grouped = (df_quantiles.groupby(['indicator','crop'])[cluster_columns+lst_field_quantiles]
                .apply(lambda x: x.stack().groupby(level=0).agg(lambda y : y.reset_index(level=0,drop=True).to_dict()).tolist())
                .reset_index(name='data')
                .to_json(orient='records'))
                # dicti = df_multivariate.pivot('indicator','operator').to_dict('index')
                quantile_data = json.loads(df_quantiles_grouped)
                
            else:
                quantile_data = []
            
            content = {
                'data': response_analysis_json,
                'calculate': min_max_mean_sd,
                'quantile': quantile_data,
                'summary': final_dictionary,
                'proportion': proportion_data
            }
                
            last_time = time.time()
            total_time = last_time - first_time
            print(total_time)
        except ValueError as ve:
            print(str(ve))
            print("Exception")
        
    return (content)


""" Service to get core collection of the selected subset """
@app.route('/api/v1/core-collection', methods=['GET', 'POST'])
@cross_origin()
def get_core_collection():
    data = request.get_json()

    cluster_data = data['data']
    #selected_cluster = data['selected_cluster']
    amount = data['amount']

    cluster_df = pd.DataFrame([s for s in cluster_data])

    for col in cluster_df.columns:
        if isinstance(cluster_df[col].iloc[0], list):
            cluster_df[[col+'_month_'+str(idx+1) for idx in range(0,len(cluster_df[col].values[0]))]]=cluster_df[col].to_list()
            cluster_df.drop(labels = [col], axis = "columns", inplace = True)
    
    cluster_column = [col for col in cluster_df if 'cluster' in col][0]

    #cluster_df = cluster_df.loc[cluster_df[cluster_column]==selected_cluster,]
    
    if cluster_column:
        core_collection = stratcc(x=cluster_df, groups=cluster_df[cluster_column], nb_entries=amount)
        cc_cellids = core_collection['cellid']

        content = {
            'cellids': list(cc_cellids)
        }

    return content


@app.route('/api/v1/subsets', methods=['GET', 'POST'])
@cross_origin()
def subsets():
    data = request.get_json()
    # Passport paramns
    passport_params = data['passport']
    # Indicators params
    indicators_params = data['data']
    # Multivariate params
    analysis_params = data['analysis']
    # Algorithms list to use
    algorithms = analysis_params['algorithm']
    # hyperparameters to the multivariate analysis
    hyperparameters = analysis_params['hyperparameter']


    period = indicators_params[0]['period']
    # periods number calculated
    nYears = (period[1]+1) - period[0]
    # Months list calculated
    ob = [k for k in indicators_params[0] if "month" in str(k)]
    # months number calculated
    nMonths = len(ob)
    content = {}

    #Get crops
    crops = Crop.objects(Q(id__in = passport_params['crop']))
    result_crops = [{"id":x.id,"name": x.name} for x in crops]

    # Filtering accessions according to passport data
    start_time_accessions = time.time()

    # Filter clauses to get accessions in order to parameters
    filter_clauses = [Q(**{filter + "__in": passport_params[filter]})
                      for filter in passport_params if len(passport_params[filter]) > 0]
    # Query to get accessions
    accesions = Accession.objects(reduce(operator.and_, filter_clauses)).select_related()
    print("Accessions: " + str(len(accesions)) )

    # Cellids found in the accessions objects
    cell_ids = [x.cellid for x in accesions if x.cellid]
    # Reduce cellid list
    cell_ids = list(set(cell_ids))
    end_time_accessions = time.time()
    time_accessions = end_time_accessions - start_time_accessions
    print("Accessions time: " + str(time_accessions))

    # Filtering periods

    multivariate_values = []
    lst_values = []
    lst_df_multivariate = []

    """ Query to univariate analysis """    
    # With loop and indicatorsperiods from request
    for indicator in indicators_params:
        # month dict for each indicator in the query
        start_time_query_multivariate = time.time()
        months_filter = [{x: indicator[x] for x in indicator if 'month' in x}]

        """ indicator_clauses = [Q(**{filter + "__gte": indicator[filter][0], filter + "__lte": indicator[filter][1]})
                                  for filter in indicator if "month" in str(filter)] """

        # Indicator periods ids
        periods_ids = indicator["indicator"]
        # Clauses to get data for multivariate analysis
        indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cell_ids})]

        rows = len(periods_ids)

        # Filtering values of indicator to multivariate analysis
        indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, indicator_periods_clauses)).select_related()
        rows_indicator = len(indicator_periods_values)
        print("multivariate: " + str(rows_indicator))
        end_time_query_multivariate = time.time()

        time_query_multivariate = end_time_query_multivariate - start_time_query_multivariate
        print("Multivariate query: " + str(time_query_multivariate))

        # loop for each crop present in the query
        for crop in result_crops:
            cell_id_crop = [x.cellid for x in accesions if x.cellid and x.crop.id == crop['id']]
            # cellid list from crop
            cell_id_crop = list(set(cell_id_crop))
            # Dict to multivariate analysis
            multivariate_values.extend([{
                "crop": crop['name'],
                "pref_indicator": x.indicator_period.indicator.pref,
                "indicator": x.indicator_period.indicator.name,
                "cellid": x.cellid,
                "month1": x.month1,
                "month2": x.month2,
                "month3": x.month3,
                "month4": x.month4,
                "month5": x.month5,
                "month6": x.month6,
                "month7": x.month7,
                "month8": x.month8,
                "month9": x.month9,
                "month10": x.month10,
                "month11": x.month11,
                "month12": x.month12,
                "period": x.indicator_period.period}
                for x in indicator_periods_values if  x.cellid in cell_id_crop])


        # Create a df from multivariate analysis dict
        df_multivariate = pd.DataFrame([s for s in multivariate_values])
        # df to univariate analysis
        start_time_query_univariate = time.time()
        df_univariate = df_multivariate
        # Query to filter the univariate data
        query_gt = ' & '.join([f'{k}>{v[0]}' for k, v in months_filter[0].items()])
        query_lt = ' & '.join([f'{k}<{v[1]}' for k, v in months_filter[0].items()])
        query = query_gt + ' & ' + query_lt

        # Filter univariate data from query
        univ = df_univariate.query(query)
        print("Univariate: " + str(len(univ)))
        end_time_query_univariate = time.time()
        time_query_univariate = end_time_query_univariate - start_time_query_univariate
        print("Filter Univariate: " + str(time_query_univariate))
        # Append to list for each indicator in the query
        lst_values.append(univ)

        # loop to generate Nan values for each column month doesn't match with the range of values
        print("Lenght df: " + str(len(df_multivariate))) 
        for x in range(len(df_multivariate)):
            # for colums in list(df_multivariate.columns.values):
            for colums in ob:
                if indicator[colums][1] <= df_multivariate.loc[x, colums] or df_multivariate.loc[x, colums] <= indicator[colums][0]:
                        df_multivariate.loc[x, colums] = np.nan

        print(df_multivariate)
        lst_df_multivariate.append(df_multivariate)
        # lst_values = lst_values + cluster_values
    
    """ End query to univariate analysis """

    # Data for univariate analysis
    univariate_data = pd.concat(lst_values)
    univariate_result = univariate_data.to_json(orient = "records")
    univariate_parsed = json.loads(univariate_result)

    # Data with Nan values for multivariate analysis
    multivariate_data = pd.concat(lst_df_multivariate)
    multivariate_result = multivariate_data.to_json(orient = "records")
    multivariate_parsed = json.loads(multivariate_result)

    """ Process to get percentil (25, 50, 75) """
    # From response to df
    if univariate_parsed:
        start_time_quartile = time.time()
        df = pd.DataFrame([s for s in univariate_parsed])
        month_columns = df.columns.difference(['indicator', 'period', 'crop','cellid','pref_indicator'])
        df_groupby_indicator = df.groupby(['indicator', 'period', 'crop'])[month_columns].quantile([0.25,0.5,0.75])

        # convert quantile index to quantile column
        df_groupby_indicator.reset_index(level=3, inplace=True)
        df_groupby_indicator.rename(columns={'level_3': 'quantile'}, inplace=True)

        #convert indexes to column names
        df_groupby_indicator.reset_index(inplace = True)
        qt_month_columns = df_groupby_indicator.columns.difference(['indicator', 'period', 'crop','cellid','pref_indicator'])

        df_to_json = (df_groupby_indicator.groupby(['indicator', 'period', 'crop'])[qt_month_columns]
        .apply(lambda x: x.to_dict('r'))
        .reset_index(name='data')
        .to_json(orient='records'))

        quantiles = json.loads(df_to_json)

        end_time_quartile = time.time()

        time_quartile = end_time_quartile - start_time_quartile
        print("Quartile: " + str(time_quartile))

        """ End Process to get percentils """

        """ Process Multivariate analysis """
        # Runing multivariable analysis
        try:
            start_time_multivariate_analysis = time.time()
            analysis = clustering_analysis(algorithms, multivariate_parsed, nMonths, nYears, minPts=hyperparameters['minpts'], eps=hyperparameters['epsilon'],
                                        n_clusters=hyperparameters['n_clusters'], min_cluster_size=hyperparameters['min_cluster_size'])
            result = analysis.to_json(orient = "records")
            parsed = json.loads(result)
            end_time_multivariate_analysis = time.time()
            time_multivariate_analysis = end_time_multivariate_analysis - start_time_multivariate_analysis
            content = {
                'data': univariate_parsed,
                'multivariety_analysis': parsed,
                'quantile': quantiles,
                'times': {
                    'accessions': time_accessions,
                    'multivariate_data': time_query_multivariate,
                    'univariate_data': time_query_univariate,
                    'quartile': time_quartile,
                    'multivariate_analysis': time_multivariate_analysis
                }
            }
        except ValueError as ve:
            print(str(ve))
            content = {
                'data': univariate_parsed,
                'multivariety_analysis': [],
                'quantile': quantiles,
                'times': {
                    'accessions': time_accessions,
                    'multivariate_data': time_query_multivariate,
                    'univariate_data': time_query_univariate,
                    'quartile': time_quartile,
                    'multivariate_analysis': -1
                }
            }
            print("Exception")   

        """ End process multivariate analysis  """

        """ Final service content """

    else:
        try:
            start_time_multivariate_analysis = time.time()
            analysis = clustering_analysis(algorithms, multivariate_parsed, nMonths, nYears, minPts=hyperparameters['minpts'], eps=hyperparameters['epsilon'],
                                        n_clusters=hyperparameters['n_clusters'], min_cluster_size=hyperparameters['min_cluster_size'])
            result = analysis.to_json(orient = "records")
            parsed = json.loads(result)
            end_time_multivariate_analysis = time.time()
            time_multivariate_analysis = end_time_multivariate_analysis - start_time_multivariate_analysis
            content = {
                'data': [],
                'multivariety_analysis': parsed,
                'quantile': [],
                'times': {
                    'accessions': time_accessions,
                    'multivariate_data': time_query_multivariate,
                    'univariate_data': -1,
                    'quartile': -1,
                    'multivariate_analysis': time_multivariate_analysis
                }
            }
        except ValueError as ve:
            print(str(ve))
            content = {
                'data': [],
                'multivariety_analysis': [],
                'quantile': [],
                'times': {
                    'accessions': time_accessions,
                    'multivariate_data': time_query_multivariate,
                    'univariate_data': -1,
                    'quartile': -1,
                    'multivariate_analysis': -1
                }
            }
            print("Exception")


    return jsonify(content)

@app.route('/api/v1/custom-data', methods=['POST'])
@cross_origin()
def custom_data():
    """ Service to get custom data """
    data = request.get_json()
    custom_data = data['data']
    var = data['vars']
    print(var)

    return('Hello world!')

@app.route('/api/v1/range-values', methods=['POST'])
@cross_origin()
def get_range_values():
    """ Get range of values from an indicator """
    data = request.get_json()
    
    passport_params = data['passport']
    # indicator_selected = data['indicator']
    # print(indicator_selected)

    filter_clauses = [Q(**{filter + "__in": passport_params[filter]})
                      for filter in passport_params if len(passport_params[filter]) > 0]
    
    accesions = Accession.objects(reduce(operator.and_, filter_clauses)).select_related()
    print("Accessions: " + str(len(accesions)) )
    cell_ids = [x.cellid for x in accesions if x.cellid]
    cell_ids = list(set(cell_ids))
    print(str(len(cell_ids)))
    ind_period = IndicatorPeriod.objects(period__in=['min', 'max']).select_related()
    print('periods', str(len(ind_period)))
    ind_periods_ids = []
    ind_periods_ids.extend(x.id for x in ind_period)
    ind_values = IndicatorValue.objects(indicator_period__in=ind_periods_ids, cellid__in=cell_ids).select_related()
    print("MinAndMax: " + str(len(ind_values)) )
    responses = []
    results = []
    responses.extend([{
            "indicator": x.indicator_period.indicator.name,
            "month1": x.month1,
            "month2": x.month2,
            "month3": x.month3,
            "month4": x.month4,
            "month5": x.month5,
            "month6": x.month6,
            "month7": x.month7,
            "month8": x.month8,
            "month9": x.month9,
            "month10": x.month10,
            "month11": x.month11,
            "month12": x.month12,}
            for x in ind_values])
    df = pd.DataFrame([s for s in responses])
    df_grouped = df.groupby(['indicator'])
    for indx, group in enumerate(df_grouped):
        min = group[1][['month1','month2', 'month3', 'month4', 'month5', 'month6', 'month7', 'month8', 'month9',
                'month10', 'month11', 'month12']].min().min()
        max = group[1][['month1','month2', 'month3', 'month4', 'month5', 'month6', 'month7', 'month8', 'month9',
                'month10', 'month11', 'month12']].max().max()
        print(group[0] ,  'min: ', str(min), 'max: ', str(max))
        ob = {'indicator': group[0], 'min': min, 'max':max}
        results.append(ob)


    """ ind_values = IndicatorValue.objects(indicator_period__in=indicator_selected, cellid__in=cell_ids).select_related()
    print("MinAndMax: " + str(len(ind_values)) )
    responses = []
    responses.extend([{
            "indicator": x.indicator_period.indicator.name,
            "month1": x.month1,
            "month2": x.month2,
            "month3": x.month3,
            "month4": x.month4,
            "month5": x.month5,
            "month6": x.month6,
            "month7": x.month7,
            "month8": x.month8,
            "month9": x.month9,
            "month10": x.month10,
            "month11": x.month11,
            "month12": x.month12,}
            for x in ind_values])
    df = pd.DataFrame([s for s in responses])
    print(df)
    min = df[['month1','month2', 'month3', 'month4', 'month5', 'month6', 'month7', 'month8', 'month9',
                'month10', 'month11', 'month12']].min().min()
    max = df[['month1','month2', 'month3', 'month4', 'month5', 'month6', 'month7', 'month8', 'month9',
                'month10', 'month11', 'month12']].max().max()
    print('min: ', str(min), 'max: ', str(max))
    content = {
        "status":1,
        "min": min,
        "max": max
    } """
    return jsonify(results)


@app.route('/api/v1/indicator-value', methods=['GET', 'POST'])
@cross_origin()
def subsets_kha():
    data = request.get_json()

    passport_params = data['passport']
    #crop_params = data['crop']
    indicators_params = data['data']

    #Get crops
    crops = Crop.objects(Q(id__in = passport_params['crop']))
    result_crops = [{"id":x.id,"name": x.name} for x in crops]

    print("Crops: " + str(len(crops)) )
    # Filtering accessions according to passport data
    start = time.time()
    #accesions = Accession.objects(Q(crop__in = crop_params) & Q(country_name__in = passport_params["countries"]))
    filter_clauses = [Q(**{filter + "__in": passport_params[filter]})
                      for filter in passport_params if len(passport_params[filter]) > 0]
    
    accesions = Accession.objects(reduce(operator.and_, filter_clauses)).select_related()
    print("Accessions: " + str(len(accesions)) )
    cell_ids = [x.cellid for x in accesions if x.cellid]
    cell_ids = list(set(cell_ids))
    print(str(len(cell_ids)))

    # Filtering periods
    cluster_values = []
    multivariate_values = []
    lst_values = []
    lst_df_multivariate = []

    """ Query to univariate analysis """    
    # With loop and indicatorsperiods from request
    for indicator in indicators_params:
        indicator_clauses = [Q(**{filter + "__gte": indicator[filter][0], filter + "__lte": indicator[filter][1]})
                                  for filter in indicator if "month" in str(filter)]

        # Indicator periods ID
        periods_ids = indicator["indicator"]
        # Clauses to get data for multivariate analysis
        indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cell_ids})]
        # Clauses to get data for univariate analysis
        indicator_clauses = [Q(**{'indicator_period__in': periods_ids})] + indicator_clauses + [Q(**{'cellid__in': cell_ids})]

        start = time.time()
        rows = len(periods_ids)
        end = time.time()
        print("Periods: " + str(rows) + " time: " + str(end-start))

        # Filtering values of indicators
        start = time.time()
        ind_values = IndicatorValue.objects(reduce(operator.and_, indicator_clauses)).select_related()

        # Filtering values of indicator to multivariate analysis
        indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, indicator_periods_clauses)).select_related()
        rows = len(list(set(ind_values)))
        rows_indicator = len(list(set(indicator_periods_values)))

        print("Univariate: " + str(rows) )
        print("multivariate: " + str(rows_indicator) )

        for crop in result_crops:
            print(crop['name'])
            cell_id_crop = [x.cellid for x in accesions if x.cellid and x.crop.id == crop['id']]
            cell_id_crop = list(set(cell_id_crop))
            cluster_values.extend([{
                "crop": crop['name'],
                "pref_indicator": x.indicator_period.indicator.pref,
                "indicator": x.indicator_period.indicator.name,
                "cellid": x.cellid,
                "month1": x.month1,
                "month2": x.month2,
                "month3": x.month3,
                "month4": x.month4,
                "month5": x.month5,
                "month6": x.month6,
                "month7": x.month7,
                "month8": x.month8,
                "month9": x.month9,
                "month10": x.month10,
                "month11": x.month11,
                "month12": x.month12,
                "period": x.indicator_period.period}
                for x in ind_values if  x.cellid in cell_id_crop])

            multivariate_values.extend([{
                "crop": crop['name'],
                "pref_indicator": x.indicator_period.indicator.pref,
                "indicator": x.indicator_period.indicator.name,
                "cellid": x.cellid,
                "month1": x.month1,
                "month2": x.month2,
                "month3": x.month3,
                "month4": x.month4,
                "month5": x.month5,
                "month6": x.month6,
                "month7": x.month7,
                "month8": x.month8,
                "month9": x.month9,
                "month10": x.month10,
                "month11": x.month11,
                "month12": x.month12,
                "period": x.indicator_period.period}
                for x in indicator_periods_values if  x.cellid in cell_id_crop])

        df_multivariate = pd.DataFrame([s for s in multivariate_values])
        for x in range(len(df_multivariate)):
            for colums in list(df_multivariate.columns.values):
                    if 'month' in colums:
                            if indicator[colums][1] <= df_multivariate.loc[x, colums] or df_multivariate.loc[x, colums] <= indicator[colums][0]:
                                    df_multivariate.loc[x, colums] = np.nan
        print(df_multivariate)
        lst_df_multivariate.append(df_multivariate)
        lst_values = lst_values + cluster_values
        print(str(len(lst_values)))
        end = time.time()
        print("Indicator values:" + str(rows) + " time: " + str(end-start))
    
    """ End query to univariate analysis """

    # Data with Nan values for multivariate analysis
    multivariate_data = pd.concat(lst_df_multivariate)
    multivariate_result = multivariate_data.to_json(orient = "records")
    multivariate_parsed = json.loads(multivariate_result)

    """ Final service content """
    content = {
        'data': lst_values,
        'nan': multivariate_parsed,
    }


    return jsonify(content)


if __name__ == "__main__":

    #connect('indicatordb', host='localhost', port=27017)
    connect('indicatordb', host='dbmongotst01.cgiarad.org', port=27017)
    # app.run(threaded=True, host='0.0.0.0', port=8437, debug=False)
    app.run(threaded=True, port=5001, debug=True)
