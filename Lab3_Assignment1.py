
"""
Lab 3: Skill Creation - Research Summary Skill
Assignment 1: Handle a Multi-Claim Source

The reusable research-summary skill is tested on three articles.
The third article contains two competing claims. The skill selects
the claim with stronger supporting evidence and explains its choice.
"""

# --------------------------------------------------
# STEP 1: Define three different article inputs
# --------------------------------------------------

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

# New article with two unrelated claims:
# 1. Operating cost reduction.
# 2. Answer accuracy improvement.
ARTICLE_C = {
    "title": "AI Tutoring Platform: Cost and Accuracy Evaluation",
    "text": (
        "The AI tutoring platform reduced annual operating costs by 20%. "
        "However, the report does not explain how the cost reduction was calculated "
        "or what period was compared. The platform also improved answer accuracy "
        "from 78% to 91%. Accuracy was measured on a test of 500 questions "
        "independently reviewed by subject experts against a reference answer key. "
        "The evaluation was conducted at one university, so results may not "
        "generalize to other institutions."
    ),
}


# --------------------------------------------------
# STEP 2: Define the reusable skill instructions
# --------------------------------------------------

SKILL_SPEC = {
    "name": "research_summary",

    "instructions": [
        "Identify the single main claim.",
        "List supporting evidence for that claim.",
        "Note at least one limitation, or 'not stated in source' if absent.",
        "Write a one-sentence undergraduate-level takeaway.",
        "If multiple unrelated claims exist, select the most evidence-supported claim.",
        "Explicitly explain when a selection is made between competing claims."
    ],

    "constraints": [
        "Never present a hedged claim as an unhedged fact.",
        "Never omit the limitation field.",
        "Do not invent information that is not in the source.",
        "Do not silently select the first claim when multiple claims exist."
    ]
}


# --------------------------------------------------
# STEP 3: Helper functions for claim detection
# --------------------------------------------------

CLAIM_INDICATORS = [
    "reduced",
    "increased",
    "improved",
    "decreased",
    "fell",
    "rose",
    "lowered",
    "saved"
]


def split_sentences(article_text):
    return [
        sentence.strip()
        for sentence in article_text.split(".")
        if sentence.strip()
    ]


def is_claim_sentence(sentence):
    sentence_lower = sentence.lower()

    return any(
        indicator in sentence_lower
        for indicator in CLAIM_INDICATORS
    )


def evidence_strength_score(evidence):
    """
    Assign a simple evidence score based on details
    explicitly present in the supporting sentence.
    """

    if evidence == "not stated in source":
        return 0

    evidence_lower = evidence.lower()
    score = 0

    # Quantitative detail
    if any(character.isdigit() for character in evidence):
        score += 2

    # Measurement or evaluation methods
    method_keywords = [
        "measured",
        "evaluation",
        "tested",
        "reviewed",
        "compared",
        "calculated",
        "recorded"
    ]

    for keyword in method_keywords:
        if keyword in evidence_lower:
            score += 2

    # Evidence involving a defined sample
    sample_keywords = [
        "questions",
        "participants",
        "records",
        "cases",
        "invoices",
        "test"
    ]

    for keyword in sample_keywords:
        if keyword in evidence_lower:
            score += 1

    # Independent or expert verification
    verification_keywords = [
        "independently",
        "subject experts",
        "reference answer"
    ]

    for keyword in verification_keywords:
        if keyword in evidence_lower:
            score += 2

    return score


# --------------------------------------------------
# STEP 4: Implement the reusable research skill
# --------------------------------------------------

