#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Aplikasi Prediksi Kelayakan Lokasi Usaha F&B di Bandung
Streamlit web application untuk memprediksi kesuksesan bisnis F&B berdasarkan lokasi strategis.
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os
import warnings
from pathlib import Path

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Konfigurasi halaman
st.set_page_config(
    page_title="Prediksi Kelayakan Usaha F&B Bandung",
    layout="wide"
)

@st.cache_resource
def load_assets():
    """
    Memuat semua aset yang diperlukan untuk prediksi.
    Menggunakan cache untuk menghindari pemuatan berulang.
    """
    try:
        # Path ke direktori model
        model_dir = Path("models/competition")
        
        # Memuat model
        model = joblib.load(model_dir / "final_competition_model.pkl")
        
        # Memuat scaler
        scaler = joblib.load(model_dir / "competition_scaler.pkl")
        
        # Memuat label encoders
        le_kategori = joblib.load(model_dir / "label_encoder_kategori.pkl")
        le_target = joblib.load(model_dir / "label_encoder_target.pkl")
        
        # Memuat feature names - dengan mapping manual untuk menghindari masalah encoding
        feature_names = [
            'Jumlah Penduduk',
            'Luas Wilayah (km²)',
            'Kepadatan (jiwa/km²)',
            'jumlah_mall',
            'jumlah_minimarket',
            'jumlah_taman',
            'jumlah_ulasan',
            'google_rating',
            'mall_per_capita',
            'minimarket_density',
            'taman_per_capita',
            'ulasan_per_capita',
            'competition_density',
            'market_potential',
            'infrastructure_score',
            'retail_accessibility',
            'rating_normalized',
            'log_jumlah_ulasan',
            'log_kepadatan',
            'kategori_resto_encoded',
            'price_range_encoded',
            'high_rating',
            'excellent_rating',
            'high_volume_reviews',
            'very_high_volume_reviews',
            'price_category_interaction',
            'rating_review_interaction',
            'density_infrastructure'
        ]
        
        # Fix encoding issues with special characters
        feature_names = [name.replace('km�', 'km²').replace('jiwa/km�', 'jiwa/km²') for name in feature_names]
        
        # Memuat target mapping
        with open(model_dir / "target_mapping.json", 'r', encoding='utf-8') as f:
            target_mapping = json.load(f)
        
        # Memuat data kecamatan
        with open("bandung_kecamatan_data.json", 'r', encoding='utf-8') as f:
            kecamatan_data = json.load(f)
        
        # Konversi ke DataFrame
        df_kecamatan = pd.DataFrame(kecamatan_data)
        
        return {
            'model': model,
            'scaler': scaler,
            'le_kategori': le_kategori,
            'le_target': le_target,
            'feature_names': feature_names,
            'target_mapping': target_mapping,
            'df_kecamatan': df_kecamatan
        }
    
    except Exception as e:
        st.error(f"Error memuat aset: {str(e)}")
        st.stop()

