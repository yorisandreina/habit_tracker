import os
import sqlite3
from typing import List, Optional
from datetime import datetime, timedelta
from .models import HabitEntity, CompletionRecord
from .repository import HabitRepository

DEFAULT_HABITS = [
    # name, periodicity, category
    ("Drink Water", "daily", "health"),
    ("Morning Stretch", "daily", "wellness"),
    ("Read a Book", "daily", "personal dev"),
    ("Weekly Planning", "weekly", "productivity"),
    ("Grocery Shopping", "weekly", "errands"),
]

class SQLiteHabitRepository(HabitRepository):
    """SQLite-backed implementation of HabitRepository."""
    def __init__(self, db_path: str = "data/habits.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialize_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _initialize_db(self) -> None:
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  periodicity TEXT NOT NULL,
                  category TEXT NOT NULL,
                  created TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS completions (
                  id INTEGER NOT NULL,
                  timestamp TEXT NOT NULL,
                  FOREIGN KEY(id) REFERENCES habits(id)
                )
            """)

    def add(self, habit: HabitEntity) -> HabitEntity:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO habits (name, periodicity, category, created) VALUES (?, ?, ?, ?)",
                (habit.name, habit.periodicity, habit.category, habit.created.isoformat())
            )
            habit.id = cur.lastrowid
            for comp in habit.completions:
                conn.execute(
                    "INSERT INTO completions (id, timestamp) VALUES (?, ?)",
                    (habit.id, comp.timestamp.isoformat())
                )
            conn.commit()
        return habit

    def get_all(self) -> List[HabitEntity]:
        habits: List[HabitEntity] = []
        with self._get_conn() as conn:
            cur = conn.cursor()
            for row in cur.execute("SELECT id, name, periodicity, category, created FROM habits"):
                h = HabitEntity(
                    id=row[0],
                    name=row[1],
                    periodicity=row[2],
                    category=row[3],
                    created=datetime.fromisoformat(row[4]),
                    completions=[]
                )
                for (ts,) in conn.execute("SELECT timestamp FROM completions WHERE id = ?", (h.id,)):
                    h.completions.append(CompletionRecord(timestamp=datetime.fromisoformat(ts)))
                habits.append(h)
        return habits

    def get_by_id(self, id: int) -> Optional[HabitEntity]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT id, name, periodicity, category, created FROM habits WHERE id = ?",
                (id,)
            ).fetchone()
            if not row:
                return None
            h = HabitEntity(
                id=row[0], name=row[1], periodicity=row[2],
                category=row[3], created=datetime.fromisoformat(row[4]), completions=[]
            )
            for (ts,) in conn.execute("SELECT timestamp FROM completions WHERE id = ?", (id,)):
                h.completions.append(CompletionRecord(timestamp=datetime.fromisoformat(ts)))
            return h

    def update(self, habit: HabitEntity) -> None:
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE habits SET name = ?, periodicity = ?, category = ?, created = ? WHERE id = ?",
                (habit.name, habit.periodicity, habit.category, habit.created.isoformat(), habit.id)
            )
            conn.execute("DELETE FROM completions WHERE id = ?", (habit.id,))
            for comp in habit.completions:
                conn.execute(
                    "INSERT INTO completions (id, timestamp) VALUES (?, ?)",
                    (habit.id, comp.timestamp.isoformat())
                )
            conn.commit()

    def delete(self, id: int) -> None:
        with self._get_conn() as conn:
            conn.execute("DELETE FROM completions WHERE id = ?", (id,))
            conn.execute("DELETE FROM habits WHERE id = ?", (id,))
            conn.commit()

    def add_defaults(self) -> None:
        """
        Insert the five default habits if none exist yet,
        and give them one example completion per period
        over the past 4 weeks.
        """
        # only add if the table is empty
        if self.get_all():
            return
 
        for name, periodicity, category in DEFAULT_HABITS:
            # create a HabitEntity dated four periods ago
            if periodicity == "daily":
                created = datetime.utcnow() - timedelta(days=27)
                # generate one completion per day for 28 days
                completions = [
                    CompletionRecord(timestamp=created + timedelta(days=i))
                    for i in range(28)
                ]
            else:  # weekly
                created = datetime.utcnow() - timedelta(weeks=3)
                # one completion per week for 4 weeks
                completions = [
                    CompletionRecord(timestamp=created + timedelta(weeks=i))
                    for i in range(4)
                ]

            habit = HabitEntity(
                name=name,
                periodicity=periodicity,
                category=category,
                created=created,
                completions=completions
            )
            # this will INSERT into habits & completions
            self.add(habit)
