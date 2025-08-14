import streamlit as st # type: ignore
from utils import load_emergency_model, detect_emergency, get_current_location, send_whatsapp, send_email, find_nearby
import os
import speech_recognition as sr 
import pyttsx3 
import math
import folium # type: ignore
from streamlit_folium import st_folium # type: ignore
# --- Haversine function ---
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

# ----- Streamlit Page Configuration -----
st.set_page_config(
    page_title="🚨 Emergency Assistant",
    layout="wide", # 'wide' layout is great for maps and larger elements
    initial_sidebar_state="collapsed" # Starts collapsed, user can expand
)

# ----- Custom CSS Styling -----
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    /* General body and text styling */
    html, body, [class*="stApp"] {
        font-family: 'Inter', sans-serif; /* Use Inter font */
        background-color: #0d1117; /* Even darker background for more contrast */
        color: #e6edf3; /* Lighter text for readability */
    }
    
    /* Main Streamlit container */
    .stApp {
        background-color: #0d1117;
        /* Removed the overall app glow effect */
    }

    /* Primary button styling */
    .stButton>button {
        background-color: #e3405f; /* A more vibrant red */
        color: white;
        border-radius: 12px; /* Slightly more rounded */
        padding: 12px; /* Slightly more padding */
        font-weight: 600; /* Medium bold */
        width: 100%;
        border: none;
        box-shadow: 0 6px 12px rgba(227, 64, 95, 0.4); /* More prominent shadow with red tint */
        transition: all 0.3s ease-in-out; /* Smooth transition for all properties */
        transform: translateY(0); /* Initial state for transform */
    }
    .stButton>button:hover {
        background-color: #ff5c7c; /* Lighter red on hover */
        box-shadow: 0 8px 16px rgba(227, 64, 95, 0.6); /* Increased shadow on hover */
        transform: translateY(-3px); /* Slight lift effect */
    }
    .stButton>button:active {
        transform: translateY(0); /* Reset on click */
        box-shadow: 0 4px 8px rgba(227, 64, 95, 0.3);
    }

    /* Text area styling */
    .stTextArea textarea {
        background-color: #161b22; /* Darker input field */
        color: #e6edf3;
        border: 2px solid #e3405f; /* Vibrant red border */
        border-radius: 12px;
        padding: 15px; /* More padding */
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.6); /* Inner shadow for depth */
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .stTextArea textarea:focus {
        border-color: #ff5c7c; /* Brighter red on focus */
        box-shadow: 0 0 0 3px rgba(227, 64, 95, 0.3); /* Outer glow on focus */
        outline: none; /* Remove default outline */
    }
    /* Placeholder text color for the text area */
    .stTextArea textarea::placeholder {
        color: #e6edf3; /* Set placeholder text to white */
        opacity: 0.6; /* Make it slightly transparent to distinguish from actual input */
    }
    /* Label for the text area */
    .stTextArea label {
        color: #e6edf3; /* Set the label text to white */
        font-weight: 600;
        font-size: 1.1em;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 28px; /* More space between tabs */
        justify-content: center; /* Center the tabs */
        margin-bottom: 30px; /* More space below tabs */
    }

    .stTabs [data-baseweb="tab"] {
        height: 55px; /* Taller tabs */
        background-color: #161b22; /* Darker tab background */
        border-bottom: 3px solid #30363d; /* Subtle bottom border */
        border-radius: 15px 15px 0 0; /* More rounded top corners */
        color: #e6edf3;
        font-size: 19px; /* Slightly larger font */
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    .stTabs [aria-selected="true"] {
        background-color: #e3405f; /* Active tab vibrant red */
        color: white;
        border-bottom: 3px solid #e6edf3; /* White line for active tab */
        box-shadow: 0 6px 12px rgba(227, 64, 95, 0.5); /* Prominent shadow for active tab */
        transform: translateY(-5px); /* Slight lift for active tab */
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #1f2a38; /* Slightly lighter on hover for inactive tabs */
        transform: translateY(-2px); /* Slight lift on hover */
    }

    /* Expander styling */
    .stExpander {
        background-color: #161b22; /* Darker background for expander */
        border-radius: 12px;
        padding: 20px; /* More padding */
        margin-top: 25px; /* More margin */
        border: 1px solid #30363d; /* Subtle border */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    .stExpander div[data-baseweb="accordion-header"] {
        color: #e6edf3;
        font-weight: 700; /* Bolder header */
        font-size: 1.3em; /* Larger header */
        text-align: center; /* Center the expander title */
    }
    .stExpander div[data-baseweb="accordion-item"] { /* Content area */
        color: #c9d1d9; /* Slightly subdued text for content */
    }

    /* Info, Success, Warning, Error boxes */
    .stAlert {
        border-radius: 10px;
        font-size: 1.05em;
        padding: 15px;
        margin-bottom: 15px; /* Consistent spacing */
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }
    .stAlert.info {
        background-color: #21394c; /* Darker blue for info */
        color: #79b8ff;
        border-left: 5px solid #79b8ff;
    }
    .stAlert.success {
        background-color: #1f422e; /* Darker green for success */
        color: #56d364;
        border-left: 5px solid #56d364;
    }
    .stAlert.warning {
        background-color: #5c3c00; /* Darker yellow for warning */
        color: #e3b341;
        border-left: 5px solid #e3b341;
    }
    .stAlert.error {
        background-color: #5c2020; /* Darker red for error */
        color: #f85149;
        border-left: 5px solid #f85149;
    }

    /* Map container styling */
    .st-emotion-cache-1cpxqw2 { /* This class targets the div wrapping the map */
        border-radius: 12px;
        overflow: hidden; /* Ensures map corners are rounded */
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5); /* Stronger shadow for map */
        margin-bottom: 20px;
    }

    /* Markdown headers within components */
    h1, h2, h3, h4, h5, h6 {
        color: #e6edf3; /* Ensure all headers are light */
    }
    .stMarkdown h3 {
        color: #e3405f; /* Make subheaders in markdown red */
    }
    .stMarkdown p {
        color: #c9d1d9; /* Ensure paragraph text is consistent */
    }

    /* --- Animation for the main title --- */
    @keyframes pulse-siren {
        0% { text-shadow: 0 0 5px rgba(255, 255, 255, 0.5); }
        50% { text-shadow: 0 0 15px rgba(255, 255, 255, 0.9), 0 0 20px rgba(255, 60, 60, 0.7); }
        100% { text-shadow: 0 0 5px rgba(255, 255, 255, 0.5); }
    }

    @keyframes bounce-text {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }

    .siren-emoji {
        display: inline-block; /* Allows transform and shadow */
        animation: pulse-siren 1.5s infinite alternate; /* Apply pulse animation */
    }

    .animated-title-text {
        display: inline-block; /* Allows transform */
        animation: bounce-text 2s infinite ease-in-out; /* Apply bounce animation */
    }

    /* --- Styling for the individual guide sections (Precautions, Do's, Don'ts) --- */
    .guide-section {
        background-color: #161b22; /* Darker background, consistent with input fields */
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px; /* Space between sections when stacked on mobile */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); /* Subtle shadow */
        transition: transform 0.2s ease, box-shadow 0.2s ease; /* Smooth transition */
        height: 100%; /* Ensure columns have equal height */
        display: flex;
        flex-direction: column;
    }
    .guide-section:hover {
        transform: translateY(-5px); /* Lift effect on hover */
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4); /* Slightly increased shadow on hover, no glow */
    }
    .guide-section h3 {
        color: #e3405f; /* Make the subheaders red as requested */
        margin-top: 0; /* Remove default top margin */
        margin-bottom: 15px; /* Space below header */
        text-align: center; /* Center the titles */
        /* Removed text-shadow for glow effect */
    }
    .guide-section ul {
        list-style: none; /* Remove default bullet points */
        padding-left: 0;
    }
    .guide-section li {
        margin-bottom: 10px; /* Space between list items */
        padding-left: 20px; /* Indent list items */
        position: relative; /* For custom bullet points */
        color: #c9d1d9; /* Subdued text for content */
    }
    .guide-section li:last-child {
        margin-bottom: 0;
    }
    /* Custom bullet points */
    .guide-section li::before {
        content: '•'; /* Custom bullet point */
        color: #e3405f; /* Red bullet point */
        position: absolute;
        left: 0;
        font-weight: bold;
        font-size: 1.2em;
        line-height: 1;
        /* Removed text-shadow for glow effect */
    }
