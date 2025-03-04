import streamlit as st
import pandas as pd
import numpy as np
from zipfile import ZipFile
import io
import requests
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Load the SMS Spam dataset from the ZIP
@st.cache_data
def load_sms_spam_data():
    url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip'
    response = requests.get(url)
    
    # Open the zip file and extract the dataset
    with ZipFile(io.BytesIO(response.content)) as z:
        # Extract the actual dataset file from the ZIP archive
        with z.open('SMSSpamCollection') as f:
            df = pd.read_csv(f, sep='\t', header=None, names=['label', 'message'])
    return df

# Text preprocessing using TF-IDF or Count Vectorizer
def preprocess_text(data, method='tfidf'):
    if method == 'tfidf':
        vectorizer = TfidfVectorizer(stop_words='english')
    else:
        vectorizer = CountVectorizer(stop_words='english')
    
    X = vectorizer.fit_transform(data['message'])
    y = data['label'].map({'ham': 0, 'spam': 1})  # Convert 'ham' to 0 and 'spam' to 1
    return X, y, vectorizer

# Sidebar to select hyperparameters
# def hyperparameter_selection(classifier_name):
#     params = {}
    
#     if classifier_name == "RandomForest":
#         n_estimators = st.sidebar.slider("n_estimators", 50, 200, 100)
#         max_depth = st.sidebar.slider("max_depth", 1, 20, 10)
#         min_samples_split = st.sidebar.slider("min_samples_split", 2, 10, 2)
#         params = {'n_estimators': n_estimators, 'max_depth': max_depth, 'min_samples_split': min_samples_split}
        
#     elif classifier_name == "GradientBoosting":
#         n_estimators = st.sidebar.slider("n_estimators", 50, 200, 100)
#         learning_rate = st.sidebar.slider("learning_rate", 0.01, 0.5, 0.1)
#         max_depth = st.sidebar.slider("max_depth", 1, 10, 3)
#         params = {'n_estimators': n_estimators, 'learning_rate': learning_rate, 'max_depth': max_depth}
        
#     elif classifier_name == "LogisticRegression":
#         C = st.sidebar.slider("C", 0.01, 1.0, 0.1)
#         max_iter = st.sidebar.slider("max_iter", 100, 500, 200)
#         params = {'C': C, 'max_iter': max_iter}
        
#     elif classifier_name == "SVM":
#         C = st.sidebar.slider("C", 0.01, 1.0, 0.1)
#         kernel = st.sidebar.selectbox("kernel", ["linear", "rbf"])
#         params = {'C': C, 'kernel': kernel}
        
#     elif classifier_name == "KNN":
#         n_neighbors = st.sidebar.slider("n_neighbors", 3, 10, 5)
#         weights = st.sidebar.selectbox("weights", ["uniform", "distance"])
#         params = {'n_neighbors': n_neighbors, 'weights': weights}
        
#     elif classifier_name == "AdaBoost":
#         n_estimators = st.sidebar.slider("n_estimators", 50, 200, 100)
#         learning_rate = st.sidebar.slider("learning_rate", 0.01, 1.0, 0.1)
#         params = {'n_estimators': n_estimators, 'learning_rate': learning_rate}
    
#     return params

# Train models
def train_models(X_train, y_train, classifiers):
    models = []
    
    for name, clf in classifiers.items():
        params = hyperparameter_selection(name)
        st.write(f"Training {name} with params: {params}")
        clf.set_params(**params)
        clf.fit(X_train, y_train)
        models.append((name, clf))
    
    return models

# Display accuracy of each model
def display_accuracy(models, X_test, y_test):
    st.subheader("Model Accuracies")
    accuracies = []
    for name, model in models:
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        st.write(f"{name}: {accuracy:.2f}")
        accuracies.append((name, accuracy))
    return accuracies

