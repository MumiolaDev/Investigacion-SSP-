import cdflib
import numpy as np
import pandas as pd
import os
import urllib.request
from pathlib import Path  

fname = '2022_3.cdf'
url = ("https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2022/psp_coho1hr_merged_mag_plasma_20220301_v01.cdf")
if not os.path.exists(fname):
    urllib.request.urlretrieve(url, fname)
cdf_file = cdflib.CDF('./2022_3.cdf')

# todos los links
#2018
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2018/psp_coho1hr_merged_mag_plasma_20180101_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2018/psp_coho1hr_merged_mag_plasma_20180201_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2018/psp_coho1hr_merged_mag_plasma_20180301_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2018/psp_coho1hr_merged_mag_plasma_20180401_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2018/psp_coho1hr_merged_mag_plasma_20180501_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2018/psp_coho1hr_merged_mag_plasma_20180601_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2018/psp_coho1hr_merged_mag_plasma_20180701_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2018/psp_coho1hr_merged_mag_plasma_20180801_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2018/psp_coho1hr_merged_mag_plasma_20180901_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2018/psp_coho1hr_merged_mag_plasma_20181001_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2018/psp_coho1hr_merged_mag_plasma_20181101_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2018/psp_coho1hr_merged_mag_plasma_20181201_v01.cdf

#2019
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2019/psp_coho1hr_merged_mag_plasma_20190101_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2019/psp_coho1hr_merged_mag_plasma_20190201_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2019/psp_coho1hr_merged_mag_plasma_20190301_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2019/psp_coho1hr_merged_mag_plasma_20190401_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2019/psp_coho1hr_merged_mag_plasma_20190501_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2019/psp_coho1hr_merged_mag_plasma_20190601_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2019/psp_coho1hr_merged_mag_plasma_20190701_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2019/psp_coho1hr_merged_mag_plasma_20190801_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2019/psp_coho1hr_merged_mag_plasma_20190901_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2019/psp_coho1hr_merged_mag_plasma_20191001_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2019/psp_coho1hr_merged_mag_plasma_20191101_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2019/psp_coho1hr_merged_mag_plasma_20191201_v01.cdf



#2020

#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2020/psp_coho1hr_merged_mag_plasma_20200101_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2020/psp_coho1hr_merged_mag_plasma_20200201_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2020/psp_coho1hr_merged_mag_plasma_20200301_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2020/psp_coho1hr_merged_mag_plasma_20200401_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2020/psp_coho1hr_merged_mag_plasma_20200501_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2020/psp_coho1hr_merged_mag_plasma_20200601_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2020/psp_coho1hr_merged_mag_plasma_20200701_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2020/psp_coho1hr_merged_mag_plasma_20200801_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2020/psp_coho1hr_merged_mag_plasma_20200901_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2020/psp_coho1hr_merged_mag_plasma_20201001_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2020/psp_coho1hr_merged_mag_plasma_20201101_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2020/psp_coho1hr_merged_mag_plasma_20201201_v01.cdf

#2021
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2021/psp_coho1hr_merged_mag_plasma_20210101_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2021/psp_coho1hr_merged_mag_plasma_20210201_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2021/psp_coho1hr_merged_mag_plasma_20210301_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2021/psp_coho1hr_merged_mag_plasma_20210401_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2021/psp_coho1hr_merged_mag_plasma_20210501_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2021/psp_coho1hr_merged_mag_plasma_20210601_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2021/psp_coho1hr_merged_mag_plasma_20210701_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2021/psp_coho1hr_merged_mag_plasma_20210801_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2021/psp_coho1hr_merged_mag_plasma_20210901_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2021/psp_coho1hr_merged_mag_plasma_20211001_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2021/psp_coho1hr_merged_mag_plasma_20211101_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2021/psp_coho1hr_merged_mag_plasma_20211201_v01.cdf

# 2022
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2022/psp_coho1hr_merged_mag_plasma_20220101_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2022/psp_coho1hr_merged_mag_plasma_20220201_v01.cdf
#https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2022/psp_coho1hr_merged_mag_plasma_20220301_v01.cdf


filepath = Path('./2022_3.csv')  
def omni_cdf_to_dataframe(file):
    """
    Load a CDF File and convert it in a Pandas DataFrame.

    WARNING: This will not return the CDF Attributes, just the variables.
    WARNING: Only works for CDFs of the same array lenght (OMNI)
    """
    cdf = cdflib.CDF(file)
    cdfdict = {}

    for key in cdf.cdf_info()['zVariables']:
        cdfdict[key] = cdf[key]

    cdfdf = pd.DataFrame(cdfdict)

    if 'Epoch' in cdf.cdf_info()['zVariables']:
        cdfdf['Epoch'] = pd.to_datetime(cdflib.cdfepoch.encode(cdfdf['Epoch'].values))
        
    
    return cdfdf.to_csv(filepath)



omni_cdf_to_dataframe('./2022_3.cdf')




#2020 enero https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2020/psp_coho1hr_merged_mag_plasma_20200101_v01.cdf

#perihelios psp
#p1 --> nov2018 https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2018/psp_coho1hr_merged_mag_plasma_20181101_v01.cdf
#p2 --> abr2019 https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2019/psp_coho1hr_merged_mag_plasma_20190401_v01.cdf
#p3 --> sep2019 https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2019/psp_coho1hr_merged_mag_plasma_20190901_v01.cdf
#p4 --> ene2020 archivos de prueba

#afelios psp
#a1 --> ene2019 https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2019/psp_coho1hr_merged_mag_plasma_20190101_v01.cdf


#momento más cercano nov 21, 2021
# https://spdf.gsfc.nasa.gov/pub/data/psp/coho1hr_magplasma/cdf/2021/psp_coho1hr_merged_mag_plasma_20211101_v01.cdf

#WIND


#SOHO
#1996 https://spdf.gsfc.nasa.gov/pub/data/soho/orbit/def_or/1996/so_or_def_19960101_v02.cdf


########################


#def bad_omni_to_nan(df):
#    if 'B' in df.columns: df.loc[df['B'] >= 4000.99, 'B'] = np.nan
#    return df.to_csv(df)
