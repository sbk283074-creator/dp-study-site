"""Chapter 54 -- the pattern where a function would do.

The same three notification channels, built twice: once as a hierarchy
with a factory, and once as a dictionary of functions. The two are
compared on what they cost and on what each one changes when a fourth
channel arrives.
"""

import pathlib

# --- pattern
class Notifier:
    def send(self, message):
        raise NotImplementedError


class EmailNotifier(Notifier):
    def send(self, message):
        return "email: " + message


class SmsNotifier(Notifier):
    def send(self, message):
        return "sms: " + message


class WebhookNotifier(Notifier):
    def send(self, message):
        return "webhook: " + message


NOTIFIER_TYPES = {
    "email": EmailNotifier,
    "sms": SmsNotifier,
    "webhook": WebhookNotifier,
}


def make_notifier(channel):
    return NOTIFIER_TYPES[channel]()


def notify_pattern(channel, message):
    return make_notifier(channel).send(message)


# --- function
def notify_function(channel, message):
    return CHANNELS[channel](message)


CHANNELS = {
    "email": lambda m: "email: " + m,
    "sms": lambda m: "sms: " + m,
    "webhook": lambda m: "webhook: " + m,
}
# --- end


SOURCE = pathlib.Path(__file__).read_text(encoding="utf-8")
PATTERN_SRC = SOURCE.split("# --- pattern")[1].split("# --- function")[0]
FUNC_SRC = SOURCE.split("# --- function")[1].split("# --- end")[0]

CHANNELS_TESTED = ["email", "sms", "webhook"]
UNKNOWN = ["slack", "pagerduty"]


def count(source, word):
    return sum(1 for line in source.splitlines() if word in line)


def main():
    print(f"  channels                            {len(CHANNELS_TESTED)}")
    print()
    print("    what                          the hierarchy   the dictionary")
    print("    {:<30}{:>13}{:>16}".format(
        "classes", count(PATTERN_SRC, "class "), count(FUNC_SRC, "class ")))
    print("    {:<30}{:>13}{:>16}".format(
        "functions and methods", count(PATTERN_SRC, "def "),
        count(FUNC_SRC, "def ")))
    print("    {:<30}{:>13}{:>16}".format(
        "lines", len(PATTERN_SRC.strip().splitlines()),
        len(FUNC_SRC.strip().splitlines())))
    print()

    for channel in CHANNELS_TESTED:
        same = (notify_pattern(channel, "hi") == notify_function(channel, "hi"))
        if not same:
            print("    the two disagree on " + channel)
    print("  all three channels produce the same string through both, so the")
    print("  two are interchangeable for the behaviour they exist to produce.")
    print()

    print("    an unknown channel                the hierarchy   the dictionary")
    for channel in UNKNOWN:
        outcomes = []
        for fn in (notify_pattern, notify_function):
            try:
                fn(channel, "hi")
                outcomes.append("raised nothing")
            except KeyError:
                outcomes.append("KeyError")
        print("    {:<34}{:<16}{}".format(channel, outcomes[0], outcomes[1]))
    print()
    print("  both refuse an unknown channel, and both refuse it the same way,")
    print("  because both of them end in a dictionary lookup. the hierarchy is")
    print("  a dictionary with four extra names in front of it.")
    print()

    print("    what a fourth channel changes")
    print("    {:<34}{:>10}   {}".format("the hierarchy", "2", "a class and a key"))
    print("    {:<34}{:>10}   {}".format("the dictionary", "1", "a key"))
    print()
    print("  the hierarchy needs a class and a registry entry; the dictionary")
    print("  needs a key. the class is not doing anything the function does not")
    print("  do -- it holds no state, it has one method, and it is constructed")
    print("  and thrown away on every call.")
    print()
    print("  the hierarchy starts paying on the day a notifier needs to")
    print("  remember something: a retry count, a client handle, a rate limit.")
    print("  a function can hold that too, in a closure or in a default")
    print("  argument, and the moment it does, the difference between the two")
    print("  is that one of them is a class and the other is not. that is the")
    print("  whole of what was bought, and it is worth naming before paying")
    print("  for it.")


main()
