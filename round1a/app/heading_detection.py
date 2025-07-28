import fitz
from collections import defaultdict
import re

HEADING_MAX_LEN = 120

def is_heading_candidate(text):
    text = text.strip()
    if not text:
        return False
    if len(text) > HEADING_MAX_LEN:
        return False
    if re.search(r"[.:;]$", text):  # headings usually don't end with punctuation
        return False
    # Allow numbers (e.g., "1. Introduction"), but not mostly numeric junk
    if len(re.sub(r"\d+[\.\)]*", "", text).strip()) == 0:
        return False
    return True

def detect_outline(pdf_path):
    doc = fitz.open(pdf_path)
    spans_info = []  # (page_idx, text, font, size, bold)

    for page_idx, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            for l in b.get("lines", []):
                for s in l.get("spans", []):
                    text = s.get("text", "").strip()
                    if not text:
                        continue
                    size = s.get("size", 0)
                    font = s.get("font", "")
                    bold = "Bold" in font or font.endswith("-B") or font.endswith("Bold")
                    spans_info.append((page_idx, text, font, size, bold))

    # Gather candidate headings by line merge heuristic: combine adjacent spans of similar size on same page
    lines_by_page = defaultdict(list)
    for page_idx, text, font, size, bold in spans_info:
        lines_by_page[page_idx].append((text, font, size, bold))

    candidates = []
    for page_idx, lines in lines_by_page.items():
        buffer = []
        prev_size = None
        prev_bold = None
        for text, font, size, bold in lines:
            if buffer and (abs(size - prev_size) > 0.1 or bold != prev_bold):
                merged = " ".join([x[0] for x in buffer]).strip()
                if is_heading_candidate(merged):
                    candidates.append((page_idx, merged, buffer[0][2], any(x[3] for x in buffer)))
                buffer = []
            buffer.append((text, font, size, bold))
            prev_size, prev_bold = size, bold
        if buffer:
            merged = " ".join([x[0] for x in buffer]).strip()
            if is_heading_candidate(merged):
                candidates.append((page_idx, merged, buffer[0][2], any(x[3] for x in buffer)))

    if not candidates:
        title = ""
        return {"title": title, "outline": []}

    # Collect distinct sizes to infer hierarchy
    sizes = sorted({c[2] for c in candidates}, reverse=True)
    # Map sizes to H-levels
    # Largest size → Title (only first occurrence), then H1/H2/H3
    level_map = {}
    if sizes:
        for idx, s in enumerate(sizes):
            if idx == 0:
                level_map[s] = "TITLE"
            elif idx == 1:
                level_map[s] = "H1"
            elif idx == 2:
                level_map[s] = "H2"
            else:
                level_map[s] = "H3"

    title = ""
    outline = []
    used_title = False
    for page, text, size, bold in candidates:
        level = level_map.get(size, "H3")
        if level == "TITLE" and not used_title:
            title = text
            used_title = True
        else:
            # Promote bold or ALL CAPS to higher heading level when ambiguous
            if bold and level == "H3":
                level = "H2"
            if text.isupper() and level == "H2":
                level = "H1"
            if level == "TITLE":
                level = "H1"
            outline.append({"level": level, "text": text, "page": page})

    return {
        "title": title,
        "outline": outline
    }