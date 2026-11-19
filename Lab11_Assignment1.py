"""
Lab 11 Assignment 1: A Second, Concurrent Story

Processes CSV export and PDF export through the same SDLC pipeline.
Design, code, and tests are tracked separately for each story.
Tests are generated from acceptance criteria, independently of code.
"""

FEATURE_REQUEST = (
    "Add CSV export to the reports page, preserving applied filters."
)


def requirement_agent(request):
    stories = [
        {
            "id": "US-1",
            "text": (
                "As a user, I can export the current report view as a CSV "
                "file, preserving the applied filters."
            ),
            "acceptance_criteria": [
                "clicking Export produces a .csv file",
                "the CSV contains only rows matching the currently applied filters",
                "the CSV header row matches the visible column names",
            ],
        },
        {
            "id": "US-2",
            "text": (
                "As a user, I can export the current report view as a PDF "
                "file, preserving the applied filters."
            ),
            "acceptance_criteria": [
                "clicking Export as PDF produces a .pdf file",
                "the PDF contains only rows matching the currently applied filters",
                "the PDF includes the visible column names",
            ],
        },
    ]
    return stories


def human_confirms_stories(stories):
    # Simulated human review.
    print("[HUMAN CHECKPOINT] Reviewing stories for real user intent...")
    for story in stories:
        print(f"  Confirmed: {story['id']} - {story['text']}")
    return True


def design_agent(stories):
    designs = {}

    for story in stories:
        if story["id"] == "US-1":
            components = [
                "csv_export_endpoint",
                "csv_serializer",
                "export_button (UI)",
            ]
        elif story["id"] == "US-2":
            components = [
                "pdf_export_endpoint",
                "pdf_generator",
                "export_as_pdf_button (UI)",
            ]
        else:
            components = ["generic_export_endpoint"]

        designs[story["id"]] = {
            "story_id": story["id"],
            "components": components,
        }

    return designs


def coding_agent(designs, stories):
    # Implementation is based on design + stories only.
    # It does not receive or inspect the test suites.
    code_artifacts = {}

    for story in stories:
        story_id = story["id"]
        design = designs[story_id]

        if story_id == "US-1":

            def export_endpoint(rows, applied_filters, columns):
                filtered = [
                    row for row in rows
                    if all(
                        row.get(key) == value
                        for key, value in applied_filters.items()
                    )
                ]

                lines = [",".join(columns)]

                for row in filtered:
                    lines.append(
                        ",".join(str(row.get(column, "")) for column in columns)
                    )

                return {
                    "filename": "report.csv",
                    "content": "\n".join(lines),
                }

        elif story_id == "US-2":

            def export_endpoint(rows, applied_filters, columns):
                filtered = [
                    row for row in rows
                    if all(
                        row.get(key) == value
                        for key, value in applied_filters.items()
                    )
                ]

                lines = [
                    "%PDF-1.4",
                    "Report Export",
                    " | ".join(columns),
                ]

                for row in filtered:
                    lines.append(
                        " | ".join(
                            str(row.get(column, "")) for column in columns
                        )
                    )

                # Simulated PDF payload for this offline lab exercise.
                return {
                    "filename": "report.pdf",
                    "content": "\n".join(lines),
                }

        else:
            continue

        code_artifacts[story_id] = {
            "story_id": story_id,
            "design_ref": design["components"],
            "export_endpoint": export_endpoint,
        }

    return code_artifacts


def testing_agent(stories):
    """
    Generates a separate test suite for each story.

    This function receives only stories and their acceptance criteria.
    It does not receive or inspect the implementation.
    """
    test_suites = {}

    for story in stories:
        story_id = story["id"]
        acceptance_criteria = story["acceptance_criteria"]

        def test_suite(export_fn, story_id=story_id,
                       acceptance_criteria=acceptance_criteria):

            rows = [
                {"region": "North", "sales": 100},
                {"region": "South", "sales": 200},
                {"region": "North", "sales": 150},
            ]

            columns = ["region", "sales"]
            output = export_fn(
                rows,
                {"region": "North"},
                columns,
            )

            filename = output["filename"]
            content = output["content"]

            results = []

            if story_id == "US-1":
                results.append(
                    ("produces .csv file", filename.endswith(".csv"))
                )
                results.append(
                    (
                        "header matches columns",
                        content.splitlines()[0] == "region,sales",
                    )
                )
                data_lines = content.splitlines()[1:]

            elif story_id == "US-2":
                results.append(
                    ("produces .pdf file", filename.endswith(".pdf"))
                )
                results.append(
                    (
                        "PDF includes visible columns",
                        "region | sales" in content,
                    )
                )
                data_lines = content.splitlines()[3:]

            else:
                results.append(("produces output", bool(content)))
                data_lines = content.splitlines()

            results.append(
                (
                    "only filtered rows present",
                    all("South" not in line for line in data_lines),
                )
            )

            return results, acceptance_criteria

        test_suites[story_id] = test_suite

    return test_suites


