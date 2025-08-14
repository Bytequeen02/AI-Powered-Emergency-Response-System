# 🚨 AI-Powered Emergency Response System

[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![Machine Learning](https://img.shields.io/badge/ML-Powered-brightgreen?logo=tensorflow)]()
[![Status](https://img.shields.io/badge/Status-Active-success)]()

An **AI-driven, real-time emergency response system** that detects emergencies from **text-based SOS** or **voice input** and immediately alerts emergency contacts.  
It also provides **live location sharing**, **nearest hospital/police station suggestions**, and an **interactive, dashboard-style UI** for quick response.

---

## 🌟 Features

- 🎙 **Voice & Text Emergency Detection** – Detect emergencies via microphone input or manual SOS messages.
- 📍 **Real-Time Location Sharing** – Share your live location instantly without paid APIs.
- 🏥 **Nearest Help Suggestions** – Locate nearby hospitals and police stations.
- 💬 **Live Chat-Style Emergency Box** – Includes emojis and precautionary info for clarity.
- 🎨 **Beautiful, Animated UI** – Smooth transitions and dashboard-style layout using Streamlit.
- 🤝 **Multi-Contact Alerts** – Notify multiple emergency contacts via **SMS** or **Email**.

---

## 🛠️ Tech Stack

| Component       | Technology |
|-----------------|------------|
| Frontend UI     | Streamlit  |
| Backend Logic   | Python     |
| ML/NLP          | Scikit-learn / Custom Models |
| Location        | OpenStreetMap API / Geopy |
| Alerts          | SMTP (Email), Twilio/Other APIs (SMS) |
| Visualization   | Streamlit Components & Animations |

---

## 📸 Screenshots

> _Add screenshots of your app in action for better visual appeal._

| Dashboard View | Emergency Location Map |
|----------------|------------------------|
| ![Dashboard](<img width="1331" height="601" alt="Screenshot 2025-08-14 153614" src="https://github.com/user-attachments/assets/41b9f345-4479-42a4-bc95-056bb312cc4d" />
) | ![Location](<img width="1291" height="618" alt="Screenshot 2025-08-14 154110" src="https://github.com/user-attachments/assets/10164097-d3df-4df8-abf8-cba3753c9c40" />
)

---

## 🚀 Getting Started

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/emergency-response-system.git
cd emergency-response-system
# AI Emergency Response System
This is an AI-powered emergency response system built using Streamlit, Python, ML, and Openstreetmam link.

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Run the application
streamlit run app.py

⚙️ Environment Variables

Before running, create a .env file in the root directory with:

EMAIL_USER=your_email@example.com
EMAIL_PASS=your_email_password
SMS_API_KEY=your_twilio_api_key

💡 How It Works

User Input – The system receives a text SOS or listens for emergency keywords from the mic.

Emergency Detection – AI model analyzes the input to confirm urgency.

Location Fetching – User’s location is fetched using free geolocation services.

Help Suggestions – Nearest hospitals and police stations are retrieved.

Alert Dispatch – Emergency contacts are notified via email/SMS with location details.

Real-Time UI – Interactive dashboard updates the emergency status live.

📌 Roadmap

 Add multilingual voice recognition.

 Integrate offline emergency detection.

 Add wearable device integration for auto-alerts.

 Enhance location tracking with live movement.

🤝 Contributing

Contributions are welcome!

Fork the repo 🍴

Create a branch (feature-new-idea)

Commit your changes and push 🚀

Open a Pull Request

📜 License

This project is licensed under the MIT License – see the LICENSE file for details.

🙌 Acknowledgements

Streamlit

Geopy

OpenStreetMap

Twilio

“Every second counts in an emergency — this system is built to make those seconds count for life.”
