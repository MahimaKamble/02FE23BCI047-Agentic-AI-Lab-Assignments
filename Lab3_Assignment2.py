
"""
Lab 3 - Assignment 2: Test Against a Low-Evidence Input

Tests whether the research-summary skill avoids inventing
evidence or limitations when the article does not provide them.
"""

# Original article A
ARTICLE_A = {
    "title": "Retrieval-Augmented Generation Reduces Hallucination in Domain QA",
    "text": (
        "A recent benchmark study found that retrieval-augmented generation (RAG) "
        "reduced factual hallucination rates by 41% compared to a non-retrieval "
        "baseline on a domain-specific question-answering task. The evaluation used "
        "200 held-out questions from a medical knowledge base. The authors note the "
        "evaluation set was small and drawn from a single domain, so results may not "
        "generalize to other domains without further testing."
    ),
}

# Original article B
ARTICLE_B = {
    "title": "Campus Wi-Fi Upgrade Improves Peak-Hour Throughput",
    "text": (
        "Following a campus-wide Wi-Fi access point upgrade, average peak-hour "
        "throughput in the library increased by 60%. The measurement was taken "
        "over two weeks post-upgrade using the network monitoring dashboard. "
        "The report does not include measurements from other buildings on campus, "
        "so it is unclear whether the improvement is uniform across campus."
    ),
}

# Fourth article: deliberately contains a claim but no evidence or limitation
ARTICLE_D = {
    "title": "New AI Tool Improves Student Productivity",
    "text": (
        "A new artificial intelligence tool improves student productivity."
    ),
}


# Research summary skill specification
SKILL_SPEC = {
    "name": "research_summary",

    "instructions": [
        "Identify the main claim.",
        "List supporting evidence.",
        "Identify limitations.",
        "Write an undergraduate-level takeaway."
    ],

    "constraints": [
        "Never invent evidence.",
        "Never invent limitations.",
        "Use 'not stated in source' when information is absent.",
        "Never omit the evidence or limitation fields."
    ]
}


# Reusable research summary skill
def apply_research_summary_skill(article):

    article_text = article["text"]

    # Split article into sentences
    sentences = [
        sentence.strip()
        for sentence in article_text.split(".")
        if sentence.strip()
    ]

    # Extract the claim
    claim = (
        sentences[0]
        if sentences
        else "not stated in source"
    )

    # Extract evidence only if another sentence exists
    evidence = (
        sentences[1]
        if len(sentences) > 1
        else "not stated in source"
    )

    # Search for explicitly signalled limitations
    limitation = next(
        (
            sentence
            for sentence in sentences
            if "small" in sentence.lower()
            or "does not include" in sentence.lower()
            or "unclear" in sentence.lower()
            or "may not generalize" in sentence.lower()
        ),
        "not stated in source"
    )

    # Create an undergraduate takeaway
    takeaway = (
        f"Undergraduate takeaway: {claim.rstrip('.')} "
        "-- verify the claim using reliable evidence."
    )

    result = {
        "claim": claim,
        "evidence": evidence,
        "limitation": limitation,
        "takeaway": takeaway
    }

    # Constraint validation: prevent empty evidence/limitation fields
    for field in ["evidence", "limitation"]:
        if not result[field].strip():
            result[field] = "not stated in source"

    return result


# Display research summary
def print_skill_output(article, output):

    print("\n" + "=" * 70)
    print("ARTICLE:", article["title"])
    print("=" * 70)

    for field, value in output.items():
        print(f"{field.capitalize():<15}: {value}")


# Main execution
if __name__ == "__main__":

    print("LOW-EVIDENCE INPUT TEST")

    # Process the fourth article
    output_d = apply_research_summary_skill(ARTICLE_D)

    print_skill_output(ARTICLE_D, output_d)

    # Verify that missing information was not fabricated
    print("\n=== CONSTRAINT VALIDATION ===")

    evidence_valid = (
        output_d["evidence"] == "not stated in source"
    )

    limitation_valid = (
        output_d["limitation"] == "not stated in source"
    )

    print("Evidence correctly marked as missing:", evidence_valid)
    print("Limitation correctly marked as missing:", limitation_valid)

    if evidence_valid and limitation_valid:
        print("\nPASS: No fabrication occurred.")
    else:
        print("\nFAIL: Constraint validation failed.")
