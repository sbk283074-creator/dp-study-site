"""Chapter 53 -- session lifecycle.

Five attacks against four settings, and the token generator underneath
them. Each attack is a function run against a store configured four
ways, so each setting shows up as the column where an attack stops
working -- and the attack that survives all four is the one worth
finding.
"""

import random
import string

ALNUM = string.ascii_letters + string.digits


class Store:
    def __init__(self, rotate_login=False, rotate_privilege=False,
                 kill_logout=False, wipe_on_rotate=False):
        self.rotate_login = rotate_login
        self.rotate_privilege = rotate_privilege
        self.kill_logout = kill_logout
        self.wipe_on_rotate = wipe_on_rotate
        self.sessions = {}
        self.n = 0

    def mint(self):
        self.n += 1
        return "s%03d" % self.n

    def login(self, presented, user):
        # the vulnerable step: whatever id the browser brought is the
        # session id, whether or not this server ever issued it
        if self.rotate_login:
            self.sessions.pop(presented, None)
            presented = self.mint()
        self.sessions[presented] = [user, "user"]
        return presented

    def escalate(self, token):
        if token not in self.sessions:
            return None
        if self.rotate_privilege:
            if self.wipe_on_rotate:
                self.sessions.clear()
            else:
                del self.sessions[token]
            token = self.mint()
            self.sessions[token] = ["u1", "admin"]
            return token
        self.sessions[token][1] = "admin"
        return token

    def change_password(self, token):
        # note what is not here. this route exists and does not touch
        # the session store, so nothing that was issued before it stops
        # working.
        return None

    def logout(self, token):
        if self.kill_logout:
            self.sessions.pop(token, None)

    def who(self, token):
        return self.sessions.get(token)


# --- the five attacks -------------------------------------------------
#
# each returns the session the attacker is holding at the end, or None
# if the store no longer honours it

def fixed_before_login(st):
    st.login("attacker-chosen", "u1")
    return st.who("attacker-chosen")


def copied_then_escalated(st):
    v = st.login("v", "u1")
    copy = v
    st.escalate(v)
    return st.who(copy)


def replayed_after_logout(st):
    v = st.login("v", "u1")
    copy = v
    st.logout(v)
    return st.who(copy)


def replayed_after_password_change(st):
    v = st.login("v", "u1")
    copy = v
    st.change_password(v)
    return st.who(copy)


def replayed_after_relogin(st):
    v1 = st.login("v", "u1")
    st.logout(v1)
    st.login("v", "u1")
    return st.who(v1)


ATTACKS = [
    ("fixed before login", fixed_before_login),
    ("copied, then escalated", copied_then_escalated),
    ("replayed after logout", replayed_after_logout),
    ("replayed after a password change", replayed_after_password_change),
    ("replayed after a re-login", replayed_after_relogin),
]

CONFIGS = [
    ("none", {}),
    ("rotate", {"rotate_login": True}),
    ("+priv", {"rotate_login": True, "rotate_privilege": True}),
    ("+logout", {"rotate_login": True, "rotate_privilege": True,
                 "kill_logout": True}),
]


# --- the token generator ----------------------------------------------

def counter_ids(n):
    return ["s%03d" % i for i in range(1, n + 1)]


def random_ids(seed, n):
    rng = random.Random(seed)
    return ["".join(rng.choice(ALNUM) for _ in range(8)) for _ in range(n)]


N = 1000


def main():
    print(f"  attacks                              {len(ATTACKS)}")
    print(f"  settings                             {len(CONFIGS)}")
    print()

    print("    attack                            " +
          "".join("{:>12}".format(name) for name, _ in CONFIGS))
    totals = [0] * len(CONFIGS)
    for label, run in ATTACKS:
        row = "    {:<34}".format(label)
        for i, (_, kwargs) in enumerate(CONFIGS):
            held = run(Store(**kwargs))
            if held:
                totals[i] += 1
                row += "{:>12}".format("attacker in")
            else:
                row += "{:>12}".format("refused")
        print(row)
    print()
    print("    attacks that still work           " +
          "".join("{:>12}".format(n) for n in totals))
    print()

    surviving = [label for label, run in ATTACKS
                 if all(run(Store(**kw)) for _, kw in CONFIGS)]
    print("  each column removes one attack, and the last column still")
    print(f"  leaves {len(surviving)}: `{surviving[0]}`.")
    print("  nothing in the settings list is about it, because it is not")
    print("  a session event at all -- it is a different route, and no")
    print("  amount of care in the session code reaches it. the only fix")
    print("  is to invalidate every session for the account when the")
    print("  credential changes, which is a line in the password route")
    print("  and not in this one.")
    print()

    print("  what the strictest setting costs")
    for wipe in (False, True):
        st = Store(rotate_login=False, rotate_privilege=True,
                   wipe_on_rotate=wipe)
        first = st.login("d1", "u1")
        second = st.login("d2", "u1")
        st.escalate(second)
        label = "clear the store" if wipe else "delete the one session"
        print("    {:<24} the other device is {}"
              .format(label, "still logged in" if st.who(first) else "logged out"))
    print()
    print("  rotating a session and clearing the store look the same in a")
    print("  test with one device in it. the second row is why the setting")
    print("  is written as a delete rather than a clear.")
    print()

    issued_random = random_ids(1, N)
    issued_counter = counter_ids(N)
    models = [
        ("a counter", issued_counter, "the same counter", counter_ids(N), "none"),
        ("random.Random(1)", issued_random, "random.Random(1)", random_ids(1, N), "32 bits"),
        ("random.Random(1)", issued_random, "random.Random(2)", random_ids(2, N), "32 bits, wrong"),
    ]
    print("    {:<23}{:<19}{:>9}{:>14}   {}".format(
        "generator issued", "attacker's model", "distinct", "reproduced",
        "state to know"))
    for label, issued, model, modelled, state in models:
        hit = sum(1 for a, b in zip(issued, modelled) if a == b)
        print("    {:<23}{:<19}{:>9}{:>14}   {}".format(
            label, model, len(set(issued)), "%d of %d" % (hit, N), state))
    print("    {:<23}{:<19}{:>9}{:>14}   {}".format(
        "secrets.token_hex(16)", "(none exists)", "-", "-", "128 bits"))
    print()

    print("  every row that can be measured is 1000 distinct out of 1000.")
    print("  uniqueness is the property people test for, and it is not the")
    print("  one that matters. the first two rows are an attacker")
    print("  reproducing every id without ever having seen one, because")
    print("  the id is a function of something smaller than the id.")
    print("  the fourth row has no model to run, and that is the whole")
    print("  difference between it and the third -- the third row is the")
    print("  same weak generator guessed wrong, which is what a strong")
    print("  generator looks like from the outside.")


main()
