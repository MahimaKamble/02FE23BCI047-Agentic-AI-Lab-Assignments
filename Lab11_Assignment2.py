
"""
Lab 11 Assignment 2: Prove Test Independence With a Deliberate Bug

A deliberate bug is introduced into coding_agent().
testing_agent() remains unchanged and independently checks
the acceptance criteria from the user story.
"""

FEATURE_REQUEST = "Add CSV export to the reports page, preserving applied filters."


def requirement_agent(request):
    stories = [{
        "id": "US-1",
        "text": (
            "As a user, I can export the current report view as a CSV file, "
            "preserving the applied filters."
        ),
        "acceptance_criteria": [
            "clicking Export produces a .csv file",
            "the CSV contains only rows matching the currently applied filters",
            "the CSV header row matches the visible column names",
        ],
    }]
    return stories


def human_confirms_stories(stories):
    print("[HUMAN CHECKPOINT] Reviewing stories for real user intent...")
    for story in stories:
        print(f"  Confirmed: {story['text']}")
    return True


def design_agent(stories):
    return {
        "story_id": stories[0]["id"],
        "components": [
            "export_endpoint",
            "csv_serializer",
            "export_button (UI)",
        ],
    }


def coding_agent(design, stories):
    # Implementation derived from design + story.
    # DELIBERATE BUG: != is used instead of == in the filter condition.
    story = stories[0]

    def export_endpoint(rows, applied_filters, columns):
        filtered = [
            r for r in rows
            if all(r.get(k) != v for k, v in applied_filters.items())
        ]

        lines = [",".join(columns)]

        for row in filtered:
            lines.append(
                ",".join(str(row.get(column, "")) for column in columns)
            )

        return "\n".join(lines)

    return {
        "design_ref": design["components"],
        "export_endpoint": export_endpoint,
    }


def testing_agent(stories):
    """
    Generates tests from the STORY's acceptance criteria ONLY.
    Does not import or inspect the implementation module.
    This function is intentionally unchanged.
    """
    acceptance_criteria = stories[0]["acceptance_criteria"]

    def test_suite(export_fn):
        rows = [
            {"region": "North", "sales": 100},
            {"region": "South", "sales": 200},
            {"region": "North", "sales": 150},
        ]

        columns = ["region", "sales"]

        csv_out = export_fn(
            rows,
            {"region": "North"},
            columns,
        )

        results = []

        results.append(
            ("produces output", len(csv_out) > 0)
        )

        results.append(
            (
                "header matches columns",
                csv_out.splitlines()[0] == "region,sales",
            )
        )

        results.append(
            (
                "only filtered rows present",
                all(
                    "South" not in line
                    for line in csv_out.splitlines()[1:]
                ),
            )
        )

        return results, acceptance_criteria

    return test_suite


def review_agent(design, code, test_results):
    issues = []

    if len(code["design_ref"]) < 2:
        issues.append("design under-specified: fewer than 2 components")

    if not all(passed for _, passed in test_results):
        issues.append("one or more tests failed")

    return {
        "issues": issues,
        "clean": len(issues) == 0,
    }


def human_final_decision(review):
    print("[HUMAN CHECKPOINT] Final accept/reject based on review + tests...")

    decision = "accept" if review["clean"] else "reject"

    print(f"  Decision: {decision}")
    return decision


def docs_agent(stories):
    return (
        f"Usage: click 'Export' on the reports page to download "
        f"the filtered view as CSV. ({stories[0]['id']})"
    )


def release_agent(decision, stories):
    if decision != "accept":
        return {
            "released": False,
            "reason": "review did not pass",
        }

    return {
        "released": True,
        "release_note": f"Added CSV export ({stories[0]['id']}).",
        "rollback_plan": (
            "Revert to previous reports-page build if export errors "
            "spike post-release."
        ),
    }


if __name__ == "__main__":

    # 1. Requirement stage
    stories = requirement_agent(FEATURE_REQUEST)
    human_confirms_stories(stories)

    # 2. Design stage
    design = design_agent(stories)
    print(f"\nDesign: {design}")

    # 3. Code stage
    code = coding_agent(design, stories)

    # 4. Test stage: generated from stories, independently of code
    test_suite = testing_agent(stories)
    test_results, acceptance_criteria = test_suite(
        code["export_endpoint"]
    )

    print("\n=== Test results (derived from acceptance criteria, not implementation) ===")
    print(f"Acceptance criteria tested: {acceptance_criteria}")

    for name, passed in test_results:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")

    # 5. Review stage
    review = review_agent(design, code, test_results)
    print(f"\nReview: {review}")

    # 6. Human decision
    decision = human_final_decision(review)

    # 7. Documentation and release
    docs = docs_agent(stories)
    release = release_agent(decision, stories)

    print(f"\nDocs: {docs}")
    print(f"Release: {release}")

    # 8. Demonstrate the deliberate regression
    failed_tests = [
        name for name, passed in test_results if not passed
    ]

    print("\n=== Regression Verification ===")

    if failed_tests:
        print("Deliberate bug detected by independent tests.")
        print(f"Failed tests: {failed_tests}")
        print("Test independence demonstrated: PASS")
    else:
        print("ERROR: The deliberate bug was not detected.")
        print("Test independence demonstrated: FAIL")

    # 9. Lineage
    print("\n=== Lineage ===")
    print("stories        <- requirement_agent(feature_request)")
    print("design         <- design_agent(stories)")
    print("code           <- coding_agent(design, stories)")
    print("tests          <- testing_agent(stories)   [independent of code]")
    print("review         <- review_agent(design, code, tests)")
    print("release        <- release_agent(human_decision, stories)")

    assert not all(passed for _, passed in test_results)
    assert not review["clean"]
    assert decision == "reject"
    assert release["released"] is False

    print("\nAll verification checks passed.")
