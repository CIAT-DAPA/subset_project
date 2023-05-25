from pandas._libs.missing import NA
from pandas.core import groupby

from flask import Flask, request, jsonify, make_response
from flask_cors import cross_origin, CORS
import werkzeug
import numpy as np

from mongoengine import *
from models_subsets import *
from mongoengine.queryset.visitor import Q
from bson import ObjectId

from functools import reduce
import operator
import json
from multivariate_analysis.clustering_analysis import clustering_analysis
import pandas as pd
from itertools import groupby
import time
from multivariate_analysis.core_collection import stratcc
import math

app = Flask(__name__)

@app.route('/api/v1/indicators-range', methods=['GET', 'POST'])
@cross_origin()
def ranges_bins():
    # get the input parameters
    data = request.get_json()
    month_fields = ['month1','month2', 'month3', 'month4', 'month5', 'month6', 'month7', 'month8', 'month9',
                'month10', 'month11', 'month12']
    
    ind_periods_ids = data['ind_periods']
    ind_periods_ids = [ObjectId(id) for id in ind_periods_ids]

    cellids_crops = data['cellid_list']
    all_distinct_cellids = [int(cell) for x in cellids_crops for cell in x['cellids']]
   
    #t1= time.time()
    min_max_pipeline = [
            { 
                "$match": {
                    "$and": [
                        {"indicator_period": {"$in": ind_periods_ids}}, 
                        {"cellid": {"$in": all_distinct_cellids}},
                        {'value_c': { '$exists': False}}
                    ]
                } 
            }, {
                "$addFields": {
                    "months_data": {"$objectToArray": "$$ROOT"}
                }
            }, {
                "$addFields":{
                    "months_data": {
                        "$filter": {
                            "input": "$months_data",
                            "as": "tuple",
                            "cond": {
                                "$eq": [{"$substrBytes": ["$$tuple.k", 0, 5]},"month"]
                            },
                        },
                    },
                }
            }, {
                "$addFields": {
                    "months_data": {
                        "$concatArrays":["$months_data", [{"k":"average","v":{"$avg": "$months_data.v"}}]]
                    },
                }
            }, {
                "$addFields": {
                    "months_data": {"$arrayToObject":"$months_data"}
                }
            }, {
                "$group": {
                    "_id": "$indicator_period",
                    "min_avg": {
                        "$min": "$months_data.average",
                    },
                    "max_avg": {
                        "$max": "$months_data.average",
                    },
                    "min_value": {
                        "$min": "$value"
                    },
                    "max_value": {
                        "$max": "$value"
                    }
                }
            }, {
                "$lookup": {
                    "from": "indicators_indicatorperiod", 
                    "localField": "_id", 
                    "foreignField": "_id", 
                    "as": "indicator_period"
                }
            }, {
                "$lookup": {
                    "from": "indicators_indicator", 
                    "localField": "indicator_period.indicator", 
                    "foreignField": "_id", 
                    "as": "indicator_name"
                }
            }, 
            {
                "$lookup": {
                    "from": "crop", 
                    "localField": "indicator_name.crop", 
                    "foreignField": "_id", 
                    "as": "crop_name"
                }
            }, 
            {
                "$unwind": {"path": "$crop_name",
                        "includeArrayIndex": 'crop_index'}
            },
            {
                "$unwind": {"path": "$indicator_name",
                    "includeArrayIndex": 'ind_index'
                }
            }, {
                "$project": {
                    "crop": "$crop_name.name",
                    "indicator": "$indicator_name.name",
                    "min_avg": "$min_avg",
                    "max_avg": "$max_avg",
                    "min_value": "$min_value",
                    "max_value": "$max_value"
                }
            },
    ]

    min_max_result = list(IndicatorValue.objects.aggregate(*min_max_pipeline))
    
    """ t2=time.time()
    print("min max...", t2-t1) """

    min_max_result = [{key[:3] if (key[:3] == 'max' or key[:3] == "min") and value is not None else key:value for key, value in dict.items()} for dict in min_max_result]

    min_max = [{key: value for key, value in dict.items() if key != '_id' and value is not None} for dict in min_max_result]
    
    quantile_result = []
    for ind in min_max_result:
        # Apply Sturges Rule to define the optimal number of bins
        bins = math.ceil(math.log2(len(all_distinct_cellids))+1)
        
        if ind['max'] == ind['min']:
            bins_boundaries = [math.floor(ind['min']), math.ceil(ind['max'])]
        else:
            bins_boundaries = np.linspace(math.floor(ind['min']), math.ceil(ind['max']), bins+1)
            bins_boundaries = list(bins_boundaries)
            rounded_bins_boundaries = [round(elt, 3) for elt in bins_boundaries]
        
        for idx, elt in enumerate(rounded_bins_boundaries):
            if idx < len(rounded_bins_boundaries)-2:
                count_pipeline = [
                { 
                    "$match": {
                        "$and": [
                            {"indicator_period": {"$in": [ObjectId(ind['_id'])]}}, 
                            {"cellid": {"$in": all_distinct_cellids}},
                            {'value_c': { '$exists': False}}
                        ]
                    }
                }, {
                    "$addFields": {
                        "average": {"$objectToArray": "$$ROOT"}
                    }
                }, {
                    "$addFields":{
                        "average": {
                            "$filter": {
                                "input": "$average",
                                "as": "tuple",
                                "cond": {
                                    "$eq": [{"$substrBytes": ["$$tuple.k", 0, 5]}, "month"]
                                },
                            },
                        },
                    }
                }, {
                    "$addFields": {
                        "average": {
                            "$avg": "$average.v"
                        }
                    },
                }, {
                    "$match": {
                        "$or": [{"average": {"$gte": rounded_bins_boundaries[idx], "$lt":rounded_bins_boundaries[idx+1]}}]
                             + [{"value": {"$gte": rounded_bins_boundaries[idx], "$lt":rounded_bins_boundaries[idx+1]}}]
                    }
                }, {
                    "$count": "cellid"                    
                }]

            elif idx == len(rounded_bins_boundaries)-2:
                count_pipeline = [
                { 
                    "$match": {
                        "$and": [
                            {"indicator_period": {"$in": [ObjectId(ind['_id'])]}}, 
                            {"cellid": {"$in": all_distinct_cellids}},
                            {'value_c': { '$exists': False}}
                        ]
                    } 
                },  {
                    "$addFields": {
                        "average": {"$objectToArray": "$$ROOT"}
                    }
                }, {
                    "$addFields":{
                        "average": {
                            "$filter": {
                                "input": "$average",
                                "as": "tuple",
                                "cond": {
                                    "$eq": [{"$substrBytes": ["$$tuple.k", 0, 5]}, "month"]
                                },
                            },
                        },
                    }
                }, {
                    "$addFields": {
                        "average": {
                            "$avg": "$average.v"
                        }
                    },
                }, {
                    "$match": {
                        "$or": [{"average": {"$gte": rounded_bins_boundaries[idx], "$lte":rounded_bins_boundaries[idx+1]}}]
                             + [{"value": {"$gte": rounded_bins_boundaries[idx], "$lte":rounded_bins_boundaries[idx+1]}}]
                    }
                }, {
                    "$count": "cellid"                    
                }]
            else:
                break

            count_result = list(IndicatorValue.objects.aggregate(*count_pipeline))
            
            quantile_result.extend([{
                "crop": ind['crop'],
                "indicator": ind['indicator'],
                "quantile": "({},{}]".format(rounded_bins_boundaries[idx],rounded_bins_boundaries[idx+1]),
                "size": count_result[0]['cellid'] if count_result else 0
            }])
    
    """ t3=time.time()
    print("bins....", t3-t2) """

    #pipeline to get categories proportions for categorical indicators
    percentage_pipeline = [{ 
                "$match": {
                    "$and": [
                        {"indicator_period": {"$in": ind_periods_ids}}, 
                        {"cellid": {"$in": all_distinct_cellids}},
                        {'value_c': { '$exists': True}}
                    ]
                } 
                }, {
                "$group": {
                    "_id": {"indicator": "$indicator_period",
                            "category": "$value_c"},
                    "count": {"$sum": 1}                    
                }
                }, {
                "$group": {
                    "_id": "$_id.indicator",
                    "abs_total": {"$sum": "$count"},
                    "categories": { 
                        "$push": { 
                            "category":"$_id.category",
                            "total":"$count"
                        }
                    }                  
                } 
                }, {
                "$unwind": "$categories"
                }, {
                "$project": {
                    "category":"$categories.category",
                    "percent": {"$multiply":[{"$divide":["$categories.total","$abs_total"]},100]}
                    }
                }, {
                "$lookup": {
                    "from": "indicators_indicatorperiod", 
                    "localField": "_id", 
                    "foreignField": "_id", 
                    "as": "indicator_period"
                }
                }, {
                "$lookup": {
                    "from": "indicators_indicator", 
                    "localField": "indicator_period.indicator", 
                    "foreignField": "_id", 
                    "as": "indicator_name"
                }
                }, {
                "$unwind": "$indicator_name"
                }, {
                "$project": {
                    "indicator": "$indicator_name.name",
                    "category": "$category",
                    "proportion": "$percent"
                }
            }]
    
    percentage_result = list(IndicatorValue.objects.aggregate(*percentage_pipeline))
    proportion = [{key: value for key, value in dict.items() if key != '_id'} for dict in percentage_result]
    
    """ t4=time.time()
    print("percentage...", t4-t3)
    print(percentage_result) """
 
    content = {
        'min_max': min_max,
        'quantile': quantile_result,
        'proportion': proportion
    }
    
    return jsonify(content)

