
"""
Lab 7: Agentic Node Graph -- Assignment 2
Add a retry limit to the Builder Node.

The builder gets exactly one retry.
If both attempts fail, the workflow escalates to a human.
"""


class Node:
    def __init__(self, name, owner, success_fn, on_success, on_fail):
        self.name = name
        self.owner = owner
        self.success_fn = success_fn
        self.on_success = on_success
        self.on_fail = on_fail


def requirement_node(state):
    state["requirements"] = [
        "user login",
        "event listing",
        "RSVP button"
    ]
    return state


def planner_node(state):
    state["tasks"] = {
        req: f"task_for({req})"
        for req in state["requirements"]
    }
    return state


def builder_node(state):
    # Simulate a build failure for testing retry behavior
    if state.get("builder_failures_remaining", 0) > 0:
        state["builder_failures_remaining"] -= 1
        state["build_ok"] = False
        return state

    state["build_ok"] = True
    state["code"] = "app.py generated"
    return state


def tester_node(state):
    state["tests_passed"] = state.get("build_ok", False)
    return state


def reviewer_node(state):
    state["review_clean"] = state.get("tests_passed", False)
    return state


def human_gate_node(state):
    state["human_signoff"] = state.get("review_clean", False)
    return state


GRAPH = [
    Node(
        "requirement",
        "requirement_agent",
        lambda s: len(s.get("requirements", [])) >= 3,
        requirement_node,
        "escalate_to_human('goal too vague to extract 3+ requirements')"
    ),

    Node(
        "planner",
        "planner_agent",
        lambda s: all(
            r in s.get("tasks", {})
            for r in s.get("requirements", [])
        ),
        planner_node,
        "return_to('requirement')"
    ),

    Node(
        "builder",
        "builder_agent",
        lambda s: s.get("build_ok", False),
        builder_node,
        "retry_once_then_escalate_to_human"
    ),

    Node(
        "tester",
        "tester_agent",
        lambda s: s.get("tests_passed", False),
        tester_node,
        "route_back_to('builder')"
    ),

    Node(
        "reviewer",
        "reviewer_agent",
        lambda s: s.get("review_clean", False),
        reviewer_node,
        "route_back_to('builder')"
    ),

    Node(
        "human_gate",
        "human",
        lambda s: s.get("human_signoff", False),
        human_gate_node,
        "return_to('planner', reason=human.notes)"
    )
]


def simulate(builder_failures=0):
    state = {
        "builder_failures_remaining": builder_failures
    }

    trace = []

    for node in GRAPH:

        # Builder gets a maximum of two attempts:
        # one initial attempt and exactly one retry.
        if node.name == "builder":

            builder_succeeded = False

            for attempt in range(1, 3):

                state = node.on_success(state)
                ok = node.success_fn(state)

                trace.append({
                    "node": node.name,
                    "owner": node.owner,
                    "attempt": attempt,
                    "success": ok,
                    "state_after": {
                        k: v for k, v in state.items()
                        if k != "builder_failures_remaining"
                    }
                })

                if ok:
                    builder_succeeded = True
                    break

                if attempt == 1:
                    trace.append({
                        "node": "builder",
                        "action": "Retrying builder (one retry allowed)"
                    })

                else:
                    trace.append({
                        "node": "builder",
                        "failure_behavior_triggered":
                            "escalate_to_human_after_one_retry"
                    })

            if not builder_succeeded:
                break

            continue

        # Normal execution for all other nodes
        state = node.on_success(state)
        ok = node.success_fn(state)

        trace.append({
            "node": node.name,
            "owner": node.owner,
            "success": ok,
            "state_after": {
                k: v for k, v in state.items()
                if k != "builder_failures_remaining"
            }
        })

        if not ok:
            trace.append({
                "node": node.name,
                "failure_behavior_triggered": node.on_fail
            })
            break

    return trace


if __name__ == "__main__":

    print("=== SCENARIO A: Builder Fails Once, Then Succeeds ===")

    for step in simulate(builder_failures=1):
        print(step)

    print("\n=== SCENARIO B: Builder Fails Twice, Escalates ===")

    for step in simulate(builder_failures=2):
        print(step)
