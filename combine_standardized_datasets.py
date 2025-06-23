"""
Script untuk menyatukan datasets di folder datasets dengan kolom standar
Kolom yang harus ada: nama, alamat, kecamatan, type
Exclude: cleaned_taman, cleaned_data_kepadatan, jumlah_supermarket
"""

import pandas as pd
import os
import glob

def identify_datasets():
    """
    Identifikasi dan kategorisasi datasets yang ada
    """
    datasets_path = "datasets"
    
    # Pola file yang akan diexclude
    exclude_patterns = [
        '*taman*',
        '*kepadatan*', 
        '*supermarket*',
        '*minimarket*'
    ]
    
    # Ambil semua file CSV
    all_csv_files = glob.glob(os.path.join(datasets_path, "*.csv"))
    
    # Filter out excluded files
    included_files = []
    excluded_files = []
    
    for file in all_csv_files:
        filename = os.path.basename(file).lower()
        exclude = False
        
        for pattern in exclude_patterns:
            if any(keyword in filename for keyword in pattern.replace('*', '').split()):
                exclude = True
                break
        
        if exclude:
            excluded_files.append(file)
        else:
            included_files.append(file)
    
    return included_files, excluded_files

def standardize_columns(df, filename, type_category):
    """
    Standardisasi kolom dataset ke format: nama, alamat, kecamatan, type
    """
    standardized_df = pd.DataFrame()
    
    # Mapping kolom berdasarkan jenis dataset
    if 'fnb' in filename.lower() or 'restaurant' in filename.lower():
        # Dataset FnB
        standardized_df['nama'] = df.get('nama_rumah_makan', df.get('nama', ''))
        standardized_df['alamat'] = df.get('alamat', '')
        standardized_df['kecamatan'] = df.get('kecamatan', '')
        standardized_df['type'] = 'restaurant'
        
        # Kolom tambahan untuk FnB
        if 'latitude' in df.columns:
            standardized_df['latitude'] = df['latitude']
        if 'longitude' in df.columns:
            standardized_df['longitude'] = df['longitude']
        if 'tahun' in df.columns:
            standardized_df['tahun'] = df['tahun']
            
    elif 'wisata' in filename.lower() or 'belanja' in filename.lower():
        # Dataset wisata/belanja
        standardized_df['nama'] = df.get('nama_tempat', df.get('nama', ''))
        standardized_df['alamat'] = df.get('alamat', '')
        standardized_df['kecamatan'] = df.get('kecamatan', '')
        standardized_df['type'] = 'tourism_shopping'
        
        # Kolom tambahan
        if 'latitude' in df.columns:
            standardized_df['latitude'] = df['latitude']
        if 'longitude' in df.columns:
            standardized_df['longitude'] = df['longitude']
        if 'tahun' in df.columns:
            standardized_df['tahun'] = df['tahun']
            
    else:
        # Dataset lainnya - coba mapping otomatis
        nama_candidates = ['nama', 'nama_tempat', 'nama_rumah_makan', 'name']
        alamat_candidates = ['alamat', 'address', 'jalan']
        kecamatan_candidates = ['kecamatan', 'district', 'subdistrict']
        
        # Cari kolom nama
        nama_col = None
        for candidate in nama_candidates:
            if candidate in df.columns:
                nama_col = candidate
                break
        
        # Cari kolom alamat
        alamat_col = None
        for candidate in alamat_candidates:
            if candidate in df.columns:
                alamat_col = candidate
                break
                
        # Cari kolom kecamatan
        kecamatan_col = None
        for candidate in kecamatan_candidates:
            if candidate in df.columns:
                kecamatan_col = candidate
                break
        
        standardized_df['nama'] = df[nama_col] if nama_col else 'Tidak Diketahui'
        standardized_df['alamat'] = df[alamat_col] if alamat_col else 'Tidak Diketahui'
        standardized_df['kecamatan'] = df[kecamatan_col] if kecamatan_col else 'Tidak Diketahui'
        standardized_df['type'] = type_category if type_category else 'other'
        
        # Kolom tambahan jika ada
        for col in ['latitude', 'longitude', 'tahun']:
            if col in df.columns:
                standardized_df[col] = df[col]
    
    # Tambahkan kolom source untuk tracking
    standardized_df['source_file'] = os.path.basename(filename)
    
    return standardized_df

