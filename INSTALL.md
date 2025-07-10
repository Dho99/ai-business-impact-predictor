# AI Business Impact Predictor - Installation Guide

## Python Version
**Current Environment**: Compatible with current .venv
**Recommended**: Python 3.10+ 
**Tested**: Works with current environment setup

## Quick Setup

### 1. Aktivasi Virtual Environment
```bash
# Jika sudah ada .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify Installation
```bash
python -c "import pandas, numpy, sklearn, xgboost, lightgbm, matplotlib, seaborn, googlemaps, tqdm, scipy; print('✅ All packages installed successfully')"
```

### 4. Start Jupyter
```bash
jupyter notebook
```

## Package Versions (Based on Current Environment)

### Core ML Pipeline:
- **pandas**: 2.3.0+ - Data manipulation dan analisis
- **numpy**: 2.3.0+ - Numerical computing
- **scikit-learn**: 1.7.0+ - Machine learning framework
- **xgboost**: 3.0.0+ - Gradient boosting (model utama)
- **lightgbm**: 4.6.0+ - Fast gradient boosting (ensemble)
- **joblib**: 1.5.0+ - Model serialization

### Data Visualization:
- **matplotlib**: 3.10.0+ - Basic plotting
- **seaborn**: 0.13.0+ - Statistical visualization
- **scipy**: 1.16.0+ - Scientific computing

### Development Environment:
- **jupyter**: 1.1.0+ - Notebook environment
- **notebook**: 7.4.0+ - Jupyter notebook server
- **ipykernel**: 6.29.0+ - Jupyter kernel
- **jupyterlab**: 4.4.0+ - Modern Jupyter interface

### External Services:
- **googlemaps**: 4.10.0+ - Google Maps API integration
- **tqdm**: 4.67.0+ - Progress bars untuk batch processing

### Built-in Python Modules (No Installation Needed):
- **pathlib** - Path manipulation
- **json** - JSON handling
- **os** - Operating system interface
- **sys** - System parameters
- **time** - Time functions
- **datetime** - Date and time
- **warnings** - Warning control

## Actual Project Usage Analysis

Based on code analysis, the project uses:

### Core Files:
- `predict_fnb_business_success.py`: Uses joblib, numpy, pandas, pathlib, matplotlib, sklearn.preprocessing, xgboost, lightgbm, json, os, sys
- `analyze_restaurant_dataset.py`: Uses pandas, numpy, matplotlib, seaborn
- `get_address_taman_full.py`: Uses pandas, googlemaps, time, tqdm, numpy, os, datetime
- `get_rating_API.py`: Uses os, pandas, googlemaps, datetime, time, tqdm

### Notebooks:
- `new_training_with_google_maps_data.ipynb`: Full ML pipeline with sklearn, xgboost, lightgbm, ensemble methods
- `restourant.ipynb`: Advanced ML with GridSearchCV, RandomForestRegressor, preprocessing
- `main.ipynb`: Data processing with googlemaps API integration

## Notes
- Semua package telah dianalisis dari actual usage di project
- Versi disesuaikan dengan environment yang sudah working
- Requirements minimal tapi lengkap untuk semua functionality
- Built-in Python modules tidak perlu diinstall
