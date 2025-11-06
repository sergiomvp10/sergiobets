"""
Train BTTS and Over/Under 2.5 models
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import log_loss, accuracy_score, classification_report
from sklearn.calibration import CalibratedClassifierCV
import joblib
import json

print("=" * 80)
print("TRAINING BTTS AND OVER/UNDER 2.5 MODELS")
print("=" * 80)
print()

# Load features
print("1. Loading features...")
df = pd.read_csv('historical_matches_features_v2.csv')
print(f"   ✅ {len(df)} matches")

# Clean data
df = df.dropna(subset=['market_prob_home', 'market_prob_draw', 'market_prob_away'])
print(f"   After cleaning: {len(df)}")

# Create targets
print()
print("2. Creating targets...")

# BTTS target: both teams scored
df['btts'] = ((df['goals_home'] > 0) & (df['goals_away'] > 0)).astype(int)
print(f"   BTTS: {df['btts'].sum()} yes ({df['btts'].mean():.1%}), {(~df['btts'].astype(bool)).sum()} no")

# Over/Under 2.5 target
df['over25'] = ((df['goals_home'] + df['goals_away']) > 2.5).astype(int)
print(f"   O/U 2.5: {df['over25'].sum()} over ({df['over25'].mean():.1%}), {(~df['over25'].astype(bool)).sum()} under")

# Features - emphasize goals for/against for these markets
feature_cols = [
    'market_prob_home', 'market_prob_draw', 'market_prob_away',
    'elo_home_pre', 'elo_away_pre', 'elo_diff',
    'home_L5_gf', 'home_L5_ga', 'home_L5_gd',
    'away_L5_gf', 'away_L5_ga', 'away_L5_gd',
    'home_L10_gf', 'home_L10_ga', 'home_L10_gd',
    'away_L10_gf', 'away_L10_ga', 'away_L10_gd',
    'home_rest_days', 'away_rest_days',
    'is_home'
]

league_cols = [col for col in df.columns if col.startswith('league_')]
feature_cols.extend(league_cols)

print(f"   Features: {len(feature_cols)}")

# Temporal split
print()
print("3. Temporal split...")
df['date_utc'] = pd.to_datetime(df['date_utc'])

train_df = df[df['date_utc'] < '2024-01-01'].copy()
test_df = df[df['date_utc'] >= '2024-01-01'].copy()

print(f"   Train: {len(train_df)}")
print(f"   Test: {len(test_df)}")

X_train = train_df[feature_cols].values
X_test = test_df[feature_cols].values

# Scale
print()
print("4. Scaling...")
scaler_btts = StandardScaler()
scaler_ou = StandardScaler()

X_train_scaled_btts = scaler_btts.fit_transform(X_train)
X_test_scaled_btts = scaler_btts.transform(X_test)

X_train_scaled_ou = scaler_ou.fit_transform(X_train)
X_test_scaled_ou = scaler_ou.transform(X_test)

print("   ✅ Done")

# Train BTTS model
print()
print("=" * 80)
print("BTTS MODEL")
print("=" * 80)

y_train_btts = train_df['btts'].values
y_test_btts = test_df['btts'].values

model_btts = LogisticRegression(
    random_state=42,
    max_iter=1000,
    C=1.0
)

model_btts.fit(X_train_scaled_btts, y_train_btts)
print("✅ Trained")

# Calibrate
calibrated_btts = CalibratedClassifierCV(model_btts, method='isotonic', cv='prefit')
calibrated_btts.fit(X_train_scaled_btts, y_train_btts)
print("✅ Calibrated")

# Evaluate
y_pred_btts = calibrated_btts.predict(X_test_scaled_btts)
y_pred_proba_btts = calibrated_btts.predict_proba(X_test_scaled_btts)

accuracy_btts = accuracy_score(y_test_btts, y_pred_btts)
logloss_btts = log_loss(y_test_btts, y_pred_proba_btts)

print()
print(f"Accuracy: {accuracy_btts:.4f} ({accuracy_btts*100:.2f}%)")
print(f"Log Loss: {logloss_btts:.4f}")
print()
print("Classification Report:")
print(classification_report(y_test_btts, y_pred_btts, target_names=['No BTTS', 'BTTS']))

# Train Over/Under model
print()
print("=" * 80)
print("OVER/UNDER 2.5 MODEL")
print("=" * 80)

y_train_ou = train_df['over25'].values
y_test_ou = test_df['over25'].values

model_ou = LogisticRegression(
    random_state=42,
    max_iter=1000,
    C=1.0
)

model_ou.fit(X_train_scaled_ou, y_train_ou)
print("✅ Trained")

# Calibrate
calibrated_ou = CalibratedClassifierCV(model_ou, method='isotonic', cv='prefit')
calibrated_ou.fit(X_train_scaled_ou, y_train_ou)
print("✅ Calibrated")

# Evaluate
y_pred_ou = calibrated_ou.predict(X_test_scaled_ou)
y_pred_proba_ou = calibrated_ou.predict_proba(X_test_scaled_ou)

accuracy_ou = accuracy_score(y_test_ou, y_pred_ou)
logloss_ou = log_loss(y_test_ou, y_pred_proba_ou)

print()
print(f"Accuracy: {accuracy_ou:.4f} ({accuracy_ou*100:.2f}%)")
print(f"Log Loss: {logloss_ou:.4f}")
print()
print("Classification Report:")
print(classification_report(y_test_ou, y_pred_ou, target_names=['Under 2.5', 'Over 2.5']))

# Save models
print()
print("5. Saving models...")

joblib.dump(calibrated_btts, 'ml_model_btts.pkl')
joblib.dump(scaler_btts, 'ml_scaler_btts.pkl')

joblib.dump(calibrated_ou, 'ml_model_ou25.pkl')
joblib.dump(scaler_ou, 'ml_scaler_ou25.pkl')

with open('ml_features_btts_ou.json', 'w') as f:
    json.dump(feature_cols, f)

print("   ✅ Saved:")
print("      - ml_model_btts.pkl")
print("      - ml_scaler_btts.pkl")
print("      - ml_model_ou25.pkl")
print("      - ml_scaler_ou25.pkl")
print("      - ml_features_btts_ou.json")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✅ BTTS Model: {accuracy_btts*100:.2f}% accuracy")
print(f"✅ O/U 2.5 Model: {accuracy_ou*100:.2f}% accuracy")
print("=" * 80)
