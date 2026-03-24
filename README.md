# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.


features....

FeatureDescriptionOwner & Pet profilesAdd owner info and register multiple pets with species, breed, age, and medical notesTask managementAdd, view, and complete tasks with description, time, frequency, and notesSmart schedulingDaily schedule view sorted chronologically using Scheduler.sort_by_time()Recurring tasksDaily and weekly tasks auto-reschedule on completion using timedeltaConflict detectionWarns when two tasks for the same pet overlap at the exact same minuteFilteringFilter tasks by pet name or completion statusPersistent sessionst.session_state keeps data alive across Streamlit page re-runs


## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

ystem Architecture
See uml_final.png for the full class diagram. Key relationships:

Owner has many Pets
Pet has many Tasks (owns the task list directly)
Scheduler reads from Owner via get_all_tasks() — never accesses pets directly
Task references itself via next_occurrence() to produce recurring instances

Suggested workflow followed

Read the scenario and identified requirements and edge cases
Drafted UML diagram (classes, attributes, methods, relationships)
Converted UML into Python class stubs in pawpal_system.py
Implemented scheduling logic incrementally (sort → filter → recurrence → conflict detection)
Added tests in tests/test_pawpal.py to verify key behaviors
Connected logic to the Streamlit UI in app.py
Refined UML to match final implementation (uml_final.png)

 Smarter Scheduling
The Scheduler class acts as the "brain" of the system — it never touches pet data directly, always going through Owner.get_all_tasks() to stay decoupled.

sort_by_time() — uses sorted() with a lambda key on scheduled_time (O(n log n))
filter_by_pet() and filter_by_status() — single-pass O(n) list comprehensions
complete_task() — marks a task done and calls Task.next_occurrence() to auto-generate the next one
detect_conflicts() — O(n) dictionary scan keyed by (pet_id, scheduled_minute); returns warning strings instead of raising exceptions


Project Structure
pawpal/
├── app.py               # Streamlit UI
├── pawpal_system.py     # Logic layer (Owner, Pet, Task, Scheduler)
├── main.py              # CLI demo and algorithm verification
├── tests/
│   └── test_pawpal.py   # Automated test suite
├── reflection.md        # Design decisions and AI strategy log
├── uml_final.png        # Final class diagram
└── README.md


Testing-----
The test suite covers:

Task completion changes status to "complete"
Completing a daily task generates a new task exactly 24 hours later
Completing a weekly task generates a new task exactly 7 days later
Completing a once task does not create a follow-up
sort_by_time() returns tasks in strict chronological order
filter_by_pet() returns only tasks for the named pet
filter_by_status() correctly separates pending and complete tasks
detect_conflicts() flags two tasks booked at the same minute for the same pet
detect_conflicts() returns no warnings when all times are distinct



Demo
<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank">
  <img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' />
</a>


Requirements
streamlit
pytest