/* ============================================================================
 * DP Study Site — global Formula Booklet + Scientific Calculator
 * Loaded on every page of the static site (GitHub Pages) from an absolute URL,
 * injected by assets/ai-widget.js. Self-contained: own styles, own launch
 * buttons and panels, no external dependencies, no MathJax needed.
 *
 * TWO FLOATING BARS
 *   1. FORMULA BOOKLET — the OFFICIAL IB Diploma Programme booklets that ship
 *      in the repo (dp learning/公示表.pdf = Mathematics: analysis and
 *      approaches formula booklet, First examinations 2021 v1.3; and
 *      dp learning/物理DataBooklet2025.pdf = Physics data booklet, First
 *      assessment 2025 v1.1). Content is transcribed faithfully, grouped by
 *      topic with the booklet's own section references (e.g. SL 1.2, A.4).
 *      Rendered with plain HTML (fractions / roots / sub-sup) so it looks
 *      identical on every page, even where MathJax is not loaded.
 *   2. SCIENTIFIC CALCULATOR — a real evaluator (shunting-yard -> RPN) with
 *      deg/rad toggle and a full scientific function set: trig + inverse,
 *      hyperbolic, logs (ln / log10 / log2 / 10^x / e^x), roots (sqrt / cbrt /
 *      nth-root / x^2 / x^3 / x^y), constants (π / e), reciprocal, absolute,
 *      sec/csc/cot, factorial, permutations/combinations (nPr / nCr),
 *      modulo, implicit multiplication, Ans memory and a store/recall (M/MR).
 * ==========================================================================*/
