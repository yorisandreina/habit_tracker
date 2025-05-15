from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class CompletionRecord:
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
@dataclass
class HabitEntity:
    name: str
    periodicity: str
    category: str
    id: Optional[int] = None
    created: datetime = field(default_factory=datetime.utcnow)
    completions: List[CompletionRecord] = field(default_factory=list)
    
    def add_completion(self) -> None:
        """Record a new completion at the current time."""
        self.completions.append(CompletionRecord())
