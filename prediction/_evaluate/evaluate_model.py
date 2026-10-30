from datetime import date
from typing import Callable, TypedDict
from models.course import Course
from models.participant import Participant
from pmu.types.enum import BetType
from pmu.utils import evaluate_bet
from pmu.dates import programme_date_to_date
from prediction._common.config import EVALUATION_YEAR, TRAINING_YEAR
from service.course import get_courses_by_year
from service.metrics import update_model_evaluation_metircs
from service.utils.deps import get_session
import pandas as pd

from utils.mapper import course_id_to_course_identifier

class EvaluateModelReturnType(TypedDict):
    training_years: int
    evaluation_years: int
    type_of_bet: BetType
    bet_count: int
    win_count: int
    win_rate: float
    total_profit: float
    net_profit: float
    average_profit: float
    roi: float
    cumulative_profit: list[tuple[date, float]]

blank_return_type: EvaluateModelReturnType = {
    "training_years": 0,
    "evaluation_years": 0,
    "type_of_bet": BetType.E_SIMPLE_GAGNANT,
    "bet_count": 0,
    "win_count": 0,
    "win_rate": 0,
    "total_profit": 0,
    "net_profit": 0,
    "average_profit": 0,
    "roi": 0,
    "cumulative_profit": [],
}


def evaluate_model(predict: Callable[[Course], list[Participant]], name: str, bet_type: BetType = BetType.E_SIMPLE_GAGNANT, training_years: int = TRAINING_YEAR, evaluation_years: int = EVALUATION_YEAR, wager_amount: int = 1) -> EvaluateModelReturnType:
    result = blank_return_type
    result["training_years"] = training_years
    result["evaluation_years"] = evaluation_years
    result["type_of_bet"] = bet_type

    courses = None
    session = get_session()
    with session:
        courses = get_courses_by_year(evaluation_years, session)

    columns = ["date","course_id", "prediction", "is_found", "is_win", "profit", "is_refound", "is_valid"]
    rows = []
    for course in courses:
        prediction = predict(course)
        combination = [int(participant.id.split("/P")[1]) for participant in prediction]
        bet_evaluation = evaluate_bet(course_id_to_course_identifier(course.id), bet_type, combination, wager_amount)
        rows.append({
            "date": programme_date_to_date(course.id.split("/")[0]),
            "course_id": course.id,
            "prediction": prediction,
            "is_found": bet_evaluation["is_found"],
            "is_win": bet_evaluation["is_win"],
            "profit": bet_evaluation["profit"],
            "is_refound": bet_evaluation["is_refound"],
            "is_valid": bet_evaluation["is_valid"],
        })

    df = pd.DataFrame(rows, columns=columns)
    result["bet_count"] = df["is_found"].sum()
    result["win_count"] = df["is_win"].sum()
    result["win_rate"] = result["win_count"] / result["bet_count"]
    result["total_profit"] = df["profit"].sum()
    result["net_profit"] = result["total_profit"] - result["bet_count"] * wager_amount
    result["roi"] = result["net_profit"] / (result["bet_count"] * wager_amount)
    df = df.sort_values(by="date")
    df = df.groupby("date", as_index=False).agg({
        "profit": "sum",
        "is_win": "sum",
        "is_found": "sum",
        "is_refound": "sum",
        "is_valid": "sum",
    })
    df["cumulative_profit"] = df["profit"].cumsum()
    result["cumulative_profit"] = df[["date", "cumulative_profit"]].to_dict(orient="records")
    
    result["bet_count"] = int(df["is_found"].sum())
    result["win_count"] = int(df["is_win"].sum())
    result["win_rate"] = float(result["win_count"] / result["bet_count"])
    result["total_profit"] = float(df["profit"].sum())
    result["net_profit"] = float(result["total_profit"] - result["bet_count"] * wager_amount)
    result["roi"] = float(result["net_profit"] / (result["bet_count"] * wager_amount))
    result["cumulative_profit"] = [
        {
            "date": row["date"].date().isoformat(),
            "cumulative_profit": float(row["cumulative_profit"]),
        }        
        for row in df[["date", "cumulative_profit"]].to_dict(orient="records")
    ]

    with session:
        update_model_evaluation_metircs(session, "model_evaluation", dict(result))
    
    return result