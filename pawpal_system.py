"""
pawpal_system.py
Logic layer: all backend class definitions for the PawPal pet care app.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Pet — dataclass (plain data object, no behaviour needed at skeleton stage)
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    pet_id: int
    name: str
    species: str
    breed: str
    age: int
    medical_notes: str = ""

    def get_upcoming_tasks(self) -> list["Task"]:
        """Return all tasks scheduled for this pet that are not yet complete."""
        pass

    def update_medical_notes(self, notes: str) -> None:
        """Append or replace this pet's medical notes."""
        pass


# ---------------------------------------------------------------------------
# Task — dataclass (structured record with status lifecycle)
# ---------------------------------------------------------------------------

@dataclass
class Task:
    task_id: int
    task_type: str          # e.g. "walk", "feed", "vet visit"
    scheduled_time: datetime
    pet: Pet
    status: str = "pending" # pending | in_progress | complete | cancelled
    notes: str = ""
    assigned_to: Optional["Caregiver"] = None

    def mark_complete(self) -> None:
        """Set task status to 'complete' and record completion time."""
        pass

    def reschedule(self, new_time: datetime) -> None:
        """Update the scheduled time for this task."""
        pass

    def assign_caregiver(self, caregiver: "Caregiver") -> None:
        """Link a caregiver to this task."""
        pass


# ---------------------------------------------------------------------------
# Owner — regular class (manages a mutable list of pets)
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, owner_id: int, name: str, email: str, phone: str = ""):
        self.owner_id = owner_id
        self.name = name
        self.email = email
        self.phone = phone
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        pass

    def remove_pet(self, pet_id: int) -> None:
        """Deregister a pet by its ID."""
        pass

    def get_pets(self) -> list[Pet]:
        """Return the list of pets belonging to this owner."""
        pass


# ---------------------------------------------------------------------------
# Caregiver — regular class (manages assignments and ratings)
# ---------------------------------------------------------------------------

class Caregiver:
    def __init__(self, caregiver_id: int, name: str, email: str,
                 specializations: list[str] | None = None):
        self.caregiver_id = caregiver_id
        self.name = name
        self.email = email
        self.specializations: list[str] = specializations or []
        self.rating: float = 0.0
        self._assigned_tasks: list[Task] = []

    def accept_task(self, task: Task) -> None:
        """Accept a task and add it to this caregiver's workload."""
        pass

    def complete_task(self, task: Task) -> None:
        """Mark a task as complete and remove it from active assignments."""
        pass

    def get_assigned_tasks(self) -> list[Task]:
        """Return all tasks currently assigned to this caregiver."""
        pass