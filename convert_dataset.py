import geopandas as gpd

# 1. Baca file GeoJSON Anda
try:
    gdf = gpd.read_file('./datasets/public_facility.geojson')
    print("File GeoJSON berhasil dibaca.")
    print("Struktur data awal (GeoDataFrame):")
    print(gdf.head())
    print("\nKolom yang ada:", gdf.columns)

except Exception as e:
    print(f"Error saat membaca file: {e}")
    exit()

# 2. Tangani kolom 'geometry' dan pastikan lat lon tetap ada jika memungkinkan
if all(gdf.geometry.geom_type == 'Point'):
    print("\nSemua geometri adalah Point. Mengekstrak Latitude dan Longitude.")
    gdf['longitude'] = gdf.geometry.x
    gdf['latitude'] = gdf.geometry.y

elif 'Point' in gdf.geometry.geom_type.unique():
    print("\nTerdapat geometri campuran. Mengekstrak Latitude dan Longitude untuk Point saja.")
    gdf['longitude'] = gdf.geometry.apply(lambda geom: geom.x if geom.geom_type == 'Point' else None)
    gdf['latitude'] = gdf.geometry.apply(lambda geom: geom.y if geom.geom_type == 'Point' else None)

else:
    print("\nTidak ada geometri bertipe Point. Latitude dan Longitude tidak dapat diambil.")
    gdf['longitude'] = None
    gdf['latitude'] = None

# Drop kolom geometry (posisi sudah disimpan di lat lon)
df_final = gdf.drop(columns='geometry')

# 3. Simpan hasilnya ke file CSV
output_filename = './datasets/public_facility.csv'
df_final.to_csv(output_filename, index=False, encoding='utf-8')

print(f"\nKonversi berhasil! Data disimpan di '{output_filename}'")
print("\nStruktur data akhir (setelah konversi ke CSV):")
print(df_final.head())
