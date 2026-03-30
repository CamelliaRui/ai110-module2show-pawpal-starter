from datetime import time
from pawpal_system import Task, Owner, Scheduler


def test_strict_priority_ordering():
    """High tasks come before medium, medium before low."""
    owner = Owner("Jordan", "Mochi", "dog", time(7, 0), time(9, 0))
    tasks = [
        Task("Grooming", 30, "low"),
        Task("Play time", 25, "medium"),
        Task("Morning walk", 20, "high"),
    ]
    schedule = Scheduler(owner, tasks).generate_schedule()
    titles = [st.task.title for st in schedule.scheduled_tasks]
    assert titles == ["Morning walk", "Play time", "Grooming"]


def test_time_slots_are_sequential():
    """Each task starts where the previous one ended."""
    owner = Owner("Jordan", "Mochi", "dog", time(7, 0), time(9, 0))
    tasks = [
        Task("Walk", 20, "high"),
        Task("Feed", 10, "high"),
    ]
    schedule = Scheduler(owner, tasks).generate_schedule()
    assert schedule.scheduled_tasks[0].start_time == time(7, 0)
    assert schedule.scheduled_tasks[0].end_time == time(7, 20)
    assert schedule.scheduled_tasks[1].start_time == time(7, 20)
    assert schedule.scheduled_tasks[1].end_time == time(7, 30)


def test_over_capacity_flag():
    """Schedule is flagged when tasks exceed available time."""
    owner = Owner("Jordan", "Mochi", "dog", time(7, 0), time(8, 0))  # 60 min
    tasks = [
        Task("Walk", 40, "high"),
        Task("Play", 30, "medium"),
    ]
    schedule = Scheduler(owner, tasks).generate_schedule()
    assert schedule.over_capacity is True
    assert schedule.total_minutes == 70
    assert schedule.available_minutes == 60


def test_not_over_capacity():
    """No flag when tasks fit within the window."""
    owner = Owner("Jordan", "Mochi", "dog", time(7, 0), time(9, 0))  # 120 min
    tasks = [Task("Walk", 20, "high")]
    schedule = Scheduler(owner, tasks).generate_schedule()
    assert schedule.over_capacity is False


def test_empty_tasks():
    """Scheduler handles no tasks gracefully."""
    owner = Owner("Jordan", "Mochi", "dog", time(7, 0), time(9, 0))
    schedule = Scheduler(owner, []).generate_schedule()
    assert schedule.scheduled_tasks == []
    assert schedule.over_capacity is False
    assert schedule.total_minutes == 0


def test_available_minutes():
    """Owner correctly calculates available time."""
    owner = Owner("Jordan", "Mochi", "dog", time(7, 0), time(9, 30))
    assert owner.available_minutes() == 150


def test_display_includes_warning_when_over_capacity():
    """Display output includes a warning when over capacity."""
    owner = Owner("Jordan", "Mochi", "dog", time(7, 0), time(7, 30))  # 30 min
    tasks = [Task("Walk", 40, "high")]
    schedule = Scheduler(owner, tasks).generate_schedule()
    output = schedule.display()
    assert "Warning" in output
    assert "40 minutes" in output
    assert "30 minutes" in output


def test_reason_includes_priority():
    """Each scheduled task's reason mentions its priority."""
    owner = Owner("Jordan", "Mochi", "dog", time(7, 0), time(9, 0))
    tasks = [Task("Walk", 20, "high")]
    schedule = Scheduler(owner, tasks).generate_schedule()
    assert "high priority" in schedule.scheduled_tasks[0].reason
