"""
Parse OCR output from NHC Clinical Terms PDF into structured JSON.
Source: 国家卫健委《常用临床医学名词(2023版)》

Each term line format: 中文名 英文名 [又称]别名△
Section headers: X. 科室名, X.Y 名词类型
"""

import json
import re
import os
import glob

OCR_DIR = "/tmp/nhc_terms_ocr"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "nhc_clinical_terms.json")

# Known chapter mappings (from explicit headers in OCR text)
# Chapters 4 and 5 had no explicit title pages; identified by content
KNOWN_CHAPTERS = {
    1: "眼科",
    2: "耳鼻喉科",
    3: "口腔科",
    4: "急诊科",
    5: "心血管内科",
    6: "呼吸内科",
    7: "消化内科",
    8: "神经内科",
    9: "肾内科",
    10: "内分泌科",
    11: "血液科",
    12: "普通外科",
    13: "神经外科",
    14: "胸外科",
    15: "心血管外科",
    16: "骨科",
    17: "泌尿外科",
    18: "整形外科",
    19: "烧伤科",
    20: "小儿外科",
    21: "麻醉科",
    22: "肿瘤科",
    23: "放射治疗科",
    24: "妇科",
    25: "产科",
    26: "新生儿科",
    27: "皮肤科",
    28: "精神科",
    29: "康复医学科",
    30: "职业病科",
    31: "传染科",
    32: "临床检验科",
}

# Page-based chapter boundaries for chapters without explicit headers.
# Format: (start_page, end_page, chapter_num, chapter_name, section_name)
# These are determined from content analysis of the OCR text.
CHAPTER_PAGE_OVERRIDES = [
    # Chapter 1: 眼科 - no "1.1" header, terms start at page 7
    (7, 29, 1, "眼科", "疾病诊断名词"),
    # Chapter 4: 急诊科 - no "4.1" header, terms on pages 75-76 before 4.2
    (75, 76, 4, "急诊科", "疾病诊断名词"),
    # Chapter 5: 心血管内科 - no "5.1" header, terms on pages 77-84 before 5.2
    (77, 84, 5, "心血管内科", "疾病诊断名词"),
    # Chapters 28-32: no chapter/section headers at all in OCR
    (442, 452, 28, "精神科", "疾病诊断名词"),
    (453, 456, 29, "康复医学科", "疾病诊断名词"),
    (457, 462, 30, "职业病科", "疾病诊断名词"),
    (463, 474, 31, "传染科", "疾病诊断名词"),
    (475, 484, 32, "临床检验科", "疾病诊断名词"),
]

SECTION_TYPES = {
    "1": "疾病诊断名词",
    "2": "症状体征名词",
    "3": "手术操作名词",
    "4": "临床检查名词",
}

# Regex patterns
CHAPTER_HEADER = re.compile(r"^(\d{1,2})\.\s*(.+?)(?:\s|$)")
SECTION_HEADER = re.compile(r"^(\d{1,2})\.(\d)\s+(.+)")
PAGE_HEADER = re.compile(r"^={3,}\s*PAGE\s+(\d+)\s*={3,}$")
PAGE_HEADER_SHORT = re.compile(r"^={3}\s*PAGE\s+(\d+)\s*={3}$")

# Term line: Chinese_name English_name [又称]Alias△
# English name starts with first ASCII letter
# Some terms have no English name (rare)
TERM_LINE = re.compile(
    r"^([一-鿿　-〿＀-￯\d\-/·、，]+.*?)\s+"
    r"([a-zA-Z][\w\s\-/(),.:'\"+=<>]+?)"
    r"(?:\s*\[又称\](.+?)△)?$"
)

# Simpler approach: split on first English letter occurrence
def parse_term_line(line):
    """Parse a single term line into components."""
    line = line.strip()
    if not line:
        return None

    # Skip known non-term lines
    if line.startswith("===") or line.startswith("NHC") or line.startswith("Pages") or line.startswith("==="):
        return None
    if re.match(r"^\d{1,2}\.\d", line):  # section header
        return None
    if re.match(r"^\d{1,2}\.\s", line):  # chapter header
        return None
    if line.startswith("(") or line.startswith("（"):  # note lines
        return None

    # Check for [又称] alias
    alias = None
    alias_match = re.search(r"\[又称\](.+?)△", line)
    if alias_match:
        alias = alias_match.group(1).strip()
        # Remove alias part from line for main parsing
        line_no_alias = line[:alias_match.start()].strip()
    else:
        line_no_alias = line

    # Find where Chinese name ends and English name begins
    # English name starts with an ASCII letter
    # Some lines have Chinese name with digits/symbols, then English
    match = re.match(r"^(.+?)\s+([a-zA-Z].+)$", line_no_alias)
    if not match:
        # No English part - might be a Chinese-only term or OCR artifact
        return None

    chinese = match.group(1).strip()
    english = match.group(2).strip()

    if not chinese or not english:
        return None

    # Clean up Chinese name - remove trailing punctuation that shouldn't be there
    chinese = chinese.rstrip("，。、；：")

    return {
        "standard_name": chinese,
        "english": english,
        "aliases": [alias] if alias else [],
    }


