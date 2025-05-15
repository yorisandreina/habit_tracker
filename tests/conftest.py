import json
from pathlib import Path
import pytest
from datetime import datetime
from habit_tracker.models import HabitEntity, CompletionRecord

@pytest.fixture
def default_habits():
    """Load the 5 predefined habits (with 4 weeks of completions) from JSON."""
    path = Path(__file__).parent / "default_habits.json"
    raw = json.loads(path.read_text())
    habits = []
    for entry in raw["habits"]:
        # parse creation timestamp
        created = datetime.fromisoformat(entry["created"])
        # parse completions
        comps = [CompletionRecord(timestamp=datetime.fromisoformat(ts))
                 for ts in entry["completions"]]
        habit = HabitEntity(
            name=entry["name"],
            periodicity=entry["periodicity"],
            category=entry["category"],
            created=created,
            completions=comps
        )
        habits.append(habit)
    return habits
