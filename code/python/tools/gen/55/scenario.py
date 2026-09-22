"""Chapter 55 -- the scenario. A checkout, wired three ways.

One service, three tests, and a vendor client that cannot be constructed
in a test. The count is of the tests that run, and of the files that name
the vendor.
"""

VENDOR_NAME = "AcmePayClient"


class AcmePayClient:
    """The vendor's client. Constructing it is what a test cannot do,
    and it fails loudly so that the failure is visible rather than
    silent."""

    def __init__(self):
        raise RuntimeError("the vendor client needs a live endpoint")

    def charge(self, amount):
        return "charged " + str(amount)


class StubGateway:
    """What a test supplies instead."""

    def __init__(self):
        self.charged = []

    def charge(self, amount):
        self.charged.append(amount)
        return "stubbed " + str(amount)


class CheckoutOwn:
    """Design A: builds its own gateway."""

    def __init__(self):
        self.gateway = AcmePayClient()

    def pay(self, amount):
        return self.gateway.charge(amount)


class CheckoutInjected:
    """Designs B and C: the gateway arrives."""

    def __init__(self, gateway):
        self.gateway = gateway

    def pay(self, amount):
        return self.gateway.charge(amount)


def charges_the_amount(checkout):
    return checkout.pay(10) == "stubbed 10"


def returns_a_string(checkout):
    return isinstance(checkout.pay(10), str)


def charges_twice(checkout):
    checkout.pay(10)
    checkout.pay(20)
    return True


TESTS = [
    ("the payment goes through", charges_the_amount),
    ("the answer is a string", returns_a_string),
    ("two payments both go", charges_twice),
]

SERVICE_A = """\
from vendor import AcmePayClient


class Checkout:
    def __init__(self):
        self.gateway = AcmePayClient()

    def pay(self, amount):
        return self.gateway.charge(amount)
"""

SERVICE_B = """\
class Checkout:
    def __init__(self, gateway):
        self.gateway = gateway

    def pay(self, amount):
        return self.gateway.charge(amount)
"""

CALLER_B = """\
from vendor import AcmePayClient
from checkout import Checkout


def the_web_route(amount):
    return Checkout(AcmePayClient()).pay(amount)
"""

SERVICE_C = """\
from typing import Protocol


class Gateway(Protocol):
    def charge(self, amount):
        ...


class Checkout:
    def __init__(self, gateway):
        self.gateway = gateway

    def pay(self, amount):
        return self.gateway.charge(amount)
"""

COMPOSITION_C = """\
from checkout import Checkout
from vendor import AcmePayClient

checkout = Checkout(AcmePayClient())
"""

DESIGNS = [
    ("builds its own gateway", [SERVICE_A], CheckoutOwn),
    ("takes one from every caller", [SERVICE_B, CALLER_B, CALLER_B, CALLER_B],
     CheckoutInjected),
    ("takes one, wired in one place",
     [SERVICE_C, COMPOSITION_C], CheckoutInjected),
]


def names(source, name):
    return sum(1 for line in source.splitlines() if name in line)


def main():
    print(f"  call sites                          {len(DESIGNS[1][1]) - 1}")
    print(f"  tests                               {len(TESTS)}")
    print()

    print("    design                        tests that run   files naming the vendor")
    for label, modules, cls in DESIGNS:
        if cls is CheckoutOwn:
            def make():
                return CheckoutOwn()
        else:
            def make():
                return CheckoutInjected(StubGateway())
        ran = 0
        for _, test in TESTS:
            try:
                ran += 1 if test(make()) else 0
            except Exception:
                pass
        files = sum(1 for module in modules if names(module, VENDOR_NAME))
        print("    {:<30}{:<17}{}".format(
            label, "%d of %d" % (ran, len(TESTS)), files))
    print()

    print("    what each design names")
    for label, modules, _ in DESIGNS:
        named = sum(names(module, VENDOR_NAME) for module in modules)
        print("    {:<30}{} reference(s) to the vendor, in {} file(s)".format(
            label, named, sum(1 for m in modules if names(m, VENDOR_NAME))))
    print()
    print("  the first design runs none of the three tests, because the")
    print("  object cannot be built. that is the loudest version of the")
    print("  problem and the easiest to notice.")
    print()
    print("  the second design runs all three and moves the vendor's name out")
    print("  of the service -- into every caller. so the number of files that")
    print("  name the vendor went from one to three, and replacing the vendor")
    print("  now edits three modules instead of one. this is where most")
    print("  refactors stop, because the tests pass and the class looks")
    print("  clean.")
    print()
    print("  the third design is the second one plus a composition root, and")
    print("  it is the only one that gets both counts right: three tests run,")
    print("  and one file names the vendor. the service names an interface it")
    print("  defined itself, the composition root names the vendor, and the")
    print("  callers name neither.")
    print()
    print("  the cost is one new module and one new file, and the thing that")
    print("  decides whether it is worth paying is the count in the middle")
    print("  column. a codebase with one caller does not need a composition")
    print("  root. a codebase with three does, and the number of callers is")
    print("  knowable before the refactor starts.")


main()
