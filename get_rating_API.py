"""
Script untuk mengambil rating dan range harga (dalam rupiah) dari Google Maps API
Versi sederhana - hanya kolom yang diperlukan
"""

import os
import pandas as pd
import googlemaps
from datetime import datetime
import time
from tqdm import tqdm

def setup_google_maps_api():
    """Setup Google Maps API client"""
    try:
        # API key untuk Google Maps
        api_key = "AIzaSyAMu_PiVlP52Z99Vzzx2umpW4lASFGCYeU"
        
        gmaps = googlemaps.Client(key=api_key)
        print("✅ Google Maps API client berhasil diinisialisasi")
        return gmaps
        
    except Exception as e:
        print(f"❌ Error setting up Google Maps API: {e}")
        return None

def search_place_details(gmaps, business_name, address, verbose=False):
    """
    Mencari detail tempat dari Google Maps API
    Returns: dict dengan place_id, rating, price_range_rupiah, business_status
    """
    
    if not gmaps:
        return {
            'place_id': None,
            'google_rating': None,
            'price_range_rupiah': None,
            'business_status': None,
            'status': 'Error'
        }
    
    try:
        # Clean dan format query pencarian
        business_name = str(business_name).strip()
        address = str(address).strip()
        
        # Variasi query pencarian untuk meningkatkan akurasi
        search_queries = [
            f"{business_name}, {address}, Bandung",
            f"{business_name}, {address}",
            f"{business_name}, Bandung",
            business_name
        ]
        
        if verbose:
            print(f"🔍 Mencari detail untuk: {business_name}")
            print(f"📍 Alamat: {address}")
        
        # Coba setiap query sampai dapat hasil
        for i, query in enumerate(search_queries):
            try:
                if verbose:
                    print(f"   Query {i+1}: {query}")
                
                # Places Text Search untuk mendapatkan place_id
                places_result = gmaps.places(query=query)
                
                if places_result['results']:
                    # Ambil result pertama yang paling relevan
                    place = places_result['results'][0]
                    place_id = place['place_id']
                    
                    # Gunakan Place Details untuk mendapatkan informasi lengkap
                    details = gmaps.place(
                        place_id=place_id,
                        fields=['place_id', 'rating', 'price_level', 'business_status']
                    )
                    
                    if details['result']:
                        result = details['result']
                        
                        # Extract data yang dibutuhkan
                        rating = result.get('rating', None)
                        price_level = result.get('price_level', None)
                        business_status = result.get('business_status', 'UNKNOWN')
                        
                        # Konversi price_level ke range harga rupiah berdasarkan standar Google Maps Indonesia
                        price_range_rupiah = None
                        if price_level is not None:
                            price_ranges_rupiah = {
                                1: "Rp 15.000 - 50.000",      # Murah
                                2: "Rp 50.000 - 100.000",    # Sedang  
                                3: "Rp 100.000 - 200.000",   # Mahal
                                4: "Rp 200.000+"             # Sangat Mahal
                            }
                            price_range_rupiah = price_ranges_rupiah.get(price_level, None)
                        
                        if verbose:
                            print(f"   ✅ Ditemukan: Tempat berhasil ditemukan")
                            print(f"   ⭐ Rating: {rating}")
                            if price_range_rupiah:
                                print(f"   💵 Range Harga: {price_range_rupiah}")
                            print(f"   🏪 Status: {business_status}")
                        
                        return {
                            'place_id': place_id,
                            'google_rating': rating,
                            'price_range_rupiah': price_range_rupiah,
                            'business_status': business_status,
                            'status': 'Success'
                        }
                
                # Delay antar query
                time.sleep(0.1)
                
            except Exception as query_error:
                if verbose:
                    print(f"   ❌ Error pada query {i+1}: {query_error}")
                continue
        
        # Jika semua query gagal
        if verbose:
            print(f"   ⚠️ Tidak ditemukan detail untuk {business_name}")
        
        return {
            'place_id': None,
            'google_rating': None,
            'price_range_rupiah': None,
            'business_status': None,
            'status': 'Not Found'
        }
        
    except Exception as e:
        if verbose:
            print(f"   ❌ Error umum: {e}")
        
        return {
            'place_id': None,
            'google_rating': None,
            'price_range_rupiah': None,
            'business_status': None,
            'status': 'Error'
        }

