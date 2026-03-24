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

"""
pawpal_system.py
Logic layer: full implementation of the PawPal pet care app classes.
Includes sorting, filtering, recurring task generation, and conflict detection.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
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

    def next_occurrence(self) -> Optional["Task"]:
        """
        Return a new pending Task for the next occurrence based on frequency.
        Returns None if the task is 'once' (non-recurring).
        """
        if self.frequency == "daily":
            delta = timedelta(days=1)
        elif self.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None

        return Task(
            task_id=self.task_id + 10000,   # offset to avoid ID collision
            description=self.description,
            scheduled_time=self.scheduled_time + delta,
            frequency=self.frequency,
            notes=self.notes,
        )

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
        """Return all incomplete tasks sorted by scheduled time."""
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

    # ------------------------------------------------------------------
    # Core retrieval
    # ------------------------------------------------------------------

    def get_todays_schedule(self) -> list[tuple[Pet, Task]]:
        """Return all of today's tasks sorted by scheduled time."""
        today = datetime.now().date()
        return self.sort_by_time([
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if task.scheduled_time.date() == today
        ])

    def get_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all incomplete tasks across every pet."""
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if not task.is_complete()
        ]

    # ------------------------------------------------------------------
    # Step 2: Sorting and filtering
    # ------------------------------------------------------------------

    def sort_by_time(
        self, pairs: list[tuple[Pet, Task]]
    ) -> list[tuple[Pet, Task]]:
        """
        Sort (pet, task) pairs in ascending order by scheduled_time.
        Uses a lambda key so no external comparator is needed.
        """
        return sorted(pairs, key=lambda x: x[1].scheduled_time)

    def filter_by_pet(self, pet_name: str) -> list[tuple[Pet, Task]]:
        """
        Return all tasks belonging to the pet with the given name.
        Case-insensitive match.
        """
        name = pet_name.strip().lower()
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if pet.name.lower() == name
        ]

    def filter_by_status(self, status: str) -> list[tuple[Pet, Task]]:
        """
        Return all tasks matching 'pending' or 'complete'.
        Raises ValueError for unknown status strings.
        """
        if status not in ("pending", "complete"):
            raise ValueError(f"Unknown status '{status}'. Use 'pending' or 'complete'.")
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if task.status == status
        ]

    # ------------------------------------------------------------------
    # Step 3: Recurring task handling
    # ------------------------------------------------------------------

    def complete_task(self, task_id: int) -> bool:
        """
        Mark a task complete by ID. If the task recurs (daily/weekly),
        automatically add the next occurrence to the pet's task list.
        Returns True if the task was found, False otherwise.
        """
        for pet, task in self.owner.get_all_tasks():
            if task.task_id == task_id:
                task.mark_complete()
                next_task = task.next_occurrence()
                if next_task:
                    pet.add_task(next_task)
                return True
        return False

    # ------------------------------------------------------------------
    # Step 4: Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(self) -> list[str]:
        """
        Check for tasks scheduled at the exact same time for the same pet.
        Returns a list of human-readable warning strings (empty = no conflicts).
        Uses a dict keyed by (pet_id, rounded_minute) for O(n) detection.

        Tradeoff: only catches exact-minute collisions, not overlapping
        durations — kept simple intentionally (see reflection.md §2b).
        """
        seen: dict[tuple[int, datetime], str] = {}
        warnings: list[str] = []

        for pet, task in self.owner.get_all_tasks():
            key = (pet.pet_id, task.scheduled_time.replace(second=0, microsecond=0))
            if key in seen:
                warnings.append(
                    f"⚠️  Conflict for {pet.name}: "
                    f"'{task.description}' and '{seen[key]}' "
                    f"both at {task.scheduled_time.strftime('%I:%M %p')} "
                    f"on {task.scheduled_time.strftime('%b %d')}"
                )
            else:
                seen[key] = task.description

        return warnings

    # ------------------------------------------------------------------
    # Display helper
    # ------------------------------------------------------------------

    def print_schedule(self, schedule: list[tuple[Pet, Task]]) -> None:
        """Print a formatted schedule grouped by pet."""
        if not schedule:
            print("  No tasks found.")
            return
        current_pet = None
        for pet, task in schedule:
            if pet != current_pet:
                print(f"\n  🐾 {pet}")
                current_pet = pet
            print(task)