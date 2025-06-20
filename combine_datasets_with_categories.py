"""
Script untuk menggabungkan seluruh datasets yang sudah memiliki kategori/type di atributnya
Datasets yang akan digabungkan:
- cleaned_objek_wisata_belanja.csv (tourism_shopping_place)
- cleaned_taman_kota_bandung.csv (city_park)
- data_fnb_bandung_2024_cleaned.csv (restaurant)
- jumlah_supermarket_minimarket_bandung.csv (shopping_place)
"""

import pandas as pd
import os

def combine_datasets_with_categories():
    """
    Menggabungkan dataset yang memiliki kolom type/kategori
    """
    
    # Path ke folder datasets
    datasets_path = "datasets"
    
    # Dictionary untuk menyimpan dataframe dari setiap dataset
    datasets = {}
    
    print("Loading datasets...")
    
    # 1. Load cleaned_objek_wisata_belanja.csv
    print("Loading objek wisata belanja...")
    df_wisata = pd.read_csv(os.path.join(datasets_path, "cleaned_objek_wisata_belanja.csv"))
    
    # Standardisasi kolom untuk objek wisata
    df_wisata_std = pd.DataFrame({
        'nama': df_wisata['nama_tempat'],
        'alamat': df_wisata['alamat'],
        'kecamatan': df_wisata['kecamatan'],
        'kelurahan': df_wisata.get('kelurahan', ''),
        'latitude': df_wisata['latitude'],
        'longitude': df_wisata['longitude'],
        'tahun': df_wisata['tahun'],
        'type': df_wisata['type'],
        'additional_info': ''
    })
    datasets['wisata_belanja'] = df_wisata_std
    
    # 2. Load cleaned_taman_kota_bandung.csv
    print("Loading taman kota...")
    df_taman = pd.read_csv(os.path.join(datasets_path, "cleaned_taman_kota_bandung.csv"))
    
    # Standardisasi kolom untuk taman
    df_taman_std = pd.DataFrame({
        'nama': df_taman['nama_taman'],
        'alamat': '',  # Tidak ada alamat di dataset taman
        'kecamatan': df_taman['kecamatan'],
        'kelurahan': '',
        'latitude': '',
        'longitude': '',
        'tahun': '',  # Tidak ada tahun di dataset taman
        'type': df_taman['type'],
        'additional_info': f"Luas: {df_taman['luas']} m2"
    })
    datasets['taman'] = df_taman_std
    
    # 3. Load data_fnb_bandung_2024_cleaned.csv
    print("Loading F&B data...")
    df_fnb = pd.read_csv(os.path.join(datasets_path, "data_fnb_bandung_2024_cleaned.csv"))
    
    # Standardisasi kolom untuk F&B
    df_fnb_std = pd.DataFrame({
        'nama': df_fnb['nama_rumah_makan'],
        'alamat': df_fnb['alamat'],
        'kecamatan': df_fnb['kecamatan'],
        'kelurahan': df_fnb['kelurahan'],
        'latitude': df_fnb['latitude'],
        'longitude': df_fnb['longitude'],
        'tahun': df_fnb['tahun'],
        'type': df_fnb['type'],
        'additional_info': f"Provinsi: {df_fnb['nama_provinsi']}, Kota: {df_fnb['bps_nama_kabupaten_kota']}"
    })
    datasets['fnb'] = df_fnb_std
    
    # 4. Load jumlah_supermarket_minimarket_bandung.csv
    print("Loading supermarket/minimarket data...")
    df_market = pd.read_csv(os.path.join(datasets_path, "jumlah_supermarket_minimarket_bandung.csv"))
    
    # Standardisasi kolom untuk supermarket/minimarket
    df_market_std = pd.DataFrame({
        'nama': df_market['kategori'] + ' - ' + df_market['kecamatan'],
        'alamat': '',
        'kecamatan': df_market['kecamatan'],
        'kelurahan': '',
        'latitude': '',
        'longitude': '',
        'tahun': df_market['tahun'],
        'type': df_market['type'],
        'additional_info': f"Kategori: {df_market['kategori']}, Jumlah: {df_market['jumlah']} {df_market['satuan']}"
    })
    datasets['market'] = df_market_std
    
    # Gabungkan semua dataset
    print("\nCombining all datasets...")
    combined_df = pd.concat([
        datasets['wisata_belanja'],
        datasets['taman'],
        datasets['fnb'],
        datasets['market']
    ], ignore_index=True)
    
    # Bersihkan data
    combined_df = combined_df.fillna('')
    
    # Tambahkan kolom source untuk identifikasi asal dataset
    source_labels = []
    for name, df in datasets.items():
        source_labels.extend([name] * len(df))
    
    combined_df['source_dataset'] = source_labels
    
    # Summary statistik
    print(f"\nSummary of combined dataset:")
    print(f"Total records: {len(combined_df)}")
    print(f"\nBreakdown by type:")
    print(combined_df['type'].value_counts())
    print(f"\nBreakdown by source dataset:")
    print(combined_df['source_dataset'].value_counts())
    print(f"\nBreakdown by kecamatan:")
    print(combined_df['kecamatan'].value_counts().head(10))
    
    # Simpan hasil gabungan
    output_file = "datasets/combined_business_data_with_categories.csv"
    combined_df.to_csv(output_file, index=False)
    print(f"\nCombined dataset saved to: {output_file}")
    
    # Buat juga versi yang dikelompokkan berdasarkan type
    print("\nCreating type-specific files...")
    for type_name in combined_df['type'].unique():
        if type_name:  # Skip empty types
            type_df = combined_df[combined_df['type'] == type_name]
            type_file = f"datasets/combined_{type_name}_data.csv"
            type_df.to_csv(type_file, index=False)
            print(f"- {type_name}: {len(type_df)} records saved to {type_file}")
    
    return combined_df

