import sys
from pandas._libs.missing import NA
from pandas.core import groupby
import requests
from flask import Flask, request, jsonify, make_response
from flask_cors import cross_origin, CORS
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

app = Flask(__name__)


@app.route('/api/v1/accessions', methods=['GET', 'POST'])
@cross_origin()
def accessions_list():
    data = request.get_json()

    start = time.time()
    filter_clauses = [Q(**{filter + "__in": data[filter]})
                      for filter in data if len(data[filter]) > 0]
    print(filter_clauses)
    #accessions = Accession.objects((Q(crop__in = data["crop"])) & (Q(country_name__in = data["country_name"]))).select_related()
    accessions = Accession.objects(
        reduce(operator.and_, filter_clauses)).select_related()
    rows = len(accessions)
    end = time.time()
    print("Accessions: " + str(rows) + " time: " + str((end-start)*1000.0))

    start = time.time()
    result = [{"name": x.name,
               "number": x.number,
               "acq_date": x.acq_date,
               "coll_date": x.coll_date,
               "country_name": x.country_name,
               "institute_fullname": x.institute_fullname,
               "institute_acronym": x.institute_acronym,
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
              for x in accessions]
    rows = len(result)
    end = time.time()
    print("Result " + str(rows) + " time: " + str((end-start)*1000.0))
    
    # Calculate range of values
    cell_ids = [x.cellid for x in accessions if x.cellid]
    cell_ids = list(set(cell_ids))

    ind_period = IndicatorPeriod.objects(period__in=['min', 'max']).select_related()
    print('periods', str(len(ind_period)))

    ind_periods_ids = []
    ind_periods_ids.extend(x.id for x in ind_period)

    ind_values = IndicatorValue.objects(indicator_period__in=ind_periods_ids, cellid__in=cell_ids).select_related()
    print("MinAndMax: " + str(len(ind_values)) )
    responses = []
    min_max = []
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
        min_max.append(ob)

    content = {
        'accessions': result,
        'min_max': min_max
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
    result = [{"name": x.name, "id": x._id, "pref": x.pref, "indicator_type": x.indicator_type.name, "crop": x.crop.name, "category": x.category.name, "checked": False}
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

def getAccessionsFiltered(crops, accessions,cell_ids,indicators_params):
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
            rows_indicator = len(indicator_periods_values)

            # loop for each crop present in the query
            for crop in crops:
                cell_id_crop = [x.cellid for x in accessions if x.cellid and x.crop.id == crop['id']]
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
        elif indicator['type'] == 'specific':
            print(indicator['crop'])
            cell_id_crop = getAccessionByCrop(crop=indicator['crop'], data=accessions)
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

    return multivariate_values



""" Service to get subsets of accessions """
@app.route('/api/v1/subset', methods=['GET', 'POST'])
@cross_origin()
def subset():
    # Start
    total_time_subsets = -1
    total_time_quantile = -1
    lst_df_univariate = []
    univariate_parsed = []
    data = request.get_json()
    # Passport paramns
    passport_params = data['passport']
    # Indicators params
    indicators_params = data['data']

    period = indicators_params[0]['period']
    
    # Months list calculated
    ob = [k for k in indicators_params[0] if "month" in str(k)]
    content = {}
    print(ob)
    #Get crops
    crops = Crop.objects(Q(id__in = passport_params['crop']))
    result_crops = [{"id":x.id,"name": x.name} for x in crops]

    # Filter clauses to get accessions in order to parameters
    filter_clauses = [Q(**{filter + "__in": passport_params[filter]})
                      for filter in passport_params if len(passport_params[filter]) > 0]
    # Query to get accessions
    accessions = Accession.objects(reduce(operator.and_, filter_clauses)).select_related()

    # Cellids found in the accessions objects
    cell_ids = [x.cellid for x in accessions if x.cellid]
    # Reduce cellid list
    cell_ids = list(set(cell_ids))

    start_time_subsets = time.time()
    result = getAccessionsFiltered(crops=result_crops, accessions=accessions,cell_ids=cell_ids,indicators_params=indicators_params)
    print('Done!')
  
    if result:
        df_multivariate = pd.DataFrame([s for s in result])
        df_groupby = df_multivariate.groupby(['indicator'], sort=False)
        print(df_multivariate)
        for indx, group in enumerate(df_groupby):
            months_filter = [{x: indicators_params[indx][x] for x in indicators_params[indx] if 'month' in x}]
            # Query to filter the univariate data
            query_gt = ' & '.join([f'{k}>={v[0]}' for k, v in months_filter[0].items()])
            query_lt = ' & '.join([f'{k}<={v[1]}' for k, v in months_filter[0].items()])
            query = query_gt + ' & ' + query_lt

            # Filter univariate data from query
            univ = group[1].query(query)

            lst_df_univariate.append(univ)
            # lst_values = lst_values + cluster_values
        
        """ End query to univariate analysis """

        # Data for univariate analysis
        univariate_data = pd.concat(lst_df_univariate)
        # print(univariate_data)
        col_one_list = list(set(univariate_data['cellid'].tolist()))
        accessions_list = []
        accessions_list.extend([{   
                "name": x.name,
                "number": x.number,
                "acq_date": x.acq_date,
                "coll_date": x.coll_date,
                "country_name": x.country_name,
                "institute_fullname": x.institute_fullname,
                "institute_acronym": x.institute_acronym,
                "crop": x.crop.name,
                "geo_lon": x.geo_lon,
                "geo_lat": x.geo_lat,
                "geo_ele": x.geo_ele,
                "taxonomy_genus": x.taxonomy_genus,
                "taxonomy_sp_author": x.taxonomy_sp_author,
                "taxonomy_species": x.taxonomy_species,
                "taxonomy_taxon_name": x.taxonomy_taxon_name,
                "cellid": x.cellid}
            for x in accessions if x.cellid in col_one_list])

        univariate_result = univariate_data.to_json(orient = "records")
        univariate_parsed = json.loads(univariate_result)
        end_time_subsets = time.time()
        total_time_subsets = end_time_subsets - start_time_subsets

        if univariate_parsed:
            start_time_quantile = time.time()
            df = pd.DataFrame([s for s in univariate_parsed])
            # print(df)
            month_columns = df.columns.difference(['indicator', 'period', 'crop','cellid','pref_indicator'])
            df_groupby_indicator = df.groupby(['indicator', 'period', 'crop'])[ob].quantile([0.25,0.5,0.75])

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
            
            quantiles_grouped = []
            obj = {}
            lst_final = []
            quantiles = json.loads(df_to_json)
            """ for key, value in groupby(quantiles, key_func):
                ls = {"crop": key, "indicators": list(value)}
                quantiles_grouped.append(ls)
            for res in quantiles_grouped:
                for prop in res['indicators']:
                    lst_obj = []
                    obj = {"name": prop["indicator"], "period": prop["period"], "data": prop["data"]}
                    lst_obj.append(obj)
                lst_final.append({"crop": res["crop"], "indicators":lst_obj})

            print(lst_final) """
            """ quantiles_list = []
            quantiles_grouped = []
            for x in quantiles:
                quantil_first = []
                quantil_second = []
                quantil_third = []
                data = x['data']
                quantil_first.extend({'x':indx, 'y':data[0][k], 'serie':0} for indx,k in enumerate(data[0]) if 'month' in str(k))
                quantil_second.extend({'x':indx, 'y':data[1][k], 'serie':0} for indx,k in enumerate(data[1]) if 'month' in str(k))
                quantil_third.extend({'x':indx, 'y':data[2][k], 'serie':0} for indx,k in enumerate(data[2]) if 'month' in str(k))
                new_obj = {'indicator': x['indicator'],
                            'crop': x['crop'],
                            'period':x['period'], 
                            'data': [ {'values': quantil_first, 'key': 0.25},
                                        {'values': quantil_second, 'key': 0.50},
                                        {'values': quantil_third, 'key': 0.75}]}
                quantiles_list.append(new_obj)

            quantiles_list = sorted(quantiles_list, key=key_func)

            for key, value in groupby(quantiles_list, key_func):
                ls = [key, list(value)]
                quantiles_grouped.append(ls)
            print(quantiles_grouped) """
            """ quantil_second.extend(data[1][k] for k in data[1] if 'month' in str(k))
                quantil_third.extend(data[2][k] for k in data[2] if 'month' in str(k))
                new_obj = {'indicator': x['indicator'],
                            'crop': x['crop'],
                            'period':x['period'], 
                            'data': [ {'data': quantil_first, 'label': 'First Quantile', 'lineTension':0, 'fill': False},
                                        {'data': quantil_second, 'label': 'Second Quantile', 'lineTension':0, 'fill': False},
                                        {'data': quantil_third, 'label': 'Third Quantile', 'lineTension':0, 'fill': False}]}
                quantiles_list.append(new_obj)

            
            quantiles_list = sorted(quantiles_list, key=key_func)

            for key, value in groupby(quantiles_list, key_func):
                ls = [key, list(value)]
                quantiles_grouped.append(ls) """

            end_time_quantile = time.time()
            total_time_quantile = end_time_quantile - start_time_quantile

            content = {
                'univariate': {'data': accessions_list, 'time': total_time_subsets},
                'quantile': quantiles
                # 'quantile': {'data': quantiles_list, 'time': total_time_quantile},
            }

    return jsonify(content)


""" Service to create clusters """
@app.route('/api/v1/cluster', methods=['GET', 'POST'])
@cross_origin()
def generate_clusters():
    data = request.get_json()
     # Passport paramns
    passport_params = data['passport']
    # Indicators params
    indicators_params = data['data']
    # Multivariate params
    analysis_params = data['analysis']

    period = indicators_params[0]['period']

       # Algorithms list to use
    algorithms = analysis_params['algorithm']
    # hyperparameters to the multivariate analysis
    hyperparameters = analysis_params['hyperparameter']

    nYears = (period[1]+1) - period[0]
    # Months list calculated
    # ob = [k for k in indicators_params[0] if "month" in str(k)]
    # months number calculated
    nMonths = 12
    content = {}

    #Get crops
    crops = Crop.objects(Q(id__in = passport_params['crop']))
    result_crops = [{"id":x.id,"name": x.name} for x in crops]
    
    # Filter clauses to get accessions in order to parameters
    filter_clauses = [Q(**{filter + "__in": passport_params[filter]})
                      for filter in passport_params if len(passport_params[filter]) > 0]
    # Query to get accessions
    accessions = Accession.objects(reduce(operator.and_, filter_clauses)).select_related()

    # Cellids found in the accessions objects
    cell_ids = [x.cellid for x in accessions if x.cellid]
    # Reduce cellid list
    cell_ids = list(set(cell_ids))

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
                cell_id_crop = [x.cellid for x in accessions if x.cellid and x.crop.id == crop['id']]
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
                    "month12": x.month12}
                    for x in indicator_periods_values if  x.cellid in cell_id_crop])
        elif indicator['type'] == 'specific':
            print(indicator['crop'])
            cell_id_crop = getAccessionByCrop(crop=indicator['crop'], data=accessions)
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
                "month12": x.month12}
                for x in indicator_periods_values if  x.cellid in cell_id_crop])
        # Create a df from multivariate analysis dict
    if multivariate_values:
        try:
            lst_calculates = []
            lst_indicators = []
            lst_months = []
            others_columns = []
            analysis = clustering_analysis(algorithms=algorithms,data=multivariate_values,summary=True, n_clusters=hyperparameters['n_clusters'])

            # from df to dict
            response_analysis = analysis.to_json(orient='records')
            
            # Columns to months
            new_cols_months = dict(zip(analysis.columns[1:len(analysis.columns) - 2], 
            [x[0] + "_" + x[1] for x in analysis.columns[1:len(analysis.columns) - 2]]))
            # Columns to others items
            new_cols = dict(zip(analysis.columns[len(analysis.columns) - 2:len(analysis.columns) ], 
            [x[0] for x in analysis.columns[len(analysis.columns) - 2:len(analysis.columns)]]))
            # Assing columns
            analysis.rename(columns=new_cols_months, inplace=True)
            analysis.rename(columns=new_cols, inplace=True)

            for k,col in enumerate(analysis.columns):
                """  """
                if 'month' in col:
                    fields = col.split('_')
                    if len(fields) >= 3:
                        lst_indicators.append(fields[0] + '_' + fields[1])
                        lst_months.append(fields[2])
                    else:
                        lst_indicators.append(fields[0])
                        lst_months.append(fields[1])
                else:
                    others_columns.append(col)
            lst_indicators = list(set(lst_indicators))
            lst_months = list(set(lst_months))
            lst_months.sort()
           
            print(others_columns)
            df = analysis.groupby([others_columns[1]])
            for group in df:
                for indicator in lst_indicators:
                    # Get min
                    # getNameIndicatorByPref(indicator)
                    mini = group[1][[indicator +  '_' + x for x in lst_months]].min()
                    obj_min = {x: mini[i] for i,x in enumerate(lst_months)}
                    obj_min['operator'] = 'min'
                    obj_min['cluster'] = group[0]
                    obj_min['indicator'] = indicator
                    lst_calculates.append(obj_min)
                    # Get max
                    maxi = group[1][[indicator +  '_' + x for x in lst_months]].max()
                    obj_max = {x: maxi[i] for i,x in enumerate(lst_months)}
                    obj_max['operator'] = 'max'
                    obj_max['cluster'] = group[0]
                    obj_max['indicator'] = indicator
                    lst_calculates.append(obj_max)
                    # Get mean
                    mean = group[1][[indicator +  '_' + x for x in lst_months]].mean()
                    obj_mean = {x: mean[i] for i,x in enumerate(lst_months)}
                    obj_mean['operator'] = 'mean'
                    obj_mean['cluster'] = group[0]
                    obj_mean['indicator'] = indicator
                    lst_calculates.append(obj_mean)
                    # Get sd
                    sd = group[1][[indicator +  '_' + x for x in lst_months]].std()
                    obj_sd = {x: sd[i] for i,x in enumerate(lst_months)}
                    obj_sd['operator'] = 'sd'
                    obj_sd['cluster'] = group[0]
                    obj_sd['indicator'] = indicator
                    lst_calculates.append(obj_sd)
            # print(lst_calculates)
            df_multivariate = pd.DataFrame([s for s in lst_calculates])
            lst_months_grouped = lst_months
            lst_months_grouped.append('cluster')
            df_multivariate = df_multivariate[['indicator', 'cluster', 'operator', 'month1', 'month2', 'month3', 'month4', 'month5', 'month6',
                                                'month7','month8','month9','month10','month11','month12']]
            # print(df_multivariate)
            df = (df_multivariate.groupby(['indicator','operator'])[lst_months_grouped]
            .apply(lambda x: x.to_dict('r'))
            .reset_index(name='data')
            .to_json(orient='records'))
            # dicti = df_multivariate.pivot('indicator','operator').to_dict('index')
            min_max_mean_sd = json.loads(df)
            response_analysis_json = json.loads(response_analysis)
            print(df)

            """ lst_indicators = []
            for k,col in enumerate(analysis.columns):
                """  """
                if 'slope' in col:
                    lst_calc = [col, analysis.columns[k+1], analysis.columns[k+2]]
                    lst_indicators.append(lst_calc)
            lst_methds = [col for col in analysis.columns if 'cluster' in str(col)]
            for indicator in lst_indicators:
                for methd in lst_methds:
                    print(methd)
                    print(str(indicator[0]))
                    indicator_split = indicator[0].split("_")
                    methd_split = methd.split("_")
                    resultado =  analysis.groupby(['crop_name', str(methd)]).median()[indicator]
                    if len(indicator_split) == 3:
                        resultado['indicator'] = indicator_split[1] + '_' + indicator_split[2]
                    else:
                        resultado['indicator'] = indicator_split[1]
                    resultado['method'] = methd_split[1]
                    resultado.reset_index(inplace=True)
                    resultado.columns = ['crop', 'cluster', 'slp_med', 'mean_med', 'sd_med', 'indicator', 'method']
                    lst_calculates.append(resultado)

            print(lst_calculates)
            min_max_mean_data = pd.concat(lst_calculates)
            min_max_mean_result = min_max_mean_data.to_json(orient = "records")
            min_max_mean_parsed = json.loads(min_max_mean_result)
            
            results = analysis.to_json(orient = "records")
            parsed = json.loads(results)
            end_time_multi_ana = time.time() """
            # total_time_multi_ana = end_time_multi_ana - start_time_multi_ana
            content = {
                'data': response_analysis_json,
                # 'time': total_time_multi_ana,
                'calculate': min_max_mean_sd,
                # 'summary': multivariate_values
            }
        except ValueError as ve:
            print(str(ve))
            print("Exception")
        
    return (content)


""" Service to create clusters """
@app.route('/api/v1/clusters', methods=['GET', 'POST'])
@cross_origin()
def clusters():
    lst_df_multivariate = []
    data = request.get_json()
    # Passport paramns
    passport_params = data['passport']
    # Indicators params
    indicators_params = data['data']
    # Multivariate params
    analysis_params = data['analysis']

    period = indicators_params[0]['period']

       # Algorithms list to use
    algorithms = analysis_params['algorithm']
    # hyperparameters to the multivariate analysis
    hyperparameters = analysis_params['hyperparameter']

    nYears = (period[1]+1) - period[0]
    # Months list calculated
    ob = [k for k in indicators_params[0] if "month" in str(k)]
    # months number calculated
    nMonths = len(ob)
    content = {}

    #Get crops
    crops = Crop.objects(Q(id__in = passport_params['crop']))
    result_crops = [{"id":x.id,"name": x.name} for x in crops]

    # Filter clauses to get accessions in order to parameters
    filter_clauses = [Q(**{filter + "__in": passport_params[filter]})
                      for filter in passport_params if len(passport_params[filter]) > 0]
    # Query to get accessions
    accessions = Accession.objects(reduce(operator.and_, filter_clauses)).select_related()

    # Cellids found in the accessions objects
    cell_ids = [x.cellid for x in accessions if x.cellid]
    # Reduce cellid list
    cell_ids = list(set(cell_ids))

    for indicator in indicators_params:
        # Indicator periods ids
        periods_ids = indicator["indicator"]
        multivariate_values = []
        # Clauses to get data for multivariate analysis
        if indicator['type'] == 'generic':
            indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cell_ids})]
                # Filtering values of indicator to multivariate analysis
            indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, indicator_periods_clauses)).select_related()
            # loop for each crop present in the query
            for crop in crops:
                cell_id_crop = [x.cellid for x in accessions if x.cellid and x.crop.id == crop['id']]
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
        elif indicator['type'] == 'specific':
            print(indicator['crop'])
            cell_id_crop = getAccessionByCrop(crop=indicator['crop'], data=accessions)
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
        # Create a df from multivariate analysis dict
        df_multivariate = pd.DataFrame([s for s in multivariate_values])
        print(df_multivariate)
        for x in range(len(df_multivariate)):
            # for colums in list(df_multivariate.columns.values):
            for colums in ob:
                if indicator[colums][1] < df_multivariate.loc[x, colums] or df_multivariate.loc[x, colums] < indicator[colums][0]:
                        df_multivariate.loc[x, colums] = np.nan

        print(df_multivariate)
        lst_df_multivariate.append(df_multivariate)

    # Data parsed    
    multi_na_data = pd.concat(lst_df_multivariate)
    multi_na_result = multi_na_data.to_json(orient = "records")
    multi_na_parsed = json.loads(multi_na_result)

    if multi_na_parsed:
        try:
            lst_calculates = []
            start_time_multi_ana = time.time()
            analysis = clustering_analysis(algorithms, multi_na_parsed, nMonths, nYears, minPts=hyperparameters['minpts'], eps=hyperparameters['epsilon'],
                                        n_clusters=hyperparameters['n_clusters'], min_cluster_size=hyperparameters['min_cluster_size'])
            print(analysis)
            # lst_indicators = [col for col in analysis.columns if 'mean' or 'slope' or 'sd' in str(col)]
            lst_indicators = []
            for k,col in enumerate(analysis.columns):
                """  """
                if 'slope' in col:
                    lst_calc = [col, analysis.columns[k+1], analysis.columns[k+2]]
                    lst_indicators.append(lst_calc)
            lst_methds = [col for col in analysis.columns if 'cluster' in str(col)]
            print(lst_indicators)
            for indicator in lst_indicators:
                for methd in lst_methds:
                    print(methd)
                    print(str(indicator[0]))
                    indicator_split = indicator[0].split("_")
                    methd_split = methd.split("_")
                    resultado =  analysis.groupby(['crop_name', str(methd)]).median()[indicator]
                    if len(indicator_split) == 3:
                        resultado['indicator'] = indicator_split[1] + '_' + indicator_split[2]
                    else:
                        resultado['indicator'] = indicator_split[1]
                    resultado['method'] = methd_split[1]
                    resultado.reset_index(inplace=True)
                    resultado.columns = ['crop', 'cluster', 'slp_med', 'mean_med', 'sd_med', 'indicator', 'method']
                    print(resultado)
                    lst_calculates.append(resultado)

            print(lst_calculates)
            min_max_mean_data = pd.concat(lst_calculates)
            min_max_mean_result = min_max_mean_data.to_json(orient = "records")
            min_max_mean_parsed = json.loads(min_max_mean_result)
            
            results = analysis.to_json(orient = "records")
            parsed = json.loads(results)
            end_time_multi_ana = time.time()
            total_time_multi_ana = end_time_multi_ana - start_time_multi_ana
            content = {
                'data': parsed,
                'time': total_time_multi_ana,
                'calculate': min_max_mean_parsed
            }
        except ValueError as ve:
            print(str(ve))
            print("Exception")
    
    return jsonify(content)



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

    connect('indicatordb', host='dbmongotst01.cgiarad.org', port=27017)
    app.run(threaded=True, host='0.0.0.0', port=8437, debug=False)
    # app.run(threaded=True, port=5001, debug=True)