def combine_datasets():
    """
    Fungsi utama untuk menggabungkan datasets
    """
    print("=== MENYATUKAN DATASETS DENGAN KOLOM STANDAR ===")
    
    # Identifikasi datasets
    included_files, excluded_files = identify_datasets()
    
    print(f"📁 Files yang akan diproses:")
    for file in included_files:
        print(f"   ✅ {os.path.basename(file)}")
    
    print(f"\n📁 Files yang dikecualikan:")
    for file in excluded_files:
        print(f"   ❌ {os.path.basename(file)}")
    
    if not included_files:
        print("❌ Tidak ada file yang bisa diproses!")
        return None
    
    # List untuk menyimpan dataframe
    combined_datasets = []
    
    # Proses setiap file
    for file_path in included_files:
        filename = os.path.basename(file_path)
        print(f"\n🔄 Memproses: {filename}")
        
        try:
            # Baca dataset
            df = pd.read_csv(file_path)
            print(f"   📊 Rows: {len(df)}, Columns: {len(df.columns)}")
            print(f"   📋 Kolom: {list(df.columns)}")
            
            # Tentukan type berdasarkan nama file
            type_category = None
            if 'fnb' in filename.lower():
                type_category = 'restaurant'
            elif 'wisata' in filename.lower() or 'belanja' in filename.lower():
                type_category = 'tourism_shopping'
            
            # Standardisasi kolom
            standardized_df = standardize_columns(df, filename, type_category)
            
            if len(standardized_df) > 0:
                combined_datasets.append(standardized_df)
                print(f"   ✅ Berhasil standardisasi: {len(standardized_df)} records")
            else:
                print(f"   ❌ Gagal standardisasi")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    if not combined_datasets:
        print("❌ Tidak ada dataset yang berhasil diproses!")
        return None
    
    # Gabungkan semua dataset
    print(f"\n🔗 Menggabungkan {len(combined_datasets)} datasets...")
    final_df = pd.concat(combined_datasets, ignore_index=True)
    
    # Bersihkan data
    final_df = final_df.fillna('')
    
    # Statistik hasil
    print(f"\n📊 HASIL PENGGABUNGAN:")
    print(f"   Total records: {len(final_df):,}")
    print(f"   Kolom utama: {['nama', 'alamat', 'kecamatan', 'type']}")
    
    print(f"\n📈 Distribusi per type:")
    type_counts = final_df['type'].value_counts()
    for type_name, count in type_counts.items():
        print(f"   {type_name}: {count:,} records")
    
    print(f"\n📈 Distribusi per source file:")
    source_counts = final_df['source_file'].value_counts()
    for source, count in source_counts.items():
        print(f"   {source}: {count:,} records")
    
    print(f"\n🏘️ Top 10 Kecamatan:")
    kecamatan_counts = final_df['kecamatan'].value_counts()
    for kecamatan, count in kecamatan_counts.head(10).items():
        print(f"   {kecamatan}: {count:,} records")
    
    return final_df

def save_combined_dataset(df, output_filename="datasets/combined_standardized_datasets.csv"):
    """
    Simpan dataset gabungan ke file
    """
    if df is None:
        return
    
    print(f"\n💾 Menyimpan dataset gabungan...")
    
    # Simpan file utama
    df.to_csv(output_filename, index=False)
    print(f"   ✅ File utama: {output_filename}")
    
    # Simpan per type
    types = df['type'].unique()
    for type_name in types:
        if type_name and type_name != '':
            type_df = df[df['type'] == type_name]
            type_filename = f"datasets/combined_{type_name}_standardized.csv"
            type_df.to_csv(type_filename, index=False)
            print(f"   ✅ File {type_name}: {type_filename} ({len(type_df):,} records)")
    
    # Sample preview
    print(f"\n👀 PREVIEW DATASET GABUNGAN:")
    print(df[['nama', 'alamat', 'kecamatan', 'type']].head())
    
    return output_filename

if __name__ == "__main__":
    print("🚀 Script Penggabungan Dataset dengan Kolom Standar")
    print("="*60)
    
    # Gabungkan datasets
    combined_df = combine_datasets()
    
    if combined_df is not None:
        # Simpan hasil
        output_file = save_combined_dataset(combined_df)
        
        print(f"\n🎉 SELESAI!")
        print(f"📁 Dataset gabungan tersimpan di: {output_file}")
        print(f"📊 Total: {len(combined_df):,} records dengan kolom standar")
        print(f"📋 Kolom: nama, alamat, kecamatan, type + tambahan")
    else:
        print(f"\n❌ Gagal menggabungkan datasets!")
