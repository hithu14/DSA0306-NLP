import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from preprocessing import preprocess_text


# Load dataset
data = pd.read_csv("complaints.csv")


# Preprocess complaints
data["clean_text"] = data["text"].apply(preprocess_text)


# TF-IDF
vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(data["clean_text"])

y = data["label"]


# Multinomial Naive Bayes
model = MultinomialNB()

model.fit(X, y)


# Save model objects
import pickle

with open("complaint_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)


print("Model trained successfully!")