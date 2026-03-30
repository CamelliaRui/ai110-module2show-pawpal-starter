# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

**Core user actions identified (Step 1):**

1. **Create and organize care tasks** — The user adds pet care tasks (walks, feeding, meds, grooming, enrichment) with a duration and priority level. They can edit or remove tasks as needs change.
2. **Generate a daily schedule** — The user requests a daily plan. The system selects and orders tasks based on constraints like available time, task priority, and owner preferences.
3. **View and understand the schedule** — The user sees the resulting plan displayed clearly, with explanations for why each task was scheduled at its time and why certain tasks were prioritized over others.

**Initial UML design (5 classes):**

- **Task** — title, duration_minutes, priority, category. Represents a single pet care task.
- **Owner** — name, pet_name, species, start_time, end_time. Represents the pet owner and their available time window.
- **ScheduledTask** — wraps a Task with an assigned start_time, end_time, and reason string.
- **Scheduler** — takes an Owner and a list of Tasks. Sorts by strict priority, assigns sequential time slots, checks capacity.
- **Schedule** — holds a list of ScheduledTasks, an over_capacity flag, total_minutes, and available_minutes.

**Initial design decisions:**

- **Priority ordering:** Strict — all high-priority tasks first, then medium, then low
- **Time model:** User provides a start time and end time. Tasks are slotted sequentially into this window.
- **Over-capacity handling:** All tasks shown but schedule flagged — the user decides what to cut.

**b. Design changes**

**Design change 1: Added the Pet class.** The initial design had Owner hold a single pet_name and species. The assignment required Owner to manage multiple pets, so we introduced a Pet class that holds its own task list. The Scheduler now gathers tasks from all of the Owner's pets. This was the biggest structural change.

**Design change 2: Duplicate task prevention.** During UI testing, clicking "Add task" multiple times added duplicates. We added a dialog warning. Initially it only checked task title, but a "Morning walk" for Mochi and a "Morning walk" for Mocha are different tasks — so we refined it to check both title AND pet name.

**Design change 3: Recurring tasks and new fields.** Added `frequency`, `completed`, `scheduled_time`, and `due_date` to Task. The `mark_complete()` method now returns a new Task instance for the next occurrence using `timedelta`. This required adding `Pet.complete_task()` to orchestrate the workflow.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints:
1. **Priority** (high/medium/low) — strict ordering, all high tasks scheduled before medium, etc.
2. **Time window** — the owner sets a start and end time; tasks are slotted sequentially.
3. **Scheduled time preference** — within the same priority level, tasks with an earlier preferred time are scheduled first.

Priority was chosen as the primary constraint because a pet owner's most important tasks (medication, feeding) should never be bumped by lower-priority ones. Time preference is secondary since the daily window is typically short.

**b. Tradeoffs**

The scheduler assigns tasks sequentially rather than solving for arbitrary time-slot placement. This means conflict detection only finds overlaps that result from the sequential assignment (e.g., when total duration exceeds the window), not user-specified time conflicts where two tasks were manually set to the same hour. This tradeoff is reasonable because our scheduler controls the assignment — it places tasks one after another, so true overlaps only happen when total duration exceeds the available window. A more complex interval-scheduling algorithm (like interval graph coloring) would add significant complexity without practical benefit for a daily pet care scenario with 5–10 tasks.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code throughout this project for:
- **Design brainstorming** — We worked through the core user actions, class design, and scheduling rules interactively, with Claude presenting options (A/B/C) and me making decisions. This was the most productive phase because it forced me to articulate my preferences.
- **Code generation** — Claude scaffolded the dataclass skeletons, implemented sorting/filtering methods, and wrote the Streamlit UI. I reviewed each output before accepting.
- **Test writing** — Claude generated the 32-test suite covering happy paths and edge cases, which caught several assumptions I hadn't thought about.
- **Refactoring** — When the assignment required a Pet class, Claude restructured the entire codebase (models, tests, UI, demo script) in one pass.

The most helpful prompts were the ones where I described a specific problem I encountered (e.g., "when I click Add Task twice it duplicates") rather than abstract requests. Concrete problems led to concrete solutions.

**b. Judgment and verification**

When Claude initially suggested duplicate detection based only on task title, I rejected it after testing the UI — I changed the pet name from Mochi to Mocha and tried to add a "Morning walk" for the new pet, but it was blocked. I pointed out that the same task name for different pets should be allowed. Claude agreed and refined the check to compare both title and pet name. I verified the fix by testing both scenarios: same task/same pet (correctly blocked) and same task/different pet (correctly allowed).

I also chose option C (show over-capacity but let the user decide) instead of Claude's recommended option A (silently drop low-priority tasks), because I felt a scheduling assistant should inform, not decide for the user.

---

## 4. Testing and Verification

**a. What you tested**

32 automated tests covering:
- Task completion and status changes (mark_complete, mark_incomplete)
- Pet task management (add, remove, get_pending)
- Priority-based and time-based sorting correctness
- Sequential time slot assignment
- Filtering by pet name and completion status
- Recurring task generation (daily +1 day, weekly +7 days, as_needed no recurrence)
- Recurring task attribute preservation (title, priority, frequency, scheduled_time all carried over)
- Conflict detection (no false positives on sequential tasks)
- Over-capacity flag and display warnings
- Edge cases: no tasks, no pets, all completed, duplicate scheduled times, nonexistent pet filter, nonexistent task completion, single task filling exact window

These tests were important because the scheduling logic has many interacting rules (priority ordering, time slotting, capacity checks, recurrence). Without tests, a change to one rule could silently break another.

**b. Confidence**

**4 out of 5.** The backend logic is thoroughly tested and I'm confident the scheduler produces correct results. The main untested area is the Streamlit UI integration — button clicks, session state persistence, and dialog behavior would need browser-based testing (e.g., Selenium or Playwright) to verify.

Edge cases I'd test next:
- Tasks that span midnight (end time before start time)
- Very large task lists (100+ tasks) for performance
- Concurrent recurring task completion (complete two tasks at once)

---

## 5. Reflection

**a. What went well**

The brainstorming phase was the most valuable part. By working through design decisions as multiple-choice questions (priority ordering: strict vs. weighted vs. only-when-limited), I made deliberate choices instead of defaulting to whatever the AI suggested first. The result was a system I understood deeply because every design decision had a reason behind it.

**b. What you would improve**

I would separate the Pet class earlier in the design. The initial design had Owner hold a single pet, which required a significant refactor when the assignment introduced multi-pet support. Starting with Pet as a first-class entity would have saved time and produced cleaner code from the start.

I would also add a "remove task" button to the UI — currently tasks can only be added, not deleted through the interface.

**c. Key takeaway**

The most important thing I learned is that **AI is most useful when you know what you want**. When I gave vague instructions, the AI made assumptions I had to correct later. When I gave specific feedback (like "this duplicate check is too aggressive because..."), the AI immediately produced the right solution. Being the "lead architect" means making the design decisions and using AI as a skilled implementer — not the other way around.
