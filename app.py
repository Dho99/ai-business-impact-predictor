import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
pd.set_option('display.max_rows', 300)


df = pd.read_csv('./datasets/public_facility.csv')

df = df.drop(columns=[
    'id', '@id', 'abandoned', 'abandoned:railway', 'access', 'access:roof',
    'addr:full', 'addr:housename', 'addr:unit', 'air_conditioning',
    'alt_name', 'amenity_1', 'area', 'atm', 'baby_feeding', 'barrier',
    'bicycle', 'bicycle_parking', 'branch', 'brand:en', 'brand:id',
    'brand:wikidata', 'brand:wikipedia', 'brand:zh', 'building:colour',
    'building:condition', 'building:floor', 'building:levels',
    'building:material', 'building:part', 'building:roof', 'building:structure',
    'building:use', 'building:walls', 'bus', 'cash_in', 'cash_out',
    'cash_withdrawal', 'changing_table', 'check_date', 'compressed_air',
    'contact:facebook', 'contact:instagram', 'contact:phone', 'contact:twitter',
    'contact:whatsapp', 'contact:youtube', 'created_by', 'crossing',
    'currency:IDR', 'currency:rupiah', 'denomination', 'designation',
    'dispensing', 'disused:railway', 'door', 'drive_through', 'email',
    'emergency', 'entrance', 'facebook', 'fax', 'female', 'fixme', 'foot',
    'fuel:GTL_diesel', 'fuel:biodiesel', 'fuel:diesel', 'fuel:lpg',
    'fuel:octane_88', 'fuel:octane_90', 'fuel:octane_92', 'fuel:octane_95',
    'fuel:octane_98', 'fuel:solar', 'gate:type', 'government', 'grades', 'health_amenity:type', 'healthcare', 'healthcare:speciality',
 'historic', 'image', 'incline', 'indoor', 'inscription',
    'instagram', 'insurance:health', 'int_name', 'internet_access:fee',
    'internet_access:ssid', 'isced:level', 'kids_area', 'landuse', 'leaf_type',
    'leisure', 'lift_gate:type', 'lit', 'locked', 'male', 'material',
    'maxheight', 'maxstay', 'mofa', 'moped', 'motor_vehicle', 'motorcar',
    'motorcycle', 'museum', 'name:de', 'name:en', 'name:hi', 'name:id',
    'name:it', 'name:ja', 'name:ko', 'name:nl', 'name:signed', 'name:su',
    'name:vi', 'name:zh', 'network', 'network:wikidata', 'noexit',
    'not:brand:wikidata', 'note', 'office', 'official_name', 'official_name:en',
    'official_name:id', 'old_name', 'oneway', 'opening_hours:covid19',
    'operator:en', 'operator:id', 'operator:type', 'operator:website',
    'operator:wikidata', 'operator:wikipedia', 'operator_type', 'orientation',
    'outdoor_seating', 'park_ride', 'parking:orientation', 'parking_space',
    'payment:cards', 'payment:cash', 'payment:coins', 'payment:contactless',
    'payment:credit_cards', 'payment:cryptocurrencies',
    'payment:debit_cards', 'payment:electronic_purses', 'payment:gpn_debit',
    'payment:maestro', 'payment:mastercard', 'payment:notes', 'payment:visa',
    'payment:visa_debit', 'payment:visa_electron', 'phone', 'place_of_worship',
    'product', 'railway', 'railway:ref', 'ref', 'religion',
    'reservation', 'roof:colour', 'roof:material', 'room', 'rooms',
    'school:gender', 'school:type_idn', 'security_desk', 'self_service',
    'service_times', 'shelter', 'short_name', 'smoking', 'smoothness',
    'source', 'sport', 'stars', 'start_date', 'supervised', 'surface',
    'tactile_paving', 'taxi_vehicle', 'toilets:access', 'toilets:wheelchair',
    'tourism', 'townhall:type', 'traffic_signals:sound', 'training',
    'type', 'type:id', 'url', 'vehicle', 'wall', 'website', 'wikidata',
    'wikimedia_commons', 'wikipedia', 'addr:city', 'addr:country', 'addr:housenumber', 'addr:neighbourhood', 'addr:province','admin_level','capacity:cargo_bike', 'capacity:disabled', 'capacity:persons','addr:suburb','floors','wheelchair', 'min_age'
])

# print(df.describe())
print(df.info())

# print(df.dtypes)
# print(df.head())
# print(df.isna().sum())
# print(df.isnull().sum())
# df_filled = df.fillna(df.mean())

# plt.figure(figsize=(10,8))
# sns.heatmap(df.select_dtypes(include=[np.number]).corr(), annot=True, cmap='coolwarm')
# plt.title('Corelation Variable')
# plt.savefig('Correlation_Variable.png')