</style>
""", unsafe_allow_html=True)

# ----- Header Section -----
# Using an emoji in the title and centering it with animation
st.markdown("""
<h1 style='text-align: center; color: #e3405f;'>
    <span class="siren-emoji">🚨</span> 
    <span class="animated-title-text">Emergency SOS Assistant</span> 
    <span class="siren-emoji">🚨</span>
</h1>
""", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #c9d1d9; font-size: 1.1em;'>Your immediate assistant in critical situations. Describe your emergency below.</p>", unsafe_allow_html=True)
st.markdown("---") # A stylish horizontal rule

# ----- Load Model Once (cached for performance) -----
@st.cache_resource
def cached_load_emergency_model():
    st.spinner("Loading AI Model...") # Show a spinner while loading
    model, vectorizer = load_emergency_model()
    st.success("✅ AI Model Loaded Successfully!")
    return model, vectorizer

model, vectorizer = cached_load_emergency_model()

# ----- Emergency Guide Data -----
EMERGENCY_GUIDE = {
    "fire": {
        "Precautions": [
            "Evacuate immediately using stairs, not elevators.",
            "Stay low to avoid smoke; crawl if necessary.",
            "Cover your nose and mouth with a wet cloth to filter smoke."
        ],
        "Do's": [
            "Use a fire extinguisher only if the fire is small and controllable.",
            "Call the fire department (Dial 101 in India) immediately.",
            "Go to your designated meeting point."
        ],
        "Don'ts": [
            "Don’t open hot doors; feel them with the back of your hand.",
            "Don’t hide in small spaces like closets.",
            "Don’t use water on electrical or grease fires."
        ]
    },
    "medical": {
        "Precautions": [
            "Keep the injured person still and calm, reassure them.",
            "Check for responsiveness, breathing, and severe bleeding.",
            "Maintain body temperature to prevent shock."
        ],
        "Do's": [
            "Call emergency medical help (Dial 102 in India) without delay.",
            "Give CPR if you are trained and the person is not breathing.",
            "Apply direct pressure to bleeding wounds with a clean cloth."
        ],
        "Don'ts": [
            "Don’t move the person unnecessarily, especially if there's a suspected spinal injury.",
            "Don’t give food or drink to an unconscious person or someone with abdominal injury.",
            "Don’t remove embedded objects from wounds."
        ]
    },
    "accident": {
        "Precautions": [
            "Secure the area to avoid further accidents (e.g., set up warning triangles).",
            "Do not crowd around the victim; provide space for responders.",
            "Assess the scene for dangers before approaching."
        ],
        "Do's": [
            "Turn on hazard lights if on the road and safely move to the side.",
            "Call emergency services (100 for Police, 102 for Ambulance, 101 for Fire).",
            "Provide basic first aid if trained and conditions allow."
        ],
        "Don'ts": [
            "Don’t move the injured unless absolutely essential for their immediate safety.",
            "Don’t delay calling for professional help, even if the injury seems minor.",
            "Don’t admit fault or discuss liability at the scene of a road accident."
        ]
    },
    "violence": {
        "Precautions": [
            "Find a safe space or hide (Run, Hide, Fight principle).",
            "Avoid confronting the attacker directly if unsafe to do so.",
            "Stay quiet and alert to your surroundings.",
            "Secure doors and windows if you are in a building."
        ],
        "Do's": [
            "Call police (Dial 100 in India) as soon as it is safe to do so.",
            "If possible and safe, record details of the perpetrator or incident (e.g., description, direction of travel).",
            "Follow instructions from law enforcement."
        ],
        "Don'ts": [
            "Don’t scream or draw attention to yourself unless it will bring immediate help.",
            "Don’t intervene directly if it puts your own life at risk.",
            "Don’t touch or disturb crime scene evidence."
        ]
    },
}

# ----- Tabs Layout -----
tab1, tab2, tab3 = st.tabs(["🆘 Emergency Input", "📍 Location & Nearby Help", "📤 Notify Contacts"])

# --- Tab 1: Emergency Input ---
with tab1:
    st.subheader("📝 Describe Your Emergency:")
    col_input, col_mic = st.columns([3, 1]) # Adjust column ratio for input vs. mic button

    # Initialize text_input in session state to persist its value across reruns
    if 'text_input' not in st.session_state:
        st.session_state.text_input = ""

    with col_input:
        st.session_state.text_input = st.text_area(
            "✍️ Type your emergency message here:",
            value=st.session_state.text_input,
            height=120, # Consistent height
            placeholder="e.g., 'My house is on fire, I need help!', 'Someone has fainted, medical emergency!', 'I hear gunshots, police please!', 'There's a car accident blocking the road.'"
        )

    with col_mic:
        st.markdown("<br>", unsafe_allow_html=True) # Adds a little space above the button
        if st.button("🎤 Use Microphone", key="mic_button", use_container_width=True):
            st.info("🎙️ Listening... Please speak clearly after the beep.")
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                try:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5) 
                    audio = recognizer.listen(source, timeout=7, phrase_time_limit=15)
                    st.success("✅ Audio captured. Processing speech...")
                    recognized_text = recognizer.recognize_google(audio)
                    st.session_state.text_input = recognized_text
                    st.chat_message("user").write(f"🗣️ You said: *\"{recognized_text}\"*")
                    st.rerun() # Rerun to update the text_area and trigger detection
                except sr.WaitTimeoutError:
                    st.warning("⏱️ Listening timed out. No speech detected. Please try again.")
                except sr.UnknownValueError:
                    st.warning("🛑 Could not understand audio. Please speak more clearly or try typing.")
                except sr.RequestError as e:
                    st.error(f"❌ Could not request results from Google Speech Recognition service; {e}. Check your internet connection.")
                except Exception as e:
                    st.error(f"An unexpected error occurred with microphone input: {e}")

    # --- Emergency Detection & Guide Display ---
    st.markdown("---") # Separator

    category = None
    if st.session_state.text_input:
        with st.spinner("Analyzing emergency type..."):
            category = detect_emergency(st.session_state.text_input, model, vectorizer)
        st.success(f"🚨 **Emergency Type Detected:** `{category.upper()}`")

        if category in EMERGENCY_GUIDE:
            # Assign an ID to the expander for scrolling
            st.markdown('<div id="emergency-guide-section"></div>', unsafe_allow_html=True) # Anchor for scrolling
            with st.expander(f"📚 Emergency Guide for {category.upper()} Situations", expanded=True):
                col_prec, col_do, col_dont = st.columns(3)

                # Construct HTML for each guide section and render it
                with col_prec:
                    precautions_list_html = ''.join([f"<li>{p}</li>" for p in EMERGENCY_GUIDE[category]["Precautions"]])
                    st.markdown(f"""
                    <div class='guide-section'>
                        <h3>⚠️ Precautions</h3>
                        <ul>
                            {precautions_list_html}
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_do:
                    dos_list_html = ''.join([f"<li>{d}</li>" for d in EMERGENCY_GUIDE[category]["Do's"]])
                    st.markdown(f"""
                    <div class='guide-section'>
                        <h3>✅ Do's</h3>
                        <ul>
                            {dos_list_html}
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_dont:
                    donts_list_html = ''.join([f"<li>{n}</li>" for n in EMERGENCY_GUIDE[category]["Don'ts"]])
                    st.markdown(f"""
                    <div class='guide-section'>
                        <h3>❌ Don'ts</h3>
                        <ul>
                            {donts_list_html}
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
            
            # JavaScript to scroll to the emergency guide section
            st.components.v1.html(
                """
                <script>
                    setTimeout(function() {
                        var element = document.getElementById('emergency-guide-section');
                        if (element) {
                            element.scrollIntoView({behavior: 'smooth', block: 'start'});
                        }
                    }, 100); // Small delay to ensure element is rendered
                </script>
                """,
                height=0, # Make the component invisible
                width=0,
                scrolling=False
            )
        else:
            st.info("No specific guide available for this emergency type. Please refer to general safety guidelines.")

# --- Tab 2: Location & Nearby Help ---
with tab2:
    st.subheader("📍 Your Current Location")
    st.info("Fetching your location... This might take a moment.")
    
    @st.cache_data(ttl=300) # Cache for 5 minutes
    def get_cached_location():
        return get_current_location()

    lat, lon, city = get_cached_location()

    # --- Centering the map and location info ---
    col_left, col_center, col_right = st.columns([1, 4, 1])

    with col_center:
        if lat and lon:
            st.success(f"📌 Location Found: **{city}** (Lat: {lat:.4f}, Lon: {lon:.4f})")
            location_map = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker([lat, lon], tooltip="You are here", popup=city).add_to(location_map)
            
            st_data = st_folium(location_map, width=800, height=500, key="current_location_map")
            
            map_link = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}"
            st.markdown(f"🔗 [View and Share Location on OpenStreetMap]({map_link})", unsafe_allow_html=True)
        else:
            st.error("❌ Could not retrieve current location. Please ensure location services are enabled or try again.")

    st.markdown("---") # Separator

    st.subheader("🔍 Find Nearby Emergency Services")
    col_hosp, col_police = st.columns(2)

    with col_hosp:
        if st.button("🏥 Show Nearby Hospitals", key="hospitals_button", use_container_width=True):
            if lat and lon:
                with st.spinner("Searching for hospitals..."):
                    hospitals = find_nearby(lat, lon, place_type="hospital")
                st.markdown("### Nearby Hospitals:")
                if hospitals:
                    with st.container(border=True):
                        for i, h in enumerate(hospitals[:5]):
                            name = h.get('display_name', 'Unknown Hospital').split(',')[0]
                            phone = h.get('contact:phone', 'N/A')
                            lat2 = float(h.get('lat', 0))
                            lon2 = float(h.get('lon', 0))
                            dist = haversine(lat, lon, lat2, lon2)
                            st.markdown(f"**{i+1}. 🏥 {name}**")
                            st.markdown(f"    📞 Phone: `{phone}`")
                            st.markdown(f"    📏 Distance: `{dist} km`")
                            if h.get('address'):
                                st.markdown(f"    📍 Address: _{h['address'].get('street')}, {h['address'].get('city')}_")
                            st.markdown("---")
                else:
                    st.info("No hospitals found nearby. Try again or check your location.")
            else:
                st.warning("Please enable location services to find nearby places.")

    with col_police:
        if st.button("🚓 Show Nearby Police Stations", key="police_button", use_container_width=True):
            if lat and lon:
                with st.spinner("Searching for police stations..."):
                    stations = find_nearby(lat, lon, place_type="police")
                st.markdown("### Nearby Police Stations:")
                if stations:
                    with st.container(border=True):
                        for i, p in enumerate(stations[:5]):
                            name = p.get('display_name', 'Unknown Police Station').split(',')[0]
                            phone = p.get('contact:phone', 'N/A')
                            lat2 = float(p.get('lat', 0))
                            lon2 = float(p.get('lon', 0))
                            dist = haversine(lat, lon, lat2, lon2)
                            st.markdown(f"**{i+1}. 🚓 {name}**")
                            st.markdown(f"    📞 Phone: `{phone}`")
                            st.markdown(f"    📏 Distance: `{dist} km`")
                            if p.get('address'):
                                st.markdown(f"    📍 Address: _{p['address'].get('street')}, {p['address'].get('city')}_")
                            st.markdown("---")
                else:
                    st.info("No police stations found nearby. Try again or check your location.")
            else:
                st.warning("Please enable location services to find nearby places.")

