import pandas as pd
import numpy as np
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def standardize_kecamatan_name(name):
    """Standardisasi nama kecamatan dengan menghapus prefix dan normalisasi"""
    if pd.isna(name):
        return ""
    
    name = str(name).strip()
    
    # Hapus prefix yang umum
    prefixes_to_remove = ['Kecamatan ', 'Kec. ', 'Kec ', 'kecamatan ', 'kec. ', 'kec ']
    for prefix in prefixes_to_remove:
        if name.startswith(prefix):
            name = name[len(prefix):]
    
    # Normalisasi case dan spasi
    name = name.title().strip()
    
    # Perbaikan nama kecamatan yang umum
    name_corrections = {
        'Bandung Kulon': 'Bandung Kulon',
        'Bandung Kidul': 'Bandung Kidul',
        'Bandung Wetan': 'Bandung Wetan',
        'Sumur Bandung': 'Sumur Bandung',
        'Ujung Berung': 'Ujung Berung',
        'Ujungberung': 'Ujung Berung',
        'Babakan Ciparay': 'Babakan Ciparay',
        'Bojongloa Kaler': 'Bojongloa Kaler',
        'Bojongloa Kidul': 'Bojongloa Kidul',
        'Cibeunying Kaler': 'Cibeunying Kaler',
        'Cibeunying Kidul': 'Cibeunying Kidul',
        'Kiaracondong': 'Kiaracondong',
        'Margacinta': 'Margacinta',
        'Gedebage': 'Gedebage'
    }
    
    return name_corrections.get(name, name)

