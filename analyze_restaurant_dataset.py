import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
df = pd.read_csv('datasets/restaurant_dataset_cleaned.csv')

print("=== ANALISIS DATASET RESTAURANT UNTUK PROJECT AI BUSINESS IMPACT PREDICTOR ===")
print()

# 1. Basic Information
print("1. INFORMASI DASAR DATASET")
print("-" * 50)
print(f"Jumlah baris: {len(df):,}")
print(f"Jumlah kolom: {len(df.columns)}")
print(f"Ukuran dataset: {df.shape}")
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
print()

# 2. Data Quality Assessment
print("2. KUALITAS DATA")
print("-" * 50)
print("Missing values per kolom:")
missing_data = df.isnull().sum()
missing_percentage = (missing_data / len(df) * 100).round(2)
for col in df.columns:
    if missing_data[col] > 0:
        print(f"  {col}: {missing_data[col]:,} ({missing_percentage[col]}%)")
    else:
        print(f"  {col}: Complete ✓")
print()

# 3. Target Variable Analysis (google_rating)
print("3. ANALISIS TARGET VARIABLE (google_rating)")
print("-" * 50)
valid_ratings = df['google_rating'].dropna()
print(f"Data rating yang valid: {len(valid_ratings):,} dari {len(df):,} ({len(valid_ratings)/len(df)*100:.1f}%)")
print(f"Range rating: {valid_ratings.min():.1f} - {valid_ratings.max():.1f}")
print(f"Mean rating: {valid_ratings.mean():.2f}")
print(f"Median rating: {valid_ratings.median():.2f}")
print(f"Standard deviation: {valid_ratings.std():.2f}")
print()

# Rating distribution
rating_dist = valid_ratings.value_counts().sort_index()
print("Distribusi rating:")
for rating, count in rating_dist.head(10).items():
    print(f"  {rating:.1f}: {count:,} restoran ({count/len(valid_ratings)*100:.1f}%)")
print()

# 4. Feature Analysis
print("4. ANALISIS FITUR PREDIKTIF")
print("-" * 50)

# Demographic features
demographic_features = ['Jumlah Penduduk', 'Luas Wilayah (km²)', 'Kepadatan (jiwa/km²)']
print("Fitur Demografis:")
for feature in demographic_features:
    if feature in df.columns:
        values = df[feature].dropna()
        print(f"  {feature}:")
        print(f"    Range: {values.min():.2f} - {values.max():.2f}")
        print(f"    Mean: {values.mean():.2f}")
        print(f"    Unique values: {values.nunique()}")
print()

# Business environment features
business_features = ['jumlah_mall', 'jumlah_minimarket', 'jumlah_taman']
print("Fitur Lingkungan Bisnis:")
for feature in business_features:
    if feature in df.columns:
        values = df[feature].dropna()
        print(f"  {feature}:")
        print(f"    Range: {values.min():.2f} - {values.max():.2f}")
        print(f"    Mean: {values.mean():.2f}")
        print(f"    Unique values: {values.nunique()}")
print()

# 5. Geographic Coverage
print("5. CAKUPAN GEOGRAFIS")
print("-" * 50)
kecamatan_stats = df['kecamatan'].value_counts()
print(f"Total kecamatan: {df['kecamatan'].nunique()}")
print(f"Kecamatan dengan restoran terbanyak:")
for kec, count in kecamatan_stats.head(5).items():
    print(f"  {kec}: {count:,} restoran")
print()
print(f"Kecamatan dengan restoran tersedikit:")
for kec, count in kecamatan_stats.tail(5).items():
    print(f"  {kec}: {count:,} restoran")
print()

# 6. Business Status Analysis
print("6. ANALISIS STATUS BISNIS")
print("-" * 50)
business_status = df['business_status'].value_counts()
for status, count in business_status.items():
    print(f"  {status}: {count:,} ({count/len(df)*100:.1f}%)")
print()

