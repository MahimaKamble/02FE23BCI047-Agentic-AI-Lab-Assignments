"""
Lab 6: OpenCLA/OpenClaw Runtime
Assignment 2: Escalate After Two Failures

If the same skill fails twice for the same user,
the third attempt is escalated to a human.

Previous failures are counted from the existing audit log.
"""

from datetime import datetime


# ---- Tools ------------------------------------------------------------

def tool_word_count(text):
    return {"count": len(text.split())}


def tool_lookup_contact(name, contacts_db):
    return contacts_db.get(
        name,
        {"error": f"no contact found for {name}"}
    )


TOOLS = {
    "word_count": tool_word_count,
    "lookup_contact": tool_lookup_contact
}


# ---- Memory, scoped per user ------------------------------------------

class Memory:
    def __init__(self):
        self._store = {}

    def scope(self, user):
        return self._store.setdefault(user, {})


# ---- Audit -------------------------------------------------------------

class Audit:
    def __init__(self):
        self.entries = []

    def log(
        self,
        task,
        skill_name,
        tool_calls,
        user,
        result=None,
        error=None
    ):
        self.entries.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "user": user,
            "task": task,
            "skill": skill_name,
            "tool_calls": tool_calls,
            "result": result,
            "error": error
        })


# ---- Skills ------------------------------------------------------------

class SummarizeNotesSkill:
    def __init__(self, memory_scope):
        self.memory_scope = memory_scope
        self.tool_calls = []

    def execute(self, task):
        text = task.get("text", "")

        wc = TOOLS["word_count"](text)

        self.tool_calls.append({
            "tool": "word_count",
            "output": wc
        })

        self.memory_scope["last_note_length"] = wc["count"]

        return f"Summary stub: note has {wc['count']} words."


class DraftEmailSkill:
    CONTACTS = {
        "Dr. Meena": {
            "email": "meena@example.edu"
        }
    }

    def __init__(self, memory_scope):
        self.memory_scope = memory_scope
        self.tool_calls = []

    def execute(self, task):
        contact = TOOLS["lookup_contact"](
            task["to"],
            self.CONTACTS
        )

        self.tool_calls.append({
            "tool": "lookup_contact",
            "output": contact
        })

        if "error" in contact:
            raise RuntimeError(contact["error"])

        return (
            f"Draft email to {contact['email']}: "
            f"'{task['subject']}'"
        )


class TranslateTextSkill:
    def __init__(self, memory_scope):
        self.memory_scope = memory_scope
        self.tool_calls = []

    def execute(self, task):
        return (
            f"[translated to {task['target_lang']}] "
            f"{task['text']}"
        )


# ---- Skill Registry ----------------------------------------------------

SKILL_REGISTRY = {
    "summarize_notes": SummarizeNotesSkill,
    "draft_email": DraftEmailSkill,
    "translate_text": TranslateTextSkill
}


# ---- Runtime Core Loop -------------------------------------------------

def select_skill(task):
    return task["skill"]


def run_task(task, user, memory, audit):
    skill_name = select_skill(task)
    skill_cls = SKILL_REGISTRY[skill_name]
    skill = skill_cls(memory.scope(user))

    try:
        result = skill.execute(task)

        audit.log(
            task,
            skill_name,
            skill.tool_calls,
            user=user,
            result=result
        )

        return result

    except Exception as e:
        audit.log(
            task,
            skill_name,
            skill.tool_calls,
            user=user,
            error=str(e)
        )

        raise


# ---- Interface with Failure Escalation -------------------------------

MAX_FAILURES = 2


def receive_task(task, user, memory, audit):
    skill_name = task["skill"]

    # Count previous failures from the audit log
    # for this particular user and skill.
    previous_failures = sum(
        1
        for entry in audit.entries
        if entry["user"] == user
        and entry["skill"] == skill_name
        and entry["error"] is not None
    )

    # Escalate instead of executing the third attempt.
    if previous_failures >= MAX_FAILURES:
        message = (
            f"Human escalation required: skill '{skill_name}' "
            f"has already failed {previous_failures} times "
            f"for user '{user}'."
        )

        audit.log(
            task,
            skill_name,
            [],
            user=user,
            error=message
        )

        return {
            "escalated": True,
            "message": message
        }

    return run_task(task, user, memory, audit)


# ---- Main Program ------------------------------------------------------

if __name__ == "__main__":

    memory = Memory()
    audit = Audit()

    print("=== Successful Run: Summarize Notes ===")

    result = receive_task(
        {
            "skill": "summarize_notes",
            "text": "Agentic AI systems combine goals tools skills memory"
        },
        user="uday",
        memory=memory,
        audit=audit
    )

    print(result)


    print("\n=== Successful Run: Draft Email ===")

    result = receive_task(
        {
            "skill": "draft_email",
            "to": "Dr. Meena",
            "subject": "Lab guide review"
        },
        user="uday",
        memory=memory,
        audit=audit
    )

    print(result)


    # First failure
    print("\n=== Draft Email Attempt 1: Unknown Contact ===")

    try:
        result = receive_task(
            {
                "skill": "draft_email",
                "to": "Unknown Person",
                "subject": "Hello"
            },
            user="maya",
            memory=memory,
            audit=audit
        )

        print(result)

    except RuntimeError as e:
        print(f"Skill failed: {e}")


    # Second failure
    print("\n=== Draft Email Attempt 2: Unknown Contact ===")

    try:
        result = receive_task(
            {
                "skill": "draft_email",
                "to": "Unknown Person",
                "subject": "Follow-up"
            },
            user="maya",
            memory=memory,
            audit=audit
        )

        print(result)

    except RuntimeError as e:
        print(f"Skill failed: {e}")


    # Third attempt: should be escalated, not executed
    print("\n=== Draft Email Attempt 3: Escalation ===")

    result = receive_task(
        {
            "skill": "draft_email",
            "to": "Unknown Person",
            "subject": "Third attempt"
        },
        user="maya",
        memory=memory,
        audit=audit
    )

    print(result)


    print("\n=== Escalation Verification ===")

    print("Escalation triggered:", result["escalated"])
    print("Third attempt executed:", not result["escalated"])


    print("\n=== Full Audit Log ===")

    for entry in audit.entries:
        print(entry)


    print("\n=== Scoped Memory ===")

    print("uday:", memory.scope("uday"))
    print("maya:", memory.scope("maya"))