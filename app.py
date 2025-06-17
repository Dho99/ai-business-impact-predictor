import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
pd.set_option('display.max_rows', 300)


df = pd.read_csv('./datasets/public_facility.csv')

num_drop_cols = ['admin_level', 'capacity:cargo_bike', 'capacity:disabled', 'capacity:persons', 'floors', 'height', 'layer', 'min_age', 'mobile', 'task', 'route_ref', 'ele']

df = df.drop(columns=num_drop_cols)

df['capacity'] = df['capacity'].fillna(df['capacity'].mean())
df['rooms'] = df['rooms'].fillna(df['rooms'].mean())
df['stars'] = df['stars'].fillna(df['stars'].mean())
df['latitude'] = df['latitude'].fillna(df['latitude'].mean())
df['longitude'] = df['longitude'].fillna(df['longitude'].mean())
df['building:levels'] = df['building:levels'].fillna(df['building:levels'].mean())
df['addr:postcode'] = df['addr:postcode'].fillna(df['addr:postcode'].mean())

# correlation = df.corr()

print(df['capacity'].describe())
print(df['capacity'].value_counts())

# print(df.describe())

missing_val = df.select_dtypes(include=[np.number]).isnull().sum()
percentage_missing = (missing_val / len(df)) * 100
missing_data_info = pd.DataFrame({'Missing Value': missing_val, 'Percentage': percentage_missing})
print(missing_data_info)





# Langkah 4: Cek apakah datanya bervariasi
print('Rooms unique values:', df['rooms'].nunique())
print('Capacity unique values:', df['capacity'].nunique())





# plt.figure(figsize=(10,8))
# sns.heatmap(df.select_dtypes(include=[np.number]).corr(), annot=True, cmap='coolwarm')
# plt.title('Corelation Variable')
# plt.savefig('Correlation_Variable.png')