# 7. Price Range Analysis
print("7. ANALISIS RENTANG HARGA")
print("-" * 50)
price_data = df['price_range_rupiah'].dropna()
print(f"Data harga tersedia: {len(price_data):,} dari {len(df):,} ({len(price_data)/len(df)*100:.1f}%)")
if len(price_data) > 0:
    price_dist = price_data.value_counts()
    print("Distribusi rentang harga:")
    for price, count in price_dist.head(5).items():
        print(f"  {price}: {count:,} ({count/len(price_data)*100:.1f}%)")
print()

# 8. Correlation Analysis
print("8. ANALISIS KORELASI DENGAN TARGET")
print("-" * 50)
numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
if 'google_rating' in numeric_columns:
    correlations = df[numeric_columns].corr()['google_rating'].abs().sort_values(ascending=False)
    print("Korelasi absolut dengan google_rating:")
    for feature, corr in correlations.items():
        if feature != 'google_rating' and not pd.isna(corr):
            print(f"  {feature}: {corr:.3f}")
print()

# 9. Data Usefulness Assessment
print("9. PENILAIAN KEGUNAAN DATA UNTUK PROJECT")
print("-" * 50)

usefulness_score = 0
max_score = 10

# Check target variable quality
if df['google_rating'].notna().sum() / len(df) >= 0.7:
    usefulness_score += 3
    print("✓ Target variable (rating) coverage: BAIK (≥70%)")
else:
    usefulness_score += 1
    print("⚠ Target variable (rating) coverage: KURANG (<70%)")

# Check feature diversity
if len(numeric_columns) >= 5:
    usefulness_score += 2
    print("✓ Feature diversity: BAIK (≥5 numeric features)")
else:
    usefulness_score += 1
    print("⚠ Feature diversity: CUKUP (<5 numeric features)")

# Check geographic coverage
if df['kecamatan'].nunique() >= 15:
    usefulness_score += 2
    print("✓ Geographic coverage: BAIK (≥15 kecamatan)")
else:
    usefulness_score += 1
    print("⚠ Geographic coverage: TERBATAS (<15 kecamatan)")

# Check sample size
if len(df) >= 1000:
    usefulness_score += 2
    print("✓ Sample size: SANGAT BAIK (≥1000 samples)")
elif len(df) >= 500:
    usefulness_score += 1
    print("✓ Sample size: BAIK (≥500 samples)")
else:
    print("⚠ Sample size: KURANG (<500 samples)")

# Check data completeness
completeness = (df.notna().sum().sum() / (len(df) * len(df.columns))) * 100
if completeness >= 80:
    usefulness_score += 1
    print(f"✓ Data completeness: BAIK ({completeness:.1f}%)")
else:
    print(f"⚠ Data completeness: KURANG ({completeness:.1f}%)")

print()
print(f"SKOR KEGUNAAN: {usefulness_score}/{max_score}")

if usefulness_score >= 8:
    recommendation = "SANGAT BERGUNA - Dataset ini sangat cocok untuk project AI business impact predictor"
elif usefulness_score >= 6:
    recommendation = "BERGUNA - Dataset ini dapat digunakan dengan beberapa penyesuaian"
elif usefulness_score >= 4:
    recommendation = "CUKUP BERGUNA - Perlu preprocessing tambahan dan feature engineering"
else:
    recommendation = "KURANG BERGUNA - Perlu perbaikan signifikan atau data tambahan"

print(f"REKOMENDASI: {recommendation}")

print()
print("10. REKOMENDASI PENGGUNAAN")
print("-" * 50)
print("Untuk project AI Business Impact Predictor, dataset ini dapat digunakan untuk:")
print("• Prediksi rating restoran berdasarkan lokasi dan lingkungan bisnis")
print("• Analisis dampak fasilitas publik (mall, minimarket, taman) terhadap performa bisnis")
print("• Identifikasi lokasi optimal untuk membuka restoran baru")
print("• Analisis kompetisi restoran per kecamatan")
print()
print("Perbaikan yang disarankan:")
print("• Lengkapi data price_range yang masih banyak missing")
print("• Tambahkan fitur seperti kategori makanan, jam operasi, fasilitas")
print("• Normalisasi data rating untuk mengatasi outlier")
print("• Feature engineering untuk membuat fitur kompetisi dan density")
