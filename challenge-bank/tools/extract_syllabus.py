#!/usr/bin/env python3
"""Regenerate tools/syllabus.json from the IB guide PDFs in ../dp learning.

    python3 tools/extract_syllabus.py

Maths AA sub-topic titles are extracted from the 2021 guide programmatically.
Physics and CS titles are taken from the confirmed syllabus roadmap in the
2025/2027 guides (hard-coded, because the roadmap renders as one run of text
with bullet markers rather than as parseable lines). Business Management has no
local guide, so its SL map is hard-coded from the 2024 guide contents.

Every node carries a priority: 1 = must be covered, 2 = should, 3 = optional.
coverage.py uses this to rank the gaps.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDES = ROOT.parent / "dp learning"
OUT = ROOT / "tools" / "syllabus.json"

PHYSICS = {
    "A.1": "Kinematics", "A.2": "Forces and momentum", "A.3": "Work, energy and power",
    "A.4": "Rigid body mechanics", "A.5": "Galilean and special relativity",
    "B.1": "Thermal energy transfers", "B.2": "Greenhouse effect", "B.3": "Gas laws",
    "B.4": "Thermodynamics", "B.5": "Current and circuits",
    "C.1": "Simple harmonic motion", "C.2": "Wave model", "C.3": "Wave phenomena",
    "C.4": "Standing waves and resonance", "C.5": "Doppler effect",
    "D.1": "Gravitational fields", "D.2": "Electric and magnetic fields",
    "D.3": "Motion in electromagnetic fields", "D.4": "Induction",
    "E.1": "Structure of the atom", "E.2": "Quantum physics", "E.3": "Radioactive decay",
    "E.4": "Fission", "E.5": "Fusion and stars",
}

CS = {
    "A1.1": "Computer hardware and operation", "A1.2": "Data representation and computer logic",
    "A1.3": "Operating systems and control systems", "A1.4": "Translation (HL only)",
    "A2.1": "Network fundamentals", "A2.2": "Network architecture", "A2.3": "Data transmissions",
    "A2.4": "Network security",
    "A3.1": "Database fundamentals", "A3.2": "Database design", "A3.3": "Database programming",
    "A3.4": "Alternative databases and data warehouses (HL only)",
    "A4.1": "Machine learning fundamentals", "A4.2": "Data preprocessing (HL only)",
    "A4.3": "Machine learning approaches (HL only)", "A4.4": "Ethical considerations",
    "B1.1": "Approaches to computational thinking",
    "B2.1": "Programming fundamentals", "B2.2": "Data structures",
    "B2.3": "Programming constructs", "B2.4": "Programming algorithms", "B2.5": "File processing",
    "B3.1": "Fundamentals of OOP for a single class",
    "B3.2": "Fundamentals of OOP for multiple classes (HL only)",
    "B4.1": "Fundamentals of ADTs (HL only)",
}

# 2024 BM guide, SL-visible sub-topics only. The unit-6 entries are the eight
# SL Toolkit tools; the other seven tools are HL and must never be used.
BM = {
    "1.1": "What is a business?", "1.2": "Types of business entities",
    "1.3": "Business objectives", "1.4": "Stakeholders",
    "1.5": "Growth and evolution", "1.6": "Multinational companies (MNCs)",
    "2.1": "Introduction to human resource management", "2.2": "Organisational structure",
    "2.3": "Leadership and management", "2.4": "Motivation and demotivation",
    "2.6": "Communication",
    "3.1": "Introduction to finance", "3.2": "Sources of finance", "3.3": "Costs and revenues",
    "3.4": "Final accounts", "3.5": "Profitability and liquidity ratio analysis",
    "3.7": "Cash flow", "3.8": "Investment appraisal",
    "4.1": "The role of marketing", "4.2": "Marketing planning", "4.4": "Market research",
    "4.5": "The seven Ps of the marketing mix",
    "5.1": "The role of operations management", "5.2": "Operations methods",
    "5.4": "Location", "5.5": "Break-even analysis",
    "6.1": "SWOT analysis", "6.2": "Ansoff matrix", "6.3": "STEEPLE analysis",
    "6.4": "Boston Consulting Group (BCG) matrix", "6.5": "Business plan",
    "6.6": "Decision trees", "6.7": "Descriptive statistics", "6.8": "Circular business models",
}

# Sub-topics that exist only at HL. Anything on this list is out of bounds for
# Business Management SL and the validator fails the question if one appears.
BM_HL_ONLY = {
    "1.7": "Organisational planning tools",
    "2.5": "Organisational (corporate) culture", "2.7": "Industrial/employee relations",
    "3.6": "Efficiency ratio analysis", "3.9": "Budgets",
    "4.3": "Sales forecasting", "4.6": "International marketing",
    "5.3": "Lean production and quality management", "5.6": "Production planning",
    "5.7": "Crisis management and contingency planning", "5.8": "Research and development",
    "5.9": "Management information systems",
}


def maths_nodes():
    """Extract (level, code, title) for every SL/AHL sub-topic in the 2021 guide."""
    import pymupdf
    path = GUIDES / "Mathematics Analysis and Approaches Guide 2021 - English.pdf"
    doc = pymupdf.open(path)
    text = re.sub(r"[ \t]+", " ", "\n".join(p.get_text() for p in doc))
    marks = [(m.group(1), m.group(2), m.end()) for m in
             re.finditer(r"\n\s*(SL|AHL)\s+(\d+\.\d+)\s*\n", text)]
    out = {}
    for i, (level, code, end) in enumerate(marks):
        stop = marks[i + 1][2] if i + 1 < len(marks) else end + 4000
        block = text[end:stop]
        block = block.replace("Content", "", 1).strip()
        block = block.replace("Guidance, clarification and syllabus links", "", 1).strip()
        lines = [" ".join(x.split()) for x in block.split("\n") if x.strip()]
        title = lines[0] if lines else ""
        title = re.sub(r"\s*Not required:.*$", "", title)
        if len(title) > 110:
            title = title[:110].rsplit(" ", 1)[0] + "..."
        if code not in out:
            out[code] = (level, title)
    return out


def main():
    nodes = {}

    try:
        maths = maths_nodes()
    except ImportError:
        print("pymupdf is not installed; cannot rebuild the maths map.", file=sys.stderr)
        return 1
    for code, (level, title) in maths.items():
        nodes["Math AA HL"] = nodes.get("Math AA HL", {})
        nodes["Math AA HL"][code] = {
            "title": title, "level": level,
            # AHL material is the HL student's differentiator, so it is covered first.
            "priority": 1 if level == "AHL" else 2,
            "ref": "%s %s" % (level, code),
        }

    for code, title in PHYSICS.items():
        nodes.setdefault("Physics HL", {})[code] = {
            "title": title, "level": "HL", "priority": 1, "ref": code}

    for code, title in CS.items():
        nodes.setdefault("Computer Science HL", {})[code] = {
            "title": title, "level": "HL", "priority": 1, "ref": code}

    for code, title in BM.items():
        # Toolkit tools are exercised inside other questions rather than standing alone.
        prio = 2 if code.startswith("6.") else 1
        nodes.setdefault("Business Management SL", {})[code] = {
            "title": title, "level": "SL", "priority": prio, "ref": code}

    payload = {
        "generated_from": {
            "math": "Mathematics Analysis and Approaches Guide 2021 - English.pdf",
            "physics": "Physics Guide 2025 - English.pdf",
            "cs": "ib-compsci-guide-en-2025.pdf",
            "bm": "IB Business Management guide 2024 (no local copy; SL/HL split verified online)",
        },
        "cohort": "May 2028",
        "subjects": {
            "Math AA HL": {"id_prefix": "MATH", "nodes": nodes["Math AA HL"]},
            "Physics HL": {"id_prefix": "PHYS", "nodes": nodes["Physics HL"]},
            "Computer Science HL": {"id_prefix": "CS", "nodes": nodes["Computer Science HL"]},
            "Business Management SL": {
                "id_prefix": "BM", "nodes": nodes["Business Management SL"],
                "hl_only": BM_HL_ONLY,
                "hl_only_tools": [
                    "gantt", "porter's generic strategies", "porter's generic",
                    "hofstede", "force field analysis", "critical path",
                    "contribution analysis", "linear regression",
                    "fishbone", "absorption costing", "make or buy",
                ],
            },
        },
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for s, body in payload["subjects"].items():
        print("%-24s %3d nodes" % (s, len(body["nodes"])))
    print("\nwrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
