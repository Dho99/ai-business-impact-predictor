#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FnB Business Success Predictor

This script predicts the potential success of an FnB (Food and Beverage) business
based on strategic location factors using a pre-trained ensemble model.

Usage:
    python predict_fnb_business_success.py
"""

import os
import sys
import json

# Check for required packages
try:
    import joblib
    import numpy as np
    import pandas as pd
    from pathlib import Path
    import matplotlib.pyplot as plt
    from sklearn.preprocessing import LabelEncoder
    # Explicitly import model packages that are required
    import xgboost as xgb
    import lightgbm as lgb
except ImportError as e:
    print(f"\n❌ Missing required package: {str(e)}")
    print("\nPlease install the missing package using:")
    print("pip install -r requirements.txt")
    print("\nOr install the specific missing package with:")
    print(f"pip install {str(e).split()[-1]}")
    sys.exit(1)

# Configuration
COMPETITION_DIR = os.path.join(os.path.dirname(__file__), 'models', 'competition')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

# Ensure results directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)

def load_model_and_components():
    """Load the trained model and all necessary components for prediction."""
    try:
        # Verify competition directory exists
        if not os.path.exists(COMPETITION_DIR):
            raise FileNotFoundError(f"Competition directory not found: {COMPETITION_DIR}")
        
        # Load model
        model_path = os.path.join(COMPETITION_DIR, 'final_competition_model.pkl')
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        model = joblib.load(model_path)
        print(f"✅ Model loaded from: {model_path}")

        # Load scaler
        scaler_path = os.path.join(COMPETITION_DIR, 'competition_scaler.pkl')
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
        scaler = joblib.load(scaler_path)
        print(f"✅ Scaler loaded from: {scaler_path}")

        # Load feature names
        feature_names_path = os.path.join(COMPETITION_DIR, 'feature_names_competition.txt')
        if not os.path.exists(feature_names_path):
            raise FileNotFoundError(f"Feature names file not found: {feature_names_path}")
        with open(feature_names_path, 'r') as f:
            feature_names = [line.strip() for line in f.readlines()]
        print(f"✅ Feature names loaded: {len(feature_names)} features")

        # Load category label encoder
        label_encoder_kategori_path = os.path.join(COMPETITION_DIR, 'label_encoder_kategori.pkl')
        if not os.path.exists(label_encoder_kategori_path):
            raise FileNotFoundError(f"Category label encoder file not found: {label_encoder_kategori_path}")
        label_encoder_kategori = joblib.load(label_encoder_kategori_path)
        print(f"✅ Category label encoder loaded")

        # Load target label encoder
        target_encoder_path = os.path.join(COMPETITION_DIR, 'label_encoder_target.pkl')
        if not os.path.exists(target_encoder_path):
            raise FileNotFoundError(f"Target label encoder file not found: {target_encoder_path}")
        le_target = joblib.load(target_encoder_path)
        print(f"✅ Target label encoder loaded")

        # Load target mapping
        target_mapping_path = os.path.join(COMPETITION_DIR, 'target_mapping.json')
        if not os.path.exists(target_mapping_path):
            raise FileNotFoundError(f"Target mapping file not found: {target_mapping_path}")
        with open(target_mapping_path, 'r') as f:
            target_mapping = json.load(f)
        print(f"✅ Target mapping loaded: {target_mapping}")

        return {
            'model': model,
            'scaler': scaler,
            'feature_names': feature_names,
            'label_encoder_kategori': label_encoder_kategori,
            'le_target': le_target,
            'target_mapping': target_mapping
        }
    except FileNotFoundError as e:
        print(f"\n❌ {str(e)}")
        print("\nPlease make sure all model files exist in the correct location.")
        print(f"Expected model directory: {COMPETITION_DIR}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error loading model components: {str(e)}")
        print("\nThis might be due to incompatible model files or corrupt data.")
        print("Make sure all model files are properly created and compatible with the current environment.")
        sys.exit(1)

def input_location_data(label_encoder_kategori):
    """Collect location data from user input."""
    print("\n=== FnB Business Location Data Input ===")
    
    # Basic demographic data
    print("\n--- Demographic Data ---")
    while True:
        try:
            jumlah_penduduk = float(input("Jumlah Penduduk (total population): "))
            if jumlah_penduduk <= 0:
                print("⚠️  Population must be greater than 0. Please try again.")
                continue
            
            luas_wilayah = float(input("Luas Wilayah (km²): "))
            if luas_wilayah <= 0:
                print("⚠️  Area must be greater than 0. Please try again.")
                continue
                
            kepadatan = jumlah_penduduk / luas_wilayah
            print(f"Calculated Kepadatan (jiwa/km²): {kepadatan:.2f}")
            break
        except ValueError:
            print("⚠️  Please enter valid numbers.")
        except ZeroDivisionError:
            print("⚠️  Area cannot be zero. Please enter a positive number.")
    
    # Local infrastructure
    print("\n--- Local Infrastructure ---")
    while True:
        try:
            jumlah_mall = int(input("Jumlah Mall (number of malls in area): "))
            if jumlah_mall < 0:
                print("⚠️  Number of malls cannot be negative. Please try again.")
                continue
                
            jumlah_minimarket = int(input("Jumlah Minimarket (number of minimarkets): "))
            if jumlah_minimarket < 0:
                print("⚠️  Number of minimarkets cannot be negative. Please try again.")
                continue
                
            jumlah_taman = int(input("Jumlah Taman (number of parks): "))
            if jumlah_taman < 0:
                print("⚠️  Number of parks cannot be negative. Please try again.")
                continue
            break
        except ValueError:
            print("⚠️  Please enter valid whole numbers.")
    
    # Business category
    print("\n--- Business Category ---")
    print("Available restaurant categories:")
    kategori_options = list(label_encoder_kategori.classes_)
    for i, cat in enumerate(kategori_options):
        print(f"{i+1}. {cat}")
        
    while True:
        try:
            kategori_idx = int(input(f"Select restaurant category (1-{len(kategori_options)}): ")) - 1
            if 0 <= kategori_idx < len(kategori_options):
                kategori_resto = kategori_options[kategori_idx]
                break
            else:
                print(f"⚠️  Please enter a number between 1 and {len(kategori_options)}.")
        except ValueError:
            print("⚠️  Please enter a valid number.")
    
    # Price range
    print("\n--- Price Range ---")
    while True:
        try:
            price_range = int(input("Price Range (1=inexpensive to 4=expensive): "))
            if 1 <= price_range <= 4:
                break
            else:
                print("⚠️  Price range must be between 1 and 4. Please try again.")
        except ValueError:
            print("⚠️  Please enter a valid number.")
    
    # Competitor data
    print("\n--- Competitor Data ---")
    while True:
        try:
            jumlah_ulasan = int(input("Average number of reviews for similar businesses in area: "))
            if jumlah_ulasan < 0:
                print("⚠️  Number of reviews cannot be negative. Please try again.")
                continue
                
            google_rating = float(input("Average Google rating for similar businesses (0.0-5.0): "))
            if not (0.0 <= google_rating <= 5.0):
                print("⚠️  Google rating must be between 0.0 and 5.0. Please try again.")
                continue
            break
        except ValueError:
            print("⚠️  Please enter valid numbers.")
    
    # Create data dictionary with all required features
    data = {
        'Jumlah Penduduk': jumlah_penduduk,
        'Luas Wilayah (km²)': luas_wilayah,
        'Kepadatan (jiwa/km²)': kepadatan,
        'jumlah_mall': jumlah_mall,
        'jumlah_minimarket': jumlah_minimarket,
        'jumlah_taman': jumlah_taman,
        'jumlah_ulasan': jumlah_ulasan,
        'google_rating': google_rating,
        'kategori_resto': kategori_resto,
        'price_range': price_range
    }
    
    return data

def preprocess_data(data, components):
    """Preprocess input data to match the model's expected features."""
    # Create derived features
    data['mall_per_capita'] = data['jumlah_mall'] / data['Jumlah Penduduk'] * 1000  # per 1000 residents
    data['minimarket_density'] = data['jumlah_minimarket'] / data['Luas Wilayah (km²)']
    data['taman_per_capita'] = data['jumlah_taman'] / data['Jumlah Penduduk'] * 1000  # per 1000 residents
    data['ulasan_per_capita'] = data['jumlah_ulasan'] / data['Jumlah Penduduk'] * 1000  # per 1000 residents
    
    # Competition and market metrics
    data['competition_density'] = (data['jumlah_mall'] + data['jumlah_minimarket']) / data['Luas Wilayah (km²)']
    data['market_potential'] = data['Jumlah Penduduk'] * (data['google_rating'] / 5)
    data['infrastructure_score'] = (data['jumlah_taman'] + data['jumlah_mall']) / data['Luas Wilayah (km²)']
    data['retail_accessibility'] = data['jumlah_minimarket'] / (data['Jumlah Penduduk'] / 1000)  # per 1000 residents
    
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

