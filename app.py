import streamlit as st
from datetime import time
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.markdown("A pet care planning assistant that helps you schedule daily tasks for your pets.")

st.divider()

# --- Step 2: Manage Application Memory ---
# Store the Owner object in session_state so it persists across reruns.
# Streamlit reruns the script top-to-bottom on every interaction,
# so we check if the Owner already exists before creating a new one.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", [], time(7, 0), time(9, 0))

owner = st.session_state.owner

# --- Owner Info ---
st.subheader("Owner Info")
col_owner, col_start, col_end = st.columns(3)
with col_owner:
    new_name = st.text_input("Owner name", value=owner.name)
    owner.name = new_name
with col_start:
    new_start = st.time_input("Start time", value=owner.start_time)
    owner.start_time = new_start
with col_end:
    new_end = st.time_input("End time", value=owner.end_time)
    owner.end_time = new_end

st.divider()

# --- Pets ---
st.subheader("Pets")

col_pet, col_species = st.columns(2)
with col_pet:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_species:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    existing_names = [p.name.lower() for p in owner.pets]
    if pet_name.lower() in existing_names:
        st.warning(f"A pet named **{pet_name}** already exists.")
    else:
        # Wire directly to Owner.add_pet() method
        owner.add_pet(Pet(pet_name, species))
        st.rerun()

if owner.pets:
    st.write("Your pets:")
    for pet in owner.pets:
        task_count = len(pet.tasks)
        pending = len(pet.get_pending_tasks())
        st.markdown(f"- **{pet.name}** ({pet.species}) — {task_count} tasks ({pending} pending)")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Tasks ---
st.subheader("Tasks")

if owner.pets:
    pet_options = [p.name for p in owner.pets]
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
    def show_duplicate_warning(title, pet_nm):
        st.warning(f"A task called **\"{title}\"** for **{pet_nm}** has already been added.")
        if st.button("OK"):
            st.rerun()

    if st.button("Add task"):
        # Find the Pet object and check for duplicates
        target_pet = next(p for p in owner.pets if p.name == task_pet)
        existing_titles = [t.title.lower() for t in target_pet.tasks]
        if task_title.lower() in existing_titles:
            show_duplicate_warning(task_title, task_pet)
        else:
            # Wire directly to Pet.add_task() method
            target_pet.add_task(Task(
                task_title, int(duration), priority,
                frequency=frequency,
            ))
            st.rerun()
else:
    st.info("Add a pet first, then you can add tasks.")

# Display all tasks across all pets
all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    task_data = []
    for pet in owner.pets:
        for task in pet.tasks:
            task_data.append({
                "pet": pet.name,
                "title": task.title,
                "duration": f"{task.duration_minutes} min",
                "priority": task.priority,
                "frequency": task.frequency,
                "status": "done" if task.completed else "pending",
            })
    st.table(task_data)

st.divider()

# --- Generate Schedule ---
st.subheader("Daily Schedule")

if st.button("Generate schedule"):
    if not owner.get_all_pending_tasks():
        st.warning("Add at least one task first.")
    elif owner.start_time >= owner.end_time:
        st.warning("Start time must be before end time.")
    else:
        # Wire directly to Scheduler — it talks to Owner to get all pet tasks
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