(function () {
  "use strict";

  if (window.__dpToolsLoaded) return;
  window.__dpToolsLoaded = true;

  // --- small HTML helpers for nicely-set formulas (no MathJax needed) --------
  function frac(n, d) {
    return '<span class="fb-frac"><span class="fb-n">' + n + '</span><span class="fb-d">' + d + '</span></span>';
  }
  function root(x) { return '<span class="fb-rad">' + x + '</span>'; }
  function sup(x) { return '<sup>' + x + '</sup>'; }
  function sub(x) { return '<sub>' + x + '</sub>'; }

  // ---- formula booklet content (sourced from the official IB booklets) ------
  // Structure: subject -> topic -> [ { ref, t, f, k } ]
  var FORMULAS = {
    "Mathematics AA HL": {
      "Prior learning": [
        { t: "Area of a parallelogram", f: "A = bh", k: "parallelogram base height area" },
        { t: "Area of a triangle", f: "A = " + frac("1", "2") + "bh", k: "triangle area" },
        { t: "Area of a trapezoid", f: "A = " + frac("1", "2") + "(a+b)h", k: "trapezoid area" },
        { t: "Area of a circle", f: "A = πr" + sup("2"), k: "circle area" },
        { t: "Circumference of a circle", f: "C = 2πr", k: "circle circumference" },
        { t: "Volume of a cuboid", f: "V = lwh", k: "cuboid volume" },
        { t: "Volume of a cylinder", f: "V = πr" + sup("2") + "h", k: "cylinder volume" },
        { t: "Volume of a prism", f: "V = Ah", k: "prism volume" },
        { t: "Curved surface of a cylinder", f: "A = 2πrh", k: "cylinder curved surface" },
        { t: "Distance between two points", f: "d = " + root("(" + sub("x2") + "−" + sub("x1") + ")" + sup("2") + "+(" + sub("y2") + "−" + sub("y1") + ")" + sup("2")), k: "distance coordinates" },
        { t: "Midpoint of a line segment", f: "(" + frac(sub("x1") + "+" + sub("x2"), "2") + ", " + frac(sub("y1") + "+" + sub("y2"), "2") + ")", k: "midpoint coordinates" }
      ],
      "Topic 1 — Number & algebra": [
        { ref: "SL 1.2", t: "nth term of an arithmetic sequence", f: "u" + sup("n") + " = u" + sup("1") + "+(n−1)d", k: "arithmetic sequence nth term" },
        { ref: "SL 1.2", t: "Sum of n terms of an arithmetic sequence", f: "S" + sup("n") + " = " + frac("n", "2") + "(2u" + sup("1") + "+(n−1)d) = " + frac("n", "2") + "(u" + sup("1") + "+u" + sup("n") + ")", k: "arithmetic sum" },
        { ref: "SL 1.3", t: "nth term of a geometric sequence", f: "u" + sup("n") + " = u" + sup("1") + "r" + sup("n−1"), k: "geometric sequence nth term" },
        { ref: "SL 1.3", t: "Sum of n terms of a finite geometric sequence", f: "S" + sup("n") + " = " + frac("u" + sup("1") + "(1−r" + sup("n") + ")", "1−r") + " = " + frac("u" + sup("1") + "−ru" + sup("n"), "1−r") + "  (r≠1)", k: "geometric sum" },
        { ref: "SL 1.4", t: "Compound interest", f: "FV = PV × " + root("1+" + frac("r", "100k")) + sup("nk"), k: "compound interest future value" },
        { ref: "SL 1.5", t: "Exponents and logarithms", f: "a" + sup("x") + " = b ⇔ x = log" + sub("a") + "b  (a>0, a≠1, b>0)", k: "exponent logarithm" },
        { ref: "SL 1.7", t: "Laws of logarithms", f: "log" + sub("a") + "(xy) = log" + sub("a") + "x + log" + sub("a") + "y ; log" + sub("a") + "(" + frac("x", "y") + ") = log" + sub("a") + "x − log" + sub("a") + "y", k: "logarithm laws product quotient" },
        { ref: "SL 1.8", t: "Sum of an infinite geometric sequence", f: "S" + sup("∞") + " = " + frac("u" + sup("1"), "1−r") + "  (|r|<1)", k: "infinite geometric sum" },
        { ref: "SL 1.9", t: "Binomial theorem", f: "(a+b)" + sup("n") + " = Σ " + frac("n!", "r!(n−r)!") + " a" + sup("n−r") + "b" + sup("r"), k: "binomial expansion combination" }
      ],
      "Topic 1 — HL only": [
        { ref: "AHL 1.10", t: "Combinations", f: "C" + sub("n,r") + " = " + frac("n!", "r!(n−r)!"), k: "combination choose" },
        { ref: "AHL 1.10", t: "Permutations", f: "P" + sub("n,r") + " = " + frac("n!", "(n−r)!"), k: "permutation arrange" },
        { ref: "AHL 1.10", t: "Extension of binomial theorem (n∈ℝ)", f: "(a+b)" + sup("n") + " = a" + sup("n") + "+n a" + sup("n−1") + "b+" + frac("n(n−1)", "2!") + "a" + sup("n−2") + "b" + sup("2") + "+…", k: "binomial real exponent" },
        { ref: "AHL 1.12", t: "Complex numbers", f: "z = a+bi", k: "complex number real imaginary" },
        { ref: "AHL 1.13", t: "Modulus-argument (polar) & Euler form", f: "z = r(cosθ+i sinθ) = r e" + sup("iθ"), k: "complex polar euler modulus argument" },
        { ref: "AHL 1.14", t: "De Moivre's theorem", f: "[r(cosθ+i sinθ)]" + sup("n") + " = r" + sup("n") + "(cos nθ+i sin nθ)", k: "de moivre complex power" }
      ],
      "Topic 2 — Functions": [
        { ref: "SL 2.1", t: "Equations of a straight line", f: "y = mx+c ; ax+by+d = 0 ; y−y" + sub("1") + " = m(x−x" + sub("1") + ")", k: "straight line equation gradient" },
        { ref: "SL 2.1", t: "Gradient formula", f: "m = " + frac("y" + sup("2") + "−y" + sup("1"), "x" + sup("2") + "−x" + sup("1")), k: "gradient slope" },
        { ref: "SL 2.6", t: "Axis of symmetry of a quadratic", f: "f(x)=ax" + sup("2") + "+bx+c ⇒ x = −" + frac("b", "2a"), k: "quadratic axis symmetry" },
        { ref: "SL 2.7", t: "Solutions of a quadratic equation", f: "ax" + sup("2") + "+bx+c=0 ⇒ x = " + frac("−b±" + root("b" + sup("2") + "−4ac"), "2a"), k: "quadratic formula roots solve" },
        { ref: "SL 2.7", t: "Discriminant", f: "Δ = b" + sup("2") + "−4ac", k: "discriminant nature of roots" },
        { ref: "SL 2.9", t: "Exponential and logarithmic functions", f: "a" + sup("x") + " = e" + sup("x ln a") + " ; log" + sub("a") + "a" + sup("x") + " = x  (a>0, a≠1)", k: "exponential logarithmic" }
      ],
      "Topic 2 — HL only": [
        { ref: "AHL 2.12", t: "Sum & product of roots of a polynomial", f: "Σ = −" + frac("a" + sup("n−1"), "a" + sup("n")) + " ; Π = (−1)" + sup("n") + frac("a" + sup("0"), "a" + sup("n")), k: "polynomial roots sum product vieta" }
      ],
      "Topic 3 — Geometry & trigonometry": [
        { ref: "SL 3.1", t: "Distance between two 3-D points", f: "d = " + root("(" + sub("x2") + "−" + sub("x1") + ")" + sup("2") + "+(" + sub("y2") + "−" + sub("y1") + ")" + sup("2") + "+(" + sub("z2") + "−" + sub("z1") + ")" + sup("2")), k: "3d distance coordinates" },
        { ref: "SL 3.1", t: "Midpoint of a 3-D line segment", f: "(" + frac(sub("x1") + "+" + sub("x2"), "2") + ", " + frac(sub("y1") + "+" + sub("y2"), "2") + ", " + frac(sub("z1") + "+" + sub("z2"), "2") + ")", k: "3d midpoint" },
        { ref: "SL 3.1", t: "Volume of a right-pyramid", f: "V = " + frac("1", "3") + "Ah", k: "pyramid volume" },
        { ref: "SL 3.1", t: "Volume of a right cone", f: "V = " + frac("1", "3") + "πr" + sup("2") + "h", k: "cone volume" },
        { ref: "SL 3.1", t: "Curved surface area of a cone", f: "A = πrl", k: "cone curved surface" },
        { ref: "SL 3.1", t: "Volume of a sphere", f: "V = " + frac("4", "3") + "πr" + sup("3"), k: "sphere volume" },
        { ref: "SL 3.1", t: "Surface area of a sphere", f: "A = 4πr" + sup("2"), k: "sphere surface area" },
        { ref: "SL 3.2", t: "Sine rule", f: frac("a", "sin A") + " = " + frac("b", "sin B") + " = " + frac("c", "sin C"), k: "sine rule triangle" },
        { ref: "SL 3.2", t: "Cosine rule", f: "c" + sup("2") + " = a" + sup("2") + "+b" + sup("2") + "−2ab cos C", k: "cosine rule triangle" },
        { ref: "SL 3.2", t: "Area of a triangle", f: "A = " + frac("1", "2") + "ab sin C", k: "area triangle trig" },
        { ref: "SL 3.4", t: "Length of an arc", f: "l = rθ  (θ in radians)", k: "arc length radians" },
        { ref: "SL 3.4", t: "Area of a sector", f: "A = " + frac("1", "2") + "r" + sup("2") + "θ", k: "sector area radians" }
      ],
      "Topic 3 — HL only": [
        { ref: "AHL 3.5", t: "Identity for tan θ", f: "tanθ = " + frac("sinθ", "cosθ"), k: "tangent identity" },
        { ref: "AHL 3.6", t: "Pythagorean identity", f: "sin" + sup("2") + "θ + cos" + sup("2") + "θ = 1", k: "pythagorean trig identity" },
        { ref: "AHL 3.6", t: "Double angle identity (sin)", f: "sin 2θ = 2 sinθ cosθ", k: "double angle sine" },
        { ref: "AHL 3.6", t: "Double angle identity (cos)", f: "cos 2θ = cos" + sup("2") + "θ − sin" + sup("2") + "θ = 2cos" + sup("2") + "θ − 1", k: "double angle cosine" },
        { ref: "AHL 3.9", t: "Reciprocal trigonometric identities", f: "secθ = " + frac("1", "cosθ") + " ; cosecθ = " + frac("1", "sinθ"), k: "secant cosecant reciprocal" },
        { ref: "AHL 3.9", t: "Pythagorean identities", f: "1+tan" + sup("2") + "θ = sec" + sup("2") + "θ ; 1+cot" + sup("2") + "θ = cosec" + sup("2") + "θ", k: "trig pythagorean identities" },
        { ref: "AHL 3.10", t: "Compound angle identities", f: "sin(A±B) = sinA cosB ± cosA sinB", k: "compound angle sine" },
        { ref: "AHL 3.10", t: "Compound angle identities (cos)", f: "cos(A±B) = cosA cosB ∓ sinA sinB", k: "compound angle cosine" },
        { ref: "AHL 3.10", t: "Compound angle identity (tan)", f: "tan(A±B) = " + frac("tanA ± tanB", "1 ∓ tanA tanB"), k: "compound angle tangent" },
        { ref: "AHL 3.12", t: "Magnitude of a vector", f: "|v| = " + root("v" + sub("1") + sup("2") + "+v" + sub("2") + sup("2") + "+v" + sub("3") + sup("2")), k: "vector magnitude length" },
        { ref: "AHL 3.13", t: "Scalar product", f: "v·w = v" + sub("1") + "w" + sub("1") + "+v" + sub("2") + "w" + sub("2") + "+v" + sub("3") + "w" + sub("3") + " = |v||w| cosθ", k: "dot product scalar" },
        { ref: "AHL 3.16", t: "Vector product", f: "v×w = (v" + sub("2") + "w" + sub("3") + "−v" + sub("3") + "w" + sub("2") + ", v" + sub("3") + "w" + sub("1") + "−v" + sub("1") + "w" + sub("3") + ", v" + sub("1") + "w" + sub("2") + "−v" + sub("2") + "w" + sub("1") + ")", k: "cross product vector" },
        { ref: "AHL 3.17", t: "Equation of a plane", f: "r·n = a·n ; ax+by+cz = d", k: "plane equation normal" }
      ],
      "Topic 4 — Statistics & probability": [
        { ref: "SL 4.2", t: "Interquartile range", f: "IQR = Q" + sup("3") + "−Q" + sup("1"), k: "interquartile range iqr" },
        { ref: "SL 4.3", t: "Mean of a set of data", f: "x̄ = " + frac("Σ f" + sub("i") + "x" + sub("i"), "Σ f" + sub("i")), k: "mean average" },
        { ref: "SL 4.5", t: "Probability of an event", f: "P(A) = " + frac("n(A)", "n(U)") + " ; P(A)+P(A′) = 1", k: "probability complement" },
        { ref: "SL 4.6", t: "Combined events", f: "P(A∪B) = P(A)+P(B)−P(A∩B)", k: "probability union intersection" },
        { ref: "SL 4.6", t: "Conditional probability", f: "P(A|B) = " + frac("P(A∩B)", "P(B)"), k: "conditional probability bayes" },
        { ref: "SL 4.6", t: "Independent events", f: "P(A∩B) = P(A)P(B)", k: "independent probability" },
        { ref: "SL 4.7", t: "Expected value of X", f: "E(X) = Σ x·P(X=x)", k: "expected value mean random" },
        { ref: "SL 4.8", t: "Binomial distribution", f: "X ~ B(n,p) ; E(X)=np ; Var(X)=np(1−p)", k: "binomial distribution expected variance" },
        { ref: "SL 4.12", t: "Standardized normal variable", f: "z = " + frac("x−μ", "σ"), k: "normal standardise z score" }
      ],
      "Topic 4 — HL only": [
        { ref: "AHL 4.13", t: "Bayes' theorem", f: "P(B" + sub("i") + "|A) = " + frac("P(B" + sub("i") + ")P(A|B" + sub("i") + ")", "Σ P(B" + sub("j") + ")P(A|B" + sub("j") + ")"), k: "bayes theorem" },
        { ref: "AHL 4.14", t: "Variance", f: "σ" + sup("2") + " = " + frac("Σ f" + sub("i") + "(x" + sub("i") + "−μ)" + sup("2"), "Σ f" + sub("i")), k: "variance standard deviation" }
      ],
      "Topic 5 — Calculus": [
        { ref: "SL 5.3", t: "Derivative of x" + sup("n"), f: frac("d", "dx") + "(x" + sup("n") + ") = n x" + sup("n−1"), k: "differentiate derivative power" },
        { ref: "SL 5.5", t: "Integral of x" + sup("n"), f: "∫ x" + sup("n") + " dx = " + frac("x" + sup("n+1"), "n+1") + "+C  (n≠−1)", k: "integrate integral power" },
        { ref: "SL 5.5", t: "Area under a curve", f: "A = ∫" + sub("a") + sup("b") + " y dx", k: "area under curve integral" },
        { ref: "SL 5.6", t: "Standard derivatives", f: frac("d", "dx") + "(sin x)=cos x ; " + frac("d", "dx") + "(cos x)=−sin x ; " + frac("d", "dx") + "(e" + sup("x") + ")=e" + sup("x") + " ; " + frac("d", "dx") + "(ln x)=" + frac("1", "x"), k: "derivative sine cosine exponential log" },
        { ref: "SL 5.6", t: "Chain rule", f: frac("dy", "dx") + " = " + frac("dy", "du") + "·" + frac("du", "dx"), k: "chain rule derivative" },
        { ref: "SL 5.6", t: "Product rule", f: frac("d", "dx") + "(uv) = u" + frac("dv", "dx") + "+v" + frac("du", "dx"), k: "product rule derivative" },
        { ref: "SL 5.6", t: "Quotient rule", f: frac("d", "dx") + "(" + frac("u", "v") + ") = " + frac("v" + frac("du", "dx") + "−u" + frac("dv", "dx"), "v" + sup("2")), k: "quotient rule derivative" },
        { ref: "SL 5.9", t: "Acceleration", f: "a = " + frac("dv", "dt") + " = " + frac("d" + sup("2") + "s", "dt" + sup("2")), k: "acceleration velocity displacement" }
      ],
      "Topic 5 — HL only": [
        { ref: "AHL 5.10", t: "Standard integrals", f: "∫" + frac("1", "x") + "dx = ln|x|+C ; ∫sin x dx = −cos x+C ; ∫cos x dx = sin x+C ; ∫e" + sup("x") + "dx = e" + sup("x") + "+C", k: "integral sin cos exp log" },
        { ref: "AHL 5.12", t: "Derivative from first principles", f: "f′(x) = lim" + sub("h→0") + frac("f(x+h)−f(x)", "h"), k: "first principles derivative limit" },
        { ref: "AHL 5.12", t: "Standard derivatives (tan…cosec)", f: frac("d", "dx") + "(tan x)=sec" + sup("2") + "x ; " + frac("d", "dx") + "(sec x)=sec x tan x ; " + frac("d", "dx") + "(cosec x)=−cosec x cot x ; " + frac("d", "dx") + "(cot x)=−cosec" + sup("2") + "x", k: "derivative tangent secant cosecant cotangent" },
        { ref: "AHL 5.12", t: "Derivatives of a" + sup("x") + " and log" + sub("a") + "x", f: frac("d", "dx") + "(a" + sup("x") + ")=a" + sup("x") + " ln a ; " + frac("d", "dx") + "(log" + sub("a") + "x)=" + frac("1", "x ln a"), k: "derivative exponential log base" },
        { ref: "AHL 5.12", t: "Derivatives of inverse trig", f: frac("d", "dx") + "(arcsin x)=" + frac("1", root("1−x" + sup("2"))) + " ; " + frac("d", "dx") + "(arctan x)=" + frac("1", "1+x" + sup("2")), k: "derivative arcsine arctangent" },
        { ref: "AHL 5.15", t: "Standard integral", f: "∫" + frac("1", "x" + sup("2") + "+a" + sup("2")) + "dx = " + frac("1", "a") + " arctan(" + frac("x", "a") + ")+C", k: "integral arctan" },
        { ref: "AHL 5.16", t: "Integration by parts", f: "∫u " + frac("dv", "dx") + "dx = uv − ∫v " + frac("du", "dx") + "dx", k: "integration by parts" },
        { ref: "AHL 5.17", t: "Volume of revolution", f: "V = π ∫ y" + sup("2") + " dx  (or π ∫ x" + sup("2") + " dy)", k: "volume revolution solid" },
        { ref: "AHL 5.18", t: "Euler's method", f: "y" + sub("n+1") + " = y" + sub("n") + "+h·f(x" + sub("n") + ",y" + sub("n") + ")", k: "euler method numerical" },
        { ref: "AHL 5.19", t: "Maclaurin series", f: "f(x) = f(0)+x f′(0)+" + frac("x" + sup("2"), "2!") + "f″(0)+…", k: "maclaurin taylor series expansion" },
        { ref: "AHL 5.19", t: "Maclaurin series of special functions", f: "e" + sup("x") + "=1+x+" + frac("x" + sup("2"), "2!") + "+… ; sin x = x−" + frac("x" + sup("3"), "3!") + "+" + frac("x" + sup("5"), "5!") + "−… ; cos x = 1−" + frac("x" + sup("2"), "2!") + "+" + frac("x" + sup("4"), "4!") + "−…", k: "maclaurin exponential sine cosine" }
      ]
    },
    "Physics HL": {
      "Data & constants": [
        { t: "Acceleration of free fall", f: "g = 9.8 m s" + sup("−2"), k: "gravity free fall constant earth" },
        { t: "Gravitational constant", f: "G = 6.67×10" + sup("−11") + " N m" + sup("2") + " kg" + sup("−2"), k: "gravitational constant" },
        { t: "Avogadro constant", f: "N" + sub("A") + " = 6.02×10" + sup("23") + " mol" + sup("−1"), k: "avogadro constant" },
        { t: "Gas constant", f: "R = 8.31 J K" + sup("−1") + " mol" + sup("−1"), k: "gas constant" },
        { t: "Boltzmann constant", f: "k" + sub("B") + " = 1.38×10" + sup("−23") + " J K" + sup("−1"), k: "boltzmann constant" },
        { t: "Stefan–Boltzmann constant", f: "σ = 5.67×10" + sup("−8") + " W m" + sup("−2") + " K" + sup("−4"), k: "stefan boltzmann constant" },
        { t: "Coulomb constant", f: "k = 8.99×10" + sup("9") + " N m" + sup("2") + " C" + sup("−2"), k: "coulomb constant electric" },
        { t: "Permittivity of free space", f: "ε" + sub("0") + " = 8.85×10" + sup("−12") + " C" + sup("2") + " N" + sup("−1") + " m" + sup("−2"), k: "permittivity free space" },
        { t: "Permeability of free space", f: "μ" + sub("0") + " = 4π×10" + sup("−7") + " T m A" + sup("−1"), k: "permeability free space" },
        { t: "Speed of light in vacuum", f: "c = 3.00×10" + sup("8") + " m s" + sup("−1"), k: "speed of light" },
        { t: "Planck constant", f: "h = 6.63×10" + sup("−34") + " J s", k: "planck constant" },
        { t: "Elementary charge", f: "e = 1.60×10" + sup("−19") + " C", k: "elementary charge electron" },
        { t: "Electron rest mass", f: "m" + sub("e") + " = 9.11×10" + sup("−31") + " kg", k: "electron mass" },
        { t: "Proton rest mass", f: "m" + sub("p") + " = 1.67×10" + sup("−27") + " kg", k: "proton mass" },
        { t: "Neutron rest mass", f: "m" + sub("n") + " = 1.675×10" + sup("−27") + " kg", k: "neutron mass" },
        { t: "Unified atomic mass unit", f: "u = 1.66×10" + sup("−27") + " kg", k: "atomic mass unit" },
        { t: "Metric (SI) multipliers", f: "peta P 10" + sup("15") + " · tera T 10" + sup("12") + " · giga G 10" + sup("9") + " · mega M 10" + sup("6") + " · kilo k 10" + sup("3") + " · centi c 10" + sup("−2") + " · milli m 10" + sup("−3") + " · micro μ 10" + sup("−6") + " · nano n 10" + sup("−9") + " · pico p 10" + sup("−12") + " · femto f 10" + sup("−15"), k: "si prefixes multipliers peta tera giga mega kilo milli micro nano pico femto" },
        { t: "Unit conversions", f: "180° = π rad ; T(K)=T(°C)+273 ; 1 ly = 9.46×10" + sup("15") + " m ; 1 AU = 1.50×10" + sup("11") + " m ; 1 kWh = 3.60×10" + sup("6") + " J", k: "unit conversion radian kelvin light year au kwh" }
      ],
      "Uncertainties": [
        { t: "Sum or difference", f: "y = a±b ⇒ Δy = Δa + Δb", k: "uncertainty sum difference addition" },
        { t: "Product or quotient", f: frac("Δy", "y") + " = " + frac("Δa", "a") + "+" + frac("Δb", "b") + "+" + frac("Δc", "c") + "  (y = ab/c)", k: "uncertainty product quotient multiplication division" },
        { t: "Power", f: frac("Δy", "y") + " = n" + frac("Δa", "a") + "  (y = a" + sup("n") + ")", k: "uncertainty power" }
      ],
      "A — Space, time & motion": [
        { ref: "A.1", t: "Kinematics", f: "s = ut+" + frac("1", "2") + "at" + sup("2") + " ; v = u+at ; v" + sup("2") + " = u" + sup("2") + "+2as", k: "suvat kinematics acceleration" },
        { ref: "A.2", t: "Forces (friction & spring)", f: "F" + sub("s") + " ≤ μ" + sub("s") + "N ; F = −kx", k: "friction spring hooke force" },
        { ref: "A.2", t: "Drag & buoyancy", f: "F" + sub("d") + " = 6πηrv ; F" + sub("b") + " = ρVg", k: "drag viscous buoyancy stokes" },
        { ref: "A.2", t: "Momentum & impulse", f: "p = mv ; J = FΔt = Δp", k: "momentum impulse collision" },
        { ref: "A.2", t: "Newton's second law", f: "F = " + frac("Δp", "Δt") + " = ma", k: "newton second law force mass acceleration" },
        { ref: "A.2", t: "Circular motion", f: "a = " + frac("v" + sup("2"), "r") + " = rω" + sup("2") + " ; T = " + frac("2πr", "v") + " = " + frac("2π", "ω"), k: "circular motion centripetal angular period" },
        { ref: "A.3", t: "Work, energy & power", f: "W = Fs cosθ ; ΔE" + sub("p") + " = mgh ; E" + sub("k") + " = " + frac("1", "2") + "mv" + sup("2") + " ; P = " + frac("W", "Δt") + " = Fv", k: "work energy power kinetic potential" },
        { ref: "A.3", t: "Efficiency", f: "η = " + frac("useful work out", "total work in"), k: "efficiency" }
      ],
      "A — HL only": [
        { ref: "A.4", t: "Rigid body — torque", f: "τ = Fr sinθ", k: "torque moment rigid body" },
        { ref: "A.4", t: "Rotational kinematics", f: "ω" + sub("f") + " = ω" + sub("i") + "+αt ; ω" + sub("f") + sup("2") + " = ω" + sub("i") + sup("2") + "+2αΔθ", k: "angular acceleration rotational kinematics" },
        { ref: "A.4", t: "Moment of inertia & angular momentum", f: "I = Σmr" + sup("2") + " ; τ = Iα ; L = Iω", k: "moment inertia angular momentum" },
        { ref: "A.4", t: "Rotational kinetic energy", f: "E" + sub("k") + " = " + frac("1", "2") + "Iω" + sup("2"), k: "rotational kinetic energy" },
        { ref: "A.5", t: "Lorentz factor", f: "γ = " + frac("1", root("1−v" + sup("2") + "/c" + sup("2"))), k: "lorentz gamma relativity" },
        { ref: "A.5", t: "Time dilation & length contraction", f: "Δt = γΔt" + sub("0") + " ; L = " + frac("L" + sub("0"), "γ"), k: "time dilation length contraction special relativity" }
      ],
      "B — Particulate matter": [
        { ref: "B.1", t: "Density", f: "ρ = " + frac("m", "V"), k: "density mass volume" },
        { ref: "B.1", t: "Kinetic energy (per molecule)", f: "E" + sub("k") + " = " + frac("3", "2") + "k" + sub("B") + "T", k: "kinetic theory temperature" },
        { ref: "B.1", t: "Thermal energy", f: "Q = mcΔT ; Q = mL", k: "heat thermal specific latent capacity" },
        { ref: "B.1", t: "Thermal conduction", f: frac("ΔQ", "Δt") + " = " + frac("kAΔT", "x"), k: "conduction heat transfer" },
        { ref: "B.1", t: "Stefan–Boltzmann & Wien", f: "L = σAT" + sup("4") + " ; λ" + sub("max") + "T = 2.90×10" + sup("−3") + " m K", k: "stefan boltzmann wien radiation" },
        { ref: "B.3", t: "Gas laws", f: "P = " + frac("F", "A") + " ; PV = nRT = Nk" + sub("B") + "T", k: "ideal gas pressure volume temperature" },
        { ref: "B.3", t: "Pressure & internal energy", f: "P = " + frac("1", "3") + "ρ⟨c" + sup("2") + "⟩ ; U = " + frac("3", "2") + "Nk" + sub("B") + "T", k: "gas pressure internal energy kinetic" },
        { ref: "B.5", t: "Current & potential difference", f: "I = " + frac("Δq", "Δt") + " ; V = " + frac("W", "q"), k: "current charge potential difference" },
        { ref: "B.5", t: "Resistance & resistivity", f: "R = " + frac("V", "I") + " ; ρ = " + frac("RA", "L"), k: "resistance resistivity ohm" },
        { ref: "B.5", t: "Electrical power", f: "P = VI = I" + sup("2") + "R = " + frac("V" + sup("2"), "R"), k: "electrical power ohm" },
        { ref: "B.5", t: "Series & parallel circuits", f: "R" + sub("s") + " = ΣR ; " + frac("1", "R" + sub("p")) + " = Σ" + frac("1", "R"), k: "series parallel resistance circuit" },
        { ref: "B.5", t: "emf of a source", f: "ε = I(R+r)", k: "emf internal resistance source" }
      ],
      "B — HL only": [
        { ref: "B.4", t: "First law of thermodynamics", f: "ΔU = Q+W ; W = PΔV", k: "thermodynamics first law internal energy" },
        { ref: "B.4", t: "Entropy", f: "ΔS = " + frac("Q", "T") + " ; S = k" + sub("B") + " lnΩ", k: "entropy thermodynamics" },
        { ref: "B.4", t: "Carnot efficiency", f: "η" + sub("Carnot") + " = 1 − " + frac("T" + sub("c"), "T" + sub("h")), k: "carnot efficiency heat engine" }
      ],
      "C — Wave behaviour": [
        { ref: "C.1", t: "Simple harmonic motion", f: "a = −ω" + sup("2") + "x ; T = " + frac("1", "f") + " = " + frac("2π", "ω"), k: "shm simple harmonic acceleration period" },
        { ref: "C.1", t: "Pendulum & spring period", f: "T = 2π" + root("m/k") + " ; T = 2π" + root("l/g"), k: "pendulum spring period" },
        { ref: "C.2", t: "Wave model", f: "v = fλ = " + frac("λ", "T"), k: "wave speed frequency wavelength" },
        { ref: "C.3", t: "Refraction (Snell's law)", f: "n" + sub("1") + " sinθ" + sub("1") + " = n" + sub("2") + " sinθ" + sub("2"), k: "snell refraction index" },
        { ref: "C.3", t: "Interference", f: "constructive: path diff = nλ ; destructive: (n+" + frac("1", "2") + ")λ", k: "interference constructive destructive path difference" },
        { ref: "C.3", t: "Double-slit spacing", f: "s = " + frac("Dλ", "d"), k: "double slit interference fringe" }
      ],
      "C — HL only": [
        { ref: "C.1", t: "SHM displacement & velocity", f: "x = x" + sub("0") + " sin(ωt+φ) ; v = ±ω" + root("x" + sub("0") + sup("2") + "−x" + sup("2")), k: "shm displacement velocity amplitude" },
        { ref: "C.1", t: "SHM energy", f: "E" + sub("k") + " = " + frac("1", "2") + "mω" + sup("2") + "(x" + sub("0") + sup("2") + "−x" + sup("2") + ") ; E" + sub("p") + " = " + frac("1", "2") + "mω" + sup("2") + "x" + sup("2"), k: "shm energy kinetic potential" },
        { ref: "C.3", t: "Diffraction grating", f: "d sinθ = nλ", k: "diffraction grating order" },
        { ref: "C.5", t: "Doppler effect", f: "f′ = f(" + frac("v", "v±v" + sub("s")) + ")  [source] ; f′ = f(" + frac("v±v" + sub("o"), "v") + ")  [observer]", k: "doppler effect frequency moving" }
      ],
      "D — Fields": [
        { ref: "D.1", t: "Newton's law of gravitation", f: "F = " + frac("G m" + sub("1") + "m" + sub("2"), "r" + sup("2")), k: "gravitation newton field" },
        { ref: "D.1", t: "Gravitational field strength", f: "g = " + frac("F", "m") + " = " + frac("GM", "r" + sup("2")), k: "gravitational field strength" },
        { ref: "D.2", t: "Coulomb's law", f: "F = " + frac("k q" + sub("1") + "q" + sub("2"), "r" + sup("2")) + "  (k=" + frac("1", "4πε" + sub("0")) + ")", k: "coulomb electric force charge" },
        { ref: "D.2", t: "Electric field & potential difference", f: "E = " + frac("F", "q") + " = " + frac("V", "d"), k: "electric field voltage potential" },
        { ref: "D.3", t: "Motion in EM fields", f: "F = qvB sinθ ; F = BIL sinθ", k: "magnetic lorentz force current" },
        { ref: "D.3", t: "Force between wires", f: frac("F", "L") + " = " + frac("μ" + sub("0") + "I" + sub("1") + "I" + sub("2"), "2πd"), k: "force parallel wires magnetic" }
      ],
      "D — HL only": [
        { ref: "D.1", t: "Gravitational potential energy", f: "E" + sub("p") + " = −" + frac("G m" + sub("1") + "m" + sub("2"), "r"), k: "gravitational potential energy" },
        { ref: "D.1", t: "Gravitational potential", f: "V" + sub("g") + " = −" + frac("GM", "r") + " ; g = −" + frac("ΔV" + sub("g"), "Δr"), k: "gravitational potential" },
        { ref: "D.1", t: "Escape & orbital speed", f: "v" + sub("esc") + " = " + root(frac("2GM", "r")) + " ; v" + sub("orb") + " = " + root(frac("GM", "r")), k: "escape orbital velocity speed" },
        { ref: "D.2", t: "Electric potential energy", f: "E" + sub("p") + " = " + frac("k q" + sub("1") + "q" + sub("2"), "r") + " ; V" + sub("e") + " = " + frac("kQ", "r"), k: "electric potential energy voltage" },
        { ref: "D.4", t: "Electromagnetic induction", f: "Φ = BA cosθ ; ε = −N" + frac("ΔΦ", "Δt") + " = BvL", k: "faraday induction emf flux" }
      ],
      "E — Nuclear & quantum": [
        { ref: "E.1", t: "Photon energy", f: "E = hf", k: "photon energy planck" },
        { ref: "E.3", t: "Mass–energy equivalence", f: "E = mc" + sup("2"), k: "mass energy equivalence" },
        { ref: "E.5", t: "Stellar distance (parsec)", f: "d(pc) = " + frac("1", "p(arcsec)"), k: "parsec stellar distance" }
      ],
      "E — HL only": [
        { ref: "E.1", t: "Atomic energy levels", f: "R = R" + sub("0") + "A" + sup("1/3") + " ; E" + sub("n") + " = −" + frac("13.6 eV", "n" + sup("2")), k: "bohr atomic energy level radius" },
        { ref: "E.1", t: "Quantised orbit", f: "mvr = " + frac("nh", "2π"), k: "quantised orbit angular momentum" },
        { ref: "E.2", t: "Photoelectric & de Broglie", f: "E" + sub("max") + " = hf − Φ ; λ = " + frac("h", "p"), k: "photoelectric de broglie wavelength" },
        { ref: "E.2", t: "Heisenberg uncertainty", f: "Δx Δp ≥ " + frac("h", "4π"), k: "uncertainty principle heisenberg" },
        { ref: "E.3", t: "Radioactive decay", f: "N = N" + sub("0") + "e" + sup("−λt") + " ; A = λN", k: "radioactive decay activity" },
        { ref: "E.3", t: "Half-life", f: "T" + sub("½") + " = " + frac("ln 2", "λ"), k: "half life decay constant" }
      ]
    }
  };

  // ---- scientific calculator: tokenizer + shunting-yard + RPN evaluator ------
  function fact(n) {
    if (n < 0 || !isFinite(n) || Math.floor(n) !== n) throw new Error("need integer");
    var r = 1;
    for (var i = 2; i <= n; i++) r *= i;
    return r;
  }
  function norm(s) {
    return String(s)
      .replace(/×/g, "*").replace(/÷/g, "/")
      .replace(/π/g, "pi").replace(/−/g, "-")
      .replace(/√/g, "sqrt").replace(/Ans/g, String(ANS === null ? 0 : ANS));
  }
  var ANS = null;
  var MEM = null;
  function calcEval(expr, deg) {
    var s = norm(expr).replace(/\s+/g, "");
    if (!s) throw new Error("empty");
    var tokens = [], i = 0;
    while (i < s.length) {
      var c = s[i];
      if ((c >= "0" && c <= "9") || c === ".") {
        var j = i + 1;
        while (j < s.length && ((s[j] >= "0" && s[j] <= "9") || s[j] === ".")) j++;
        tokens.push({ t: "num", v: parseFloat(s.slice(i, j)) }); i = j;
      } else if (/[a-zA-Z]/.test(c)) {
        var k = i + 1;
        while (k < s.length && /[a-zA-Z]/.test(s[k])) k++;
        var name = s.slice(i, k).toLowerCase();
        if (name === "pi") tokens.push({ t: "num", v: Math.PI });
        else if (name === "e") tokens.push({ t: "num", v: Math.E });
        else tokens.push({ t: "name", v: name });
        i = k;
      } else if ("+-*/^%()!,".indexOf(c) >= 0) {
        tokens.push({ t: "op", v: c }); i++;
      } else throw new Error("bad char " + c);
    }
    // Implicit multiplication: insert "*" between (num or ")") and (num / name / "(").
    var imp = [];
    for (var ti = 0; ti < tokens.length; ti++) {
      imp.push(tokens[ti]);
      var cur = tokens[ti], nxt = tokens[ti + 1];
      if (!nxt) continue;
      var left = (cur.t === "num" || (cur.t === "op" && cur.v === ")"));
      var right = (nxt.t === "num" || nxt.t === "name" || (nxt.t === "op" && nxt.v === "("));
      if (left && right) imp.push({ t: "op", v: "*" });
    }
    tokens = imp;

    // Unary minus/plus: tighter than * (2*-3 = 2·(-3)) but looser than ^
    // (-2^2 = -(2^2)), matching the standard math convention.
    var prec = { "+": 2, "-": 2, "*": 3, "/": 3, "%": 3, "^": 5, "-u": 4, "+u": 4 };
    var right = { "^": true };
    var out = [], ops = [], prev = null;
    function isUnary(tk) {
      if (prev === null) return true;
      if (prev.t === "num") return false;
      if (prev.t === "op" && prev.v === ")") return false;
      return true; // after "(" or any operator / function name
    }
    for (var n = 0; n < tokens.length; n++) {
      var tk = tokens[n];
      if (tk.t === "num") out.push(tk);
      else if (tk.t === "name") ops.push(tk);
      else if (tk.v === "(") ops.push(tk);
      else if (tk.v === ")") {
        while (ops.length && ops[ops.length - 1].v !== "(") out.push(ops.pop());
        if (!ops.length) throw new Error("mismatch");
        ops.pop();
        if (ops.length && ops[ops.length - 1].t === "name") out.push(ops.pop());
      } else if (tk.v === "!") {
        out.push(tk); // postfix unary: output immediately
      } else if (tk.v === ",") {
        // argument separator: reduce operators down to the enclosing "("
        while (ops.length && ops[ops.length - 1].v !== "(") out.push(ops.pop());
      } else {
        var unary = isUnary(tk);
        if (unary) {
          ops.push({ t: "op", v: tk.v + "u" });
        } else {
          while (ops.length) {
            var top = ops[ops.length - 1];
            if (top.t === "op" && top.v !== "(") {
              var p1 = prec[tk.v], p2 = prec[top.v];
              if (p2 > p1 || (p2 === p1 && !right[tk.v])) { out.push(ops.pop()); continue; }
            }
            break;
          }
          ops.push(tk);
        }
      }
      prev = tk;
    }
    while (ops.length) {
      var o = ops.pop();
      if (o.v === "(" || o.v === ")") throw new Error("mismatch");
      out.push(o);
    }
    var st = [];
    for (var m = 0; m < out.length; m++) {
      var t = out[m];
      if (t.t === "num") st.push(t.v);
      else if (t.v === "+") { var b = st.pop(), a = st.pop(); st.push(a + b); }
      else if (t.v === "-") { var b2 = st.pop(), a2 = st.pop(); st.push(a2 - b2); }
      else if (t.v === "*") { var b3 = st.pop(), a3 = st.pop(); st.push(a3 * b3); }
      else if (t.v === "/") { var b4 = st.pop(), a4 = st.pop(); st.push(a4 / b4); }
      else if (t.v === "%") { var b5 = st.pop(), a5 = st.pop(); st.push(a5 % b5); }
      else if (t.v === "^") { var b6 = st.pop(), a6 = st.pop(); st.push(Math.pow(a6, b6)); }
      else if (t.v === "-u") st.push(-st.pop());
      else if (t.v === "+u") { /* no-op */ }
      else if (t.v === "!") { st.push(fact(st.pop())); }
      else if (t.t === "name") {
        var fn = t.v;
        if (fn === "npr" || fn === "ncr") {
          var pb = st.pop(), pa = st.pop();
          st.push(fn === "npr" ? fact(pa) / fact(pa - pb) : fact(pa) / (fact(pb) * fact(pa - pb)));
          continue;
        }
        if (fn === "nrt") { var rb = st.pop(), ra = st.pop(); st.push(Math.pow(ra, 1 / rb)); continue; }
        var x = st.pop(), r, ang = deg ? x * Math.PI / 180 : x;
        switch (fn) {
          case "sin": r = Math.sin(ang); break;
          case "cos": r = Math.cos(ang); break;
          case "tan": r = Math.tan(ang); break;
          case "asin": r = deg ? Math.asin(x) * 180 / Math.PI : Math.asin(x); break;
          case "acos": r = deg ? Math.acos(x) * 180 / Math.PI : Math.acos(x); break;
          case "atan": r = deg ? Math.atan(x) * 180 / Math.PI : Math.atan(x); break;
          case "ln": r = Math.log(x); break;
          case "log": r = Math.log10(x); break;
          case "lb": r = Math.log2(x); break;
          case "sqrt": r = Math.sqrt(x); break;
          case "cbrt": r = Math.cbrt(x); break;
          case "exp": r = Math.exp(x); break;
          case "abs": r = Math.abs(x); break;
          case "inv": r = 1 / x; break;
          case "sec": r = 1 / Math.cos(ang); break;
          case "csc": r = 1 / Math.sin(ang); break;
          case "cot": r = 1 / Math.tan(ang); break;
          case "sinh": r = Math.sinh(x); break;
          case "cosh": r = Math.cosh(x); break;
          case "tanh": r = Math.tanh(x); break;
          default: throw new Error("unknown " + fn);
        }
        st.push(r);
      }
    }
    if (st.length !== 1) throw new Error("syntax");
    return st[0];
  }
  function fmtNum(r) {
    if (typeof r !== "number") return "Error";
    if (!isFinite(r)) return r > 0 ? "∞" : (r < 0 ? "−∞" : "Error");
    if (Number.isInteger(r)) return String(r);
    var s = r.toPrecision(12).replace(/\.?0+$/, "");
    return s;
  }

  // ---- build the DOM --------------------------------------------------------
  if (document.getElementById("dp-tools-root")) return;
  var styles = [
    // Launch buttons are injected into the AI/Sites launch cluster (so the
    // Formula + Calc bars sit right next to Ask AI and Sites). This standalone
    // cluster is only used as a fallback if that cluster is somehow absent.
    ".dp-tools-launch{position:fixed;right:18px;bottom:18px;z-index:2147483000;display:flex;align-items:center;gap:10px}",
    ".dp-tools-btn{display:flex;align-items:center;gap:7px;padding:11px 14px;border:1px solid #d8dfeb;border-radius:999px;",
    "background:#fff;color:#334155;font:600 13px/1 -apple-system,Segoe UI,Roboto,Arial,sans-serif;cursor:pointer;",
    "box-shadow:0 4px 14px rgba(16,24,40,.12);transition:transform .15s ease,border-color .15s ease,color .15s ease}",
    ".dp-tools-btn:hover{transform:translateY(-2px);border-color:#3653d6;color:#3653d6}",
    ".dp-tools-btn .ic{font-size:14px;line-height:1}",
    // shared panel chrome
    ".dp-tools-panel{position:fixed;right:18px;bottom:78px;z-index:2147483002;width:min(440px,calc(100vw - 36px));",
    "height:min(660px,calc(100vh - 96px));display:none;flex-direction:column;background:#fff;border:1px solid #e3e8f0;",
    "border-radius:16px;overflow:hidden;box-shadow:0 18px 50px rgba(16,24,40,.18);font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#151923}",
    ".dp-tools-panel.open{display:flex}",
    ".dp-tools-head{display:flex;align-items:center;gap:8px;padding:13px 14px;background:linear-gradient(135deg,#3653d6,#5b73e8);color:#fff}",
    ".dp-tools-head h3{margin:0;font-size:15px;font-weight:700;flex:1}",
    ".dp-tools-head .tg{margin-left:auto;display:flex;gap:6px;align-items:center}",
    ".dp-tools-head button{background:rgba(255,255,255,.15);border:none;color:#fff;min-width:28px;height:28px;border-radius:8px;cursor:pointer;font-size:13px;line-height:1;padding:0 8px}",
    ".dp-tools-head button:hover{background:rgba(255,255,255,.28)}",
    ".dp-tools-head .seg{display:flex;gap:0;background:rgba(255,255,255,.15);border-radius:8px;overflow:hidden}",
    ".dp-tools-head .seg button{border-radius:0;background:transparent;min-width:auto;padding:0 10px;height:28px;font-weight:600}",
    ".dp-tools-head .seg button.on{background:rgba(255,255,255,.32)}",
    // ---- formula booklet ----
    ".dp-fb-search{display:block;width:100%;box-sizing:border-box;padding:9px 12px;border:none;border-bottom:1px solid #eef1f6;font:14px -apple-system,Segoe UI,Roboto,Arial,sans-serif;outline:none}",
    ".dp-fb-search:focus{border-bottom-color:#3653d6}",
    ".dp-fb-topic{display:block;width:100%;box-sizing:border-box;padding:8px 12px;border:none;border-bottom:1px solid #eef1f6;background:#fafbfd;font:13px -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#334155;outline:none;cursor:pointer}",
    ".dp-fb-body{flex:1;min-height:0;overflow-y:auto;padding:10px 12px 16px;background:#fafbfd}",
    ".dp-fb-group-lab{display:block;font-size:10px;font-weight:800;color:#8b93a7;text-transform:uppercase;letter-spacing:.06em;margin:12px 2px 6px}",
    ".dp-fb-item{border:1px solid #e6eaf3;border-radius:10px;background:#fff;margin-bottom:7px;overflow:hidden}",
    ".dp-fb-item .t{font-size:11.5px;font-weight:700;color:#3653d6;padding:6px 11px 0}",
    ".dp-fb-item .t .ref{font-size:9.5px;font-weight:600;color:#9aa3b5;margin-left:6px}",
    ".dp-fb-item .f{padding:4px 11px 10px;font-size:15px;line-height:1.7;color:#1d2436;text-align:center}",
    ".dp-fb-empty{color:#8b93a7;font-size:13px;text-align:center;padding:30px 10px}",
    // formula typesetting helpers
    ".fb-frac{display:inline-flex;flex-direction:column;text-align:center;vertical-align:middle;margin:0 .12em;line-height:1.05}",
    ".fb-frac .fb-n{display:block;padding:0 .4em}",
    ".fb-frac .fb-d{display:block;padding:0 .4em;border-top:1.5px solid currentColor}",
    ".fb-rad{display:inline-block;border-top:1.5px solid currentColor;padding:0 .28em;margin-left:.08em;vertical-align:middle}",
    // ---- calculator ----
    ".dp-cal-body{flex:1;min-height:0;display:flex;flex-direction:column;padding:12px;background:#fafbfd}",
    ".dp-cal-res{text-align:right;font-size:13px;color:#6c7788;min-height:18px;padding:0 4px;word-break:break-all}",
    ".dp-cal-expr{width:100%;box-sizing:border-box;text-align:right;font:600 22px/1.3 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;",
    "border:1px solid #ccd5e4;border-radius:10px;padding:8px 12px;margin:6px 0 10px;outline:none;color:#151923;background:#fff}",
    ".dp-cal-expr:focus{border-color:#3653d6;box-shadow:0 0 0 3px #eef1ff}",
    ".dp-cal-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:6px;flex:1;overflow-y:auto;align-content:start}",
    ".dp-cal-grid button{border:1px solid #d8dfeb;background:#fff;color:#151923;border-radius:10px;font:600 14px -apple-system,Segoe UI,Roboto,Arial,sans-serif;cursor:pointer;padding:9px 0;transition:background .1s,border-color .1s}",
    ".dp-cal-grid button:hover{background:#f1f4fb;border-color:#3653d6}",
    ".dp-cal-grid button:active{background:#e6ecfb}",
    ".dp-cal-grid button.op{background:#eef1ff;color:#2a44b8;border-color:#dbe2ff}",
    ".dp-cal-grid button.fn{background:#f3f6fb;color:#334155}",
    ".dp-cal-grid button.eq{background:linear-gradient(135deg,#3653d6,#5b73e8);color:#fff;border-color:transparent}",
    ".dp-cal-grid button.util{background:#fff;color:#b02a1f}",
    ".dp-cal-note{font-size:10px;color:#8b93a7;text-align:center;margin-top:7px;line-height:1.4}"
  ].join("");

  var styleEl = document.createElement("style");
  styleEl.textContent = styles +
    // Fixed-position launcher and panels: hide them from print / Save-as-PDF so
    // a printed question sheet is the paper only.
    "@media print{#dp-tools-root{display:none !important}}";
  document.head.appendChild(styleEl);

  var root = document.createElement("div");
  root.id = "dp-tools-root";
  root.innerHTML =
    // --- formula booklet panel ---
    '<div class="dp-tools-panel" id="dpFbPanel" role="dialog" aria-label="Formula booklet">' +
      '<div class="dp-tools-head">' +
        '<h3>Formula Booklet</h3>' +
        '<div class="tg"><div class="seg" id="dpFbSeg">' +
          '<button type="button" data-cat="Mathematics AA HL" class="on">Math</button>' +
          '<button type="button" data-cat="Physics HL">Physics</button>' +
        '</div><button id="dpFbClose" aria-label="Close">\u00d7</button></div>' +
      '</div>' +
      '<input class="dp-fb-search" id="dpFbSearch" type="text" placeholder="Search formulas\u2026" aria-label="Search formulas">' +
      '<select class="dp-fb-topic" id="dpFbTopic" aria-label="Filter by topic"></select>' +
      '<div class="dp-fb-body" id="dpFbBody"></div>' +
    '</div>' +

    // --- calculator panel ---
    '<div class="dp-tools-panel" id="dpCalPanel" role="dialog" aria-label="Scientific calculator">' +
      '<div class="dp-tools-head">' +
        '<h3>Calculator</h3>' +
        '<div class="tg"><div class="seg" id="dpCalMode">' +
          '<button type="button" data-deg="1" class="on">DEG</button>' +
          '<button type="button" data-deg="0">RAD</button>' +
        '</div><button id="dpCalClose" aria-label="Close">\u00d7</button></div>' +
      '</div>' +
      '<div class="dp-cal-body">' +
        '<div class="dp-cal-res" id="dpCalRes"></div>' +
        '<input class="dp-cal-expr" id="dpCalExpr" type="text" inputmode="text" placeholder="0" aria-label="Calculator expression" autocomplete="off">' +
        '<div class="dp-cal-grid" id="dpCalGrid"></div>' +
        '<div class="dp-cal-note">fx: sin cos tan asin acos atan ln log lb(=log₂) √ ∛ ⁿ√(a,b) x² x³ π e 10ˣ eˣ 1/x |x| sec csc cot nPr(a,b) nCr(a,b) x! %. Implicit × via 2π, (2)(3). Ans = last result; M stores, MR recalls.</div>' +
      '</div>' +
    '</div>';
  document.body.appendChild(root);

  // Mount the two launch buttons into the AI/Sites launch cluster so the
  // Formula + Calc bars sit directly next to Ask AI and Sites. If that cluster
  // is missing for any reason, fall back to a standalone cluster at bottom-right.
  var TOOLS_BTNS =
    '<button class="dp-tools-btn" id="dpFbBtn" aria-label="Open formula booklet" aria-expanded="false">' +
      '<span class="ic">\u{1F4D8}</span><span>Formula</span>' +
    '</button>' +
    '<button class="dp-tools-btn" id="dpCalBtn" aria-label="Open calculator" aria-expanded="false">' +
      '<span class="ic">\u{1F9EE}</span><span>Calc</span>' +
    '</button>';
  var aiLaunch = document.querySelector(".dp-ai-launch");
  var tlaunch = aiLaunch || document.createElement("div");
  if (!aiLaunch) {
    tlaunch.className = "dp-tools-launch";
    document.body.appendChild(tlaunch);
  }
  tlaunch.insertAdjacentHTML("beforeend", TOOLS_BTNS);

  // ---- formula booklet logic ----
  var fbBtn = document.getElementById("dpFbBtn");
  var fbPanel = document.getElementById("dpFbPanel");
  var fbBody = document.getElementById("dpFbBody");
  var fbSearch = document.getElementById("dpFbSearch");
  var fbSeg = document.getElementById("dpFbSeg");
  var fbTopic = document.getElementById("dpFbTopic");
  var fbClose = document.getElementById("dpFbClose");
  var fbCat = "Mathematics AA HL";

  function fillTopics() {
    var groups = FORMULAS[fbCat];
    var opts = ['<option value="__all__">All topics</option>'];
    Object.keys(groups).forEach(function (t) { opts.push('<option value="' + t + '">' + t + '</option>'); });
    fbTopic.innerHTML = opts.join("");
  }
  function renderFormulas() {
    var q = fbSearch.value.trim().toLowerCase();
    var groups = FORMULAS[fbCat];
    var topic = fbTopic.value || "__all__";
    var html = "";
    Object.keys(groups).forEach(function (g) {
      if (topic !== "__all__" && topic !== g) return;
      var items = groups[g];
      var shown = items.filter(function (it) {
        return !q || (it.t + " " + (it.ref || "") + " " + it.k).toLowerCase().indexOf(q) !== -1;
      });
      if (!shown.length) return;
      html += '<div class="dp-fb-group-lab">' + g + '</div>';
      shown.forEach(function (it) {
        html += '<div class="dp-fb-item"><div class="t">' + it.t +
          (it.ref ? ' <span class="ref">' + it.ref + '</span>' : '') +
          '</div><div class="f">' + it.f + '</div></div>';
      });
    });
    if (!html) html = '<div class="dp-fb-empty">No formulas match \u201c' + q + '\u201d.</div>';
    fbBody.innerHTML = html;
  }
  fbSeg.addEventListener("click", function (e) {
    var b = e.target.closest("button[data-cat]");
    if (!b) return;
    fbCat = b.getAttribute("data-cat");
    fbSeg.querySelectorAll("button").forEach(function (x) { x.classList.toggle("on", x === b); });
    fillTopics();
    renderFormulas();
  });
  fbSearch.addEventListener("input", renderFormulas);
  fbTopic.addEventListener("change", renderFormulas);

  // ---- calculator logic ----
  var calBtn = document.getElementById("dpCalBtn");
  var calPanel = document.getElementById("dpCalPanel");
  var calExpr = document.getElementById("dpCalExpr");
  var calRes = document.getElementById("dpCalRes");
  var calGrid = document.getElementById("dpCalGrid");
  var calMode = document.getElementById("dpCalMode");
  var calClose = document.getElementById("dpCalClose");
  var deg = true;

  // button layout: [label, kind, insertText?]
  var CAL_KEYS = [
    ["sin", "fn", "sin("], ["cos", "fn", "cos("], ["tan", "fn", "tan("], ["asin", "fn", "asin("], ["acos", "fn", "acos("],
    ["atan", "fn", "atan("], ["ln", "fn", "ln("], ["log", "fn", "log("], ["log₂", "fn", "lb("], ["xʸ", "fn", "^( "],
    ["√", "fn", "sqrt("], ["∛", "fn", "cbrt("], ["ⁿ√", "fn", "nrt("], ["x²", "fn", "^(2)"], ["x³", "fn", "^(3)"],
    ["π", "fn", "π"], ["e", "fn", "e"], ["10ˣ", "fn", "10^("], ["eˣ", "fn", "e^("], ["1/x", "fn", "inv("],
    ["|x|", "fn", "abs("], ["sec", "fn", "sec("], ["csc", "fn", "csc("], ["cot", "fn", "cot("], ["x!", "fn", "!"],
    ["nPr", "fn", "nPr("], ["nCr", "fn", "nCr("], ["(", "op", "("], [")", "op", ")"], ["⌫", "util", "back"],
    ["7", "", "7"], ["8", "", "8"], ["9", "", "9"], ["÷", "op", "÷"], ["AC", "util", "clear"],
    ["4", "", "4"], ["5", "", "5"], ["6", "", "6"], ["×", "op", "×"], ["%", "op", "%"],
    ["1", "", "1"], ["2", "", "2"], ["3", "", "3"], ["−", "op", "−"], ["M", "util", "store"],
    ["0", "", "0"], [".", "", "."], ["Ans", "fn", "Ans"], ["+", "op", "+"], ["MR", "util", "recall"],
    ["=", "eq", "eq"]
  ];
  CAL_KEYS.forEach(function (k) {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = k[1] || "";
    btn.textContent = k[0];
    btn.addEventListener("click", function () { calKey(k[2]); });
    calGrid.appendChild(btn);
  });

  function insertAtCursor(t) {
    if (t === "back") {
      var s = calExpr.selectionStart, e = calExpr.selectionEnd, v = calExpr.value;
      if (s === e && s > 0) { calExpr.value = v.slice(0, s - 1) + v.slice(s); calExpr.selectionStart = calExpr.selectionEnd = s - 1; }
      else { calExpr.value = v.slice(0, s) + v.slice(e); calExpr.selectionStart = calExpr.selectionEnd = s; }
      return;
    }
    if (t === "clear") { calExpr.value = ""; calRes.textContent = ""; return; }
    if (t === "store") {
      if (ANS === null) { calRes.textContent = "No Ans yet"; return; }
      MEM = ANS; calRes.textContent = "M = " + fmtNum(MEM); return;
    }
    if (t === "recall") { t = (MEM === null ? "0" : String(MEM)); }
    if (t === "eq") { evaluate(); return; }
    var s2 = calExpr.selectionStart, e2 = calExpr.selectionEnd, v2 = calExpr.value;
    calExpr.value = v2.slice(0, s2) + t + v2.slice(e2);
    calExpr.selectionStart = calExpr.selectionEnd = s2 + t.length;
    calExpr.focus();
  }
  function calKey(t) { insertAtCursor(t); }

  function evaluate() {
    var raw = calExpr.value;
    if (!raw.trim()) return;
    try {
      var r = calcEval(raw, deg);
      if (typeof r !== "number" || isNaN(r)) { calRes.textContent = "Error"; return; }
      ANS = r;
      calRes.textContent = fmtNum(r);
    } catch (err) {
      calRes.textContent = "Error";
    }
  }

  calExpr.addEventListener("keydown", function (e) {
    if (e.key === "Enter") { e.preventDefault(); evaluate(); }
    else if (e.key === "=") { e.preventDefault(); evaluate(); }
  });
  calMode.addEventListener("click", function (e) {
    var b = e.target.closest("button[data-deg]");
    if (!b) return;
    deg = b.getAttribute("data-deg") === "1";
    calMode.querySelectorAll("button").forEach(function (x) { x.classList.toggle("on", x === b); });
  });

  // ---- open / close wiring ----
  function openFb() { calPanel.classList.remove("open"); calBtn.setAttribute("aria-expanded", "false"); fbPanel.classList.add("open"); fbBtn.setAttribute("aria-expanded", "true"); fbSearch.focus(); }
  function closeFb() { fbPanel.classList.remove("open"); fbBtn.setAttribute("aria-expanded", "false"); }
  function openCal() { fbPanel.classList.remove("open"); fbBtn.setAttribute("aria-expanded", "false"); calPanel.classList.add("open"); calBtn.setAttribute("aria-expanded", "true"); calExpr.focus(); }
  function closeCal() { calPanel.classList.remove("open"); calBtn.setAttribute("aria-expanded", "false"); }

  fbBtn.addEventListener("click", function () { fbPanel.classList.contains("open") ? closeFb() : openFb(); });
  calBtn.addEventListener("click", function () { calPanel.classList.contains("open") ? closeCal() : openCal(); });
  fbClose.addEventListener("click", closeFb);
  calClose.addEventListener("click", closeCal);

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (fbPanel.classList.contains("open")) closeFb();
    else if (calPanel.classList.contains("open")) closeCal();
  });

  // first paint
  fillTopics();
  renderFormulas();
})();
