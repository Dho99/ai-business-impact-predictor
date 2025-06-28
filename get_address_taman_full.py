#!/usr/bin/env python3
"""
Script lengkap untuk mendapatkan alamat lengkap dari SEMUA dataset taman kota bandung 
menggunakan Google Maps API yang sudah digunakan sebelumnya.
Dengan optimasi batch processing dan error handling yang robust.
"""

import pandas as pd
import googlemaps
import time
from tqdm import tqdm
import numpy as np
import os
from datetime import datetime

def setup_google_maps_api():
    """Setup Google Maps API client"""
    # API Key yang sudah digunakan sebelumnya
    API_KEY = 'AIzaSyAMu_PiVlP52Z99Vzzx2umpW4lASFGCYeU'
    
    try:
        gmaps = googlemaps.Client(key=API_KEY)
        print("✅ Google Maps API client berhasil diinisialisasi")
        return gmaps
    except Exception as e:
        print(f"❌ Error inisialisasi Google Maps API: {e}")
        return None

def cari_alamat_taman(gmaps, row, verbose=False):
    """
    Mencari alamat lengkap berdasarkan nama taman dan kecamatan menggunakan Google Maps API.
    
    Parameters:
    - gmaps: Google Maps client
    - row: Baris dataframe yang berisi 'nama_taman' dan 'kecamatan'
    - verbose: Apakah menampilkan detail log (default False untuk batch processing)
    
    Returns:
    - Dict dengan alamat lengkap, koordinat, dan status
    """
    
    if not gmaps:
        return {
            'alamat': "API Tidak Tersedia",
            'latitude': None,
            'longitude': None,
            'status': 'API Error',
            'query_used': 'No API'
        }
    
    try:
        # Buat query pencarian yang lebih spesifik
        nama_taman = str(row['nama_taman']).strip()
        kecamatan = str(row['kecamatan']).strip()
        
        # Variasi query pencarian (prioritas dari yang paling spesifik)
        search_queries = [
            f"{nama_taman}, {kecamatan}, Bandung, Jawa Barat",
            f"{nama_taman}, Kecamatan {kecamatan}, Kota Bandung",
            f"Taman {nama_taman}, {kecamatan}, Bandung",
            f"{nama_taman}, {kecamatan}, Bandung",
            f"{nama_taman} Bandung"
        ]
        
        if verbose:
            print(f"🔍 Mencari alamat untuk: {nama_taman} di {kecamatan}")
        
        # Coba setiap query sampai dapat hasil
        for i, query in enumerate(search_queries):
            try:
                if verbose:
                    print(f"   Query {i+1}: {query}")
                
                # Geocoding untuk mendapatkan koordinat dan alamat
                geocode_result = gmaps.geocode(query)
                
                if geocode_result:
                    # Ambil alamat lengkap dari result pertama
                    formatted_address = geocode_result[0]['formatted_address']
                    
                    # Ambil koordinat juga
                    location = geocode_result[0]['geometry']['location']
                    lat = location['lat']
                    lng = location['lng']
                    
                    if verbose:
                        print(f"   ✅ Ditemukan: {formatted_address}")
                        print(f"   📍 Koordinat: {lat}, {lng}")
                    
                    # Return dalam format yang terstruktur
                    return {
                        'alamat': formatted_address,
                        'latitude': lat,
                        'longitude': lng,
                        'status': 'Success',
                        'query_used': query
                    }
                
                # Delay antar query untuk menghormati rate limit
                time.sleep(0.1)
                
            except Exception as query_error:
                if verbose:
                    print(f"   ❌ Error pada query {i+1}: {query_error}")
                continue
        
        # Jika semua query gagal
        if verbose:
            print(f"   ⚠️ Tidak ditemukan alamat untuk {nama_taman}")
        
        return {
            'alamat': 'Tidak Ditemukan',
            'latitude': None,
            'longitude': None,
            'status': 'Not Found',
            'query_used': 'All queries failed'
        }
        
    except Exception as e:
        if verbose:
            print(f"   ❌ Error umum: {e}")
        
        return {
            'alamat': f'Error: {str(e)}',
            'latitude': None,
            'longitude': None,
            'status': 'Error',
            'query_used': 'Error occurred'
        }

def save_checkpoint(df, checkpoint_name):
    """Simpan checkpoint untuk recovery jika ada error"""
    checkpoint_file = f'./datasets/checkpoint_{checkpoint_name}.csv'
    df.to_csv(checkpoint_file, index=False)
    print(f"📄 Checkpoint disimpan: {checkpoint_file}")

