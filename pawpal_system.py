from dataclasses import dataclass, field
from datetime import time, timedelta, datetime
from typing import List


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "high", "medium", "low"
    category: str = ""

    def __repr__(self):
        return f"Task({self.title!r}, {self.duration_minutes}min, {self.priority})"


@dataclass
class Owner:
    name: str
    pet_name: str
    species: str
    start_time: time
    end_time: time

    def available_minutes(self) -> int:
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        return int((end - start).total_seconds() / 60)


@dataclass
class ScheduledTask:
    task: Task
    start_time: time
    end_time: time
    reason: str

    def __repr__(self):
        start_str = self.start_time.strftime("%-I:%M %p")
        end_str = self.end_time.strftime("%-I:%M %p")
        return f"{start_str} - {end_str}: {self.task.title} ({self.reason})"


@dataclass
class Schedule:
    scheduled_tasks: List[ScheduledTask] = field(default_factory=list)
    over_capacity: bool = False
    total_minutes: int = 0
    available_minutes: int = 0

    def display(self) -> str:
        lines = []
        for st in self.scheduled_tasks:
            lines.append(repr(st))
        if self.over_capacity:
            lines.append(
                f"\nWarning: Tasks total {self.total_minutes} minutes "
                f"but only {self.available_minutes} minutes available."
            )
        return "\n".join(lines)


class Scheduler:
    def __init__(self, owner: Owner, tasks: List[Task]):
        self.owner = owner
        self.tasks = tasks

    def generate_schedule(self) -> Schedule:
        sorted_tasks = self._sort_by_priority(self.tasks)
        scheduled = self._assign_time_slots(sorted_tasks)
        total = sum(t.duration_minutes for t in self.tasks)
        available = self.owner.available_minutes()
        over_capacity = self._check_capacity()
        return Schedule(scheduled, over_capacity, total, available)

    def _sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda t: priority_order.get(t.priority, 3))

    def _assign_time_slots(self, tasks: List[Task]) -> List[ScheduledTask]:
        scheduled = []
        current = datetime.combine(datetime.today(), self.owner.start_time)
        for i, task in enumerate(tasks):
            start = current.time()
            current += timedelta(minutes=task.duration_minutes)
            end = current.time()
            rank = i + 1
            reason = f"{task.priority} priority, scheduled #{rank}"
            scheduled.append(ScheduledTask(task, start, end, reason))
        return scheduled

    def _check_capacity(self) -> bool:
        total = sum(t.duration_minutes for t in self.tasks)
        return total > self.owner.available_minutes()
