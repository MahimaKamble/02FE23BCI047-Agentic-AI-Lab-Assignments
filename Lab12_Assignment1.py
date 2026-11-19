
"""
Lab 12 Assignment 1: A Cost-Category Control

Adds a cost estimate and budget threshold to ProdChangeAgent.
Proposals exceeding the budget require finance approval.
Missing cost estimates are rejected.
"""

REGRESSION_SUITE_RESULT = {"passed": 9, "total": 10}


class ProdChangeAgent:
    permissions = {"can_write": "staging_only"}

    def __init__(self, budget_threshold=50000):
        self.audit_log = []
        self.evaluated = False
        self.budget_threshold = budget_threshold

    def evaluate(self):
        pass_rate = (
            REGRESSION_SUITE_RESULT["passed"]
            / REGRESSION_SUITE_RESULT["total"]
        )

        self.evaluated = pass_rate >= 0.8

        self._log(
            "evaluation",
            {
                "pass_rate": pass_rate,
                "passed_gate": self.evaluated,
            },
        )

        return self.evaluated

    def _log(self, step, data):
        self.audit_log.append({
            "step": step,
            "data": data,
        })

    def propose_change(
        self,
        diagnosis,
        action,
        rollback_plan,
        privacy_scrubbed,
        estimated_cost=None,
        finance_approved=False,
    ):

        # Evaluation gate
        if not self.evaluated:
            self._log(
                "propose_change",
                {
                    "rejected": True,
                    "reason": "agent not evaluated",
                },
            )

            return {
                "rejected": True,
                "reason": "Evaluation gate not passed; cannot propose changes.",
            }

        # Least-privilege permission check
        if self.permissions["can_write"] != "staging_only":
            raise PermissionError(
                "Agent must not hold direct production write access."
            )

        # Privacy check
        if not privacy_scrubbed:
            self._log(
                "propose_change",
                {
                    "rejected": True,
                    "reason": "unscrubbed customer data in input",
                },
            )

            return {
                "rejected": True,
                "reason": (
                    "Diagnostic input was not privacy-scrubbed; rejecting."
                ),
            }

        # Rollback check
        if not rollback_plan:
            self._log(
                "propose_change",
                {
                    "rejected": True,
                    "reason": "no rollback plan supplied",
                },
            )

            return {
                "rejected": True,
                "reason": "No rollback plan defined; rejecting proposal.",
            }

        # New Control 1: Reject missing cost estimates
        if estimated_cost is None:
            self._log(
                "propose_change",
                {
                    "rejected": True,
                    "reason": "missing cost estimate",
                },
            )

            return {
                "rejected": True,
                "reason": (
                    "Cost estimate is missing; rejecting proposal."
                ),
            }

        # Validate the cost estimate
        if (
            isinstance(estimated_cost, bool)
            or not isinstance(estimated_cost, (int, float))
            or estimated_cost < 0
        ):
            self._log(
                "propose_change",
                {
                    "rejected": True,
                    "reason": "invalid cost estimate",
                },
            )

            return {
                "rejected": True,
                "reason": "Invalid cost estimate; rejecting proposal.",
            }

        # New Control 2: Budget threshold check
        if (
            estimated_cost > self.budget_threshold
            and not finance_approved
        ):
            self._log(
                "propose_change",
                {
                    "rejected": True,
                    "reason": "budget exceeded without finance approval",
                    "estimated_cost": estimated_cost,
                    "budget_threshold": self.budget_threshold,
                },
            )

            return {
                "rejected": True,
                "reason": (
                    "Estimated cost exceeds budget threshold; "
                    "finance approval required."
                ),
                "estimated_cost": estimated_cost,
                "budget_threshold": self.budget_threshold,
            }

        # Human approval is still required for production changes.
        request = {
            "diagnosis": diagnosis,
            "proposed_action": action,
            "rollback_plan": rollback_plan,
            "category": "production",
            "estimated_cost": estimated_cost,
            "budget_threshold": self.budget_threshold,
            "finance_approved": finance_approved,
            "requires_approval": True,
        }

        self._log("approval_requested", request)

        return request

    def apply_after_approval(self, request, human_decision):
        if request.get("rejected"):
            return {
                "applied": False,
                "reason": "Rejected proposal cannot be applied.",
            }

        if human_decision != "approved":
            self._log(
                "human_decision",
                {"decision": human_decision},
            )

            return {
                "applied": False,
                "reason": "Human approval not granted.",
            }

        self._log(
            "human_decision",
            {"decision": "approved"},
        )

        return {
            "applied": False,
            "handed_off_to": "privileged_deploy_process",
            "note": (
                "This agent never holds production write access; "
                "a separate privileged process performs the actual apply step."
            ),
        }