def load_checkpoint(checkpoint_name):
    """Load checkpoint jika ada"""
    checkpoint_file = f'./datasets/checkpoint_{checkpoint_name}.csv'
    if os.path.exists(checkpoint_file):
        df = pd.read_csv(checkpoint_file)
        print(f"📄 Checkpoint ditemukan dan dimuat: {checkpoint_file}")
        return df
    return None

def estimate_cost_and_time(total_records, daily_free_limit=200):
    """Estimasi biaya dan waktu processing"""
    print("\n💰 ESTIMASI BIAYA DAN WAKTU:")
    
    # Hitung biaya (setelah 200 gratis per hari)
    if total_records <= daily_free_limit:
        cost = 0
        paid_requests = 0
    else:
        paid_requests = total_records - daily_free_limit
        cost = (paid_requests / 1000) * 5  # $5 per 1000 requests
    
    # Estimasi waktu (dengan delay 0.3 detik per request)
    estimated_time_seconds = total_records * 0.3
    estimated_time_minutes = estimated_time_seconds / 60
    estimated_time_hours = estimated_time_minutes / 60
    
    print(f"   📊 Total requests: {total_records:,}")
    print(f"   🆓 Gratis (200 per hari): {min(total_records, daily_free_limit):,}")
    print(f"   💳 Berbayar: {paid_requests:,}")
    print(f"   💰 Estimasi biaya: ${cost:.2f}")
    print(f"   ⏱️  Estimasi waktu: {estimated_time_minutes:.1f} menit ({estimated_time_hours:.1f} jam)")
    
    return cost, estimated_time_minutes

