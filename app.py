"""
app.py
Streamlit front-end for PawPal. Bridges the UI to pawpal_system.py.
Run with: streamlit run app.py
"""

"""
app.py  —  PawPal+ Streamlit UI
Run with: streamlit run app.py
"""

import streamlit as st
from datetime import datetime
from pawpal_system import Task, Pet, Owner, Scheduler

# ── Session state ──────────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = Owner(1, "My Household", "owner@pawpal.app")
if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1
if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

owner: Owner = st.session_state.owner
scheduler    = Scheduler(owner)

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+ — Smart Pet Care Scheduler")

# ── Conflict banner ────────────────────────────────────────────────────────
for w in scheduler.detect_conflicts():
    st.warning(w)

# ── Sidebar: Add a Pet ─────────────────────────────────────────────────────
st.sidebar.header("Add a New Pet")
with st.sidebar.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Name")
    species  = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
    breed    = st.text_input("Breed")
    age      = st.number_input("Age (years)", min_value=0, max_value=30, step=1)
    if st.form_submit_button("Add Pet"):
        if not pet_name.strip():
            st.sidebar.error("Please enter a pet name.")
        else:
            owner.add_pet(Pet(
                pet_id=st.session_state.next_pet_id,
                name=pet_name.strip(),
                species=species,
                breed=breed.strip(),
                age=int(age),
            ))
            st.session_state.next_pet_id += 1
            st.sidebar.success(f"{pet_name} added!")

# ── Tabs ───────────────────────────────────────────────────────────────────
tab_schedule, tab_pets, tab_add_task, tab_filter = st.tabs([
    "📅 Today's Schedule", "🐶 My Pets", "➕ Add Task", "🔍 Filter & Search"
])

# ── Tab 1: Today's Schedule ────────────────────────────────────────────────
with tab_schedule:
    st.subheader("Today's Schedule")
    schedule = scheduler.get_todays_schedule()

    if not schedule:
        st.info("No tasks scheduled for today. Add a task using the ➕ tab above!")
    else:
        st.table([{
            "Time":      task.scheduled_time.strftime("%I:%M %p"),
            "Pet":       pet.name,
            "Task":      task.description,
            "Frequency": task.frequency,
            "Status":    "✓ Done" if task.is_complete() else "Pending",
        } for pet, task in schedule])

        st.divider()
        st.write("**Mark tasks complete:**")
        for pet, task in schedule:
            if not task.is_complete():
                c1, c2 = st.columns([5, 1])
                c1.write(f"**{pet.name}** · {task.scheduled_time.strftime('%I:%M %p')} — {task.description}")
                if c2.button("✓", key=f"done_{task.task_id}"):
                    scheduler.complete_task(task.task_id)
                    st.success(
                        f"'{task.description}' complete!"
                        + (" Next occurrence scheduled." if task.frequency != "once" else "")
                    )
                    st.rerun()

# ── Tab 2: My Pets ─────────────────────────────────────────────────────────
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
                if st.button("Save note", key=f"save_{pet.pet_id}"):
                    if new_note.strip():
                        pet.update_medical_notes(new_note.strip())
                        st.success("Note saved!")
                        st.rerun()

                upcoming = pet.get_upcoming_tasks()
                if upcoming:
                    st.write(f"**Upcoming tasks ({len(upcoming)}):**")
                    for t in upcoming:
                        st.write(f"- {t.scheduled_time.strftime('%b %d %I:%M %p')} — {t.description} *({t.frequency})*")
                else:
                    st.write("No upcoming tasks.")

# ── Tab 3: Add Task ────────────────────────────────────────────────────────
with tab_add_task:
    st.subheader("Schedule a New Task")
    pets = owner.get_pets()

    if not pets:
        st.warning("Add a pet first before scheduling tasks.")
    else:
        with st.form("add_task_form", clear_on_submit=True):
            chosen_name = st.selectbox("Pet", [p.name for p in pets])
            description = st.text_input("Task description (e.g. Morning walk)")
            task_date   = st.date_input("Date", value=datetime.now().date())
            task_time   = st.time_input("Time", value=datetime.now().replace(minute=0, second=0, microsecond=0).time())
            frequency   = st.selectbox("Frequency", ["once", "daily", "weekly"])
            notes       = st.text_area("Notes (optional)")

            if st.form_submit_button("Add Task"):
                if not description.strip():
                    st.error("Please enter a task description.")
                else:
                    chosen_pet = next(p for p in pets if p.name == chosen_name)
                    chosen_pet.add_task(Task(
                        task_id=st.session_state.next_task_id,
                        description=description.strip(),
                        scheduled_time=datetime.combine(task_date, task_time),
                        frequency=frequency,
                        notes=notes.strip(),
                    ))
                    st.session_state.next_task_id += 1
                    st.success(f"'{description}' added for {chosen_name}!")
                    st.rerun()

# ── Tab 4: Filter & Search ─────────────────────────────────────────────────
with tab_filter:
    st.subheader("Filter Tasks")
    pets = owner.get_pets()

    c1, c2 = st.columns(2)
    pet_filter    = c1.selectbox("Filter by pet",    ["All"] + [p.name for p in pets])
    status_filter = c2.selectbox("Filter by status", ["All", "pending", "complete"])

    results = scheduler.filter_by_pet(pet_filter) if pet_filter != "All" else owner.get_all_tasks()
    if status_filter != "All":
        results = [(pet, t) for pet, t in results if t.status == status_filter]
    results = scheduler.sort_by_time(results)

    if not results:
        st.info("No tasks match your filters.")
    else:
        st.table([{
            "Pet":       pet.name,
            "Task":      task.description,
            "Date":      task.scheduled_time.strftime("%b %d"),
            "Time":      task.scheduled_time.strftime("%I:%M %p"),
            "Frequency": task.frequency,
            "Status":    "✓ Done" if task.is_complete() else "Pending",
        } for pet, task in results])
        st.caption(f"{len(results)} task(s) found.")