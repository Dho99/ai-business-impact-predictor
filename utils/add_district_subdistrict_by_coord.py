import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

# Membaca data CSV
df = pd.read_csv('./datasets/objek_wisata_belanja.csv')

geolocator = Nominatim(user_agent="wisata_bandung_app") # Ganti dengan nama aplikasi Anda

# Menampilkan info dataset
print(f"Total data: {len(df)} baris")
print(f"Kolom dataset: {list(df.columns)}")

# Mengecek data yang memiliki koordinat kosong atau tidak valid
missing_coords = df[df['titik_koordinat'].isna() | (df['titik_koordinat'] == '') | (df['titik_koordinat'] == '-')]
print(f"Data dengan koordinat kosong/tidak valid: {len(missing_coords)} baris")

# Hapus data dengan koordinat kosong sebelum processing
df_clean = df[~(df['titik_koordinat'].isna() | (df['titik_koordinat'] == '') | (df['titik_koordinat'] == '-'))].copy()
print(f"Data setelah pembersihan: {len(df_clean)} baris")

# Menghapus baris dengan index spesifik yang error
error_indices = [84, 85, 229]
df = df.drop(error_indices, errors='ignore')

# df = df.head(10)


# print(df.info())

def split_titik_koordinat(row):
    try:
        # Split koordinat dengan indexing untuk lat dan lon
        koordinat_parts = str(row['titik_koordinat']).split(',')
        lat = koordinat_parts[0].strip()  # Index 0 untuk latitude
        lon = koordinat_parts[1].strip()  # Index 1 untuk longitude
        
        # print(f"Index {row.name}: Splitting koordinat: {row['titik_koordinat']} into lat={lat}, lon={lon}")
        
        # Konversi ke float untuk validasi
        lat_float = float(lat)
        lon_float = float(lon)
        
        return pd.Series([lat_float, lon_float])
    except (IndexError, ValueError) as e:
        print(f"Index {row.name}: Error splitting koordinat: {row['titik_koordinat']} - {e}")
        return pd.Series([None, None])
    except Exception as e:
        print(f"Index {row.name}: Unexpected error: {row['titik_koordinat']} - {e}")
        return pd.Series([None, None])

# Memisahkan kolom titik_koordinat menjadi latitude dan longitude
df[['latitude', 'longitude']] = df.apply(split_titik_koordinat, axis=1)

def get_admin_areas_nominatim(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), language='id', addressdetails=True, timeout=10)
        if location and location.address:
            address = location.raw.get('address', {})
            kelurahan = address.get('village') or address.get('suburb') or address.get('hamlet')
            kecamatan = address.get('district') or address.get('subdistrict')
            kota_kabupaten = address.get('city') or address.get('town') or address.get('county')
            provinsi = address.get('state')
            data = [kelurahan, kecamatan, kota_kabupaten, provinsi]
            return pd.Series(data)
        else:
            return pd.Series([None, None, None, None])
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Error geocoding ({lat}, {lon}): {e}. Retrying after a delay...")
        time.sleep(5) # Jeda untuk menghindari batasan rate
        return get_admin_areas_nominatim(lat, lon) # Coba lagi
    except Exception as e:
        print(f"An unexpected error occurred for ({lat}, {lon}): {e}")
        return pd.Series([None, None, None, None])

df[['kelurahan', 'kecamatan', 'kota_kabupaten', 'provinsi']] = df.apply(
    lambda row: get_admin_areas_nominatim(row['latitude'], row['longitude']),
    axis=1
)

# Menyimpan DataFrame ke file CSV baru

print(df.head())
output_file = './datasets/objek_wisata_belanja_with_coordinates.csv'
df.to_csv(output_file, index=False)
print(f"Data saved to {output_file}")  