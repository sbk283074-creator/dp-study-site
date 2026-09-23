"""Chapter 59 -- what the key has to contain.

One function whose answer depends on two arguments, cached four ways. The
count is of calls that got an answer computed for different arguments.
"""

ITEMS = 10
CURRENCIES = ["eur", "usd"]
ROUNDS = 2
CALLS = ITEMS * len(CURRENCIES) * ROUNDS
RATES = {"eur": 1, "usd": 2}


def price(item, currency):
    return item * RATES[currency]


def on_the_item(item, currency, cache):
    """The key names one of the two arguments the answer depends on."""
    if item not in cache:
        cache[item] = price(item, currency)
    return cache[item]


def on_both(item, currency, cache):
    if (item, currency) not in cache:
        cache[(item, currency)] = price(item, currency)
    return cache[(item, currency)]


def on_a_string(item, currency, cache):
    """Both arguments, joined into one string."""
    key = "%s-%s" % (item, currency)
    if key not in cache:
        cache[key] = price(item, currency)
    return cache[key]


def on_the_types(item, currency, cache):
    """Both arguments, reduced to what type they are."""
    key = (type(item), type(currency))
    if key not in cache:
        cache[key] = price(item, currency)
    return cache[key]


DESIGNS = [
    ("the item alone", on_the_item),
    ("the item and the currency", on_both),
    ("a string of both", on_a_string),
    ("the type of both", on_the_types),
]


def sequence():
    out = []
    for _round in range(ROUNDS):
        for currency in CURRENCIES:
            for item in range(ITEMS):
                out.append((item, currency))
    return out


def main():
    ops = sequence()
    print(f"  items                               {ITEMS}")
    print(f"  currencies                          {len(CURRENCIES)}")
    print(f"  calls                               {CALLS}")
    print()
    print("    what the key names           misses   hits   wrong   entries")
    results = {}
    for name, design in DESIGNS:
        cache = {}
        misses = 0
        hits = 0
        wrong = 0
        for item, currency in ops:
            before = len(cache)
            value = design(item, currency, cache)
            if len(cache) > before:
                misses += 1
            else:
                hits += 1
            if value != price(item, currency):
                wrong += 1
        results[name] = (misses, hits, wrong, len(cache))
        print("    {:<25}{:>8}{:>7}{:>8}{:>10}".format(
            name, misses, hits, wrong, len(cache)))
    print()

    bad = [name for name, row in results.items() if row[2] > 0]
    item_row = results["the item alone"]
    type_row = results["the type of both"]
    print(f"  {len(bad)} of the {len(DESIGNS)} designs returned an answer computed for different")
    print(f"  arguments, and both of them report an excellent hit rate.")
    print()
    print(f"  `the item alone` is the mistake that looks reasonable. The item is")
    print(f"  the interesting half of the call and the currency feels like a")
    print(f"  detail, so the key names the item and the currency is captured in")
    print(f"  the value. After warm-up it hits on {item_row[1]} of the {CALLS} calls and")
    print(f"  {item_row[2]} of those answers are wrong.")
    print()
    print(f"  `the type of both` is the same mistake taken further, and the table")
    print(f"  shows what taking it further buys: {type_row[1]} hits instead of {item_row[1]}, and")
    print(f"  {type_row[2]} wrong answers instead of {item_row[2]}. A key that names less is a")
    print(f"  cache that hits more and is wrong more, and the two counts move")
    print(f"  together.")
    print()
    print("  the key is not an optimisation. It is the statement of what the")
    print("  cached value depends on, and a cache is correct exactly when that")
    print("  statement is complete. Nothing in either of the wrong designs looks")
    print("  wrong, and no test that calls it with one currency would fail.")
    print()
    print(f"  the other two designs are both right, and they agree on every")
    print(f"  count in the table: {results['the item and the currency'][0]} misses, {results['the item and the currency'][1]} hits, no wrong")
    print(f"  answers. The difference between them appears when a third currency")
    print("  is added. The tuple key needs no change. The string key needs its")
    print("  separator to stay unambiguous, which is a property of the data")
    print("  rather than of the code -- and `eu-r` is a currency code that would")
    print("  break it.")


main()
