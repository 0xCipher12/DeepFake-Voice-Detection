import librosa
import numpy as np
import os
import joblib
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings('ignore')

# -------------------------------
# Advanced Feature Extraction (More Professional)
# -------------------------------
def extract_features(file_path):
    """Extract advanced audio features for deepfake detection"""
    try:
        audio, sample_rate = librosa.load(file_path, sr=None, duration=30)  # Max 30 seconds
        
        # 1. MFCC (13 coefficients)
        mfcc = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
        mfcc_mean = np.mean(mfcc.T, axis=0)
        mfcc_std = np.std(mfcc.T, axis=0)
        
        # 2. Chroma Features
        chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
        chroma_mean = np.mean(chroma.T, axis=0)
        
        # 3. Mel Spectrogram
        mel = librosa.feature.melspectrogram(y=audio, sr=sample_rate)
        mel_mean = np.mean(mel.T, axis=0)
        mel_std = np.std(mel.T, axis=0)
        
        # 4. Zero Crossing Rate
        zcr = librosa.feature.zero_crossing_rate(audio)
        zcr_mean = np.mean(zcr)
        zcr_std = np.std(zcr)
        
        # 5. Spectral Centroid
        centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)
        centroid_mean = np.mean(centroid)
        centroid_std = np.std(centroid)
        
        # 6. Spectral Bandwidth
        bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate)
        bandwidth_mean = np.mean(bandwidth)
        bandwidth_std = np.std(bandwidth)
        
        # 7. Spectral Rolloff
        rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sample_rate)
        rolloff_mean = np.mean(rolloff)
        
        # 8. RMS Energy
        rms = librosa.feature.rms(y=audio)
        rms_mean = np.mean(rms)
        rms_std = np.std(rms)
        
        # Combine all features
        features = np.hstack([
            mfcc_mean, mfcc_std,
            chroma_mean,
            mel_mean[:5], mel_std[:5],  # Take first 5 to avoid overfitting
            zcr_mean, zcr_std,
            centroid_mean, centroid_std,
            bandwidth_mean, bandwidth_std,
            rolloff_mean,
            rms_mean, rms_std
        ])
        
        return features
        
    except Exception as e:
        print(f"Error extracting features from {file_path}: {e}")
        # Return dummy features if error
        return np.zeros(13 + 13 + 12 + 5 + 5 + 2 + 2 + 2 + 2 + 1 + 2)

# -------------------------------
# Load or Train Model
# -------------------------------
def load_or_train_model():
    """Load pre-trained model or train if not exists"""
    model_path = "voice_model.pkl"
    scaler_path = "scaler.pkl"
    
    # Check if model exists
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        print("Loading pre-trained model...")
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        return model, scaler
    
    print("Training new model...")
    
    # Check if dataset exists
    if not os.path.exists("dataset/real") or not os.path.exists("dataset/fake"):
        print("⚠️ Dataset not found! Using fallback mode.")
        print("Create folders: dataset/real/ and dataset/fake/ with audio files")
        # Return dummy model for development
        return None, None
    
    X = []
    y = []
    
    # Load REAL voices (0)
    real_files = os.listdir("dataset/real")
    print(f"Loading {len(real_files)} REAL samples...")
    for file in real_files:
        if file.endswith(('.wav', '.mp3', '.m4a')):
            path = os.path.join("dataset/real", file)
            features = extract_features(path)
            X.append(features)
            y.append(0)
    
    # Load FAKE voices (1)
    fake_files = os.listdir("dataset/fake")
    print(f"Loading {len(fake_files)} FAKE samples...")
    for file in fake_files:
        if file.endswith(('.wav', '.mp3', '.m4a')):
            path = os.path.join("dataset/fake", file)
            features = extract_features(path)
            X.append(features)
            y.append(1)
    
    if len(X) == 0:
        print("❌ No audio files found in dataset folders!")
        return None, None
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"Total samples: {len(X)} | Features: {X.shape[1]}")
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Random Forest (better than SVM for this task)
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_scaled, y)
    
    # Save model
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    print("✅ Model trained and saved successfully!")
    
    return model, scaler

# -------------------------------
# Global Model Load
# -------------------------------
print("🎤 Initializing Voice Deepfake Detector...")
model, scaler = load_or_train_model()

# -------------------------------
# Prediction Function
# -------------------------------
def predict_voice(file_path):
    """
    Predict if voice is REAL or FAKE
    Returns: (prediction_string, confidence_array)
    """
    if model is None or scaler is None:
        # Fallback for demo
        return "DEMO MODE", [[0.5, 0.5]]
    
    try:
        features = extract_features(file_path)
        features = scaler.transform([features])
        
        prediction = model.predict(features)
        confidence = model.predict_proba(features)
        
        if prediction[0] == 0:
            result = "REAL VOICE"
        else:
            result = "FAKE VOICE"
        
        return result, confidence
        
    except Exception as e:
        print(f"Prediction error: {e}")
        return "ERROR", [[0.5, 0.5]]

# -------------------------------
# Test Function
# -------------------------------
if __name__ == "__main__":
    # Test with a sample file
    test_file = "dataset/real/real1.wav" if os.path.exists("dataset/real/real1.wav") else None
    
    if test_file and os.path.exists(test_file):
        result, confidence = predict_voice(test_file)
        print(f"\n🔍 Test Result: {result}")
        print(f"📊 Confidence: REAL={confidence[0][0]:.2%} | FAKE={confidence[0][1]:.2%}")
    else:
        print("\n⚠️ No test file found. Place test audio in dataset/real/ or dataset/fake/")
        print("Current directory:", os.getcwd())