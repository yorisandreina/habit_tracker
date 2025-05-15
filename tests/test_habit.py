import pytest

def test_repository_seeding(default_habits, tmp_path):
    """
    Example: ensure that loading from our JSON fixtures yields correct counts.
    """
    from habit_tracker.sqlite_repository import SQLiteHabitRepository
    repo = SQLiteHabitRepository(db_path=str(tmp_path / "test.db"))
    for habit in default_habits:
        repo.add(habit)

    loaded = repo.get_all()
    assert len(loaded) == 5

    daily = [h for h in loaded if h.periodicity == "daily"]
    assert all(len(h.completions) == 28 for h in daily)

    weekly = [h for h in loaded if h.periodicity == "weekly"]
    assert all(len(h.completions) == 4 for h in weekly)

def test_empty_repository(tmp_path):
    from habit_tracker.sqlite_repository import SQLiteHabitRepository
    repo = SQLiteHabitRepository(db_path=str(tmp_path / "empty.db"))
    assert repo.get_all() == []
    assert repo.get_by_id(123) is None

def test_add_and_get_by_id(tmp_path):
    from habit_tracker.sqlite_repository import SQLiteHabitRepository
    from habit_tracker.models import HabitEntity

    repo = SQLiteHabitRepository(db_path=str(tmp_path / "addget.db"))
    habit = HabitEntity(name="Test", periodicity="daily", category="cat")
    saved = repo.add(habit)

    # id should be set
    assert saved.id is not None

    fetched = repo.get_by_id(saved.id)
    assert fetched is not None
    assert fetched.name == "Test"
    assert fetched.periodicity == "daily"
    assert fetched.category == "cat"
    assert fetched.completions == []

def test_update_completions(tmp_path):
    from habit_tracker.sqlite_repository import SQLiteHabitRepository
    from habit_tracker.models import HabitEntity

    repo = SQLiteHabitRepository(db_path=str(tmp_path / "update.db"))
    habit = repo.add(HabitEntity(name="UpTest", periodicity="weekly", category="cat"))

    # record two completions
    habit.add_completion()
    habit.add_completion()
    repo.update(habit)

    reloaded = repo.get_by_id(habit.id)
    assert len(reloaded.completions) == 2

def test_delete_habit(tmp_path):
    from habit_tracker.sqlite_repository import SQLiteHabitRepository
    from habit_tracker.models import HabitEntity

    repo = SQLiteHabitRepository(db_path=str(tmp_path / "del.db"))
    habit = repo.add(HabitEntity(name="DeleteMe", periodicity="daily", category="c"))
    repo.delete(habit.id)

    assert repo.get_by_id(habit.id) is None
    assert all(h.id != habit.id for h in repo.get_all())

def test_analytics_longest_streak(default_habits):
    from habit_tracker.services import AnalyticsService

    svc = AnalyticsService()
    for h in default_habits:
        expected = 28 if h.periodicity == "daily" else 4
        assert svc.longest_streak(h) == expected

def test_analytics_current_streak():
    from habit_tracker.services import AnalyticsService
    from habit_tracker.models import HabitEntity, CompletionRecord
    from datetime import datetime, timedelta

    # simulate a daily habit that has three most-recent consecutive completions
    h = HabitEntity(name="C", periodicity="daily", category="cat")
    today = datetime.utcnow().date()
    # last 3 days
    h.completions = [
        CompletionRecord(timestamp=datetime.combine(today - timedelta(days=i), datetime.min.time()))
        for i in [0, 1, 2]
    ]
    svc = AnalyticsService()
    assert svc.current_streak(h) == 3

def test_analytics_completion_rate():
    from habit_tracker.services import AnalyticsService
    from habit_tracker.models import HabitEntity, CompletionRecord
    from datetime import datetime, timedelta

    # 5-day old daily habit with 3 completions
    h = HabitEntity(name="R", periodicity="daily", category="c",
                    created=datetime.utcnow() - timedelta(days=4))
    for offset in [0, 2, 4]:
        h.completions.append(CompletionRecord(timestamp=datetime.utcnow() - timedelta(days=offset)))

    svc = AnalyticsService()
    rate = svc.completion_rate(h)
    assert abs(rate - (3/5)) < 1e-6

def test_analytics_report(default_habits):
    from habit_tracker.services import AnalyticsService

    svc = AnalyticsService()
    weekly = svc.report(default_habits, "weekly")
    monthly = svc.report(default_habits, "monthly")

    # Ensure every habit appears in the report
    expected_names = {h.name for h in default_habits}
    assert set(weekly.keys()) == expected_names
    assert set(monthly.keys()) == expected_names

    # Each value should be a boolean
    assert all(isinstance(v, bool) for v in weekly.values())
    assert all(isinstance(v, bool) for v in monthly.values())

    # Invalid period should raise
    with pytest.raises(ValueError):
        svc.report(default_habits, "yearly")
