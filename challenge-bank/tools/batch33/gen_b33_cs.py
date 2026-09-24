"""Batch 33, item 3: CS-A2.1-601 -- Computer Science HL, Paper 1 Section A, structured.

Every number is computed from the model the question states, and the model is inverted in part
(c), which is the lever: the candidates have only ever used S = W*MSS*8/RTT forwards.

No figure. The situation is one stated model and three parameters; a diagram would decorate it,
and STANDARD.md 0.1 forbids drawing for the sake of the count.
"""
import json, math, os, sys

MSS, RTT, CAP = 1460, 0.040, 100e6
TARGET = 20e6


def throughput(p, rtt=RTT, mss=MSS):
    return (1.22 / math.sqrt(p)) * mss * 8 / rtt


def loss_for(S, rtt=RTT, mss=MSS):
    """The inversion: p from a required throughput."""
    return (1.22 * mss * 8 / (S * rtt)) ** 2


p0 = 0.01
S0 = throughput(p0)
W0 = 1.22 / math.sqrt(p0)
p_max = loss_for(TARGET)
S_half_rtt = throughput(p0, rtt=RTT / 2)
S_half_p = throughput(p0 / 2)
S_mss4 = throughput(p0, mss=4 * MSS)
print("W=%.2f pkts | S=%.3f Mbit/s | p_max=%.3e (%.4f%%) | half-RTT %.2f | half-p %.2f | 4xMSS %.2f"
      % (W0, S0 / 1e6, p_max, 100 * p_max, S_half_rtt / 1e6, S_half_p / 1e6, S_mss4 / 1e6))
print("ratio of the two upgrades: %.3f" % (S_half_rtt / S_half_p))
print("S as a fraction of the rated capacity: %.4f" % (S0 / CAP))
# the byte-time the window must cover, and the window needed to fill the pipe
bdp = CAP * RTT / 8
print("bandwidth-delay product = %.0f bytes = %.1f MSS-sized packets" % (bdp, bdp / MSS))

sys.path.insert(0, "tools")
import validate as V
taken = {q["id"] for _, q in V.load()}

STEM = ("A file server delivers data over a single TCP connection. The link is rated at "
        "**100 Mbit/s**, the round-trip time is **40 ms**, and packets carry a maximum segment "
        "size (MSS) of **1460 bytes**. Packets are lost independently with probability $p$, and a "
        "loss causes the congestion window to halve.\n\n"
        "A model of the connection's steady state gives the **average window**\n\n"
        "$$W = \\frac{1.22}{\\sqrt{p}} \\quad \\text{packets},$$\n\n"
        "and the throughput is then the number of bytes acknowledged per round trip:\n\n"
        "$$S = \\frac{W \\times \\mathrm{MSS} \\times 8}{\\mathrm{RTT}} .$$\n\n"
        "No knowledge of TCP is assumed beyond these two formulas. Assume the window is never "
        "smaller than one packet and that the receiver never limits the window.")

PARTS = [
    {"label": "a", "marks": 3, "command_term": "Calculate",
     "text": "For a loss probability of $p = 0.01$, calculate the average window in packets and "
             "the resulting throughput in Mbit/s."},
    {"label": "b", "marks": 3, "command_term": "Explain",
     "text": "The link is rated at 100 Mbit/s but the connection delivers the value found in part "
             "(a). Explain, referring to the two formulas, what it is that limits this connection, "
             "and why the rating does not appear in the answer."},
    {"label": "c", "marks": 4, "command_term": "Determine",
     "text": "A new service requires a sustained throughput of 20 Mbit/s on this connection with "
             "the same round-trip time. Determine the maximum packet loss probability the network "
             "can tolerate."},
    {"label": "d", "marks": 2, "command_term": "Determine",
     "text": "Two upgrades are proposed: route the traffic so that the round-trip time is halved, "
             "or improve the network so that the loss probability is halved. Determine the "
             "throughput produced by each and state which is the more effective."},
    {"label": "e", "marks": 3, "command_term": "Evaluate",
     "text": "An engineer proposes achieving the 20 Mbit/s requirement by using packets with four "
             "times the MSS, leaving $p = 0.01$ unchanged. Evaluate this proposal."},
]

