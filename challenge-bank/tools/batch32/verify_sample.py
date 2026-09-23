"""Independent verification of every number in the sample item MATH-P3-013.

Nothing here reuses the closed form to check itself: the integrals are computed by
composite Simpson quadrature on the *definition* of the integrand, the infinite
sums by adding many lobes numerically, and only then compared against the
algebra the markscheme quotes. This is the `verification.method` the item claims.
"""
import math

f = lambda x, k=1.0: math.exp(-k * x) * math.sin(x)


def simpson(a, b, n, k=1.0):
    if n % 2:
        n += 1
    h = (b - a) / n
    s = f(a, k) + f(b, k)
    for i in range(1, n):
        s += f(a + i * h, k) * (4 if i % 2 else 2)
    return s * h / 3


PI = math.pi
E = math.exp(-PI)

print("=== (a) the first lobe ===")
num = simpson(0, PI, 200000)
exact = (1 + E) / 2
print(f"  quadrature int_0^pi e^-x sin x dx = {num:.12f}")
print(f"  closed form (1+e^-pi)/2           = {exact:.12f}   |diff| = {abs(num-exact):.2e}")
anti = lambda x: -math.exp(-x) * (math.sin(x) + math.cos(x)) / 2
print(f"  antiderivative -e^-x(sin x+cos x)/2 at pi minus at 0 = {anti(PI)-anti(0):.12f}")

print("\n=== (b) the ratio between successive lobe areas ===")
lobes = [abs(simpson(n * PI, (n + 1) * PI, 40000)) for n in range(6)]
print("  lobe areas:", "  ".join(f"{v:.6f}" for v in lobes[:4]))
for i in range(3):
    print(f"  A{i+2}/A{i+1} = {lobes[i+1]/lobes[i]:.12f}   e^-pi = {E:.12f}")
print(f"  signed integral on (pi,2pi) = {simpson(PI,2*PI,40000):.12f}  (negative: the lobe is below the axis)")
print(f"  e^-2pi (the wrong ratio a full period suggests) = {math.exp(-2*PI):.6f}")

print("\n=== (c) the total area ===")
closed = lobes[0] / (1 - E)
partial = sum(lobes)
tail = lobes[-1] * E / (1 - E)
print(f"  GP sum A1/(1-e^-pi)            = {closed:.12f}")
print(f"  six lobes + geometric tail      = {partial + tail:.12f}")
print(f"  (1+e^-pi)/(2(1-e^-pi))          = {(1+E)/(2*(1-E)):.12f}")
frac = [sum(lobes[:n]) / closed for n in (1, 2, 3)]
for n, fr in enumerate(frac, 1):
    print(f"  first {n} lobe(s) = {100*fr:.4f}% of the total   (1-e^-{n}pi = {100*(1-math.exp(-n*PI)):.4f}%)")
print(f"  smallest N over 99%: {[n for n in range(1,6) if 1-math.exp(-n*PI) > 0.99][0]}")

print("\n=== (d) net integral versus total area ===")
net_num = simpson(0, 60 * PI, 400000)
print(f"  quadrature int_0^inf (signed) = {net_num:.12f}   1/2 = 0.5")
rel = (closed - 0.5) / closed
print(f"  total area - net = {closed-0.5:.12f}; relative error of quoting 1/2 = {100*rel:.4f}%  -> {rel:.4f}")

print("\n=== the k-family ===")
for kk in (1.0, 0.5, 0.1, 0.02):
    a1 = abs(simpson(0, PI, 40000, kk))
    r = math.exp(-kk * PI)
    tot_k = a1 / (1 - r)
    formula = (1 + r) / ((1 + kk ** 2) * (1 - r))
    net_k = 1 / (1 + kk ** 2)
    print(f"  k={kk:<5} total={tot_k:.8f}  (1+e^-kpi)/((1+k^2)(1-e^-kpi))={formula:.8f}  "
          f"2/(k pi)={2/(kk*PI):.6f}  net=1/(1+k^2)={net_k:.6f}")

print("\n=== 3 s.f. values the markscheme prints ===")
for name, v in [("A1", lobes[0]), ("A2", lobes[1]), ("total", closed), ("e^-pi", E),
                ("rel err %", 100 * rel), ("net", net_num)]:
    print(f"  {name:9s} {v:.6g}")
