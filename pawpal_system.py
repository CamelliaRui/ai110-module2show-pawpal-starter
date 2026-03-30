from dataclasses import dataclass, field
from datetime import time, timedelta, datetime
from typing import List


@dataclass
class Task:
    """Represents a single pet care activity with priority, frequency, and completion status."""

    title: str
    duration_minutes: int
    priority: str  # "high", "medium", "low"
    category: str = ""
    frequency: str = "daily"  # "daily", "weekly", "as_needed"
    completed: bool = False

    def mark_complete(self):
        """Set this task's status to completed."""
        self.completed = True

    def mark_incomplete(self):
        """Reset this task's status to pending."""
        self.completed = False

    def __repr__(self):
        status = "done" if self.completed else "pending"
        return f"Task({self.title!r}, {self.duration_minutes}min, {self.priority}, {status})"


@dataclass
class Pet:
    """Stores pet details and manages its list of care tasks."""

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str):
        """Remove a task by title from this pet."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_pending_tasks(self) -> List[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    """Manages multiple pets and defines the daily available time window."""

    name: str
    pets: List[Pet] = field(default_factory=list)
    start_time: time = time(7, 0)
    end_time: time = time(9, 0)

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's collection."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_all_pending_tasks(self) -> List[Task]:
        """Return all pending tasks across all pets."""
        pending = []
        for pet in self.pets:
            pending.extend(pet.get_pending_tasks())
        return pending

    def available_minutes(self) -> int:
        """Calculate total available minutes from the time window."""
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        return int((end - start).total_seconds() / 60)


@dataclass
class ScheduledTask:
    """A task assigned to a specific time slot in the daily schedule."""

    task: Task
    pet_name: str
    start_time: time
    end_time: time
    reason: str

    def __repr__(self):
        start_str = self.start_time.strftime("%-I:%M %p")
        end_str = self.end_time.strftime("%-I:%M %p")
        return f"{start_str} - {end_str}: {self.task.title} for {self.pet_name} ({self.reason})"


@dataclass
class Schedule:
    """The result of scheduling: a list of time-slotted tasks with capacity info."""

    scheduled_tasks: List[ScheduledTask] = field(default_factory=list)
    over_capacity: bool = False
    total_minutes: int = 0
    available_minutes: int = 0

    def display(self) -> str:
        """Return a formatted string of the full schedule with warnings."""
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
    """The brain: retrieves tasks from the Owner's pets, organizes and schedules them."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_schedule(self) -> Schedule:
        """Build a daily schedule from all pending tasks, sorted by priority."""
        tasks_with_pets = self._gather_tasks()
        sorted_tasks = self._sort_by_priority(tasks_with_pets)
        scheduled = self._assign_time_slots(sorted_tasks)
        total = sum(t.duration_minutes for t, _ in tasks_with_pets)
        available = self.owner.available_minutes()
        over_capacity = total > available
        return Schedule(scheduled, over_capacity, total, available)

    def _gather_tasks(self) -> List[tuple]:
        """Retrieve all pending tasks from the Owner's pets, paired with pet name."""
        tasks_with_pets = []
        for pet in self.owner.pets:
            for task in pet.get_pending_tasks():
                tasks_with_pets.append((task, pet.name))
        return tasks_with_pets

    def _sort_by_priority(self, tasks_with_pets: List[tuple]) -> List[tuple]:
        """Sort task-pet pairs by priority: high first, then medium, then low."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks_with_pets, key=lambda tp: priority_order.get(tp[0].priority, 3))

    def _assign_time_slots(self, tasks_with_pets: List[tuple]) -> List[ScheduledTask]:
        """Assign sequential time slots starting from the owner's start time."""
        scheduled = []
        current = datetime.combine(datetime.today(), self.owner.start_time)
        for i, (task, pet_name) in enumerate(tasks_with_pets):
            start = current.time()
            current += timedelta(minutes=task.duration_minutes)
            end = current.time()
            rank = i + 1
            reason = f"{task.priority} priority, scheduled #{rank}"
            scheduled.append(ScheduledTask(task, pet_name, start, end, reason))
        return scheduled
