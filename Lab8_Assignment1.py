
"""
Lab 8: Parallel Swarm -- Hackathon Planner
Assignment 1: Add a Fifth Role - Marketing

Five independent agents run in parallel.
Their outputs are merged, checked for conflicts,
and resolved using the budget_over_preference rule.
"""

from concurrent.futures import ThreadPoolExecutor


# -----------------------------
# 1. Define the five role agents
# -----------------------------

def research_agent(goal):
    return {
        "role": "research",
        "output": "Past events favored a 24-hour format with themed tracks."
    }


def logistics_agent(goal):
    return {
        "role": "logistics",
        "output": {
            "venue": "Grand Hall",
            "venue_cost": 45000,
            "date": "Saturday"
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
        "output": "Judge on innovation, technical depth, and demo quality."
    }


# NEW FIFTH ROLE: MARKETING
def marketing_agent(goal):
    return {
        "role": "marketing",
        "output": {
            "publicity_plan": "Social media campaigns, posters and email promotions",
            "marketing_cost": 35000
        }
    }


# -----------------------------
# 2. Register all five agents
# -----------------------------

ROLES = {
    "research": research_agent,
    "logistics": logistics_agent,
    "budget": budget_agent,
    "judging": judging_agent,
    "marketing": marketing_agent
}


# -----------------------------
# 3. Run agents in parallel
# -----------------------------

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


# -----------------------------
# 4. Merge all agent outputs
# -----------------------------

def merge(outputs):
    return {
        "format_notes": outputs["research"]["output"],

        "venue": outputs["logistics"]["output"]["venue"],
        "venue_cost": outputs["logistics"]["output"]["venue_cost"],
        "date": outputs["logistics"]["output"]["date"],

        "budget_cap": outputs["budget"]["output"]["total_cap"],

        "judging_criteria": outputs["judging"]["output"],

        # New marketing information
        "publicity_plan": outputs["marketing"]["output"]["publicity_plan"],
        "marketing_cost": outputs["marketing"]["output"]["marketing_cost"]
    }


# -----------------------------
# 5. Critique merged plan
# -----------------------------

def critique(draft):
    conflicts = []

    # Existing conflict: venue cost exceeds budget
    if draft["venue_cost"] > draft["budget_cap"]:
        conflicts.append({
            "conflict": "venue_cost exceeds budget_cap",
            "roles_involved": ["logistics", "budget"],
            "logistics_value": draft["venue_cost"],
            "budget_value": draft["budget_cap"]
        })

    # NEW conflict: marketing cost exceeds budget
    if draft["marketing_cost"] > draft["budget_cap"]:
        conflicts.append({
            "conflict": "marketing_cost exceeds budget_cap",
            "roles_involved": ["marketing", "budget"],
            "marketing_value": draft["marketing_cost"],
            "budget_value": draft["budget_cap"]
        })

    return conflicts


# -----------------------------
# 6. Resolve identified conflicts
# -----------------------------

def resolve(conflict, priority_rule="budget_over_preference"):

    if conflict["conflict"] == "venue_cost exceeds budget_cap":
        return {
            "rule_applied": priority_rule,
            "resolution": (
                f"Reject venue at {conflict['logistics_value']}; "
                f"request logistics to propose an alternative under "
                f"{conflict['budget_value']}."
            )
        }

    elif conflict["conflict"] == "marketing_cost exceeds budget_cap":
        return {
            "rule_applied": priority_rule,
            "resolution": (
                f"Reject marketing plan costing "
                f"{conflict['marketing_value']}; "
                f"request marketing to propose a cheaper publicity plan "
                f"under {conflict['budget_value']}."
            )
        }

    return {
        "rule_applied": priority_rule,
        "resolution": "No matching conflict-resolution rule."
    }


# -----------------------------
# 7. Main execution
# -----------------------------

if __name__ == "__main__":

    goal = "Plan a college AI hackathon"

    # Run all five agents
    outputs = run_swarm(goal)

    print("=== Parallel Role Outputs ===")

    for name, out in outputs.items():
        print(f"  {name}: {out['output']}")

    # Merge agent outputs
    draft = merge(outputs)

    print("\n=== Merged Draft Plan ===")
    print(draft)

    # Identify conflicts
    conflicts = critique(draft)

    print("\n=== Critique: Conflicts Found ===")

    conflict_log = []

    for conflict in conflicts:

        resolution = resolve(conflict)

        log_entry = {
            **conflict,
            **resolution
        }

        conflict_log.append(log_entry)

        print(f"  Conflict: {conflict}")
        print(f"  Resolution: {resolution}")

    if not conflicts:
        print("  No conflicts found.")

    # Final conflict log
    print("\n=== Final Conflict Log ===")

    for entry in conflict_log:
        print(entry)

    print("\n=== Verification ===")
    print("Marketing role registered:", "marketing" in ROLES)
    print("Marketing output merged:", "marketing_cost" in draft)
    print("Marketing budget conflict detected:",
          any(c["conflict"] == "marketing_cost exceeds budget_cap"
              for c in conflicts))
    print("All conflicts resolved:",
          len(conflict_log) == len(conflicts))
