
"""
Lab 4: Memory and Retrieval - Multi-Session Project Assistant

Assignment 2: A Staleness / Retention Policy

Features:
1. Long-term project memory
2. Topic-based retrieval
3. Source-tagged answers
4. Conflict detection
5. Permission-controlled memory updates
6. Retention period and stale memory warning
"""

from dataclasses import dataclass
from datetime import date, timedelta


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

    def __init__(self, memory, retention_days=30):
        self.memory = memory

        # Short-term working state
        self.session_facts = {}

        # Maximum age allowed for stored decisions
        self.retention_days = retention_days

    # Answer questions using stored memory
    def answer(self, topic, question):

        hits = self.memory.retrieve(topic)

        if not hits:
            return (
                f"[session] No stored decision on '{topic}' yet. "
                f"{question}"
            )

        latest = hits[-1]

        # Calculate the age of the stored decision
        decision_date = date.fromisoformat(latest.date)
        age_days = (date.today() - decision_date).days

        # Check whether the decision is older than retention period
        if age_days > self.retention_days:

            warning = (
                f"WARNING: this decision is from {age_days} days ago "
                f"and may be out of date.\n"
            )

        else:
            warning = ""

        return (
            warning
            + f"[memory, dated {latest.date}] "
            + f"Per a decision on {latest.date}, {latest.fact}"
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
# STEP 4: Demonstrate fresh and stale memory
# --------------------------------------------------

if __name__ == "__main__":

    memory = ProjectMemory()

    # Configure memory retention period to 30 days
    RETENTION_DAYS = 30

    assistant = ProjectAssistant(
        memory,
        retention_days=RETENTION_DAYS
    )

    today = date.today()

    # Store a fresh decision (3 days old)
    memory.write(
        MemoryRecord(
            topic="database",
            fact="we chose PostgreSQL",
            date=str(today - timedelta(days=3))
        ),
        user_role="team_lead"
    )

    # Store an artificially old decision (45 days old)
    memory.write(
        MemoryRecord(
            topic="hosting",
            fact="we chose AWS for hosting",
            date=str(today - timedelta(days=45))
        ),
        user_role="team_lead"
    )

    # Test fresh memory
    print("=== Fresh Memory Test ===")

    print(
        assistant.answer(
            "database",
            "What did we decide about the database?"
        )
    )

    # Test stale memory
    print("\n=== Old Memory Test ===")

    print(
        assistant.answer(
            "hosting",
            "Where is the project hosted?"
        )
    )

    # Verify retention policy
    print("\n=== Retention Policy Verification ===")

    fresh_answer = assistant.answer(
        "database",
        "What is the database decision?"
    )

    stale_answer = assistant.answer(
        "hosting",
        "What is the hosting decision?"
    )

    assert "WARNING" not in fresh_answer
    assert "PostgreSQL" in fresh_answer

    assert "WARNING" in stale_answer
    assert "45 days ago" in stale_answer
    assert "AWS" in stale_answer

    print("Fresh memory used without warning: PASS")
    print("Old memory warning displayed: PASS")
    print("Stale decision identified correctly: PASS")

    # Test unauthorized memory update
    print("\n=== Permission Verification ===")

    try:
        memory.write(
            MemoryRecord(
                topic="database",
                fact="switch to MongoDB",
                date=str(today)
            ),
            user_role="member"
        )

    except PermissionError as e:
        print(f"Blocked as expected: {e}")
