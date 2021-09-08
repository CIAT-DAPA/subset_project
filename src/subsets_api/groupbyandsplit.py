import pandas as pd
import numpy as np
from pandas.core import groupby  
from functools import reduce

data = [{'period':1995,'cellid':1, 'month1':0.1, 'month2':0.9, 'month3':0.1, 'month4':0.3, 'month5':0.4, 'month6':0.4},{'period':1995,'cellid':3, 'month1':0.2, 'month2':0.3, 'month3':0, 'month4':0.2, 'month5':0.3, 'month6':0.5},
        {'period':1996,'cellid':1, 'month1':0.3, 'month2':0.1, 'month3':0.1, 'month4':0.3, 'month5':0.4, 'month6':0.5}, {'period':1996,'cellid':2, 'month1':0.4, 'month2':0.1, 'month3':0.1, 'month4':0.3, 'month5':0.4, 'month6':0.4}, {'period':1996,'cellid':3, 'month1':0.7, 'month2':0.5, 'month3':0.7, 'month4':0.8, 'month5':0.7, 'month6':0.7},
        {'period':1997,'cellid':1, 'month1':0.9, 'month2':0.6, 'month3':0.4, 'month4':0.1, 'month5':2, 'month6':1}, {'period':1997,'cellid':2, 'month1':0.3, 'month2':0.4, 'month3':0.1, 'month4':0.3, 'month5':0.4, 'month6':0.4}, {'period':1997,'cellid':3, 'month1':0.1, 'month2':0.3, 'month3':0.1, 'month4':0.1, 'month5':0.1, 'month6':0.1}]

df = pd.DataFrame(data)

months = ['month1', 'month2']
month_dict = {'month1':[0.2,0.5],'month2':[0.2,0.5]}

query_gt = ' & '.join([f'{k}>={v[0]}' for k, v in month_dict.items()])
query_lt = ' & '.join([f'{k}<={v[1]}' for k, v in month_dict.items()])

query = query_gt + ' & ' + query_lt
print(query)

print(df.query(query))
# df_gt = df.loc[:, 'month1'] >= 0.7 
# df_lt = df.loc[:, 'month1'] <=

# df_a = df.loc[df_gt + df_lt]

# if 

# df.iloc[1, [1,2]] = np.nan

#print(df.loc[(df['month1'] >= 0.2),['cellid','month1']])