ANSWER = r"""**(a)** The window is $W = 1.22 / \\sqrt{0.01} = 1.22 / 0.1 = 12.2$ packets **(M1)**, so about
twelve full segments are acknowledged per round trip. The throughput is

$$S = \frac{12.2 \times 1460 \times 8}{0.040} = 3.56 \times 10^{6}\ \mathrm{bit\,s^{-1}}
= 3.56\ \mathrm{Mbit/s}. \tag{A1}$$

A candidate who rounds the window to 12 packets first obtains $3.50\ \mathrm{Mbit/s}$, which is
accepted **(A1)**.

**(b)** The rating of 100 Mbit/s is the capacity of the wire; it never enters either formula, and
that is not an omission **(M1)**. What the model allows onto the link is $W \times \mathrm{MSS}$
bytes once every round trip, so the achievable rate is set by **how much can be in flight** and
**how long a round trip takes**, not by how fast the wire could carry it. The link is idle for most
of every round trip: putting 12.2 segments on a $100\ \mathrm{Mbit/s}$ wire takes
$\frac{12.2 \times 1460 \times 8}{100 \times 10^{6}} = 1.43\ \mathrm{ms}$, which is $3.6\%$ of the
$40\ \mathrm{ms}$ cycle, and the remaining $96.4\%$ is waiting for acknowledgements **(A1)**. Losses set $W$ through $1.22/\sqrt{p}$, so it is the loss
probability and the round-trip time that govern the throughput; the wire rating only becomes the
limit once the window is large enough to fill it, which at $p = 0.01$ it is nowhere near
**(R1)**.

**(c)** The relation must be run backwards: $p$ is the unknown, and it sits inside a square root in
the denominator **(M1)**. From $S = W \times \mathrm{MSS} \times 8 / \mathrm{RTT}$,

$$W = \frac{S \times \mathrm{RTT}}{\mathrm{MSS} \times 8}
= \frac{20 \times 10^{6} \times 0.040}{1460 \times 8} = 68.5\ \mathrm{packets}. \tag{A1}$$

Then from $W = 1.22 / \sqrt{p}$, squaring is required and $\sqrt{p} = 1.22 / W$ **(M1)**, so

$$p = \left(\frac{1.22 \times \mathrm{MSS} \times 8}{S \times \mathrm{RTT}}\right)^{2}
= \left(\frac{1.22}{68.5}\right)^{2} = 3.17 \times 10^{-4},$$

i.e. about **one packet in 3150**, or $0.032\%$ **(A1)**. The common slip is to divide rather than
to square, giving $p = 1.22/68.5 = 0.0178$ --- a loss rate fifty-six times more forgiving than the
network can actually support, and one that would be reported as a comfortably achievable target.

**(d)** Halving the round-trip time doubles the throughput, because $\mathrm{RTT}$ appears to the
first power in the denominator: $S = 3.56 \times 2 = 7.12\ \mathrm{Mbit/s}$; halving the loss
probability multiplies the window by $\sqrt{2}$, because $p$ appears under a square root:
$W = 1.22/\sqrt{0.005} = 17.3$ packets and $S = 5.04\ \mathrm{Mbit/s}$ **(M1)**. The routing change is
the more effective, by a factor of $7.12 / 5.04 = 1.41 = \sqrt{2}$, and the reason is in the
exponents: the model is linear in $1/\mathrm{RTT}$ and only proportional to $1/\sqrt{p}$ **(A1)**.

**(e)** Substituting $4 \times \mathrm{MSS}$ gives $S = 4 \times 3.56 = 14.2\ \mathrm{Mbit/s}$,
which the model does scale linearly with **(M1)** --- and even that is short of the 20
$\mathrm{Mbit/s}$ required, so the proposal cannot reach the target on the model's own terms
**(A1)**. It also fails on the way there: a segment of $4 \times 1460 = 5840$ bytes does not fit an
Ethernet frame, whose MTU is 1500 bytes, so the data would be fragmented, and a fragment carries the
same loss exposure as a whole segment --- losing any fragment retransmits the datagram, so the
effective loss probability rises rather than staying at $0.01$ **(A1)**. The MSS is not a free
variable to be traded against $p$; it is fixed by the link, which is exactly why the model treats
it as a constant."""

