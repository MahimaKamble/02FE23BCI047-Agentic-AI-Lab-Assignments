
"""
Lab 9: Deep Research Agent -- Weight Sources by Quality
Question -> Search -> Extract -> Compare -> Synthesize.

Each source has a quality tier. When sources conflict,
the synthesis leans toward the higher-quality source but
still discloses the lower-quality source's claim.
"""

QUESTION = (
    "What are the demonstrated benefits and limitations of retrieval-augmented "
    "generation (RAG) for domain-specific question answering, as of the last year?"
)

SUCCESS_CRITERIA = (
    "At least 3 independent sources; at least 1 limitation identified; "
    "1 executive summary."
)

# Higher quality rank means stronger evidence for this exercise.
QUALITY_RANK = {
    "peer-reviewed": 3,
    "independent benchmark": 2,
    "vendor blog": 1,
}

SOURCES = [
    {
        "id": "S1",
        "type": "peer-reviewed paper",
        "quality": "peer-reviewed",
        "date": "2026-02",
        "claim": (
            "RAG reduces hallucination rate by 41% on domain QA "
            "vs a non-retrieval baseline."
        ),
        "evidence": (
            "200 held-out questions from a medical knowledge base."
        ),
        "limitation": (
            "Small, single-domain evaluation set; may not generalize."
        ),
    },
    {
        "id": "S2",
        "type": "vendor engineering blog",
        "quality": "vendor blog",
        "date": "2026-04",
        "claim": (
            "RAG improves answer accuracy by 35% in an internal "
            "support-ticket QA system."
        ),
        "evidence": "Internal A/B test over 10,000 tickets.",
        "limitation": (
            "Funded/internal evaluation; no independent replication reported."
        ),
    },
    {
        "id": "S3",
        "type": "independent benchmark report",
        "quality": "independent benchmark",
        "date": "2026-05",
        "claim": (
            "RAG introduces a measurable latency overhead of "
            "200-400ms per query."
        ),
        "evidence": "Benchmarked across 5 open-source RAG pipelines.",
        "limitation": (
            "Latency depends heavily on retrieval index size; not tested at scale."
        ),
    },
    {
        "id": "S4",
        "type": "independent benchmark report",
        "quality": "independent benchmark",
        "date": "2026-06",
        "claim": (
            "RAG showed no measurable reduction in hallucination rate "
            "compared with a non-retrieval baseline."
        ),
        "evidence": (
            "Controlled evaluation using 500 general-domain QA samples."
        ),
        "limitation": (
            "Different domain and dataset from the medical QA evaluation."
        ),
    },
]


def build_evidence_table(sources):
    return sources


def compare(sources):
    agreements = []
    conflicts = []
    gaps = []

    # S1 and S2 both report accuracy-related improvements.
    if any(s["id"] == "S1" for s in sources) and any(
        s["id"] == "S2" for s in sources
    ):
        agreements.append(
            "S1 and S2 agree that RAG improves factual/answer accuracy "
            "over a non-retrieval baseline, in different domains."
        )

    # S1 and S4 make directly contradictory claims about hallucination reduction.
    s1 = next((s for s in sources if s["id"] == "S1"), None)
    s4 = next((s for s in sources if s["id"] == "S4"), None)

    if s1 and s4:
        conflicts.append({
            "source_1": "S1",
            "source_2": "S4",
            "description": (
                "S1 reports a 41% reduction in hallucination, while "
                "S4 reports no measurable reduction."
            ),
            "possible_reason": (
                "The evaluations used different domains, methodologies, "
                "and dataset sizes: S1 used 200 medical QA questions, "
                "whereas S4 used 500 general-domain QA samples."
            ),
        })

    if any("latency" in s["claim"].lower() for s in sources):
        gaps.append(
            "The accuracy-focused sources do not measure latency; "
            "latency is an additional performance consideration."
        )

    gaps.append(
        "No source in this set reports on RAG performance for non-English languages."
    )

    return {
        "agreements": agreements,
        "conflicts": conflicts,
        "gaps": gaps,
    }


def synthesize(evidence_table, comparison):
    summary = []

    # Keep each source's claim traceable to its evidence-table ID.
    for source in evidence_table:
        summary.append(
            f"[{source['id']}] {source['claim']} "
            f"(Quality: {source['quality']}; "
            f"Evidence: {source['evidence']}; "
            f"Limitation: {source['limitation']})"
        )

    for agreement in comparison["agreements"]:
        summary.append(f"[S1,S2] {agreement}")

    # Resolve each conflict using the declared quality ranking.
    for conflict in comparison["conflicts"]:
        source_a = next(
            s for s in evidence_table if s["id"] == conflict["source_1"]
        )
        source_b = next(
            s for s in evidence_table if s["id"] == conflict["source_2"]
        )

        rank_a = QUALITY_RANK[source_a["quality"]]
        rank_b = QUALITY_RANK[source_b["quality"]]

        if rank_a >= rank_b:
            preferred = source_a
            down_weighted = source_b
        else:
            preferred = source_b
            down_weighted = source_a

        summary.append(
            f"[{preferred['id']}] Quality-weighted conclusion: "
            f"The synthesis leans toward this claim because "
            f"'{preferred['quality']}' ranks higher than "
            f"'{down_weighted['quality']}' in the defined quality hierarchy."
        )

        summary.append(
            f"[{down_weighted['id']}] The conflicting claim was "
            f"down-weighted, not discarded: {down_weighted['claim']}"
        )

        summary.append(
            f"[{source_a['id']},{source_b['id']}] "
            f"Possible reason for disagreement: {conflict['possible_reason']}"
        )

    for gap in comparison["gaps"]:
        summary.append(f"[gap] {gap}")

    return summary


if __name__ == "__main__":
    evidence_table = build_evidence_table(SOURCES)
    comparison = compare(evidence_table)
    executive_summary = synthesize(evidence_table, comparison)

    print("=== Research Question ===")
    print(QUESTION)

    print("\n=== Success Criteria ===")
    print(SUCCESS_CRITERIA)

    print("\n=== Source Quality Hierarchy ===")
    for tier, rank in sorted(
        QUALITY_RANK.items(), key=lambda item: item[1], reverse=True
    ):
        print(f"{rank}. {tier}")

    print("\n=== Evidence Table ===")
    for source in evidence_table:
        print(source)

    print("\n=== Comparison ===")
    print(comparison)

    print("\n=== Executive Summary ===")
    for line in executive_summary:
        print(line)

    print("\n=== Quality Weighting Verification ===")
    s1 = next(s for s in evidence_table if s["id"] == "S1")
    s4 = next(s for s in evidence_table if s["id"] == "S4")

    print(
        "S1 has higher quality than S4:",
        QUALITY_RANK[s1["quality"]] > QUALITY_RANK[s4["quality"]]
    )
    print(
        "S4 is still included in the evidence table:",
        any(s["id"] == "S4" for s in evidence_table)
    )
    print(
        "Lower-tier claim explicitly disclosed:",
        any("down-weighted, not discarded" in line
            for line in executive_summary)
    )
