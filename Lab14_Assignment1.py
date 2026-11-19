
"""
Lab 14: Capstone Project Studio
Assignment 1: Add a Second Reusable Skill

Original skill: triage_skill
New skill: password_reset_skill

The node graph routes requests to the appropriate skill.
"""

from datetime import datetime

# ============================================================
# TOOLS (3)
# ============================================================

FAQ_DB = {
    "wifi": "Connect to 'Campus-Secure' and log in with your student ID."
}

TICKET_DB = []


def tool_search_faq(query):
    for key, value in FAQ_DB.items():
        if key in query.lower():
            return {"found": True, "answer": value}

    return {"found": False}


def tool_create_ticket(issue):
    ticket_id = f"T-{len(TICKET_DB) + 1:03d}"

    TICKET_DB.append({
        "id": ticket_id,
        "issue": issue,
        "status": "open"
    })

    return {"ticket_id": ticket_id}


def tool_check_ticket_status(ticket_id):
    for ticket in TICKET_DB:
        if ticket["id"] == ticket_id:
            return ticket

    return {"error": "not found"}


# ============================================================
# SKILL 1: TRIAGE AND RESPOND
# ============================================================

def triage_skill(issue_text):
    """
    Instructions:
    Search the FAQ first.
    Create a support ticket only if no FAQ match exists.

    Constraint:
    Never fabricate an FAQ answer.
    """

    faq_result = tool_search_faq(issue_text)

    if faq_result["found"]:
        return {
            "skill": "triage_skill",
            "resolution": "faq",
            "answer": faq_result["answer"]
        }

    ticket = tool_create_ticket(issue_text)

    return {
        "skill": "triage_skill",
        "resolution": "escalated",
        "ticket_id": ticket["ticket_id"]
    }


# ============================================================
# SKILL 2: PASSWORD RESET GUIDANCE (NEW)
# ============================================================

def password_reset_skill(issue_text):
    """
    Instructions:
    Identify password-reset requests and provide the
    approved password-reset guidance.

    Constraint:
    Never request or store the user's current password.
    Never claim that the password has been reset automatically.
    """

    return {
        "skill": "password_reset_skill",
        "resolution": "guidance",
        "answer": (
            "To reset your campus account password, visit the "
            "official university password-reset portal. "
            "Follow the identity verification steps and create "
            "a new password. Contact IT support if you cannot "
            "complete the verification."
        )
    }


# ============================================================
# MEMORY: SHORT-TERM AND LONG-TERM
# ============================================================

class CapstoneMemory:

    def __init__(self):
        self.session = {}
        self.history = []

    def record(self, user, issue, outcome):

        entry = {
            "user": user,
            "issue": issue,
            "outcome": outcome,
            "date": datetime.now().isoformat(timespec="seconds")
        }

        self.history.append(entry)
        self.session["last_issue"] = issue


# ============================================================
# NODE GRAPH
# INTAKE -> SKILL ROUTING -> RESPONSE -> LOG
# ============================================================

def route_to_skill(issue_text):

    text = issue_text.lower()

    # Route password-related requests to Skill 2.
    if "password" in text and (
        "reset" in text or "forgot" in text
    ):
        return password_reset_skill(issue_text)

    # All other requests go through the original triage skill.
    return triage_skill(issue_text)


def node_graph_run(user, issue, memory, audit_log, prompt_log):

    # Node 1: Intake
    prompt_log.append({
        "stage": "intake",
        "input": issue
    })

    # Safety control: reject empty input.
    if not issue.strip():

        audit_log.append({
            "stage": "intake",
            "result": "rejected: empty issue"
        })

        return {
            "rejected": True,
            "reason": "empty issue text"
        }

    # Node 2: Skill routing and execution
    outcome = route_to_skill(issue)

    prompt_log.append({
        "stage": "skill_routing",
        "selected_skill": outcome["skill"],
        "output": outcome
    })

    # Node 3: Prepare response
    if outcome["resolution"] == "faq":
        response = outcome["answer"]

    elif outcome["resolution"] == "guidance":
        response = outcome["answer"]

    else:
        response = (
            f"Ticket {outcome['ticket_id']} created; "
            "support will follow up."
        )

    # Node 4: Memory and audit logging
    memory.record(user, issue, outcome)

    audit_log.append({
        "stage": "complete",
        "user": user,
        "issue": issue,
        "selected_skill": outcome["skill"],
        "outcome": outcome
    })

    return {
        "rejected": False,
        "response": response,
        "outcome": outcome
    }


# ============================================================
# EVALUATION
# ============================================================

def run_evaluation():

    cases = [
        ("How do I connect to wifi?", "triage_skill"),
        ("I forgot my password and need a reset.", "password_reset_skill")
    ]

    memory = CapstoneMemory()
    audit_log = []
    prompt_log = []

    results = []

    for issue, expected_skill in cases:

        result = node_graph_run(
            "eval_user",
            issue,
            memory,
            audit_log,
            prompt_log
        )

        actual_skill = result["outcome"]["skill"]

        results.append({
            "issue": issue,
            "expected": expected_skill,
            "actual": actual_skill,
            "passed": actual_skill == expected_skill
        })

    return results


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    memory = CapstoneMemory()
    audit_log = []
    prompt_log = []

    # Demonstration 1: Original triage skill
    print("=== Run 1: Original Triage Skill ===")

    r1 = node_graph_run(
        "alice",
        "How do I connect to wifi on campus?",
        memory,
        audit_log,
        prompt_log
    )

    print(r1)

    # Demonstration 2: New password reset skill
    print("\n=== Run 2: New Password Reset Skill ===")

    r2 = node_graph_run(
        "bob",
        "I forgot my password and need a reset.",
        memory,
        audit_log,
        prompt_log
    )

    print(r2)

    # Demonstration 3: Unknown issue goes to ticket escalation
    print("\n=== Run 3: Unknown Issue ===")

    r3 = node_graph_run(
        "carol",
        "My laptop charger is broken",
        memory,
        audit_log,
        prompt_log
    )

    print(r3)

    # Demonstration 4: Safety control
    print("\n=== Run 4: Empty Input Safety Check ===")

    r4 = node_graph_run(
        "david",
        "   ",
        memory,
        audit_log,
        prompt_log
    )

    print(r4)

    # Evaluation
    print("\n=== Evaluation ===")

    evaluation_results = run_evaluation()

    for result in evaluation_results:
        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"[{status}] {result['issue']} "
            f"-> {result['actual']} "
            f"(expected {result['expected']})"
        )

    assert all(r["passed"] for r in evaluation_results)

    # Prompt log
    print("\n=== Prompt Log ===")

    for entry in prompt_log:
        print(entry)

    # Audit log
    print("\n=== Audit Log ===")

    for entry in audit_log:
        print(entry)

    # Memory
    print("\n=== Long-Term Memory / History ===")

    for entry in memory.history:
        print(entry)

    # Verification
    assert r1["outcome"]["skill"] == "triage_skill"
    assert r2["outcome"]["skill"] == "password_reset_skill"
    assert r3["outcome"]["resolution"] == "escalated"
    assert r4["rejected"] is True

    print("\n=== Assignment Verification ===")
    print("Original triage skill works: PASS")
    print("Password reset skill works: PASS")
    print("Skill routing works correctly: PASS")
    print("Unknown issue escalates to ticket: PASS")
    print("Empty input safety control works: PASS")
    print("Both skills passed evaluation: PASS")
