import pandas as pd
import numpy as np
import os

## load data

df = pd.read_csv('./datasets/Kepadatan Penduduk menurut Kecamatan di Kota Bandung, 2022.csv',
                 skiprows=4,
                 names=['Kecamatan', 'Luas Wilayah (km2)', 'Jumlah Penduduk', 'Kepadatan Penduduk (jiwa/km2)'])
print(df.head())

## df.to_csv('./datasets/cleaned_data_Kepadatan_menurut_kecamatan.csv', index=False)



