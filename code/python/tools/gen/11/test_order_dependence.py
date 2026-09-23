"""Chapter 11 -- a test that passes or fails depending on what ran before it.

Five tests over one piece of module-level state, run in three orders. The count
is of failures, and the result is that the same five tests fail once in two of
the orders and twice in the third -- which is the definition of an
order-dependent suite.
"""

STATE = {"loaded": False}


def test_loads_the_data():
    STATE["loaded"] = True


def test_uses_the_data():
    assert STATE["loaded"], "the data was not loaded"


def test_resets_the_state():
    STATE["loaded"] = False


def test_uses_the_data_again():
    assert STATE["loaded"], "the data was not loaded"


def test_is_independent():
    assert 1 + 1 == 2


TESTS = [
    ("loads", test_loads_the_data),
    ("uses", test_uses_the_data),
    ("resets", test_resets_the_state),
    ("uses again", test_uses_the_data_again),
    ("independent", test_is_independent),
]

ORDERS = [
    ["loads", "uses", "resets", "uses again", "independent"],
    ["resets", "uses", "loads", "uses again", "independent"],
    ["uses", "uses again", "independent", "loads", "resets"],
]

by_name = dict(TESTS)

print(f"{len(TESTS)} tests over one piece of module-level state, {len(ORDERS)} orders")
print()
print(f"{'order':<44}{'passed':>8}{'failed':>8}")
print("-" * 60)
for order in ORDERS:
    STATE["loaded"] = False
    passed = 0
    failed = 0
    for name in order:
        try:
            by_name[name]()
            passed += 1
        except AssertionError:
            failed += 1
    print(f"{' -> '.join(order):<44}{passed:>8}{failed:>8}")

print()
print("The same five tests fail once in two of the orders and twice in the")
print("third, and the state they share is the reason. `uses` passes when")
print("`loads` ran before it and fails when it did not, so the test is not")
print("testing the code -- it is testing the order.")
print()
print("The failure count is the useful part of this. A suite whose result")
print("depends on the order is a suite you cannot trust in either direction:")
print("the green run does not mean the code is right, and the red run does not")
print("mean it is broken. Both are reporting on what ran before.")
print()
print("The fix is not to sort the tests. It is to give each one its own state,")
print("so that the count is the same in every order -- and the way to know you")
print("have done it is to run the suite in a shuffled order and check that the")
print("number does not move.")
