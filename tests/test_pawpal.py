"""
tests/test_pawpal.py
Basic unit tests for PawPal core logic.
Run with: python -m pytest
"""

from datetime import datetime
from pawpal_system import Task, Pet, Owner, Scheduler


# --- Fixtures ---

def make_task(task_id=1, description="Walk", hour=8):
    return Task(
        task_id=task_id,
        description=description,
        scheduled_time=datetime.now().replace(hour=hour, minute=0)
    )

def make_pet():
    return Pet(pet_id=1, name="Buddy", species="Dog", breed="Lab", age=3)


# --- Tests ---

def test_mark_complete_changes_status():
    """mark_complete() should set task status to 'complete'."""
    task = make_task()
    assert task.status == "pending"
    task.mark_complete()
    assert task.status == "complete"


def test_mark_complete_is_idempotent():
    """Calling mark_complete() twice should not raise an error."""
    task = make_task()
    task.mark_complete()
    task.mark_complete()
    assert task.status == "complete"


def test_add_task_increases_count():
    """Adding a task to a Pet should increase its task list length by 1."""
    pet = make_pet()
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1


def test_add_multiple_tasks():
    """Adding three tasks should result in a task list of length 3."""
    pet = make_pet()
    for i in range(3):
        pet.add_task(make_task(task_id=i))
    assert len(pet.tasks) == 3


def test_get_upcoming_excludes_complete():
    """get_upcoming_tasks() should not return completed tasks."""
    pet = make_pet()
    t1 = make_task(task_id=1, description="Walk")
    t2 = make_task(task_id=2, description="Feed")
    t1.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)
    upcoming = pet.get_upcoming_tasks()
    assert len(upcoming) == 1
    assert upcoming[0].description == "Feed"


def test_scheduler_complete_task():
    """Scheduler.complete_task() should mark the correct task complete."""
    owner = Owner(1, "Alex", "alex@example.com")
    pet = make_pet()
    task = make_task(task_id=99)
    pet.add_task(task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    result = scheduler.complete_task(99)
    assert result is True
    assert task.status == "complete"



"""
tests/test_pawpal.py
Unit tests for PawPal — covers Phase 2 basics + Phase 4 algorithms.
Run with: python -m pytest -v
"""

from datetime import datetime, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(task_id=1, description="Walk", hour=8, minute=0, frequency="once"):
    return Task(
        task_id=task_id,
        description=description,
        scheduled_time=datetime.now().replace(
            hour=hour, minute=minute, second=0, microsecond=0
        ),
        frequency=frequency,
    )

def make_pet(pet_id=1, name="Buddy"):
    return Pet(pet_id=pet_id, name=name, species="Dog", breed="Lab", age=3)

def make_owner_with_pets():
    owner = Owner(1, "Alex", "alex@example.com")
    buddy    = make_pet(pet_id=1, name="Buddy")
    whiskers = make_pet(pet_id=2, name="Whiskers")
    owner.add_pet(buddy)
    owner.add_pet(whiskers)
    return owner, buddy, whiskers


# ---------------------------------------------------------------------------
# Phase 2 — basics
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """mark_complete() should set task status to 'complete'."""
    task = make_task()
    assert task.status == "pending"
    task.mark_complete()
    assert task.status == "complete"

def test_mark_complete_is_idempotent():
    task = make_task()
    task.mark_complete()
    task.mark_complete()
    assert task.status == "complete"

def test_add_task_increases_count():
    pet = make_pet()
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1

def test_add_multiple_tasks():
    pet = make_pet()
    for i in range(3):
        pet.add_task(make_task(task_id=i))
    assert len(pet.tasks) == 3

def test_get_upcoming_excludes_complete():
    pet = make_pet()
    t1 = make_task(task_id=1, description="Walk")
    t2 = make_task(task_id=2, description="Feed")
    t1.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)
    upcoming = pet.get_upcoming_tasks()
    assert len(upcoming) == 1
    assert upcoming[0].description == "Feed"


# ---------------------------------------------------------------------------
# Phase 4 — sorting
# ---------------------------------------------------------------------------