NOTES = r"""**(a)** (M1) for $W = 12.2$ packets; (A1) for $3.56\ \mathrm{Mbit/s}$. Accept $3.5$ from a window
rounded to 12, and accept $3.6$ from $\sqrt{0.01} = 0.1$ carried to one significant figure at the
end. Do not accept an answer that uses the 100 Mbit/s rating --- that is part (b)'s misconception,
and it earns nothing here.

**(b)** (M1) for observing that the rating does not appear in the model, (A1) for quantifying the
idle time or the bytes-in-flight limit, (R1) for naming what does govern the rate. A candidate who
says only "there is overhead" or "TCP is slow" has not used the two formulas given and scores (M1)
at most; the question says *referring to the two formulas*, and that is the reasoning being marked.
Accept the bandwidth-delay-product argument in place of the idle-time argument: $100\ \mathrm{Mbit/s}
\times 40\ \mathrm{ms} = 500\ \mathrm{KB} \approx 342$ packets would be needed to fill the pipe, and
$12$ is far short of it.

**(c)** (M1) for committing to the inversion by solving for $W$, (A1) for $W = 68.5$ packets, (M1)
for squaring rather than dividing, (A1) for $p = 3.17 \times 10^{-4}$. Accept $3.2 \times 10^{-4}$,
$0.032\%$, or "about one packet in 3000". The division slip $p = 0.0178$ loses the two marks that
depend on the square; do not carry it forward as if it were the target value. Follow-through is
allowed from a part-(a) throughput the candidate computed wrongly, provided the inversion is
correctly performed on their own number.

**(d)** (M1) for both values, $7.12$ and $5.04\ \mathrm{Mbit/s}$; (A1) for the routing change
together with the exponent reason. A numerical answer with no reason scores (M1) only. A candidate who answers "halving $p$ is better because losses are
the root cause" has reasoned from intuition against their own arithmetic and scores the two
numerical marks only.

**(e)** (M1) for the model's $14.2\ \mathrm{Mbit/s}$, (A1) for noting that this still misses the
20 required, (A1) for the objection. Accept the MTU argument, the fragmentation argument, or the
observation that a larger segment carries proportionally more data per loss and so raises the cost
of a loss; do not accept "it would work" or a bare "MSS cannot be changed" without a reason. The engineer's proposal is attractive precisely because the algebra
works, which is why the (M1) is awarded freely and the (A1) is not."""

EXPL = r"""The item is one misconception with two formulas attached to it. Students who have been taught
that a $100\ \mathrm{Mbit/s}$ link delivers $100\ \mathrm{Mbit/s}$ will compute part (a) correctly
and be dissatisfied with the answer, and part (b) exists to make them say why the number is small
rather than let it pass. The governing quantity is the product of the window and the segment size
divided by the round-trip time; the wire rating is a ceiling that this connection never approaches,
and the model says so plainly by not containing $100\ \mathrm{Mbit/s}$ anywhere.

Part (c) is where the difficulty actually sits. The formula has been used in one direction --- give
me $p$, I will tell you $S$ --- and the question asks the other way. The unknown is under a square
root in a denominator, so the inversion requires squaring at the end, and the reflex is to divide:
$1.22 / 68.5 = 0.0178$, which is a loss rate fifty-six times more permissive than the truth and
would be reported as a comfortable margin. Nothing in the arithmetic looks wrong; the number is a
small decimal, in the right order of magnitude to be plausible, and only the structure of the model
says it is not.

Part (d) rewards the same structural reading rather than the calculation. Both upgrades are
"factor of two" changes, and they are not equal, because $\mathrm{RTT}$ enters to the first power
and $p$ enters under a root: the ratio comes out at $\sqrt{2}$, and a candidate who has understood
the model can predict that before computing it. Part (e) closes the item on the kind of judgement
the papers increasingly ask for: the proposal produces the right number from the given model, and it
is still wrong, because the model treats as a free constant something the link fixes. Learning to
distract oneself with an algebra that is valid inside a model and void outside it is the transfer
this item is for."""

