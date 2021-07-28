import sys
import requests
from flask import Flask, request, jsonify, make_response
from flask_cors import cross_origin, CORS

from mongoengine import *
from models_subsets import *
from mongoengine.queryset.visitor import Q
from functools import reduce
import operator
import json
#from multivariate_analysis.dbscan_analysis import clustering_analysis

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
               "taxonomy_taxon_name": x.taxonomy_taxon_name
               }
              for x in accessions]
    rows = len(result)
    end = time.time()
    print("Result " + str(rows) + " time: " + str((end-start)*1000.0))

    return jsonify(result)


@app.route('/api/v1/crops', methods=['GET'])
@cross_origin()
def crop_list():
    crops = Crop.objects.all()

    start = time.time()
    result = [{"name": x.name, "id": x.id}
              for x in crops]
    rows = len(result)
    end = time.time()
    print("Result " + str(rows) + " time: " + str((end-start)*1000.0))

    return json.dumps(result, default=str)


"""Get indicators"""


@app.route('/api/v1/indicators', methods=['GET'])
@cross_origin()
def indicator_list():
    indicator = Indicator.objects.all()

    start = time.time()
    result = [{"name": x.name, "id": x._id}
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

    passport_params = data['passport']
    #crop_params = data['crop']
    indicators_params = data['data']
    analysis_params = data['analysis']

    period = indicators_params[0]['period']
    nYears = (period[1]+1) - period[0]
    nMonths = nYears * 12

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

    # Filtering periods
    cluster_values = []
    lst_values = []
    algorithms = [x["algorithm"] for x in analysis_params]

    # With loop and indicators
    """ for indicator in indicators_params:
        print("Indicator: " + indicator["indicator"])
        start = time.time()
        period_range = [str(p) for p in range(period[0],period[1]+1)]
        periods = IndicatorPeriod.objects(Q(indicator = indicator["indicator"]) & Q(period__in = period_range))
        periods_ids = [str(x.id) for x in periods]
        rows = len(periods)
        end = time.time()
        print("Periods: " + str(rows) + " time: " + str(end-start))

        # Filtering values of indicators
        start = time.time()
        ind_values = IndicatorValue.objects(Q(indicator_period__in = periods_ids) 
                                        & Q(month1__gte = indicator["month1"][0]) &  Q(month1__lte = indicator["month1"][1])
                                        & Q(month2__gte = indicator["month2"][0]) &  Q(month2__lte = indicator["month2"][1])
                                        & Q(month3__gte = indicator["month3"][0]) &  Q(month3__lte = indicator["month3"][1])
                                        & Q(month4__gte = indicator["month4"][0]) &  Q(month4__lte = indicator["month4"][1])
                                        & Q(month5__gte = indicator["month5"][0]) &  Q(month5__lte = indicator["month5"][1])
                                        & Q(month6__gte = indicator["month6"][0]) &  Q(month6__lte = indicator["month6"][1])
                                        & Q(month7__gte = indicator["month7"][0]) &  Q(month7__lte = indicator["month7"][1])
                                        & Q(month8__gte = indicator["month8"][0]) &  Q(month8__lte = indicator["month8"][1])
                                        & Q(month9__gte = indicator["month9"][0]) &  Q(month9__lte = indicator["month9"][1])
                                        & Q(month10__gte = indicator["month10"][0]) &  Q(month10__lte = indicator["month10"][1])
                                        & Q(month11__gte = indicator["month11"][0]) &  Q(month11__lte = indicator["month11"][1])
                                        & Q(month12__gte = indicator["month12"][0]) &  Q(month12__lte = indicator["month12"][1])
                                        & Q(cellid__in = cell_ids) )    
        rows = len(ind_values)        
        cluster_values.extend([{ "algorithms":[algorithms], 
                            "crop_name": crop_params, 
                            "pref_indicator": "cdd", 
                            #"period": x.indicator_period.period, 
                            "cellid": x.cellid,
                            "month1":x.month1,
                            "month2":x.month2,
                            "month3":x.month3}
                            for x in ind_values])        
        end = time.time()
        print("Indicator values: " + str(rows) + " time: " + str(end-start)) """

    # Without loop
    """ start = time.time()
    period_range = [str(p) for p in range(period[0],period[1]+1)]
    indicators_ids = [x["indicator"] for x in indicators_params]
    periods = IndicatorPeriod.objects(Q(indicator__in = indicators_ids) & Q(period__in = period_range))
    periods_ids = [str(x.id) for x in periods]
    rows = len(periods)
    end = time.time()
    print("Periods: " + str(rows) + " time: " + str(end-start))

    # Filtering values of indicators
    start = time.time()
    indicator = indicators_params[0]
    ind_values = IndicatorValue.objects(Q(indicator_period__in = periods_ids) 
                                        & Q(month1__gte = indicator["month1"][0]) &  Q(month1__lte = indicator["month1"][1])
                                        & Q(month2__gte = indicator["month2"][0]) &  Q(month2__lte = indicator["month2"][1])
                                        & Q(month3__gte = indicator["month3"][0]) &  Q(month3__lte = indicator["month3"][1])
                                        & Q(month4__gte = indicator["month4"][0]) &  Q(month4__lte = indicator["month4"][1])
                                        & Q(month5__gte = indicator["month5"][0]) &  Q(month5__lte = indicator["month5"][1])
                                        & Q(month6__gte = indicator["month6"][0]) &  Q(month6__lte = indicator["month6"][1])
                                        & Q(month7__gte = indicator["month7"][0]) &  Q(month7__lte = indicator["month7"][1])
                                        & Q(month8__gte = indicator["month8"][0]) &  Q(month8__lte = indicator["month8"][1])
                                        & Q(month9__gte = indicator["month9"][0]) &  Q(month9__lte = indicator["month9"][1])
                                        & Q(month10__gte = indicator["month10"][0]) &  Q(month10__lte = indicator["month10"][1])
                                        & Q(month11__gte = indicator["month11"][0]) &  Q(month11__lte = indicator["month11"][1])
                                        & Q(month12__gte = indicator["month12"][0]) &  Q(month12__lte = indicator["month12"][1])
                                        & Q(cellid__in = cell_ids) )    
    rows = len(ind_values)        
    cluster_values.extend([{ "algorithms":[algorithms], 
                            "crop_name": crop_params, 
                            "pref_indicator": "cdd", 
                            #"period": x.indicator_period.period, 
                            "cellid": x.cellid,
                            "month1":x.month1,
                            "month2":x.month2,
                            "month3":x.month3}
                            for x in ind_values])        
    end = time.time()
    print("Indicator values: " + str(rows) + " time: " + str(end-start)) """
    
    # With loop and indicatorsperiods from request
    for indicator in indicators_params:
        indicator_clauses = [Q(**{filter + "__gte": indicator[filter][0], filter + "__lte": indicator[filter][1]})
                                  for filter in indicator if "month" in str(filter)]
        periods_ids = indicator["indicator"]
        indicator_clauses = [Q(**{'indicator_period__in': periods_ids})] + indicator_clauses + [Q(**{'cellid__in': cell_ids})]
        start = time.time()
        rows = len(periods_ids)
        end = time.time()
        print("Periods: " + str(rows) + " time: " + str(end-start))

        # Filtering values of indicators
        start = time.time()
        ind_values = IndicatorValue.objects(reduce(operator.and_, indicator_clauses)).select_related()
        rows = len(list(set(ind_values)))

        print("Accessions: " + str(rows) )

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
                #for x in ind_values])

            #result = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in cluster_values)]

        lst_values = lst_values + cluster_values
        print(str(len(lst_values)))
        end = time.time()
        print("Indicator values:" + str(rows) + " time: " + str(end-start))
    multivariety_analysis = []
    # Runing multivariable analysis
    #start = time.time()
    # analysis = clustering_analysis(algorithms, "crop_name": crop_name, "pref_indicator": pref_indicator, "period":period, "cellid": cellid)
    #end = time.time()
    #print("Multivariable analysis. time: " + str(end-start))

    return jsonify(lst_values)


if __name__ == "__main__":

    connect('indicatordb', host='dbmongotst01.cgiarad.org', port=27017)
    app.run(threaded=True, port=5001, debug=True)
