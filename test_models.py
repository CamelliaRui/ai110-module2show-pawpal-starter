from datetime import time, date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# --- Priority & Time Slot Tests ---

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


def test_time_slots_are_sequential():
    """Each task starts where the previous one ended."""
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


def test_empty_tasks():
    """Scheduler handles no tasks gracefully."""
    pet = Pet("Mochi", "dog")
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert schedule.scheduled_tasks == []
    assert schedule.over_capacity is False
    assert schedule.total_minutes == 0


def test_available_minutes():
    """Owner correctly calculates available time."""
    owner = Owner("Jordan", [], time(7, 0), time(9, 30))
    assert owner.available_minutes() == 150


def test_display_includes_warning_when_over_capacity():
    """Display output includes a warning when over capacity."""
    pet = Pet("Mochi", "dog", [Task("Walk", 40, "high")])
    owner = Owner("Jordan", [pet], time(7, 0), time(7, 30))
    schedule = Scheduler(owner).generate_schedule()
    output = schedule.display()
    assert "Warning" in output
    assert "40 minutes" in output
    assert "30 minutes" in output


def test_reason_includes_priority():
    """Each scheduled task's reason mentions its priority."""
    pet = Pet("Mochi", "dog", [Task("Walk", 20, "high")])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert "high priority" in schedule.scheduled_tasks[0].reason


def test_multiple_pets():
    """Tasks from multiple pets are gathered and scheduled together."""
    mochi = Pet("Mochi", "dog", [Task("Walk Mochi", 20, "high")])
    mocha = Pet("Mocha", "cat", [Task("Feed Mocha", 10, "medium")])
    owner = Owner("Jordan", [mochi, mocha], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert len(schedule.scheduled_tasks) == 2
    assert schedule.scheduled_tasks[0].pet_name == "Mochi"
    assert schedule.scheduled_tasks[1].pet_name == "Mocha"


def test_completed_tasks_excluded():
    """Completed tasks are not included in the schedule."""
    walk = Task("Walk", 20, "high")
    feed = Task("Feed", 10, "high")
    walk.mark_complete()
    pet = Pet("Mochi", "dog", [walk, feed])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert len(schedule.scheduled_tasks) == 1
    assert schedule.scheduled_tasks[0].task.title == "Feed"


def test_pet_add_remove_task():
    """Pet can add and remove tasks."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 20, "high"))
    pet.add_task(Task("Feed", 10, "medium"))
    assert len(pet.tasks) == 2
    pet.remove_task("Walk")
    assert len(pet.tasks) == 1
    assert pet.tasks[0].title == "Feed"


def test_scheduled_task_includes_pet_name():
    """ScheduledTask repr includes the pet name."""
    pet = Pet("Mochi", "dog", [Task("Walk", 20, "high")])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert "Mochi" in repr(schedule.scheduled_tasks[0])


# --- Sorting Tests ---

def test_sort_by_time():
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


def test_sort_by_priority_and_time():
    """Within the same priority, tasks are sorted by scheduled_time."""
    pet = Pet("Mochi", "dog", [
        Task("Late walk", 20, "high", scheduled_time=time(8, 0)),
        Task("Early walk", 20, "high", scheduled_time=time(7, 0)),
    ])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    titles = [st.task.title for st in schedule.scheduled_tasks]
    assert titles == ["Early walk", "Late walk"]


# --- Filtering Tests ---

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


# --- Recurring Task Tests ---

def test_mark_complete_daily_creates_next():
    """Completing a daily task creates a new instance due tomorrow."""
    task = Task("Walk", 20, "high", frequency="daily", due_date=date.today())
    next_task = task.mark_complete()
    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=1)


def test_mark_complete_weekly_creates_next():
    """Completing a weekly task creates a new instance due in 7 days."""
    task = Task("Grooming", 30, "low", frequency="weekly", due_date=date.today())
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=7)


def test_mark_complete_as_needed_no_next():
    """Completing an as_needed task does not create a next occurrence."""
    task = Task("Vet visit", 60, "high", frequency="as_needed")
    next_task = task.mark_complete()
    assert task.completed is True
    assert next_task is None


def test_pet_complete_task_adds_next():
    """Pet.complete_task() marks done and adds next occurrence to pet's task list."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 20, "high", frequency="daily", due_date=date.today()))
    assert len(pet.tasks) == 1
    pet.complete_task("Walk")
    assert len(pet.tasks) == 2
    assert pet.tasks[0].completed is True
    assert pet.tasks[1].completed is False


# --- Conflict Detection Tests ---

def test_no_conflicts_sequential():
    """Sequential tasks should not produce conflicts."""
    pet = Pet("Mochi", "dog", [
        Task("Walk", 20, "high"),
        Task("Feed", 10, "high"),
    ])
    owner = Owner("Jordan", [pet], time(7, 0), time(9, 0))
    schedule = Scheduler(owner).generate_schedule()
    assert schedule.conflicts == []


def test_conflict_detected_over_capacity():
    """Over-capacity schedule reports conflict info in display."""
    pet = Pet("Buddy", "dog", [
        Task("Walk", 30, "high"),
        Task("Vet", 30, "high"),
    ])
    owner = Owner("Alex", [pet], time(10, 0), time(10, 30))
    schedule = Scheduler(owner).generate_schedule()
    assert schedule.over_capacity is True
    # Sequential assignment means no time overlap, just over-capacity
    assert schedule.total_minutes == 60
    assert schedule.available_minutes == 30
