"""Insert the two required fields the authoring template is missing.

`STANDARD.md` §4 points an author at `data/_TEMPLATE.json` as "the full skeleton", but the
template predates 2026-09-13: it has no `difficulty_evidence` and no `provenance.source_family`,
and `validate.py` fails an item for either. A copied template therefore cannot pass the gate.
"""
import json, collections

P = "data/_TEMPLATE.json"
doc = json.load(open(P, encoding="utf-8"))

EVIDENCE = collections.OrderedDict([
    ("lever_type", "ONE term from the closed taxonomy in STANDARD.md 2.4: implicit_dependence | "
                   "variable_swap | exceptional_parameter | decoy_technique | binding_constraint | "
                   "partial_cancellation | non_governing_variable | derived_limit | aggregate_recovery | "
                   "wrong_design_cost | quant_vs_judgement | non_obvious_tool | seeded_anomaly. "
                   "Anything else is a hard failure, on purpose."),
    ("naive_path", "What a well-prepared student actually tries first, concretely enough that a reviewer "
                   "could attempt it. >= 8 words. This is the field that makes the trap testable."),
    ("failure_point", "The exact step where that path breaks, and why. >= 8 words, and it must not "
                      "restate naive_path -- a trap that cannot be located apart from the path is not a trap."),
    ("wrong_answer", "The plausible result the naive path yields instead. >= 8 words, and it must differ "
                     "from the real answer. This commits you to a number a reviewer can check."),
])

FAMILY = ("Closed list (STANDARD.md 4.5): original | ib | china-gaokao | china-qiangji | "
          "china-competition | uk-alevel | uk-further-maths | us-ap | singapore-alevel | other. "
          "If it is anything but `original`, `resource_origin` must name the source -- and the "
          "difficulty has to survive the adaptation, not be borrowed from content this syllabus "
          "does not examine.")

changed = 0
for q in doc["questions"]:
    # difficulty_evidence goes straight after challenge_mechanism, as in every real item.
    if "difficulty_evidence" not in q:
        rebuilt = collections.OrderedDict()
        for k, v in q.items():
            rebuilt[k] = v
            if k == "challenge_mechanism":
                rebuilt["difficulty_evidence"] = EVIDENCE
        if "difficulty_evidence" not in rebuilt:
            rebuilt["difficulty_evidence"] = EVIDENCE
        q.clear()
        q.update(rebuilt)
        changed += 1
    prov = q.get("provenance")
    if prov is not None and "source_family" not in prov:
        rebuilt_p = collections.OrderedDict()
        for k, v in prov.items():
            rebuilt_p[k] = v
            if k == "inspired_by":
                rebuilt_p["source_family"] = FAMILY
        prov.clear()
        prov.update(rebuilt_p)

# The rubric decides the label, so say so next to the field it scores against.
doc["_note"] = (doc["_note"].rstrip() +
                "  `difficulty` is not free: validate.py scores the difficulty_evidence block out of 9 "
                "(STANDARD.md 2.3) and a label of 5 needs 8, a 4 needs 6, with all three prose fields "
                "each scoring full marks. Lower the label, never the evidence.")

with open(P, "w", encoding="utf-8") as fh:
    json.dump(doc, fh, indent=2, ensure_ascii=False)
    fh.write("\n")

print("items given difficulty_evidence:", changed)
for q in doc["questions"]:
    print(" ", q["id"], "->", list(q.keys())[:16])
    print("    provenance:", list(q["provenance"].keys()))
