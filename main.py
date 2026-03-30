from datetime import time, date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def print_section(title):
    print()
    print("=" * 55)
    print(f"  {title}")
    print("=" * 55)


def print_schedule(schedule):
    for st_task in schedule.scheduled_tasks:
        start = st_task.start_time.strftime("%-I:%M %p")
        end = st_task.end_time.strftime("%-I:%M %p")
        print(f"  {start:>8} - {end:<8}  {st_task.task.title} ({st_task.pet_name})")
        print(f"{'':>22}  [{st_task.reason}]")
    print()
    if schedule.conflicts:
        for c in schedule.conflicts:
            print(f"  !! {c}")
        print()
    print(f"  Total: {schedule.total_minutes} min / {schedule.available_minutes} min available")
    if schedule.over_capacity:
        print("  WARNING: OVER CAPACITY")
    else:
        print(f"  {schedule.available_minutes - schedule.total_minutes} min remaining")


def main():
    # --- Setup: tasks added OUT OF ORDER to test sorting ---
    mochi = Pet("Mochi", "dog")
    mochi.add_task(Task("Grooming", 30, "low", category="grooming", frequency="weekly",
                        scheduled_time=time(8, 30)))
    mochi.add_task(Task("Morning walk", 20, "high", category="walk", frequency="daily",
                        scheduled_time=time(7, 0)))
    mochi.add_task(Task("Evening walk", 20, "medium", category="walk", frequency="daily",
                        scheduled_time=time(17, 0)))

    mocha = Pet("Mocha", "cat")
    mocha.add_task(Task("Play session", 25, "medium", category="enrichment", frequency="daily",
                        scheduled_time=time(8, 0)))
    mocha.add_task(Task("Breakfast", 10, "high", category="feeding", frequency="daily",
                        scheduled_time=time(7, 15)))
    mocha.add_task(Task("Medication", 5, "high", category="meds", frequency="daily",
                        scheduled_time=time(7, 0), due_date=date.today()))

    owner = Owner("Jordan", [mochi, mocha], start_time=time(7, 0), end_time=time(9, 0))
    scheduler = Scheduler(owner)

    # --- 1. Full schedule (sorted by priority + time) ---
    print_section("Today's Schedule (sorted by priority & time)")
    schedule = scheduler.generate_schedule()
    print_schedule(schedule)

    # --- 2. Sort by time only ---
    print_section("All Tasks Sorted by Scheduled Time")
    by_time = scheduler.sort_by_time(scheduler._gather_tasks())
    for task, pet_name in by_time:
        t_str = task.scheduled_time.strftime("%-I:%M %p") if task.scheduled_time else "no time"
        print(f"  {t_str:>8}  {task.title} ({pet_name}) [{task.priority}]")

    # --- 3. Filter by pet ---
    print_section("Filter: Mochi's Tasks Only")
    mochi_tasks = scheduler.filter_by_pet("Mochi")
    for task, pet_name in mochi_tasks:
        print(f"  - {task.title} ({task.priority}, {task.frequency})")

    # --- 4. Filter by status ---
    print_section("Filter: All Pending Tasks")
    pending = scheduler.filter_by_status(completed=False)
    print(f"  {len(pending)} pending tasks")
    for task, pet_name in pending:
        print(f"  - {task.title} for {pet_name}")

    # --- 5. Recurring task demo ---
    print_section("Recurring Task: Complete Medication")
    print(f"  Before: {mocha.tasks}")
    mocha.complete_task("Medication")
    print(f"  After:  {mocha.tasks}")
    # Show the new occurrence
    new_med = [t for t in mocha.tasks if t.title == "Medication" and not t.completed]
    if new_med:
        print(f"  Next occurrence due: {new_med[0].due_date}")

    # --- 6. Conflict detection demo ---
    print_section("Conflict Detection Demo")
    # Create two tasks that will overlap when manually given the same slot
    conflict_pet = Pet("Buddy", "dog")
    conflict_pet.add_task(Task("Walk", 30, "high"))
    conflict_pet.add_task(Task("Vet visit", 30, "high"))
    conflict_owner = Owner("Alex", [conflict_pet], start_time=time(10, 0), end_time=time(10, 30))
    # With only 30 min available but 60 min of tasks, the second task will overflow
    conflict_schedule = Scheduler(conflict_owner).generate_schedule()
    print_schedule(conflict_schedule)


if __name__ == "__main__":
    main()
