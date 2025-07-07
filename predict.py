"""
AI Business Impact Predictor - Deployment Script
Provides a simple API interface for the trained model
"""

import pandas as pd
import numpy as np
import joblib
import json
from typing import Dict, Any, List
import warnings
warnings.filterwarnings('ignore')

class BusinessImpactPredictor:
    def __init__(self, model_path: str, scaler_path: str, features_path: str):
        """
        Initialize the predictor with trained model, scaler, and feature names
        """
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        
        # Load feature names
        with open(features_path, 'r') as f:
            self.feature_names = [line.strip() for line in f.readlines()]
    
    def predict_rating(self, location_data: Dict[str, float]) -> float:
        """
        Predict business rating for given location data
        """
        # Ensure all required features are present
        features = []
        for feature in self.feature_names:
            if feature in location_data:
                features.append(location_data[feature])
            else:
                # Use default values for missing features
                features.append(0.0)
        
        # Convert to numpy array
        features = np.array(features).reshape(1, -1)
        
        # Make prediction (handle both scaled and unscaled models)
        try:
            # Try scaled prediction first
            features_scaled = self.scaler.transform(features)
            prediction = self.model.predict(features_scaled)[0]
        except:
            # Fall back to unscaled prediction
            prediction = self.model.predict(features)[0]
        
        return float(prediction)
    
    def calculate_risk_score(self, predicted_rating: float, 
                           market_saturation: float, 
                           competition_density: float) -> float:
        """
        Calculate comprehensive risk score
        """
        # Base risk from predicted rating (inverse relationship)
        rating_risk = (5.0 - predicted_rating) / 4.0
        
        # Market saturation risk
        saturation_risk = min(market_saturation * 1000, 1.0)
        
        # Competition density risk
        competition_risk = min(competition_density / 10, 1.0)
        
        # Weighted composite risk score
        composite_risk = (
            0.5 * rating_risk +      # 50% weight on predicted performance
            0.3 * saturation_risk +  # 30% weight on market saturation
            0.2 * competition_risk   # 20% weight on competition density
        )
        
        return min(composite_risk, 1.0)
    
    def get_risk_category(self, risk_score: float) -> tuple:
        """
        Categorize risk level
        """
        if risk_score <= 0.3:
            return "LOW RISK", "🟢"
        elif risk_score <= 0.6:
            return "MEDIUM RISK", "🟡"
        else:
            return "HIGH RISK", "🔴"
    
    def assess_location(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete location assessment
        """
        # Extract basic location data
        jumlah_penduduk = input_data.get('jumlah_penduduk', 50000)
        luas_wilayah = input_data.get('luas_wilayah', 10.0)
        kepadatan_jiwa = input_data.get('kepadatan_jiwa', 5000)
        jumlah_fnb = input_data.get('jumlah_fnb', 20)
        jumlah_taman = input_data.get('jumlah_taman', 3)
        avg_price = input_data.get('avg_price', 35000)
        jumlah_shopping_place = input_data.get('jumlah_shopping_place', 5)
        jumlah_universitas = input_data.get('jumlah_universitas', 1)
        
        # Calculate derived features
        location_features = {
            'Jumlah Penduduk': jumlah_penduduk,
            'Luas Wilayah': luas_wilayah,
            'Kepadatan Jiwa': kepadatan_jiwa,
            'jumlah_fnb': jumlah_fnb,
            'jumlah_taman': jumlah_taman,
            'avg_price': avg_price,
            'jumlah_shopping_place': jumlah_shopping_place,
            'jumlah_universitas': jumlah_universitas,
            'fnb_per_capita': jumlah_fnb / jumlah_penduduk,
            'fnb_per_km2': jumlah_fnb / luas_wilayah,
            'taman_per_capita': jumlah_taman / jumlah_penduduk,
            'jumlah_penduduk_usia_produktif': jumlah_penduduk * 0.65,
            'penduduk_produktif_ratio': 0.65
        }
        
        # Get prediction
        predicted_rating = self.predict_rating(location_features)
        
        # Calculate risk score
        risk_score = self.calculate_risk_score(
            predicted_rating,
            location_features['fnb_per_capita'],
            location_features['fnb_per_km2']
        )
        
        # Get risk category
        risk_category, risk_emoji = self.get_risk_category(risk_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_score, predicted_rating, location_features
        )
        
        return {
            'predicted_rating': round(predicted_rating, 2),
            'risk_score': round(risk_score, 3),
            'risk_category': risk_category,
            'risk_emoji': risk_emoji,
            'recommendations': recommendations,
            'market_analysis': {
                'fnb_per_1000_people': round(location_features['fnb_per_capita'] * 1000, 2),
                'fnb_density_per_km2': round(location_features['fnb_per_km2'], 2),
                'parks_per_1000_people': round(location_features['taman_per_capita'] * 1000, 2)
            },
            'location_summary': {
                'population': jumlah_penduduk,
                'area_km2': luas_wilayah,
                'population_density': kepadatan_jiwa,
                'existing_fnb': jumlah_fnb,
                'parks': jumlah_taman,
                'avg_price': avg_price
            }
        }
    
    def _generate_recommendations(self, risk_score: float, 
                                predicted_rating: float, 
                                location_data: Dict[str, float]) -> List[str]:
        """
        Generate business recommendations
        """
        recommendations = []
        
        # Rating-based recommendations
        if predicted_rating < 3.5:
            recommendations.append("Focus on exceptional food quality and service")
            recommendations.append("Consider unique value proposition to stand out")
        
        # Market saturation recommendations
        if location_data.get('fnb_per_capita', 0) > 0.001:
            recommendations.append("Differentiate with specialized cuisine or concept")
            recommendations.append("Implement competitive pricing strategy")
        
        # Competition density recommendations
        if location_data.get('fnb_per_km2', 0) > 5:
            recommendations.append("Invest in strong marketing and branding")
            recommendations.append("Focus on exceptional customer experience")
        
        # Population-based recommendations
        if location_data.get('Jumlah Penduduk', 0) < 50000:
            recommendations.append("Target tourists or office workers")
            recommendations.append("Host events to attract customers from nearby areas")
        
        # Risk-based recommendations
        if risk_score > 0.6:
            recommendations.append("Consider alternative locations or business models")
            recommendations.append("Ensure strong financial reserves for initial period")
        elif risk_score < 0.3:
            recommendations.append("Good location fundamentals - focus on execution")
            recommendations.append("Monitor market trends for expansion opportunities")
        
        return recommendations

def main():
    """
    Example usage of the predictor
    """
    # Initialize predictor
    try:
        predictor = BusinessImpactPredictor(
            model_path='models/best_model.pkl',
            scaler_path='models/scaler.pkl',
            features_path='models/feature_names.txt'
        )
        print("✅ AI Business Impact Predictor loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading predictor: {e}")
        return
    
    # Example location assessment
    example_location = {
        'jumlah_penduduk': 85000,
        'luas_wilayah': 12.5,
        'kepadatan_jiwa': 6800,
        'jumlah_fnb': 35,
        'jumlah_taman': 6,
        'avg_price': 40000,
        'jumlah_shopping_place': 8,
        'jumlah_universitas': 2
    }
    
    # Perform assessment
    result = predictor.assess_location(example_location)
    
    # Display results
    print("\\n" + "="*60)
    print("🏪 AI BUSINESS IMPACT PREDICTION REPORT")
    print("="*60)
    
    print(f"📍 Location Summary:")
    summary = result['location_summary']
    print(f"   Population: {summary['population']:,}")
    print(f"   Area: {summary['area_km2']:.1f} km²")
    print(f"   Population Density: {summary['population_density']:,} people/km²")
    print(f"   Existing F&B: {summary['existing_fnb']}")
    print(f"   Parks: {summary['parks']}")
    print(f"   Average Price: Rp {summary['avg_price']:,}")
    
    print(f"\\n📊 Market Analysis:")
    market = result['market_analysis']
    print(f"   F&B per 1000 people: {market['fnb_per_1000_people']}")
    print(f"   F&B density: {market['fnb_density_per_km2']:.2f} per km²")
    print(f"   Parks per 1000 people: {market['parks_per_1000_people']}")
    
    print(f"\\n🎯 AI Predictions:")
    print(f"   Expected Rating: {result['predicted_rating']}/5.0 ⭐")
    print(f"   Risk Score: {result['risk_score']}")
    print(f"   Risk Level: {result['risk_emoji']} {result['risk_category']}")
    
    print(f"\\n💡 Recommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    print("="*60)
    
    # Save result as JSON
    with open('assessment_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("\\n📁 Assessment result saved to 'assessment_result.json'")

if __name__ == "__main__":
    main()