# --- Tab 3: Notify Contacts & Help ---
with tab3:
    st.subheader("📤 Notify Your Emergency Contacts")
    st.info("This section allows you to send an emergency alert to your pre-configured contacts via Email and WhatsApp.")

    current_category = detect_emergency(st.session_state.text_input, model, vectorizer) if st.session_state.text_input else None
    
    if not st.session_state.text_input:
        st.warning("Please describe your emergency in the 'Emergency Input' tab first to enable notifications.")
    elif not current_category:
        st.warning("Could not determine emergency category from your input. Please provide more details.")
    else:
        st.markdown(f"Emergency detected: **`{current_category.upper()}`**")
        st.markdown("---")

        lat, lon, city = get_cached_location()

        if st.button("📱 Send Emergency Notification", key="send_notify_button", use_container_width=True):
            if not lat or not lon:
                st.error("Cannot send notifications without a valid location. Please ensure location services are active.")
            else:
                with st.spinner("Composing and sending notifications..."):
                    maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
                    msg = (
                        f"🚨 EMERGENCY ALERT 🚨\n\n"
                        f"**Type:** {current_category.upper()}\n"
                        f"**Location:** {city}\n"
                        f"**Coordinates:** {lat:.4f}, {lon:.4f}\n"
                        f"**Google Maps:** {maps_link}\n\n"
                        f"_{st.session_state.text_input}_\n"
                        f"Please check on me!"
                    )
                    
                    st.markdown("---")
                    st.write("Sending Email...")
                    email_success = send_email(f"URGENT: EMERGENCY ALERT - {current_category.upper()}", msg)
                    st.success("✅ Email sent successfully." if email_success else "❌ Email failed. Check `SENDER_EMAIL`, `RECEIVER_EMAIL`, `APP_PASSWORD` in `.env`.")
                    
                    st.write("Sending WhatsApp...")
                    whatsapp_success = send_whatsapp(msg)
                    st.success("✅ WhatsApp message sent." if whatsapp_success else "⚠️ WhatsApp failed. Check `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` in `.env` and recipient number.")
                st.balloons()


# --- Footer ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #888888; font-size: 0.9em;'>Developed with ❤️ using Streamlit and Machine Learning.</p>", unsafe_allow_html=True)