def apply_research_summary_skill(article):
    """
    Apply the research-summary skill to an article.

    If multiple claims are detected, compare their
    supporting evidence and select the strongest one.
    """

    sentences = split_sentences(article["text"])

    # Detect all claim sentences.
    claim_indices = [
        index
        for index, sentence in enumerate(sentences)
        if is_claim_sentence(sentence)
    ]

    # Find the limitation.
    limitation = next(
        (
            sentence
            for sentence in sentences
            if any(
                keyword in sentence.lower()
                for keyword in [
                    "small",
                    "does not include",
                    "unclear",
                    "may not generalize",
                    "does not explain",
                    "not explain"
                ]
            )
        ),
        "not stated in source"
    )

    # ------------------------------------------------
    # Case 1: Multiple competing claims
    # ------------------------------------------------

    if len(claim_indices) > 1:

        candidates = []

        for index in claim_indices:

            claim = sentences[index]

            # Examine the sentence immediately after the claim.
            evidence = (
                sentences[index + 1]
                if index + 1 < len(sentences)
                else "not stated in source"
            )

            # Avoid treating a limitation as supporting evidence.
            if evidence == limitation:
                evidence = "not stated in source"

            score = evidence_strength_score(evidence)

            candidates.append({
                "claim": claim,
                "evidence": evidence,
                "score": score
            })

        # Select the claim with the highest evidence score.
        selected = max(
            candidates,
            key=lambda candidate: candidate["score"]
        )

        claim = selected["claim"]
        evidence = selected["evidence"]

        selection_note = (
            f"Multiple claims were detected. The selected claim was: "
            f"'{claim}'. It received an evidence score of "
            f"{selected['score']}. The skill selected it because its "
            f"supporting evidence was stronger than the competing claims."
        )

        # Include the competing claims in the explanation.
        for candidate in candidates:
            if candidate["claim"] != claim:
                selection_note += (
                    f" Competing claim: '{candidate['claim']}' "
                    f"(evidence score: {candidate['score']})."
                )

    # ------------------------------------------------
    # Case 2: Only one claim
    # ------------------------------------------------

    else:

        claim = sentences[claim_indices[0]] if claim_indices else (
            sentences[0] if sentences else "not stated in source"
        )

        claim_position = (
            claim_indices[0] if claim_indices else 0
        )

        evidence = (
            sentences[claim_position + 1]
            if claim_position + 1 < len(sentences)
            else "not stated in source"
        )

        if evidence == limitation:
            evidence = "not stated in source"

        selection_note = (
            "Only one main claim was detected; "
            "no competing-claim selection was needed."
        )

    # Create undergraduate-level takeaway.
    takeaway = (
        f"Undergraduate takeaway: {claim.strip().rstrip('.')} "
        "-- but verify before generalizing."
    )

    return {
        "claim": claim,
        "evidence": evidence,
        "limitation": limitation,
        "takeaway": takeaway,
        "selection_note": selection_note
    }


# --------------------------------------------------
# STEP 5: Display the skill output
# --------------------------------------------------

def print_skill_output(article, output):

    print("\n" + "=" * 75)
    print("ARTICLE:", article["title"])
    print("=" * 75)

    print("\nRESEARCH SUMMARY")

    print("-" * 75)
    print(f"{'FIELD':<17} | CONTENT")
    print("-" * 75)

    print(f"{'Claim':<17} | {output['claim']}")
    print(f"{'Evidence':<17} | {output['evidence']}")
    print(f"{'Limitation':<17} | {output['limitation']}")
    print(f"{'Takeaway':<17} | {output['takeaway']}")
    print(f"{'Claim Selection':<17} | {output['selection_note']}")

    print("-" * 75)


# --------------------------------------------------
# STEP 6: Check whether the skill is reusable
# --------------------------------------------------

def reusability_check(*outputs):

    expected_keys = set(outputs[0].keys())

    same_structure = all(
        set(output.keys()) == expected_keys
        for output in outputs
    )

    all_have_limitation = all(
        output["limitation"] != ""
        for output in outputs
    )

    print("\n" + "=" * 50)
    print("REUSABILITY CHECK")
    print("=" * 50)

    print("Same output structure across all inputs:", same_structure)

    print("Limitation field populated in all outputs:", all_have_limitation)

    if same_structure and all_have_limitation:
        print("\nConclusion: SKILL IS REUSABLE")
    else:
        print("\nConclusion: SKILL NEEDS TIGHTER INSTRUCTIONS")


# --------------------------------------------------
# STEP 7: Execute the skill on all three articles
# --------------------------------------------------

if __name__ == "__main__":

    print("RESEARCH SUMMARY SKILL")
    print("Skill name:", SKILL_SPEC["name"])

    # Apply the same reusable skill to all three articles.
    output_a = apply_research_summary_skill(ARTICLE_A)
    output_b = apply_research_summary_skill(ARTICLE_B)
    output_c = apply_research_summary_skill(ARTICLE_C)

    # Display all outputs.
    print_skill_output(ARTICLE_A, output_a)
    print_skill_output(ARTICLE_B, output_b)
    print_skill_output(ARTICLE_C, output_c)

    # Verify that the competing-claim selection occurred.
    assert "Multiple claims were detected" in output_c["selection_note"]
    assert "answer accuracy" in output_c["claim"].lower()
    assert output_c["evidence"] != "not stated in source"

    print("\n=== Multi-Claim Verification ===")
    print("Multiple claims detected: PASS")
    print("Most evidence-supported claim selected: PASS")
    print("Selection explicitly explained: PASS")

    # Verify reusability.
    reusability_check(output_a, output_b, output_c)
