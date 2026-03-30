# PawPal+

A Streamlit-based pet care scheduling assistant that helps busy pet owners plan daily care tasks across multiple pets.

## Features

- **Multi-pet management** — Add and manage multiple pets (dogs, cats, etc.) each with their own task lists
- **Task creation** — Define care tasks with title, duration, priority (high/medium/low), and frequency (daily/weekly/as needed)
- **Smart scheduling** — Generates a daily plan sorted by priority, then by preferred time within each priority level
- **Recurring tasks** — Daily and weekly tasks auto-generate the next occurrence when marked complete
- **Conflict detection** — Flags overlapping time slots with clear error messages in the UI
- **Over-capacity warnings** — Alerts when total task duration exceeds your available time window, with actionable advice
- **Filtering** — Filter the task list by pet or by completion status
- **Duplicate prevention** — Prevents adding the same task twice for the same pet, with a dialog explaining the issue
- **Color-coded schedule** — Priority levels are visually distinguished (🔴 high, 🟡 medium, 🟢 low)

## Demo

To run the app locally:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank"><img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## Architecture

The system uses 6 classes defined in `pawpal_system.py`:

| Class | Role |
|-------|------|
| **Task** | A single care activity with priority, frequency, completion status, and optional scheduled time |
| **Pet** | Stores pet details and manages its task list |
| **Owner** | Manages multiple pets and defines the daily time window |
| **Scheduler** | The "brain" — gathers tasks from all pets, sorts, assigns time slots, detects conflicts |
| **ScheduledTask** | A task assigned to a specific time slot with a reason string |
| **Schedule** | The output: list of scheduled tasks, capacity info, and conflict warnings |

See `uml_diagram.md` for the full Mermaid.js class diagram.

## Smarter Scheduling

- **Priority + time sorting** — `sorted()` with a multi-key lambda: priority first, then `scheduled_time`
- **Filtering** — `filter_by_pet()` and `filter_by_status()` on the Scheduler
- **Recurring tasks** — `mark_complete()` uses `timedelta` to create the next occurrence (+1 day for daily, +7 for weekly)
- **Conflict detection** — `_detect_conflicts()` compares all scheduled task pairs for overlapping time ranges
- **Over-capacity** — All tasks are shown even when over budget; the user decides what to cut

## Testing PawPal+

```bash
python -m pytest
```

The test suite (32 tests) covers:

- **Task basics** — completion status, add/remove from pets
- **Sorting** — priority ordering, time-based sorting, combined priority+time
- **Filtering** — by pet name, by completion status
- **Recurring tasks** — daily (+1 day), weekly (+7 days), as_needed (no recurrence), attribute preservation
- **Conflict detection** — sequential tasks produce no conflicts, display shows conflict text
- **Over-capacity** — flagged when tasks exceed window, warning in display output
- **Edge cases** — no tasks, no pets, all completed, same scheduled time, nonexistent pet/task, exact window fit

**Confidence Level: 4/5** — Core scheduling, sorting, filtering, and recurrence are thoroughly tested. The remaining gap is integration testing of the Streamlit UI layer.

## Project Structure

```
pawpal_system.py    # Backend logic (Task, Pet, Owner, Scheduler, Schedule, ScheduledTask)
app.py              # Streamlit UI
main.py             # CLI demo script
tests/test_pawpal.py # Automated test suite (32 tests)
uml_diagram.md      # Final Mermaid.js UML class diagram
reflection.md       # Project reflection and design decisions
```