# define a function for key
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

def restrict_months_list(low, up):
        months_list = []
        if low<up:
            months_list = list(range(low, up+1))
        elif low>up:
            months_list = list(range(low, 13))
            months_list.extend(list(range(1,up+1))) if up != 1 else months_list.append(1)
        else:
            months_list = [low]
        return months_list

def filterData(crops, cell_ids, indicators_params):
    
    subset = []
    
    for indicator in indicators_params:
        # Indicator periods ids
        periods_ids = indicator["indicator"]
        months_filter_range = indicator["months"]
        
        if months_filter_range:
            low = months_filter_range[0]
            up = months_filter_range[1]
            months_filter = restrict_months_list(low, up)
        
        range_values = indicator["range"]

        if indicator['type'] == 'generic':
            print(indicator['name'])
            filter_by_avg_pipeline = [
            { 
                "$match": {
                    "$and": [
                        {"indicator_period": ObjectId(periods_ids[0])}, 
                        {"cellid": {"$in": cell_ids}}
                    ]
                } 
            }, {
                "$addFields": {
                    "months_data": {"$objectToArray": "$$ROOT"}
                }
            }, {
                "$addFields":{
                    "months_data": {
                        "$filter": {
                            "input": "$months_data",
                            "as": "tuple",
                            "cond": {
                                "$eq": [{"$substrBytes": ["$$tuple.k", 0, 5]},"month"]
                            },
                        },
                    },
                }
            }, {
                "$addFields": {
                    "months_data": {
                        "$concatArrays":["$months_data", [{"k":"average","v":{"$avg": "$months_data.v"}}]]
                    },
                }
            }, {
                "$addFields": {
                    "months_data": {"$arrayToObject":"$months_data"}
                }
            }, {
                "$match": {
                    "$and":[
                        {"months_data.average":{"$gte":range_values[0]}},
                        {"months_data.average":{"$lte":range_values[1]}}
                    ]
                }
            }, {
                "$lookup":{
                    "from": "indicators_indicatorperiod",
                    "localField": "indicator_period",
                    "foreignField": "_id",
                    "as": "indicator_period",
                }
            }, {
                "$lookup":{
                    "from": "indicators_indicator",
                    "localField": "indicator_period.indicator",
                    "foreignField": "_id",
                    "as": "indicator_name",
                }
            }, {
                "$lookup":{
                    "from": "crop",
                    "localField": "indicator_name.crop",
                    "foreignField": "_id",
                    "as": "crop_name",
                }
            }, {
                "$project": {
                    "crop": {"$let": {
                                "vars": {
                                    "firstMember": {
                                        "$arrayElemAt": [
                                            "$crop_name",
                                            0
                                        ]
                                    }
                                },
                                    "in": "$$firstMember.name"
                            }},
                    "indicator": {"$let": {
                                    "vars": {
                                        "firstMember": {
                                            "$arrayElemAt": [
                                                "$indicator_name",
                                                0
                                            ]
                                        }
                                    },
                                        "in": "$$firstMember.name"
                                }},
                    "pref_indicator":{"$let": {
                                        "vars": {
                                            "firstMember": {
                                                "$arrayElemAt": [
                                                    "$indicator_name",
                                                    0
                                                ]
                                            }
                                        },
                                        "in": "$$firstMember.pref"
                                    }},
                    "indicator_period":{"$let": {
                                            "vars": {
                                                "firstMember": {
                                                    "$arrayElemAt": [
                                                        "$indicator_period",
                                                        0
                                                    ]
                                                }
                                            },
                                            "in": "$$firstMember.period"
                                        }},
                    "cellid":1,
                    "average":"$months_data.average",
                    **{f"month{month}": 1 for month in months_filter}
                }
            }            
            ]

            indicator_periods_values = IndicatorValue.objects.aggregate(*filter_by_avg_pipeline)

            if indicator_periods_values:
                #loop for each crop present in the request params
                for crop in crops:
                    # Dict to multivariate analysis
                    cell_id_crop = [cell for x in crops for cell in x['cellids'] if crop['crop'].lower() == x['crop'].lower()]
                    subset.extend([{
                        **{"crop": crop['crop'].lower(),
                        "pref_indicator": x['pref_indicator'],
                        "indicator": x['indicator'],
                        "cellid": x['cellid']},
                        **{f"month_{month}": x[f"month{month}"] for month in months_filter},
                        **{"period": x['indicator_period']}}
                        for x in indicator_periods_values if x['cellid'] in cell_id_crop])
            else:
                raise ValueError('No accessions matching the filters applied to the indicator: '+ indicator['name'])
        
        elif indicator['type'] == 'specific':
            print(indicator['name'])
            crp = indicator['crop'].lower()
            cell_id_crop = [cell for x in crops for cell in x['cellids'] if crp == x['crop'].lower()]
            
            filter_by_avg_pipeline = [
            { 
                "$match": {
                    "$and": [
                        {"indicator_period": ObjectId(periods_ids[0])}, 
                        {"cellid": {"$in": cell_id_crop}}
                    ]
                } 
            }, {
                "$addFields": {
                    "months_data": {"$objectToArray": "$$ROOT"}
                }
            }, {
                "$addFields":{
                    "months_data": {
                        "$filter": {
                            "input": "$months_data",
                            "as": "tuple",
                            "cond": {
                                "$eq": [{"$substrBytes": ["$$tuple.k", 0, 5]},"month"]
                            },
                        },
                    },
                }
            }, {
                "$addFields": {
                    "months_data": {
                        "$concatArrays":["$months_data", [{"k":"average","v":{"$avg": "$months_data.v"}}]]
                    },
                }
            }, {
                "$addFields": {
                    "months_data": {"$arrayToObject":"$months_data"}
                }
            }, {
                "$match": {
                    "$and":[
                        {"months_data.average":{"$gte":range_values[0]}},
                        {"months_data.average":{"$lte":range_values[1]}}
                    ]
                }
            }, {
                "$lookup":{
                    "from": "indicators_indicatorperiod",
                    "localField": "indicator_period",
                    "foreignField": "_id",
                    "as": "indicator_period",
                }
            }, {
                "$lookup":{
                    "from": "indicators_indicator",
                    "localField": "indicator_period.indicator",
                    "foreignField": "_id",
                    "as": "indicator_name",
                }
            }, {
                "$lookup":{
                    "from": "crop",
                    "localField": "indicator_name.crop",
                    "foreignField": "_id",
                    "as": "crop_name",
                }
            }, {
                "$project": {
                    "crop": {"$let": {
                                "vars": {
                                    "firstMember": {
                                        "$arrayElemAt": [
                                            "$crop_name",
                                            0
                                        ]
                                    }
                                },
                                    "in": "$$firstMember.name"
                            }},
                    "indicator": {"$let": {
                                    "vars": {
                                        "firstMember": {
                                            "$arrayElemAt": [
                                                "$indicator_name",
                                                0
                                            ]
                                        }
                                    },
                                        "in": "$$firstMember.name"
                                }},
                    "pref_indicator":{"$let": {
                                        "vars": {
                                            "firstMember": {
                                                "$arrayElemAt": [
                                                    "$indicator_name",
                                                    0
                                                ]
                                            }
                                        },
                                        "in": "$$firstMember.pref"
                                    }},
                    "indicator_period":{"$let": {
                                            "vars": {
                                                "firstMember": {
                                                    "$arrayElemAt": [
                                                        "$indicator_period",
                                                        0
                                                    ]
                                                }
                                            },
                                            "in": "$$firstMember.period"
                                        }},
                    "cellid":1,
                    "average":"$months_data.average",
                    **{f"month{month}": 1 for month in months_filter}
                }
            }            
            ]

            indicator_periods_values = IndicatorValue.objects.aggregate(*filter_by_avg_pipeline)
            if indicator_periods_values:
                subset.extend([{
                    **{"crop": crp,
                    "pref_indicator": x['pref_indicator'],
                    "indicator": x['indicator'],
                    "cellid": x['cellid']},
                    **{f"month_{month}": x[f"month{month}"] for month in months_filter},
                    **{"period": x['indicator_period']}}
                    for x in indicator_periods_values if x['cellid'] in cell_id_crop])
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
                    # Whisker high
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
        low = months_filter_range[0]
        up = months_filter_range[1]
        months_filter = restrict_months_list(low, up)
    
    # Algorithms list to use
    algorithms = analysis_params['algorithm']
    # hyperparameters to the multivariate analysis
    hyperparameters = analysis_params['hyperparameter']
    
    hyperparameters={"max_cluster" if k == 'n_clusters' else k:v for k,v in hyperparameters.items()}    
    
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
                    for x in indicator_periods_values if x.cellid in crop['cellids']])
        
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
                df_multivariate = pd.DataFrame(lst_calculates)
                
                df_multivariate = df_multivariate[['indicator','crop', 'operator']+cluster_columns+lst_months]
                
                df_calculate = (df_multivariate.groupby(['indicator','operator', 'crop'])[lst_months+cluster_columns]
                .apply(lambda x: x.stack().groupby(level=0).agg(lambda y : y.reset_index(level=0,drop=True).to_dict()).tolist())
                .reset_index(name='data')
                .to_json(orient='records'))
                
                min_max_mean_sd = json.loads(df_calculate)
                
            summary_json = json.dumps(lst_summary)
            # converting string to json
            final_dictionary = json.loads(summary_json)
            response_analysis_json = json.loads(response_analysis)
  
            # Calculate quantiles by month
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
                df_quantiles = pd.DataFrame(obj_list_quantiles)
                lst_field_quantiles = ['Q1', 'Q2', 'Q3', 'month', 'whisker_low', 'whisker_high']
                
                df_quantiles_grouped = (df_quantiles.groupby(['indicator','crop'])[cluster_columns+lst_field_quantiles]
                .apply(lambda x: x.stack().groupby(level=0).agg(lambda y : y.reset_index(level=0,drop=True).to_dict()).tolist())
                .reset_index(name='data')
                .to_json(orient='records'))
                
                quantile_data = json.loads(df_quantiles_grouped)
            
            content = {
                'data': response_analysis_json,
                'calculate': min_max_mean_sd if lst_calculates else [],
                'quantile': quantile_data if obj_list_quantiles else [],
                'summary': final_dictionary,
                'proportion': proportion_data
            }
                
        except ValueError as ve:
            print(str(ve))
        
    return (content)


