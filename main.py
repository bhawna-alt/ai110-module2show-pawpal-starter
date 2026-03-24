"""
main.py
Temporary demo script — verifies that PawPal logic works in the terminal.
"""

from datetime import datetime
from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    # --- Build owner ---
    owner = Owner(owner_id=1, name="Alex Rivera", email="alex@example.com")

    # --- Build pets ---
    buddy = Pet(pet_id=1, name="Buddy", species="Dog", breed="Labrador", age=3)
    whiskers = Pet(pet_id=2, name="Whiskers", species="Cat", breed="Siamese", age=5)

    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    # --- Add tasks (all dated today so they show in Today's Schedule) ---
    today = datetime.now()

    buddy.add_task(Task(
        task_id=1,
        description="Morning walk",
        scheduled_time=today.replace(hour=7, minute=0),
        frequency="daily"
    ))
    buddy.add_task(Task(
        task_id=2,
        description="Feed breakfast",
        scheduled_time=today.replace(hour=7, minute=30),
        frequency="daily"
    ))
    buddy.add_task(Task(
        task_id=3,
        description="Vet check-up",
        scheduled_time=today.replace(hour=10, minute=0),
        frequency="once"
    ))
    whiskers.add_task(Task(
        task_id=4,
        description="Feed breakfast",
        scheduled_time=today.replace(hour=8, minute=0),
        frequency="daily"
    ))
    whiskers.add_task(Task(
        task_id=5,
        description="Clean litter box",
        scheduled_time=today.replace(hour=9, minute=0),
        frequency="daily"
    ))

    # --- Run scheduler ---
    scheduler = Scheduler(owner)

    print("\n" + "=" * 40)
    print(f"  🐶 PawPal — Today's Schedule")
    print(f"  Owner: {owner.name}")
    print("=" * 40)

    schedule = scheduler.get_todays_schedule()
    scheduler.print_schedule(schedule)

    # --- Demo: mark one task complete ---
    print("\n  > Marking 'Morning walk' as complete...")
    scheduler.complete_task(task_id=1)

    print("\n  --- Pending tasks remaining ---")
    for pet, task in scheduler.get_pending_tasks():
        print(f"  {pet.name}: {task.description}")

    print("\n" + "=" * 40 + "\n")


if __name__ == "__main__":
    main()



"""
main.py
Demo script for Phase 4 — verifies sorting, filtering,
recurring task generation, and conflict detection.
"""

from datetime import datetime, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def section(title: str) -> None:
    print(f"\n{'=' * 45}")
    print(f"  {title}")
    print('=' * 45)


def main():
    owner = Owner(owner_id=1, name="Alex Rivera", email="alex@example.com")

    buddy    = Pet(pet_id=1, name="Buddy",    species="Dog", breed="Labrador", age=3)
    whiskers = Pet(pet_id=2, name="Whiskers", species="Cat", breed="Siamese",  age=5)
    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    today = datetime.now().replace(second=0, microsecond=0)

    # Tasks added OUT OF ORDER intentionally to test sorting
    buddy.add_task(Task(1, "Evening walk",    today.replace(hour=18, minute=0),  "daily"))
    buddy.add_task(Task(2, "Feed breakfast",  today.replace(hour=7,  minute=30), "daily"))
    buddy.add_task(Task(3, "Morning walk",    today.replace(hour=7,  minute=0),  "daily"))
    buddy.add_task(Task(4, "Vet check-up",    today.replace(hour=10, minute=0),  "once"))

    whiskers.add_task(Task(5, "Feed breakfast",  today.replace(hour=8,  minute=0),  "daily"))
    whiskers.add_task(Task(6, "Clean litter box",today.replace(hour=9,  minute=0),  "daily"))

    # Conflict: Buddy has two tasks at exactly 07:00
    buddy.add_task(Task(7, "Give medication", today.replace(hour=7, minute=0), "once"))

    scheduler = Scheduler(owner)

    # ── 1. Today's schedule (sorted) ──────────────────────────────────
    section("Today's Schedule (sorted by time)")
    scheduler.print_schedule(scheduler.get_todays_schedule())

    # ── 2. Filter by pet ──────────────────────────────────────────────
    section("Filter: Whiskers only")
    scheduler.print_schedule(scheduler.filter_by_pet("Whiskers"))

    # ── 3. Filter by status ───────────────────────────────────────────
    section("Filter: all PENDING tasks")
    scheduler.print_schedule(scheduler.filter_by_status("pending"))

    # ── 4. Conflict detection ─────────────────────────────────────────
    section("Conflict Detection")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for w in conflicts:
            print(f"  {w}")
    else:
        print("  No conflicts found.")

    # ── 5. Mark a recurring task complete → auto-generates next one ───
    section("Recurring Task: complete 'Morning walk' (daily)")
    print("  Before:", len(buddy.tasks), "tasks for Buddy")
    scheduler.complete_task(task_id=3)
    print("  After: ", len(buddy.tasks), "tasks for Buddy")

    new_walk = next(
        t for t in buddy.tasks
        if t.description == "Morning walk" and t.status == "pending"
    )
    print(f"  Next occurrence scheduled: "
          f"{new_walk.scheduled_time.strftime('%b %d at %I:%M %p')}")

    # ── 6. Final pending list ─────────────────────────────────────────
    section("All Pending Tasks (after completing morning walk)")
    scheduler.print_schedule(scheduler.filter_by_status("pending"))

    print("\n" + "=" * 45 + "\n")


if __name__ == "__main__":
    main()