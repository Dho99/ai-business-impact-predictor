"""
Utility functions untuk menggabungkan datasets dengan kategori/type
"""

import pandas as pd
import os

def load_and_combine_categorized_datasets(datasets_path="datasets"):
    """
    Function utility untuk menggabungkan datasets yang memiliki kolom type/kategori
    
    Parameters:
    datasets_path (str): Path ke folder datasets
    
    Returns:
    pd.DataFrame: Dataset gabungan yang sudah terstandarisasi
    """
    
    datasets = {}
    
    # 1. Load objek wisata belanja
    df_wisata = pd.read_csv(os.path.join(datasets_path, "cleaned_objek_wisata_belanja.csv"))
    df_wisata_std = pd.DataFrame({
        'nama': df_wisata['nama_tempat'],
        'alamat': df_wisata['alamat'],
        'kecamatan': df_wisata['kecamatan'],
        'kelurahan': df_wisata.get('kelurahan', ''),
        'latitude': df_wisata['latitude'],
        'longitude': df_wisata['longitude'],
        'tahun': df_wisata['tahun'],
        'type': df_wisata['type'],
        'additional_info': '',
        'source_dataset': 'wisata_belanja'
    })
    datasets['wisata_belanja'] = df_wisata_std
    
    # 2. Load taman kota
    df_taman = pd.read_csv(os.path.join(datasets_path, "cleaned_taman_kota_bandung.csv"))
    df_taman_std = pd.DataFrame({
        'nama': df_taman['nama_taman'],
        'alamat': '',
        'kecamatan': df_taman['kecamatan'],
        'kelurahan': '',
        'latitude': '',
        'longitude': '',
        'tahun': '',
        'type': df_taman['type'],
        'additional_info': f"Luas: {df_taman['luas']} m2",
        'source_dataset': 'taman'
    })
    datasets['taman'] = df_taman_std
    
    # 3. Load F&B data
    df_fnb = pd.read_csv(os.path.join(datasets_path, "data_fnb_bandung_2024_cleaned.csv"))
    df_fnb_std = pd.DataFrame({
        'nama': df_fnb['nama_rumah_makan'],
        'alamat': df_fnb['alamat'],
        'kecamatan': df_fnb['kecamatan'],
        'kelurahan': df_fnb['kelurahan'],
        'latitude': df_fnb['latitude'],
        'longitude': df_fnb['longitude'],
        'tahun': df_fnb['tahun'],
        'type': df_fnb['type'],
        'additional_info': f"Provinsi: {df_fnb['nama_provinsi']}, Kota: {df_fnb['bps_nama_kabupaten_kota']}",
        'source_dataset': 'fnb'
    })
    datasets['fnb'] = df_fnb_std
    
    # 4. Load supermarket/minimarket
    df_market = pd.read_csv(os.path.join(datasets_path, "jumlah_supermarket_minimarket_bandung.csv"))
    df_market_std = pd.DataFrame({
        'nama': df_market['kategori'] + ' - ' + df_market['kecamatan'],
        'alamat': '',
        'kecamatan': df_market['kecamatan'],
        'kelurahan': '',
        'latitude': '',
        'longitude': '',
        'tahun': df_market['tahun'],
        'type': df_market['type'],
        'additional_info': f"Kategori: {df_market['kategori']}, Jumlah: {df_market['jumlah']} {df_market['satuan']}",
        'source_dataset': 'market'
    })
    datasets['market'] = df_market_std
    
    # Gabungkan semua dataset
    combined_df = pd.concat(list(datasets.values()), ignore_index=True)
    combined_df = combined_df.fillna('')
    
    return combined_df

def filter_by_type(df, business_type):
    """
    Filter dataset berdasarkan type tertentu
    
    Parameters:
    df (pd.DataFrame): Dataset gabungan
    business_type (str): Type yang ingin difilter
    
    Returns:
    pd.DataFrame: Dataset yang sudah difilter
    """
    return df[df['type'] == business_type]

def filter_by_kecamatan(df, kecamatan):
    """
    Filter dataset berdasarkan kecamatan
    
    Parameters:
    df (pd.DataFrame): Dataset gabungan
    kecamatan (str): Nama kecamatan
    
    Returns:
    pd.DataFrame: Dataset yang sudah difilter
    """
    return df[df['kecamatan'].str.upper() == kecamatan.upper()]

def get_summary_stats(df):
    """
    Mendapatkan statistik ringkasan dari dataset
    
    Parameters:
    df (pd.DataFrame): Dataset gabungan
    
    Returns:
    dict: Dictionary berisi statistik ringkasan
    """
    stats = {
        'total_records': len(df),
        'types_distribution': df['type'].value_counts().to_dict(),
        'kecamatan_distribution': df['kecamatan'].value_counts().head(10).to_dict(),
        'records_with_coordinates': len(df[(df['latitude'] != '') & (df['longitude'] != '')]),
        'source_distribution': df['source_dataset'].value_counts().to_dict()
    }
    
    # Analisis tahun
    df_with_year = df[df['tahun'] != '']
    if not df_with_year.empty:
        stats['year_distribution'] = df_with_year['tahun'].value_counts().sort_index().to_dict()
    
    return stats

def save_combined_dataset(df, output_path="datasets/combined_business_data_with_categories.csv"):
    """
    Menyimpan dataset gabungan ke file CSV
    
    Parameters:
    df (pd.DataFrame): Dataset gabungan
    output_path (str): Path output file
    """
    df.to_csv(output_path, index=False)
    print(f"Dataset saved to: {output_path}")

def create_type_specific_files(df, output_dir="datasets"):
    """
    Membuat file terpisah untuk setiap type
    
    Parameters:
    df (pd.DataFrame): Dataset gabungan
    output_dir (str): Directory output
    """
    for type_name in df['type'].unique():
        if type_name:  # Skip empty types
            type_df = filter_by_type(df, type_name)
            output_file = os.path.join(output_dir, f"combined_{type_name}_data.csv")
            type_df.to_csv(output_file, index=False)
            print(f"- {type_name}: {len(type_df)} records saved to {output_file}")

# Example usage
if __name__ == "__main__":
    print("Loading and combining datasets...")
    combined_data = load_and_combine_categorized_datasets()
    
    print(f"Total records: {len(combined_data)}")
    
    # Get summary stats
    stats = get_summary_stats(combined_data)
    print(f"Types available: {list(stats['types_distribution'].keys())}")
    
    # Example filtering
    restaurants = filter_by_type(combined_data, 'restaurant')
    print(f"Total restaurants: {len(restaurants)}")
    
    # Save combined dataset
    save_combined_dataset(combined_data)
    
    # Create type-specific files
    create_type_specific_files(combined_data)
