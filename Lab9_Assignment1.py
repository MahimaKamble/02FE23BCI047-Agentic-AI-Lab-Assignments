
"""
Lab 9: Deep Research Agent -- Assignment 1
Add a Directly Contradicting Source

Add S4, which contradicts S1's hallucination-reduction finding.
Update compare() and synthesize() to report a genuine conflict
and explain a plausible reason for the disagreement.
"""

QUESTION = (
    "What are the demonstrated benefits and limitations of "
    "retrieval-augmented generation (RAG) for domain-specific "
    "question answering, as of the last year?"
)

SUCCESS_CRITERIA = (
    "At least 3 independent sources; at least 1 limitation identified; "
    "1 executive summary."
)


# --------------------------------
# 1. Evidence sources
# --------------------------------

SOURCES = [
    {
        "id": "S1",
        "type": "peer-reviewed paper",
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
        )
    },

    {
        "id": "S2",
        "type": "vendor engineering blog",
        "date": "2026-04",
        "claim": (
            "RAG improves answer accuracy by 35% in an internal "
            "support-ticket QA system."
        ),
        "evidence": (
            "Internal A/B test over 10,000 tickets."
        ),
        "limitation": (
            "Funded/internal evaluation; no independent replication reported."
        )
    },

    {
        "id": "S3",
        "type": "independent benchmark report",
        "date": "2026-05",
        "claim": (
            "RAG introduces a measurable latency overhead of "
            "200-400ms per query."
        ),
        "evidence": (
            "Benchmarked across 5 open-source RAG pipelines."
        ),
        "limitation": (
            "Latency depends heavily on retrieval index size; "
            "not tested at scale."
        )
    },

    # NEW FOURTH SOURCE: DIRECT CONTRADICTION
    {
        "id": "S4",
        "type": "independent benchmark report",
        "date": "2026-06",
        "claim": (
            "RAG showed no measurable reduction in hallucination "
            "rate compared with a non-retrieval baseline."
        ),
        "evidence": (
            "A controlled evaluation using 500 general-domain "
            "question-answering samples."
        ),
        "limitation": (
            "The evaluation used a different domain and dataset "
            "from the medical QA study."
        )
    }
]


# --------------------------------
# 2. Build evidence table
# --------------------------------

def build_evidence_table(sources):
    return sources


# --------------------------------
# 3. Compare evidence
# --------------------------------

def compare(sources):

    agreements = []
    conflicts = []
    gaps = []

    # Identify the relevant sources
    s1 = next(s for s in sources if s["id"] == "S1")
    s2 = next(s for s in sources if s["id"] == "S2")
    s3 = next(s for s in sources if s["id"] == "S3")
    s4 = next(s for s in sources if s["id"] == "S4")

    # Agreement between S1 and S2
    agreements.append({
        "sources": ["S1", "S2"],
        "finding": (
            "S1 and S2 agree that RAG improves factual/answer "
            "accuracy over a non-retrieval baseline, in different domains."
        )
    })

    # NEW: Direct contradiction between S1 and S4
    conflicts.append({
        "sources": ["S1", "S4"],
        "finding": (
            "S1 reports a 41% reduction in hallucination rate, "
            "whereas S4 reports no measurable reduction."
        ),
        "reason": (
            "The studies used different evaluation methodologies, "
            "domains, and dataset sizes. S1 used 200 medical-domain "
            "questions, while S4 used 500 general-domain questions. "
            "These differences may explain the disagreement."
        )
    })

    # S3 reports latency, which is not contradicted by S1 or S2.
    # This is a gap in the other sources, not a direct conflict.
    gaps.append({
        "source": "S3",
        "finding": (
            "S3 reports a 200-400ms latency overhead, "
            "which is not discussed by S1 or S2."
        )
    })

    # Existing gap about non-English performance
    gaps.append({
        "source": "All sources",
        "finding": (
            "No source in this set reports on RAG performance "
            "for non-English languages."
        )
    })

    return {
        "agreements": agreements,
        "conflicts": conflicts,
        "gaps": gaps
    }


# --------------------------------
# 4. Synthesize findings
# --------------------------------

def synthesize(evidence_table, comparison):

    lines = []

    # Individual source claims
    for source in evidence_table:
        lines.append(
            f"[{source['id']}] {source['claim']}"
        )

    # Agreements
    for agreement in comparison["agreements"]:
        source_ids = ",".join(agreement["sources"])

        lines.append(
            f"[{source_ids}] {agreement['finding']}"
        )

    # Genuine contradictions
    for conflict in comparison["conflicts"]:
        source_ids = ",".join(conflict["sources"])

        lines.append(
            f"[GENUINE CONFLICT: {source_ids}] "
            f"{conflict['finding']}"
        )

        lines.append(
            f"[EXPLANATION: {source_ids}] "
            f"Plausible reason: {conflict['reason']}"
        )

    # Gaps
    for gap in comparison["gaps"]:
        lines.append(
            f"[GAP: {gap['source']}] {gap['finding']}"
        )

    return lines


# --------------------------------
# 5. Main execution
# --------------------------------

if __name__ == "__main__":

    print("=== Question ===")
    print(QUESTION)

    print(f"\nSuccess criteria: {SUCCESS_CRITERIA}")

    # Build evidence table
    table = build_evidence_table(SOURCES)

    print("\n=== Evidence Table ===")

    for row in table:
        print(row)

    # Compare evidence
    comparison = compare(table)

    print("\n=== Comparison ===")

    print("Agreements:")
    for agreement in comparison["agreements"]:
        print(agreement)

    print("\nGenuine Conflicts:")
    for conflict in comparison["conflicts"]:
        print(conflict)

    print("\nGaps:")
    for gap in comparison["gaps"]:
        print(gap)

    # Synthesize findings
    synthesis = synthesize(table, comparison)

    print("\n=== Executive Summary ===")

    for line in synthesis:
        print(line)

    # Verification
    print("\n=== Verification ===")

    print("Total sources:", len(table))
    print("Fourth source added:", any(s["id"] == "S4" for s in table))
    print("Genuine contradiction detected:",
          len(comparison["conflicts"]) > 0)
    print("Conflict reason provided:",
          bool(comparison["conflicts"][0]["reason"]))
    print("S3 latency correctly classified as a gap:",
          any(g["source"] == "S3" for g in comparison["gaps"]))
