from ast import For
import csv
import numpy as np
import pandas as pd
import os
import urllib.request
from pathlib import Path 



def bad_omni_to_nan(df):
    if 'B' in df.columns: df.loc[df['B'] >= 9999.99, 'B'] = np.nan
    return df.to_csv(df)

#df = pd.read_csv('./data.csv')
#bad_omni_to_nan(df)

def remove_specific_row_from_csv(file, file2, column_name, *args):
    '''
    :param file: file to remove the rows from
    :param column_name: The column that determines which row will be 
           deleted (e.g. if Column == Name and row-*args
           contains "Gavri", All rows that contain this word will be deleted)
    :param args: Strings from the rows according to the conditions with 
                 the column
    '''
    row_to_remove = []
    for row_name in args:
        row_to_remove.append(row_name)
    try:
        df = pd.read_csv(file)
        for row in row_to_remove:
            df = df[eval("df.{}".format(column_name)) != row]
        df.to_csv(file2, index=False)
    except Exception  as e:
        raise Exception("Error message....")


remove_specific_row_from_csv('./append.csv','./data_B.csv' , "B" , -1e+31)
remove_specific_row_from_csv('./append.csv','./data_Dens.csv' , "protonDensity" , -1e+31)
remove_specific_row_from_csv('./append.csv','./data_Temp.csv' , "protonTemp" , -1e+31)
#pal seba
remove_specific_row_from_csv('./append.csv','./data_BR.csv' , "BR" , -1e+31)
remove_specific_row_from_csv('./append.csv','./data_BT.csv' , "BT" , -1e+31)
remove_specific_row_from_csv('./append.csv','./data_BN.csv' , "BN" , -1e+31)
remove_specific_row_from_csv('./append.csv','./data_VR.csv' , "VR" , -1e+31)
remove_specific_row_from_csv('./append.csv','./data_VT.csv' , "VT" , -1e+31)
remove_specific_row_from_csv('./append.csv','./data_VN.csv' , "VN" , -1e+31)
#Report_Card = pd.read_csv('./data.csv')
#Report_Card.drop(Report_Card. index[0])