def validate_business_logic(target_ulasan, target_rating, kecamatan_data):
    """
    Validasi logika bisnis berdasarkan analisis data real dari dataset.
    Data menunjukkan:
    - Rating rata-rata: 4.51
    - Ulasan rata-rata: 517, median: 202
    - Bisnis dengan rating ≥4.8: rata-rata hanya 79 ulasan, maksimal 200 ulasan
    - P95 ulasan: 2,819
    - P99 ulasan: 5,025
    """
    warnings = []
    errors = []
    
    jumlah_penduduk = kecamatan_data['Jumlah Penduduk']
    
    # Validasi berdasarkan data real: Rating vs Ulasan
    if target_rating >= 4.8:
        # Berdasarkan data, bisnis rating ≥4.8 rata-rata hanya 79 ulasan, max 200
        if target_ulasan > 200:
            errors.append(f"Rating {target_rating} dengan {target_ulasan:,} ulasan sangat tidak realistis. "
                         f"Dari dataset real, bisnis dengan rating ≥4.8 maksimal hanya 200 ulasan (rata-rata 79).")
        elif target_ulasan > 100:
            warnings.append(f"Rating {target_rating} dengan {target_ulasan} ulasan cukup optimis. "
                           f"Bisnis rating tinggi dalam dataset rata-rata hanya 79 ulasan.")
    
    elif target_rating >= 4.5:
        # Rating tinggi tapi tidak ekstrem
        if target_ulasan > 1000:
            warnings.append(f"Rating {target_rating} dengan {target_ulasan:,} ulasan memerlukan kualitas sangat konsisten.")
        elif target_ulasan > 500:
            warnings.append(f"Mempertahankan rating {target_rating} dengan {target_ulasan} ulasan butuh manajemen kualitas ketat.")
    
    # Validasi jumlah ulasan berdasarkan persentil dataset
    if target_ulasan > 5000:  # P99: 5,025
        errors.append(f"Target {target_ulasan:,} ulasan melebihi 99% bisnis terbaik di dataset (maksimal realistis: ~5,000 ulasan).")
    elif target_ulasan > 2800:  # P95: 2,819
        warnings.append(f"Target {target_ulasan:,} ulasan sangat tinggi - hanya 5% bisnis terbaik yang mencapainya.")
    elif target_ulasan > 950:  # P90: 958
        warnings.append(f"Target {target_ulasan:,} ulasan tinggi - perlu strategi marketing dan kualitas konsisten.")
    
    # Validasi berdasarkan populasi
    review_percentage = (target_ulasan / jumlah_penduduk) * 100
    if review_percentage > 3:  # Lebih ketat dari sebelumnya
        errors.append(f"Target ulasan ({target_ulasan:,}) tidak realistis untuk populasi {jumlah_penduduk:,.0f} orang "
                     f"({review_percentage:.1f}% populasi). Maksimal realistis: ~{int(jumlah_penduduk * 0.03):,} ulasan.")
    elif review_percentage > 1:
        warnings.append(f"Target {review_percentage:.1f}% populasi memberi ulasan cukup optimis.")
    
    # Validasi rating yang terlalu rendah
    if target_rating < 3.0:
        errors.append(f"Rating {target_rating} terlalu rendah untuk bisnis yang viable. "
                     f"Minimal target rating 3.0 untuk bisnis yang sustainable.")
    elif target_rating < 3.5:
        warnings.append(f"Rating {target_rating} di bawah rata-rata market (4.51). Pertimbangkan target yang lebih tinggi.")
    
    # Validasi kombinasi rating rendah dengan ulasan tinggi
    if target_rating < 4.0 and target_ulasan > 500:
        warnings.append(f"Rating {target_rating} dengan {target_ulasan} ulasan menunjukkan masalah kualitas yang serius.")
    
    return warnings, errors

def create_feature_engineered_data(input_data, kecamatan_data):
    """
    Melakukan feature engineering pada data input.
    """
    # Gabungkan data input dengan data kecamatan
    combined_data = {**kecamatan_data, **input_data}
    
    # Basic features
    data = {
        'Jumlah Penduduk': combined_data['Jumlah Penduduk'],
        'Luas Wilayah (km²)': combined_data['Luas Wilayah (km²)'],
        'Kepadatan (jiwa/km²)': combined_data['Kepadatan (jiwa/km²)'],
        'jumlah_mall': combined_data['jumlah_mall'],
        'jumlah_minimarket': combined_data['jumlah_minimarket'],
        'jumlah_taman': combined_data['jumlah_taman'],
        'jumlah_ulasan': combined_data['jumlah_ulasan'],
        'google_rating': combined_data['google_rating']
    }
    
    # Feature engineering - sama seperti di training
    data['mall_per_capita'] = data['jumlah_mall'] / data['Jumlah Penduduk'] * 1000
    data['minimarket_density'] = data['jumlah_minimarket'] / data['Luas Wilayah (km²)']
    data['taman_per_capita'] = data['jumlah_taman'] / data['Jumlah Penduduk'] * 1000
    data['ulasan_per_capita'] = data['jumlah_ulasan'] / data['Jumlah Penduduk'] * 1000
    
    # Competition dan market metrics
    data['competition_density'] = data['jumlah_ulasan'] / data['Luas Wilayah (km²)']
    data['market_potential'] = data['Kepadatan (jiwa/km²)'] * (data['jumlah_mall'] + data['jumlah_minimarket'])
    data['infrastructure_score'] = data['jumlah_mall'] + data['jumlah_minimarket'] + data['jumlah_taman']
    data['retail_accessibility'] = data['jumlah_mall'] + data['jumlah_minimarket']
    
    # Normalisasi dan log transform
    data['rating_normalized'] = data['google_rating'] / 5.0
    data['log_jumlah_ulasan'] = np.log1p(data['jumlah_ulasan'])
    data['log_kepadatan'] = np.log1p(data['Kepadatan (jiwa/km²)'])
    
    # Encoding categorical
    data['kategori_resto_encoded'] = combined_data['kategori_resto_encoded']
    data['price_range_encoded'] = combined_data['price_range'] - 1  # 1-4 menjadi 0-3
    
    # Binary features
    data['high_rating'] = 1 if data['google_rating'] >= 4.0 else 0
    data['excellent_rating'] = 1 if data['google_rating'] >= 4.5 else 0
    data['high_volume_reviews'] = 1 if data['jumlah_ulasan'] >= 100 else 0
    data['very_high_volume_reviews'] = 1 if data['jumlah_ulasan'] >= 500 else 0
    
    # Interaction features
    data['price_category_interaction'] = data['price_range_encoded'] * data['kategori_resto_encoded']
    data['rating_review_interaction'] = data['rating_normalized'] * data['log_jumlah_ulasan']
    data['density_infrastructure'] = data['log_kepadatan'] * data['infrastructure_score']
    
    return data