if __name__ == "__main__":

    agent = ProdChangeAgent(budget_threshold=50000)

    print("=== Control 2: Evaluation gate ===")
    print(f"Evaluated and passed: {agent.evaluate()}")

    print("\n=== Attempt 1: Missing cost estimate ===")

    result = agent.propose_change(
        diagnosis="Config X causes memory leak under load.",
        action="revert config X to previous value",
        rollback_plan="Revert config X to v3 if v4 also leaks.",
        privacy_scrubbed=True,
        # estimated_cost deliberately omitted
    )

    print(result)

    print("\n=== Attempt 2: Cost exceeds budget ===")

    result = agent.propose_change(
        diagnosis="Config X causes memory leak under load.",
        action="revert config X to previous value",
        rollback_plan="Revert config X to v3 if v4 also leaks.",
        privacy_scrubbed=True,
        estimated_cost=75000,
        finance_approved=False,
    )

    print(result)

    print("\n=== Attempt 3: Cost exceeds budget but finance approved ===")

    request = agent.propose_change(
        diagnosis="Config X causes memory leak under load.",
        action="revert config X to previous value",
        rollback_plan="Revert config X to v3 if v4 also leaks.",
        privacy_scrubbed=True,
        estimated_cost=75000,
        finance_approved=True,
    )

    print(request)

    print("\n=== Attempt 4: Cost within budget ===")

    request_within_budget = agent.propose_change(
        diagnosis="Config Y requires a controlled update.",
        action="update config Y",
        rollback_plan="Restore config Y to its previous value.",
        privacy_scrubbed=True,
        estimated_cost=30000,
        finance_approved=False,
    )

    print(request_within_budget)

    print("\n=== Human approval and privileged handoff ===")

    outcome = agent.apply_after_approval(
        request_within_budget,
        human_decision="approved",
    )

    print(outcome)

    # Verification
    print("\n=== Adversarial Verification ===")

    missing_cost_rejected = (
        result is not None
    )

    # Re-run the missing-cost attack and verify explicitly.
    attack = agent.propose_change(
        diagnosis="Attempt to bypass budget control.",
        action="reconfigure production",
        rollback_plan="Restore previous configuration.",
        privacy_scrubbed=True,
    )

    print(f"Missing cost estimate rejected: {attack['rejected']}")
    print(f"Rejection reason: {attack['reason']}")

    over_budget_attack = agent.propose_change(
        diagnosis="Expensive production change.",
        action="reconfigure production",
        rollback_plan="Restore previous configuration.",
        privacy_scrubbed=True,
        estimated_cost=75000,
        finance_approved=False,
    )

    print(
        "Over-budget proposal without finance approval rejected: "
        f"{over_budget_attack['rejected']}"
    )

    approved_over_budget = agent.propose_change(
        diagnosis="Approved expensive production change.",
        action="reconfigure production",
        rollback_plan="Restore previous configuration.",
        privacy_scrubbed=True,
        estimated_cost=75000,
        finance_approved=True,
    )

    print(
        "Over-budget proposal with finance approval accepted for "
        f"human review: {not approved_over_budget.get('rejected', False)}"
    )

    assert attack["rejected"] is True
    assert over_budget_attack["rejected"] is True
    assert not approved_over_budget.get("rejected", False)
    assert not request_within_budget.get("rejected", False)

    print("\nAll Assignment 1 verification checks passed.")

    print("\n=== Full Audit Log ===")
    for entry in agent.audit_log:
        print(entry)
