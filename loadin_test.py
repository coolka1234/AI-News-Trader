# load_predict.py

from hmac import new
from turtle import st
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import pickle
import re
import matplotlib.pyplot as plt

# Preprocess text function
def preprocess_text(text):
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\d+', '', text)
    text = text.lower()
    return text
def load_predict(news_array, stock_array):
    model = load_model('stock_prediction_model.h5')

    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    with open('feature_scaler.pkl', 'rb') as f:
        feature_scaler = pickle.load(f)
    with open('target_scaler.pkl', 'rb') as f:
        target_scaler = pickle.load(f)

    new_articles = news_array.tolist()
    new_open_prices = [stock_array]
    new_articles = [preprocess_text(article) for article in new_articles]
    new_data_text_features = vectorizer.transform(new_articles).toarray()
    # new_data_stock_features = np.array(new_open_prices).reshape(-1, 1)  # Reshape to (n_samples, 1)
    weight_factor = 1000  # This should match the weight factor used in training
    new_data_stock_features = np.full((1, weight_factor), new_open_prices[0]) 
    new_combined_features = np.hstack((new_data_text_features, new_data_stock_features))
    new_combined_features = feature_scaler.transform(new_combined_features)
    new_combined_features = np.expand_dims(new_combined_features, axis=1)
    new_combined_features = np.asarray(new_combined_features).astype(np.float32)
    predicted_stock_price = model.predict(new_combined_features)
    predicted_stock_price = target_scaler.inverse_transform(predicted_stock_price)
    return predicted_stock_price