import pandas as pd
import pickle
import re
import os
file_path = os.path.join(os.path.dirname(__file__),"data.csv")
data=pd.read_csv(file_path)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

data = pd.read_csv("data.csv")

X = data["text"]
y = data["label"]

vectorizer = TfidfVectorizer(stop_words='english')
X_vector = vectorizer.fit_transform(X)

model = MultinomialNB()
model.fit(X_vector, y)

pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    return text

def predict(text):
    model = pickle.load(open("model.pkl", "rb"))
    vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

    text = clean_text(text)
    text_vector = vectorizer.transform([text])
    return model.predict(text_vector)[0]