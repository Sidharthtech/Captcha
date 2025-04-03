from flask import Flask, request, jsonify, redirect, session
from flask_cors import CORS
import numpy as np
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key_here")

# Allow only requests from your frontend (update with your actual domain)
CORS(app, resources={r"/*": {"origins": "https://portfolio-website-jet-delta-49.vercel.app"}})

# Default redirect URL (your portfolio website)
DEFAULT_REDIRECT_URL = "https://portfolio-website-jet-delta-49.vercel.app"

# Function to analyze mouse movement and detect bots
def analyze_movements(movements):
    if len(movements) < 10:
        print("❌ Not enough data to analyze.")
        return False

    distances, time_intervals, accelerations = [], [], []

    for i in range(1, len(movements)):
        dx = movements[i]['x'] - movements[i - 1]['x']
        dy = movements[i]['y'] - movements[i - 1]['y']
        distance = np.sqrt(dx**2 + dy**2)
        time_diff = movements[i]['time'] - movements[i - 1]['time']
        if time_diff <= 0:
            continue

        distances.append(distance)
        time_intervals.append(time_diff)

        if i > 1:
            prev_speed = distances[i - 2] / time_intervals[i - 2] if time_intervals[i - 2] > 0 else 0
            current_speed = distance / time_diff
            acceleration = abs(current_speed - prev_speed) / time_diff
            accelerations.append(acceleration)

    avg_distance = np.mean(distances) if distances else 0
    std_distance = np.std(distances) if distances else 0
    avg_time = np.mean(time_intervals) if time_intervals else 0
    accel_variability = np.std(accelerations) if accelerations else 0

    # Heuristic detection logic
    if avg_distance < 1 or std_distance < 0.5 or avg_time < 5:
        print("🚨 Bot detected: Uniform movement.")
        return False

    if accel_variability < 0.01:
        print("🚨 Bot detected: Low acceleration variability.")
        return False

    print("✅ Human verified.")
    return True

@app.route('/verify', methods=['POST'])
def verify():
    try:
        data = request.get_json()
        movements = data.get('movements', [])

        if not movements:
            return jsonify({"error": "No movement data provided"}), 400

        print(f"🔍 Received {len(movements)} movement data points for verification.")

        is_human = analyze_movements(movements)

        if is_human:
            session['verified'] = True
            return jsonify({"verified": True, "redirect": DEFAULT_REDIRECT_URL})
        else:
            return jsonify({"verified": False})

    except Exception as e:
        print(f"❌ Error processing request: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/redirect')
def handle_redirect():
    if session.get('verified'):
        session.pop('verified', None)  # Clear session
        return redirect(DEFAULT_REDIRECT_URL)  # Redirect to portfolio
    return "❌ Verification required.", 403

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  
    print(f"🚀 CAPTCHA server running on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
