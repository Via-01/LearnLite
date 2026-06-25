# pdf_utils.py

import pymupdf4llm


def extract_pdf_markdown(pdf_path: str) -> str:
    """
    Convert PDF to markdown using PyMuPDF4LLM.
    """
    try:
        return pymupdf4llm.to_markdown(pdf_path)
    except Exception as e:
        return f"PDF extraction failed: {e}"


def split_sections(markdown_text: str):
    """
    Split markdown into sections based on headings.
    """
    if not markdown_text:
        return []

    sections = []

    current_section = ""

    for line in markdown_text.splitlines():
        if line.startswith("#"):
            if current_section.strip():
                sections.append(current_section)

            current_section = line + "\n"

        else:
            current_section += line + "\n"

    if current_section.strip():
        sections.append(current_section)

    return sections


def score_section(section: str, question: str) -> int:
    """
    Basic keyword overlap scoring.
    """

    section_lower = section.lower()

    score = 0

    for word in question.lower().split():
        word = word.strip()

        if len(word) < 3:
            continue

        score += section_lower.count(word)

    return score


def get_relevant_context(
    markdown_text: str,
    question: str,
    max_sections: int = 3,
):
    """
    Retrieve most relevant sections.
    """

    sections = split_sections(markdown_text)

    if not sections:
        return markdown_text[:5000]

    scored = []

    for section in sections:
        scored.append(
            (
                score_section(section, question),
                section,
            )
        )

    scored.sort(reverse=True, key=lambda x: x[0])

    selected = []

    for score, section in scored[:max_sections]:
        if score > 0:
            selected.append(section)

    if not selected:
        selected = sections[:3]

    return "\n\n".join(selected)[:8000]


def extract_headings(markdown_text: str):
    """
    Extract headings for evidence card.
    """

    headings = []

    for line in markdown_text.splitlines():
        if line.startswith("#"):
            headings.append(line.replace("#", "").strip())

    return headings[:15]
