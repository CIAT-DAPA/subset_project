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

    return jsonify(result)


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


"""Get indicators"""


@app.route('/api/v1/indicators', methods=['GET'])
@cross_origin()
def indicator_list():
    indicator = Indicator.objects.all()

    start = time.time()
    result = [{"name": x.name, "id": x._id, "pref": x.pref, "indicator_type": x.indicator_type.name, "crop": x.crop}
              for x in indicator]
    rows = len(result)
    end = time.time()
    print("Result " + str(rows) + " time: " + str((end-start)*1000.0))

    return json.dumps(result, default=str)


"""Get indicator_period objects"""


@app.route('/api/v1/indicator-period', methods=['GET'])
@cross_origin()
def indicator_period_list():
    indicator_period = IndicatorPeriod.objects().select_related()
    result = [{"id": x.id, "indicator": x.indicator._id, "period": x.period}
              for x in indicator_period]

    return json.dumps(result, default=str)


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

    print("Crops: " + str(len(crops)) )
    # Filtering accessions according to passport data
    start = time.time()

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
    print(str(len(cell_ids)))

    # Filtering periods

    multivariate_values = []
    lst_values = []
    lst_df_multivariate = []

    """ Query to univariate analysis """    
    # With loop and indicatorsperiods from request
    for indicator in indicators_params:
        # month dict for each indicator in the query
        months_filter = [{x: indicator[x] for x in indicator if 'month' in x}]

        """ indicator_clauses = [Q(**{filter + "__gte": indicator[filter][0], filter + "__lte": indicator[filter][1]})
                                  for filter in indicator if "month" in str(filter)] """

        # Indicator periods ids
        periods_ids = indicator["indicator"]
        # Clauses to get data for multivariate analysis
        indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cell_ids})]
        # Clauses to get data for univariate analysis
        # indicator_clauses = [Q(**{'indicator_period__in': periods_ids})] + indicator_clauses + [Q(**{'cellid__in': cell_ids})]

        start = time.time()
        rows = len(periods_ids)
        end = time.time()
        print("Periods: " + str(rows) + " time: " + str(end-start))

        # Filtering values of indicators
        # start = time.time()
        # ind_values = IndicatorValue.objects(reduce(operator.and_, indicator_clauses)).select_related()
        # rows = len(ind_values)
        # print("Univariate: " + str(rows) )

        # Filtering values of indicator to multivariate analysis
        indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, indicator_periods_clauses)).select_related()
        rows_indicator = len(indicator_periods_values)
        print("multivariate: " + str(rows_indicator))

        # loop for each crop present in the query
        for crop in result_crops:
            cell_id_crop = [x.cellid for x in accesions if x.cellid and x.crop.id == crop['id']]
            # cellid list from crop
            cell_id_crop = list(set(cell_id_crop))
            """ cluster_values.extend([{
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
                for x in ind_values if  x.cellid in cell_id_crop]) """
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
        df_univariate = df_multivariate
        # Query to filter the univariate data
        query_gt = ' & '.join([f'{k}>{v[0]}' for k, v in months_filter[0].items()])
        query_lt = ' & '.join([f'{k}<{v[1]}' for k, v in months_filter[0].items()])
        query = query_gt + ' & ' + query_lt

        # Filter univariate data from query
        univ = df_univariate.query(query)
        print("Univariate: " + str(len(univ)))
        # Append to list for each indicator in the query
        lst_values.append(univ)

        # loop to generate Nan values for each column month doesn't match with the range of values 
        for x in range(len(df_multivariate)):
            # for colums in list(df_multivariate.columns.values):
            for colums in ob:
                if indicator[colums][1] <= df_multivariate.loc[x, colums] or df_multivariate.loc[x, colums] <= indicator[colums][0]:
                        df_multivariate.loc[x, colums] = np.nan

        print(df_multivariate)
        lst_df_multivariate.append(df_multivariate)
        # lst_values = lst_values + cluster_values
        end = time.time()
    
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

        """ End Process to get percentils """

        """ Process Multivariate analysis """
        # Runing multivariable analysis
        try:
            analysis = clustering_analysis(algorithms, multivariate_parsed, nMonths, nYears, minPts=hyperparameters['minpts'], eps=hyperparameters['epsilon'],
                                        n_clusters=hyperparameters['n_clusters'], min_cluster_size=hyperparameters['min_cluster_size'])
            result = analysis.to_json(orient = "records")
            parsed = json.loads(result)
            content = {
                'data': univariate_parsed,
                'multivariety_analysis': parsed,
                'quantile': quantiles
            }
        except ValueError as ve:
            print(str(ve))
            content = {
                'data': univariate_parsed,
                'multivariety_analysis': [],
                'quantile': quantiles
            }
            print(content)        

        """ End process multivariate analysis  """

        """ Final service content """

    else:
        try:
            analysis = clustering_analysis(algorithms, multivariate_parsed, nMonths, nYears, minPts=hyperparameters['minpts'], eps=hyperparameters['epsilon'],
                                        n_clusters=hyperparameters['n_clusters'], min_cluster_size=hyperparameters['min_cluster_size'])
            result = analysis.to_json(orient = "records")
            parsed = json.loads(result)
            content = {
                'data': [],
                'multivariety_analysis': parsed,
                'quantile': []
            }
        except ValueError as ve:
            print(str(ve))
            content = {
                'data': [],
                'multivariety_analysis': [],
                'quantile': []
            }
            print(content)        


    return jsonify(content)

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
    app.run(threaded=True, port=5001, debug=True)
