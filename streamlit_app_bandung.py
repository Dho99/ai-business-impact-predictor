#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FnB Business Success Predictor - Bandung Specific

Aplikasi web untuk prediksi sukses bisnis FnB di Kota Bandung berdasarkan 
analisis kecamatan dan faktor strategis lainnya menggunakan AI model.
"""

import os
import sys
import json
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from bandung_data import get_bandung_kecamatan_data, get_kecamatan_options, get_kecamatan_info

# Check for required packages
try:
    import joblib
    import numpy as np
    from pathlib import Path
    # Explicitly import model packages that are required
    import xgboost as xgb
    import lightgbm as lgb
except ImportError as e:
    st.error(f"❌ Missing required package: {str(e)}")
    st.error("Please install the missing package using: pip install -r requirements.txt")
    st.stop()

# Configuration
COMPETITION_DIR = os.path.join(os.path.dirname(__file__), 'models', 'competition')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

# Ensure results directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)

# Page configuration
st.set_page_config(
    page_title="Prediksi Sukses Bisnis FnB - Kota Bandung",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .prediction-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .danger-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .kecamatan-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .metric-card {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model_and_components():
    """Load the trained model and all necessary components for prediction."""
    try:
        # Verify competition directory exists
        if not os.path.exists(COMPETITION_DIR):
            st.error(f"Competition directory not found: {COMPETITION_DIR}")
            st.stop()
        
        # Load model
        model_path = os.path.join(COMPETITION_DIR, 'final_competition_model.pkl')
        if not os.path.exists(model_path):
            st.error(f"Model file not found: {model_path}")
            st.stop()
        model = joblib.load(model_path)

        # Load scaler
        scaler_path = os.path.join(COMPETITION_DIR, 'competition_scaler.pkl')
        if not os.path.exists(scaler_path):
            st.error(f"Scaler file not found: {scaler_path}")
            st.stop()
        scaler = joblib.load(scaler_path)

        # Load feature names
        feature_names_path = os.path.join(COMPETITION_DIR, 'feature_names_competition.txt')
        if not os.path.exists(feature_names_path):
            st.error(f"Feature names file not found: {feature_names_path}")
            st.stop()
        with open(feature_names_path, 'r') as f:
            feature_names = [line.strip() for line in f.readlines()]

        # Load category label encoder
        label_encoder_kategori_path = os.path.join(COMPETITION_DIR, 'label_encoder_kategori.pkl')
        if not os.path.exists(label_encoder_kategori_path):
            st.error(f"Category label encoder file not found: {label_encoder_kategori_path}")
            st.stop()
        label_encoder_kategori = joblib.load(label_encoder_kategori_path)

        # Load target label encoder
        target_encoder_path = os.path.join(COMPETITION_DIR, 'label_encoder_target.pkl')
        if not os.path.exists(target_encoder_path):
            st.error(f"Target label encoder file not found: {target_encoder_path}")
            st.stop()
        le_target = joblib.load(target_encoder_path)

        # Load target mapping
        target_mapping_path = os.path.join(COMPETITION_DIR, 'target_mapping.json')
        if not os.path.exists(target_mapping_path):
            st.error(f"Target mapping file not found: {target_mapping_path}")
            st.stop()
        with open(target_mapping_path, 'r') as f:
            target_mapping = json.load(f)

        return {
            'model': model,
            'scaler': scaler,
            'feature_names': feature_names,
            'label_encoder_kategori': label_encoder_kategori,
            'le_target': le_target,
            'target_mapping': target_mapping
        }
    except Exception as e:
        st.error(f"❌ Error loading model components: {str(e)}")
        st.error("This might be due to incompatible model files or corrupt data.")
        st.stop()

def preprocess_data(data, components):
    """Preprocess input data to match the model's expected features."""
    # Create derived features
    data['mall_per_capita'] = data['jumlah_mall'] / data['Jumlah Penduduk'] * 1000  # per 1000 residents
    data['minimarket_density'] = data['jumlah_minimarket'] / data['Luas Wilayah (km²)']
    data['taman_per_capita'] = data['jumlah_taman'] / data['Jumlah Penduduk'] * 1000  # per 1000 residents
    data['ulasan_per_capita'] = data['jumlah_ulasan'] / data['Jumlah Penduduk'] * 1000  # per 1000 residents
    
    # Competition and market metrics - CORRECTED FORMULAS FROM TRAINING
    data['competition_density'] = data['jumlah_ulasan'] / data['Luas Wilayah (km²)']
    data['market_potential'] = data['Kepadatan (jiwa/km²)'] * (data['jumlah_mall'] + data['jumlah_minimarket'])
    data['infrastructure_score'] = data['jumlah_mall'] + data['jumlah_minimarket'] + data['jumlah_taman']
    data['retail_accessibility'] = data['jumlah_mall'] + data['jumlah_minimarket']
    
    # Normalize and log transform features
    data['rating_normalized'] = data['google_rating'] / 5.0
    data['log_jumlah_ulasan'] = np.log1p(data['jumlah_ulasan'])
    data['log_kepadatan'] = np.log1p(data['Kepadatan (jiwa/km²)'])
    
    # Encode categorical variables
    data['kategori_resto_encoded'] = components['label_encoder_kategori'].transform([data['kategori_resto']])[0]
    data['price_range_encoded'] = data['price_range'] - 1  # Assuming 1-4 range becomes 0-3
    
    # Binary features
    data['high_rating'] = 1 if data['google_rating'] >= 4.0 else 0
    data['excellent_rating'] = 1 if data['google_rating'] >= 4.5 else 0
    data['high_volume_reviews'] = 1 if data['jumlah_ulasan'] >= 100 else 0
    data['very_high_volume_reviews'] = 1 if data['jumlah_ulasan'] >= 500 else 0
    
    # Interaction features
    data['price_category_interaction'] = data['price_range_encoded'] * data['kategori_resto_encoded']
    data['rating_review_interaction'] = data['rating_normalized'] * data['log_jumlah_ulasan']
    data['density_infrastructure'] = data['log_kepadatan'] * data['infrastructure_score']
    
    # Create feature vector in correct order
    X = []
    for feature in components['feature_names']:
        X.append(data.get(feature, 0))  # Default to 0 if feature is missing
    
    # Scale features
    X_scaled = components['scaler'].transform([X])
    
    return X_scaled

