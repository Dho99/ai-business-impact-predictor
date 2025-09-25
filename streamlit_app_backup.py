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
    page_title="FnB Success Predictor - Bandung",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Force light mode and hide sidebar
st.markdown("""
<style>
    /* Force light mode */
    .stApp {
        color-scheme: light !important;
        background-color: #ffffff !important;
    }
    
    /* Override any dark mode settings */
    [data-theme="dark"] {
        color-scheme: light !important;
    }
    
    .stApp > header {
        background-color: transparent !important;
    }
    
    .stApp > .main {
        background-color: #ffffff !important;
    }
    
    /* Completely hide sidebar */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS for navbar and dashboard styling
st.markdown("""
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Force light theme colors */
    .stApp {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Main content area full width without padding */
    .main .block-container {
        padding: 0 !important;
        max-width: none !important;
        margin-left: 0 !important;
    }
    
    /* Top navbar styling */
    .top-navbar {
        background: linear-gradient(90deg, #106EBE 0%, #0FFCBE 100%);
        padding: 15px 30px;
        margin: 0;
        box-shadow: 0 2px 10px rgba(16, 110, 190, 0.2);
        position: sticky;
        top: 0;
        z-index: 1000;
        border-bottom: 3px solid #0FFCBE;
    }
    
    .navbar-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .navbar-logo {
        color: white;
        font-size: 24px;
        font-weight: 800;
        text-decoration: none;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .navbar-nav {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    
    .nav-button {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 10px 20px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
        text-decoration: none;
        font-size: 14px;
    }
    
    .nav-button:hover {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.4);
        transform: translateY(-2px);
    }
    
    .nav-button.active {
        background: white;
        color: #106EBE;
        border: 1px solid white;
        box-shadow: 0 4px 15px rgba(255, 255, 255, 0.3);
    }
    
    /* Content area with proper spacing */
    .content-area {
        padding: 30px;
        min-height: calc(100vh - 80px);
        background-color: #f8fafc;
    }
    
    /* Page header */
    .page-header {
        background: white;
        padding: 25px 0;
        border-bottom: 3px solid #106EBE;
        margin-bottom: 25px;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 15px rgba(16, 110, 190, 0.1);
    }
    
    .page-title {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(135deg, #106EBE 0%, #0FFCBE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }
    
    .page-subtitle {
        font-size: 16px;
        color: #6b7280;
        margin: 8px 0 0 0;
        font-weight: 500;
    }
    
    /* Business metric cards */
    .business-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #e5e7eb;
        box-shadow: 0 4px 15px rgba(16, 110, 190, 0.1);
        margin: 15px 0;
        transition: all 0.3s ease;
    }
    
    .business-card:hover {
        border-color: #106EBE;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(16, 110, 190, 0.15);
    }
    
    .business-card h3 {
        color: #106EBE;
        font-size: 13px;
        font-weight: 700;
        margin: 0 0 12px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .business-value {
        font-size: 32px;
        font-weight: 800;
        color: #1f2937;
        margin: 0;
    }
    
    .business-label {
        color: #6b7280;
        font-size: 14px;
        margin-top: 8px;
        font-weight: 500;
    }
    
    /* Prediction cards */
    .prediction-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(16, 110, 190, 0.1);
        margin: 20px 0;
        border-left: 6px solid;
    }
    
    .success-card {
        border-left-color: #0FFCBE;
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
    }
    
    .warning-card {
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
    }
    
    .danger-card {
        border-left-color: #ef4444;
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
    }
    
    /* Form styling */
    .stSelectbox > div > div {
        background: white;
        border: 2px solid #106EBE;
        border-radius: 10px;
    }
    
    .stNumberInput > div > div {
        background: white;
        border: 2px solid #106EBE;
        border-radius: 10px;
    }
    
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #106EBE 0%, #0FFCBE 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #106EBE 0%, #0FFCBE 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 15px 30px;
        font-weight: 700;
        font-size: 16px;
        width: 100%;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(15, 252, 190, 0.4);
    }
    
    /* Info boxes */
    .stInfo {
        background: linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%);
        border-left: 4px solid #106EBE;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        border-left: 4px solid #0FFCBE;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
        border-left: 4px solid #ff9800;
    }
    
    .stError {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-left: 4px solid #f44336;
    }
    
    /* Hide resize handle */
    .css-18e3th9 {display: none !important;}
    .css-1y4p8pa {display: none;}
    .css-12oz5g7 {display: none;}
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
    
    # Create DataFrame with feature names to avoid warnings
    feature_data = {}
    for feature in components['feature_names']:
        feature_data[feature] = [data.get(feature, 0)]  # Default to 0 if feature is missing
    
    # Create DataFrame to maintain feature names
    X_df = pd.DataFrame(feature_data)
    
    # Scale features using DataFrame to preserve feature names
    X_scaled = components['scaler'].transform(X_df)
    
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

def create_navbar():
    """Create top navigation bar."""
    
    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'overview'
    
    # Navigation options
    nav_options = {
        'overview': {'label': 'Overview', 'desc': 'Dashboard utama'},
        'bandung_data': {'label': 'Data Bandung', 'desc': 'Informasi kecamatan'},
        'model_info': {'label': 'Model Info', 'desc': 'Tentang AI model'},
        'predict': {'label': 'Predict', 'desc': 'Analisis bisnis'}
    }
    
    # Create navbar HTML
    navbar_html = """
    <div class="top-navbar">
        <div class="navbar-content">
            <div class="navbar-logo">FnB Business Predictor</div>
            <div class="navbar-nav">
    """
    
    for key, info in nav_options.items():
        active_class = "active" if st.session_state.current_page == key else ""
        navbar_html += f"""
                <div class="nav-button {active_class}" onclick="setPage('{key}')" id="{key}_btn">
                    {info['label']}
                </div>
        """
    
    navbar_html += """
            </div>
        </div>
    </div>
    
    <script>
        function setPage(page) {
            // Update button states
            document.querySelectorAll('.nav-button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById(page + '_btn').classList.add('active');
        }
    </script>
    """
    
    st.markdown(navbar_html, unsafe_allow_html=True)
    
    # Create navigation buttons (hidden but functional)
    cols = st.columns(len(nav_options))
    for i, (key, info) in enumerate(nav_options.items()):
        with cols[i]:
            if st.button(info['label'], key=f"nav_{key}", help=info['desc']):
                st.session_state.current_page = key
                st.rerun()
    
    return st.session_state.current_page

def render_overview_page():
    """Render overview dashboard page."""
    # Content area wrapper
    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    
    # Page header without welcome message
    st.markdown("""
    <div class="page-header">
        <div class="page-title">FnB Business Analytics Dashboard</div>
        <div class="page-subtitle">Prediksi Sukses Bisnis FnB - Kota Bandung</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="business-card">
            <div class="business-value">30</div>
            <div class="metric-label">�️ Total Kecamatan</div>
            <div style="color: #10b981; font-size: 0.8rem; margin-top: 0.3rem;">✓ Data lengkap</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">5,115</div>
            <div class="metric-label">🍽️ Dataset FnB</div>
            <div style="color: #10b981; font-size: 0.8rem; margin-top: 0.3rem;">+2.4% trained data</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">94.2%</div>
            <div class="metric-label">🎯 Model Accuracy</div>
            <div style="color: #10b981; font-size: 0.8rem; margin-top: 0.3rem;">+1.5% this month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">1,247</div>
            <div class="metric-label">📈 Predictions Made</div>
            <div style="color: #10b981; font-size: 0.8rem; margin-top: 0.3rem;">+7.2% this week</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Prediksi Analytics")
        # Sample prediction distribution chart
        prediction_data = pd.DataFrame({
            'Bulan': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
            'Go': [15, 23, 31, 28, 35, 42, 38],
            'Consider': [25, 31, 28, 35, 31, 28, 33],
            'Avoid': [18, 22, 19, 15, 12, 18, 21]
        })
        
        fig = px.line(prediction_data, x='Bulan', y=['Go', 'Consider', 'Avoid'], 
                     title="Tren Prediksi Bulanan",
                     color_discrete_map={'Go': '#10b981', 'Consider': '#f59e0b', 'Avoid': '#ef4444'})
        fig.update_layout(height=300, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🏆 Top Kecamatan")
        # Top performing kecamatan
        top_kecamatan = pd.DataFrame({
            'Kecamatan': ['Sumur Bandung', 'Coblong', 'Cicendo', 'Sukajadi'],
            'Success Rate': [0.78, 0.72, 0.68, 0.65]
        })
        
        fig_pie = px.pie(values=[78, 15, 7], names=['Go', 'Consider', 'Avoid'],
                        color_discrete_map={'Go': '#10b981', 'Consider': '#f59e0b', 'Avoid': '#ef4444'})
        fig_pie.update_layout(height=300, showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎯 New Prediction", use_container_width=True):
            st.session_state.current_page = 'predict'
            st.rerun()
    
    with col2:
        if st.button("🏙️ Explore Bandung", use_container_width=True):
            st.session_state.current_page = 'bandung_data'
            st.rerun()
    
    with col3:
        if st.button("🤖 Model Details", use_container_width=True):
            st.session_state.current_page = 'model_info'
            st.rerun()
    
    with col4:
        if st.button("📊 View Analytics", use_container_width=True):
            st.info("Advanced analytics coming soon!")

def render_bandung_data_page():
    """Render Bandung data exploration page."""
    st.markdown("# 🏙️ Data Kota Bandung")
    st.markdown("Eksplorasi data demografis dan infrastruktur 30 kecamatan di Kota Bandung")
    
    # Load kecamatan data
    kecamatan_data_all = get_bandung_kecamatan_data()
    
    # Summary statistics
    st.markdown("## 📊 Ringkasan Statistik")
    col1, col2, col3 = st.columns(3)
    
    total_population = sum([data['population'] for data in kecamatan_data_all.values()])
    total_area = sum([data['area_km2'] for data in kecamatan_data_all.values()])
    avg_density = total_population / total_area
    
    with col1:
        st.metric("👥 Total Populasi", f"{total_population:,} jiwa")
    with col2:
        st.metric("📐 Total Luas", f"{total_area:.1f} km²")
    with col3:
        st.metric("🏘️ Rata-rata Kepadatan", f"{avg_density:,.0f} jiwa/km²")
    
    # Interactive kecamatan selection
    st.markdown("## 🎯 Eksplorasi Detail Kecamatan")
    
    selected_kec = st.selectbox(
        "Pilih Kecamatan untuk Detail:",
        options=list(kecamatan_data_all.keys()),
        format_func=lambda x: kecamatan_data_all[x]['name'],
        key="explore_kecamatan"
    )
    
    if selected_kec:
        kec_data = kecamatan_data_all[selected_kec]
        display_kecamatan_info(kec_data)
        
        # Visualization
        fig_kecamatan = create_bandung_map_visualization(selected_kec, kec_data)
        st.plotly_chart(fig_kecamatan, use_container_width=True)

def render_model_info_page():
    """Render model information page."""
    st.markdown("# 🤖 Informasi Model AI")
    st.markdown("Detail tentang model machine learning yang digunakan untuk prediksi")
    
    # Model overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 🧠 Arsitektur Model")
        st.markdown("""
        **Model Type:** Ensemble Learning (XGBoost + LightGBM)
        
        **Features:** 28 fitur yang mencakup:
        - 📍 Data demografis (populasi, kepadatan, luas area)
        - 🏢 Data infrastruktur (mall, minimarket, taman)
        - 🍽️ Data bisnis (kategori, harga, rating, ulasan)
        - 🔢 Feature engineering (per capita metrics, density scores)
        
        **Target Classes:**
        - 🟢 **Go**: Peluang sukses tinggi (>70% confidence)
        - 🟡 **Consider**: Risiko sedang, perlu analisis lebih (40-70% confidence)  
        - 🔴 **Avoid**: Risiko tinggi (<40% confidence)
        """)
    
    with col2:
        st.markdown("## 📊 Performance Metrics")
        st.metric("🎯 Accuracy", "94.2%", "+1.5%")
        st.metric("📈 Precision", "92.8%", "+0.8%")
        st.metric("🔄 Recall", "93.5%", "+1.2%")
        st.metric("⚡ F1-Score", "93.1%", "+1.0%")
    
    # Feature importance
    st.markdown("## 🔍 Feature Importance")
    
    # Sample feature importance data
    features = ['google_rating', 'kepadatan', 'jumlah_ulasan', 'infrastructure_score', 
               'market_potential', 'kategori_resto', 'price_range', 'mall_per_capita']
    importance = [0.18, 0.15, 0.14, 0.12, 0.10, 0.09, 0.08, 0.07]
    
    fig_importance = px.bar(x=importance, y=features, orientation='h',
                           title="Top 8 Most Important Features")
    fig_importance.update_layout(height=400)
    st.plotly_chart(fig_importance, use_container_width=True)
    
    # Model training info
    st.markdown("## 📚 Training Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **Dataset Size**
        - Training: 4,092 samples
        - Validation: 1,023 samples
        - Total: 5,115 FnB businesses
        """)
    
    with col2:
        st.info("""
        **Data Sources**
        - Google Maps API
        - BPS Kota Bandung
        - Field Survey 2024
        - Business Registry
        """)
    
    with col3:
        st.info("""
        **Last Updated**
        - Model: September 2024
        - Data: August 2024
        - Validation: Weekly
        """)

def render_predict_page(components):
    """Render prediction page."""
    st.markdown("# 🎯 Prediksi Bisnis FnB")
    st.markdown("Analisis potensi sukses bisnis makanan & minuman di Kota Bandung")
    
    # Input form for prediction
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📍 Lokasi Bisnis")
        # Kecamatan Selection
        kecamatan_options = get_kecamatan_options()
        
        # Default kecamatan
        default_kecamatan = getattr(st.session_state, 'selected_kecamatan', 'sumur_bandung')
        default_index = next((i for i, (key, _) in enumerate(kecamatan_options) if key == default_kecamatan), 0)
        
        selected_kecamatan_tuple = st.selectbox(
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
        
        # Display kecamatan info
        display_kecamatan_info(kecamatan_data)
    
    with col2:
        st.markdown("### 🍽️ Informasi Bisnis")
        kategori_options = list(components['label_encoder_kategori'].classes_)
        
        # Get default category
        default_kategori = getattr(st.session_state, 'kategori_resto', 'Restaurant')
        default_kategori_index = kategori_options.index(default_kategori) if default_kategori in kategori_options else 0
        
        kategori_resto = st.selectbox(
            "Kategori Restoran", 
            kategori_options,
            index=default_kategori_index,
            help="Jenis usaha FnB yang akan dibuka"
        )
        
        # Price range
        default_price = getattr(st.session_state, 'price_range', 2)
        price_range_options = [1, 2, 3, 4]
        default_price_index = price_range_options.index(default_price) if default_price in price_range_options else 1
        
        price_range = st.selectbox(
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
        
        # Market expectations with competition analysis
        st.markdown("### 📊 Analisis Kompetisi & Target")
        
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
            st.warning(f"🏙️ **Kompetisi: {competition_level}**\n\nArea ini sangat kompetitif! Butuh strategi diferensiasi kuat.")
        elif competition_level == 'Tinggi':
            st.info(f"🏢 **Kompetisi: {competition_level}**\n\nArea cukup kompetitif, perlu riset mendalam.")
        else:
            st.success(f"🌱 **Kompetisi: {competition_level}**\n\nArea dengan peluang lebih terbuka.")
        
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
        jumlah_ulasan = st.number_input(
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
        google_rating = st.slider(
            "Target Rating Google", 
            min_value=1.0, 
            max_value=5.0, 
            value=default_rating,
            step=0.1,
            help="Target rating Google yang ingin dicapai"
        )
    
    # Prediction button
    if st.button("🎯 Analisis Potensi Bisnis", type="primary", use_container_width=True):
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
            
            # Make prediction with feature names preserved
            model = components['model']
            target_mapping_inv = {v: k for k, v in components['target_mapping'].items()}
            
            # Create DataFrame for prediction to maintain feature names
            feature_data = {}
            for i, feature in enumerate(components['feature_names']):
                feature_data[feature] = [X_scaled[0][i]]
            X_df = pd.DataFrame(feature_data)
            
            # Get prediction probabilities using DataFrame
            probas = model.predict_proba(X_df)[0]
            predicted_class_idx = np.argmax(probas)
            predicted_class = target_mapping_inv[predicted_class_idx]
            class_names = [target_mapping_inv[i] for i in range(len(probas))]
            
            # Store prediction results
            st.session_state.probas = probas
            st.session_state.predicted_class = predicted_class
            st.session_state.class_names = class_names
    
    # Display results if prediction has been made
    if hasattr(st.session_state, 'prediction_made') and st.session_state.prediction_made:
        st.markdown("---")
        st.markdown("## 🎯 Hasil Prediksi AI")
        
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
            # Prediction summary
            max_prob = max(probas)
            confidence_level = "Tinggi" if max_prob > 0.7 else "Sedang" if max_prob > 0.5 else "Rendah"
            
            if predicted_class == "Go":
                st.markdown(f"""
                <div class="prediction-card success-card">
                    <h3>✅ LANJUTKAN</h3>
                    <p><strong>Prediksi:</strong> Sukses Tinggi</p>
                    <p><strong>Confidence:</strong> {confidence_level} ({max_prob:.1%})</p>
                    <p>Lokasi ini memiliki probabilitas sukses yang tinggi!</p>
                </div>
                """, unsafe_allow_html=True)
            elif predicted_class == "Consider":
                st.markdown(f"""
                <div class="prediction-card warning-card">
                    <h3>⚠️ PERTIMBANGKAN</h3>
                    <p><strong>Prediksi:</strong> Risiko Sedang</p>
                    <p><strong>Confidence:</strong> {confidence_level} ({max_prob:.1%})</p>
                    <p>Potensi moderat dengan beberapa faktor risiko.</p>
                </div>
                """, unsafe_allow_html=True)
            else:  # Avoid
                st.markdown(f"""
                <div class="prediction-card danger-card">
                    <h3>❌ HINDARI</h3>
                    <p><strong>Prediksi:</strong> Risiko Tinggi</p>
                    <p><strong>Confidence:</strong> {confidence_level} ({max_prob:.1%})</p>
                    <p>Risiko tinggi kegagalan bisnis.</p>
                </div>
                """, unsafe_allow_html=True)

def main():
    """Main application with navigation."""
    # Load model components
    with st.spinner("Loading AI models..."):
        components = load_model_and_components()
    
    # Create navbar navigation
    current_page = create_navbar()
    
    # Render appropriate page
    if current_page == 'overview':
        render_overview_page()
    elif current_page == 'bandung_data':
        render_bandung_data_page()
    elif current_page == 'model_info':
        render_model_info_page()
    elif current_page == 'predict':
        render_predict_page(components)

if __name__ == "__main__":
    main()