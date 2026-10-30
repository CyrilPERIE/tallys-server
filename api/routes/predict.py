from fastapi import APIRouter
from pmu.types.enum import BetType
from prediction._evaluate.evaluate_all_models import predict_random
from prediction._evaluate.evaluate_model import evaluate_model

router = APIRouter(prefix="/predict", tags=["predict"])

@router.get("/")
def predict():
    # return evaluate_model(predict_random, "Aléatoire", BetType.E_SIMPLE_GAGNANT)
    return {"message": "OK"}