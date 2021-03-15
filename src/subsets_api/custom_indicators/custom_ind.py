# Load libraries
import pandas as pd 
from ..indicators.scripts import *

# Read data 
""" data = pd.read_csv("6_summary_genetic.csv")  """

def calculate_summary(data, vars):
    df_summary = pd.DataFrame(columns=['average','1st_quartile','2nd_quartile',
    '3rd_quartile','std_dev'])
    for var in vars:
        vals = [data[var].mean(), 
                data[var].quantile(0.25), 
                data[var].quantile(0.5), 
                data[var].quantile(0.75),
                data[var].std()]
        df_summary.loc[var] = vals

    return df_summary


def filter_by_var(data, data_summary, var, metric, operator):
    if operator == 'greater':
        condition = data[var] > data_summary.loc[var, metric]

    if operator == 'lower':
        condition = data[var] < data_summary.loc[var, metric]

    return data[condition]

""" id_custom_data: column name in custom data having id data
    id_accessions: column name in accessions data having id data
"""
def merge_data(custom_data, id_custom_data, id_accessions):
    id_list = custom_data[id_custom_data].tolist()
    """ get accessions data that match id_list """
    accessions_data = getAccessionsById(id_list)

    merged_data = custom_data.merge(accessions_data, how='inner', left_on=id_custom_data, right_on=id_accessions)



