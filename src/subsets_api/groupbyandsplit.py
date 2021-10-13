import pandas as pd
import numpy as np
from pandas.core import groupby  
from functools import reduce

csv = pd.read_csv('convertcsv.csv')

periods = range(1983,2017)
lst_results = []
for index, row in csv.iterrows():
        # print(row['indicator'])
        new = pd.DataFrame({'indicator': row['indicator'], 'period': periods})
        lst_results.append(new)

univariate_data = pd.concat(lst_results)

print(univariate_data)
univariate_data.to_csv('file_name.csv', index=False)


# print(new)