"""
pawpal_system.py
Logic layer: full implementation of the PawPal pet care app classes.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Represents a single care activity assigned to a pet."""
    task_id: int
    description: str
    scheduled_time: datetime
    frequency: str = "once"       # once | daily | weekly
    status: str = "pending"       # pending | complete
    notes: str = ""

    def mark_complete(self) -> None:
        """Mark this task as complete."""
        self.status = "complete"

    def is_complete(self) -> bool:
        """Return True if the task has been completed."""
        return self.status == "complete"

    def __str__(self) -> str:
        tick = "✓" if self.is_complete() else "○"
        t = self.scheduled_time.strftime("%I:%M %p")
        return f"  [{tick}] {t} — {self.description} ({self.frequency})"


@dataclass
class Pet:
    """Stores pet details and owns a list of care tasks."""
    pet_id: int
    name: str
    species: str
    breed: str
    age: int
    medical_notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def get_upcoming_tasks(self) -> list[Task]:
        """Return all tasks that are not yet complete, sorted by time."""
        return sorted(
            [t for t in self.tasks if not t.is_complete()],
            key=lambda t: t.scheduled_time
        )

    def update_medical_notes(self, notes: str) -> None:
        """Append a note to this pet's medical history."""
        self.medical_notes += f"\n{notes}" if self.medical_notes else notes

    def __str__(self) -> str:
        return f"{self.name} ({self.species}, {self.age}yr)"


class Owner:
    """Manages an owner profile and their collection of pets."""

    def __init__(self, owner_id: int, name: str, email: str, phone: str = ""):
        self.owner_id = owner_id
        self.name = name
        self.email = email
        self.phone = phone
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: int) -> None:
        """Deregister a pet by its ID."""
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

    def get_pets(self) -> list[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every task across all pets as (pet, task) pairs."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Retrieves, organizes, and manages tasks across an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_todays_schedule(self) -> list[tuple[Pet, Task]]:
        """Return all of today's tasks sorted by scheduled time."""
        today = datetime.now().date()
        todays = [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if task.scheduled_time.date() == today
        ]
        return sorted(todays, key=lambda x: x[1].scheduled_time)

    def get_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all incomplete tasks across every pet."""
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if not task.is_complete()
        ]

    def complete_task(self, task_id: int) -> bool:
        """Find a task by ID and mark it complete. Returns True if found."""
        for _, task in self.owner.get_all_tasks():
            if task.task_id == task_id:
                task.mark_complete()
                return True
        return False

    def print_schedule(self, schedule: list[tuple[Pet, Task]]) -> None:
        """Print a formatted daily schedule to the terminal."""
        if not schedule:
            print("  No tasks scheduled.")
            return
        current_pet = None
        for pet, task in schedule:
            if pet != current_pet:
                print(f"\n  🐾 {pet}")
                current_pet = pet
            print(task)