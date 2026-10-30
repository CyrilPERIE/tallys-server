from datetime import timedelta
import datetime
from pmu.dates import date_to_programme_date, programme_date_to_date

class CourseIdentifier: 
    def __init__(self, course_num: int, reunion_num: int, programme: str):
        self.course_num = course_num
        self.reunion_num = reunion_num
        self.programme = programme

    def __str__(self) -> str:
        return f"{self.programme}/R{self.reunion_num}/C{self.course_num}"

    def __lt__(self, other: 'CourseIdentifier') -> bool:
        return ReunionIdentifier(self.reunion_num, self.programme) < ReunionIdentifier(other.reunion_num, other.programme) or (ReunionIdentifier(self.reunion_num, self.programme) == ReunionIdentifier(other.reunion_num, other.programme) and self.course_num < other.course_num)

    def __le__(self, other: 'CourseIdentifier') -> bool:
        return ReunionIdentifier(self.reunion_num, self.programme) <= ReunionIdentifier(other.reunion_num, other.programme) or (ReunionIdentifier(self.reunion_num, self.programme) == ReunionIdentifier(other.reunion_num, other.programme) and self.course_num <= other.course_num)

    def __gt__(self, other: 'CourseIdentifier') -> bool:
        return ReunionIdentifier(self.reunion_num, self.programme) > ReunionIdentifier(other.reunion_num, other.programme) or (ReunionIdentifier(self.reunion_num, self.programme) == ReunionIdentifier(other.reunion_num, other.programme) and self.course_num > other.course_num)

    def __ge__(self, other: 'CourseIdentifier') -> bool:
        return ReunionIdentifier(self.reunion_num, self.programme) >= ReunionIdentifier(other.reunion_num, other.programme) or (ReunionIdentifier(self.reunion_num, self.programme) == ReunionIdentifier(other.reunion_num, other.programme) and self.course_num >= other.course_num)

    def is_in_past_days(self) -> bool:
        return ProgrammeIdentifier(self.programme) < ProgrammeIdentifier(date_to_programme_date(datetime.date.today()))

class ReunionIdentifier:
    def __init__(self, reunion_num: int, programme: str):
        self.reunion_num = reunion_num
        self.programme = programme

    def __str__(self) -> str:
        return f"{self.programme}/R{self.reunion_num}"

    def __lt__(self, other: 'ReunionIdentifier') -> bool:
        return ProgrammeIdentifier(self.programme) < ProgrammeIdentifier(other.programme) or (ProgrammeIdentifier(self.programme) == ProgrammeIdentifier(other.programme) and self.reunion_num < other.reunion_num)

    def __le__(self, other: 'ReunionIdentifier') -> bool:
        return ProgrammeIdentifier(self.programme) <= ProgrammeIdentifier(other.programme) or (ProgrammeIdentifier(self.programme) == ProgrammeIdentifier(other.programme) and self.reunion_num <= other.reunion_num)

    def __gt__(self, other: 'ReunionIdentifier') -> bool:
        return ProgrammeIdentifier(self.programme) > ProgrammeIdentifier(other.programme) or (ProgrammeIdentifier(self.programme) == ProgrammeIdentifier(other.programme) and self.reunion_num > other.reunion_num)

    def __ge__(self, other: 'ReunionIdentifier') -> bool:
        return ProgrammeIdentifier(self.programme) >= ProgrammeIdentifier(other.programme) or (ProgrammeIdentifier(self.programme) == ProgrammeIdentifier(other.programme) and self.reunion_num >= other.reunion_num)

class ProgrammeIdentifier:
    def __init__(self, programme: str):
        self.programme = programme

    def __str__(self) -> str:
        return self.programme

    def __lt__(self, other: 'ProgrammeIdentifier') -> bool:
        return programme_date_to_date(self.programme) < programme_date_to_date(other.programme)

    def __le__(self, other: 'ProgrammeIdentifier') -> bool:
        return programme_date_to_date(self.programme) <= programme_date_to_date(other.programme)

    def __gt__(self, other: 'ProgrammeIdentifier') -> bool:
        return programme_date_to_date(self.programme) > programme_date_to_date(other.programme)

    def __ge__(self, other: 'ProgrammeIdentifier') -> bool:
        return programme_date_to_date(self.programme) >= programme_date_to_date(other.programme)

    def __eq__(self, other: 'ProgrammeIdentifier') -> bool:
        return self.programme == other.programme

    def increment(self) -> 'ProgrammeIdentifier':
        return ProgrammeIdentifier(date_to_programme_date(programme_date_to_date(self.programme) + timedelta(days=1)))

    