def check_kecamatan_compatibility():
    """
    Fungsi utama untuk mengecek kompatibilitas nama kecamatan
    """
    print("=== CEK KOMPATIBILITAS NAMA KECAMATAN ===")
    
    # Load datasets
    print("📂 Loading datasets...")
    try:
        df_fnb = pd.read_csv('datasets/data_fnb_bandung_with_kecamatan_api.csv')
        print(f"✅ FnB dataset loaded: {len(df_fnb):,} records")
    except FileNotFoundError:
        print("❌ File FnB tidak ditemukan: datasets/data_fnb_bandung_with_kecamatan_api.csv")
        return
    
    try:
        df_kepadatan = pd.read_csv('datasets/cleaned_data_Kepadatan_menurut_kecamatan.csv')
        print(f"✅ Kepadatan dataset loaded: {len(df_kepadatan):,} records")
    except FileNotFoundError:
        print("❌ File kepadatan tidak ditemukan: datasets/cleaned_data_Kepadatan_menurut_kecamatan.csv")
        return
    
    # Standardisasi nama kecamatan
    print(f"\n🔧 Standardisasi nama kecamatan...")
    df_fnb['kecamatan_clean'] = df_fnb['kecamatan'].apply(standardize_kecamatan_name)
    df_kepadatan['kecamatan_clean'] = df_kepadatan['Kecamatan'].apply(standardize_kecamatan_name)
    
    # Filter data FnB yang memiliki kecamatan valid (bukan status error/tidak ditemukan)
    df_fnb_valid = df_fnb[
        ~df_fnb['kecamatan'].isin(['Tidak Diketahui', 'Tidak Ditemukan', 'API Tidak Tersedia']) &
        ~df_fnb['kecamatan'].str.startswith('Error', na=False) &
        (df_fnb['kecamatan_clean'] != '')
    ].copy()
    
    print(f"📊 FnB records dengan kecamatan valid: {len(df_fnb_valid):,}")
    
    # Analisis kecamatan di masing-masing dataset
    print(f"\n📋 ANALISIS KECAMATAN:")
    
    kecamatan_fnb = set(df_fnb_valid['kecamatan_clean'].unique())
    kecamatan_kepadatan = set(df_kepadatan['kecamatan_clean'].unique())
    
    print(f"🏘️  Kecamatan di FnB dataset: {len(kecamatan_fnb)}")
    print(f"🏘️  Kecamatan di Kepadatan dataset: {len(kecamatan_kepadatan)}")
    
    # Kecamatan yang cocok exact match
    kecamatan_match = kecamatan_fnb.intersection(kecamatan_kepadatan)
    print(f"✅ Kecamatan yang cocok (exact): {len(kecamatan_match)}")
    
    # Kecamatan yang tidak cocok
    kecamatan_fnb_only = kecamatan_fnb - kecamatan_kepadatan
    kecamatan_kepadatan_only = kecamatan_kepadatan - kecamatan_fnb
    
    print(f"❓ Kecamatan hanya di FnB: {len(kecamatan_fnb_only)}")
    print(f"❓ Kecamatan hanya di Kepadatan: {len(kecamatan_kepadatan_only)}")
    
    # Detail kecamatan yang cocok
    if kecamatan_match:
        print(f"\n✅ KECAMATAN YANG COCOK ({len(kecamatan_match)}):")
        for kec in sorted(kecamatan_match):
            count_fnb = len(df_fnb_valid[df_fnb_valid['kecamatan_clean'] == kec])
            print(f"   • {kec} ({count_fnb:,} FnB records)")
    
    # Detail kecamatan yang tidak cocok
    if kecamatan_fnb_only:
        print(f"\n❓ KECAMATAN HANYA DI FnB ({len(kecamatan_fnb_only)}):")
        for kec in sorted(kecamatan_fnb_only):
            count = len(df_fnb_valid[df_fnb_valid['kecamatan_clean'] == kec])
            print(f"   • {kec} ({count:,} records)")
    
    if kecamatan_kepadatan_only:
        print(f"\n❓ KECAMATAN HANYA DI KEPADATAN ({len(kecamatan_kepadatan_only)}):")
        for kec in sorted(kecamatan_kepadatan_only):
            print(f"   • {kec}")
    
    # Coba fuzzy matching untuk kecamatan yang tidak cocok
    print(f"\n🔍 FUZZY MATCHING untuk kecamatan yang tidak cocok...")
    fuzzy_matches = []
    
    for kec_fnb in kecamatan_fnb_only:
        best_match = None
        best_score = 0
        
        for kec_kepadatan in kecamatan_kepadatan_only:
            score = similarity(kec_fnb.lower(), kec_kepadatan.lower())
            if score > best_score and score > 0.6:  # Threshold 60%
                best_score = score
                best_match = kec_kepadatan
        
        if best_match:
            count = len(df_fnb_valid[df_fnb_valid['kecamatan_clean'] == kec_fnb])
            fuzzy_matches.append({
                'fnb_kecamatan': kec_fnb,
                'kepadatan_kecamatan': best_match,
                'similarity': best_score,
                'fnb_count': count
            })
    
    if fuzzy_matches:
        print(f"\n🎯 KEMUNGKINAN MATCHING ({len(fuzzy_matches)}):")
        for match in sorted(fuzzy_matches, key=lambda x: x['similarity'], reverse=True):
            print(f"   • {match['fnb_kecamatan']} ≈ {match['kepadatan_kecamatan']} ({match['similarity']:.1%}, {match['fnb_count']} records)")
    
    # Pisahkan file berdasarkan kecocokan
    print(f"\n📁 MEMISAHKAN FILE BERDASARKAN KECOCOKAN...")
    
    # File 1: Data FnB yang cocok dengan kepadatan
    df_fnb_matched = df_fnb_valid[df_fnb_valid['kecamatan_clean'].isin(kecamatan_match)].copy()
    
    # File 2: Data FnB yang tidak cocok dengan kepadatan  
    df_fnb_unmatched = df_fnb_valid[df_fnb_valid['kecamatan_clean'].isin(kecamatan_fnb_only)].copy()
    
    # File 3: Data FnB yang tidak valid (error, tidak ditemukan, dll)
    df_fnb_invalid = df_fnb[
        df_fnb['kecamatan'].isin(['Tidak Diketahui', 'Tidak Ditemukan', 'API Tidak Tersedia']) |
        df_fnb['kecamatan'].str.startswith('Error', na=False) |
        (df_fnb['kecamatan_clean'] == '')
    ].copy()
    
    # Simpan file-file terpisah
    files_created = []
    
    if len(df_fnb_matched) > 0:
        file_matched = 'datasets/fnb_matched_with_kepadatan.csv'
        df_fnb_matched.to_csv(file_matched, index=False)
        files_created.append(file_matched)
        print(f"✅ File matched: {file_matched} ({len(df_fnb_matched):,} records)")
    
    if len(df_fnb_unmatched) > 0:
        file_unmatched = 'datasets/fnb_unmatched_with_kepadatan.csv'
        df_fnb_unmatched.to_csv(file_unmatched, index=False)
        files_created.append(file_unmatched)
        print(f"❓ File unmatched: {file_unmatched} ({len(df_fnb_unmatched):,} records)")
    
    if len(df_fnb_invalid) > 0:
        file_invalid = 'datasets/fnb_invalid_kecamatan.csv'
        df_fnb_invalid.to_csv(file_invalid, index=False)
        files_created.append(file_invalid)
        print(f"❌ File invalid: {file_invalid} ({len(df_fnb_invalid):,} records)")
    
    # Buat file mapping kecamatan
    mapping_data = []
    
    # Exact matches
    for kec in sorted(kecamatan_match):
        count = len(df_fnb_valid[df_fnb_valid['kecamatan_clean'] == kec])
        mapping_data.append({
            'fnb_kecamatan': kec,
            'kepadatan_kecamatan': kec,
            'match_type': 'exact',
            'similarity': 1.0,
            'fnb_count': count,
            'status': 'matched'
        })
    
    # Fuzzy matches
    for match in fuzzy_matches:
        mapping_data.append({
            'fnb_kecamatan': match['fnb_kecamatan'],
            'kepadatan_kecamatan': match['kepadatan_kecamatan'],
            'match_type': 'fuzzy',
            'similarity': match['similarity'],
            'fnb_count': match['fnb_count'],
            'status': 'potential_match'
        })
    
    # Unmatched
    for kec in kecamatan_fnb_only:
        if kec not in [m['fnb_kecamatan'] for m in fuzzy_matches]:
            count = len(df_fnb_valid[df_fnb_valid['kecamatan_clean'] == kec])
            mapping_data.append({
                'fnb_kecamatan': kec,
                'kepadatan_kecamatan': '',
                'match_type': 'none',
                'similarity': 0.0,
                'fnb_count': count,
                'status': 'unmatched'
            })
    
    if mapping_data:
        df_mapping = pd.DataFrame(mapping_data)
        mapping_file = 'datasets/kecamatan_mapping_analysis.csv'
        df_mapping.to_csv(mapping_file, index=False)
        files_created.append(mapping_file)
        print(f"📋 File mapping: {mapping_file}")
    
    # Summary statistik
    print(f"\n📊 SUMMARY STATISTIK:")
    print(f"   📈 Total FnB records: {len(df_fnb):,}")
    print(f"   ✅ Valid kecamatan: {len(df_fnb_valid):,} ({len(df_fnb_valid)/len(df_fnb)*100:.1f}%)")
    print(f"   🎯 Matched dengan kepadatan: {len(df_fnb_matched):,} ({len(df_fnb_matched)/len(df_fnb)*100:.1f}%)")
    print(f"   ❓ Unmatched: {len(df_fnb_unmatched):,} ({len(df_fnb_unmatched)/len(df_fnb)*100:.1f}%)")
    print(f"   ❌ Invalid: {len(df_fnb_invalid):,} ({len(df_fnb_invalid)/len(df_fnb)*100:.1f}%)")
    
    print(f"\n📁 FILES CREATED:")
    for file in files_created:
        print(f"   • {file}")
    
    return {
        'total_records': len(df_fnb),
        'valid_records': len(df_fnb_valid),
        'matched_records': len(df_fnb_matched),
        'unmatched_records': len(df_fnb_unmatched),
        'invalid_records': len(df_fnb_invalid),
        'files_created': files_created,
        'kecamatan_exact_match': list(kecamatan_match),
        'kecamatan_fuzzy_match': fuzzy_matches
    }

if __name__ == "__main__":
    result = check_kecamatan_compatibility()
    print(f"\n🎉 Analisis selesai!")
    print(f"💾 {len(result['files_created'])} file berhasil dibuat")