def make_prediction(assets, kecamatan_terpilih, kategori_resto, target_rating, target_ulasan, price_range):
    """
    Melakukan prediksi berdasarkan input pengguna dengan validasi logika bisnis.
    """
    # Ambil data kecamatan yang dipilih
    kecamatan_data = assets['df_kecamatan'][
        assets['df_kecamatan']['kecamatan'] == kecamatan_terpilih
    ].iloc[0].to_dict()
    
    # Validasi logika bisnis
    warnings, errors = validate_business_logic(target_ulasan, target_rating, kecamatan_data)
    
    # Jika ada error, return dengan pesan error
    if errors:
        return None, None, None, None, errors, warnings
    
    # Encode kategori restoran
    kategori_encoded = assets['le_kategori'].transform([kategori_resto])[0]
    
    # Siapkan input data
    input_data = {
        'jumlah_ulasan': target_ulasan,
        'google_rating': target_rating,
        'kategori_resto_encoded': kategori_encoded,
        'price_range': price_range
    }
    
    # Lakukan feature engineering
    processed_data = create_feature_engineered_data(input_data, kecamatan_data)
    
    # Buat DataFrame dengan urutan fitur yang sama dengan training
    feature_data = {}
    for feature in assets['feature_names']:
        feature_data[feature] = [processed_data.get(feature, 0)]
    
    X_df = pd.DataFrame(feature_data)
    
    # Scaling
    X_scaled = assets['scaler'].transform(X_df)
    
    # Prediksi
    prediction = assets['model'].predict(X_scaled)[0]
    probabilities = assets['model'].predict_proba(X_scaled)[0]
    
    # Konversi kembali ke label
    target_mapping_inv = {v: k for k, v in assets['target_mapping'].items()}
    predicted_label = target_mapping_inv[prediction]
    
    # Ambil probabilitas tertinggi
    max_prob = np.max(probabilities)
    
    return predicted_label, max_prob, probabilities, target_mapping_inv, [], warnings

def show_overview():
    """Halaman Overview - Penjelasan tentang AI Predictor"""
    
    # Penjelasan umum
    st.header("Tentang Aplikasi")
    st.write("""
    **AI Business Impact Predictor** adalah sistem cerdas yang membantu calon pengusaha Food & Beverage (F&B) 
    untuk mengevaluasi kelayakan lokasi usaha di Kota Bandung berdasarkan data demografis, infrastruktur, 
    dan faktor-faktor strategis lainnya.
    """)
    
    # Bagaimana AI bekerja
    st.header("Bagaimana AI Ini Bekerja?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Analisis Data Multi-Dimensi")
        st.write("""
        - **Data Demografis**: Jumlah penduduk, kepadatan, luas wilayah
        - **Infrastruktur Komersial**: Jumlah mall, minimarket, taman
        - **Profil Bisnis**: Kategori restoran, rentang harga target
        - **Target Performa**: Rating dan jumlah ulasan yang diharapkan
        """)
        
        st.subheader("2. Machine Learning Model")
        st.write("""
        Sistem menggunakan **Ensemble Learning** yang menggabungkan:
        - Random Forest Classifier
        - XGBoost Classifier  
        - Decision Tree Classifier
        - Voting mechanism untuk prediksi final
        """)
    
    with col2:
        st.subheader("3. Feature Engineering")
        st.write("""
        AI melakukan rekayasa fitur otomatis:
        - Mall per capita
        - Kepadatan minimarket
        - Potensi pasar (density × infrastructure)
        - Skor aksesibilitas retail
        - Normalisasi dan transformasi logaritmik
        """)
        
        st.subheader("4. Validasi Logika Bisnis")
        st.write("""
        Sistem memvalidasi input berdasarkan data real:
        - Rating vs volume ulasan yang realistis
        - Persentase penetrasi pasar yang wajar
        - Konsistensi kategori bisnis dengan ekspektasi
        """)
    
    # Manfaat dan tujuan
    st.header("Manfaat dan Tujuan")
    
    benefit_col1, benefit_col2, benefit_col3 = st.columns(3)
    
    with benefit_col1:
        st.subheader("Mitigasi Risiko")
        st.write("""
        - Mengurangi risiko investasi yang salah
        - Identifikasi lokasi dengan potensi rendah
        - Peringatan dini untuk target yang tidak realistis
        """)
    
    with benefit_col2:
        st.subheader("Optimasi Keputusan")
        st.write("""
        - Rekomendasi berbasis data objektif
        - Analisis komprehensif faktor lokasi
        - Prediksi tingkat kepercayaan tinggi
        """)
    
    with benefit_col3:
        st.subheader("Efisiensi Waktu")
        st.write("""
        - Analisis instan tanpa riset manual
        - Perbandingan cepat antar lokasi
        - Basis untuk keputusan strategis
        """)
    
    # Metodologi
    st.header("Metodologi dan Data")
    st.write("""
    **Dataset Training**: 5,115 bisnis F&B di Bandung dengan data real dari Google Maps dan statistik pemerintah
    
    **Akurasi Model**: Sistem telah divalidasi dengan cross-validation dan mencapai performa yang reliable
    
    **Update Berkala**: Model dilatih ulang secara periodik untuk mempertahankan akurasi prediksi
    """)
    
    # Disclaimer
    st.header("Catatan Penting")
    st.info("""
    **Disclaimer**: Prediksi ini adalah alat bantu pengambilan keputusan berdasarkan analisis data historis. 
    Keputusan investasi final tetap memerlukan pertimbangan faktor lain seperti modal, strategi pemasaran, 
    kualitas produk, dan kondisi pasar terkini. Gunakan hasil prediksi sebagai salah satu referensi dalam 
    analisis kelayakan bisnis yang komprehensif.
    """)