ITEM = {
    "id": "CS-A2.1-601",
    "subject": "Computer Science HL", "level": "HL",
    "syllabus_ref": "A2.1 Network fundamentals (the difference between latency, bandwidth and "
                    "throughput), with A2.3 Data transmissions (packet switching and retransmission)",
    "topic": "Theme A: Concepts of computer science",
    "subtopic": "A2.1 Network fundamentals: a stated model of a windowed connection, where the "
                "throughput is governed by bytes in flight per round trip rather than by the rated "
                "capacity of the link",
    "paper": "P1", "section": "A", "question_type": "structured",
    "technology": None, "language": None,
    "marks": 15, "difficulty": 5,
    "challenge_mechanism":
        "The model has only ever been read forwards, from loss probability to throughput; part (c) "
        "asks for the reverse, and because the unknown sits under a square root in a denominator the "
        "inversion ends in a squaring that the familiar direction never requires --- so the reflex "
        "division produces a loss rate fifty-six times too forgiving and looks entirely plausible.",
    "difficulty_evidence": {
        "lever_type": "variable_swap",
        "naive_path":
            "Compute the window and the throughput as the question's own example does, then for the "
            "required throughput divide 1.22 by the window it implies and report the quotient as the "
            "loss probability.",
        "failure_point":
            "The unknown $p$ is under a square root in the denominator of $W = 1.22/\\sqrt{p}$, so "
            "solving for it means isolating the root and squaring both sides, and the quotient "
            "$1.22/W$ is the square root of the answer rather than the answer.",
        "wrong_answer":
            "A maximum tolerable loss probability of $0.0178$, obtained by dividing instead of "
            "squaring, which is fifty-six times the network's real tolerance of $3.17 \\times 10^{-4}$ "
            "and would be reported as a comfortable margin on a link that cannot support the service.",
    },
    "command_terms": ["Calculate", "Explain", "Determine", "Determine", "Evaluate"],
    "tags": ["networks", "throughput", "bandwidth", "latency", "congestion window", "packet loss",
             "model inversion", "P1", "Section A", "batch33"],
    "stimulus": None,
    "figure": None,
    "question": ("A network engineer is asked to size a connection for a new service. Use the model "
                 "given above to answer the questions that follow. Numerical answers should be given "
                 "to three significant figures."),
    "parts": PARTS,
    "answer": ANSWER, "markscheme_notes": NOTES, "explanation": EXPL,
    "provenance": {
        "inspired_by": "the A-level and IB-style 'why is my fast link slow' packet-trace question, "
                       "and the TCP steady-state window model used in university networking courses",
        "source_family": "uk-alevel",
        "adaptation":
            "The situation is the standard one; the question is not. A-level treatments ask the "
            "candidate to read a graph of throughput against loss or to explain one effect in "
            "prose. Here (i) the model is stated in full so that no protocol knowledge is required "
            "and the algebra is the assessment, (ii) the given and asked quantities are inverted "
            "relative to every worked example of this model --- the loss probability is the unknown, "
            "and it hides under a square root, (iii) part (d) asks which of two 'factor of two' "
            "upgrades wins, which is a comparison of exponents rather than a calculation, and (iv) "
            "part (e) supplies a proposal that the model endorses and the physical link refutes. "
            "IB command terms, marking annotations and the three-significant-figure convention are "
            "applied throughout.",
        "resource_origin": "AQA/OCR A-level Computer Science network-performance questions "
                           "(throughput below stated bandwidth) and the standard TCP "
                           "steady-state window model as presented in university first-course "
                           "networking notes; the model itself is stated in the question",
        "source_url": None, "rights": "original",
    },
    "originality": {"max_similarity": None, "nearest_bank_id": None,
                    "max_internal_similarity": None, "nearest_internal_id": None,
                    "max_approach_similarity": None, "nearest_approach_id": None,
                    "checked_at": None},
    "verification": {
        "method":
            "Every value was computed from the two stated formulas and then cross-checked by an "
            "independent route. $W(0.01) = 12.2$ packets and $S = 3.56\\ \\mathrm{Mbit/s}$; the "
            "inversion in (c) was checked by substituting the answer back into the forward model, so "
            "that $W = 1.22/\\sqrt{%.6e} = %.1f$ packets returns $S = %.4f\\ \\mathrm{Mbit/s}$ against "
            "the required 20. The two upgrades in (d) were computed both from the formula and from "
            "the exponents alone ($\\times 2$ and $\\times\\sqrt{2}$), agreeing at $7.12$ and $5.04$ "
            "$\\mathrm{Mbit/s}$, and their ratio is $\\sqrt{2}$ to three figures. The idle-time claim "
            "in (b) was checked two ways: $12.2$ segments take $1.42\\ \\mathrm{ms}$ of $40\\ "
            "\\mathrm{ms}$, and the bandwidth-delay product of the link is $500\\ \\mathrm{KB} = "
            "%.0f$ packets against a window of $12.2$. The division slip $1.22/W = %.5f$ was computed "
            "explicitly to confirm that it is $56$ times the correct tolerance, which is what makes it "
            "a plausible wrong answer rather than a straw one." % (
                p_max, 1.22 / math.sqrt(p_max), throughput(p_max) / 1e6, CAP * RTT / 8 / MSS,
                1.22 / 68.5),
        "assertions": [
            "approx(1.22/sqrt(0.01), 12.2, 1e-12)",
            "approx(%.6e/1e6, 3.56, 0.005)" % S0,
            "approx(%.6e, 3.17e-4, 1e-6)" % p_max,
            "approx(1.22/sqrt(%.6e), 68.5, 0.1)" % p_max,
            "approx(%.6e*8/0.040/1e6, 20.0, 0.05)" % (68.5 * MSS),
            "approx(%.6e/1e6, 7.12, 0.01)" % S_half_rtt,
            "approx(%.6e/1e6, 5.04, 0.01)" % S_half_p,
            "approx(%.6e/%.6e, sqrt(2), 1e-3)" % (S_half_rtt, S_half_p),
            "approx(1.22/68.5, 0.0178, 1e-4)",
            "approx((1.22/(20e6*0.040/(1460*8)))**2, %.9e, 1e-12)" % p_max,
            "approx(0.0178/%.6e, 56.1, 0.6)" % p_max,
            "approx(12.2*1460*8/100e6*1000, 1.43, 0.02)",
            "approx(100e6*0.040/8/1460, 342.5, 0.5)",
            "approx(%.6e/1e6, 14.2, 0.02)" % S_mss4,
            "4*1460 > 1500",
            "3.17e-4 < 0.01",
        ],
        "solution_skeleton": [
            "evaluate the stated window model at the given loss probability",
            "convert packets per round trip into a bit rate through the segment size",
            "rearrange the throughput relation to find the window a target rate demands",
            "isolate the square root and square both sides to recover the loss probability",
            "compare two interventions by the exponent each variable carries",
            "test a proposal that the model supports but the physical link does not",
        ],
        "checked_by": "ai", "status": "pass",
    },
    "status": "published", "authored_by": "ai",
    "created_at": "2026-09-24", "updated_at": "2026-09-24",
}

# ---------------------------------------------------------------- self-check
assert ITEM["id"] not in taken or "--force" in sys.argv, "id collision"
taken.discard(ITEM["id"])
assert sum(p["marks"] for p in ITEM["parts"]) == ITEM["marks"]
first, rest = ITEM["parts"][0]["marks"], [p["marks"] for p in ITEM["parts"][1:]]
assert first <= max(rest), "arc: the first part is the heaviest"
assert len(ITEM["verification"]["assertions"]) >= 0.5 * ITEM["marks"]
assert 3 <= len(ITEM["verification"]["solution_skeleton"]) <= 6
for f, med in (("answer", 652), ("markscheme_notes", 258), ("explanation", 380)):
    n = len(str(ITEM[f]).split())
    print("  %-18s %4d words (80%% of median = %d)" % (f, n, 0.8 * med))
    assert n >= 0.8 * med, f

OUT = "data/computer-science-hl/batch33.json"
if os.path.exists(OUT) and "--force" not in sys.argv:
    sys.exit("%s exists -- pass --force" % OUT)
json.dump({"_batch": "33", "questions": [ITEM]}, open(OUT, "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)
print("wrote", OUT)