def review_agent(designs, code_artifacts, test_results):
    reviews = {}

    for story_id in code_artifacts:
        issues = []

        if len(code_artifacts[story_id]["design_ref"]) < 2:
            issues.append("design under-specified: fewer than 2 components")

        if not all(
            passed for _, passed in test_results[story_id]
        ):
            issues.append("one or more tests failed")

        reviews[story_id] = {
            "story_id": story_id,
            "issues": issues,
            "clean": len(issues) == 0,
        }

    return reviews


def human_final_decision(reviews):
    print("\n[HUMAN CHECKPOINT] Final accept/reject based on review + tests...")

    decision = (
        "accept"
        if all(review["clean"] for review in reviews.values())
        else "reject"
    )

    print(f"  Decision: {decision}")
    return decision


def docs_agent(stories):
    documentation = {}

    for story in stories:
        if story["id"] == "US-1":
            usage = (
                "Click 'Export' on the reports page to download "
                "the filtered view as CSV."
            )
        else:
            usage = (
                "Click 'Export as PDF' on the reports page to download "
                "the filtered view as PDF."
            )

        documentation[story["id"]] = (
            f"Usage: {usage} ({story['id']})"
        )

    return documentation


def release_agent(decision, stories):
    releases = {}

    for story in stories:
        story_id = story["id"]

        if decision != "accept":
            releases[story_id] = {
                "released": False,
                "reason": "review did not pass",
            }
        else:
            feature_name = (
                "CSV export" if story_id == "US-1" else "PDF export"
            )

            releases[story_id] = {
                "released": True,
                "release_note": f"Added {feature_name} ({story_id}).",
                "rollback_plan": (
                    "Revert to previous reports-page build if "
                    "export errors spike post-release."
                ),
            }

    return releases


if __name__ == "__main__":
    # 1. Requirements
    stories = requirement_agent(FEATURE_REQUEST)
    human_confirms_stories(stories)

    # 2. Design: one design per story
    designs = design_agent(stories)

    print("\n=== Designs ===")
    for story_id, design in designs.items():
        print(f"{story_id}: {design}")

    # 3. Coding: one implementation per story
    code_artifacts = coding_agent(designs, stories)

    # 4. Testing: generated independently from stories
    test_suites = testing_agent(stories)

    test_results = {}
    acceptance_criteria = {}

    print("\n=== Independent Test Results ===")

    for story in stories:
        story_id = story["id"]

        results, criteria = test_suites[story_id](
            code_artifacts[story_id]["export_endpoint"]
        )

        test_results[story_id] = results
        acceptance_criteria[story_id] = criteria

        print(f"\n{story_id} - Acceptance criteria tested:")
        print(criteria)

        for name, passed in results:
            print(f"  [{'PASS' if passed else 'FAIL'}] {name}")

    # 5. Review: one review per story
    reviews = review_agent(designs, code_artifacts, test_results)

    print("\n=== Reviews ===")
    for story_id, review in reviews.items():
        print(f"{story_id}: {review}")

    # 6. Human decision
    decision = human_final_decision(reviews)

    # 7. Documentation and release
    documentation = docs_agent(stories)
    releases = release_agent(decision, stories)

    print("\n=== Documentation ===")
    for story_id, docs in documentation.items():
        print(f"{story_id}: {docs}")

    print("\n=== Release Results ===")
    for story_id, release in releases.items():
        print(f"{story_id}: {release}")

    # 8. Story-specific lineage
    print("\n=== Lineage ===")

    for story in stories:
        story_id = story["id"]

        print(f"\n{story_id}:")
        print(f"  story  <- requirement_agent(feature_request)")
        print(f"  design <- design_agent(stories)[{story_id}]")
        print(f"  code   <- coding_agent(design, stories)[{story_id}]")
        print(
            f"  tests  <- testing_agent(stories)[{story_id}] "
            "[independent of code]"
        )
        print(
            f"  review <- review_agent(design, code, tests)[{story_id}]"
        )
        print(f"  docs   <- docs_agent(stories)[{story_id}]")
        print(
            f"  release <- release_agent(human_decision, stories)[{story_id}]"
        )

    # 9. Verification
    assert len(stories) == 2
    assert set(designs.keys()) == {"US-1", "US-2"}
    assert set(code_artifacts.keys()) == {"US-1", "US-2"}
    assert set(test_suites.keys()) == {"US-1", "US-2"}
    assert all(
        passed
        for results in test_results.values()
        for _, passed in results
    )
    assert all(review["clean"] for review in reviews.values())
    assert all(release["released"] for release in releases.values())

    print("\nAll Assignment 1 checks passed.")