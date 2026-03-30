import streamlit as st
from datetime import time
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.markdown("A pet care planning assistant that helps you schedule daily tasks for your pets.")

st.divider()

# --- Session State: persist Owner across reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", [], time(7, 0), time(9, 0))

owner = st.session_state.owner

# ============================================================
# Owner Info
# ============================================================
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

# ============================================================
# Pets
# ============================================================
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
        owner.add_pet(Pet(pet_name, species))
        st.rerun()

if owner.pets:
    for pet in owner.pets:
        pending = len(pet.get_pending_tasks())
        total = len(pet.tasks)
        st.success(f"**{pet.name}** ({pet.species}) — {total} tasks, {pending} pending")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ============================================================
# Tasks
# ============================================================
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

    col_add, col_complete = st.columns(2)
    with col_add:
        if st.button("Add task"):
            target_pet = next(p for p in owner.pets if p.name == task_pet)
            existing_titles = [t.title.lower() for t in target_pet.tasks]
            if task_title.lower() in existing_titles:
                show_duplicate_warning(task_title, task_pet)
            else:
                target_pet.add_task(Task(
                    task_title, int(duration), priority,
                    frequency=frequency,
                ))
                st.rerun()

    with col_complete:
        # Complete task button — triggers recurring logic
        target_pet_obj = next(p for p in owner.pets if p.name == task_pet)
        pending_titles = [t.title for t in target_pet_obj.get_pending_tasks()]
        if pending_titles:
            complete_title = st.selectbox("Mark complete", pending_titles, key="complete_select")
            if st.button("Complete task"):
                next_task = target_pet_obj.complete_task(complete_title)
                if next_task:
                    st.toast(f"'{complete_title}' completed! Next occurrence created for {next_task.due_date}.")
                else:
                    st.toast(f"'{complete_title}' completed!")
                st.rerun()
else:
    st.info("Add a pet first, then you can add tasks.")

# --- Task Table with Filtering ---
all_tasks = owner.get_all_tasks()
if all_tasks:
    scheduler = Scheduler(owner)

    # Filter controls
    st.markdown("#### Task List")
    col_filter_pet, col_filter_status = st.columns(2)
    with col_filter_pet:
        filter_pet = st.selectbox(
            "Filter by pet", ["All pets"] + [p.name for p in owner.pets],
            key="filter_pet"
        )
    with col_filter_status:
        filter_status = st.selectbox(
            "Filter by status", ["All", "Pending", "Completed"],
            key="filter_status"
        )

    # Apply filters
    task_data = []
    for pet in owner.pets:
        if filter_pet != "All pets" and pet.name != filter_pet:
            continue
        for task in pet.tasks:
            if filter_status == "Pending" and task.completed:
                continue
            if filter_status == "Completed" and not task.completed:
                continue
            task_data.append({
                "pet": pet.name,
                "title": task.title,
                "duration": f"{task.duration_minutes} min",
                "priority": task.priority,
                "frequency": task.frequency,
                "status": "done" if task.completed else "pending",
            })

    if task_data:
        st.table(task_data)
    else:
        st.info("No tasks match the current filters.")

st.divider()

# ============================================================
# Daily Schedule
# ============================================================
st.subheader("Daily Schedule")

if st.button("Generate schedule", type="primary"):
    if not owner.get_all_pending_tasks():
        st.warning("Add at least one task first.")
    elif owner.start_time >= owner.end_time:
        st.warning("Start time must be before end time.")
    else:
        schedule = Scheduler(owner).generate_schedule()

        # Conflict warnings
        if schedule.conflicts:
            for conflict in schedule.conflicts:
                st.error(f"**Conflict:** {conflict}")

        # Over-capacity warning
        if schedule.over_capacity:
            st.warning(
                f"**Over capacity:** Tasks total **{schedule.total_minutes} min** "
                f"but only **{schedule.available_minutes} min** available. "
                f"Consider removing {schedule.total_minutes - schedule.available_minutes} min of lower-priority tasks."
            )

        # Schedule display
        if not schedule.scheduled_tasks:
            st.info("No pending tasks to schedule.")
        else:
            for st_task in schedule.scheduled_tasks:
                start_str = st_task.start_time.strftime("%-I:%M %p")
                end_str = st_task.end_time.strftime("%-I:%M %p")

                # Color-code by priority
                if st_task.task.priority == "high":
                    icon = "🔴"
                elif st_task.task.priority == "medium":
                    icon = "🟡"
                else:
                    icon = "🟢"

                st.markdown(
                    f"{icon} **{start_str} – {end_str}** | "
                    f"**{st_task.task.title}** for {st_task.pet_name}  \n"
                    f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_{st_task.reason}_"
                )

            # Summary
            remaining = schedule.available_minutes - schedule.total_minutes
            if not schedule.over_capacity:
                st.success(
                    f"**Schedule complete!** {schedule.total_minutes} min planned, "
                    f"{remaining} min remaining in your window."
                )