def create_prediction_visualization(probas, class_names, predicted_class):
    """Create interactive prediction visualization using Plotly."""
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=class_names,
            y=probas,
            text=[f'{p:.1%}' for p in probas],
            textposition='auto',
            marker_color=['#ff4444' if cls == 'Avoid' else '#ffaa00' if cls == 'Consider' else '#44ff44' 
                         for cls in class_names]
        )
    ])
    
    fig.update_layout(
        title={
            'text': 'Prediksi Sukses Bisnis FnB di Bandung',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="Potensi Bisnis",
        yaxis_title="Probabilitas",
        yaxis=dict(range=[0, 1], tickformat='.0%'),
        height=400,
        showlegend=False
    )
    
    return fig

def display_kecamatan_info(kecamatan_data):
    """Display kecamatan information in a nice card format."""
    st.markdown(f"""
    <div class="kecamatan-card">
        <h4>📍 Profil Kecamatan {kecamatan_data['name']}</h4>
        <p><strong>Deskripsi:</strong> {kecamatan_data['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("👥 Populasi", f"{kecamatan_data['population']:,} jiwa")
        st.metric("📐 Luas Area", f"{kecamatan_data['area_km2']} km²")
    
    with col2:
        st.metric("🏘️ Kepadatan", f"{kecamatan_data['density']:,} jiwa/km²")
        st.metric("🏬 Mall", f"{kecamatan_data['malls']:.0f} unit")
    
    with col3:
        st.metric("🏪 Minimarket", f"{kecamatan_data['minimarkets']:.0f} unit")
        st.metric("🌳 Taman", f"{kecamatan_data['parks']:.0f} unit")

def create_bandung_map_visualization(selected_kecamatan, kecamatan_data):
    """Create a simple visualization showing selected kecamatan position."""
    # Create a simple bar chart showing key metrics for the selected kecamatan
    metrics = ['Kepadatan', 'Mall', 'Minimarket', 'Taman']
    values = [
        kecamatan_data['density'] / 1000,  # Scale density for visualization
        kecamatan_data['malls'],
        kecamatan_data['minimarkets'] / 10,  # Scale minimarkets
        kecamatan_data['parks'] / 10  # Scale parks
    ]
    
    fig = go.Figure(data=[
        go.Bar(
            x=metrics,
            y=values,
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
            text=[f"{v:.1f}" for v in values],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title=f"Profil Infrastruktur - {kecamatan_data['name']}",
        xaxis_title="Aspek",
        yaxis_title="Skala Relatif",
        height=300,
        showlegend=False
    )
    
    return fig

def main():
    """Main Streamlit application."""
    # Header
    st.markdown('<h1 class="main-header">🏙️ Prediksi Sukses Bisnis FnB Kota Bandung</h1>', unsafe_allow_html=True)
    st.markdown("**Prediksi potensi sukses bisnis makanan & minuman berdasarkan analisis kecamatan dan faktor strategis di Kota Bandung**")
    
    # Load model components
    with st.spinner("Memuat AI models..."):
        components = load_model_and_components()
    
    st.success("✅ AI models berhasil dimuat!")
    
    # Sidebar for inputs
    st.sidebar.markdown("## 🏙️ Informasi Bisnis Bandung")
    
    # Kecamatan Selection
    st.sidebar.markdown("### 📍 Pilih Kecamatan")
    kecamatan_options = get_kecamatan_options()
    
    # Default kecamatan
    default_kecamatan = getattr(st.session_state, 'selected_kecamatan', 'sumur_bandung')
    default_index = next((i for i, (key, _) in enumerate(kecamatan_options) if key == default_kecamatan), 0)
    
    selected_kecamatan_tuple = st.sidebar.selectbox(
        "Kecamatan di Bandung",
        kecamatan_options,
        index=default_index,
        format_func=lambda x: x[1],
        help="Pilih kecamatan tempat usaha akan didirikan"
    )
    
    selected_kecamatan = selected_kecamatan_tuple[0]
    kecamatan_data = get_kecamatan_info(selected_kecamatan)
    
    # Store in session state
    st.session_state.selected_kecamatan = selected_kecamatan
    
    # Business info section
    st.sidebar.markdown("### 🍽️ Informasi Bisnis")
    kategori_options = list(components['label_encoder_kategori'].classes_)
    
    # Get default category
    default_kategori = getattr(st.session_state, 'kategori_resto', 'Restaurant')
    default_kategori_index = kategori_options.index(default_kategori) if default_kategori in kategori_options else 0
    
    kategori_resto = st.sidebar.selectbox(
        "Kategori Restoran", 
        kategori_options,
        index=default_kategori_index,
        help="Jenis usaha FnB yang akan dibuka"
    )
    
    # Price range
    default_price = getattr(st.session_state, 'price_range', 2)
    price_range_options = [1, 2, 3, 4]
    default_price_index = price_range_options.index(default_price) if default_price in price_range_options else 1
    
    price_range = st.sidebar.selectbox(
        "Kisaran Harga", 
        price_range_options,
        index=default_price_index,
        format_func=lambda x: {
            1: "$ - Ekonomis (< Rp 50.000)",
            2: "$$ - Menengah (Rp 50.000 - 100.000)", 
            3: "$$$ - Premium (Rp 100.000 - 200.000)",
            4: "$$$$ - Mewah (> Rp 200.000)"
        }[x],
        help="Tingkat harga target bisnis"
    )
    
    # Market expectations
    st.sidebar.markdown("### 📊 Analisis Kompetisi & Target")
    
    # Competition analysis berdasarkan kecamatan 
    kecamatan_competition_level = {
        'sumur_bandung': 'Sangat Tinggi', 'coblong': 'Tinggi', 'cibeunying_kidul': 'Tinggi',
        'bandung_wetan': 'Sangat Tinggi', 'lengkong': 'Tinggi', 'cicendo': 'Sedang-Tinggi',
        'sukajadi': 'Tinggi', 'astanaanyar': 'Sedang', 'bojongloa_kaler': 'Sedang',
        'buahbatu': 'Sedang', 'antapani': 'Sedang-Rendah', 'arcamanik': 'Rendah'
    }
    
    competition_level = kecamatan_competition_level.get(selected_kecamatan, 'Sedang')
    
    # Display competition warning
    if competition_level == 'Sangat Tinggi':
        st.sidebar.warning(f"🏙️ **Kompetisi: {competition_level}**\n\nArea ini sangat kompetitif! Butuh strategi diferensiasi kuat.")
    elif competition_level == 'Tinggi':
        st.sidebar.info(f"🏢 **Kompetisi: {competition_level}**\n\nArea cukup kompetitif, perlu riset mendalam.")
    else:
        st.sidebar.success(f"🌱 **Kompetisi: {competition_level}**\n\nArea dengan peluang lebih terbuka.")
    
    # Realistic review expectations based on competition level
    competition_reviews = {
        'Sangat Tinggi': {'min': 500, 'recommended': 800, 'max': 1500},
        'Tinggi': {'min': 200, 'recommended': 400, 'max': 800},
        'Sedang-Tinggi': {'min': 150, 'recommended': 300, 'max': 600},
        'Sedang': {'min': 80, 'recommended': 150, 'max': 400},
        'Sedang-Rendah': {'min': 50, 'recommended': 100, 'max': 250},
        'Rendah': {'min': 20, 'recommended': 60, 'max': 150}
    }
    
    review_range = competition_reviews.get(competition_level, competition_reviews['Sedang'])
    
    # Review expectation with better explanation
    default_ulasan = getattr(st.session_state, 'jumlah_ulasan', review_range['recommended'])
    jumlah_ulasan = st.sidebar.number_input(
        "Target Jumlah Review (dalam 2 tahun)", 
        min_value=review_range['min'], 
        max_value=review_range['max'],
        value=default_ulasan,
        step=10,
        help=f"""Target realistis untuk area dengan kompetisi {competition_level.lower()}:
        • Min: {review_range['min']} (conservative)
        • Recommended: {review_range['recommended']} (realistic) 
        • Max: {review_range['max']} (optimistic)
        
        ⚠️ Target terlalu tinggi = area over-competitive!"""
    )
    
    # Rating expectations
    default_rating = getattr(st.session_state, 'google_rating', 4.2)
    google_rating = st.sidebar.slider(
        "Target Rating Google", 
        min_value=1.0, 
        max_value=5.0, 
        value=default_rating,
        step=0.1,
        help="Target rating Google yang ingin dicapai"
    )
    
    # Prediction button
    if st.sidebar.button("🎯 Analisis Potensi Bisnis", type="primary"):
        # Create data dictionary using kecamatan data
        input_data = {
            'Jumlah Penduduk': kecamatan_data['population'],
            'Luas Wilayah (km²)': kecamatan_data['area_km2'],
            'Kepadatan (jiwa/km²)': kecamatan_data['density'],
            'jumlah_mall': kecamatan_data['malls'],
            'jumlah_minimarket': kecamatan_data['minimarkets'],
            'jumlah_taman': kecamatan_data['parks'],
            'jumlah_ulasan': jumlah_ulasan,
            'google_rating': google_rating,
            'kategori_resto': kategori_resto,
            'price_range': price_range,
            'kecamatan': kecamatan_data['name']
        }
        
        # Store in session state
        st.session_state.input_data = input_data
        st.session_state.kecamatan_data = kecamatan_data
        st.session_state.prediction_made = True
        
        # Store inputs for persistence
        st.session_state.kategori_resto = kategori_resto
        st.session_state.price_range = price_range
        st.session_state.jumlah_ulasan = jumlah_ulasan
        st.session_state.google_rating = google_rating
        
        # Preprocess data
        with st.spinner("Memproses data dan membuat prediksi..."):
            X_scaled = preprocess_data(input_data, components)
            
            # Make prediction
            model = components['model']
            target_mapping_inv = {v: k for k, v in components['target_mapping'].items()}
            
            # Get prediction probabilities
            probas = model.predict_proba(X_scaled)[0]
            predicted_class_idx = np.argmax(probas)
            predicted_class = target_mapping_inv[predicted_class_idx]
            class_names = [target_mapping_inv[i] for i in range(len(probas))]
            
            # Store prediction results
            st.session_state.probas = probas
            st.session_state.predicted_class = predicted_class
            st.session_state.class_names = class_names
    
    # Display results if prediction has been made
    if hasattr(st.session_state, 'prediction_made') and st.session_state.prediction_made:
        # Main content area
        st.markdown('<h2 class="section-header">📍 Analisis Lokasi Kecamatan</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            display_kecamatan_info(st.session_state.kecamatan_data)
        
        with col2:
            # Kecamatan visualization
            fig_kecamatan = create_bandung_map_visualization(st.session_state.selected_kecamatan, st.session_state.kecamatan_data)
            st.plotly_chart(fig_kecamatan, use_container_width=True)
        
        # Business profile summary
        st.markdown('<h3 class="section-header">🍽️ Profil Bisnis</h3>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📍 Kecamatan", st.session_state.input_data['kecamatan'])
        with col2:
            st.metric("🏷️ Kategori", st.session_state.input_data['kategori_resto'])
        with col3:
            price_symbol = "$" * st.session_state.input_data['price_range']
            st.metric("💰 Harga", price_symbol)
        with col4:
            st.metric("⭐ Target Rating", f"{st.session_state.input_data['google_rating']}/5.0")
        
        # Prediction results
        st.markdown('<h2 class="section-header">🎯 Hasil Prediksi AI</h2>', unsafe_allow_html=True)
        
        predicted_class = st.session_state.predicted_class
        probas = st.session_state.probas
        class_names = st.session_state.class_names
        
        # Display main prediction
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create and display visualization
            fig = create_prediction_visualization(probas, class_names, predicted_class)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Prediction summary with Indonesian labels
            max_prob = max(probas)
            confidence_level = "Tinggi" if max_prob > 0.7 else "Sedang" if max_prob > 0.5 else "Rendah"
            
            prediction_labels = {
                "Go": "LANJUTKAN",
                "Consider": "PERTIMBANGKAN", 
                "Avoid": "HINDARI"
            }
            
            if predicted_class == "Go":
                st.markdown(f"""
                <div class="prediction-box success-box">
                    <h3>✅ {prediction_labels[predicted_class]}</h3>
                    <p><strong>Prediksi:</strong> Sukses Tinggi</p>
                    <p><strong>Confidence:</strong> {confidence_level} ({max_prob:.1%})</p>
                    <p>Lokasi ini memiliki probabilitas sukses yang tinggi untuk bisnis FnB!</p>
                </div>
                """, unsafe_allow_html=True)
            elif predicted_class == "Consider":
                st.markdown(f"""
                <div class="prediction-box warning-box">
                    <h3>⚠️ {prediction_labels[predicted_class]}</h3>
                    <p><strong>Prediksi:</strong> Risiko Sedang</p>
                    <p><strong>Confidence:</strong> {confidence_level} ({max_prob:.1%})</p>
                    <p>Potensi moderat dengan beberapa faktor risiko yang perlu dipertimbangkan.</p>
                </div>
                """, unsafe_allow_html=True)
            else:  # Avoid
                st.markdown(f"""
                <div class="prediction-box danger-box">
                    <h3>❌ {prediction_labels[predicted_class]}</h3>
                    <p><strong>Prediksi:</strong> Risiko Tinggi</p>
                    <p><strong>Confidence:</strong> {confidence_level} ({max_prob:.1%})</p>
                    <p>Risiko tinggi kegagalan bisnis di lokasi ini.</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Detailed probabilities with Indonesian labels
        st.markdown('<h3 class="section-header">📊 Detail Analisis Probabilitas</h3>', unsafe_allow_html=True)
        
        # Map English to Indonesian
        indo_class_names = []
        for name in class_names:
            if name == "Go":
                indo_class_names.append("Lanjutkan")
            elif name == "Consider": 
                indo_class_names.append("Pertimbangkan")
            else:
                indo_class_names.append("Hindari")
        
        prob_df = pd.DataFrame({
            'Rekomendasi': indo_class_names,
            'Probabilitas': [f"{p:.2%}" for p in probas],
            'Probabilitas_Value': probas
        })
        
        # Create horizontal bar chart for detailed view
        fig_detailed = px.bar(
            prob_df, 
            x='Probabilitas_Value', 
            y='Rekomendasi',
            orientation='h',
            text='Probabilitas',
            color='Rekomendasi',
            color_discrete_map={
                'Hindari': '#ff4444',
                'Pertimbangkan': '#ffaa00', 
                'Lanjutkan': '#44ff44'
            }
        )
        fig_detailed.update_layout(
            title="Distribusi Probabilitas Rekomendasi",
            xaxis_title="Probabilitas",
            xaxis=dict(tickformat='.0%'),
            showlegend=False,
            height=300
        )
        fig_detailed.update_traces(textposition='auto')
        
        st.plotly_chart(fig_detailed, use_container_width=True)
        
        # Business recommendations with competition context
        st.markdown('<h3 class="section-header">💡 Rekomendasi Bisnis & Interpretasi</h3>', unsafe_allow_html=True)
        
        # Add interpretation note
        st.info(f"""
        **📊 Catatan Interpretasi Model:**
        Target review yang Anda set: **{st.session_state.input_data['jumlah_ulasan']} reviews**
        
        • **High Review Target (>500)** → Area kompetitif tinggi, butuh modal besar & diferensiasi kuat
        • **Medium Review Target (150-500)** → Area balanced, kompetisi sedang  
        • **Low Review Target (<150)** → Area emerging, peluang pioneer tapi perlu edukasi pasar
        """)
        
        if predicted_class == "Go":
            if st.session_state.input_data['jumlah_ulasan'] > 500:
                st.warning(f"""
                **⚠️ REKOMENDASI UNTUK AREA KOMPETITIF - Kecamatan {st.session_state.kecamatan_data['name']}:**
                - 🏆 **Model memprediksi sukses KARENA target tinggi cocok dengan area kompetitif**
                - 💰 **Modal Besar Required**: Siapkan investasi signifikan untuk bersaing
                - 🎯 **Diferensiasi Wajib**: Harus punya unique selling point yang kuat
                - 📍 **Lokasi Premium**: Fokus ke spot strategis dengan foot traffic tinggi  
                - 🚀 **Marketing Agresif**: Budget marketing harus substantial untuk breakthrough
                - ⏰ **Break-even Lama**: Ekspektasi ROI dalam 18-24 bulan, bukan 6-12 bulan
                """)
            else:
                st.success(f"""
                **✅ REKOMENDASI UNTUK TARGET REALISTIS - Kecamatan {st.session_state.kecamatan_data['name']}:**
                - 🎯 **Target Sesuai Kondisi**: Review target Anda realistic untuk area ini
                - 💡 **Strategi Fokus**: Prioritas pada kualitas vs quantity di awal
                - 📈 **Growth Gradual**: Build base customer loyal terlebih dahulu
                - 🏘️ **Community-Centric**: Manfaatkan kedekatan dengan masyarakat lokal
                - 💵 **Modal Efisien**: Bisa mulai dengan modal lebih modest dan scale up
                """)
        elif predicted_class == "Consider":
            st.warning(f"""
            **⚠️ PERTIMBANGAN MENDALAM - Kecamatan {st.session_state.kecamatan_data['name']}:**
            - 🔍 **Analisis Gap**: Cek apakah target review Anda sesuai dengan potensi area
            - 📊 **Riset Kompetitor**: Survey langsung resto existing, hitung rata-rata review mereka  
            - 💰 **Budget Planning**: Siapkan runway 12-18 bulan untuk mencapai break-even
            - 🎨 **Concept Validation**: Test konsep dengan soft opening/pre-launch campaign
            - 📱 **Digital Strategy**: Fokus pada online presence dan delivery di awal
            - 🤝 **Partnership**: Pertimbangkan kolaborasi dengan bisnis lokal existing
            """)
        else:
            if st.session_state.input_data['jumlah_ulasan'] > 400:
                st.error(f"""
                **❌ TARGET TERLALU TINGGI UNTUK AREA INI - Kecamatan {st.session_state.kecamatan_data['name']}:**
                - 📉 **Mismatch**: Target review terlalu optimis untuk karakteristik area
                - 🔄 **Adjust Expectation**: Turunkan target ke range 100-200 reviews
                - 📍 **Alternative Location**: Pertimbangkan kecamatan dengan traffic lebih tinggi
                - 💡 **Niche Focus**: Jika tetap lanjut, fokus ke segment spesifik (misal: family dining)
                - 🏠 **Hyperlocal**: Strategy door-to-door dan word-of-mouth marketing
                """)
            else:
                st.error(f"""
                **❌ MITIGASI RISIKO AREA CHALLENGING - Kecamatan {st.session_state.kecamatan_data['name']}:**
                - 🎯 **Model Insight**: Meski target reasonable, area ini memiliki tantangan struktural  
                - 📊 **Deep Research**: Lakukan survei mendalam tentang dining habits lokal
                - 🥇 **First Mover**: Jika kompetisi rendah, bisa jadi pioneer tapi butuh edukasi pasar
                - 💸 **Low Investment**: Mulai dengan konsep lean, test market dulu
                - 🔄 **Pivot Ready**: Siap mengubah konsep berdasarkan feedback pasar
                """)
        
        # Model interpretation explanation
        st.markdown('<h3 class="section-header">🧠 Bagaimana AI Menganalisis Data Anda</h3>', unsafe_allow_html=True)
        
        review_input = st.session_state.input_data['jumlah_ulasan']
        rating_input = st.session_state.input_data['google_rating']
        
        st.markdown(f"""
        **📈 Analisis Input Anda:**
        
        🔹 **Target Review: {review_input}** 
        - Model melihat ini sebagai indikator **tingkat kompetisi area**
        - **Tinggi (>500)**: "Area ini ramai, banyak resto sukses, tapi butuh modal besar untuk bersaing"  
        - **Sedang (150-500)**: "Area balanced, kompetisi wajar, peluang realistis"
        - **Rendah (<150)**: "Area masih developing, lebih mudah penetrasi tapi market size kecil"
        
        🔹 **Target Rating: {rating_input}/5.0**
        - **4.5+**: Ekspektasi premium, butuh execution excellence
        - **4.0-4.4**: Standard yang baik dan sustainable  
        - **<4.0**: Fokus value-for-money, acceptable quality
        
        🔹 **Kombinasi Logika**: 
        Model trained dengan data bahwa resto sukses (Go) umumnya ada di area dengan **review volume tinggi** 
        (kompetitor banyak) DAN berhasil **menonjol** di area tersebut. Jadi **bukan "semakin banyak review semakin mudah"**, 
        tapi **"kalau Anda target tinggi, pastikan siap berkompetisi di level itu"**.
        """)
        
        # Additional insights based on kecamatan characteristics
        st.markdown('<h3 class="section-header">🔍 Insight Khusus Lokasi</h3>', unsafe_allow_html=True)
        
        kec_data = st.session_state.kecamatan_data
        
        # Generate specific insights
        insights = []
        
        if kec_data['density'] > 20000:
            insights.append("🏘️ **Kepadatan Tinggi**: Area ini memiliki traffic pelanggan potensial yang besar")
        elif kec_data['density'] < 10000:
            insights.append("🏞️ **Kepadatan Rendah**: Fokus pada customer loyalty dan repeat customers")
        
        if kec_data['malls'] >= 3:
            insights.append("🏬 **Infrastruktur Mall Baik**: Kompetisi tinggi tapi akses customer mudah")
        elif kec_data['malls'] < 2:
            insights.append("🏪 **Mall Terbatas**: Kesempatan untuk menjadi pioneer di area ini")
        
        if kec_data['minimarkets'] > 30:
            insights.append("🛒 **Retail Density Tinggi**: Area komersial aktif dengan daya beli baik")
        elif kec_data['minimarkets'] < 15:
            insights.append("🚶 **Retail Terbatas**: Pertimbangkan aksesibilitas dan convenience factor")
        
        if kec_data['parks'] > 40:
            insights.append("🌳 **Banyak Ruang Hijau**: Area family-friendly, cocok untuk family dining")
        
        for insight in insights:
            st.info(insight)
    
    else:
        # Initial state - show Bandung information
        st.markdown("## 🏙️ Selamat Datang di Prediksi Bisnis FnB Kota Bandung")
        
        # Create tabs for different information
        tab1, tab2, tab3 = st.tabs(["🚀 Panduan Penggunaan", "📊 Tentang Kecamatan Bandung", "💡 Tips Bisnis FnB"])
        
        with tab1:
            st.markdown("""
            ### Cara Menggunakan Aplikasi Prediksi
            
            1. **📍 Pilih Kecamatan**: Pilih kecamatan di Bandung tempat usaha akan didirikan
            2. **🍽️ Tentukan Jenis Bisnis**: Pilih kategori dan kisaran harga restoran  
            3. **📊 Set Target Realistis**: Masukkan target review dan rating yang sesuai kondisi area
            4. **🎯 Dapatkan Analisis**: Klik tombol analisis untuk mendapat prediksi AI
            
            **⚠️ PENTING - Cara Membaca Jumlah Review:**
            - **Jumlah review BUKAN "semakin besar semakin mudah sukses"**  
            - **Jumlah review = indicator tingkat KOMPETISI di area tersebut**
            - **Target tinggi (>500)** = Anda siap bersaing di area kompetitif dengan modal besar
            - **Target rendah (<150)** = Anda memilih strategi pioneer di area emerging
            - **Target sedang (150-500)** = Ekspektasi balanced sesuai kondisi area
            
            **Fitur Unggulan:**
            - ✅ **Data Kecamatan Real**: Menggunakan data demografis dan infrastruktur aktual Kota Bandung
            - ✅ **AI Analysis**: Model machine learning yang dilatih dengan 5000+ data bisnis FnB real
            - ✅ **Competition-Aware**: Analisis level kompetisi per kecamatan  
            - ✅ **Rekomendasi Kontekstual**: Saran disesuaikan dengan target dan karakteristik area
            - ✅ **Visual Analytics**: Grafik interaktif untuk analisis yang mudah dipahami
            """)
        
        with tab2:
            st.markdown("""
            ### Profil Kecamatan di Kota Bandung
            
            Kota Bandung memiliki **30 kecamatan** dengan karakteristik unik masing-masing:
            
            **Kecamatan dengan Kepadatan Tertinggi:**
            - 🏆 Bojongloa Kaler: 39,847 jiwa/km²
            - 🥈 Cibeunying Kidul: 27,424 jiwa/km²  
            - 🥉 Astanaanyar: 27,325 jiwa/km²
            
            **Kecamatan dengan Infrastruktur Terbaik:**
            - 🏬 Bandung Wetan: 4 mall, 117 taman
            - 🛒 Coblong: 62 minimarket, area premium
            - 🌳 Arcamanik: 77 taman, area hijau
            
            **Area Strategis untuk FnB:**
            - 💼 **Pusat Kota**: Sumur Bandung, Bandung Wetan
            - 🏘️ **Residensial Premium**: Sukajadi, Coblong
            - 👨‍👩‍👧‍👦 **Family Area**: Antapani, Buahbatu
            """)
        
        with tab3:
            st.markdown("""
            ### Tips Sukses Bisnis FnB di Bandung
            
            **🎯 Faktor Kunci Sukses:**
            1. **Lokasi Strategis**: Pilih area dengan traffic tinggi dan aksesibilitas baik
            2. **Target Market**: Sesuaikan konsep dengan demografi kecamatan
            3. **Kompetisi**: Analisis pesaing dan cari diferensiasi unik
            4. **Harga**: Sesuaikan dengan daya beli masyarakat setempat
            
            **💡 Insight Berdasarkan Data:**
            - **Area Padat**: Fokus pada speed service dan takeaway
            - **Area Premium**: Emphasis pada experience dan ambiance  
            - **Area Keluarga**: Menu kids-friendly dan family package
            - **Area Muda**: Instagram-worthy concept dan digital marketing
            
            **⚠️ Hindari Kesalahan Umum:**
            - Tidak riset kompetitor lokal
            - Overestimasi daya beli area
            - Underestimasi biaya operasional
            - Mengabaikan preferensi lokal Bandung
            """)
        
        # Quick kecamatan samples
        st.markdown("## 🎯 Coba Analisis Cepat")
        st.markdown("**Pilih kecamatan untuk melihat contoh analisis:**")
        
        # Get some interesting kecamatan examples
        sample_kecamatan = [
            ('sumur_bandung', '🏛️ Sumur Bandung - Pusat Kota'),
            ('coblong', '💎 Coblong - Area Premium'), 
            ('bojongloa_kaler', '🏘️ Bojongloa Kaler - Kepadatan Tinggi'),
            ('gedebage', '🏭 Gedebage - Area Industri')
        ]
        
        col1, col2, col3, col4 = st.columns(4)
        
        for i, (kec_key, kec_label) in enumerate(sample_kecamatan):
            with [col1, col2, col3, col4][i]:
                if st.button(kec_label, key=f"quick_{kec_key}"):
                    # Set sample data and trigger analysis
                    st.session_state.selected_kecamatan = kec_key
                    st.session_state.kategori_resto = 'Restaurant'
                    st.session_state.price_range = 2
                    st.session_state.jumlah_ulasan = 150
                    st.session_state.google_rating = 4.2
                    st.rerun()

if __name__ == "__main__":
    main()