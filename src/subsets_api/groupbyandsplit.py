import pandas as pd
import numpy as np
from pandas.core import groupby  
from functools import reduce

csv = pd.read_csv('andeanIds.csv')

# print(csv)
lst_results = []


periods = range(1983,2017)
for index, row in csv.iterrows():
        obj_min = {"indicator": row['_id'], "period": 'min'}
        obj_max = {"indicator": row['_id'], "period": 'max'}
        obj_mean = {"indicator": row['_id'], "period": 'mean'}
        # print(row['name'])
        # new = pd.DataFrame({'indicator': row['_id'], 'period': 'min'}, {'indicator': row['_id'], 'period': 'max'}, {'indicator': row['_id'], 'period': 'mean'})
        lst_results.append(obj_min)
        lst_results.append(obj_max)
        lst_results.append(obj_mean)
        

print(lst_results)
df_multivariate = pd.DataFrame([s for s in lst_results])
df_multivariate.to_csv('andean_summary.csv', index=False)
# univariate_data = pd.concat(lst_results)

# print(univariate_data)
# univariate_data.to_csv('andean_summary.csv', index=False)


# print(new)