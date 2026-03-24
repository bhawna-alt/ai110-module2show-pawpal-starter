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