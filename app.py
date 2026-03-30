import streamlit as st
from datetime import time
from pawpal_system import Task, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.markdown("A pet care planning assistant that helps you schedule daily tasks for your pet.")

st.divider()

# --- Owner & Pet Info ---
st.subheader("Owner & Pet Info")
col_owner, col_pet, col_species = st.columns(3)
with col_owner:
    owner_name = st.text_input("Owner name", value="Jordan")
with col_pet:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_species:
    species = st.selectbox("Species", ["dog", "cat", "other"])

# --- Time Window ---
st.subheader("Available Time Window")
col_start, col_end = st.columns(2)
with col_start:
    start_time = st.time_input("Start time", value=time(7, 0))
with col_end:
    end_time = st.time_input("End time", value=time(9, 0))

st.divider()

# --- Tasks ---
st.subheader("Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["high", "medium", "low"], index=0)

@st.dialog("Duplicate Task")
def show_duplicate_warning(title, pet):
    st.warning(f"A task called **\"{title}\"** for **{pet}** has already been added.")
    st.write("**Existing tasks:**")
    st.table(st.session_state.tasks)
    if st.button("OK"):
        st.rerun()

if st.button("Add task"):
    existing = [(t["title"].lower(), t["pet"].lower()) for t in st.session_state.tasks]
    if (task_title.lower(), pet_name.lower()) in existing:
        show_duplicate_warning(task_title, pet_name)
    else:
        st.session_state.tasks.append(
            {"title": task_title, "duration_minutes": int(duration), "priority": priority, "pet": pet_name}
        )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("Daily Schedule")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task first.")
    elif start_time >= end_time:
        st.warning("Start time must be before end time.")
    else:
        owner = Owner(owner_name, pet_name, species, start_time, end_time)
        tasks = [
            Task(t["title"], t["duration_minutes"], t["priority"])
            for t in st.session_state.tasks
        ]
        scheduler = Scheduler(owner, tasks)
        schedule = scheduler.generate_schedule()

        if schedule.over_capacity:
            st.warning(
                f"Tasks total {schedule.total_minutes} minutes "
                f"but only {schedule.available_minutes} minutes available."
            )

        for st_task in schedule.scheduled_tasks:
            start_str = st_task.start_time.strftime("%-I:%M %p")
            end_str = st_task.end_time.strftime("%-I:%M %p")
            st.markdown(
                f"**{start_str} - {end_str}:** {st_task.task.title} "
                f"— _{st_task.reason}_"
            )
