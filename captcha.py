from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

app = Flask(__name__)
CORS(app)  # Allow requests from any origin (for Live Server compatibility)

# Function to analyze mouse movements and detect "bot-like" patterns
def analyze_movements(movements):
    if len(movements) < 10:
        print("❌ Not enough data to analyze.")
        return False  # Not enough data for analysis

    # Calculate distances, time intervals, and acceleration
    distances = []
    time_intervals = []
    accelerations = []

    for i in range(1, len(movements)):
        dx = movements[i]['x'] - movements[i - 1]['x']
        dy = movements[i]['y'] - movements[i - 1]['y']
        distance = np.sqrt(dx**2 + dy**2)

        time_diff = movements[i]['time'] - movements[i - 1]['time']

        distances.append(distance)
        time_intervals.append(time_diff)

        # Calculate acceleration (rate of change in speed)
        if i > 1 and time_diff > 0:
            prev_speed = distances[i - 2] / time_intervals[i - 2]
            current_speed = distance / time_diff
            acceleration = abs(current_speed - prev_speed) / time_diff
            accelerations.append(acceleration)

    # Statistical checks to identify "bot-like" behavior
    avg_distance = np.mean(distances)
    std_distance = np.std(distances)
    avg_time = np.mean(time_intervals)
    accel_variability = np.std(accelerations) if accelerations else 0

    print(f"👉 Avg Distance: {avg_distance}, Std Distance: {std_distance}")
    print(f"👉 Avg Time: {avg_time}, Accel Variability: {accel_variability}")

    # Heuristic: Bots often show low variability in movement and timing
    if avg_distance < 1 or std_distance < 0.5 or avg_time < 5:
        print("🚨 Bot detected: Uniform movement.")
        return False  # Likely a bot

    # Low acceleration variability suggests automated input
    if accel_variability < 0.01:
        print("🚨 Bot detected: Low acceleration variability.")
        return False

    print("✅ Human detected.")
    return True  # Likely a human

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

if __name__ == '__main__':
    print("🚀 Starting CAPTCHA verification server...")
    app.run(debug=True)
