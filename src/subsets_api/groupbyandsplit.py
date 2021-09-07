import pandas as pd
import numpy as np
from pandas.core import groupby  
from functools import reduce

data = [{'period':1995,'cellid':1, 'month1':0.1, 'month2':0.1},{'period':1995,'cellid':3, 'month1':0.2, 'month2':0.3},
        {'period':1996,'cellid':1, 'month1':0.3, 'month2':0.1}, {'period':1996,'cellid':2, 'month1':0.4, 'month2':0.1}, {'period':1996,'cellid':3, 'month1':0.7, 'month2':0.5},
        {'period':1997,'cellid':1, 'month1':0.9, 'month2':0.6}, {'period':1997,'cellid':2, 'month1':0.3, 'month2':0.4}, {'period':1997,'cellid':3, 'month1':0.1, 'month2':0.3}]

df = pd.DataFrame(data)

for x in range(len(df)):
        for colums in list(df.columns.values):
                if 'month' in colums:
                        if 0.7 <= df.loc[x, colums] or df.loc[x, colums] <= 0.2:
                                df.loc[x, colums] = np.nan

print(df)
# df_gt = df.loc[:, 'month1'] >= 0.7 
# df_lt = df.loc[:, 'month1'] <=

# df_a = df.loc[df_gt + df_lt]

# if 

# df.iloc[1, [1,2]] = np.nan

#print(df.loc[(df['month1'] >= 0.2),['cellid','month1']])