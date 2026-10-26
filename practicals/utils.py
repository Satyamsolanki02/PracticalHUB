
import re
import fitz


def detect_practicals(pdf_path):
    """
    PDF ke text mein practical/experiment headings dhoondhta hai.
    Page numbers 1 se count hote hain.
    """
    detected = []
    patterns = [
        re.compile(
            r"^\s*(?:practical|experiment)\s*"
            r"(?:no\.?\s*)?[-:#.]?\s*(\d+)\s*[:.\-–—]?\s*(.*)$",
            re.IGNORECASE
        ),
        re.compile(
            r"^\s*(?:practical|experiment)\s+"
            r"(?:no\.?\s*)?(\d+)\s*[:.\-–—]?\s*(.*)$",
            re.IGNORECASE
        ),
    ]

    with fitz.open(pdf_path) as document:
        for page_index, page in enumerate(document):
            text = page.get_text("text")

            for line in text.splitlines():
                line = " ".join(line.split())

                if not line:
                    continue

                for pattern in patterns:
                    match = pattern.match(line)

                    if match:
                        number = match.group(1)
                        heading = match.group(2).strip(" :-–—.")

                        name = f"Practical {number}"
                        if heading:
                            name += f" - {heading}"

                        detected.append({
                            "name": name,
                            "start_page": page_index + 1,
                        })
                        break

    # Same practical heading agar ek hi page par repeat ho,
    # toh duplicate entry hata do.
    unique = []
    seen = set()

    for item in detected:
        key = (item["name"].lower(), item["start_page"])
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique
