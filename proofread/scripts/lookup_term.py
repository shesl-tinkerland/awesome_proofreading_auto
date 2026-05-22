"""
NHC临床医学术语快速查询工具。
用法:
  python lookup_term.py 心房钠尿肽          # 查询某术语是否为规范名/别名
  python lookup_term.py 心房钠尿肽 --all    # 返回所有匹配（含模糊）
  python lookup_term.py --chapter 心血管内科  # 列出某科室所有术语
  python lookup_term.py --stats             # 输出统计信息
"""

import json
import sys
import os
import re

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TERMS_FILE = os.path.join(_SCRIPT_DIR, "..", "references", "knowledge_base", "nhc_clinical_terms.json")


def load_terms():
    with open(TERMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def lookup(query, terms, find_all=False):
    """Look up a term by Chinese name, English name, or alias."""
    results = []

    # Exact match on standard_name
    for t in terms:
        if t["standard_name"] == query:
            results.append(("exact_standard", t))

    # Match on alias
    for t in terms:
        if query in t.get("aliases", []):
            results.append(("alias", t))

    # Exact match on english name (case-insensitive)
    query_lower = query.lower()
    for t in terms:
        if t["english"].lower() == query_lower:
            results.append(("exact_english", t))

    if find_all:
        # Fuzzy: standard_name contains query
        for t in terms:
            if query in t["standard_name"] and t["standard_name"] != query:
                results.append(("fuzzy_standard", t))
        # Fuzzy: english contains query
        for t in terms:
            if query_lower in t["english"].lower() and t["english"].lower() != query_lower:
                results.append(("fuzzy_english", t))

    return results


def by_chapter(chapter_name, terms):
    """Return all terms for a given chapter."""
    return [t for t in terms if t.get("chapter") == chapter_name]


def print_result(match_type, term):
    label = {
        "exact_standard": "✓ 规范名",
        "alias": "→ 别名（规范名如下）",
        "exact_english": "✓ 英文名匹配",
        "fuzzy_standard": "~ 近似中文名",
        "fuzzy_english": "~ 近似英文名",
    }.get(match_type, "?")

    print(f"  [{label}] {term['standard_name']} / {term['english']}")
    if term.get("aliases"):
        print(f"    别名: {', '.join(term['aliases'])}")
    print(f"    科室: {term.get('chapter', '?')} | 分类: {term.get('category', '?')}")


def main():
    terms = load_terms()

    if len(sys.argv) < 2:
        print("用法: python lookup_term.py <术语> [--all|--chapter <科室>|--stats]")
        return

    arg = sys.argv[1]

    if arg == "--stats":
        chapters = {}
        for t in terms:
            ch = t.get("chapter", "未知")
            chapters[ch] = chapters.get(ch, 0) + 1
        print(f"总术语数: {len(terms)}")
        print(f"有别名术语: {sum(1 for t in terms if t.get('aliases'))}")
        print(f"科室数: {len(chapters)}")
        print("\n各科室术语数:")
        for ch, cnt in sorted(chapters.items(), key=lambda x: -x[1]):
            print(f"  {ch}: {cnt}")
        return

    if arg == "--chapter":
        if len(sys.argv) < 3:
            print("请指定科室名称")
            return
        chapter_terms = by_chapter(sys.argv[2], terms)
        print(f"{sys.argv[2]}: {len(chapter_terms)} 条术语")
        for t in chapter_terms[:20]:
            alias_str = f" [又称: {', '.join(t['aliases'])}]" if t.get("aliases") else ""
            print(f"  {t['standard_name']} / {t['english']}{alias_str}")
        if len(chapter_terms) > 20:
            print(f"  ... 还有 {len(chapter_terms) - 20} 条")
        return

    find_all_flag = "--all" in sys.argv
    results = lookup(arg, terms, find_all=find_all_flag)

    if not results:
        print(f"未找到: {arg}")
        print("（该术语不在卫健委《常用临床医学名词(2023版)》中）")
        return

    print(f"查询: {arg} ({len(results)} 条结果)")
    seen = set()
    for match_type, term in results:
        key = term["standard_name"]
        if key not in seen:
            seen.add(key)
            print_result(match_type, term)


if __name__ == "__main__":
    main()
