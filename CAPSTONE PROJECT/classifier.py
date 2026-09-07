import pickle


# Load trained model
with open("complaint_model.pkl", "rb") as f:
    model = pickle.load(f)


# Load TF-IDF vectorizer
with open("tfidf_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)


def classify_complaint(text):

    # Convert text into TF-IDF features
    features = vectorizer.transform([text])

    # Predict category
    prediction = model.predict(features)[0]

    # Calculate confidence
    probabilities = model.predict_proba(features)[0]

    confidence = max(probabilities)

    return prediction, confidence
def detect_priority(text):

    high_priority_words = [
        "emergency",
        "danger",
        "stuck",
        "fire",
        "accident",
        "urgent",
        "immediately",
        "unsafe"
    ]

    medium_priority_words = [
        "not working",
        "broken",
        "leak",
        "problem",
        "issue"
    ]

    text = text.lower()

    for word in high_priority_words:

        if word in text:
            return "High"

    for word in medium_priority_words:

        if word in text:
            return "Medium"

    return "Low"