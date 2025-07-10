# 🏪 AI Business Impact Predictor for F&B in Bandung

Sistem AI untuk memprediksi tingkat kesuksesan dan mengambil keputusan bisnis sebelum membuka restoran/usaha F&B di Kota Bandung. Menggunakan **Competition Model** yang dilatih dengan ensemble learning untuk memberikan rekomendasi **Go**, **Consider**, atau **Avoid**.

## 🎯 Fitur Utama

### 1. **Competition Model Prediction**
- **Go**: Sangat direkomendasikan untuk membuka usaha (🟢)
- **Consider**: Perlu pertimbangan lebih lanjut dengan analisis mendalam (🟡)
- **Avoid**: Tidak direkomendasikan untuk membuka usaha (🔴)

### 2. **Analisis Komprehensif**
- **Risk Assessment**: Penilaian tingkat risiko bisnis
- **Investment Analysis**: Evaluasi potensi investasi dan estimasi ROI
- **Market Potential**: Analisis potensi pasar berdasarkan demografis
- **Competition Analysis**: Evaluasi tingkat kompetisi di area target

### 3. **Visualisasi & Reporting**
- Dashboard interaktif dengan grafik dan chart
- Laporan bisnis dalam format Markdown dan Excel
- Perbandingan multiple skenario lokasi
- Export hasil dalam berbagai format

## 📊 Model Performance

- **Best Model**: [To be filled after running model_development.ipynb]
- **Test R² Score**: [To be determined]
- **Test RMSE**: [To be determined]
- **Features Used**: 13+ demographic and market features

## 🗂️ Project Structure

```
ai-business-impact-predictor/
├── datasets/                     # Training and processed datasets
│   ├── final_training_dataset.csv
│   ├── cleaned_data_*.csv
│   └── ...
├── EDA/                          # Exploratory Data Analysis notebooks
│   ├── data_understanding.ipynb  # Data exploration and visualization
│   ├── model_development.ipynb   # ML model training and evaluation
│   ├── risk_assessment.ipynb     # Risk scoring system
│   ├── index.ipynb              # Data preprocessing
│   └── main.ipynb               # Business understanding
├── models/                       # Trained models and artifacts
│   ├── best_model.pkl           # Best performing model
│   ├── scaler.pkl               # Feature scaler
│   └── feature_names.txt        # Feature names for prediction
├── results/                      # Analysis results and visualizations
│   ├── *.png                    # Generated plots and charts
│   ├── *.csv                    # Analysis results
│   └── *.txt                    # Reports and guides
├── predict.py                    # Deployment script for predictions
├── predict_fnb_business_success.py # Script untuk prediksi cepat sukses bisnis F&B
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-business-impact-predictor
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
.venv\\Scripts\\activate  # On Windows
# source .venv/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Jupyter Notebooks
```bash
jupyter notebook
```

## 📈 Usage

### For Data Scientists & Developers

1. **Data Understanding**: Open `EDA/data_understanding.ipynb`
2. **Model Development**: Run `EDA/model_development.ipynb`
3. **Risk Assessment**: Execute `EDA/risk_assessment.ipynb`

### Quick Prediction with Competition Model

Run the dedicated prediction script for strategic location analysis:

```bash
python predict_fnb_business_success.py
```

This interactive script will guide you through entering location data and will generate a prediction with visualization.

### For Business Users

Use the deployment script for quick predictions:

```python
from predict import BusinessImpactPredictor

# Initialize predictor
predictor = BusinessImpactPredictor(
    model_path='models/best_model.pkl',
    scaler_path='models/scaler.pkl', 
    features_path='models/feature_names.txt'
)

# Assess a location
location_data = {
    'jumlah_penduduk': 75000,
    'luas_wilayah': 12.0,
    'kepadatan_jiwa': 6250,
    'jumlah_fnb': 25,
    'jumlah_taman': 8,
    'avg_price': 35000,
    'jumlah_shopping_place': 8,
    'jumlah_universitas': 1
}

result = predictor.assess_location(location_data)
print(f"Expected Rating: {result['predicted_rating']}/5.0")
print(f"Risk Level: {result['risk_category']}")
```

## 📋 Input Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `jumlah_penduduk` | Population count | 75000 |
| `luas_wilayah` | Area in km² | 12.0 |
| `kepadatan_jiwa` | Population density (people/km²) | 6250 |
| `jumlah_fnb` | Number of existing F&B businesses | 25 |
| `jumlah_taman` | Number of parks | 8 |
| `avg_price` | Average F&B price (Rupiah) | 35000 |
| `jumlah_shopping_place` | Number of shopping centers | 8 |
| `jumlah_universitas` | Number of universities | 1 |

## 🎯 Risk Scoring System

- **🟢 LOW RISK (0.0-0.3)**: Favorable conditions for F&B business
- **🟡 MEDIUM RISK (0.3-0.6)**: Moderate challenges, manageable with good strategy
- **🔴 HIGH RISK (0.6-1.0)**: Significant challenges, consider alternative locations

## 📊 Key Features Analyzed

1. **Demographic Factors**
   - Population size and density
   - Economic indicators (price levels)

2. **Market Competition**
   - F&B saturation (businesses per capita)
   - Competition density (businesses per km²)

3. **Infrastructure & Amenities**
   - Parks and recreational facilities
   - Shopping centers
   - Educational institutions

## 🔍 Next Steps for Development

### ✅ Completed:
- [x] Data collection and preprocessing
- [x] Exploratory data analysis
- [x] Feature engineering
- [x] Basic model framework

### 🚧 To Do:
- [ ] Execute model training (run `model_development.ipynb`)
- [ ] Complete risk assessment system (run `risk_assessment.ipynb`)
- [ ] Model hyperparameter tuning
- [ ] Web dashboard development
- [ ] API deployment
- [ ] Real-time data integration

### 🎯 Future Enhancements:
- [ ] Integration with real-time traffic data
- [ ] Social media sentiment analysis
- [ ] Economic indicator integration
- [ ] Mobile app development
- [ ] Automated model retraining pipeline

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

[Specify your license here]

## 👥 Team

- **Data Scientist**: [Your Name]
- **Domain Expert**: F&B Industry Specialist
- **Technical Lead**: [Your Name]

## 📞 Support

For questions or issues, please contact:
- Email: [your-email@domain.com]
- Issues: [GitHub Issues URL]

---

**Note**: This project is specifically designed for the Bandung F&B market. Adaptation may be required for other cities or industries.
