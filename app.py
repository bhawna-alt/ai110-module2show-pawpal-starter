"""
app.py
Streamlit front-end for PawPal. Bridges the UI to pawpal_system.py.
Run with: streamlit run app.py
"""

import streamlit as st
from datetime import datetime
from pawpal_system import Task, Pet, Owner, Scheduler

# ---------------------------------------------------------------------------
# Step 1 & 2: Import logic layer + initialise persistent session state
# ---------------------------------------------------------------------------
# st.session_state works like a dictionary that survives page re-runs.
# We check "owner" exists before creating it so data is never wiped on refresh.

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        owner_id=1,
        name="My Household",
        email="owner@pawpal.app"
    )

if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1

if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

# Convenience aliases
owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="PawPal", page_icon="🐾", layout="centered")
st.title("🐾 PawPal — Pet Care Manager")

# ---------------------------------------------------------------------------
# Sidebar — Add a Pet
# ---------------------------------------------------------------------------

st.sidebar.header("Add a New Pet")

with st.sidebar.form("add_pet_form", clear_on_submit=True):
    pet_name  = st.text_input("Name")
    species   = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
    breed     = st.text_input("Breed")
    age       = st.number_input("Age (years)", min_value=0, max_value=30, step=1)
    submitted = st.form_submit_button("Add Pet")

    if submitted:
        if not pet_name.strip():
            st.sidebar.error("Please enter a pet name.")
        else:
            # Step 3: wire form data → Owner.add_pet()
            new_pet = Pet(
                pet_id=st.session_state.next_pet_id,
                name=pet_name.strip(),
                species=species,
                breed=breed.strip(),
                age=int(age)
            )
            owner.add_pet(new_pet)
            st.session_state.next_pet_id += 1
            st.sidebar.success(f"{pet_name} added!")

# ---------------------------------------------------------------------------
# Main area — tabs
# ---------------------------------------------------------------------------

tab_schedule, tab_pets, tab_add_task = st.tabs(
    ["📅 Today's Schedule", "🐶 My Pets", "➕ Add Task"]
)

# ---- Tab 1: Today's Schedule ----
with tab_schedule:
    st.subheader("Today's Schedule")
    schedule = scheduler.get_todays_schedule()

    if not schedule:
        st.info("No tasks scheduled for today. Add a task using the tab above!")
    else:
        for pet, task in schedule:
            col1, col2 = st.columns([5, 1])
            label = (
                f"~~{task.description}~~" if task.is_complete()
                else task.description
            )
            time_str = task.scheduled_time.strftime("%I:%M %p")
            col1.markdown(
                f"**{pet.name}** · {time_str} — {label} *(_{task.frequency}_)*"
            )
            if not task.is_complete():
                if col2.button("✓ Done", key=f"done_{task.task_id}"):
                    # Step 3: wire button → Scheduler.complete_task()
                    scheduler.complete_task(task.task_id)
                    st.rerun()

# ---- Tab 2: My Pets ----
with tab_pets:
    st.subheader("Registered Pets")
    pets = owner.get_pets()

    if not pets:
        st.info("No pets yet — add one using the sidebar!")
    else:
        for pet in pets:
            with st.expander(f"🐾 {pet.name} — {pet.species}"):
                st.write(f"**Breed:** {pet.breed or '—'}")
                st.write(f"**Age:** {pet.age} yr")
                st.write(f"**Medical notes:** {pet.medical_notes or 'None'}")

                new_note = st.text_input("Add medical note", key=f"note_{pet.pet_id}")
                if st.button("Save note", key=f"save_note_{pet.pet_id}"):
                    if new_note.strip():
                        pet.update_medical_notes(new_note.strip())
                        st.success("Note saved!")
                        st.rerun()

                upcoming = pet.get_upcoming_tasks()
                st.write(f"**Upcoming tasks:** {len(upcoming)}")
                for t in upcoming:
                    st.write(f"- {t.scheduled_time.strftime('%I:%M %p')} — {t.description}")

# ---- Tab 3: Add Task ----
with tab_add_task:
    st.subheader("Schedule a New Task")
    pets = owner.get_pets()

    if not pets:
        st.warning("Add a pet first before scheduling tasks.")
    else:
        with st.form("add_task_form", clear_on_submit=True):
            pet_names   = [p.name for p in pets]
            chosen_name = st.selectbox("Pet", pet_names)
            description = st.text_input("Task description (e.g. Morning walk)")
            task_date   = st.date_input("Date", value=datetime.now().date())
            task_time   = st.time_input("Time", value=datetime.now().replace(
                                            minute=0, second=0, microsecond=0).time())
            frequency   = st.selectbox("Frequency", ["once", "daily", "weekly"])
            notes       = st.text_area("Notes (optional)")
            submit_task = st.form_submit_button("Add Task")

            if submit_task:
                if not description.strip():
                    st.error("Please enter a task description.")
                else:
                    chosen_pet = next(p for p in pets if p.name == chosen_name)
                    scheduled_dt = datetime.combine(task_date, task_time)

                    # Step 3: wire form → Pet.add_task()
                    new_task = Task(
                        task_id=st.session_state.next_task_id,
                        description=description.strip(),
                        scheduled_time=scheduled_dt,
                        frequency=frequency,
                        notes=notes.strip()
                    )
                    chosen_pet.add_task(new_task)
                    st.session_state.next_task_id += 1
                    st.success(f"Task '{description}' added for {chosen_name}!")
                    st.rerun()