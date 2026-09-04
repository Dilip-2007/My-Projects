import streamlit as st
import pandas as pd
import numpy as np
import re
from collections import Counter


# --------------------------------
# Page configuration
# --------------------------------
st.set_page_config(
    page_title="Sentiment Analyzer",
    page_icon="😊",
    layout="centered"
)


# --------------------------------
# Title
# --------------------------------
st.title("😊 Sentiment Analyzer Agent")

st.write(
    "Enter a customer review and the machine-learning model "
    "will predict whether the sentiment is Positive or Negative."
)


# --------------------------------
# Training dataset
# --------------------------------
training_data = [

    # Positive reviews
    ("I love this product", "Positive"),
    ("This product is amazing", "Positive"),
    ("Excellent quality and great service", "Positive"),
    ("Very happy with my purchase", "Positive"),
    ("The product works perfectly", "Positive"),
    ("Absolutely wonderful experience", "Positive"),
    ("Fast delivery and good quality", "Positive"),
    ("I really enjoyed this product", "Positive"),
    ("Fantastic product", "Positive"),
    ("Very useful and reliable", "Positive"),
    ("Great product and excellent quality", "Positive"),
    ("I am satisfied with this purchase", "Positive"),

    # Negative reviews
    ("I hate this product", "Negative"),
    ("This product is terrible", "Negative"),
    ("Very bad quality", "Negative"),
    ("I am unhappy with my purchase", "Negative"),
    ("The product does not work", "Negative"),
    ("Absolutely horrible experience", "Negative"),
    ("Very slow delivery and poor quality", "Negative"),
    ("I really disliked this product", "Negative"),
    ("Terrible product", "Negative"),
    ("Very useless and unreliable", "Negative"),
    ("Bad product and poor quality", "Negative"),
    ("I am disappointed with this purchase", "Negative"),
    ("The product is worst", "Negative"),
]


# --------------------------------
# Text preprocessing
# --------------------------------
def tokenize(text):

    text = text.lower()

    words = re.findall(r"\b[a-zA-Z]+\b", text)

    return words


# --------------------------------
# Train Naive Bayes model
# --------------------------------
positive_words = Counter()
negative_words = Counter()

positive_total = 0
negative_total = 0


for review, sentiment in training_data:

    words = tokenize(review)

    if sentiment == "Positive":

        positive_words.update(words)
        positive_total += len(words)

    else:

        negative_words.update(words)
        negative_total += len(words)


# --------------------------------
# Vocabulary
# --------------------------------
vocabulary = set(
    list(positive_words.keys())
    + list(negative_words.keys())
)

vocabulary_size = len(vocabulary)


# --------------------------------
# Number of training examples
# --------------------------------
positive_reviews = sum(
    1 for _, sentiment in training_data
    if sentiment == "Positive"
)

negative_reviews = sum(
    1 for _, sentiment in training_data
    if sentiment == "Negative"
)

total_reviews = len(training_data)


# --------------------------------
# Prior probabilities
# --------------------------------
positive_prior = positive_reviews / total_reviews

negative_prior = negative_reviews / total_reviews


# --------------------------------
# Naive Bayes prediction
# --------------------------------
def predict_sentiment(review):

    words = tokenize(review)

    positive_probability = positive_prior
    negative_probability = negative_prior

    for word in words:

        # Laplace smoothing
        positive_probability *= (
            (positive_words[word] + 1)
            / (positive_total + vocabulary_size)
        )

        negative_probability *= (
            (negative_words[word] + 1)
            / (negative_total + vocabulary_size)
        )

    total_probability = (
        positive_probability
        + negative_probability
    )

    if total_probability == 0:

        return "Unknown", 0.0, 0.0

    positive_confidence = (
        positive_probability
        / total_probability
    )

    negative_confidence = (
        negative_probability
        / total_probability
    )

    if positive_confidence >= negative_confidence:

        return (
            "Positive",
            positive_confidence,
            negative_confidence
        )

    else:

        return (
            "Negative",
            positive_confidence,
            negative_confidence
        )


# --------------------------------
# Calculate model accuracy
# --------------------------------
correct_predictions = 0

for review, actual_sentiment in training_data:

    predicted_sentiment, _, _ = predict_sentiment(review)

    if predicted_sentiment == actual_sentiment:

        correct_predictions += 1


accuracy = (
    correct_predictions
    / len(training_data)
) * 100


# --------------------------------
# User input
# --------------------------------
review = st.text_area(
    "📝 Enter customer feedback:",
    placeholder="Example: The product is excellent and I love it."
)


# --------------------------------
# Analyze button
# --------------------------------
if st.button("🔍 Analyze Sentiment"):

    if review.strip() == "":

        st.warning(
            "Please enter a customer review."
        )

    else:

        sentiment, positive_confidence, negative_confidence = (
            predict_sentiment(review)
        )


        # --------------------------------
        # Prediction result
        # --------------------------------
        st.subheader("🎯 Prediction")


        if sentiment == "Positive":

            st.success(
                "😊 Positive Sentiment"
            )

            confidence = positive_confidence * 100

        else:

            st.error(
                "😞 Negative Sentiment"
            )

            confidence = negative_confidence * 100


        # --------------------------------
        # Confidence
        # --------------------------------
        st.metric(
            "Model Confidence",
            f"{confidence:.2f}%"
        )


        st.progress(
            min(max(confidence / 100, 0), 1)
        )


        # --------------------------------
        # Probability details
        # --------------------------------
        st.subheader(
            "📊 Probability Details"
        )

        probability_data = pd.DataFrame(
            {
                "Sentiment": [
                    "Positive",
                    "Negative"
                ],
                "Probability": [
                    positive_confidence * 100,
                    negative_confidence * 100
                ]
            }
        )


        st.dataframe(
            probability_data,
            use_container_width=True,
            hide_index=True
        )


# --------------------------------
# Model information
# --------------------------------
st.divider()

st.subheader("🤖 Model Information")


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Training Reviews",
        total_reviews
    )


with col2:

    st.metric(
        "Vocabulary Size",
        vocabulary_size
    )


with col3:

    st.metric(
        "Training Accuracy",
        f"{accuracy:.2f}%"
    )


st.info(
    "Model: Multinomial-style Naive Bayes with "
    "word-frequency features and Laplace smoothing."
)