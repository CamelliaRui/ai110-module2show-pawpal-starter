"""
Automated test suite for PawPal+ scheduling system.

Covers:
- Task completion and status changes
- Pet task management (add/remove)
- Priority-based sorting
- Time-based sorting
- Sequential time slot assignment
- Filtering by pet and status
- Recurring task generation (daily, weekly, as_needed)
- Conflict detection
- Over-capacity warnings
- Edge cases (no tasks, no pets, all completed, duplicate times)
"""

from datetime import time, date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ============================================================
# Happy Path: Task Basics
# ============================================================

def test_mark_complete_changes_status():
    """Verify that calling mark_complete() changes the task's status."""
    task = Task("Walk", 20, "high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_mark_incomplete_changes_status():
    """Verify that mark_incomplete() reverts a completed task."""
    task = Task("Walk", 20, "high")
    task.mark_complete()
    task.mark_incomplete()
    assert task.completed is False


def test_adding_task_increases_pet_task_count():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", 20, "high"))
    assert len(pet.tasks) == 1
    pet.add_task(Task("Feed", 10, "medium"))
    assert len(pet.tasks) == 2


def test_pet_add_remove_task():
    """Pet can add and remove tasks by title."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 20, "high"))
    pet.add_task(Task("Feed", 10, "medium"))
    assert len(pet.tasks) == 2
    pet.remove_task("Walk")
    assert len(pet.tasks) == 1
    assert pet.tasks[0].title == "Feed"


# ============================================================
# Happy Path: Sorting
# ============================================================

def test_strict_priority_ordering():
    """High tasks come before medium, medium before low."""
    pet = Pet("Mochi", "dog", [
        Task("Grooming", 30, "low"),
        Task("Play time", 25, "medium"),
        Task("Morning walk", 20, "high"),
    ])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    titles = [st.task.title for st in schedule.scheduled_tasks]
    assert titles == ["Morning walk", "Play time", "Grooming"]


def test_sort_by_time_chronological():
    """Tasks are sorted by scheduled_time; tasks without time go last."""
    pet = Pet("Mochi", "dog", [
        Task("Grooming", 30, "low", scheduled_time=time(9, 0)),
        Task("Walk", 20, "high", scheduled_time=time(7, 0)),
        Task("Feed", 10, "high"),  # no scheduled_time
    ])
    owner = Owner("Jordan", [pet], time(7, 0), time(10, 0))
    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time(scheduler._gather_tasks())
    titles = [t.title for t, _ in sorted_tasks]
    assert titles == ["Walk", "Grooming", "Feed"]


def test_sort_by_priority_then_time():
    """Within the same priority, tasks are sorted by scheduled_time."""
    pet = Pet("Mochi", "dog", [
        Task("Late walk", 20, "high", scheduled_time=time(8, 0)),
        Task("Early walk", 20, "high", scheduled_time=time(7, 0)),
    ])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    titles = [st.task.title for st in schedule.scheduled_tasks]
    assert titles == ["Early walk", "Late walk"]


def test_time_slots_are_sequential():
    """Each task starts exactly where the previous one ended."""
    pet = Pet("Mochi", "dog", [
        Task("Walk", 20, "high"),
        Task("Feed", 10, "high"),
    ])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert schedule.scheduled_tasks[0].start_time == time(7, 0)
    assert schedule.scheduled_tasks[0].end_time == time(7, 20)
    assert schedule.scheduled_tasks[1].start_time == time(7, 20)
    assert schedule.scheduled_tasks[1].end_time == time(7, 30)


# ============================================================
# Happy Path: Filtering
# ============================================================

def test_filter_by_pet():
    """Filter returns only tasks for the specified pet."""
    mochi = Pet("Mochi", "dog", [Task("Walk", 20, "high")])
    mocha = Pet("Mocha", "cat", [Task("Feed", 10, "high")])
    owner = Owner("Jordan", [mochi, mocha], time(7, 0), time(9, 0))
    result = Scheduler(owner).filter_by_pet("Mochi")
    assert len(result) == 1
    assert result[0][0].title == "Walk"


def test_filter_by_status():
    """Filter by completion status returns correct tasks."""
    walk = Task("Walk", 20, "high")
    feed = Task("Feed", 10, "high")
    walk.mark_complete()
    pet = Pet("Mochi", "dog", [walk, feed])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    scheduler = Scheduler(owner)
    completed = scheduler.filter_by_status(completed=True)
    pending = scheduler.filter_by_status(completed=False)
    assert len(completed) == 1
    assert completed[0][0].title == "Walk"
    assert len(pending) == 1
    assert pending[0][0].title == "Feed"


def test_completed_tasks_excluded_from_schedule():
    """Completed tasks are not included in the generated schedule."""
    walk = Task("Walk", 20, "high")
    feed = Task("Feed", 10, "high")
    walk.mark_complete()
    pet = Pet("Mochi", "dog", [walk, feed])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert len(schedule.scheduled_tasks) == 1
    assert schedule.scheduled_tasks[0].task.title == "Feed"


# ============================================================
# Happy Path: Recurring Tasks
# ============================================================

def test_daily_task_creates_next_occurrence():
    """Completing a daily task creates a new instance due tomorrow."""
    task = Task("Walk", 20, "high", frequency="daily", due_date=date.today())
    next_task = task.mark_complete()
    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=1)


def test_weekly_task_creates_next_occurrence():
    """Completing a weekly task creates a new instance due in 7 days."""
    task = Task("Grooming", 30, "low", frequency="weekly", due_date=date.today())
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=7)


def test_as_needed_task_no_recurrence():
    """Completing an as_needed task does not create a next occurrence."""
    task = Task("Vet visit", 60, "high", frequency="as_needed")
    next_task = task.mark_complete()
    assert task.completed is True
    assert next_task is None


def test_recurring_task_preserves_attributes():
    """Next occurrence keeps the same title, duration, priority, and frequency."""
    task = Task("Medication", 5, "high", category="meds", frequency="daily",
                scheduled_time=time(7, 0), due_date=date.today())
    next_task = task.mark_complete()
    assert next_task.title == "Medication"
    assert next_task.duration_minutes == 5
    assert next_task.priority == "high"
    assert next_task.category == "meds"
    assert next_task.frequency == "daily"
    assert next_task.scheduled_time == time(7, 0)


def test_pet_complete_task_adds_next_to_list():
    """Pet.complete_task() marks done and adds next occurrence to the pet's task list."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 20, "high", frequency="daily", due_date=date.today()))
    assert len(pet.tasks) == 1
    pet.complete_task("Walk")
    assert len(pet.tasks) == 2
    assert pet.tasks[0].completed is True
    assert pet.tasks[1].completed is False


# ============================================================
# Happy Path: Conflict Detection & Capacity
# ============================================================

def test_no_conflicts_when_sequential():
    """Sequential tasks should produce zero conflicts."""
    pet = Pet("Mochi", "dog", [
        Task("Walk", 20, "high"),
        Task("Feed", 10, "high"),
    ])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert schedule.conflicts == []


def test_over_capacity_flag():
    """Schedule is flagged when tasks exceed available time."""
    pet = Pet("Mochi", "dog", [
        Task("Walk", 40, "high"),
        Task("Play", 30, "medium"),
    ])
    owner = Owner("Jordan", [pet], time(7, 0), time(8, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert schedule.over_capacity is True
    assert schedule.total_minutes == 70
    assert schedule.available_minutes == 60


def test_not_over_capacity():
    """No flag when tasks fit within the window."""
    pet = Pet("Mochi", "dog", [Task("Walk", 20, "high")])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert schedule.over_capacity is False


def test_display_includes_warning_when_over_capacity():
    """Display output includes warning text when over capacity."""
    pet = Pet("Mochi", "dog", [Task("Walk", 40, "high")])
    owner = Owner("Jordan", [pet], time(7, 0), time(7, 30))
    schedule = Scheduler(owner).generate_schedule()
    output = schedule.display()
    assert "Warning" in output
    assert "40 minutes" in output
    assert "30 minutes" in output


def test_multiple_pets_scheduled_together():
    """Tasks from multiple pets are gathered and scheduled by priority."""
    mochi = Pet("Mochi", "dog", [Task("Walk Mochi", 20, "high")])
    mocha = Pet("Mocha", "cat", [Task("Feed Mocha", 10, "medium")])
    owner = Owner("Jordan", [mochi, mocha], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert len(schedule.scheduled_tasks) == 2
    assert schedule.scheduled_tasks[0].pet_name == "Mochi"
    assert schedule.scheduled_tasks[1].pet_name == "Mocha"


def test_scheduled_task_includes_pet_name():
    """ScheduledTask repr includes the pet name."""
    pet = Pet("Mochi", "dog", [Task("Walk", 20, "high")])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert "Mochi" in repr(schedule.scheduled_tasks[0])


def test_reason_includes_priority():
    """Each scheduled task's reason mentions its priority level."""
    pet = Pet("Mochi", "dog", [Task("Walk", 20, "high")])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert "high priority" in schedule.scheduled_tasks[0].reason


def test_available_minutes_calculation():
    """Owner correctly calculates available minutes from time window."""
    owner = Owner("Jordan", [], time(7, 0), time(9, 30))
    assert owner.available_minutes() == 150


# ============================================================
# Edge Cases
# ============================================================

def test_pet_with_no_tasks():
    """A pet with zero tasks produces an empty schedule."""
    pet = Pet("Mochi", "dog")
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert schedule.scheduled_tasks == []
    assert schedule.over_capacity is False
    assert schedule.total_minutes == 0


def test_owner_with_no_pets():
    """An owner with no pets produces an empty schedule."""
    owner = Owner("Jordan", [], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert schedule.scheduled_tasks == []
    assert schedule.total_minutes == 0


def test_all_tasks_completed():
    """If every task is completed, the schedule is empty."""
    walk = Task("Walk", 20, "high")
    feed = Task("Feed", 10, "high")
    walk.mark_complete()
    feed.mark_complete()
    pet = Pet("Mochi", "dog", [walk, feed])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert schedule.scheduled_tasks == []
    assert schedule.total_minutes == 0


def test_two_tasks_same_scheduled_time():
    """Two tasks with the exact same scheduled_time are both included."""
    pet = Pet("Mochi", "dog", [
        Task("Walk", 20, "high", scheduled_time=time(7, 0)),
        Task("Medication", 5, "high", scheduled_time=time(7, 0)),
    ])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert len(schedule.scheduled_tasks) == 2


def test_filter_by_nonexistent_pet():
    """Filtering by a pet name that doesn't exist returns empty list."""
    pet = Pet("Mochi", "dog", [Task("Walk", 20, "high")])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    result = Scheduler(owner).filter_by_pet("Ghost")
    assert result == []


def test_complete_nonexistent_task():
    """Completing a task title that doesn't exist returns None."""
    pet = Pet("Mochi", "dog", [Task("Walk", 20, "high")])
    result = pet.complete_task("Nonexistent")
    assert result is None
    assert len(pet.tasks) == 1  # original task unchanged


def test_single_task_fills_entire_window():
    """A single task that exactly fills the time window is not over capacity."""
    pet = Pet("Mochi", "dog", [Task("Long walk", 60, "high")])
    owner = Owner("Jordan", [pet], time(7, 0), time(8, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert schedule.over_capacity is False
    assert schedule.total_minutes == 60
    assert schedule.available_minutes == 60


def test_display_shows_conflicts():
    """Display output includes conflict text when conflicts exist."""
    from pawpal_system import Schedule, ScheduledTask
    # Manually create overlapping scheduled tasks
    t1 = Task("Walk", 30, "high")
    t2 = Task("Feed", 30, "high")
    st1 = ScheduledTask(t1, "Mochi", time(7, 0), time(7, 30), "high priority, scheduled #1")
    st2 = ScheduledTask(t2, "Mochi", time(7, 15), time(7, 45), "high priority, scheduled #2")
    schedule = Schedule([st1, st2], False, 60, 120,
                        ['"Walk" (Mochi) and "Feed" (Mochi) overlap'])
    output = schedule.display()
    assert "Conflict" in output
    assert "overlap" in output
