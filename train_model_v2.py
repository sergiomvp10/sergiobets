"""
Train Improved Model V2 with all features
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
print("TRAINING IMPROVED MODEL V2")
print("=" * 80)
print()

# Load features
print("1. Loading features...")
df = pd.read_csv('historical_matches_features_v2.csv')
print(f"   ✅ {len(df)} matches, {len(df.columns)} columns")
print()

# Clean data
df = df.dropna(subset=['market_prob_home', 'market_prob_draw', 'market_prob_away'])
print(f"   After cleaning: {len(df)} matches")

# Target
df['target'] = df['result'].map({'home': 0, 'draw': 1, 'away': 2})

# Feature columns
feature_cols = [
    'market_prob_home', 'market_prob_draw', 'market_prob_away',
    'elo_home_pre', 'elo_away_pre', 'elo_diff',
    'home_L5_wins', 'home_L5_gf', 'home_L5_ga', 'home_L5_gd',
    'away_L5_wins', 'away_L5_gf', 'away_L5_ga', 'away_L5_gd',
    'home_L10_wins', 'home_L10_gf', 'home_L10_ga', 'home_L10_gd',
    'away_L10_wins', 'away_L10_gf', 'away_L10_ga', 'away_L10_gd',
    'home_rest_days', 'away_rest_days',
    'is_home'
]

# Add league dummies
league_cols = [col for col in df.columns if col.startswith('league_')]
feature_cols.extend(league_cols)

print(f"   Features: {len(feature_cols)}")
print()

# Temporal split
print("2. Temporal split...")
df['date_utc'] = pd.to_datetime(df['date_utc'])

train_df = df[df['date_utc'] < '2024-01-01'].copy()
test_df = df[df['date_utc'] >= '2024-01-01'].copy()

print(f"   Train: {len(train_df)} (pre-2024)")
print(f"   Test: {len(test_df)} (2024+)")
print()

X_train = train_df[feature_cols].values
y_train = train_df['target'].values

X_test = test_df[feature_cols].values
y_test = test_df['target'].values

# Scale
print("3. Scaling...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("   ✅ Done")
print()

# Train
print("4. Training Logistic Regression...")
model = LogisticRegression(
    multi_class='multinomial',
    solver='lbfgs',
    max_iter=1000,
    random_state=42,
    C=1.0
)

model.fit(X_train_scaled, y_train)
print("   ✅ Trained")
print()

# Calibrate
print("5. Calibrating...")
calibrated_model = CalibratedClassifierCV(model, method='isotonic', cv='prefit')
calibrated_model.fit(X_train_scaled, y_train)
print("   ✅ Calibrated")
print()

# Evaluate
print("=" * 80)
print("EVALUATION ON TEST SET (2024+)")
print("=" * 80)
print()

y_pred = calibrated_model.predict(X_test_scaled)
y_pred_proba = calibrated_model.predict_proba(X_test_scaled)

accuracy = accuracy_score(y_test, y_pred)
logloss = log_loss(y_test, y_pred_proba)

brier_scores = []
for i in range(3):
    y_true_binary = (y_test == i).astype(int)
    y_pred_binary = y_pred_proba[:, i]
    brier = np.mean((y_true_binary - y_pred_binary) ** 2)
    brier_scores.append(brier)

avg_brier = np.mean(brier_scores)

print(f"Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"Log Loss: {logloss:.4f}")
print(f"Brier Score: {avg_brier:.4f}")
print()

print("Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Home', 'Draw', 'Away']))
print()

print("Win rate by prediction:")
for i, label in enumerate(['Home', 'Draw', 'Away']):
    mask = y_pred == i
    if mask.sum() > 0:
        wins = (y_test[mask] == i).sum()
        total = mask.sum()
        win_rate = wins / total
        print(f"  {label}: {wins}/{total} = {win_rate:.4f} ({win_rate*100:.2f}%)")
print()

# Compare with market
print("=" * 80)
print("VS MARKET")
print("=" * 80)
print()

market_probs = test_df[['market_prob_home', 'market_prob_draw', 'market_prob_away']].values
market_pred = np.argmax(market_probs, axis=1)

market_accuracy = accuracy_score(y_test, market_pred)
print(f"Market: {market_accuracy:.4f} ({market_accuracy*100:.2f}%)")
print(f"Model: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"Improvement: {(accuracy - market_accuracy)*100:.2f} pp")
print()

# Save
print("6. Saving model...")
joblib.dump(calibrated_model, 'ml_model_v2.pkl')
joblib.dump(scaler, 'ml_scaler_v2.pkl')

with open('ml_features_v2.json', 'w') as f:
    json.dump(feature_cols, f)

print("   ✅ Saved:")
print("      - ml_model_v2.pkl")
print("      - ml_scaler_v2.pkl")
print("      - ml_features_v2.json")
print()

# Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✅ Model V2 trained with {len(feature_cols)} features")
print(f"✅ Test Accuracy: {accuracy*100:.2f}%")
print(f"✅ Log Loss: {logloss:.4f}")
print(f"✅ Brier Score: {avg_brier:.4f}")
print()

if accuracy > 0.60:
    print("🎉 TARGET ACHIEVED! Accuracy > 60%")
elif accuracy > 0.55:
    print("✅ Good progress! Close to 60% target")
    print("   Next: Try XGBoost for further improvement")
else:
    print("⚠️ Need more features or different approach")

print("=" * 80)
