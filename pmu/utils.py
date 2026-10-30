from datetime import date, datetime
from typing import List, TYPE_CHECKING, TypedDict

from pmu.types.api_types import Course
from pmu.types.enum import BetType
from pmu.types.types import CourseIdentifier
from service.rapport import get_rapport_by_course_and_bet_type
from service.utils.deps import get_session
if TYPE_CHECKING:
    from pmu.types.types import ProgrammeIdentifier

def is_arrivee_definitive(course: Course) -> bool:
    return "arriveeDefinitive" in course.keys() and course["arriveeDefinitive"] == True

def is_course_annulee(course: Course) -> bool:
    return "statut" in course.keys() and course["statut"] == "COURSE_ANNULEE"

def programme_dates_between_dates(start_date: "ProgrammeIdentifier", end_date: "ProgrammeIdentifier") -> "List[ProgrammeIdentifier]":    
    programmes = []
    current_date = start_date
    while current_date <= end_date:
        programmes.append(current_date)
        current_date = current_date.increment()
    return programmes

class EvaluateBetReturnType(TypedDict):
    is_found: bool
    is_win: bool
    profit: float
    is_refound: bool
    is_valid: bool

def evaluate_bet(CourseIdentifier: CourseIdentifier, bet_type: BetType, combinaison: list[int], wager_amount: int = 1) -> EvaluateBetReturnType:
    session = get_session()
    rapports = None
    raw = None
    with session:
        rapport = get_rapport_by_course_and_bet_type(CourseIdentifier, bet_type, session)
        if rapport is None:
            return {"is_found": False, "is_win": False, "profit": 0, "is_refound": False, "is_valid": True}
        raw = rapport.raw
        if raw["rembourse"] == "true":
            return {"is_found": True, "is_win": False, "profit": 0, "is_refound": True, "is_valid": True}
        rapports = raw["rapports"]
    base_wager_amount = raw["miseBase"]
    if wager_amount * 100 < base_wager_amount:
        return {"is_found": True, "is_win": False, "profit": 0, "is_refound": True, "is_valid": False}
    
    for r in rapports:
        if sorted(r["combinaison"]) == sorted(combinaison):
            dividend = r["dividendePourUnEuro"]
            return {"is_found": True, "is_win": True, "profit": dividend / 100 * wager_amount - wager_amount, "is_refound": False, "is_valid": True}
    return {"is_found": True, "is_win": False, "profit": - wager_amount, "is_refound": False, "is_valid": True}
    
    