def show_prediction():
    """Halaman Prediksi - Form input dan hasil analisis"""
    st.subheader("Analisis Potensi Kesuksesan Bisnis Food & Beverage Berdasarkan Lokasi Strategis")
    
    # Memuat aset
    assets = load_assets()
    
    # BAGIAN 1: INPUT DETAIL USAHA
    st.header("Masukkan Detail Usaha")
    
    # Layout input dalam 2 kolom
    input_col1, input_col2 = st.columns(2)
    
    with input_col1:
        # Input kecamatan
        kecamatan_options = sorted(assets['df_kecamatan']['kecamatan'].unique())
        kecamatan_terpilih = st.selectbox(
            "Pilih Kecamatan:",
            kecamatan_options,
            index=0
        )
        
        # Input kategori restoran
        kategori_options = list(assets['le_kategori'].classes_)
        kategori_resto = st.selectbox(
            "Kategori Restoran:",
            kategori_options,
            index=0
        )
        
        # Input price range
        price_range = st.selectbox(
            "Rentang Harga:",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Rp 15.000 - 50.000",
                2: "Rp 50.000 - 100.000", 
                3: "Rp 100.000 - 200.000",
                4: "Rp 200.000 - 500.000"
            }[x],
            index=2
        )
    
    with input_col2:
        # Input target rating
        target_rating = st.number_input(
            "Target Google Rating:",
            min_value=1.0,
            max_value=5.0,
            value=4.2,
            step=0.1,
            format="%.1f",
            help="Berdasarkan data real: Rating rata-rata 4.51. Realistis: 4.0-4.5 (Baik), 4.5-4.7 (Sangat Baik), >4.8 (Extremely Rare - hanya dengan ulasan sedikit)"
        )
        
        # Input target jumlah ulasan  
        target_ulasan = st.number_input(
            "Target Jumlah Ulasan:",
            min_value=0,
            value=100,
            step=10,
            help="Berdasarkan data real: Rata-rata 517 ulasan. Realistis: 50-500 (Normal), 500-1000 (Tinggi), >1000 (Sangat Tinggi). Rating tinggi (≥4.8) biasanya <200 ulasan."
        )
    
    # Tombol prediksi (full width)
    st.markdown("---")
    if st.button("Lakukan Prediksi", type="primary", use_container_width=True):
        # Lakukan prediksi
        predicted_label, max_prob, probabilities, target_mapping_inv, errors, warnings = make_prediction(
            assets, kecamatan_terpilih, kategori_resto, target_rating, target_ulasan, price_range
        )
        
        # Tampilkan error jika ada
        if errors:
            for error in errors:
                st.error(f"Error: {error}")
            st.warning("Silakan perbaiki input Anda dan coba lagi.")
        else:
            # Tampilkan warning jika ada
            if warnings:
                st.warning("Peringatan:")
                for warning in warnings:
                    st.warning(f"- {warning}")
            
            # Simpan hasil dalam session state
            st.session_state['prediction_made'] = True
            st.session_state['predicted_label'] = predicted_label
            st.session_state['max_prob'] = max_prob
            st.session_state['probabilities'] = probabilities
            st.session_state['target_mapping_inv'] = target_mapping_inv
            st.session_state['kecamatan_terpilih'] = kecamatan_terpilih
            st.session_state['warnings'] = warnings
    
    # BAGIAN 2: INFORMASI KECAMATAN
    st.markdown("---")
    st.header("Informasi Kecamatan")
    
    if kecamatan_terpilih:
        kecamatan_info = assets['df_kecamatan'][
            assets['df_kecamatan']['kecamatan'] == kecamatan_terpilih
        ].iloc[0]
        
        st.subheader(f"Kecamatan {kecamatan_terpilih.title()}")
        
        # Tampilkan metrics dalam 3 kolom
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            st.metric("Jumlah Penduduk", f"{kecamatan_info['Jumlah Penduduk']:,.0f}")
            st.metric("Jumlah Mall", f"{kecamatan_info['jumlah_mall']:.0f}")
        
        with info_col2:
            st.metric("Luas Wilayah", f"{kecamatan_info['Luas Wilayah (km²)']:.2f} km²")
            st.metric("Jumlah Minimarket", f"{kecamatan_info['jumlah_minimarket']:.0f}")
        
        with info_col3:
            st.metric("Kepadatan Penduduk", f"{kecamatan_info['Kepadatan (jiwa/km²)']:,.0f} jiwa/km²")
            st.metric("Jumlah Taman", f"{kecamatan_info['jumlah_taman']:.0f}")
    
    # BAGIAN 3: HASIL ANALISIS
    if st.session_state.get('prediction_made', False):
        st.markdown("---")
        st.header("Hasil Analisis")
        
        predicted_label = st.session_state['predicted_label']
        max_prob = st.session_state['max_prob']
        probabilities = st.session_state['probabilities']
        target_mapping_inv = st.session_state['target_mapping_inv']
        
        # Tampilkan rekomendasi utama dalam card besar
        result_col1, result_col2 = st.columns([2, 1])
        
        with result_col1:
            # Tampilkan rekomendasi dengan warna sesuai
            if predicted_label == "Go":
                st.success("**REKOMENDASI: GO**")
                st.success("Lokasi sangat direkomendasikan untuk bisnis F&B")
                explanation = "Lokasi ini memiliki potensi tinggi untuk kesuksesan bisnis F&B berdasarkan analisis data demografis dan infrastruktur."
            elif predicted_label == "Consider":
                st.warning("**REKOMENDASI: CONSIDER**")
                st.warning("Pertimbangkan dengan hati-hati")
                explanation = "Lokasi ini memiliki potensi sedang. Perlu analisis lebih mendalam dan strategi bisnis yang tepat."
            else:  # Avoid
                st.error("**REKOMENDASI: AVOID**")
                st.error("Tidak direkomendasikan")
                explanation = "Lokasi ini memiliki risiko tinggi untuk kegagalan bisnis berdasarkan analisis data yang ada."
            
            st.info(f"**Penjelasan:** {explanation}")
        
        with result_col2:
            # Tampilkan tingkat kepercayaan
            st.metric("Tingkat Kepercayaan", f"{max_prob:.1%}", help="Seberapa yakin model dengan prediksi ini")
        
        # Tampilkan detail probabilitas
        st.subheader("Detail Probabilitas")
        prob_col1, prob_col2, prob_col3 = st.columns(3)
        
        class_names = [target_mapping_inv[i] for i in range(len(probabilities))]
        
        for i, (class_name, prob) in enumerate(zip(class_names, probabilities)):
            if i == 0:
                with prob_col1:
                    st.metric(f"{class_name}", f"{prob:.1%}")
            elif i == 1:
                with prob_col2:
                    st.metric(f"{class_name}", f"{prob:.1%}")
            else:
                with prob_col3:
                    st.metric(f"{class_name}", f"{prob:.1%}")
        
        # Tampilkan warning jika ada
        if st.session_state.get('warnings'):
            st.markdown("---")
            st.warning("**Catatan Penting:**")
            for warning in st.session_state['warnings']:
                st.warning(f"- {warning}")

def main():
    """Fungsi utama dengan navigasi"""
    
    # Header utama
    st.title("AI Business Impact Predictor")
    
    # Navbar horizontal menggunakan tabs
    tab1, tab2 = st.tabs(["Overview", "Predict"])
    
    with tab1:
        show_overview()
    
    with tab2:
        show_prediction()

if __name__ == "__main__":
    main()