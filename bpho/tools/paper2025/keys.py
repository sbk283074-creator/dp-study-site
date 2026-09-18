# -*- coding: utf-8 -*-
"""Which key points each of the 25 past-paper questions actually uses.

This is the single place the mapping lives: build.py stamps it onto the questions
(`key: [...]`) and build_concepts.py reverses it into each concept's "used by" list.
Every id here must exist in concepts_*.py and every concept must appear here.
"""

KEYS = {
    "R0-01": ["stressstrain", "strainenergy", "units-elim"],
    "R0-02": ["refractive", "snell", "readdiagram", "nocalc"],
    "R0-03": ["units", "momentum", "dimensions"],
    "R0-04": ["nuclide", "alphabeta", "decayseries"],
    "R0-05": ["waves", "superposition", "pathphase", "coherence", "nocalc"],
    "R0-06": ["resistance", "seriesparallel", "search"],
    "R0-07": ["kinematics", "relvel", "readdiagram"],
    "R0-08": ["charge", "meters", "kirchhoff"],
    "R0-09": ["standingwaves", "lineardensity", "resistivity", "ratio"],
    "R0-10": ["stdform", "estimate", "moles"],
    "R0-11": ["photons", "levels", "counting"],
    "R0-12": ["momcons", "ke", "limits"],
    "R0-13": ["dimensions", "casimir"],
    "R0-14": ["com", "toppling", "statics", "nocalc"],
    "R0-15": ["specificheat", "latentheat", "stdform"],
    "R0-16": ["snell", "lightspeed", "surds", "nocalc"],
    "R0-17": ["photoelectric", "stopping", "capacitors"],
    "R0-18": ["projectile", "smallangle", "limits"],
    "R0-19": ["expdecay", "logs", "nocalc"],
    "R0-20": ["force", "hookeslaw", "shm", "graphshape"],
    "R0-21": ["vectors-resolve", "kinematics", "moments", "statics"],
    "R0-22": ["circular", "conical", "ratio", "nocalc"],
    "R0-23": ["loggraphs", "inversesquare", "divider", "nocalc"],
    "R0-24": ["com", "pe-gpe", "smallchange"],
    "R0-25": ["seriesparallel", "networks", "ratio", "nocalc"],
}
