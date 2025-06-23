"""
Script analisis dataset gabungan yang sudah distandarisasi
Mengecek kualitas data dan membuat summary statistik
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_combined_dataset():
    """
    Analisis detail dataset gabungan yang sudah distandarisasi
    """
    
    print("=== ANALISIS DATASET GABUNGAN STANDAR ===")
    
    # Load dataset gabungan
    try:
        df = pd.read_csv("datasets/combined_standardized_datasets.csv")
        print(f"✅ Dataset berhasil dimuat: {len(df):,} records")
    except FileNotFoundError:
        print("❌ File combined_standardized_datasets.csv tidak ditemukan!")
        return
    
    print(f"\n📊 INFORMASI UMUM:")
    print(f"   Total records: {len(df):,}")
    print(f"   Total kolom: {len(df.columns)}")
    print(f"   Kolom: {list(df.columns)}")
    
    # Cek missing values
    print(f"\n❓ MISSING VALUES:")
    missing_counts = df.isnull().sum()
    for col, count in missing_counts.items():
        if count > 0:
            percentage = (count / len(df)) * 100
            print(f"   {col}: {count:,} ({percentage:.1f}%)")
        else:
            print(f"   {col}: ✅ No missing values")
    
    # Cek empty strings
    print(f"\n📝 EMPTY STRINGS:")
    for col in ['nama', 'alamat', 'kecamatan']:
        if col in df.columns:
            empty_count = len(df[df[col] == ''])
            if empty_count > 0:
                percentage = (empty_count / len(df)) * 100
                print(f"   {col}: {empty_count:,} kosong ({percentage:.1f}%)")
            else:
                print(f"   {col}: ✅ No empty values")
    
    # Analisis per type
    print(f"\n📈 DISTRIBUSI PER TYPE:")
    type_stats = df['type'].value_counts()
    for type_name, count in type_stats.items():
        percentage = (count / len(df)) * 100
        print(f"   {type_name}: {count:,} ({percentage:.1f}%)")
    
    # Analisis per source file
    print(f"\n📁 DISTRIBUSI PER SOURCE FILE:")
    source_stats = df['source_file'].value_counts()
    for source, count in source_stats.items():
        percentage = (count / len(df)) * 100
        print(f"   {source}: {count:,} ({percentage:.1f}%)")
    
    # Analisis kecamatan
    print(f"\n🏘️ TOP 15 KECAMATAN:")
    kecamatan_stats = df['kecamatan'].value_counts()
    for i, (kecamatan, count) in enumerate(kecamatan_stats.head(15).items(), 1):
        percentage = (count / len(df)) * 100
        print(f"   {i:2d}. {kecamatan}: {count:,} ({percentage:.1f}%)")
    
    # Analisis koordinat (jika ada)
    if 'latitude' in df.columns and 'longitude' in df.columns:
        coords_available = df[(df['latitude'].notna()) & (df['longitude'].notna()) & 
                             (df['latitude'] != '') & (df['longitude'] != '')]
        coord_percentage = (len(coords_available) / len(df)) * 100
        print(f"\n📍 DATA KOORDINAT:")
        print(f"   Dengan koordinat: {len(coords_available):,} ({coord_percentage:.1f}%)")
        print(f"   Tanpa koordinat: {len(df) - len(coords_available):,} ({100-coord_percentage:.1f}%)")
    
    # Analisis tahun (jika ada)
    if 'tahun' in df.columns:
        tahun_available = df[(df['tahun'].notna()) & (df['tahun'] != '')]
        print(f"\n📅 DATA TAHUN:")
        if len(tahun_available) > 0:
            tahun_stats = tahun_available['tahun'].value_counts().sort_index()
            for tahun, count in tahun_stats.items():
                percentage = (count / len(df)) * 100
                print(f"   {tahun}: {count:,} ({percentage:.1f}%)")
        print(f"   Tanpa tahun: {len(df) - len(tahun_available):,}")
    
    # Kualitas data
    print(f"\n✅ KUALITAS DATA:")
    
    # Records dengan data lengkap
    complete_records = df[
        (df['nama'] != '') & 
        (df['alamat'] != '') & 
        (df['kecamatan'] != '') & 
        (df['type'] != '')
    ]
    complete_percentage = (len(complete_records) / len(df)) * 100
    print(f"   Data lengkap (nama, alamat, kecamatan, type): {len(complete_records):,} ({complete_percentage:.1f}%)")
    
    # Records dengan minimal nama dan kecamatan
    minimal_records = df[
        (df['nama'] != '') & 
        (df['kecamatan'] != '')
    ]
    minimal_percentage = (len(minimal_records) / len(df)) * 100
    print(f"   Data minimal (nama, kecamatan): {len(minimal_records):,} ({minimal_percentage:.1f}%)")
    
    # Records bermasalah
    problematic = df[
        (df['nama'] == '') | 
        (df['kecamatan'] == '')
    ]
    if len(problematic) > 0:
        prob_percentage = (len(problematic) / len(df)) * 100
        print(f"   ⚠️  Data bermasalah: {len(problematic):,} ({prob_percentage:.1f}%)")
    
    return df

def create_summary_files(df):
    """
    Buat file summary untuk berbagai keperluan
    """
    print(f"\n💾 MEMBUAT FILE SUMMARY:")
    
    # 1. File data lengkap saja
    complete_df = df[
        (df['nama'] != '') & 
        (df['alamat'] != '') & 
        (df['kecamatan'] != '') & 
        (df['type'] != '')
    ]
    
    if len(complete_df) > 0:
        complete_file = "datasets/combined_complete_data_only.csv"
        complete_df.to_csv(complete_file, index=False)
        print(f"   ✅ Data lengkap: {complete_file} ({len(complete_df):,} records)")

    # 3. Summary statistik
    summary_stats = {
        'total_records': len(df),
        'restaurants': len(df[df['type'] == 'restaurant']),
        'tourism_shopping': len(df[df['type'] == 'tourism_shopping']),
        'unique_kecamatan': df['kecamatan'].nunique(),
        'with_coordinates': len(df[(df['latitude'].notna()) & (df['longitude'].notna())]) if 'latitude' in df.columns else 0,
        'complete_data': len(complete_df)
    }
    
    summary_df = pd.DataFrame([summary_stats])
    summary_df.to_csv("datasets/dataset_summary_stats.csv", index=False)
    print(f"   ✅ Summary stats: datasets/dataset_summary_stats.csv")

def main():
    """
    Fungsi utama analisis
    """
    print("🔍 ANALISIS DATASET GABUNGAN STANDAR")
    print("="*60)
    
    # Analisis dataset
    df = analyze_combined_dataset()
    
    if df is not None:
        # Buat file summary
        create_summary_files(df)
        
        print(f"\n🎉 ANALISIS SELESAI!")
        print(f"📊 Dataset gabungan siap untuk digunakan")
        print(f"📁 File utama: datasets/combined_standardized_datasets.csv")
        print(f"📋 Kolom standar: nama, alamat, kecamatan, type")
        print(f"📈 Total: {len(df):,} records dari 2 dataset")

if __name__ == "__main__":
    main()
