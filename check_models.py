#!/usr/bin/env python3
"""Check what models are available in PhishGuard"""

import pickle
import os

models_dir = "/Users/matthewscott/Projects/Security-Tools/security-phishing-detector/models"

# Load and inspect the models
try:
    with open(f"{models_dir}/phishing_clf.pkl", 'rb') as f:
        clf = pickle.load(f)
        print(f"Main classifier type: {type(clf)}")
        print(f"Model: {clf}")

    with open(f"{models_dir}/model_metadata.pkl", 'rb') as f:
        metadata = pickle.load(f)
        print(f"\nMetadata: {metadata}")

    with open(f"{models_dir}/tfidf_vec.pkl", 'rb') as f:
        vec = pickle.load(f)
        print(f"\nVectorizer type: {type(vec)}")

except Exception as e:
    print(f"Error loading models: {e}")

print("\n=== Available Models ===")
for file in os.listdir(models_dir):
    if file.endswith(('.pkl', '.joblib', '.h5', '.pt', '.pth')):
        size = os.path.getsize(f"{models_dir}/{file}") / 1024
        print(f"  {file}: {size:.1f} KB")