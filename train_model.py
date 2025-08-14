from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

texts = [
    "My house is on fire",
    "There’s smoke everywhere",
    "Fire in the building",
    "I need an ambulance",
    "Someone fainted",
    "There is a medical emergency",
    "I hear gunshots",
    "There’s a robbery",
    "Someone broke into my house",
    "Help! Heart attack!",
    "There is a car accident",
    "Fire alarm ringing",
    "Police chase happening nearby"
]

labels = [
    "fire", "fire", "fire",
    "medical", "medical", "medical",
    "police", "police", "police",
    "medical", "medical", "fire",
    "police"
]

# Vectorize the text data
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

# Train the model
model = MultinomialNB()
model.fit(X, labels)

# Save the trained model and vectorizer
joblib.dump(model, "emergency_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("Model and vectorizer saved successfully!")
