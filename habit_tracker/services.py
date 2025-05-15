from typing import List, Dict
from datetime import datetime, timedelta
from .models import HabitEntity
from .repository import HabitRepository

class HabitService:
    """High-level operations on habits, delegates persistence to a repository."""
    def __init__(self, repo: HabitRepository):
        self.repo = repo

    def create_habit(self, name: str, periodicity: str, category: str) -> HabitEntity:
        habit = HabitEntity(name=name, periodicity=periodicity, category=category)
        return self.repo.add(habit)

    def record_completion(self, habit_id: int) -> None:
        habit = self.repo.get_by_id(habit_id)
        if not habit:
            raise ValueError(f"Habit with id={habit_id} not found")
        habit.add_completion()
        self.repo.update(habit)

    def list_habits(self) -> List[HabitEntity]:
        return self.repo.get_all()

class AnalyticsService:
    """Pure‐function analytics over HabitEntity objects."""
    def longest_streak(self, habit: HabitEntity) -> int:
        if not habit.completions:
            return 0
        dates = sorted(c.timestamp.date() for c in habit.completions)
        max_streak = streak = 1
        for i in range(1, len(dates)):
            delta = (dates[i] - dates[i - 1]).days if habit.periodicity == "daily" \
                    else (dates[i].isocalendar()[1] - dates[i - 1].isocalendar()[1])
            streak = streak + 1 if delta == 1 else 1
            max_streak = max(max_streak, streak)
        return max_streak

    def current_streak(self, habit: HabitEntity) -> int:
        if not habit.completions:
            return 0
        today = datetime.utcnow().date()
        comp_dates = sorted(c.timestamp.date() for c in habit.completions)[::-1]
        delta = timedelta(days=1) if habit.periodicity == "daily" else timedelta(weeks=1)
        streak = 0
        prev_date = today
        for d in comp_dates:
            if (prev_date - d) <= delta:
                streak += 1
                prev_date = d
            else:
                break
        return streak

    def completion_rate(self, habit: HabitEntity) -> float:
        if not habit.completions:
            return 0.0
        created = habit.created.date()
        today = datetime.utcnow().date()
        if habit.periodicity == "daily":
            total = (today - created).days + 1
        else:
            total = (today.isocalendar()[1] - created.isocalendar()[1]) + 1
        return len(habit.completions) / total if total > 0 else 0.0

    def report(self, habits: List[HabitEntity], period: str) -> Dict[str,bool]:
        today = datetime.utcnow().date()
        result: Dict[str,bool] = {}
        if period == "weekly":
            current_week = today.isocalendar()[1]
            for h in habits:
                result[h.name] = any(c.timestamp.isocalendar()[1] == current_week
                                     for c in h.completions)
        elif period == "monthly":
            current_month = today.month
            for h in habits:
                result[h.name] = any(c.timestamp.month == current_month
                                     for c in h.completions)
        else:
            raise ValueError("`period` must be 'weekly' or 'monthly'")
        return result