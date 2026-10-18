from toddler_book.agent.agent import cited_passages, parse_citations


def passage(file_name: str, page: int, text: str = "x") -> dict:
    return {"file_name": file_name, "page": page, "score": 0.5, "text": text}


def test_only_cited_pages_are_returned_deduplicated_and_sorted():
    retrieved = [passage("b.pdf", 2), passage("a.pdf", 7), passage("a.pdf", 3), passage("a.pdf", 3)]
    answer = "Fact one [a.pdf, p.7]. Fact two [b.pdf, p. 2] and [a.pdf, p.3]."

    result = cited_passages(answer, retrieved)

    assert [(p["file_name"], p["page"]) for p in result] == [("a.pdf", 3), ("a.pdf", 7), ("b.pdf", 2)]


def test_parses_page_ranges_and_grouped_citations():
    answer = (
        "Step four [The Adult Journey Five Steps.pdf, p.3-4]. "
        "Step five [The Adult Journey Five Steps.pdf, p.3; Step 5 - Part 1 I Solve.pdf, p.1]. "
        "Not a citation [see above]."
    )
    assert parse_citations(answer) == {
        ("The Adult Journey Five Steps.pdf", 3),
        ("The Adult Journey Five Steps.pdf", 4),
        ("Step 5 - Part 1 I Solve.pdf", 1),
    }


def test_uncited_answer_lists_no_sources():
    retrieved = [passage("a.pdf", 1), passage("a.pdf", 2)]
    assert cited_passages("I couldn't find that in your sources.", retrieved) == []


def test_no_retrieval_means_no_citations():
    assert cited_passages("Hi there!", []) == []
