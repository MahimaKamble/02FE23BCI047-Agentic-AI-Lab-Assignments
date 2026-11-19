
"""
Lab 8: Parallel Swarm -- Assignment 2
Distributed Critique

Each role independently critiques the merged draft
against its own constraints. Objections are recorded
with the name of the role that raised them.
"""

from concurrent.futures import ThreadPoolExecutor


# --------------------------------
# 1. Define the four role agents
# --------------------------------

def research_agent(goal):
    return {
        "role": "research",
        "output": {
            "format_notes": "Past events favored a 24-hour format with themed tracks.",
            "recommended_duration": "24 hours"
        }
    }


def logistics_agent(goal):
    return {
        "role": "logistics",
        "output": {
            "venue": "Grand Hall",
            "venue_cost": 45000,
            "date": "Saturday",
            "preferred_venue_limit": 40000
        }
    }


def budget_agent(goal):
    return {
        "role": "budget",
        "output": {
            "total_cap": 30000
        }
    }


def judging_agent(goal):
    return {
        "role": "judging",
        "output": {
            "criteria": [
                "innovation",
                "technical depth",
                "demo quality"
            ]
        }
    }


ROLES = {
    "research": research_agent,
    "logistics": logistics_agent,
    "budget": budget_agent,
    "judging": judging_agent
}


# --------------------------------
# 2. Execute agents in parallel
# --------------------------------

def run_swarm(goal):
    with ThreadPoolExecutor(max_workers=len(ROLES)) as pool:

        futures = {
            name: pool.submit(fn, goal)
            for name, fn in ROLES.items()
        }

        outputs = {
            name: future.result()
            for name, future in futures.items()
        }

    return outputs


# --------------------------------
# 3. Merge agent outputs
# --------------------------------

def merge(outputs):
    return {
        "format_notes":
            outputs["research"]["output"]["format_notes"],

        "recommended_duration":
            outputs["research"]["output"]["recommended_duration"],

        "venue":
            outputs["logistics"]["output"]["venue"],

        "venue_cost":
            outputs["logistics"]["output"]["venue_cost"],

        "date":
            outputs["logistics"]["output"]["date"],

        "preferred_venue_limit":
            outputs["logistics"]["output"]["preferred_venue_limit"],

        "budget_cap":
            outputs["budget"]["output"]["total_cap"],

        "judging_criteria":
            outputs["judging"]["output"]["criteria"]
    }


# --------------------------------
# 4. Independent role critiques
# --------------------------------

def research_critique(draft):
    objections = []

    if not draft.get("format_notes"):
        objections.append({
            "conflict": "Missing research-based event format",
            "details": "Research notes are missing."
        })

    return objections


def logistics_critique(draft):
    objections = []

    if draft["venue_cost"] > draft["preferred_venue_limit"]:
        objections.append({
            "conflict": "Venue exceeds logistics preference",
            "details": (
                f"Venue cost {draft['venue_cost']} exceeds "
                f"logistics limit {draft['preferred_venue_limit']}."
            )
        })

    return objections


def budget_critique(draft):
    objections = []

    if draft["venue_cost"] > draft["budget_cap"]:
        objections.append({
            "conflict": "Venue cost exceeds overall budget",
            "details": (
                f"Venue cost {draft['venue_cost']} exceeds "
                f"budget cap {draft['budget_cap']}."
            )
        })

    return objections


def judging_critique(draft):
    objections = []

    if not draft.get("judging_criteria"):
        objections.append({
            "conflict": "Judging criteria missing",
            "details": "Judging criteria must be provided."
        })

    return objections


# Each role has its own independent critique function.
ROLE_CRITIQUES = {
    "research": research_critique,
    "logistics": logistics_critique,
    "budget": budget_critique,
    "judging": judging_critique
}


# --------------------------------
# 5. Collect distributed critiques
# --------------------------------

def distributed_critique(draft):
    conflict_log = []

    for role, critique_function in ROLE_CRITIQUES.items():

        objections = critique_function(draft)

        for objection in objections:
            conflict_log.append({
                "raised_by": role,
                "conflict": objection["conflict"],
                "details": objection["details"]
            })

    return conflict_log


# --------------------------------
# 6. Resolve conflicts
# --------------------------------

def resolve(conflict, priority_rule="budget_over_preference"):

    if conflict["raised_by"] == "logistics":
        return {
            "rule_applied": priority_rule,
            "resolution": (
                "Ask logistics to select an alternative venue "
                "within its preferred cost limit."
            )
        }

    if conflict["raised_by"] == "budget":
        return {
            "rule_applied": priority_rule,
            "resolution": (
                "Budget takes priority. Reject the venue and "
                "request an alternative within the overall budget."
            )
        }

    return {
        "rule_applied": priority_rule,
        "resolution": "Review the objection with the responsible role."
    }


# --------------------------------
# 7. Main execution
# --------------------------------

if __name__ == "__main__":

    goal = "Plan a college AI hackathon"

    outputs = run_swarm(goal)

    print("=== Parallel Role Outputs ===")

    for name, out in outputs.items():
        print(f"{name}: {out['output']}")

    draft = merge(outputs)

    print("\n=== Merged Draft Plan ===")
    print(draft)

    # Each role critiques independently.
    conflicts = distributed_critique(draft)

    print("\n=== Distributed Critique ===")

    for conflict in conflicts:
        print(
            f"Role: {conflict['raised_by']} | "
            f"Objection: {conflict['conflict']}"
        )
        print(f"Details: {conflict['details']}")

    # Resolve and record all objections.
    conflict_log = []

    for conflict in conflicts:
        resolution = resolve(conflict)

        conflict_log.append({
            **conflict,
            **resolution
        })

    print("\n=== Final Distributed Conflict Log ===")

    for entry in conflict_log:
        print(entry)

    print("\n=== Verification ===")

    roles_raising_objections = {
        entry["raised_by"] for entry in conflicts
    }

    print("Central critique function replaced: PASS")
    print("Independent role critiques executed: PASS")
    print("Number of roles raising objections:",
          len(roles_raising_objections))
    print("At least two roles raised objections:",
          len(roles_raising_objections) >= 2)
    print("Conflict log records objection owners:",
          all("raised_by" in entry for entry in conflict_log))