def main():
    """Fungsi utama untuk mengambil rating dan price_level"""
    
    import sys
    
    print("="*80)
    print("⭐ SCRIPT PENGAMBILAN RATING & RANGE HARGA RUPIAH - GOOGLE MAPS")
    print("="*80)
    
    # Tentukan file input
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = './datasets/full_restaurant_dataset.csv'
    
    # Load dataset utama
    print(f"\n📂 Membaca dataset: {input_file}...")
    try:
        df = pd.read_csv(input_file)
        print(f"✅ Dataset berhasil dimuat: {len(df)} records")
        print(f"📊 Kolom yang tersedia: {list(df.columns)}")
    except Exception as e:
        print(f"❌ Error membaca dataset: {e}")
        return
    
    # Karena file input sudah hanya berisi restoran, gunakan semua data
    df_business = df.copy()
    print(f"🏪 Data restoran untuk diproses: {len(df_business)} records")
    
    # Setup Google Maps API
    print(f"\n🔧 Setup Google Maps API...")
    gmaps = setup_google_maps_api()
    
    if not gmaps:
        print("❌ Tidak dapat melanjutkan tanpa Google Maps API")
        return
    
    # PRODUCTION MODE: Proses semua data restoran
    print(f"\n� PRODUCTION MODE: Memproses semua {len(df_business)} data restoran...")
    df_test = df_business.copy()
    
    # Estimasi biaya untuk Places API
    estimated_requests = len(df_test) * 2  # Search + Details
    estimated_cost = (estimated_requests / 1000) * 34
    
    print(f"💰 Estimasi untuk {len(df_test)} restoran:")
    print(f"   📊 Total API calls: ~{estimated_requests} (Search + Details)")
    print(f"   💰 Estimasi biaya: ${estimated_cost:.2f}")
    print(f"   ⏱️  Estimasi waktu: ~{len(df_test) * 0.5 / 60:.1f} menit")
    
    # Konfirmasi untuk melanjutkan
    proceed = input(f"\n🚀 Lanjutkan dengan proses full dataset? (y/n): ")
    if proceed.lower() != 'y':
        print("❌ Proses dibatalkan")
        return
    
    # Inisialisasi kolom hasil (hanya kolom yang diperlukan)
    df_test['place_id'] = None
    df_test['google_rating'] = None
    df_test['price_range_rupiah'] = None
    df_test['business_status'] = None
    df_test['processed_at'] = None
    
    print(f"\n🚀 Memulai pengambilan rating dan range harga untuk {len(df_test)} bisnis...")
    print("-" * 80)
    
    # Progress tracking
    success_count = 0
    error_count = 0
    not_found_count = 0
    
    # Proses setiap bisnis dengan progress bar
    start_time = time.time()
    
    for index, row in tqdm(df_test.iterrows(), total=len(df_test), desc="⭐ Mengambil rating & range harga"):
        
        # Debug untuk beberapa record pertama
        verbose_mode = index < 5  # Verbose untuk 5 record pertama
        
        if verbose_mode:
            print(f"\n[{index+1}/{len(df_test)}] Processing: {row['nama']}")
        
        # Panggil fungsi pencarian detail
        result = search_place_details(
            gmaps, 
            row['nama'], 
            row['alamat'], 
            verbose=verbose_mode
        )
        
        # Update dataframe dengan hasil (hanya kolom yang diperlukan)
        df_test.at[index, 'place_id'] = result['place_id']
        df_test.at[index, 'google_rating'] = result['google_rating']
        df_test.at[index, 'price_range_rupiah'] = result['price_range_rupiah']
        df_test.at[index, 'business_status'] = result['business_status']
        df_test.at[index, 'processed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Count status
        if result['status'] == 'Success':
            success_count += 1
        elif result['status'] == 'Not Found':
            not_found_count += 1
        else:
            error_count += 1
        
        # Delay untuk rate limiting
        time.sleep(0.5)  # 500ms delay untuk menghormati API limits
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "="*80)
    print("📊 HASIL PENGAMBILAN RATING & RANGE HARGA RUPIAH")
    print("="*80)
    
    success_rate = success_count / len(df_test) * 100
    print(f"✅ Berhasil ditemukan : {success_count}/{len(df_test)} ({success_rate:.1f}%)")
    print(f"⚠️  Tidak ditemukan   : {not_found_count}/{len(df_test)} ({not_found_count/len(df_test)*100:.1f}%)")
    print(f"❌ Error             : {error_count}/{len(df_test)} ({error_count/len(df_test)*100:.1f}%)")
    print(f"⏱️  Waktu total       : {total_time:.1f} detik ({total_time/60:.1f} menit)")
    print(f"📈 Rate processing   : {len(df_test)/total_time:.1f} records/detik")
    
    # Simpan hasil dengan nama yang sesuai input file
    import os
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = f'./datasets/{base_name}_with_google_rupiah.csv'
    df_test.to_csv(output_file, index=False)
    print(f"\n💾 Hasil processing disimpan ke: {output_file}")
    
    print("\n🏁 Full processing selesai!")
    print(f"📊 Untuk analisis lengkap, lihat file: {output_file}")

if __name__ == "__main__":
    main()