def test_sort_by_time_orders_ascending():
    """sort_by_time() should return tasks in earliest-first order."""
    owner, buddy, _ = make_owner_with_pets()
    buddy.add_task(make_task(task_id=1, hour=10))
    buddy.add_task(make_task(task_id=2, hour=7))
    buddy.add_task(make_task(task_id=3, hour=14))

    scheduler = Scheduler(owner)
    sorted_pairs = scheduler.sort_by_time(scheduler.owner.get_all_tasks())
    times = [task.scheduled_time.hour for _, task in sorted_pairs]
    assert times == sorted(times)


# ---------------------------------------------------------------------------
# Phase 4 — filtering
# ---------------------------------------------------------------------------

def test_filter_by_pet_returns_only_that_pet():
    owner, buddy, whiskers = make_owner_with_pets()
    buddy.add_task(make_task(task_id=1, description="Walk"))
    whiskers.add_task(make_task(task_id=2, description="Feed"))

    scheduler = Scheduler(owner)
    results = scheduler.filter_by_pet("Buddy")
    assert all(pet.name == "Buddy" for pet, _ in results)
    assert len(results) == 1

def test_filter_by_status_pending():
    owner, buddy, _ = make_owner_with_pets()
    t1 = make_task(task_id=1)
    t2 = make_task(task_id=2)
    t1.mark_complete()
    buddy.add_task(t1)
    buddy.add_task(t2)

    scheduler = Scheduler(owner)
    pending = scheduler.filter_by_status("pending")
    assert all(task.status == "pending" for _, task in pending)

def test_filter_by_status_complete():
    owner, buddy, _ = make_owner_with_pets()
    t = make_task()
    t.mark_complete()
    buddy.add_task(t)

    scheduler = Scheduler(owner)
    complete = scheduler.filter_by_status("complete")
    assert len(complete) == 1


# ---------------------------------------------------------------------------
# Phase 4 — recurring tasks
# ---------------------------------------------------------------------------

def test_daily_task_creates_next_occurrence():
    """Completing a daily task should add a new task 1 day later."""
    owner, buddy, _ = make_owner_with_pets()
    task = make_task(task_id=10, frequency="daily")
    original_time = task.scheduled_time
    buddy.add_task(task)

    scheduler = Scheduler(owner)
    scheduler.complete_task(task_id=10)

    assert task.status == "complete"
    assert len(buddy.tasks) == 2
    new_task = buddy.tasks[1]
    assert new_task.scheduled_time == original_time + timedelta(days=1)
    assert new_task.status == "pending"

def test_weekly_task_creates_next_occurrence():
    owner, buddy, _ = make_owner_with_pets()
    task = make_task(task_id=20, frequency="weekly")
    original_time = task.scheduled_time
    buddy.add_task(task)

    scheduler = Scheduler(owner)
    scheduler.complete_task(task_id=20)

    new_task = buddy.tasks[1]
    assert new_task.scheduled_time == original_time + timedelta(weeks=1)

def test_once_task_does_not_recur():
    """Completing a 'once' task should NOT add any new task."""
    owner, buddy, _ = make_owner_with_pets()
    task = make_task(task_id=30, frequency="once")
    buddy.add_task(task)

    scheduler = Scheduler(owner)
    scheduler.complete_task(task_id=30)

    assert len(buddy.tasks) == 1


# ---------------------------------------------------------------------------
# Phase 4 — conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_finds_same_time():
    """Two tasks for the same pet at the same minute should be flagged."""
    owner, buddy, _ = make_owner_with_pets()
    buddy.add_task(make_task(task_id=1, description="Walk",       hour=8, minute=0))
    buddy.add_task(make_task(task_id=2, description="Medication", hour=8, minute=0))

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "Buddy" in warnings[0]

def test_detect_conflicts_no_conflict():
    owner, buddy, _ = make_owner_with_pets()
    buddy.add_task(make_task(task_id=1, hour=8,  minute=0))
    buddy.add_task(make_task(task_id=2, hour=9,  minute=0))
    buddy.add_task(make_task(task_id=3, hour=10, minute=0))

    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []