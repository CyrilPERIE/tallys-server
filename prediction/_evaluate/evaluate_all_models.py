from typing import Callable, TypedDict
from models.course import Course
from models.participant import Participant
from pmu.types.enum import BetType
from random import random
from prediction._evaluate.evaluate_model import evaluate_model
from prediction.random.predict import predict as predict_random

class Predict(TypedDict):
    model: Callable[[Course], list[Participant]]
    bet_type: BetType
    name: str
    
predicts: list[Predict] = [
    {
        "model": predict_random,
        "bet_type": BetType.E_SIMPLE_GAGNANT,
        "name": "Aléatoire",
    }
]

def evaluate_all_models(): 
    for p in predicts:
        result = evaluate_model(p["model"], p["name"], p["bet_type"])