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