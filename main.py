from datetime import time
from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    # Create pets
    mochi = Pet("Mochi", "dog")
    mochi.add_task(Task("Morning walk", 20, "high", category="walk", frequency="daily"))
    mochi.add_task(Task("Grooming", 30, "low", category="grooming", frequency="weekly"))

    mocha = Pet("Mocha", "cat")
    mocha.add_task(Task("Breakfast", 10, "high", category="feeding", frequency="daily"))
    mocha.add_task(Task("Play session", 25, "medium", category="enrichment", frequency="daily"))
    mocha.add_task(Task("Medication", 5, "high", category="meds", frequency="daily"))

    # Create owner with time window
    owner = Owner("Jordan", [mochi, mocha], start_time=time(7, 0), end_time=time(9, 0))

    # Generate and display schedule
    schedule = Scheduler(owner).generate_schedule()

    print("=" * 50)
    print(f"  Today's Schedule for {owner.name}")
    print(f"  Pets: {', '.join(p.name for p in owner.pets)}")
    print(f"  Window: {owner.start_time.strftime('%-I:%M %p')} - {owner.end_time.strftime('%-I:%M %p')}")
    print("=" * 50)
    print()

    for st_task in schedule.scheduled_tasks:
        start = st_task.start_time.strftime("%-I:%M %p")
        end = st_task.end_time.strftime("%-I:%M %p")
        print(f"  {start:>8} - {end:<8}  {st_task.task.title} ({st_task.pet_name})")
        print(f"{'':>22}  [{st_task.reason}]")
        print()

    print("-" * 50)
    print(f"  Total: {schedule.total_minutes} min / {schedule.available_minutes} min available")
    if schedule.over_capacity:
        print("  ⚠ OVER CAPACITY — some tasks may not fit!")
    else:
        print(f"  ✓ {schedule.available_minutes - schedule.total_minutes} min remaining")
    print("-" * 50)


if __name__ == "__main__":
    main()
