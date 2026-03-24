# PawPal+ Project Reflection

## 1. System Design
My initial UML design consisted of four main classes: Owner, Pet, Task, and Scheduler.

- The Owner class represents the user and stores their available time, preferences, and pets. It is responsible for managing pets and retrieving all tasks.
- The Pet class stores basic pet information and maintains a list of tasks associated with that pet.
- The Task class represents individual care activities such as feeding, walking, or medication. Each task includes attributes like duration, priority, and optional time constraints.
- The Scheduler class handles the core logic of the system. It collects tasks from all pets, prioritizes them, and generates a daily schedule based on constraints.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
The system uses four classes. Owner manages a collection of pets and is the entry point for creating tasks. Pet holds the animal's data and medical history — it's a dataclass because it's primarily a data record. Task (also a dataclass) represents a scheduled care event with a status lifecycle (pending → complete). Caregiver accepts and fulfills tasks, and tracks their own workload. The main relationships are: Owner has many Pets, Pet has many Tasks, and a Caregiver is assigned to many Tasks.



**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, my design evolved during implementation.

Initially, I considered placing scheduling logic inside the Owner class. However, I refactored this into a separate Scheduler class. This change improved separation of concerns and made the system more maintainable and testable.

I also added optional attributes like time_window to the Task class to support future features such as scheduling tasks at specific times of day.

......one thing worth noting is that Task holds a direct reference to Pet, which creates tight coupling — a future improvement would be to use IDs instead of object references to make persistence easier.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
The scheduler considers the following constraints:

Total available time (hard constraint)
Task duration
Task priority (higher priority tasks are scheduled first)
Optional time preferences (e.g., morning or evening tasks)

Priority and available time were the most important constraints because the goal is to ensure that the most critical tasks are completed within a limited time.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Conflict detection — exact-minute matching only
The current detect_conflicts() method flags tasks scheduled at the exact same minute for the same pet. It does not account for task duration — a 30-minute walk starting at 08:00 and a vet appointment at 08:15 will not be flagged even though they practically overlap.
This was a deliberate tradeoff: exact-minute matching is O(n) with a dictionary lookup and never crashes or produces false positives. Duration-based overlap detection would require every Task to carry an end_time field and would need pairwise O(n²) comparisons, or a more complex interval-tree structure. For a household scheduler with a small number of daily tasks, the simpler model is easier to reason about and sufficient for real use.
If the app grows to support professional caregivers managing dozens of pets, upgrading to interval-based conflict detection would be the right next step.
Recurring task IDs — offset strategy
New recurring tasks receive task_id = original_id + 10000 to avoid collision with existing IDs. This works for a single-session in-memory app but would break in a database-backed system where IDs must be unique and auto-incremented. A production fix would use a central ID counter stored in st.session_state (already done in app.py) or a database sequence.


---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
I used AI tools to:

Brainstorm the system design and identify core classes
Generate a UML diagram using Mermaid syntax
Create Python class skeletons using dataclasses
Refactor and improve code structure

The most helpful prompts were:

“Generate a class diagram for a pet care scheduling system”
“Convert this UML into Python dataclasses”
“Review this code for missing relationships or design issues”

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
One instance where I did not fully accept AI output was when it suggested placing too much logic inside a single class.

Instead of using it directly, I evaluated whether the design followed good software principles like separation of concerns. I decided to keep scheduling logic in a separate Scheduler class to improve modularity and testability.

I verified decisions by checking if:

Each class had a clear responsibility
The system would be easy to extend later
The logic could be tested independently

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
I tested key behaviors such as:

Tasks are sorted correctly by priority
Tasks exceeding available time are not scheduled
The scheduler handles empty task lists gracefully
Total scheduled time does not exceed available time

These tests were important to ensure that the scheduling logic behaves correctly under normal and edge conditions.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
I am reasonably confident that my scheduler works correctly for the core functionality.

If I had more time, I would test additional edge cases such as:

Tasks with equal priority
Tasks with time windows (morning vs evening conflicts)
Very large numbers of tasks
Scenarios where no tasks fit within the available time

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
