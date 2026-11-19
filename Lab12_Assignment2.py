
"""
Lab 12 Assignment 2: Mandatory Re-Evaluation After N Proposals

The agent must be re-evaluated after every 5 successful proposals.
The 6th proposal is blocked until evaluate() is called again.
"""

REGRESSION_SUITE_RESULT = {"passed": 9, "total": 10}

MAX_PROPOSALS = 5


class ProdChangeAgent:
    permissions = {"can_write": "staging_only"}

    def __init__(self):
        self.audit_log = []
        self.evaluated = False
        self.proposal_count = 0

    def evaluate(self):
        # Evaluation must pass before the agent can propose changes.
        pass_rate = (
            REGRESSION_SUITE_RESULT["passed"]
            / REGRESSION_SUITE_RESULT["total"]
        )

        self.evaluated = pass_rate >= 0.8

        # Reset the proposal counter after re-evaluation.
        if self.evaluated:
            self.proposal_count = 0

        self._log(
            "evaluation",
            {
                "pass_rate": pass_rate,
                "passed_gate": self.evaluated,
                "proposal_count_reset": self.proposal_count,
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
    ):

        # Check whether the agent has been evaluated.
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
                "reason": (
                    "Evaluation gate not passed; cannot propose changes."
                ),
            }

        # New Control: Mandatory re-evaluation after 5 proposals.
        if self.proposal_count >= MAX_PROPOSALS:
            message = (
                "Proposal limit reached (5). "
                "Re-evaluation required before another proposal."
            )

            self._log(
                "propose_change",
                {
                    "rejected": True,
                    "reason": message,
                    "proposal_count": self.proposal_count,
                },
            )

            return {
                "rejected": True,
                "reason": message,
            }

        # Least-privilege permission check.
        if self.permissions["can_write"] != "staging_only":
            raise PermissionError(
                "Agent must not hold direct production write access."
            )

        # Privacy check.
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

        # Rollback check.
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

        # Valid proposal: request human approval.
        request = {
            "diagnosis": diagnosis,
            "proposed_action": action,
            "rollback_plan": rollback_plan,
            "category": "production",
            "requires_approval": True,
        }

        # Increment only after a valid proposal is created.
        self.proposal_count += 1

        request["proposal_number"] = self.proposal_count

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

    agent = ProdChangeAgent()

    print("=== Initial Evaluation ===")
    print(f"Evaluated and passed: {agent.evaluate()}")

    # Make five valid proposals.
    print("\n=== First Five Proposals ===")

    for number in range(1, 6):
        result = agent.propose_change(
            diagnosis=f"Configuration issue detected for proposal {number}.",
            action=f"update configuration {number}",
            rollback_plan=f"Restore configuration {number} to its previous value.",
            privacy_scrubbed=True,
        )

        print(f"Proposal {number}: {result}")
        assert not result.get("rejected", False)

    print(f"\nProposal count: {agent.proposal_count}")

    # Attempt the sixth proposal without re-evaluation.
    print("\n=== Sixth Proposal: Should Be Blocked ===")

    sixth_attempt = agent.propose_change(
        diagnosis="Another configuration issue detected.",
        action="update configuration 6",
        rollback_plan="Restore configuration 6 to its previous value.",
        privacy_scrubbed=True,
    )

    print(sixth_attempt)

    assert sixth_attempt["rejected"] is True
    assert agent.proposal_count == 5

    # Re-evaluate the agent.
    print("\n=== Mandatory Re-Evaluation ===")

    reevaluation = agent.evaluate()

    print(f"Re-evaluated and passed: {reevaluation}")
    print(f"Proposal count after reset: {agent.proposal_count}")

    # Retry the sixth proposal after re-evaluation.
    print("\n=== Sixth Proposal: After Re-Evaluation ===")

    sixth_proposal = agent.propose_change(
        diagnosis="Another configuration issue detected.",
        action="update configuration 6",
        rollback_plan="Restore configuration 6 to its previous value.",
        privacy_scrubbed=True,
    )

    print(sixth_proposal)

    assert not sixth_proposal.get("rejected", False)
    assert agent.proposal_count == 1

    # Verify the approval handoff remains in place.
    print("\n=== Human Approval and Privileged Handoff ===")

    outcome = agent.apply_after_approval(
        sixth_proposal,
        human_decision="approved",
    )

    print(outcome)

    # Final verification.
    print("\n=== Assignment Verification ===")

    print("First five proposals accepted: PASS")
    print(
        "Sixth proposal blocked before re-evaluation: "
        f"{sixth_attempt['rejected']}"
    )
    print(f"Re-evaluation successful: {reevaluation}")
    print(
        "Sixth proposal accepted after re-evaluation: "
        f"{not sixth_proposal.get('rejected', False)}"
    )
    print(
        "Proposal counter reset correctly: "
        f"{agent.proposal_count == 1}"
    )

    assert reevaluation is True
    assert outcome["applied"] is False
    assert outcome["handed_off_to"] == "privileged_deploy_process"

    print("\nAll  verification checks passed.")

    print("\n=== Full Audit Log ===")
    for entry in agent.audit_log:
        print(entry)
