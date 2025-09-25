#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sample Data Generator for FnB Business Success Predictor

This module contains predefined sample datasets for different business scenarios
that demonstrate various prediction outcomes (Go, Consider, Avoid).
"""

def get_sample_datasets():
    """
    Returns a dictionary of sample datasets for different business scenarios.
    
    Returns:
        dict: Dictionary containing sample datasets with their descriptions
    """
    
    samples = {
        'go_urban_center': {
            'name': 'GO - Urban Center',
            'description': 'High-density urban area with excellent infrastructure and strong market indicators',
            'expected_outcome': 'Go',
            'data': {
                'Jumlah Penduduk': 150000,
                'Luas Wilayah (km²)': 8.5,
                'Kepadatan (jiwa/km²)': 17647,  # Auto-calculated
                'jumlah_mall': 4,
                'jumlah_minimarket': 25,
                'jumlah_taman': 8,
                'jumlah_ulasan': 200,
                'google_rating': 4.5,
                'kategori_resto': 'Restaurant',
                'price_range': 2
            }
        },
        
        'go_premium_district': {
            'name': 'GO - Premium District',
            'description': 'High-end area with premium positioning potential',
            'expected_outcome': 'Go',
            'data': {
                'Jumlah Penduduk': 200000,
                'Luas Wilayah (km²)': 5.0,
                'Kepadatan (jiwa/km²)': 40000,  # Auto-calculated
                'jumlah_mall': 6,
                'jumlah_minimarket': 40,
                'jumlah_taman': 10,
                'jumlah_ulasan': 300,
                'google_rating': 4.3,
                'kategori_resto': 'Cafe',
                'price_range': 3
            }
        },
        
        'consider_suburban': {
            'name': 'CONSIDER - Suburban Area',
            'description': 'Moderate population with limited infrastructure and average market conditions',
            'expected_outcome': 'Consider',
            'data': {
                'Jumlah Penduduk': 75000,
                'Luas Wilayah (km²)': 12.0,
                'Kepadatan (jiwa/km²)': 6250,  # Auto-calculated
                'jumlah_mall': 1,
                'jumlah_minimarket': 10,
                'jumlah_taman': 3,
                'jumlah_ulasan': 80,
                'google_rating': 3.8,
                'kategori_resto': 'Fast food',
                'price_range': 1
            }
        },
        
        'consider_family_area': {
            'name': 'CONSIDER - Family Area',
            'description': 'Suburban family-oriented area with moderate infrastructure',
            'expected_outcome': 'Consider',
            'data': {
                'Jumlah Penduduk': 90000,
                'Luas Wilayah (km²)': 18.0,
                'Kepadatan (jiwa/km²)': 5000,  # Auto-calculated
                'jumlah_mall': 2,
                'jumlah_minimarket': 12,
                'jumlah_taman': 6,
                'jumlah_ulasan': 120,
                'google_rating': 4.0,
                'kategori_resto': 'Family restaurant',
                'price_range': 2
            }
        },
        
        'consider_tourist': {
            'name': 'CONSIDER - Tourist Area',
            'description': 'Tourist destination with seasonal variations and moderate risk',
            'expected_outcome': 'Consider',
            'data': {
                'Jumlah Penduduk': 65000,
                'Luas Wilayah (km²)': 8.0,
                'Kepadatan (jiwa/km²)': 8125,  # Auto-calculated
                'jumlah_mall': 3,
                'jumlah_minimarket': 20,
                'jumlah_taman': 12,
                'jumlah_ulasan': 180,
                'google_rating': 4.1,
                'kategori_resto': 'Seafood',
                'price_range': 3
            }
        },
        
        'avoid_low_density': {
            'name': 'AVOID - Low Density Rural',
            'description': 'Low-density area with poor infrastructure and weak market indicators',
            'expected_outcome': 'Avoid',
            'data': {
                'Jumlah Penduduk': 35000,
                'Luas Wilayah (km²)': 15.0,
                'Kepadatan (jiwa/km²)': 2333,  # Auto-calculated
                'jumlah_mall': 0,
                'jumlah_minimarket': 3,
                'jumlah_taman': 1,
                'jumlah_ulasan': 25,
                'google_rating': 3.2,
                'kategori_resto': 'Fine dining',
                'price_range': 4
            }
        },
        
        'avoid_industrial': {
            'name': 'AVOID - Industrial Zone',
            'description': 'Industrial area with working-class demographics and limited leisure spending',
            'expected_outcome': 'Avoid',
            'data': {
                'Jumlah Penduduk': 45000,
                'Luas Wilayah (km²)': 25.0,
                'Kepadatan (jiwa/km²)': 1800,  # Auto-calculated
                'jumlah_mall': 1,
                'jumlah_minimarket': 8,
                'jumlah_taman': 2,
                'jumlah_ulasan': 60,
                'google_rating': 3.5,
                'kategori_resto': 'Fast food',
                'price_range': 1
            }
        },
        
        'avoid_oversaturated': {
            'name': 'AVOID - Oversaturated Market',
            'description': 'High competition area with declining market conditions',
            'expected_outcome': 'Avoid',
            'data': {
                'Jumlah Penduduk': 80000,
                'Luas Wilayah (km²)': 10.0,
                'Kepadatan (jiwa/km²)': 8000,  # Auto-calculated
                'jumlah_mall': 2,
                'jumlah_minimarket': 15,
                'jumlah_taman': 4,
                'jumlah_ulasan': 50,
                'google_rating': 3.0,
                'kategori_resto': 'Restaurant',
                'price_range': 3
            }
        }
    }
    
    # Auto-calculate density for all samples
    for sample_key, sample_data in samples.items():
        data = sample_data['data']
        data['Kepadatan (jiwa/km²)'] = data['Jumlah Penduduk'] / data['Luas Wilayah (km²)']
    
    return samples

def display_sample_info(sample_key):
    """
    Display detailed information about a specific sample dataset.
    
    Args:
        sample_key (str): Key of the sample dataset
    """
    samples = get_sample_datasets()
    
    if sample_key not in samples:
        print(f"❌ Sample '{sample_key}' not found.")
        return
    
    sample = samples[sample_key]
    data = sample['data']
    
    print(f"\n{'='*60}")
    print(f"   {sample['name']}")
    print(f"{'='*60}")
    print(f"Description: {sample['description']}")
    print(f"Expected Outcome: {sample['expected_outcome']}")
    print(f"\nLocation Details:")
    print(f"- Population: {data['Jumlah Penduduk']:,} people")
    print(f"- Area: {data['Luas Wilayah (km²)']} km²")
    print(f"- Density: {data['Kepadatan (jiwa/km²)']:,.0f} people/km²")
    print(f"\nInfrastructure:")
    print(f"- Malls: {data['jumlah_mall']}")
    print(f"- Minimarkets: {data['jumlah_minimarket']}")
    print(f"- Parks: {data['jumlah_taman']}")
    print(f"\nBusiness Profile:")
    print(f"- Category: {data['kategori_resto']}")
    print(f"- Price Range: {'$' * data['price_range']}")
    print(f"\nMarket Conditions:")
    print(f"- Average Reviews: {data['jumlah_ulasan']}")
    print(f"- Average Rating: {data['google_rating']}/5.0")

def list_all_samples():
    """List all available sample datasets with brief descriptions."""
    samples = get_sample_datasets()
    
    print("\n📋 Available Sample Datasets:")
    print("="*80)
    
    # Group by expected outcome
    outcomes = ['Go', 'Consider', 'Avoid']
    
    for outcome in outcomes:
        outcome_samples = {k: v for k, v in samples.items() if v['expected_outcome'] == outcome}
        
        if outcome == 'Go':
            print(f"\n✅ {outcome.upper()} Scenarios (Recommended):")
        elif outcome == 'Consider':
            print(f"\n⚠️  {outcome.upper()} Scenarios (Moderate Risk):")
        else:
            print(f"\n❌ {outcome.upper()} Scenarios (High Risk):")
        
        for i, (key, sample) in enumerate(outcome_samples.items(), 1):
            print(f"   {i}. {sample['name']}")
            print(f"      {sample['description']}")
            print(f"      Key: '{key}'")
            print()

if __name__ == "__main__":
    # Demo the sample data
    print("FnB Business Success Predictor - Sample Datasets")
    list_all_samples()
    
    print("\n" + "="*80)
    print("Example usage:")
    print("from sample_datasets import get_sample_datasets")
    print("samples = get_sample_datasets()")
    print("go_sample = samples['go_urban_center']['data']")