# -*- coding: utf-8 -*-
"""Which key points each of the 12 SAMPLE questions (S1..S12) actually uses.

Same contract as tools/paper2025/keys.py: build.py stamps it onto the questions
(`key: [...]`), and tools/paper2025/build_concepts.py reverses it into each concept's
"used by" list. The two maps are resolved together, so a concept reached only by the
sample sheet still gets a non-empty reverse index and the "every concept is used by
at least one question" gate keeps its teeth.

Four ids here have no counterpart in the 2025 map, because the sample sheet teaches
something the past paper never tested: `criticalangle`, `secondorder`,
`apparentweight` and `tailmass`. They are authored in tools/paper2025/concepts_d.py.
"""

KEYS = {
    # S1 — two nuclei written in A-over-Z form; only the neutron number matches
    "R0S-01": ["nuclide", "ratio", "nocalc"],
    # S2 — five antinodes on a string of fixed length: length = 5 half-wavelengths
    "R0S-02": ["standingwaves", "waves", "ratio"],
    # S3 — two cells sharing a zero-resistance link: the link current is the difference
    "R0S-03": ["kirchhoff", "networks", "seriesparallel", "readdiagram"],
    # S4 — the whole double-slit rig under water: lambda shrinks by n, so does w
    "R0S-04": ["superposition", "refractive", "ratio", "nocalc"],
    # S5 — one resistor, first in series with a twin then in parallel with it
    "R0S-05": ["resistance", "seriesparallel", "ratio", "nocalc"],
    # S6 — which combination of base units is a capacitance
    "R0S-06": ["capacitors", "units", "dimensions"],
    # S7 — three rods under an equilateral sheet, with an extra load on an edge
    "R0S-07": ["moments", "com", "statics", "readdiagram"],
    # S8 — the shape of critical angle against refractive index
    "R0S-08": ["criticalangle", "snell", "refractive", "graphshape"],
    # S9 — three springs displaced sideways: the first-order term cancels
    "R0S-09": ["secondorder", "hookeslaw", "smallchange", "ratio"],
    # S10 — f from L, rho and E: dimensions fix the exponent for free
    "R0S-10": ["dimensions", "ratio", "nocalc"],
    # S11 — the ground pushes less hard at the equator, by the centripetal term
    "R0S-11": ["apparentweight", "circular", "ratio", "nocalc"],
    # S12 — tension behind block n in a chain whose masses halve going back
    "R0S-12": ["tailmass", "force", "ratio", "nocalc"],
}
