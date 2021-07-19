import requests

request_body = {}
#request_body["data"] = [
        
#        {"indicator_name": "Extreme daily precipitation","month1__range": [20,60], "month2__range": [20,60], "month3__range": [20,60],  "month4__range": [20,60],"period": [1983,1985]},
#        {"indicator_name": "Consecutive dry days","month1__range": [20,60], "month2__range": [20,60], "month3__range": [20,60],  "month4__range": [20,60],"period": [1983,1985]}

        #{ ​​"indicator_name": "Extreme daily precipitation","month1__range": [20,60], "month2__range": [20,60],"month3__range": [20,60],"month4__range": [20,60],"period": [1983,1985]}​​​
        #{​​​"indicator_name": "Consecutive dry days","month1__range": [20,60], "month2__range": [20,60], "month3__range": [20,60],"month4__range": [20,60],  "period": [1983,1985]}​​​
#    ]

request_body = {
    #"data": [ {"indicator": "60818c34fc024440e44621f4","month1":[0,109], "month2":[0,109], "month3":[0,109],"period": [1983,2016]}],
    "data" :[
                {"indicator": "60818c34fc024440e44621f4","month1":[0,109], "month2":[0,109], "month3":[0,109],"month4":[0,109], "month5":[0,109], "month6":[0,109], "month7":[0,109],"month8":[0,109], "month9":[0,109], "month10":[0,109], "month11":[0,109],"month12":[0, 109],"period": [1983,2016]},
                {"indicator": "60818c34fc024440e44621f3","month1":[0,109], "month2":[0,109], "month3":[0,109],"month4":[0,109], "month5":[0,109], "month6":[0,109], "month7":[0,109],"month8":[0,109], "month9":[0,109], "month10":[0,109], "month11":[0,109],"month12":[0, 109],"period": [1983,2016]},
                {"indicator": "60818c34fc024440e44621f2","month1":[0,109], "month2":[0,109], "month3":[0,109],"month4":[0,109], "month5":[0,109], "month6":[0,109], "month7":[0,109],"month8":[0,109], "month9":[0,109], "month10":[0,109], "month11":[0,109],"month12":[0, 109],"period": [1983,2016]}
        ],
    "crop": ["60818b1efc024440e44621d3"],
    "passport": {"countries": ["Mexico"]},
    #"passport": {"countries": []},
    "analysis": [{"algorithm":"dbscan" }]
}

#{"indicator_period__indicator__name": "Extreme daily precipitation","month1": 0.767530918, "month2": 0.325088953, "month3": 0.406348705,  "indicator_period__period__range": [1983,1983]}
        #{"indicator_period__indicator__name": "Extreme daily precipitation","month1__range": [0,1], "month2__range": [0,1], "month3__range": [0,1],  "indicator_period__period__range": [1983,1983]}


#request_body = { "crop": ["60818b1efc024440e44621d3"],
#                "passport": [ {"country_name__in": []}]}

print(request_body)
#response = requests.post('http://localhost:8000/api/ind-value/',json=request_body)
#response = requests.post('http://localhost:8000/api/accessions/',json=request_body)


#response = requests.post('http://localhost:5001/api/v1/accessions',json=request_body)
response = requests.post('http://localhost:5001/api/v1/subsets',json=request_body)


print(response.content)