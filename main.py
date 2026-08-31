from fastapi import FastAPI
import joblib
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from schema import Ecommercefeatures, PredictionResponse
app  = FastAPI(
    title="E-Commerce Purchase prediction",
    version='1.0'
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load("model.pkl")
preprocessor = joblib.load("preprocessor.pkl")
@app.get('/')
def home():
    return "Server is started"


# 5. Prediction API Endpoint
@app.post("/predict", response_model=PredictionResponse)
def predict(data: Ecommercefeatures):
    # Convert request to dictionary
    input_data = data.model_dump()

    # Convert to DataFrame
    df = pd.DataFrame([input_data])
    transformed_data = preprocessor.transform(df)

    # Predict
    prediction = model.predict(transformed_data)[0]

    # Convert prediction to readable output
    if prediction == 1:
        result = "PURCHASED"
    else:
        result = "NOT PURCHASED"

    return PredictionResponse(
        prediction=result
    )



