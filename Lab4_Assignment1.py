
"""
Lab 4: Memory and Retrieval - Multi-Session Project Assistant

Assignment 1: A Second, Isolated Topic

Features:
1. Long-term project memory
2. Topic-based retrieval
3. Source-tagged answers
4. Conflict detection
5. Permission-controlled memory updates
6. Isolation between different topics
"""

from dataclasses import dataclass
from datetime import date


# --------------------------------------------------
# STEP 1: Define a memory record
# --------------------------------------------------

@dataclass
class MemoryRecord:
    topic: str
    fact: str
    date: str
    source: str = "memory"


# --------------------------------------------------
# STEP 2: Implement project memory
# --------------------------------------------------

class ProjectMemory:

    def __init__(self):
        self.records = []

        # Only team leaders can write to memory
        self.allowed_writers = {"team_lead"}

    # Retrieve records for a particular topic
    def retrieve(self, topic):
        return [
            record
            for record in self.records
            if record.topic == topic
        ]

    # Store a record after checking permission
    def write(self, record, user_role):

        if user_role not in self.allowed_writers:
            raise PermissionError(
                f"role '{user_role}' is not permitted to write memory"
            )

        self.records.append(record)


# --------------------------------------------------
# STEP 3: Implement the project assistant
# --------------------------------------------------

class ProjectAssistant:

    def __init__(self, memory):
        self.memory = memory

        # Short-term working state
        self.session_facts = {}

    # Answer questions using stored memory
    def answer(self, topic, question):

        hits = self.memory.retrieve(topic)

        if not hits:
            return (
                f"[session] No stored decision on '{topic}' yet. "
                f"{question}"
            )

        latest = hits[-1]

        return (
            f"[memory, dated {latest.date}] "
            f"Per a decision on {latest.date}, {latest.fact}"
        )

    # Receive a new statement and check for conflicts
    def receive_statement(self, topic, new_fact, user_role):

        hits = self.memory.retrieve(topic)

        # Check whether the new statement conflicts with memory
        if hits and hits[-1].fact.lower() != new_fact.lower():

            return {
                "conflict": True,
                "stored": hits[-1].fact,
                "stored_date": hits[-1].date,
                "new": new_fact,

                "message": (
                    f"This conflicts with the stored decision from "
                    f"{hits[-1].date} ('{hits[-1].fact}'). "
                    f"Should I update memory to '{new_fact}'?"
                ),
            }

        # No conflict: prepare a new memory record
        record = MemoryRecord(
            topic=topic,
            fact=new_fact,
            date=str(date.today())
        )

        # Write only if the user has permission
        self.memory.write(record, user_role)

        return {
            "conflict": False,
            "message": f"Recorded: {new_fact}",
            "written": True
        }


# --------------------------------------------------
# STEP 4: Demonstrate memory operations
# --------------------------------------------------

if __name__ == "__main__":

    memory = ProjectMemory()

    # Initially store a database decision
    memory.write(
        MemoryRecord(
            topic="database",
            fact="we chose PostgreSQL",
            date="2026-07-03"
        ),
        user_role="team_lead"
    )

    # ADDITION: Store a separate hosting decision
    memory.write(
        MemoryRecord(
            topic="hosting",
            fact="we chose AWS for project hosting",
            date="2026-07-05"
        ),
        user_role="team_lead"
    )

    assistant = ProjectAssistant(memory)

    # Display the original database decision
    print("=== Database Decision ===")

    database_answer = assistant.answer(
        "database",
        "What did we decide about the database?"
    )

    print(database_answer)

    # ADDITION: Retrieve hosting decision independently
    print("\n=== Hosting Decision ===")

    hosting_answer = assistant.answer(
        "hosting",
        "Where is the project hosted?"
    )

    print(hosting_answer)

    # ADDITION: Verify topic isolation
    print("\n=== Topic Isolation Verification ===")

    assert "PostgreSQL" in database_answer
    assert "AWS" not in database_answer

    assert "AWS" in hosting_answer
    assert "PostgreSQL" not in hosting_answer

    print("Database retrieval contains only database information: PASS")
    print("Hosting retrieval contains only hosting information: PASS")
    print("No cross-topic information leakage: PASS")

    # --------------------------------------------------
    # Original conflict detection demonstration
    # --------------------------------------------------

    print("\n--- A team member proposes a database change ---")

    result = assistant.receive_statement(
        "database",
        "we're switching to SQLite",
        user_role="member"
    )

    print(result["message"])

    # Team lead confirms the proposed change
    print("\n--- Team lead confirms the switch (permitted write) ---")

    assistant.receive_statement(
        "database",
        "we're switching to SQLite",
        user_role="team_lead"
    )

    if result["conflict"]:

        memory.write(
            MemoryRecord(
                topic="database",
                fact="we're switching to SQLite",
                date=str(date.today())
            ),
            user_role="team_lead"
        )

        print("Write permitted: memory updated by team_lead.")

    # Test unauthorized memory update
    print("\n--- Attempted write by an unpermitted role ---")

    try:

        memory.write(
            MemoryRecord(
                topic="database",
                fact="switch to MongoDB",
                date=str(date.today())
            ),
            user_role="member"
        )

    except PermissionError as e:

        print(f"Blocked as expected: {e}")

    # Display the latest database decision
    print("\n--- Final database decision ---")

    print(
        assistant.answer(
            "database",
            "What did we decide about the database?"
        )
    )

    # Confirm hosting decision remains unchanged
    print("\n--- Hosting decision remains isolated ---")

    print(
        assistant.answer(
            "hosting",
            "Where is the project hosted?"
        )
    )

    assert "AWS" in assistant.answer("hosting", "Where is hosting?")
    assert "SQLite" not in assistant.answer("hosting", "Where is hosting?")

    print("\nFinal topic isolation check: PASS")
