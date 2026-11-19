"""
Lab 6: OpenCLA/OpenClaw Runtime
Assignment 1: Add Per-User Rate Limiting

Each user can run at most 3 tasks per session.
The fourth task from the same user is rejected.

The original runtime loop and skill-dispatch logic remain unchanged.
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

    def log(self, task, skill_name, tool_calls, result=None, error=None):
        self.entries.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
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


# ---- Runtime Core Loop: unchanged -------------------------------------

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
            result=result
        )

        return result

    except Exception as e:
        audit.log(
            task,
            skill_name,
            skill.tool_calls,
            error=str(e)
        )
        raise


# ---- Interface with Per-User Rate Limiting ----------------------------

MAX_TASKS_PER_SESSION = 3


def receive_task(task, user, memory, audit):
    user_memory = memory.scope(user)

    tasks_run = user_memory.get("_session_task_count", 0)

    # Reject the task if the user has already reached the limit.
    if tasks_run >= MAX_TASKS_PER_SESSION:
        reason = (
            f"session limit reached: maximum "
            f"{MAX_TASKS_PER_SESSION} tasks per user"
        )

        audit.log(
            task,
            task.get("skill", "unknown"),
            [],
            error=reason
        )

        return {
            "rejected": True,
            "reason": reason
        }

    # Count the task before execution.
    # Failed executions also count as attempted tasks.
    user_memory["_session_task_count"] = tasks_run + 1

    return run_task(task, user, memory, audit)


# ---- Main Program ------------------------------------------------------

if __name__ == "__main__":

    memory = Memory()
    audit = Audit()

    print("=== Task 1: Summarize Notes (uday) ===")

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


    print("\n=== Task 2: Draft Email (uday) ===")

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


    print("\n=== Task 3: Draft Email to Unknown Contact (uday) ===")

    try:
        result = receive_task(
            {
                "skill": "draft_email",
                "to": "Unknown Person",
                "subject": "Hello"
            },
            user="uday",
            memory=memory,
            audit=audit
        )

        print(result)

    except RuntimeError as e:
        print(f"Run failed as expected: {e}")


    print("\n=== Task 4: Translate Text (uday) ===")

    result = receive_task(
        {
            "skill": "translate_text",
            "text": "Hello, team",
            "target_lang": "Kannada"
        },
        user="uday",
        memory=memory,
        audit=audit
    )

    print(result)


    print("\n=== Per-User Limit Verification ===")

    print(
        "Tasks used by uday:",
        memory.scope("uday")["_session_task_count"]
    )

    print(
        "Fourth task rejected:",
        result["rejected"]
    )


    print("\n=== Same Skill for a Different User (maya) ===")

    result = receive_task(
        {
            "skill": "translate_text",
            "text": "Hello, team",
            "target_lang": "Kannada"
        },
        user="maya",
        memory=memory,
        audit=audit
    )

    print(result)

    print(
        "Tasks used by maya:",
        memory.scope("maya")["_session_task_count"]
    )


    print("\n=== Full Audit Log ===")

    for entry in audit.entries:
        print(entry)


    print("\n=== Scoped Memory ===")

    print("uday:", memory.scope("uday"))
    print("maya:", memory.scope("maya"))