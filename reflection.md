# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**Core user actions identified (Step 1):**

1. **Create and organize care tasks** — The user adds pet care tasks (walks, feeding, meds, grooming, enrichment) with a duration and priority level. They can edit or remove tasks as needs change.
2. **Generate a daily schedule** — The user requests a daily plan. The system selects and orders tasks based on constraints like available time, task priority, and owner preferences.
3. **View and understand the schedule** — The user sees the resulting plan displayed clearly, with explanations for why each task was scheduled at its time and why certain tasks were prioritized over others.

**UML design (5 classes):**

- **Task** — title, duration_minutes, priority, category. Represents a single pet care task.
- **Owner** — name, pet_name, species, start_time, end_time. Represents the pet owner and their available time window. Has `available_minutes()` method.
- **ScheduledTask** — wraps a Task with an assigned start_time, end_time, and reason string. Represents one slot in the generated plan.
- **Scheduler** — takes an Owner and a list of Tasks. Sorts by strict priority, assigns sequential time slots, checks capacity. Produces a Schedule.
- **Schedule** — holds a list of ScheduledTasks, an over_capacity flag, total_minutes, and available_minutes. Has `display()` method.

**Relationships:** Scheduler uses 1 Owner + many Tasks → produces 1 Schedule → contains many ScheduledTasks → each wraps 1 Task.

**Initial design decisions (from brainstorming):**

- **Classes:** Task (title, duration, priority, category), Owner (name, pet name, species, available time window), Scheduler (takes Owner + Tasks, produces a Schedule)
- **Priority ordering:** Strict — all high-priority tasks first, then medium, then low
- **Time model:** User provides a start time and end time. Tasks are slotted sequentially into this window.
- **Over-capacity handling:** If total task duration exceeds available time, all tasks are still shown but the schedule is flagged as over-capacity — the user decides what to cut.
- **Reasoning:** Each scheduled task shows its time slot and a brief explanation (e.g., "7:00 AM - 7:20 AM: Morning walk (high priority, scheduled first)")

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

**Design change 1: Duplicate task prevention.** During testing of the Streamlit UI, we discovered that clicking "Add task" multiple times would add the same task repeatedly. We added duplicate detection with a pop-up dialog warning, instead of silently adding the duplicate.

**Design change 2: Pet-aware duplicate check.** The initial duplicate check only compared task titles, which was too aggressive. For example, a "Morning walk" for Mochi and a "Morning walk" for Mocha are different tasks for different pets and should both be allowed. We refined the check to compare both the task title AND the pet name (case-insensitive). A task is only flagged as a duplicate if the same title is being added for the same pet. Each task now also stores which pet it belongs to.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