def main():
    """Fungsi utama untuk memproses semua data taman"""
    
    print("="*80)
    print("🏞️  SCRIPT PENCARIAN ALAMAT TAMAN KOTA BANDUNG - FULL PROCESSING")
    print("="*80)
    
    # Load dataset taman kota bandung
    print("\n📂 Membaca dataset taman kota bandung...")
    try:
        df = pd.read_csv('./datasets/cleaned_taman_kota_bandung.csv')
        print(f"✅ Dataset berhasil dimuat: {len(df)} records")
        print(f"📊 Kolom yang tersedia: {list(df.columns)}")
    except Exception as e:
        print(f"❌ Error membaca dataset: {e}")
        return
    
    # Tampilkan distribusi per kecamatan
    print(f"\n📈 Distribusi taman per kecamatan:")
    kecamatan_counts = df['kecamatan'].value_counts()
    print(kecamatan_counts.head(10))
    print(f"   ... dan {len(kecamatan_counts)} kecamatan lainnya")
    
    # Setup Google Maps API
    print(f"\n🔧 Setup Google Maps API...")
    gmaps = setup_google_maps_api()
    
    if not gmaps:
        print("❌ Tidak dapat melanjutkan tanpa Google Maps API")
        return
    
    # Estimasi biaya dan waktu
    cost, time_minutes = estimate_cost_and_time(len(df))
    
    # Konfirmasi user untuk melanjutkan
    if cost > 10:  # Warning jika biaya lebih dari $10
        proceed = input(f"\n⚠️  Proses akan menggunakan ${cost:.2f} kredit dan memakan waktu {time_minutes:.1f} menit. Lanjutkan? (y/n): ")
        if proceed.lower() != 'y':
            print("❌ Proses dibatalkan")
            return
    
    # Cek apakah ada checkpoint yang bisa dilanjutkan
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    checkpoint_name = f"taman_address_{timestamp}"
    
    existing_checkpoint = load_checkpoint("taman_address_latest")
    if existing_checkpoint is not None:
        use_checkpoint = input("🔄 Ditemukan checkpoint sebelumnya. Lanjutkan dari checkpoint? (y/n): ")
        if use_checkpoint.lower() == 'y':
            df = existing_checkpoint
            print(f"✅ Melanjutkan dari checkpoint dengan {len(df)} records")
        else:
            print("🆕 Memulai proses baru...")
    
    # Inisialisasi kolom hasil jika belum ada
    if 'alamat_lengkap' not in df.columns:
        df['alamat_lengkap'] = 'Belum Diproses'
        df['latitude'] = None
        df['longitude'] = None
        df['status'] = 'Pending'
        df['query_used'] = ''
        df['processed_at'] = ''
    
    # Identifikasi data yang belum diproses
    unprocessed_mask = (df['status'] == 'Pending') | (df['status'] == '') | (df['alamat_lengkap'] == 'Belum Diproses')
    df_unprocessed = df[unprocessed_mask]
    
    print(f"\n🎯 Data yang akan diproses:")
    print(f"   📊 Total data: {len(df):,}")
    print(f"   ✅ Sudah diproses: {len(df) - len(df_unprocessed):,}")
    print(f"   🔄 Akan diproses: {len(df_unprocessed):,}")
    
    if len(df_unprocessed) == 0:
        print("🎉 Semua data sudah diproses!")
        return
    
    print(f"\n🚀 Memulai proses pencarian alamat untuk {len(df_unprocessed)} taman...")
    print(f"💡 Progress akan disimpan setiap 50 records untuk recovery")
    print("-" * 80)
    
    # Progress tracking
    success_count = 0
    error_count = 0
    not_found_count = 0
    processed_count = 0
    
    # Proses setiap taman dengan progress bar
    for idx, (index, row) in enumerate(tqdm(df_unprocessed.iterrows(), total=len(df_unprocessed), desc="🔍 Mencari alamat")):
        
        # Panggil fungsi pencarian alamat (verbose=False untuk batch processing)
        result = cari_alamat_taman(gmaps, row, verbose=False)
        
        # Update dataframe dengan hasil
        if isinstance(result, dict):
            df.at[index, 'alamat_lengkap'] = result['alamat']
            df.at[index, 'latitude'] = result['latitude']
            df.at[index, 'longitude'] = result['longitude']
            df.at[index, 'status'] = result['status']
            df.at[index, 'query_used'] = result['query_used']
            df.at[index, 'processed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Count status
            if result['status'] == 'Success':
                success_count += 1
            elif result['status'] == 'Not Found':
                not_found_count += 1
            else:
                error_count += 1
        else:
            # Fallback jika result bukan dict
            df.at[index, 'alamat_lengkap'] = str(result)
            df.at[index, 'status'] = 'Unknown'
            error_count += 1
        
        processed_count += 1
        
        # Simpan checkpoint setiap 50 records
        if processed_count % 50 == 0:
            save_checkpoint(df, "taman_address_latest")
            print(f"\n📊 Progress checkpoint - {processed_count}/{len(df_unprocessed)}")
            print(f"   ✅ Berhasil: {success_count} | ⚠️ Tidak ditemukan: {not_found_count} | ❌ Error: {error_count}")
        
        # Delay antar request untuk menghormati rate limit
        time.sleep(0.3)  # 300ms delay untuk memastikan tidak overload
    
    print("\n" + "="*80)
    print("📊 HASIL AKHIR PROCESSING")
    print("="*80)
    
    total_processed = success_count + not_found_count + error_count
    print(f"✅ Berhasil ditemukan : {success_count:,}/{total_processed:,} ({success_count/total_processed*100:.1f}%)")
    print(f"⚠️  Tidak ditemukan   : {not_found_count:,}/{total_processed:,} ({not_found_count/total_processed*100:.1f}%)")
    print(f"❌ Error             : {error_count:,}/{total_processed:,} ({error_count/total_processed*100:.1f}%)")
    
    # Simpan hasil final
    output_file = './datasets/cleaned_taman_kota_bandung_with_address.csv'
    df.to_csv(output_file, index=False)
    print(f"\n💾 Hasil lengkap disimpan ke: {output_file}")
    
    # Simpan juga yang berhasil saja untuk analisis
    df_success = df[df['status'] == 'Success'].copy()
    success_file = './datasets/taman_kota_bandung_with_complete_address.csv'
    df_success.to_csv(success_file, index=False)
    print(f"💾 Data lengkap (berhasil saja) disimpan ke: {success_file}")
    
    # Analisis hasil
    if len(df_success) > 0:
        print(f"\n🎯 ANALISIS HASIL:")
        print(f"   📍 Total taman dengan alamat lengkap: {len(df_success):,}")
        print(f"   🗺️  Total taman dengan koordinat: {df_success['latitude'].notna().sum():,}")
        print(f"   🏙️  Kecamatan terwakili: {df_success['kecamatan'].nunique():,}")
        
        # Distribusi hasil per kecamatan
        success_by_kecamatan = df_success['kecamatan'].value_counts()
        print(f"\n🏆 TOP 10 KECAMATAN DENGAN TAMAN TERBANYAK (yang berhasil):")
        for i, (kecamatan, count) in enumerate(success_by_kecamatan.head(10).items(), 1):
            print(f"   {i:2d}. {kecamatan:<20} : {count:3d} taman")
    
    # Hapus checkpoint karena sudah selesai
    try:
        checkpoint_file = './datasets/checkpoint_taman_address_latest.csv'
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)
            print(f"🗑️  Checkpoint dihapus: {checkpoint_file}")
    except:
        pass
    
    print("\n🏁 Processing selesai!")
    print("✨ Dataset taman kota Bandung sekarang sudah dilengkapi dengan alamat dan koordinat!")
    print(f"📊 Siap untuk digabungkan dengan dataset lain untuk analisis business impact!")

if __name__ == "__main__":
    main()