def predict_and_visualize(X_scaled, components, input_data):
    """Make prediction and visualize results."""
    model = components['model']
    le_target = components['le_target']
    target_mapping_inv = {v: k for k, v in components['target_mapping'].items()}
    
    # Get prediction probabilities
    probas = model.predict_proba(X_scaled)[0]
    
    # Get predicted class
    predicted_class_idx = np.argmax(probas)
    predicted_class = target_mapping_inv[predicted_class_idx]
    
    # Class names for visualization
    class_names = [target_mapping_inv[i] for i in range(len(probas))]
    
    # Display prediction
    print("\n=== Prediction Results ===")
    print(f"Predicted Business Potential: {predicted_class}")
    print("\nPrediction Probabilities:")
    for i, class_name in enumerate(class_names):
        print(f"- {class_name}: {probas[i]:.2%}")
    
    # Create and save visualization
    plt.figure(figsize=(10, 6))
    
    # Bar chart of probabilities
    bars = plt.bar(class_names, probas, color=['red', 'gold', 'green'])
    plt.title('FnB Business Success Prediction', fontsize=16)
    plt.ylabel('Probability', fontsize=14)
    plt.ylim(0, 1.0)
    
    # Add probability values on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                 f'{height:.2%}', ha='center', fontsize=12)
    
    # Add location info as text
    price_level = ""
    for _ in range(input_data.get('price_range', 0)):
        price_level += "$"
    
    location_info = (
        f"Area: {input_data.get('Luas Wilayah (km²)', 'N/A')} km²\n"
        f"Population: {input_data.get('Jumlah Penduduk', 'N/A'):,.0f}\n"
        f"Density: {input_data.get('Kepadatan (jiwa/km²)', 'N/A'):,.0f} people/km²\n"
        f"Category: {input_data.get('kategori_resto', 'N/A')}\n"
        f"Price Range: {price_level}"
    )
    plt.figtext(0.15, 0.02, location_info, fontsize=12)
    
    # Add recommendation based on prediction
    recommendation = ""
    if predicted_class == "Go":
        recommendation = "✅ RECOMMENDED: High probability of success in this location!"
    elif predicted_class == "Consider":
        recommendation = "⚠️ CONSIDER CAREFULLY: Moderate potential with some risk factors."
    else:  # Avoid
        recommendation = "❌ NOT RECOMMENDED: High risk of business failure in this location."
    
    plt.figtext(0.5, 0.02, recommendation, fontsize=14, ha='center', 
               bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
    
    # Save the figure
    result_file = os.path.join(RESULTS_DIR, 'business_prediction_result.png')
    plt.tight_layout(rect=[0, 0.08, 1, 0.95])  # Adjust layout to make room for text at bottom
    plt.savefig(result_file, dpi=100)
    print(f"\n✅ Prediction visualization saved to: {result_file}")
    
    # Show the plot
    plt.show()

def main():
    """Main function to run the prediction process."""
    print("=" * 60)
    print("   FnB Business Success Predictor based on Strategic Location   ")
    print("=" * 60)
    
    # Load model and components
    components = load_model_and_components()
    label_encoder_kategori = components['label_encoder_kategori']
    
    # Input location data
    input_data = input_location_data(label_encoder_kategori)
    
    # Preprocess data
    X_scaled = preprocess_data(input_data, components)
    
    # Make prediction and visualize
    predict_and_visualize(X_scaled, components, input_data)
    
    print("\nThank you for using the FnB Business Success Predictor!")

if __name__ == "__main__":
    main()
