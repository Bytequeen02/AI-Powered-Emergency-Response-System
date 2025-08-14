import joblib
import geocoder
import requests
import os
import smtplib
from dotenv import load_dotenv
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage

load_dotenv()

def load_emergency_model():
    model = joblib.load("emergency_model.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
    return model, vectorizer

def detect_emergency(text, model, vectorizer):
    X = vectorizer.transform([text])
    return model.predict(X)[0]

def get_current_location():
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()
        lat = data["lat"]
        lon = data["lon"]
        city = data["city"]
        return lat, lon, city
    except Exception as e:
        print("Error getting location:", e)
        return None, None, None

# Send WhatsApp using Twilio sandbox
def send_whatsapp(message):
    try:
        client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH"))
        msg = client.messages.create(
            from_=os.getenv("TWILIO_WHATSAPP_FROM"),
            body=message,
            to=os.getenv("WHATSAPP_TO")
        )
        print("WhatsApp message sent:", msg.sid)
        return True
    except Exception as e:
        print("WhatsApp error:", e)
        return False

def send_email(subject, body, to_email=None):
    try:
        sender = os.getenv("EMAIL_SENDER")
        app_password = os.getenv("GMAIL_APP_PASSWORD")
        receiver = to_email or os.getenv("EMAIL_RECEIVER")

        # Validate credentials
        if not sender or not app_password or not receiver:
            raise ValueError("Missing email credentials or recipient address")
        
        msg = MIMEMultipart()
        #msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = receiver
        msg.attach(MIMEText(body, "plain"))

        # Connect and send the email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.set_debuglevel(1)  # For detailed debugging, you can remove this in production
        server.starttls()
        server.login(sender, app_password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()

        print("✅ Email sent successfully.")
        return True

    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

#def find_nearby(lat, lon, place_type="hospital"):
    try:
        query = f"{place_type} near {lat},{lon}"
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={query}&limit=5&bounded=1&viewbox={lon-0.05},{lat+0.05},{lon+0.05},{lat-0.05}"
        headers = {"User-Agent": "EmergencyApp/1.0"}
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Error finding nearby {place_type}: {e}")
        return []

def find_nearby(lat, lon, place_type="hospital"):
    # Static demo data 
    hospitals = [
        {
            "display_name": "EMC Super Speciality Hospital, Amritsar",
            "contact:phone": "+91 180 2571222",
            "lat": "31.6203",
            "lon": "74.8765"
        },
        {
            "display_name": "PULSE Hospital, Amritsar",
            "contact:phone": "+91 180 2640022",
            "lat": "31.6200",
            "lon": "74.8760"
        },
        {
            "display_name": "Fortis Escorts Hospital, Amritsar",
            "contact:phone": "+91 7527000036",
            "lat": "31.6400",
            "lon": "74.8770"
        },
        {
            "display_name": "Amandeep Medicity Hospital, Amritsar",
            "contact:phone": "+91 8288082870",
            "lat": "31.64123",
            "lon": "74.87735"
        }
    ]

    police_stations = [
        {
            "display_name": "A Division Police Station (Rambagh / Kotwali area)",
            "contact:phone": "+91 9781130201",
            "lat": "31.6358",
            "lon": "74.88038"
        },
        {
            "display_name": "B Division Police Station (Sultanwind Gate area)",
            "contact:phone": "+91 9781130202",
            "lat": "31.6357",
            "lon": "74.88030"
        },
        {
            "display_name": "C Division Police Station (Gilwali Gate / Maqboolpura)",
            "contact:phone": "+91 9781130203",
            "lat": "31.6360",
            "lon": "74.88040"
        }
    ]

    return hospitals if place_type == "hospital" else police_stations