def create_analysis_summary(df):
    """
    Membuat ringkasan analisis dari dataset gabungan
    """
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    
    # Analisis per kecamatan
    print("\nTop 10 Kecamatan dengan jumlah bisnis/tempat terbanyak:")
    kecamatan_counts = df['kecamatan'].value_counts().head(10)
    for i, (kecamatan, count) in enumerate(kecamatan_counts.items(), 1):
        print(f"{i:2d}. {kecamatan}: {count} tempat")
    
    # Analisis per type
    print(f"\nDistribusi berdasarkan kategori:")
    type_counts = df['type'].value_counts()
    for type_name, count in type_counts.items():
        percentage = (count / len(df)) * 100
        print(f"- {type_name}: {count} ({percentage:.1f}%)")
    
    # Analisis koordinat (yang memiliki lat/long)
    coords_available = df[(df['latitude'] != '') & (df['longitude'] != '')]
    print(f"\nData dengan koordinat: {len(coords_available)} dari {len(df)} ({(len(coords_available)/len(df)*100):.1f}%)")
    
    # Analisis per tahun
    print(f"\nDistribusi berdasarkan tahun:")
    df_with_year = df[df['tahun'] != '']
    if not df_with_year.empty:
        year_counts = df_with_year['tahun'].value_counts().sort_index()
        for year, count in year_counts.items():
            print(f"- {year}: {count} tempat")

if __name__ == "__main__":
    print("Script untuk menggabungkan datasets dengan kategori/type")
    print("="*60)
    
    try:
        # Gabungkan datasets
        combined_data = combine_datasets_with_categories()
        
        # Buat analisis summary
        create_analysis_summary(combined_data)
        
        print(f"\n{'='*60}")
        print("SELESAI! Dataset berhasil digabungkan.")
        print("File output:")
        print("- datasets/combined_business_data_with_categories.csv (semua data)")
        print("- datasets/combined_[type]_data.csv (data per kategori)")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Pastikan semua file dataset ada di folder 'datasets/'")