def parse_all():
    """Parse all OCR batch files into structured terms."""
    all_terms = []
    current_chapter = 0
    current_chapter_name = ""
    current_section = ""
    current_page = 0
    stats = {"total_terms": 0, "terms_with_alias": 0, "skipped_lines": 0, "parse_errors": 0}

    # Get all batch files sorted
    batch_files = sorted(glob.glob(os.path.join(OCR_DIR, "batch_*.txt")))

    for batch_file in batch_files:
        print(f"Processing {os.path.basename(batch_file)}...")
        with open(batch_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                stripped = line.strip()

                # Skip empty lines and file headers
                if not stripped or stripped.startswith("NHC") or stripped.startswith("Pages") or stripped == "================================":
                    continue

                # Page header
                page_match = PAGE_HEADER.match(stripped)
                if page_match:
                    current_page = int(page_match.group(1))
                    continue

                # Chapter header: "X. 科室名"
                chapter_match = CHAPTER_HEADER.match(stripped)
                if chapter_match and not SECTION_HEADER.match(stripped):
                    ch_num = int(chapter_match.group(1))
                    ch_name = chapter_match.group(2).strip()
                    # Validate it's a real chapter header (name ends with 科/学 or is known)
                    if ch_name in KNOWN_CHAPTERS.values() or any(
                        ch_name.endswith(s) for s in ["科", "学", "中心"]
                    ):
                        current_chapter = ch_num
                        current_chapter_name = ch_name
                        print(f"  Chapter {ch_num}: {ch_name} (page {current_page})")
                    continue

                # Section header: "X.Y 名词类型"
                section_match = SECTION_HEADER.match(stripped)
                if section_match:
                    sec_chapter = int(section_match.group(1))
                    sec_num = section_match.group(2)
                    sec_name = section_match.group(3).strip()
                    current_section = sec_name
                    # If we didn't have the chapter, try to infer it
                    if sec_chapter != current_chapter:
                        current_chapter = sec_chapter
                        current_chapter_name = KNOWN_CHAPTERS.get(sec_chapter, f"科室{sec_chapter}")
                    print(f"  Section {sec_chapter}.{sec_num}: {sec_name}")
                    continue

                # Try to parse as a term line
                term = parse_term_line(stripped)
                if term:
                    term["chapter"] = current_chapter_name or KNOWN_CHAPTERS.get(current_chapter, "")
                    term["chapter_num"] = current_chapter
                    term["category"] = current_section
                    term["page"] = current_page
                    all_terms.append(term)
                    stats["total_terms"] += 1
                    if term["aliases"]:
                        stats["terms_with_alias"] += 1
                else:
                    # Could be a continuation line, note, or OCR artifact
                    # Skip silently - most are blank lines or headers
                    if stripped and not stripped.startswith("(") and not stripped.startswith("（"):
                        stats["skipped_lines"] += 1

    print(f"\n=== Parsing Complete ===")
    print(f"Total terms: {stats['total_terms']}")
    print(f"Terms with aliases: {stats['terms_with_alias']}")
    print(f"Skipped lines: {stats['skipped_lines']}")

    return all_terms


def fix_chapters(terms):
    """Fix chapter assignments for terms on pages without explicit headers."""
    fixed = 0
    for t in terms:
        page = t.get("page", 0)
        for start, end, ch_num, ch_name, section in CHAPTER_PAGE_OVERRIDES:
            if start <= page <= end:
                if t.get("chapter_num") != ch_num:
                    t["chapter"] = ch_name
                    t["chapter_num"] = ch_num
                    if not t.get("category"):
                        t["category"] = section
                    fixed += 1
                break
    print(f"Fixed chapter assignments: {fixed} terms")
    return terms


def main():
    terms = parse_all()

    # Fix chapter assignments based on known page ranges
    terms = fix_chapters(terms)

    # Deduplicate by standard_name (keep first occurrence)
    seen = set()
    unique_terms = []
    dupes = 0
    for t in terms:
        key = t["standard_name"]
        if key not in seen:
            seen.add(key)
            unique_terms.append(t)
        else:
            dupes += 1

    print(f"Duplicates removed: {dupes}")
    print(f"Unique terms: {len(unique_terms)}")

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(unique_terms, f, ensure_ascii=False, indent=2)

    print(f"\nWritten to {OUTPUT_FILE}")

    # Summary by chapter
    chapter_counts = {}
    for t in unique_terms:
        ch = t.get("chapter", "未知")
        chapter_counts[ch] = chapter_counts.get(ch, 0) + 1

    print("\n=== Terms per Chapter ===")
    for ch, count in sorted(chapter_counts.items(), key=lambda x: -x[1]):
        print(f"  {ch}: {count}")


if __name__ == "__main__":
    main()
