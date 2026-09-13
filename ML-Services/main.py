from fastapi import FastAPI
from pydantic import BaseModel
from predict import predict_url

app = FastAPI(title="Fraud Detection ML Service")

class URLRequest(BaseModel):
    url: str

@app.get("/")
def root():
    return {"message": "Fraud Detection ML Service is running"}

@app.post("/predict")
def predict(request: URLRequest):
    result = predict_url(request.url)
    return result