"""
====================================================
  AI Diabetes Detection System — Model Training
  SVM with GridSearchCV, Pipeline, Cross-Validation
====================================================
Run this ONCE to train and save the model:
    python model_training.py
"""

import numpy as np
import pandas as pd
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import (
    train_test_split, GridSearchCV, StratifiedKFold, cross_val_score
)
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, roc_auc_score
)

# ─────────────────────────────────────────────────────
# 1.  LOAD DATA
# ─────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "PimaIndiansDiabetes.csv")

print("=" * 60)
print("  AI DIABETES DETECTION — SVM MODEL TRAINING")
print("=" * 60)

df = pd.read_csv(DATA_PATH)
print(f"\n✅ Dataset loaded: {df.shape[0]} rows × {df.shape[1]} cols")
print(df.head(3).to_string())

# ─────────────────────────────────────────────────────
# 2.  PREPROCESSING
# ─────────────────────────────────────────────────────
# Medical columns that CANNOT be 0 — replace with median
zero_not_valid = ['GlucoseConcentration', 'BloodPrs', 'SkinThickness', 'Serum', 'BMI']

for col in zero_not_valid:
    # Count zeros before
    n_zeros = (df[col] == 0).sum()
    if n_zeros > 0:
        median_val = df[col][df[col] != 0].median()
        df[col] = df[col].replace(0, median_val)
        print(f"   Fixed {n_zeros} zero(s) in '{col}' → median={median_val:.2f}")

print(f"\n✅ Preprocessing done. Missing values: {df.isnull().sum().sum()}")

# ─────────────────────────────────────────────────────
# 3.  FEATURE / TARGET SPLIT
# ─────────────────────────────────────────────────────
FEATURES = ['TimesPregnant', 'GlucoseConcentration', 'BloodPrs',
            'SkinThickness', 'Serum', 'BMI', 'DiabetesFunct', 'Age']
TARGET   = 'Class'

X = df[FEATURES]
y = df[TARGET]

print(f"\n✅ Class distribution:\n{y.value_counts().to_string()}")

# ─────────────────────────────────────────────────────
# 4.  TRAIN / TEST SPLIT  (stratified)
# ─────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"\n✅ Train={len(X_train)}  Test={len(X_test)}")

# ─────────────────────────────────────────────────────
# 5.  PIPELINE  (Scaler → SVM)
# ─────────────────────────────────────────────────────
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('svm',    SVC(probability=True, random_state=42))
])

# ─────────────────────────────────────────────────────
# 6.  HYPERPARAMETER GRID
# ─────────────────────────────────────────────────────
param_grid = [
    # RBF kernel — usually best for tabular medical data
    {'svm__kernel': ['rbf'],
     'svm__C':      [0.1, 1, 10, 100],
     'svm__gamma':  ['scale', 'auto', 0.01, 0.001]},

    # Linear kernel — good when classes are linearly separable
    {'svm__kernel': ['linear'],
     'svm__C':      [0.01, 0.1, 1, 10]},

    # Polynomial kernel
    {'svm__kernel': ['poly'],
     'svm__C':      [0.1, 1, 10],
     'svm__degree': [2, 3],
     'svm__gamma':  ['scale', 'auto']},
]

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

print("\n🔍 Running GridSearchCV (this may take ~30 s)…")
grid_search = GridSearchCV(
    pipeline, param_grid,
    cv=cv, scoring='accuracy',
    n_jobs=-1, verbose=1
)
grid_search.fit(X_train, y_train)

# ─────────────────────────────────────────────────────
# 7.  BEST MODEL EVALUATION
# ─────────────────────────────────────────────────────
best_model = grid_search.best_estimator_
print(f"\n✅ Best params: {grid_search.best_params_}")
print(f"✅ Best CV accuracy: {grid_search.best_score_*100:.2f}%")

y_pred = best_model.predict(X_test)
test_acc = accuracy_score(y_test, y_pred)

print(f"\n{'='*50}")
print(f"  TEST ACCURACY  : {test_acc*100:.2f}%")
print(f"  ROC-AUC SCORE  : {roc_auc_score(y_test, best_model.predict_proba(X_test)[:,1])*100:.2f}%")
print(f"{'='*50}")
print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred, target_names=['No Diabetes','Diabetes']))

# Cross-validation scores on full dataset
cv_scores = cross_val_score(best_model, X, y, cv=cv, scoring='accuracy')
print(f"\n📊 5-Fold CV Accuracy: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")

# ─────────────────────────────────────────────────────
# 8.  SAVE MODEL WITH PICKLE
# ─────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "diabetes_model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "scaler.pkl")

# Save full pipeline (scaler + svm)
with open(MODEL_PATH, 'wb') as f:
    pickle.dump(best_model, f)

# Save standalone scaler for easy access
with open(SCALER_PATH, 'wb') as f:
    pickle.dump(best_model.named_steps['scaler'], f)

# Save training metadata
meta = {
    'features': FEATURES,
    'test_accuracy': round(test_acc * 100, 2),
    'cv_accuracy': round(cv_scores.mean() * 100, 2),
    'cv_std': round(cv_scores.std() * 100, 2),
    'best_params': grid_search.best_params_,
    'class_names': ['No Diabetes', 'Diabetes'],
    'train_size': len(X_train),
    'test_size': len(X_test),
}
with open(os.path.join(os.path.dirname(__file__), "model_meta.pkl"), 'wb') as f:
    pickle.dump(meta, f)

print(f"\n✅ Model saved  → {MODEL_PATH}")
print(f"✅ Metadata saved → model_meta.pkl")
print("\n🎉 Training complete! Run  streamlit run app.py  to launch the app.")