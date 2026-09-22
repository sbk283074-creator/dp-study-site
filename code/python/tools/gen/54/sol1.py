"""Chapter 54 -- practice 1.

A field-validation chain and the table that replaces it. The chain's
last branch is a default, and the default is what an unknown field gets.
"""

import pathlib

KNOWN = ["email", "age", "postcode", "phone", "name"]
UNKNOWN = ["nickname", "tax_id", "referrer"]


# --- chain
def validate_chain(field, value, count):
    count[0] = 0

    count[0] += 1
    if field == "email":
        return "@" in value

    count[0] += 1
    if field == "age":
        return value.isdigit() and 0 <= int(value) < 130

    count[0] += 1
    if field == "postcode":
        return len(value) == 6

    count[0] += 1
    if field == "phone":
        return value.startswith("+")

    count[0] += 1
    if field == "name":
        return len(value) > 0

    return True


# --- table
def check_email(value):
    return "@" in value


def check_age(value):
    return value.isdigit() and 0 <= int(value) < 130


def check_postcode(value):
    return len(value) == 6


def check_phone(value):
    return value.startswith("+")


def check_name(value):
    return len(value) > 0


CHECKS = {
    "email": check_email,
    "age": check_age,
    "postcode": check_postcode,
    "phone": check_phone,
    "name": check_name,
}


def validate_table(field, value, count):
    count[0] = 1
    try:
        return CHECKS[field](value)
    except KeyError:
        raise ValueError("unknown field: " + field) from None
# --- end


SOURCE = pathlib.Path(__file__).read_text(encoding="utf-8")
CHAIN_SRC = SOURCE.split("# --- chain")[1].split("# --- table")[0]
TABLE_SRC = SOURCE.split("# --- table")[1].split("# --- end")[0]

SAMPLES = {
    "email": "ada@example.com",
    "age": "36",
    "postcode": "123456",
    "phone": "+441234",
    "name": "Ada",
    "nickname": "!! not a name",
    "tax_id": "",
    "referrer": "",
}


def main():
    print(f"  fields the chain knows              {len(KNOWN)}")
    print(f"  fields it does not                  {len(UNKNOWN)}")
    print(f"  lines in the chain region           "
          f"{len(CHAIN_SRC.strip().splitlines())}")
    print(f"  lines in the table region           "
          f"{len(TABLE_SRC.strip().splitlines())}")
    print()

    print("    field          value              chain   table")
    chain_total = 0
    for field in KNOWN + UNKNOWN:
        count = [0]
        chain = validate_chain(field, SAMPLES[field], count)
        chain_total += count[0]
        count = [0]
        try:
            table = validate_table(field, SAMPLES[field], count)
        except ValueError:
            table = "refused"
        print("    {:<15}{:<19}{:<8}{}".format(
            field, repr(SAMPLES[field])[:18], str(chain), str(table)))
    print()
    print(f"  the chain compares the field name {chain_total} times over "
          f"{len(KNOWN) + len(UNKNOWN)} calls")
    print(f"  and the table compares it once per call, which is the column")
    print("  everybody looks at.")
    print()
    accepted = [f for f in UNKNOWN if validate_chain(f, SAMPLES[f], [0])]
    print(f"  the column that matters is the three fields the chain does not")
    print(f"  know, and the chain accepted {len(accepted)} of them: "
          f"{', '.join(accepted)}.")
    print("  a validator that returns `True` for a field it has never heard of")
    print("  is a validator that will accept any field a later release adds to")
    print("  the form, and nothing anywhere reports it -- the value is")
    print("  validated, the request succeeds, and the only signal is that no")
    print("  error appeared.")
    print()
    print("  the table refuses all three, because a missing key is a")
    print("  `KeyError` and the code turns it into a `ValueError`. the")
    print("  difference between the two shapes is not the comparison count")
    print("  and it is not the line count -- the table region is the longer of")
    print("  the two. it is that a chain has a last branch and whatever it")
    print("  returns is the answer for everything not listed above it.")


main()
