import random
from models import Participant
from models.course import Course


def predict(course: Course) -> list[Participant]:
    return [random.choice(course.participants)]
