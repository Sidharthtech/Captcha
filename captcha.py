from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import os

app = Flask(__name__)
CORS(app, resources={r"/verify": {"origins": "https://your-vercel-frontend.vercel.app"}})  # Allow only your frontend

# Analyze mouse movements for bot detection
def analyze_movements(movements):
    if len(movements) < 10:
        print("❌ Not enough data to analyze.")
        return False  # Too few movements

    try:
        distances, time_intervals, accelerations = [], [], []

        for i in range(1, len(movements)):
            dx = movements[i]['x'] - movements[i - 1]['x']
            dy = movements[i]['y'] - movements[i - 1]['y']
            distance = np.sqrt(dx**2 + dy**2)
            time_diff = movements[i]['time'] - movements[i - 1]['time']

            distances.append(distance)
            time_intervals.append(time_diff)

            # Calculate acceleration
            if i > 1 and time_diff > 0 and time_intervals[i - 2] > 0:
                prev_speed = distances[i - 2] / time_intervals[i - 2]
                current_speed = distance / time_diff
                acceleration = abs(current_speed - prev_speed) / time_diff
                accelerations.append(acceleration)

        # Ensure lists are not empty before computing stats
        avg_distance = np.mean(distances) if distances else 0
        std_distance = np.std(distances) if distances else 0
        avg_time = np.mean(time_intervals) if time_intervals else 0
        accel_variability = np.std(accelerations) if accelerations else 0

        print(f"👉 Avg Distance: {avg_distance:.4f}, Std Distance: {std_distance:.4f}")
        print(f"👉 Avg Time: {avg_time:.4f}, Accel Variability: {accel_variability:.4f}")

        # Detection Heuristics
        if avg_distance < 1 or std_distance < 0.5 or avg_time < 5:
            print("🚨 Bot detected: Uniform movement.")
            return False

        if accel_variability < 0.01:
            print("🚨 Bot detected: Low acceleration variability.")
            return False

        print("✅ Human detected.")
        return True

    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        return False

@app.route('/verify', methods=['POST'])  # Ensure POST is allowed
def verify():
    try:
        data = request.get_json()

        if not data or 'movements' not in data:
            return jsonify({"error": "No movement data provided"}), 400

        movements = data['movements']
        is_human = analyze_movements(movements)

        return jsonify({"verified": is_human})

    except Exception as e:
        print(f"❌ Error processing request: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Use Render-assigned port
    print(f"🚀 Server running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