""" Service to get core collection of the selected subset """
@app.route('/api/v1/core-collection', methods=['GET', 'POST'])
@cross_origin()
def get_core_collection():
    data = request.get_json()

    indicators_params = data['indicators']
    amount = data['amount']
    cellids = data['cellIds']
    cellids = list(set(cellids))
    months_range = data['months']

    if months_range:
        low = months_range[0]
        up = months_range[1]
        months_filter = restrict_months_list(low, up)
    
    #get indicators data
    indicators_data = []
    for indicator in indicators_params:
        
        periods_ids = indicator["indicator"]
        if indicator['type'] == 'generic' or indicator['type'] == 'specific':
            indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cellids})]
            indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, indicator_periods_clauses)).select_related()
                   
            indicators_data.extend([{
                **{"pref_indicator": x.indicator_period.indicator.pref,
                "cellid": x.cellid},
                **{f"month{month}": getattr(x, f"month{month}") for month in months_filter}}
                for x in indicator_periods_values])
            
        elif indicator['type'] == 'extracted':
            indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cellids})]
            indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, indicator_periods_clauses)).select_related()
            
            indicators_data.extend([{
                    "pref_indicator": x.indicator_period.indicator.pref,
                    "cellid": x.cellid,
                    "value": x.value}
                    for x in indicator_periods_values])
            
        elif indicator['type'] == 'categorical':
            indicator_periods_clauses = [Q(**{'indicator_period__in': periods_ids})] + [Q(**{'cellid__in': cellids})]
            indicator_periods_values = IndicatorValue.objects(reduce(operator.and_, indicator_periods_clauses)).select_related()
            
            indicators_data.extend([{
                "pref_indicator": x.indicator_period.indicator.pref,
                "cellid": x.cellid,
                "category": x.value_c}
                for x in indicator_periods_values])

    indicators_df = pd.DataFrame(indicators_data, dtype='object')

    months_colnames = [col for col in indicators_df.columns if 'month' in col]
    value_colname = [col for col in indicators_df.columns if 'value' in col]
    category_colname = [col for col in indicators_df.columns if 'category' in col]

    months_slice = indicators_df[['cellid','pref_indicator']+months_colnames]
    value_slice = indicators_df[['cellid','pref_indicator']+value_colname]
    category_slice = indicators_df[['cellid','pref_indicator']+category_colname]

    merged_slices = pd.DataFrame([])

    for s in [months_slice, value_slice, category_slice]:
        s = s.dropna()
        s = s.pivot(index = 'cellid', columns = ['pref_indicator'])
        s = s.swaplevel(0, 1, axis = 1)
        s.columns = s.columns.map('_'.join)
        s = s.reset_index()

        merged_slices = s if merged_slices.empty else s.merge(merged_slices, on='cellid')

    merged_slices.reset_index(drop=True, inplace=True)
    ind_data = merged_slices
    
    ind_data = ind_data.dropna(axis=0)
    ind_data.reset_index(drop=True, inplace=True)
    
    core_collection = stratcc(x=ind_data, nb_entries=amount)
    cc_cellids = core_collection['cellid']

    content = {
        'cellids': list(cc_cellids)
    }

    return content

if __name__ == "__main__":

    #connect('indicatordb', host='localhost', port=27017)
    connect('indicatordb', host='dbmongotst01.cgiarad.org', port=27017)

    #app.wsgi_app = ProfilerMiddleware(app.wsgi_app, sort_by=('time', 'calls'), restrictions=[60], profile_dir='.')
    app.run(threaded=True, port=5001, debug=True)
