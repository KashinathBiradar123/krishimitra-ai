<h1 align="center">🌾 Agricultural Advisory Assistant for Farmers</h1>
<p align="center">
  <b>KrishiMitra AI — An intelligent farming companion for Indian farmers</b><br/>
  Crop disease detection · Weather forecasting · Market prices · Smart farming advice
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python"/>
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi"/>
  <img src="https://img.shields.io/badge/Deep%20Learning-MobileNetV2-orange?style=flat-square&logo=tensorflow"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square"/>
</p>

---

## 🧠 About the Project

**Agricultural Advisory Assistant for Farmers** is an end-to-end AI platform, branded as **KrishiMitra** (Hindi: *Farmer's Friend*), built to empower Indian farmers with modern technology. Farmers can upload a photo of a diseased crop leaf, get an instant AI diagnosis, check live weather and mandi prices, and receive actionable farming advice — all in one place.

> Built with the goal of bridging the technology gap for rural and semi-urban farmers across India.

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 🔬 **Crop Disease Detection** | Upload a leaf image → MobileNetV2 model identifies the disease and suggests treatment |
| 🌦️ **Weather Forecasting** | Location-based weather data to plan sowing, irrigation, and harvesting |
| 📈 **Market (Mandi) Prices** | Live commodity prices to help farmers sell at the right time |
| 🤖 **AI Farming Advice** | Intelligent recommendations based on crop, season, and soil conditions |

---

## 🏗️ Project Structure

<img width="900" height="366" alt="image" src="https://github.com/user-attachments/assets/752e6b1a-f4dc-4af4-81ae-99338b54a0f3" />
---

## 🤖 Model Details

- **Architecture:** MobileNetV2 (Transfer Learning)
- **Task:** Multi-class image classification (crop leaf diseases)
- **Dataset:** PlantVillage / Mendeley Crop Disease Dataset
- **Framework:** TensorFlow / Keras
- **Serving:** FastAPI REST endpoint (`/predict`)

---

## 🛠️ Tech Stack

**Backend**
- Python 3.10+
- FastAPI
- TensorFlow / Keras (MobileNetV2)
- Uvicorn

**Frontend**
- HTML / CSS / JavaScript

**APIs Used**
- OpenWeatherMap (weather forecasting)
- Agmarknet / custom scraper (mandi/market prices)

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/KashinathBiradar123/krishimitra-ai.git
cd krishimitra-ai
```

### 2. Set up the backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Download the dataset
```bash
python download_dataset_mendeley.py
```

### 4. Open the frontend

Open `frontend/index.html` in your browser, or serve it locally:
```bash
cd frontend
npx serve .
```

---

## 📓 Notebooks

The `notebooks/` folder contains:
- **EDA** — Exploratory Data Analysis of crop disease image data
- **Model Training** — MobileNetV2 fine-tuning pipeline
- **Evaluation** — Accuracy, Confusion Matrix, per-class metrics

---

## 🌱 Roadmap

- [ ] Multilingual support (Hindi, Marathi, Kannada)
- [ ] Mobile app (React Native / Flutter)
- [ ] Offline inference for low-connectivity rural areas
- [ ] Government scheme recommendations (PM-Kisan, crop insurance)
- [ ] Soil health input integration

---

## 🙋 Author

**Kashinath Biradar**  
[GitHub](https://github.com/KashinathBiradar123) · Made with for Indian farmers

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
