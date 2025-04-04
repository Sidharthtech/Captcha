# Real-Time CAPTCHA Using Mouse Movements 🖱️🧠

This project is a real-time CAPTCHA system that verifies human users by analyzing their mouse movements — no puzzles or images, just natural behavior.

## 🔐 How It Works

The system evaluates the authenticity of user interaction based on:

- Mouse movement paths
- Angular changes in movement (non-linear = human-like)
- Timing and activity detection (e.g., inactivity delay)
- Heuristic checks for bot-like patterns

If the user is verified as human, they are allowed to proceed. If behavior is too linear or inactive, verification fails temporarily.

## ✨ Features

- 🔍 Detects linear mouse movement as bot-like behavior
- ⏱️ Temporarily disables verification if movement seems automated
- 🧠 No need for backend or third-party CAPTCHA providers
- 🌙 Stylish dark mode with animated feedback
