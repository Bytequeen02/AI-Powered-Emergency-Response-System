'''import streamlit as st
from utils import load_emergency_model, detect_emergency, get_current_location, send_whatsapp, send_email, find_nearby
import os
import speech_recognition as sr
import pyttsx3
import math

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the distance in kilometers between two latitude/longitude points using the Haversine formula.
    """
    R = 6371  # Earth radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(R * c, 2)

st.set_page_config(page_title="Emergency Detection System", layout="centered")
st.title("🚨 Emergency Detection System")

model, vectorizer = load_emergency_model()

col1, col2 = st.columns(2)

with col1:
    text_input = st.text_area("✍️ Type your SOS here:")

with col2:
    if st.button("🎤 Use Microphone"):
        st.info("🎙️ Listening... Please speak.")
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                st.success("Transcription complete.")
                text_input = recognizer.recognize_google(audio)
                st.chat_message("user").write(f"🗣️ {text_input}")
            except sr.WaitTimeoutError:
                st.warning("⏱️ Listening timed out. Please try again.")
            except sr.UnknownValueError:
                st.warning("🛑 Could not understand audio.")
            except sr.RequestError:
                st.error("❌ Could not request results from Google Speech Recognition.")

EMERGENCY_GUIDE = {
    "fire": {
        "Precautions": [
            "Evacuate immediately using stairs.",
            "Avoid elevators and stay low to avoid smoke.",
            "Cover nose and mouth with a cloth."
        ],
        "Do's": [
            "Use a fire extinguisher if the fire is small.",
            "Call the fire department (Dial 101)."
        ],
        "Don'ts": [
            "Don’t open hot doors.",
            "Don’t hide in small spaces.",
            "Don’t use water on electrical fires."
        ]
    },
    "medical": {
        "Precautions": [
            "Keep the injured person still and calm.",
            "Check for responsiveness and breathing.",
            "Apply pressure to bleeding wounds."
        ],
        "Do's": [
            "Call emergency medical help (Dial 102).",
            "Give CPR if trained and needed."
        ],
        "Don'ts": [
            "Don’t move the person unnecessarily.",
            "Don’t give food or drink."
        ]
    },
    "accident": {
        "Precautions": [
            "Secure the area to avoid further accidents.",
            "Do not crowd around the victim.",
            "Call ambulance immediately."
        ],
        "Do's": [
            "Turn on hazard lights if on the road.",
            "Help with basic first aid."
        ],
        "Don'ts": [
            "Don’t move the injured unless essential.",
            "Don’t delay calling for help."
        ]
    },
    "violence": {
        "Precautions": [
            "Find a safe space or hide.",
            "Avoid confronting the attacker.",
            "Stay quiet and alert."
        ],
        "Do's": [
            "Call police (Dial 100).",
            "Record details if safe."
        ],
        "Don'ts": [
            "Don’t scream unless it will bring help.",
            "Don’t intervene directly if unsafe."
        ]
    },
}
# Emergency Detection Logic
if text_input:
    category = detect_emergency(text_input, model, vectorizer)
    st.success(f"🆘 Emergency Detected: **{category.upper()}**")

    # Show precautions
    if category in EMERGENCY_GUIDE:
        guide = EMERGENCY_GUIDE[category]
        with st.expander("📋 Precautions and Emergency Guide", expanded=True):
            st.markdown("### ⚠️ Precautions")
            for p in guide["Precautions"]:
                st.markdown(f"- {p}")
        
            st.markdown("### ✅ Do's")
            for d in guide["Do's"]:
                st.markdown(f"- {d}")
        
            st.markdown("### ❌ Don'ts")
            for n in guide["Don'ts"]:
                st.markdown(f"- {n}")
    
lat, lon, city = get_current_location()

import folium
from streamlit_folium import st_folium

# Show user location on a map
st.subheader("📍 Your Current Location")
location_map = folium.Map(location=[lat, lon], zoom_start=15)
folium.Marker([lat, lon], tooltip="You are here", popup=city).add_to(location_map)
st_data = st_folium(location_map, width=700, height=400)

# Shareable OpenStreetMap link
map_link = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}"
st.markdown(f"🔗 [Share Location on OpenStreetMap]({map_link})")   

# Nearby Hospitals Section
if st.button("🏥 Show Nearby Hospitals"):
    hospitals = find_nearby(lat, lon, place_type="hospital")
    st.subheader("Nearby Hospitals with Contact & Distance")
    for h in hospitals:
        name = h.get('display_name', 'Unknown')
        contact = h.get('contact:phone', 'N/A')
        try:
            lat2 = float(h.get('lat'))
            lon2 = float(h.get('lon'))
            distance = haversine(lat, lon, lat2, lon2)
        except (TypeError, ValueError):
            distance = "Unknown"
        st.markdown(f"**🏥 {name}**\n- 📞 Phone: {contact}\n- 📏 Distance: {distance} km")
    
# Nearby Police Stations Section
if st.button("🚓 Show Nearby Police Stations"):
    police_stations = find_nearby(lat, lon, place_type="police")
    st.subheader("Nearby Police Stations with Contact & Distance")
    for p in police_stations:
        name = p.get('display_name', 'Unknown')
        contact = p.get('contact:phone', 'N/A')
        try:
            lat2 = float(p.get('lat'))
            lon2 = float(p.get('lon'))
            distance = haversine(lat, lon, lat2, lon2)
        except (TypeError, ValueError):
            distance = "Unknown"
        st.markdown(f"**🚓 {name}**\n- 📞 Phone: {contact}\n- 📏 Distance: {distance} km")

if st.button("📱 Notify Contacts"):
    # Format the emergency message with full location info
    maps_link = f"https://www.google.com/maps?q={lat},{lon}"
    msg = (
        f"🚨 EMERGENCY ALERT 🚨\n"
        f"Type: {category.upper()}\n"
        f"Location: {city}\n"
        f"Coordinates: Latitude {lat}, Longitude {lon}\n"
        f"Google Maps: {maps_link}\n"
        f"⚠️ Immediate assistance required!"
    )

    st.write("Sending Email...")
    if send_email("EMERGENCY ALERT!", msg):
        st.success("✅ Email sent.")
    else:
        st.error("❌ Failed to send email.")

    st.write("Sending WhatsApp message...")
    if send_whatsapp(msg):
        st.success("✅ WhatsApp message sent.")
    else:
        st.warning("⚠️ WhatsApp failed (check Twilio setup).")

if st.button("🏥 Suggest Nearby Help"):
    service_type = "hospital" if category == "medical" else "police"
    results = find_nearby(lat, lon, service_type)
    for r in results[:3]:
        st.write(f"🏥 {r['name']} - {r['vicinity']}")'''




