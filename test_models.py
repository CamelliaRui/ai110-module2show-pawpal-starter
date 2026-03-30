from datetime import time
from pawpal_system import Task, Pet, Owner, Scheduler


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
    owner = Owner("Jordan", [pet], time(7, 0), time(8, 0))  # 60 min
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
    owner = Owner("Jordan", [pet], time(7, 0), time(7, 30))  # 30 min
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
