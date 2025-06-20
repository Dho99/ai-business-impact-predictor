# Script Penggabungan Dataset dengan Kategori/Type

## Deskripsi
Script ini dibuat untuk menggabungkan seluruh dataset yang sudah memiliki kategori/type di atributnya. Dataset yang digabungkan meliputi:

1. **cleaned_objek_wisata_belanja.csv** - Data objek wisata dan tempat belanja (type: `tourism_shopping_place`)
2. **cleaned_taman_kota_bandung.csv** - Data taman kota (type: `city_park`)
3. **data_fnb_bandung_2024_cleaned.csv** - Data food & beverage (type: `restaurant`)
4. **jumlah_supermarket_minimarket_bandung.csv** - Data supermarket dan minimarket (type: `shopping_place`)

## File yang Dihasilkan

### 1. Script Utama
- **`combine_datasets_with_categories.py`** - Script utama untuk menggabungkan dataset
- **`utils/combine_datasets_utils.py`** - Utility functions yang dapat diimport
- **`example_usage.py`** - Contoh penggunaan script

### 2. Output Dataset
- **`datasets/combined_business_data_with_categories.csv`** - Dataset gabungan semua kategori
- **`datasets/combined_city_park_data.csv`** - Dataset khusus taman kota
- **`datasets/combined_restaurant_data.csv`** - Dataset khusus restaurant
- **`datasets/combined_tourism_shopping_place_data.csv`** - Dataset khusus wisata & belanja
- **`datasets/combined_shopping_place_data.csv`** - Dataset khusus supermarket/minimarket

## Cara Penggunaan

### 1. Menjalankan Script Utama
```bash
python combine_datasets_with_categories.py
```

### 2. Menggunakan sebagai Module
```python
from utils.combine_datasets_utils import (
    load_and_combine_categorized_datasets,
    filter_by_type,
    filter_by_kecamatan,
    get_summary_stats
)

# Load semua dataset
combined_df = load_and_combine_categorized_datasets()

# Filter berdasarkan kategori
restaurants = filter_by_type(combined_df, 'restaurant')
parks = filter_by_type(combined_df, 'city_park')

# Filter berdasarkan kecamatan
bandung_wetan = filter_by_kecamatan(combined_df, 'BANDUNG WETAN')

# Dapatkan statistik
stats = get_summary_stats(combined_df)
```

### 3. Menjalankan Contoh Penggunaan
```bash
python example_usage.py
```

## Struktur Dataset Gabungan

Dataset gabungan memiliki kolom-kolom yang sudah distandarisasi:

| Kolom | Deskripsi |
|-------|-----------|
| `nama` | Nama tempat/bisnis |
| `alamat` | Alamat (jika tersedia) |
| `kecamatan` | Nama kecamatan |
| `kelurahan` | Nama kelurahan (jika tersedia) |
| `latitude` | Koordinat latitude (jika tersedia) |
| `longitude` | Koordinat longitude (jika tersedia) |
| `tahun` | Tahun data (jika tersedia) |
| `type` | Kategori bisnis (`restaurant`, `city_park`, `tourism_shopping_place`, `shopping_place`) |
| `additional_info` | Informasi tambahan yang spesifik untuk setiap dataset |
| `source_dataset` | Sumber dataset asli (`fnb`, `taman`, `wisata_belanja`, `market`) |

## Statistik Dataset Gabungan

### Total Records: 2,118
- **City Parks**: 999 records (47.2%)
- **Restaurants**: 706 records (33.3%)
- **Tourism & Shopping Places**: 323 records (15.3%)
- **Shopping Places**: 90 records (4.2%)

### Top 5 Kecamatan dengan Data Terbanyak:
1. Kabupaten Bandung: 705 tempat
2. BANDUNG WETAN: 120 tempat
3. Bandung Wetan: 101 tempat
4. BUAHBATU: 93 tempat
5. ARCAMANIK: 80 tempat

### Data dengan Koordinat:
1,029 dari 2,118 records (48.6%) memiliki koordinat GPS

### Distribusi per Tahun:
- 2019: 90 tempat (supermarket/minimarket)
- 2021: 323 tempat (wisata/belanja)
- 2024: 706 tempat (restaurant)

## Functions Tersedia

### `load_and_combine_categorized_datasets(datasets_path="datasets")`
Memuat dan menggabungkan semua dataset yang memiliki kategori.

### `filter_by_type(df, business_type)`
Filter dataset berdasarkan kategori bisnis.

### `filter_by_kecamatan(df, kecamatan)`
Filter dataset berdasarkan nama kecamatan.

### `get_summary_stats(df)`
Mendapatkan statistik ringkasan dari dataset.

### `save_combined_dataset(df, output_path)`
Menyimpan dataset gabungan ke file CSV.

### `create_type_specific_files(df, output_dir)`
Membuat file terpisah untuk setiap kategori bisnis.

## Contoh Analisis

### 1. Analisis Restoran per Kecamatan
```python
restaurants = filter_by_type(combined_df, 'restaurant')
restaurant_by_kecamatan = restaurants['kecamatan'].value_counts()
print(restaurant_by_kecamatan.head())
```

### 2. Mencari Semua Tempat di Kecamatan Tertentu
```python
bandung_wetan_places = filter_by_kecamatan(combined_df, 'BANDUNG WETAN')
print(f"Total tempat di Bandung Wetan: {len(bandung_wetan_places)}")
```

### 3. Analisis Koordinat GPS
```python
with_coords = combined_df[(combined_df['latitude'] != '') & (combined_df['longitude'] != '')]
print(f"Tempat dengan koordinat: {len(with_coords)}")
```

## Catatan Penting

1. **Konsistensi Nama Kecamatan**: Beberapa dataset menggunakan format nama kecamatan yang berbeda (uppercase vs title case). Script ini mempertahankan format asli.

2. **Data Koordinat**: Tidak semua dataset memiliki koordinat GPS. Dataset taman kota dan supermarket/minimarket tidak memiliki koordinat.

3. **Additional Info**: Setiap dataset memiliki informasi tambahan yang spesifik:
   - Taman: Informasi luas area
   - Restaurant: Informasi provinsi dan kota
   - Supermarket: Informasi kategori dan jumlah unit

4. **Source Dataset**: Kolom `source_dataset` membantu melacak asal data untuk analisis lebih lanjut.

## Pengembangan Selanjutnya

1. **Standardisasi Koordinat**: Menambahkan koordinat untuk dataset yang belum memiliki.
2. **Geocoding**: Menggunakan alamat untuk mendapatkan koordinat GPS.
3. **Cleaning Nama Kecamatan**: Standardisasi format nama kecamatan.
4. **Additional Categories**: Menambahkan kategori bisnis yang lebih spesifik.
