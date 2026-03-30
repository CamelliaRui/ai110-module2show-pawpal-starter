import streamlit as st
from datetime import time
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.markdown("A pet care planning assistant that helps you schedule daily tasks for your pets.")

st.divider()

# --- Owner Info ---
st.subheader("Owner Info")
col_owner, col_start, col_end = st.columns(3)
with col_owner:
    owner_name = st.text_input("Owner name", value="Jordan")
with col_start:
    start_time = st.time_input("Start time", value=time(7, 0))
with col_end:
    end_time = st.time_input("End time", value=time(9, 0))

st.divider()

# --- Pets ---
st.subheader("Pets")

if "pets" not in st.session_state:
    st.session_state.pets = {}  # {pet_name: species}

col_pet, col_species = st.columns(2)
with col_pet:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_species:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if pet_name.lower() in [p.lower() for p in st.session_state.pets]:
        st.warning(f"A pet named **{pet_name}** already exists.")
    else:
        st.session_state.pets[pet_name] = species
        st.rerun()

if st.session_state.pets:
    st.write("Your pets:")
    for name, sp in st.session_state.pets.items():
        st.markdown(f"- **{name}** ({sp})")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Tasks ---
st.subheader("Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if st.session_state.pets:
    pet_options = list(st.session_state.pets.keys())
    col_for, col_title = st.columns(2)
    with col_for:
        task_pet = st.selectbox("For pet", pet_options)
    with col_title:
        task_title = st.text_input("Task title", value="Morning walk")

    col1, col2, col3 = st.columns(3)
    with col1:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col2:
        priority = st.selectbox("Priority", ["high", "medium", "low"], index=0)
    with col3:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as_needed"], index=0)

    @st.dialog("Duplicate Task")
    def show_duplicate_warning(title, pet):
        st.warning(f"A task called **\"{title}\"** for **{pet}** has already been added.")
        st.write("**Existing tasks:**")
        st.table(st.session_state.tasks)
        if st.button("OK"):
            st.rerun()

    if st.button("Add task"):
        existing = [(t["title"].lower(), t["pet"].lower()) for t in st.session_state.tasks]
        if (task_title.lower(), task_pet.lower()) in existing:
            show_duplicate_warning(task_title, task_pet)
        else:
            st.session_state.tasks.append({
                "title": task_title,
                "duration_minutes": int(duration),
                "priority": priority,
                "frequency": frequency,
                "pet": task_pet,
            })
            st.rerun()
else:
    st.info("Add a pet first, then you can add tasks.")

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)

st.divider()

# --- Generate Schedule ---
st.subheader("Daily Schedule")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task first.")
    elif start_time >= end_time:
        st.warning("Start time must be before end time.")
    else:
        # Build Pet objects with their tasks
        pet_objects = {}
        for name, sp in st.session_state.pets.items():
            pet_objects[name] = Pet(name, sp)

        for t in st.session_state.tasks:
            pet_obj = pet_objects.get(t["pet"])
            if pet_obj:
                pet_obj.add_task(Task(
                    t["title"], t["duration_minutes"], t["priority"],
                    frequency=t.get("frequency", "daily"),
                ))

        owner = Owner(owner_name, list(pet_objects.values()), start_time, end_time)
        schedule = Scheduler(owner).generate_schedule()

        if schedule.over_capacity:
            st.warning(
                f"Tasks total {schedule.total_minutes} minutes "
                f"but only {schedule.available_minutes} minutes available."
            )

        if not schedule.scheduled_tasks:
            st.info("No pending tasks to schedule.")
        else:
            for st_task in schedule.scheduled_tasks:
                start_str = st_task.start_time.strftime("%-I:%M %p")
                end_str = st_task.end_time.strftime("%-I:%M %p")
                st.markdown(
                    f"**{start_str} - {end_str}:** {st_task.task.title} "
                    f"for {st_task.pet_name} — _{st_task.reason}_"
                )
