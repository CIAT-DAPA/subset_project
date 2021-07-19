import sys
import requests
from flask import Flask, request, jsonify, make_response
from flask_cors import cross_origin#CORS

from mongoengine import *
from models_subsets import *
from mongoengine.queryset.visitor import Q

#from multivariate_analysis.dbscan_analysis import clustering_analysis

import time

app = Flask(__name__)

@app.route('/api/v1/accessions', methods=['GET', 'POST'])
@cross_origin()
def accessions_list():  
    data = request.get_json()  

    start = time.time()
    accesions = Accession.objects(Q(crop__in = data["crop"]))
    end = time.time()
    print("Accessions: " + str(len(accesions)) + " time: " + str((end-start)*1000.0))

    start = time.time()
    result = [{"name":x.name, 
                "number":x.number, 
                "acq_date":x.acq_date, 
                "coll_date":x.coll_date, 
                "country_name":x.country_name,
                "institute_fullname":x.institute_fullname, 
                "institute_acronym":x.institute_acronym, 
                #"crop":x.crop.name,
                "geo_lon":x.geo_lon, 
                "geo_lat":x.geo_lat,
                "geo_ele":x.geo_ele,
                "taxonomy_genus":x.taxonomy_genus, 
                "taxonomy_sp_author":x.taxonomy_sp_author,
                "taxonomy_species":x.taxonomy_species, 
                "taxonomy_taxon_name":x.taxonomy_taxon_name} 
                for x in accesions]
    end = time.time()
    print("Result time: " + str((end-start)*1000.0))

    return jsonify(result)

@app.route('/api/v1/subsets', methods=['GET', 'POST'])
@cross_origin()
def subsets():  
    data = request.get_json()  

    passport_params = data['passport']
    crop_params = data['crop']
    indicators_params = data['data']    
    analysis_params = data['analysis']

    period = indicators_params[0]
    nYears = (period['period'][1]+1) - period['period'][0]
    nMonths = nYears * 12
    
    # Filtering accessions according to passport data    
    start = time.time()
    #accesions = Accession.objects(Q(crop__in = crop_params) & Q(country_name__in = passport_params["countries"]))
    accesions = Accession.objects(Q(crop__in = crop_params))
    cell_ids = [x.cellid for x in accesions if x.cellid]
    cell_ids = list(set(cell_ids))
    rows = len(accesions)
    end = time.time()
    print("Accessions: " + str(rows) + " time: " + str(end-start))

    # Filtering periods
    start = time.time()
    indicator = indicators_params[0]
    #periods = IndicatorPeriod.objects(Q(indicator = indicator["indicator"]) & Q(period__gte = indicator["period"][0]) & Q(period__lte = indicator["period"][1]))
    period_range = [str(p) for p in range(indicator["period"][0],indicator["period"][1]+1)]
    periods = IndicatorPeriod.objects(Q(indicator = indicator["indicator"]) & Q(period__in = period_range))
    periods_ids = [str(x.id) for x in periods]
    rows = len(periods)
    end = time.time()
    print("Periods: " + str(len(periods)) + " time: " + str(end-start))

    # Filtering values of indicators
    start = time.time()
    ind_values = IndicatorValue.objects(Q(indicator_period__in = periods_ids) 
                                    & Q(month1__gte = indicator["month1"][0]) &  Q(month1__lte = indicator["month1"][1])
                                    & Q(month2__gte = indicator["month2"][0]) &  Q(month2__lte = indicator["month2"][1])
                                    & Q(month3__gte = indicator["month3"][0]) &  Q(month3__lte = indicator["month3"][1])
                                    & Q(cellid__in = cell_ids) )    
    algorithms = [x["algorithm"] for x in analysis_params]
    cluster_values = [{ "algorithms":[algorithms], 
                        "crop_name": crop_params, 
                        "pref_indicator": "cdd", 
                        #"period": x.indicator_period.period, 
                        "cellid": x.cellid,
                        "month1":x.month1,
                        "month2":x.month2,
                        "month3":x.month3}
                        for x in ind_values]
    rows = len(ind_values)
    rows2 = len(cluster_values)
    end = time.time()
    print("Indicator values: " + str(rows) + " cluster values: " + str(rows2) + " time: " + str(end-start))
    
    # Runing multivariable analysis
    #start = time.time()
    #analysis = clustering_analysis(algorithms, "crop_name": crop_name, "pref_indicator": pref_indicator, "period":period, "cellid": cellid)
    #end = time.time()
    #print("Multivariable analysis. time: " + str(end-start))

    result = "Hola"
    return jsonify(result)


if __name__ == "__main__":
    
    connect('indicatordb', host='dbmongotst01.cgiarad.org', port=27017)
    app.run(threaded=True, port=5001, debug=True)