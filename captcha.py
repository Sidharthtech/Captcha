from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

app = Flask(_name_)
CORS(app)  # Allow requests from any origin

# Generate synthetic training data (this should be replaced with real data)
def generate_training_data():
    np.random.seed(42)
    num_samples = 500
    
    human_data = np.random.normal(loc=[10, 50, 0.2], scale=[5, 20, 0.1], size=(num_samples, 3))
    bot_data = np.random.normal(loc=[1, 5, 0.01], scale=[0.5, 2, 0.005], size=(num_samples, 3))
    
    X = np.vstack((human_data, bot_data))
    y = np.array([1] * num_samples + [0] * num_samples)  # 1 for human, 0 for bot
    
    return X, y

# Train the Random Forest model
X, y = generate_training_data()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train_scaled, y_train)

def analyze_movements(movements):
    if len(movements) < 10:
        print("❌ Not enough data to analyze.")
        return False

    distances = []
    time_intervals = []
    accelerations = []

    for i in range(1, len(movements)):
        dx = movements[i]['x'] - movements[i - 1]['x']
        dy = movements[i]['y'] - movements[i - 1]['y']
        distance = np.sqrt(dx*2 + dy*2)
        time_diff = movements[i]['time'] - movements[i - 1]['time']
        distances.append(distance)
        time_intervals.append(time_diff)

        if i > 1 and time_diff > 0:
            prev_speed = distances[i - 2] / time_intervals[i - 2]
            current_speed = distance / time_diff
            acceleration = abs(current_speed - prev_speed) / time_diff
            accelerations.append(acceleration)

    avg_distance = np.mean(distances)
    avg_time = np.mean(time_intervals)
    accel_variability = np.std(accelerations) if accelerations else 0
    
    input_features = np.array([[avg_distance, avg_time, accel_variability]])
    input_scaled = scaler.transform(input_features)
    prediction = rf_model.predict(input_scaled)
    
    return bool(prediction[0])

@app.route('/verify', methods=['POST'])
def verify():
    try:
        data = request.get_json()
        movements = data.get('movements', [])

        if not movements:
            return jsonify({"error": "No movement data provided"}), 400

        is_human = analyze_movements(movements)
        return jsonify({"verified": is_human})
    except Exception as e:
        print(f"❌ Error processing request: {e}")
        return jsonify({"error": "Internal server error"}), 500

if _name_ == '_main_':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting CAPTCHA verification server on port:", port)
    app.run(host='0.0.0.0', port=port, debug=True)