# Plot accuracy comparison
def plot_accuracy_chart(accuracies):
    names, values = zip(*accuracies)
    fig, ax = plt.subplots()
    ax.barh(names, values, color='skyblue')
    ax.set_xlabel("Accuracy")
    ax.set_title("Model Accuracy Comparison")
    st.pyplot(fig)

# Confusion matrix plot
def plot_confusion_matrix(y_true, y_pred, classifier_name):
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots()
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
    ax.set_title(f"Confusion Matrix - {classifier_name}")
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("True Label")
    st.pyplot(fig)

# Display class distribution
def plot_class_distribution(data):
    st.subheader("Class Distribution")
    class_counts = data['label'].value_counts()
    fig, ax = plt.subplots()
    class_counts.plot(kind='bar', color=['green', 'red'], ax=ax)
    ax.set_title("Class Distribution of Spam and Ham")
    ax.set_xlabel("Class")
    ax.set_ylabel("Count")
    st.pyplot(fig)

# Display most frequent words in spam and ham
def plot_word_frequencies(data, vectorizer):
    st.subheader("Most Frequent Words in Spam and Ham")
    spam_words = ' '.join(data[data['label'] == 'spam']['message'])
    ham_words = ' '.join(data[data['label'] == 'ham']['message'])
    
    spam_counter = Counter(spam_words.split())
    ham_counter = Counter(ham_words.split())
    
    spam_common = pd.DataFrame(spam_counter.most_common(10), columns=['word', 'count'])
    ham_common = pd.DataFrame(ham_counter.most_common(10), columns=['word', 'count'])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    sns.barplot(x='count', y='word', data=spam_common, ax=ax1, palette='Reds_r')
    ax1.set_title("Most Frequent Words in Spam")
    
    sns.barplot(x='count', y='word', data=ham_common, ax=ax2, palette='Greens_r')
    ax2.set_title("Most Frequent Words in Ham")
    
    st.pyplot(fig)

# Main app function
def main():
    st.title("SMS Spam Detection with Ensemble Learning [Ajay Kumar Jha]")

    # Load dataset
    data = load_sms_spam_data()
    st.write("Dataset Preview:")
    st.dataframe(data.head())

    # Show class distribution
    plot_class_distribution(data)

    # Sidebar for user input
    vectorizer_method = st.sidebar.selectbox("Vectorizer Method", ["tfidf", "count"])
    test_size = st.sidebar.slider("Test Size", 0.1, 0.5, 0.2)
    classifiers_to_use = st.sidebar.multiselect(
        "Select Classifiers",
        ["RandomForest", "GradientBoosting", "LogisticRegression", "SVM", "KNN", "AdaBoost"],
        ["RandomForest", "GradientBoosting", "LogisticRegression"]
    )

    # Preprocess data
    X, y, vectorizer = preprocess_text(data, vectorizer_method)
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    # Available classifiers
    classifiers = {
        "RandomForest": RandomForestClassifier(),
        "GradientBoosting": GradientBoostingClassifier(),
        "LogisticRegression": LogisticRegression(max_iter=200),
        "SVM": SVC(),
        "KNN": KNeighborsClassifier(),
        "AdaBoost": AdaBoostClassifier()
    }

    # Filter classifiers based on user selection
    selected_classifiers = {name: classifiers[name] for name in classifiers_to_use}

    if st.button("Submit"):
        # Train individual models
        trained_models = train_models(X_train, y_train, selected_classifiers)

        # Evaluate and display accuracies
        accuracies = display_accuracy(trained_models, X_test, y_test)

        # Plot accuracy comparison chart
        plot_accuracy_chart(accuracies)

        # Plot confusion matrix and other evaluation metrics
        for name, model in trained_models:
            y_pred = model.predict(X_test)
            plot_confusion_matrix(y_test, y_pred, name)
            st.text(f"Classification Report for {name}:")
            st.text(classification_report(y_test, y_pred))

        # Display most frequent words in spam and ham
        plot_word_frequencies(data, vectorizer)

if __name__ == '__main__':
    main()
