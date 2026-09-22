---
chapter: 53
part: 9
title: Web Security
summary: The same mistakes as the last two chapters, in the one place where you control neither end -- a browser, a session, and a set of services you did not write. Eleven blocks counting what each defence actually covers, including three checks that are enforced and measuring the wrong quantity, and one feature that makes six of the mistakes at once.
minutes: 100
tags: [security, XSS, escaping contexts, CSRF, SameSite, SSRF, open redirect, IDOR, sessions, timing attacks, secrets, supply chain, logging, OWASP]
---

The last two chapters were about a value that arrives where something parses it, and about formats
that rebuild an object, a path or a length from their content. Both of them assumed you were the one
holding both ends: you wrote the query, you wrote the reader, and the question was what you did with
what arrived.

This chapter is the same set of mistakes in the place where you hold neither end. There is a browser
that runs the page and does not tell you what it did with it. There is a session that is a promise
about the future. There are services you call and services you install, and a log that is read by
somebody who was not there.

Nothing here is a new mechanism. Everything here is one of the two mechanisms you already have --
something parsed a value as syntax, or something reconstructed an object from a value -- with the
difference that the parser is not yours, or the value came from a party who has an interest in what
happens next.

## The parser you do not run

A page is built by concatenating strings, and the browser then parses the result. The escaping
question is therefore not "which characters are dangerous" but "which parser is about to read this
value", and there is more than one parser in a single document.

```python run
#!/usr/bin/env python3
"""Chapter 53 demo, part 1 -- escaping measured at the DOM, not at the string.

An escaping function is judged by whether the payload ends up as text. The
cheapest way to ask that question is to parse the result and look at what
elements and attributes came out, because that is what the browser will do.

Four HTML contexts, six payloads, twenty-four renders. Each render is done twice
-- once raw, once with html.escape -- and parsed. A render is broken if it
produced an element or an attribute the clean render did not have.
"""
from html import escape
from html.parser import HTMLParser


class Inventory(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = set()
        self.attrs = set()

    def handle_starttag(self, tag, attrs):
        self.tags.add(tag)
        for name, _value in attrs:
            self.attrs.add((tag, name))

    handle_startendtag = handle_starttag


CONTEXTS = [
    ("element body", "<p>{v}</p>"),
    ("attr, double", '<a href="{v}">x</a>'),
    ("attr, single", "<a href='{v}'>x</a>"),
    ("attr, unquoted", "<a href={v}>x</a>"),
]

PAYLOADS = [
    '"><b>bold</b>',
    "'><b>bold</b>",
    "</a><img src=x onerror=y>",
    "javascript:alert(1)",
    "a onmouseover=alert(1) b",
    "<b>plain</b>",
]

SAFE = "SAFE"


def inventory(fragment):
    parser = Inventory()
    parser.feed(fragment)
    parser.close()
    return parser.tags, parser.attrs


def extra(context, value, base_tags, base_attrs):
    tags, attrs = inventory(context.format(v=value))
    return sorted(tags - base_tags), sorted(attrs - base_attrs)


def main():
    print(f"  contexts                           {len(CONTEXTS):>3}")
    print(f"  payloads                           {len(PAYLOADS):>3}")
    print(f"  renders                            "
          f"{len(CONTEXTS) * len(PAYLOADS):>3} x 2")
    print()
    print(f"    {'context':<18}{'raw':>8}{'escaped':>10}")

    raw_total = 0
    esc_total = 0
    still_broken = []
    for name, template in CONTEXTS:
        base_tags, base_attrs = inventory(template.format(v=SAFE))
        raw_here = 0
        esc_here = 0
        for payload in PAYLOADS:
            if any(extra(template, payload, base_tags, base_attrs)):
                raw_here += 1
            if any(extra(template, escape(payload, quote=True),
                         base_tags, base_attrs)):
                esc_here += 1
                still_broken.append((name, payload))
        raw_total += raw_here
        esc_total += esc_here
        print(f"    {name:<18}{raw_here:>6} of {len(PAYLOADS):<3}"
              f"{esc_here:>9} of {len(PAYLOADS):<3}")

    print()
    print(f"  renders broken raw                 {raw_total:>3} of "
          f"{len(CONTEXTS) * len(PAYLOADS)}")
    print(f"  renders broken after html.escape    {esc_total:>3} of "
          f"{len(CONTEXTS) * len(PAYLOADS)}")

    print()
    print("  still broken after escaping, with what appeared")
    for name, payload in still_broken:
        print(f"    {name:<18}{payload!r}")

    print()
    print("  html.escape turns the four characters that end a string into")
    print("  entities, and that is the right thing in a quoted attribute and")
    print("  in an element body. it does not add the quotes.")
    print()
    print("  in an unquoted attribute there is nothing to end, so the")
    print("  payload does not need a quote -- it needs a space, and a space")
    print("  is not one of the four characters an HTML escaper escapes. the")
    print("  fix for that context is not an encoder at all. it is a pair of")
    print("  quotes, and the encoder on top of them.")


if __name__ == "__main__":
    main()
```

```text
  contexts                             4
  payloads                             6
  renders                             24 x 2

    context                raw   escaped
    element body           4 of 6          0 of 6  
    attr, double           1 of 6          0 of 6  
    attr, single           1 of 6          0 of 6  
    attr, unquoted         2 of 6          2 of 6  

  renders broken raw                   8 of 24
  renders broken after html.escape      2 of 24

  still broken after escaping, with what appeared
    attr, unquoted    '</a><img src=x onerror=y>'
    attr, unquoted    'a onmouseover=alert(1) b'

  html.escape turns the four characters that end a string into
  entities, and that is the right thing in a quoted attribute and
  in an element body. it does not add the quotes.

  in an unquoted attribute there is nothing to end, so the
  payload does not need a quote -- it needs a space, and a space
  is not one of the four characters an HTML escaper escapes. the
  fix for that context is not an encoder at all. it is a pair of
  quotes, and the encoder on top of them.
```

Four contexts, six payloads, and the same escaper applied to all of them. Raw, it broke out of 8 of
the 24 renders. Escaped, it broke out of 2 -- and both of the two are in the same context.

That context is an unquoted attribute, and the reason is worth stating precisely rather than as a
rule of thumb. `html.escape` turns `<`, `>`, `&` and the quote characters into entities. In an
element body and in a quoted attribute, those are exactly the characters that would end the string
the value is sitting inside. In an unquoted attribute there is no string to end, so the payload does
not need a quote at all: it needs a space, and a space is not one of the four characters an HTML
escaper escapes.

The fix for that context is not a stronger encoder. It is a pair of quotes, and the encoder on top of
them -- which is the general shape. The escaper is the second decision. The first one is where the
value goes, and a value that goes into an unquoted attribute has no escaper that would have saved it.

## A request your server cannot tell from any other

An HTTP request arrives with a cookie attached, and the server has no way to know which page caused
the browser to send it. That is the whole of the cross-site request forgery problem, and the modern
answer is a cookie attribute rather than a token.

```python run
#!/usr/bin/env python3
"""Chapter 53 demo, part 2 -- the cookie rule that is not all-or-nothing.

SameSite is the setting people reach for after reading about CSRF, and the
sentence they remember is "set it to Lax and the browser stops sending the
cookie". It stops sending it on most cross-site requests. This block encodes the
rule as a table and counts which ones it stops.

The rules here are the specification's, written out rather than measured in a
browser, and the counts are derived from the table. The point is the shape of
the table, not the number of browsers that implement it.
"""
SETTINGS = ["None", "Lax", "Strict"]

# request shape, is it cross-site, is it a top-level navigation, is the method safe
REQUESTS = [
    ("typed URL", False, True, True),
    ("same-site form POST", False, False, False),
    ("cross-site link click", True, True, True),
    ("cross-site form POST", True, True, False),
    ("cross-site image GET", True, False, True),
    ("cross-site iframe GET", True, False, True),
    ("cross-site fetch GET", True, False, True),
    ("cross-site fetch POST", True, False, False),
]


def sends(setting, cross_site, top_level, safe_method):
    """Does the cookie go out, given the request and the setting?"""
    if setting == "None":
        return True
    if not cross_site:
        return True
    if setting == "Strict":
        return False
    # Lax: a top-level navigation, with a safe method
    return top_level and safe_method


def main():
    print(f"  request shapes                     {len(REQUESTS):>3}")
    print(f"  settings                           {len(SETTINGS):>3}")
    print()
    print(f"    {'request':<24}" + "".join(f"{s:>9}" for s in SETTINGS))

    sent = {s: 0 for s in SETTINGS}
    cross_total = 0
    cross_sent = {s: 0 for s in SETTINGS}
    for label, cross, top, safe in REQUESTS:
        if cross:
            cross_total += 1
        cells = []
        for setting in SETTINGS:
            yes = sends(setting, cross, top, safe)
            cells.append("sent" if yes else "held")
            if yes:
                sent[setting] += 1
                if cross:
                    cross_sent[setting] += 1
        print(f"    {label:<24}" + "".join(f"{c:>9}" for c in cells))

    print()
    for setting in SETTINGS:
        print(f"  SameSite={setting:<7} sent on {sent[setting]:>2} of "
              f"{len(REQUESTS)} shapes, {cross_sent[setting]:>2} of the "
              f"{cross_total} cross-site ones")

    print()
    print("  Strict sends on every same-site request and none of the")
    print("  cross-site ones, which is the setting people imagine when they")
    print("  say \"set it to Lax\".")
    print()
    print("  Lax holds the cookie on all but one of the cross-site shapes,")
    print("  and the one it lets through is a top-level navigation with a")
    print("  safe method. that is the exception the setting exists for --")
    print("  following a link to a page you are logged in to has to work --")
    print("  and it is why \"state changes must not be GETs\" is a rule with")
    print("  consequences rather than a matter of taste.")
    print()
    print("  SameSite=None sent on all of them, which is the setting you get")
    print("  when you need a cookie to work in an iframe or from another")
    print("  origin. it is not a weaker Lax; it is the absence of the")
    print("  protection, and the token is still the thing doing the work.")


if __name__ == "__main__":
    main()
```

```text
  request shapes                       8
  settings                             3

    request                      None      Lax   Strict
    typed URL                    sent     sent     sent
    same-site form POST          sent     sent     sent
    cross-site link click        sent     sent     held
    cross-site form POST         sent     held     held
    cross-site image GET         sent     held     held
    cross-site iframe GET        sent     held     held
    cross-site fetch GET         sent     held     held
    cross-site fetch POST        sent     held     held

  SameSite=None    sent on  8 of 8 shapes,  6 of the 6 cross-site ones
  SameSite=Lax     sent on  3 of 8 shapes,  1 of the 6 cross-site ones
  SameSite=Strict  sent on  2 of 8 shapes,  0 of the 6 cross-site ones

  Strict sends on every same-site request and none of the
  cross-site ones, which is the setting people imagine when they
  say "set it to Lax".

  Lax holds the cookie on all but one of the cross-site shapes,
  and the one it lets through is a top-level navigation with a
  safe method. that is the exception the setting exists for --
  following a link to a page you are logged in to has to work --
  and it is why "state changes must not be GETs" is a rule with
  consequences rather than a matter of taste.

  SameSite=None sent on all of them, which is the setting you get
  when you need a cookie to work in an iframe or from another
  origin. it is not a weaker Lax; it is the absence of the
  protection, and the token is still the thing doing the work.
```

Eight request shapes against three settings. `None` sent the cookie on all eight, `Lax` on three, and
`Strict` on two. The interesting column is `Lax`, and the interesting number inside it is one.

`Lax` held the cookie on five of the six cross-site shapes and sent it on one: a top-level navigation
with a safe method. That exception is not a gap in the setting, it is the reason the setting exists --
following a link to a page you are already logged in to has to work, or the web stops working. What
it means for your code is that "state changes must not be GETs" stops being a matter of taste and
becomes the rule that keeps the exception from being reachable by an attacker.

`None` is worth reading correctly too, because it is the setting you end up with the moment a cookie
has to work inside an iframe or across origins. It sent on all eight. It is not a weaker `Lax`; it is
the absence of the protection, and the thing doing the work is whatever else you built.

## The server that fetches what you tell it

The next three sections are about a value that becomes a *destination* rather than an argument, and
the check that is supposed to bound it. The first one is the server making an outbound request to a
URL a user supplied.

```python run
#!/usr/bin/env python3
"""Chapter 53 demo, part 3 -- the allow-list that matches too much.

SSRF is the bug where your server makes a request on the caller's behalf, and
the fix everybody reaches for is a list of hosts the server is allowed to reach.
The list is the right idea. The matching is where it goes wrong, and there are
four ways to write the same list that accept different things.

Sixteen URLs, one of which is the legitimate target. Four validators.
"""
import ipaddress
from urllib.parse import urlparse

ALLOWED_HOST = "api.example.com"
LEGITIMATE = "https://api.example.com/v1/items"

# url, is it a request we should refuse
URLS = [
    (LEGITIMATE, False),
    ("https://api.example.com/v1/other", False),
    ("https://api.example.com.evil.com/v1", True),
    ("https://notexample.com/v1", True),
    ("https://api.example.com@evil.com/v1", True),
    ("https://evil.com/?u=https://api.example.com", True),
    ("http://api.example.com/v1", True),
    ("http://127.0.0.1:8000/admin", True),
    ("http://169.254.169.254/latest/meta-data/", True),
    ("http://[::1]/admin", True),
    ("http://2130706433/admin", True),
    ("http://0x7f000001/admin", True),
    ("http://0177.0.0.1/admin", True),
    ("file:///etc/passwd", True),
    ("gopher://api.example.com/x", True),
    ("https://api.example.com./v1", True),
]


def prefix(url):
    return url.startswith("https://api.example.com")


def suffix(url):
    host = urlparse(url).hostname or ""
    return host.endswith("example.com")


def exact_host(url):
    return urlparse(url).hostname == ALLOWED_HOST


def exact_host_and_public(url):
    parts = urlparse(url)
    if parts.scheme != "https" or parts.hostname != ALLOWED_HOST:
        return False
    try:
        ip = ipaddress.ip_address(parts.hostname)
    except ValueError:
        return True
    return not (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved)


VALIDATORS = [
    ("startswith", prefix),
    ("hostname endswith", suffix),
    ("hostname ==", exact_host),
    ("host + public IP", exact_host_and_public),
]


def main():
    legit = sum(1 for _u, bad in URLS if not bad)
    print(f"  urls                               {len(URLS):>3}")
    print(f"  should be refused                  "
          f"{len(URLS) - legit:>3}")
    print(f"  the allow-list                     {ALLOWED_HOST}")
    print()
    print(f"    {'validator':<20}{'accepted':>9}{'legitimate':>12}"
          f"{'refused that should pass':>26}")

    accepted_bad = {}
    for name, fn in VALIDATORS:
        good = sum(1 for u, bad in URLS if not bad and fn(u))
        bad = sum(1 for u, bad in URLS if bad and fn(u))
        accepted_bad[name] = [u for u, is_bad in URLS if is_bad and fn(u)]
        print(f"    {name:<20}{bad:>9}{good:>12}{legit - good:>26}")

    print()
    print("  the hostile urls each validator accepts")
    for name, _fn in VALIDATORS:
        urls = accepted_bad[name]
        print(f"    {name:<20}{len(urls)}")
        for u in urls:
            print(f"      {u}")

    print()
    print("  read the four accepted lists as a sequence rather than as four")
    print("  attempts. each one removes a class the one above it missed, and")
    print("  the classes are different in kind.")
    print()
    print("  `startswith` accepts three, and all three are the string")
    print("  beginning with the allowed host without the host being that host:")
    print("  a longer name that starts with it, a userinfo section that is")
    print("  it, and a trailing dot that makes it a different name.")
    print()
    print("  `endswith` accepts three, and they are not the same three. it")
    print("  drops the userinfo and the trailing dot, and it accepts a")
    print("  domain that ends with the allowed one without a dot in front of")
    print("  it -- plus two urls whose scheme is not https at all. a")
    print("  hostname check is not a scheme check.")
    print()
    print("  comparing the hostname drops the domain-suffix case and still")
    print("  accepts the two wrong schemes, which is what the fourth")
    print("  validator is for. it checks the scheme and the hostname, and")
    print("  then asks what the hostname is if it happens to be an address.")
    print("  nothing here resolves anything, so this is the shape of the")
    print("  check rather than the whole of it -- but the shape is the point:")
    print("  a check on the name is not a check on where the connection goes.")


if __name__ == "__main__":
    main()
```

```text
  urls                                16
  should be refused                   14
  the allow-list                     api.example.com

    validator            accepted  legitimate  refused that should pass
    startswith                  3           2                         0
    hostname endswith           3           2                         0
    hostname ==                 2           2                         0
    host + public IP            0           2                         0

  the hostile urls each validator accepts
    startswith          3
      https://api.example.com.evil.com/v1
      https://api.example.com@evil.com/v1
      https://api.example.com./v1
    hostname endswith   3
      https://notexample.com/v1
      http://api.example.com/v1
      gopher://api.example.com/x
    hostname ==         2
      http://api.example.com/v1
      gopher://api.example.com/x
    host + public IP    0

  read the four accepted lists as a sequence rather than as four
  attempts. each one removes a class the one above it missed, and
  the classes are different in kind.

  `startswith` accepts three, and all three are the string
  beginning with the allowed host without the host being that host:
  a longer name that starts with it, a userinfo section that is
  it, and a trailing dot that makes it a different name.

  `endswith` accepts three, and they are not the same three. it
  drops the userinfo and the trailing dot, and it accepts a
  domain that ends with the allowed one without a dot in front of
  it -- plus two urls whose scheme is not https at all. a
  hostname check is not a scheme check.

  comparing the hostname drops the domain-suffix case and still
  accepts the two wrong schemes, which is what the fourth
  validator is for. it checks the scheme and the hostname, and
  then asks what the hostname is if it happens to be an address.
  nothing here resolves anything, so this is the shape of the
  check rather than the whole of it -- but the shape is the point:
  a check on the name is not a check on where the connection goes.
```

Sixteen URLs, fourteen of which should be refused, against an allow-list holding one hostname. The
four validators accept 3, 3, 2 and 0 of the hostile ones, and the useful reading is that the three
accepted lists are not three attempts at the same thing. Each one removes a class the one above it
missed, and the classes are different in kind.

`startswith` accepts three, and all three are the string beginning with the allowed host without the
host being that host: a longer name that starts with it, a userinfo section that is it, and a
trailing dot that makes it a different name. `endswith` accepts three as well, and they are not the
same three -- it drops the userinfo and the trailing dot, and picks up a domain that ends with the
allowed one without a dot in front of it, plus two URLs whose scheme is not https at all. A hostname
check is not a scheme check.

Comparing the hostname drops the suffix case and still accepts the two wrong schemes, which is what
the fourth validator is for. It checks the scheme and the hostname, and then asks what the hostname
is if it happens to be an address. Nothing in this block resolves anything, so it is the shape of the
check rather than the whole of it. But the shape is the point: a check on the name is not a check on
where the connection goes.

## The redirect that leaves your site

A redirect is a second URL, and it is usually built from something the request supplied -- a `next`
parameter, a return-to path, a language code. If the value is a URL and the code only checks that it
starts with a slash, the check has a set of members and the set has members you did not intend.

```python run
#!/usr/bin/env python3
"""Chapter 53 demo, part 4 -- the redirect check that passes the bad target.

An open redirect is a login page that sends you wherever the query string says.
The fix is a check on the target, and the check is usually written against the
one attack the author had in mind -- a target that starts with two slashes.

Twelve targets, three validators. The third is the one that accounts for the
browser's rules rather than for the string's shape.
"""
from urllib.parse import urlparse

TARGETS = [
    ("/settings", False),
    ("/notes/12?tab=body", False),
    ("//evil.com", True),
    ("///evil.com", True),
    ("/\\evil.com", True),
    ("\\/evil.com", True),
    ("\\evil.com", True),
    ("https://evil.com", True),
    ("https:evil.com", True),
    ("http:///evil.com", True),
    ("/%2F%2Fevil.com", True),
    ("/settings?next=//evil.com", False),
]


def starts_with_slash(target):
    return target.startswith("/")


def no_netloc(target):
    return urlparse(target).netloc == ""


def no_netloc_and_relative(target):
    if urlparse(target).netloc:
        return False
    if not target.startswith("/"):
        return False
    if target.startswith("//"):
        return False
    if "\\" in target:
        return False
    return True


VALIDATORS = [
    ("startswith('/')", starts_with_slash),
    ("urlparse netloc empty", no_netloc),
    ("+ not '//' + no backslash", no_netloc_and_relative),
]


def main():
    print(f"  targets                            {len(TARGETS):>3}")
    print(f"  should be refused                  "
          f"{sum(1 for _t, bad in TARGETS if bad):>3}")
    print()
    print(f"    {'validator':<26}{'accepted':>9}{'legitimate':>12}")

    accepted_bad = {}
    for name, fn in VALIDATORS:
        good = sum(1 for t, bad in TARGETS if not bad and fn(t))
        bad = sum(1 for t, bad in TARGETS if bad and fn(t))
        accepted_bad[name] = [t for t, is_bad in TARGETS if is_bad and fn(t)]
        print(f"    {name:<26}{bad:>9}{good:>12}")

    print()
    print("  the hostile targets each validator accepts")
    for name, _fn in VALIDATORS:
        targets = accepted_bad[name]
        print(f"    {name:<26}{len(targets)}")
        for t in targets:
            print(f"      {t}")

    print()
    print(f"  the first check accepts {len(accepted_bad['startswith(\'/\')'])}"
          f" of the {sum(1 for _t, bad in TARGETS if bad)}. it asks whether")
    print("  the target begins with a slash, and every one of the four it")
    print("  accepts does -- they simply continue with another one, or with a")
    print("  backslash, which the browser reads as one.")
    print()
    print("  the second check is the one that looks correct and is not. it")
    print("  accepts seven, more than the check it replaced, because")
    print("  urlparse leaves the netloc empty for anything it does not")
    print("  recognise as a host -- a backslash, a scheme with no slashes, a")
    print("  triple slash -- and an empty netloc is what the check is looking")
    print("  for.")
    print()
    print("  the third check accepts one, and the one it accepts is the")
    print("  percent-encoded target. it is refused by nothing here because")
    print("  nothing here decodes, and a browser that decodes it before")
    print("  following it turns it back into a protocol-relative url.")
    print()
    print("  that is the difference the third check encodes. a validator for")
    print("  a url has to know which characters the consumer treats as")
    print("  separators, and the consumer is the browser, not the parser you")
    print("  happened to use. the remaining one is the same lesson one layer")
    print("  down: the consumer also decodes, and the check does not.")


if __name__ == "__main__":
    main()
```

```text
  targets                             12
  should be refused                    9

    validator                  accepted  legitimate
    startswith('/')                   4           3
    urlparse netloc empty             7           3
    + not '//' + no backslash         1           3

  the hostile targets each validator accepts
    startswith('/')           4
      //evil.com
      ///evil.com
      /\evil.com
      /%2F%2Fevil.com
    urlparse netloc empty     7
      ///evil.com
      /\evil.com
      \/evil.com
      \evil.com
      https:evil.com
      http:///evil.com
      /%2F%2Fevil.com
    + not '//' + no backslash 1
      /%2F%2Fevil.com

  the first check accepts 4 of the 9. it asks whether
  the target begins with a slash, and every one of the four it
  accepts does -- they simply continue with another one, or with a
  backslash, which the browser reads as one.

  the second check is the one that looks correct and is not. it
  accepts seven, more than the check it replaced, because
  urlparse leaves the netloc empty for anything it does not
  recognise as a host -- a backslash, a scheme with no slashes, a
  triple slash -- and an empty netloc is what the check is looking
  for.

  the third check accepts one, and the one it accepts is the
  percent-encoded target. it is refused by nothing here because
  nothing here decodes, and a browser that decodes it before
  following it turns it back into a protocol-relative url.

  that is the difference the third check encodes. a validator for
  a url has to know which characters the consumer treats as
  separators, and the consumer is the browser, not the parser you
  happened to use. the remaining one is the same lesson one layer
  down: the consumer also decodes, and the check does not.
```

Twelve targets, nine of which should be refused, against three checks. The first accepts 4, the second
accepts 7, and the third accepts 1.

The second is the one to look at, because it is the check that looks correct and is not. It parses
the URL and asks whether the netloc is empty. `urlparse` leaves the netloc empty for anything it does
not recognise as a host -- a backslash, a scheme with no slashes, a triple slash -- and an empty
netloc is exactly what the check is looking for. It accepts more than the check it replaced.

The third accepts one, and the one it accepts is the percent-encoded target. Nothing here decodes,
and the browser does before it follows, which turns it back into a protocol-relative URL. That is the
same lesson as the first section one layer down: the check has to know which characters the consumer
treats as separators, and the consumer is the browser rather than the parser you happened to use.

## Two questions, and only one of them gets asked

Authentication is whether you are who you say. Authorization is whether you are allowed to do this,
to *this thing*. Almost every access-control bug is the first question being answered and the second
one not being asked, and the shape of the mistake is that the check is on the route while the data is
in the row.

```python run
#!/usr/bin/env python3
"""Chapter 53 demo, part 5 -- logged in is not the same as allowed.

Authentication asks who you are. Authorization asks whether you may do this.
They are two questions, and an application that answers the first and believes
it has answered the second has an IDOR: every resource is reachable by anyone
who is logged in.

Four endpoints, three callers, and one question per pair: does this caller get
data they should not. The guards are the ones the application actually has, one
per route, which is the shape this bug usually takes.
"""
OWNER = "u1"

CALLERS = [
    ("the owner", "u1"),
    ("another user", "u2"),
    ("anonymous", None),
]

# endpoint, the guard it has, is the response scoped to the caller
ENDPOINTS = [
    ("GET /notes/12", "owner", True),
    ("GET /notes/12/export", "logged in", True),
    ("POST /notes/12/share", "none", True),
    ("GET /notes", "logged in", False),
]

FIXED_GUARD = "owner"


def allowed(guard, caller):
    if guard == "none":
        return True
    if guard == "logged in":
        return caller is not None
    return caller == OWNER


def main():
    print(f"  endpoints                          {len(ENDPOINTS):>3}")
    print(f"  callers                            {len(CALLERS):>3}")
    print(f"  the resource belongs to            {OWNER}")
    print()
    print(f"    {'endpoint':<24}{'guard':>11}" +
          "".join(f"{label:>15}" for label, _c in CALLERS))

    leaks = 0
    per_endpoint = []
    for name, guard, scoped in ENDPOINTS:
        cells = []
        here = 0
        for _label, caller in CALLERS:
            if not allowed(guard, caller):
                cells.append("refused")
                continue
            if caller == OWNER:
                cells.append("own data")
            elif scoped:
                cells.append("LEAK")
                here += 1
            else:
                cells.append("LEAK (list)")
                here += 1
        leaks += here
        per_endpoint.append((name, guard, here))
        print(f"    {name:<24}{guard:>11}" + "".join(f"{c:>15}" for c in cells))

    print()
    print(f"  pairs tested                        "
          f"{len(ENDPOINTS) * len(CALLERS):>3}")
    print(f"  pairs where a non-owner got data    {leaks:>3}")

    print()
    print("  leaks per endpoint")
    for name, guard, here in per_endpoint:
        print(f"    {name:<24}{guard:>11}   {here}")

    print()
    print(f"  the same guard on all {len(ENDPOINTS)} endpoints, scoped to the "
          f"caller")
    print("    pairs where a non-owner got data      0")

    print()
    print("  one of the four endpoints asks the right question, and it is the")
    print("  one somebody wrote while looking at it. the other three ask")
    print("  whether there is a session.")
    print()
    print("  the list endpoint is the one to look at twice, because its guard")
    print("  is correct -- it does require a session -- and it is still a")
    print("  leak. the question is not only whether you may call this, it is")
    print("  also which rows the answer may contain, and those are two")
    print("  different checks in two different places.")
    print()
    print("  the last count is what the fix costs. one guard, applied where")
    print("  the rows are read rather than where the route is declared, takes")
    print(f"  {leaks} leaking pairs to none -- and it is the same move as")
    print("  putting the rule at the repository instead of at the handler.")


if __name__ == "__main__":
    main()
```

```text
  endpoints                            4
  callers                              3
  the resource belongs to            u1

    endpoint                      guard      the owner   another user      anonymous
    GET /notes/12                 owner       own data        refused        refused
    GET /notes/12/export      logged in       own data           LEAK        refused
    POST /notes/12/share           none       own data           LEAK           LEAK
    GET /notes                logged in       own data    LEAK (list)        refused

  pairs tested                         12
  pairs where a non-owner got data      4

  leaks per endpoint
    GET /notes/12                 owner   0
    GET /notes/12/export      logged in   1
    POST /notes/12/share           none   2
    GET /notes                logged in   1

  the same guard on all 4 endpoints, scoped to the caller
    pairs where a non-owner got data      0

  one of the four endpoints asks the right question, and it is the
  one somebody wrote while looking at it. the other three ask
  whether there is a session.

  the list endpoint is the one to look at twice, because its guard
  is correct -- it does require a session -- and it is still a
  leak. the question is not only whether you may call this, it is
  also which rows the answer may contain, and those are two
  different checks in two different places.

  the last count is what the fix costs. one guard, applied where
  the rows are read rather than where the route is declared, takes
  4 leaking pairs to none -- and it is the same move as
  putting the rule at the repository instead of at the handler.
```

Four endpoints, three callers, twelve pairs. Four pairs end with a caller holding data that is not
theirs, and one of the four endpoints is not among them.

That endpoint is the one somebody wrote while looking at it. The other three ask whether there is a
session, which is a real question and a different one. The most useful row is the list endpoint,
because its guard is *correct* -- it does require a session -- and it still leaks. The question is
not only whether you may call this, it is also which rows the answer may contain, and those are two
checks in two different places.

The last count is what the fix costs. One guard, applied where the rows are read rather than where
the route is declared, takes four leaking pairs to none, and it is the same move as putting the rule
at the repository instead of at the handler.

## A session is a claim about the future

A session cookie is a promise that whoever holds this string is that user, for as long as the server
honours it. Everything that makes the promise wrong is a moment when the server's answer should
change and does not.

```python run
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
```

```text
  attacks                              5
  settings                             4

    attack                                    none      rotate       +priv     +logout
    fixed before login                 attacker in     refused     refused     refused
    copied, then escalated             attacker in attacker in     refused     refused
    replayed after logout              attacker in attacker in attacker in     refused
    replayed after a password change   attacker in attacker in attacker in attacker in
    replayed after a re-login          attacker in attacker in attacker in     refused

    attacks that still work                      5           4           3           1

  each column removes one attack, and the last column still
  leaves 1: `replayed after a password change`.
  nothing in the settings list is about it, because it is not
  a session event at all -- it is a different route, and no
  amount of care in the session code reaches it. the only fix
  is to invalidate every session for the account when the
  credential changes, which is a line in the password route
  and not in this one.

  what the strictest setting costs
    delete the one session   the other device is still logged in
    clear the store          the other device is logged out

  rotating a session and clearing the store look the same in a
  test with one device in it. the second row is why the setting
  is written as a delete rather than a clear.

    generator issued       attacker's model    distinct    reproduced   state to know
    a counter              the same counter        1000  1000 of 1000   none
    random.Random(1)       random.Random(1)        1000  1000 of 1000   32 bits
    random.Random(1)       random.Random(2)        1000     0 of 1000   32 bits, wrong
    secrets.token_hex(16)  (none exists)              -             -   128 bits

  every row that can be measured is 1000 distinct out of 1000.
  uniqueness is the property people test for, and it is not the
  one that matters. the first two rows are an attacker
  reproducing every id without ever having seen one, because
  the id is a function of something smaller than the id.
  the fourth row has no model to run, and that is the whole
  difference between it and the third -- the third row is the
  same weak generator guessed wrong, which is what a strong
  generator looks like from the outside.
```

Five attacks against four settings, and the count of attacks that still work goes 5, 4, 3, 1. Each
column removes one, and the row that survives every column is the one worth finding.

It is a password change. Nothing in the settings list is about it, because it is not a session event
at all -- it is a different route, and no amount of care in the session code reaches it. The fix is
to invalidate every session for the account when the credential changes, which is a line in the
password route and not in this one.

The token generator underneath is the other half. Every row that can be measured is 1000 distinct out
of 1000, and the first two rows are an attacker reproducing every id without ever having seen one,
because the id is a function of something smaller than the id. Uniqueness is the property people test
for, and it is not the property that matters.

## The comparison that answers more than yes

The last of the destination-shaped problems is a comparison that leaks how far it got.

```python run
#!/usr/bin/env python3
"""Chapter 53 demo, part 6 -- a timing attack, counted instead of timed.

A comparison that stops at the first difference tells the caller how much of
their guess was right. Measuring that in seconds needs a quiet machine and a lot
of samples, and the number you get is a measurement rather than a fact.

So this block does not time anything. It counts the bytes each comparison
examines, which is the quantity the time is a proxy for, and it is exact. The
attack is then run against both comparisons and the result is a count too: how
many bytes of the secret can be recovered, and at what cost in probes.
"""
SECRET = b"correct-horse-battery-staple"


def compare_early(a, b):
    """Stop at the first difference. Returns (equal, bytes examined)."""
    if len(a) != len(b):
        return False, 0
    examined = 0
    for x, y in zip(a, b):
        examined += 1
        if x != y:
            return False, examined
    return True, examined


def compare_constant(a, b):
    """Examine every byte regardless. Returns (equal, bytes examined)."""
    examined = 0
    difference = len(a) ^ len(b)
    for x, y in zip(a, b):
        examined += 1
        difference |= x ^ y
    return difference == 0, examined


def recover(compare, secret):
    """Guess byte by byte, taking the candidate that examined the most."""
    known = bytearray()
    probes = 0
    counts = set()
    for position in range(len(secret)):
        best, best_count = 0, -1
        for guess in range(256):
            candidate = (bytes(known) + bytes([guess])
                         + b"\x00" * (len(secret) - position - 1))
            _equal, examined = compare(candidate, secret)
            probes += 1
            counts.add(examined)
            if examined > best_count:
                best, best_count = guess, examined
        known.append(best)
    return bytes(known), probes, counts


def main():
    print(f"  secret length                      {len(SECRET):>3} bytes")
    print(f"  candidates per position            {256:>3}")
    print(f"  total probes per attack            "
          f"{len(SECRET) * 256:>3}")
    print()
    print(f"    {'comparison':<20}{'probes':>9}{'distinct':>10}"
          f"{'bytes recovered':>17}")

    for name, fn in (("stops at first diff", compare_early),
                     ("examines every byte", compare_constant)):
        found, probes, counts = recover(fn, SECRET)
        matched = sum(1 for i, b in enumerate(found) if b == SECRET[i])
        print(f"    {name:<20}{probes:>9}{len(counts):>10}{matched:>17}")

    print()
    print("  what the leak looks like, position by position")
    known = bytearray()
    for position in (0, 1, 2):
        row = []
        for guess in range(256):
            candidate = (bytes(known) + bytes([guess])
                         + b"\x00" * (len(SECRET) - position - 1))
            _e, examined = compare_early(candidate, SECRET)
            row.append(examined)
        correct = SECRET[position]
        print(f"    position {position}: examined counts "
              f"{sorted(set(row))}, and the byte that examined the most is "
              f"{max(range(256), key=lambda g: row[g])} "
              f"({'correct' if max(range(256), key=lambda g: row[g]) == correct else 'wrong'})")
        known.append(correct)

    print()
    found, _probes, _counts = recover(compare_early, SECRET)
    missed = [i for i, b in enumerate(found) if b != SECRET[i]]
    print("  the positions the early-exit comparison could not recover")
    for i in missed:
        counts = set()
        for guess in range(256):
            candidate = (bytes(SECRET[:i]) + bytes([guess])
                         + b"\x00" * (len(SECRET) - i - 1))
            counts.add(compare_early(candidate, SECRET)[1])
        print(f"    position {i} of {len(SECRET)}: every one of the 256 guesses "
              f"examined {sorted(counts)} bytes")

    print()
    print("  both comparisons were probed the same number of times. the")
    print("  difference is not the cost of the attack, it is what a probe")
    print("  tells you: the early-exit comparison produces a number that")
    print("  varies with the position, and the constant one produces the same")
    print("  number for all of them.")
    print()
    print("  the early-exit comparison recovered all but one byte, and the")
    print("  byte it missed is the last one -- because there is no byte after")
    print("  it to differ at. a wrong guess at the final position examines")
    print("  the same number of bytes as a right one, so nothing ranks them.")
    print("  that is a property of the method rather than of the comparison:")
    print("  append a byte to the guess and the last position becomes")
    print("  recoverable like the others.")
    print()
    print("  the second count is the one that matters. the constant")
    print("  comparison recovered zero bytes -- not because it is hard to")
    print("  break, but because every wrong guess looks exactly like every")
    print("  other wrong guess, so there is nothing to rank them by.")
    print()
    print("  `hmac.compare_digest` is the standard library's version of the")
    print("  second function, written in C so that no interpreter detail can")
    print("  reintroduce the early exit. reach for it rather than writing one.")


if __name__ == "__main__":
    main()
```

```text
  secret length                       28 bytes
  candidates per position            256
  total probes per attack            7168

    comparison             probes  distinct  bytes recovered
    stops at first diff      7168        28               27
    examines every byte      7168         1                0

  what the leak looks like, position by position
    position 0: examined counts [1, 2], and the byte that examined the most is 99 (correct)
    position 1: examined counts [2, 3], and the byte that examined the most is 111 (correct)
    position 2: examined counts [3, 4], and the byte that examined the most is 114 (correct)

  the positions the early-exit comparison could not recover
    position 27 of 28: every one of the 256 guesses examined [28] bytes

  both comparisons were probed the same number of times. the
  difference is not the cost of the attack, it is what a probe
  tells you: the early-exit comparison produces a number that
  varies with the position, and the constant one produces the same
  number for all of them.

  the early-exit comparison recovered all but one byte, and the
  byte it missed is the last one -- because there is no byte after
  it to differ at. a wrong guess at the final position examines
  the same number of bytes as a right one, so nothing ranks them.
  that is a property of the method rather than of the comparison:
  append a byte to the guess and the last position becomes
  recoverable like the others.

  the second count is the one that matters. the constant
  comparison recovered zero bytes -- not because it is hard to
  break, but because every wrong guess looks exactly like every
  other wrong guess, so there is nothing to rank them by.

  `hmac.compare_digest` is the standard library's version of the
  second function, written in C so that no interpreter detail can
  reintroduce the early exit. reach for it rather than writing one.
```

A 28-byte secret, 256 candidates per position, 7168 probes per attack, run against two comparisons.
Both were probed the same number of times. The difference is not the cost of the attack; it is what a
probe tells you. The early-exit comparison produced a number that varies with the position, and the
constant one produced the same number for all of them.

The early-exit comparison recovered 27 of the 28 bytes, and the byte it missed is the last one,
because there is no byte after it to differ at. A wrong guess at the final position examines the same
number of bytes as a right one, so nothing ranks them. That is a property of the method rather than
of the comparison -- append a byte to the guess and the last position becomes recoverable like the
others.

The second count is the one that matters. The constant comparison recovered zero bytes, not because
it is hard to break, but because every wrong guess looks exactly like every other wrong guess. The
standard library's version is `hmac.compare_digest`, written in C so that no interpreter detail can
reintroduce the early exit. Reach for it rather than writing one.

## The file that must not be in the repository

Everything so far has been about a value arriving. This is about a value that should never have been
there, and about the fact that finding it is a detection problem rather than a design one.

```python run
"""Chapter 53 -- secret scanning.

Three detectors over twelve config lines. The credential-shaped values
are built from a seeded generator rather than written out, so that this
file -- which is published -- contains no string that a secret scanner
would flag, and so that the sample values are identical on every machine.
Nothing here prints a full value; the report shows a redaction, which is
what a scanner report is supposed to show.
"""

import math
import re
import string

HEX = "0123456789abcdef"
ALNUM = string.ascii_letters + string.digits
UPPER = string.ascii_uppercase + string.digits
BASE64 = string.ascii_letters + string.digits + "+/"


class Stream:
    """A linear congruential generator, so the samples are the same
    everywhere. The high bits are used because the low bits of an LCG
    are the ones with the short period."""

    def __init__(self, seed):
        self.state = seed & 0x7FFFFFFF

    def _step(self):
        self.state = (1103515245 * self.state + 12345) & 0x7FFFFFFF
        return self.state

    def body(self, n, alphabet):
        out = []
        for _ in range(n):
            out.append(alphabet[(self._step() >> 15) % len(alphabet)])
        return "".join(out)


S = Stream(53)

# --- the twelve lines -------------------------------------------------
#
# (name, value, does it really carry a credential)
LINES = [
    ("DB_PASSWORD", "hunter2", True),
    ("STRIPE_KEY", "sk-" + S.body(24, ALNUM), True),
    ("AWS_ACCESS_KEY_ID", "AKIA" + S.body(16, UPPER), True),
    ("SESSION_SIGNING_KEY", S.body(32, HEX), True),
    ("OAUTH_CLIENT_SECRET", S.body(30, BASE64), True),
    ("WEBHOOK_URL", "https://hooks.internal/services/" + S.body(32, BASE64), True),
    ("BUILD_HASH", S.body(40, HEX), False),
    ("REQUEST_ID_SALT", S.body(24, ALNUM), False),
    ("CDN_ASSET_DIGEST", S.body(64, HEX), False),
    ("TOKEN_BUDGET", "5000", False),
    ("LOG_LEVEL", "info", False),
    ("REGION", "eu-west-1", False),
]

# --- the three detectors ----------------------------------------------

# one: a list of formats someone wrote down, after an incident
PREFIXES = ["sk-", "pk_", "ghp_", "xoxb-", "AKIA", "ASIA"]
PREFIX = re.compile("|".join(re.escape(p) for p in PREFIXES) + r"[A-Za-z0-9]{12,}")

# two: the name of the setting, and not its value at all
KEYWORD = re.compile(r"password|passwd|secret|token|api[_-]?key|signing", re.I)

# three: find a candidate token, then ask how surprising it is
TOKEN = re.compile(r"[A-Za-z0-9_\-+/]{16,}")
# 3.0 sits between the two populations rather than on top of either: a
# word-shaped password measures about 2.8, a random hex string about 3.5.
ENTROPY_FLOOR = 3.0


def entropy(value):
    if not value:
        return 0.0
    counts = {}
    for ch in value:
        counts[ch] = counts.get(ch, 0) + 1
    n = len(value)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def detect(name, value):
    candidate = TOKEN.search(value)
    return {
        "prefix": bool(PREFIX.search(value)),
        "keyword": bool(KEYWORD.search(name)),
        "entropy": bool(candidate) and entropy(candidate.group(0)) >= ENTROPY_FLOOR,
    }


def redact(value):
    """A scanner report shows enough to find the line and not enough to
    use the value."""
    return value[:4] + "\u2026" if len(value) > 8 else value


DETECTORS = ["prefix", "keyword", "entropy"]
FOUND = {name: detect(name, value) for name, value, _ in LINES}
REAL = [(n, v) for n, v, real in LINES if real]
FAKE = [(n, v) for n, v, real in LINES if not real]


def hits(pairs, detector):
    return [n for n, v in pairs if FOUND[n][detector]]


def main():
    print(f"  config lines                       {len(LINES):>3}")
    print(f"  lines that really carry one         {len(REAL):>3}")
    print()

    print("    line                    prefix  keyword  entropy  reported as")
    for name, value, real in LINES:
        d = FOUND[name]
        mark = {"prefix": "yes", "keyword": "yes", "entropy": "yes"}
        row = "    {:<22}".format(name)
        for key in DETECTORS:
            row += "{:>7}".format(mark[key] if d[key] else "-")
        row += "  " + redact(value)
        print(row)
    print()

    print("    detector     of the %d   false alarms" % len(REAL))
    union = set()
    for key in DETECTORS:
        got = hits(REAL, key)
        union.update(got)
        print("    {:<10}{:>9}{:>14}".format(key, len(got), len(hits(FAKE, key))))
    print("    {:<10}{:>9}{:>14}".format("all three", len(union), len(
        [n for n, v in FAKE if any(FOUND[n][k] for k in DETECTORS)])))
    print()

    print("  what each detector missed")
    for key in DETECTORS:
        missed = [n for n, v in REAL if not FOUND[n][key]]
        print("    {:<9} {}".format(key, "  ".join(missed) if missed else "(nothing)"))
    print()

    print("  what each detector flagged that is not a credential")
    for key in DETECTORS:
        wrong = hits(FAKE, key)
        print("    {:<9} {}".format(key, "  ".join(wrong) if wrong else "(nothing)"))
    print()

    print("  the three detectors are not three attempts at the same thing.")
    print("  they look at different parts of the line.")
    print()
    print("  the prefix detector reads the value and knows a handful of")
    print(f"  formats. it found {len(hits(REAL, 'prefix'))} of the {len(REAL)} and raised "
          f"{len(hits(FAKE, 'prefix'))}")
    print("  false alarms -- because a format it does not have written")
    print("  down is invisible to it, and the formats are issued by")
    print("  whoever runs the service.")
    print()
    by_kw = [n for n, v in REAL if not FOUND[n]["keyword"]]
    purpose_named = [n for n in by_kw if "KEY" not in n.upper()]
    key_named = [n for n in by_kw if "KEY" in n.upper()]
    print("  the keyword detector reads the name and not the value at")
    print(f"  all. it found {len(hits(REAL, 'keyword'))} of the {len(REAL)}. one of the misses is")
    print(f"  `{purpose_named[0]}`, a credential whose name describes what")
    print("  it is for rather than what it is -- and the name is chosen")
    print("  by whoever wrote the config, so this detector's recall is")
    print("  a property of other people's habits. the other "
          f"{len(key_named)} are")
    print("  " + " and ".join("`" + n + "`" for n in key_named) + ",")
    print("  both of which have \"key\" in the name: the list holds")
    print("  `api key` and not `key`, because a bare `key` flags every")
    print("  config file that has one. the detector is exactly as wide")
    print("  as the words someone chose, and it also flagged")
    print(f"  `{hits(FAKE, 'keyword')[0]}`, which is a number.")
    print()
    by_ent = [n for n, v in REAL if not FOUND[n]["entropy"]]
    print("  the entropy detector reads the value and knows nothing about")
    print(f"  formats or names. it found {len(hits(REAL, 'entropy'))} of the {len(REAL)} and flagged")
    print(f"  {len(hits(FAKE, 'entropy'))} of the {len(FAKE)} that are not credentials, because a")
    print("  build hash is a random string and so is a key. it is the")
    print("  only one that finds a credential nobody has seen before,")
    print("  and the only one that cannot tell one from a checksum.")
    if by_ent:
        print(f"  the one it misses is `{by_ent[0]}`, and its value is a word:")
        print("  entropy is high when the characters vary, and a password a")
        print("  person chose is the one value in this file that does not.")
    print()
    print(f"  the union finds all {len(union)} and costs "
          f"{len([n for n, v in FAKE if any(FOUND[n][k] for k in DETECTORS)])} false alarms --")
    print("  and what all three depend on is the same thing: a corpus")
    print("  someone chose. that is the blocklist argument from the")
    print("  injection chapter, and it ends the same way. detection is a")
    print("  backstop for a credential that has already leaked. the fix")
    print("  is that it was never in the file.")


main()
```

```text
  config lines                        12
  lines that really carry one           6

    line                    prefix  keyword  entropy  reported as
    DB_PASSWORD                 -    yes      -  hunter2
    STRIPE_KEY                yes      -    yes  sk-m…
    AWS_ACCESS_KEY_ID         yes      -    yes  AKIA…
    SESSION_SIGNING_KEY         -    yes    yes  7c51…
    OAUTH_CLIENT_SECRET         -    yes    yes  muMr…
    WEBHOOK_URL                 -      -    yes  http…
    BUILD_HASH                  -      -    yes  553f…
    REQUEST_ID_SALT             -      -    yes  yqny…
    CDN_ASSET_DIGEST            -      -    yes  5137…
    TOKEN_BUDGET                -    yes      -  5000
    LOG_LEVEL                   -      -      -  info
    REGION                      -      -      -  eu-w…

    detector     of the 6   false alarms
    prefix            2             0
    keyword           3             1
    entropy           5             3
    all three         6             4

  what each detector missed
    prefix    DB_PASSWORD  SESSION_SIGNING_KEY  OAUTH_CLIENT_SECRET  WEBHOOK_URL
    keyword   STRIPE_KEY  AWS_ACCESS_KEY_ID  WEBHOOK_URL
    entropy   DB_PASSWORD

  what each detector flagged that is not a credential
    prefix    (nothing)
    keyword   TOKEN_BUDGET
    entropy   BUILD_HASH  REQUEST_ID_SALT  CDN_ASSET_DIGEST

  the three detectors are not three attempts at the same thing.
  they look at different parts of the line.

  the prefix detector reads the value and knows a handful of
  formats. it found 2 of the 6 and raised 0
  false alarms -- because a format it does not have written
  down is invisible to it, and the formats are issued by
  whoever runs the service.

  the keyword detector reads the name and not the value at
  all. it found 3 of the 6. one of the misses is
  `WEBHOOK_URL`, a credential whose name describes what
  it is for rather than what it is -- and the name is chosen
  by whoever wrote the config, so this detector's recall is
  a property of other people's habits. the other 2 are
  `STRIPE_KEY` and `AWS_ACCESS_KEY_ID`,
  both of which have "key" in the name: the list holds
  `api key` and not `key`, because a bare `key` flags every
  config file that has one. the detector is exactly as wide
  as the words someone chose, and it also flagged
  `TOKEN_BUDGET`, which is a number.

  the entropy detector reads the value and knows nothing about
  formats or names. it found 5 of the 6 and flagged
  3 of the 6 that are not credentials, because a
  build hash is a random string and so is a key. it is the
  only one that finds a credential nobody has seen before,
  and the only one that cannot tell one from a checksum.
  the one it misses is `DB_PASSWORD`, and its value is a word:
  entropy is high when the characters vary, and a password a
  person chose is the one value in this file that does not.

  the union finds all 6 and costs 4 false alarms --
  and what all three depend on is the same thing: a corpus
  someone chose. that is the blocklist argument from the
  injection chapter, and it ends the same way. detection is a
  backstop for a credential that has already leaked. the fix
  is that it was never in the file.
```

Twelve config lines, six of which really carry a credential, against three detectors. The prefix
detector found 2 of the 6 and raised 0 false alarms. The keyword detector found 3 and raised 1. The
entropy detector found 5 and raised 3. The union found all 6 and cost 4.

The three are not three attempts at the same thing; they read different parts of the line. The prefix
detector reads the value and knows a handful of formats, which is why its precision is perfect and
its recall is the worst of the three -- a format it does not have written down is invisible to it,
and the formats are issued by whoever runs the service.

The keyword detector reads the name and not the value at all. One of the three it misses is
`WEBHOOK_URL`, a credential whose name describes what it is for rather than what it is, and the name
is chosen by whoever wrote the config. The other two have "key" in the name: the list holds `api key`
and not `key`, because a bare `key` flags every config file that has one. The detector is exactly as
wide as the words somebody chose.

The entropy detector reads the value and knows nothing about formats or names. It found 5 of the 6
and flagged 3 of the 6 that are not credentials, because a build hash is a random string and so is a
key. It is the only one that finds a credential nobody has seen before, and the only one that cannot
tell one from a checksum. The one it misses is a password whose value is a word, which is what a
password a person chose looks like.

The union finds all six and costs four false alarms, and what all three depend on is the same thing:
a corpus somebody chose. That is the blocklist argument from the injection chapter, and it ends the
same way. Detection is a backstop for a credential that has already leaked. The fix is that it was
never in the file.

## What runs when you install

The last section before the callouts is the one where the code you are responsible for is not the
code you wrote.

```python run
"""Chapter 53 -- the dependency supply chain.

What you install, what runs when you install it, and the two checks that
are not name checks. The resolution counts are computed from a small
version set rather than asserted, so they move if the version set does.
"""

import itertools

# --- the resolution surface -------------------------------------------

PACKAGES = {
    "pdf-toolkit": ["1.0", "1.1", "1.2", "2.0", "2.1"],
    "color-picker": ["1.0", "1.1", "1.2", "2.0", "2.1"],
    "json-schema": ["1.0", "1.1", "1.2", "2.0", "2.1"],
}


def satisfying(package, constraint):
    out = []
    for v in PACKAGES[package]:
        major = int(v.split(".")[0])
        if constraint == "any":
            out.append(v)
        elif constraint == "major 1" and major == 1:
            out.append(v)
        elif constraint.startswith("==") and v == constraint[2:]:
            out.append(v)
    return out


def surface(spec):
    """The number of distinct sets of versions a fresh install can land on."""
    pools = [satisfying(p, c) for p, c in spec.items()]
    if any(not pool for pool in pools):
        return 0
    return len(list(itertools.product(*pools)))


SPECS = [
    ("no constraint", {p: "any" for p in PACKAGES}, "accepted"),
    ("major 1 only", {p: "major 1" for p in PACKAGES}, "accepted"),
    ("one package pinned", {"pdf-toolkit": "==1.1",
                            "color-picker": "any", "json-schema": "any"},
     "accepted"),
    ("every package pinned", {p: "==1.1" for p in PACKAGES}, "accepted"),
    ("a lock file with hashes", {p: "==1.1" for p in PACKAGES}, "refused"),
]


# --- what runs when you install ---------------------------------------

INSTALL_STEPS = [
    ("python, sdist", "runs the build backend", True),
    ("python, wheel", "unpacks an archive", False),
    ("npm", "runs preinstall, install, postinstall", True),
    ("cargo", "compiles and runs build.rs", True),
    ("go modules", "verifies a checksum", False),
    ("apt / deb", "runs preinst and postinst, as root", True),
]


# --- name checks -------------------------------------------------------

REAL = ["pdf-toolkit", "color-picker", "json-schema", "snowflake-client"]

CANDIDATES = [
    "pdf-toolklt",
    "pdf-toolkitt",
    "pdf-toolkit-pro",
    "colorpicker",
    "color-picker-js",
    "json-chema",
    "json-schemas",
    "snowfake-client",
    "snowflake-clinet",
    "snowflake_client",
    "snowflake-api",
]


def levenshtein(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def nearest(name):
    best = min(REAL, key=lambda r: levenshtein(name, r))
    return best, levenshtein(name, best)


def main():
    print("    requirements                 resolutions   a replaced artifact")
    for label, spec, replaced in SPECS:
        print("    {:<29}{:>11}   {}".format(label, surface(spec), replaced))
    print()
    print("  the last two rows have the same number and are not the same")
    print("  thing. a version is a name the publisher chooses and can move;")
    print("  a hash is the bytes. pinning every version narrows the surface")
    print("  to one and still installs whatever is served under that")
    print("  version -- which is the row above it, with a smaller number.")
    print()

    print("    install step                 what the step does")
    for name, what, runs in INSTALL_STEPS:
        print("    {:<29}{}{}".format(name, what,
                                    "" if runs else "  (no package code)"))
    running = [n for n, _, runs in INSTALL_STEPS if runs]
    print()
    print(f"  {len(running)} of the {len(INSTALL_STEPS)} run code the package author wrote,")
    print("  and none of them ask. the two that do not are the two that")
    print("  install a built artefact or check a checksum, and that is the")
    print("  only reason they are different.")
    print()

    print("    candidate name            nearest real name    distance")
    flagged, missed = [], []
    for name in CANDIDATES:
        real, d = nearest(name)
        print("    {:<25}{:<21}{:>2}".format(name, real, d))
        (flagged if d <= 1 else missed).append((name, real, d))
    print()
    print("  a check that flags anything within one edit of a name you")
    print(f"  already use catches {len(flagged)} of the {len(CANDIDATES)} and misses "
          f"{len(missed)}.")
    print()
    print("  the misses are two different kinds. one kind keeps the name")
    print("  you know and changes the part after it:")
    for name, real, d in missed:
        if d > 2 and name.startswith(real.split("-")[0]):
            print(f"    {name}")
    print("  those are the more convincing ones, because they look like an")
    print("  edition of something already in the file. the other kind is a")
    print("  transposition:")
    for name, real, d in missed:
        if d == 2:
            print(f"    {name}  (distance {d} from {real})")
    print("  a swapped pair of letters is two edits, not one, so the check")
    print("  misses the single most common typo there is. a blocklist of")
    print("  names known to be bad would catch 0 of these, because every")
    print("  one of them was fine on the day it was written.")
    print()

    print("  what the two rows above are really about")
    mirrors = 3
    print(f"    artifacts the index can serve for one version   {mirrors}")
    print(f"    accepted without a hash                         {mirrors}")
    print("    accepted with a hash                            1")
    print()
    print("  the name is the part the attacker chooses, and both of the")
    print("  checks above are checks on the name. the hash is the only one")
    print("  that is not, because it is a statement about the artefact")
    print("  rather than about who published it -- and that is also why it")
    print("  is the only one that has to be generated by someone who")
    print("  already had the artefact.")


main()
```

```text
    requirements                 resolutions   a replaced artifact
    no constraint                        125   accepted
    major 1 only                          27   accepted
    one package pinned                    25   accepted
    every package pinned                   1   accepted
    a lock file with hashes                1   refused

  the last two rows have the same number and are not the same
  thing. a version is a name the publisher chooses and can move;
  a hash is the bytes. pinning every version narrows the surface
  to one and still installs whatever is served under that
  version -- which is the row above it, with a smaller number.

    install step                 what the step does
    python, sdist                runs the build backend
    python, wheel                unpacks an archive  (no package code)
    npm                          runs preinstall, install, postinstall
    cargo                        compiles and runs build.rs
    go modules                   verifies a checksum  (no package code)
    apt / deb                    runs preinst and postinst, as root

  4 of the 6 run code the package author wrote,
  and none of them ask. the two that do not are the two that
  install a built artefact or check a checksum, and that is the
  only reason they are different.

    candidate name            nearest real name    distance
    pdf-toolklt              pdf-toolkit           1
    pdf-toolkitt             pdf-toolkit           1
    pdf-toolkit-pro          pdf-toolkit           4
    colorpicker              color-picker          1
    color-picker-js          color-picker          3
    json-chema               json-schema           1
    json-schemas             json-schema           1
    snowfake-client          snowflake-client      1
    snowflake-clinet         snowflake-client      2
    snowflake_client         snowflake-client      1
    snowflake-api            snowflake-client      5

  a check that flags anything within one edit of a name you
  already use catches 7 of the 11 and misses 4.

  the misses are two different kinds. one kind keeps the name
  you know and changes the part after it:
    pdf-toolkit-pro
    color-picker-js
    snowflake-api
  those are the more convincing ones, because they look like an
  edition of something already in the file. the other kind is a
  transposition:
    snowflake-clinet  (distance 2 from snowflake-client)
  a swapped pair of letters is two edits, not one, so the check
  misses the single most common typo there is. a blocklist of
  names known to be bad would catch 0 of these, because every
  one of them was fine on the day it was written.

  what the two rows above are really about
    artifacts the index can serve for one version   3
    accepted without a hash                         3
    accepted with a hash                            1

  the name is the part the attacker chooses, and both of the
  checks above are checks on the name. the hash is the only one
  that is not, because it is a statement about the artefact
  rather than about who published it -- and that is also why it
  is the only one that has to be generated by someone who
  already had the artefact.
```

The first table is the size of the surface you did not choose. Five published versions of three
packages is 125 distinct sets of versions a fresh install can land on. A major-version constraint
takes it to 27, pinning one package to 25, and pinning all three to 1.

The last two rows have the same number and are not the same thing. A version is a name the publisher
chooses and can move; a hash is the bytes. Pinning every version narrows the surface to one and still
installs whatever is served under that version, which is why the row above it is the same number with
a different answer in the last column.

The second table is what happens at install. Four of the six steps run code the package author wrote,
and none of them ask. The two that do not are the two that install a built artefact or check a
checksum, and that is the only reason they are different.

The third is a name check, and it is the part that generalises. A check that flags anything within
one edit of a name you already use caught 7 of 11. The misses are two kinds: names that keep the name
you know and change the part after it, which are the more convincing ones because they look like an
edition of something already in your file; and a transposition, which is two edits rather than one,
so the check misses the single most common typo there is. A blocklist of known-bad names would catch
none of them, because every one of them was fine on the day it was written.

:::pitfall The log that is a copy of the request

Every section so far has had a defence. This one is the category where the defence is a decision
rather than a mechanism, and it is the last of the OWASP top ten for that reason.

A service logging ten event types over sixty requests.

```python run
#!/usr/bin/env python3
"""Chapter 53 demo, part 8 -- the log that leaks what it should record.

Logging and monitoring failures are the OWASP category with no syntax-level fix,
which is why they are easy to leave out of a chapter like this and why they
belong in it. The category is usually described as "you did not log enough",
and half the problem runs the other way.

Ten event types, sixty requests. For each type: does the application write a
line, does the line carry a credential, and is the event one an incident review
would need.
"""
# name, requests, is a line written, does the line carry a credential,
# is the event security-relevant
EVENTS = [
    ("login success", 12, True, True, True),
    ("login failure", 8, True, True, True),
    ("password reset", 2, True, True, True),
    ("token refresh", 10, True, True, False),
    ("page view", 15, True, False, False),
    ("note created", 6, True, False, False),
    ("permission denied", 3, False, False, True),
    ("role changed", 1, False, False, True),
    ("account locked", 2, False, False, True),
    ("export downloaded", 1, True, False, True),
]


def main():
    total = sum(n for _e, n, _l, _s, _r in EVENTS)
    print(f"  event types                        {len(EVENTS):>3}")
    print(f"  requests                           {total:>3}")
    print()
    print(f"    {'event':<20}{'count':>6}{'logged':>8}{'credential':>12}"
          f"{'needed':>8}")

    lines = 0
    leaky = 0
    needed = 0
    needed_logged = 0
    silent = []
    for name, count, logged, sensitive, relevant in EVENTS:
        if logged:
            lines += count
            if sensitive:
                leaky += count
        if relevant:
            needed += count
            if logged:
                needed_logged += count
            else:
                silent.append((name, count))
        print(f"    {name:<20}{count:>6}{'yes' if logged else 'no':>8}"
              f"{'yes' if sensitive else '-':>12}"
              f"{'yes' if relevant else '-':>8}")

    print()
    print(f"  lines written                      {lines:>3} of {total}")
    print(f"  lines carrying a credential        {leaky:>3} of {lines}")
    print(f"  security-relevant requests         {needed:>3}")
    print(f"  of those, requests with no line    "
          f"{needed - needed_logged:>3}")

    print()
    print("  security-relevant events that leave no trace at all")
    for name, count in silent:
        print(f"    {name:<20}{count}")

    print()
    print("  two numbers, and they are opposite problems in the same file.")
    print()
    print(f"  {leaky} of the {lines} lines written carry a credential, because")
    print("  the line is built from the request body and the request body is")
    print("  where the password is. the log is the most copied artefact in an")
    print("  incident and the least protected one in most systems.")
    print()
    print(f"  and {needed - needed_logged} of the {needed} requests an incident")
    print("  review would need produced no line, because nobody decided they")
    print("  should. the ones missing are the failures and the changes: a")
    print("  refusal, a role change, a lockout. those are the events that")
    print("  describe an attack, and they are the ones nobody is watching")
    print("  for, because a successful request is the thing the log was")
    print("  built to record.")
    print()
    print("  the fix for the first is a field allow-list rather than a body")
    print("  dump. the fix for the second is a list of events that must")
    print("  always produce a line, written down and tested like any other")
    print("  requirement -- which is the whole of the category, and the")
    print("  reason it has no syntax-level fix.")


if __name__ == "__main__":
    main()
```

```text
  event types                         10
  requests                            60

    event                count  logged  credential  needed
    login success           12     yes         yes     yes
    login failure            8     yes         yes     yes
    password reset           2     yes         yes     yes
    token refresh           10     yes         yes       -
    page view               15     yes           -       -
    note created             6     yes           -       -
    permission denied        3      no           -     yes
    role changed             1      no           -     yes
    account locked           2      no           -     yes
    export downloaded        1     yes           -     yes

  lines written                       54 of 60
  lines carrying a credential         32 of 54
  security-relevant requests          29
  of those, requests with no line      6

  security-relevant events that leave no trace at all
    permission denied   3
    role changed        1
    account locked      2

  two numbers, and they are opposite problems in the same file.

  32 of the 54 lines written carry a credential, because
  the line is built from the request body and the request body is
  where the password is. the log is the most copied artefact in an
  incident and the least protected one in most systems.

  and 6 of the 29 requests an incident
  review would need produced no line, because nobody decided they
  should. the ones missing are the failures and the changes: a
  refusal, a role change, a lockout. those are the events that
  describe an attack, and they are the ones nobody is watching
  for, because a successful request is the thing the log was
  built to record.

  the fix for the first is a field allow-list rather than a body
  dump. the fix for the second is a list of events that must
  always produce a line, written down and tested like any other
  requirement -- which is the whole of the category, and the
  reason it has no syntax-level fix.
```

Two numbers, and they are opposite problems in the same file. 32 of the 54 lines written carry a
credential, because the line is built from the request body and the request body is where the
password is. And 6 of the 29 requests an incident review would need produced no line at all.

The log is the most copied artefact in an incident and the least protected one in most systems, which
is why the first number is the one that gets fixed. The second is the one that matters more. The
events with no line are a refusal, a role change and a lockout -- the events that describe an attack
-- and they are missing because nobody decided they should be there. A successful request is what the
log was built to record, and an attack is made of the ones that failed.

The fix for the first is a field allow-list rather than a body dump. The fix for the second is a list
of events that must always produce a line, written down and tested like any other requirement. That
second list is the whole of the category, and it is also why the category has no syntax-level fix:
nothing in the code is wrong, and the thing that is missing is missing from the output you would
check it against.

:::

:::scenario The password reset link

A reset link is the feature to end on, because it is small, it is in every application, and it walks
through most of this chapter on its own. It takes an address, mails a token, accepts the token back,
lets the holder set a new password, and redirects them somewhere afterwards.

Six mistakes are available to it, and they are in six different places.

```python run
"""Chapter 53 -- the scenario.

One feature, the password reset link, and the six mistakes it can make.
Each design adds fixes and the fixes live in different parts of the
flow, which is the point: the six are in six places and no two of them
are in the same file.
"""

SECRET = "0123456789abcdef"


def probes(guess, secret, constant):
    """How many bytes the comparison examines before it answers."""
    if constant:
        return len(secret)
    for i in range(min(len(guess), len(secret))):
        if guess[i] != secret[i]:
            return i + 1
    return min(len(guess), len(secret)) + 1


def wrong_guesses(secret):
    out = []
    for i in range(len(secret)):
        c = "z" if secret[i] != "z" else "y"
        out.append(secret[:i] + c + secret[i + 1:])
    return out


def observe(fixes):
    """The mistakes this design makes, in the order the flow reaches them."""
    made = []

    # the reply to a reset request, for an address that exists and for
    # one that does not
    replies = ["a link has been sent", "a link has been sent"]
    if "uniform response" not in fixes:
        replies[1] = "no account with that address"
    if replies[0] != replies[1]:
        made.append("the reply says whether the account exists")

    # the token comparison
    counts = [probes(g, SECRET, "constant-time" in fixes)
              for g in wrong_guesses(SECRET)]
    if len(set(counts)) > 1:
        made.append("the comparison stops at the first difference")

    # the token, presented a second time
    if "single-use token" not in fixes:
        made.append("the token still works a second time")

    # a session that was opened before the reset
    if "invalidate sessions" not in fixes:
        made.append("the old session survives the reset")

    # the target the reset form redirects to
    target = "//evil.com"
    if "redirect allow-list" not in fixes and target.startswith("//"):
        made.append("the redirect target comes from the request")

    # the line written when the reset completes
    if "field allow-list" not in fixes:
        made.append("the log line is built from the request body")

    return made


MISTAKES = [
    ("the reply says whether the account exists", "the handler"),
    ("the comparison stops at the first difference", "the comparison"),
    ("the token still works a second time", "the token store"),
    ("the old session survives the reset", "the session store"),
    ("the redirect target comes from the request", "the redirect"),
    ("the log line is built from the request body", "the logger"),
]

DESIGNS = [
    ("A", set()),
    ("B", {"constant-time"}),
    ("C", {"constant-time", "single-use token", "invalidate sessions"}),
    ("D", {"constant-time", "single-use token", "invalidate sessions",
           "uniform response", "redirect allow-list", "field allow-list"}),
]


def main():
    print(f"  mistakes the feature can make       {len(MISTAKES)}")
    print(f"  places they live in                 "
          f"{len(set(place for _, place in MISTAKES))}")
    print(f"  designs                             {len(DESIGNS)}")
    print()

    print("    {:<45}".format("mistake") +
          "".join("{:>7}".format(name) for name, _ in DESIGNS))
    made_by = {}
    for label, fixes in DESIGNS:
        made_by[label] = observe(fixes)
    for text, _ in MISTAKES:
        row = "    {:<45}".format(text)
        for label, _ in DESIGNS:
            row += "{:>7}".format("made" if text in made_by[label] else "-")
        print(row)
    print()
    print("    {:<45}".format("mistakes made") +
          "".join("{:>7}".format(len(made_by[label])) for label, _ in DESIGNS))
    print()

    counts = [probes(g, SECRET, False) for g in wrong_guesses(SECRET)]
    flat = [probes(g, SECRET, True) for g in wrong_guesses(SECRET)]
    print("  the comparison, for each of the "
          f"{len(counts)} single-byte-wrong guesses")
    for label, values in (("stopping at the first difference", counts),
                          ("always the whole secret", flat)):
        print("    " + label)
        for i in range(0, len(values), 8):
            print("      " + " ".join("{:>2}".format(v)
                                      for v in values[i:i + 8]))
    print()
    print(f"  the first row takes {len(set(counts))} different values and the second "
          f"takes {len(set(flat))},")
    print("  so the answer is a function of the guess in one of them and not")
    print("  in the other. that is the whole of the attack: the reply is")
    print("  still only yes or no, and the *work* behind it is what leaks.")
    print()

    print("    {:<46}{}".format("mistake", "the fix goes in"))
    for text, place in MISTAKES:
        print("    {:<46}{}".format(text, place))
    print()
    print(f"  {len(MISTAKES)} mistakes, "
          f"{len(set(place for _, place in MISTAKES))} places, and the four designs are")
    print("  not four versions of one decision. each column adds a fix")
    print("  somewhere else in the flow, and a review that reads one file")
    print("  finds the mistakes that happen to be in that file.")
    print()
    print("  that is why this chapter is not a list of topics. every one of")
    print("  these is a place, and a feature is the unit that reaches all of")
    print("  them -- which also means the only way to check a feature is to")
    print("  walk it from the request to the row and to the log, and ask at")
    print("  each step which parser or which check is reading the value now.")


main()
```

```text
  mistakes the feature can make       6
  places they live in                 6
  designs                             4

    mistake                                            A      B      C      D
    the reply says whether the account exists       made   made   made      -
    the comparison stops at the first difference    made      -      -      -
    the token still works a second time             made   made      -      -
    the old session survives the reset              made   made      -      -
    the redirect target comes from the request      made   made   made      -
    the log line is built from the request body     made   made   made      -

    mistakes made                                      6      5      3      0

  the comparison, for each of the 16 single-byte-wrong guesses
    stopping at the first difference
       1  2  3  4  5  6  7  8
       9 10 11 12 13 14 15 16
    always the whole secret
      16 16 16 16 16 16 16 16
      16 16 16 16 16 16 16 16

  the first row takes 16 different values and the second takes 1,
  so the answer is a function of the guess in one of them and not
  in the other. that is the whole of the attack: the reply is
  still only yes or no, and the *work* behind it is what leaks.

    mistake                                       the fix goes in
    the reply says whether the account exists     the handler
    the comparison stops at the first difference  the comparison
    the token still works a second time           the token store
    the old session survives the reset            the session store
    the redirect target comes from the request    the redirect
    the log line is built from the request body   the logger

  6 mistakes, 6 places, and the four designs are
  not four versions of one decision. each column adds a fix
  somewhere else in the flow, and a review that reads one file
  finds the mistakes that happen to be in that file.

  that is why this chapter is not a list of topics. every one of
  these is a place, and a feature is the unit that reaches all of
  them -- which also means the only way to check a feature is to
  walk it from the request to the row and to the log, and ask at
  each step which parser or which check is reading the value now.
```

Four designs. The first makes all six. Adding a constant-time comparison takes it to five; adding a
single-use token and invalidating the sessions takes it to three; and the last one, which also makes
the reply uniform, restricts the redirect target and allow-lists the logged fields, reaches zero.

Read the columns as places rather than as strengths. The comparison is in the comparison, the
single-use token is in the token store, the invalidation is in the session store, the uniform reply
is in the handler, the redirect target is in the redirect, and the logged fields are in the logger. A
review that reads one file finds the mistakes that happen to be in that file, and a feature is the
unit that reaches all of them.

The comparison evidence underneath is the part that is measured rather than counted. Sixteen
single-byte-wrong guesses, and the early-exit comparison takes sixteen different numbers of bytes to
answer them while the constant one takes one. The reply is still only yes or no. What leaked was the
work behind it, which is the same shape as the timing section and the same shape as the blocklist:
the thing that is observable is not the thing you were thinking about.

:::

## Key takeaways

- **The escaping question is which parser reads the value, not which characters are dangerous.** Four
  contexts, one escaper, 8 of 24 renders broken raw and 2 of 24 broken after escaping.
- **`html.escape` escapes the four characters that end a string.** In an unquoted attribute there is
  no string to end, so the payload needs a space, and a space is not one of the four.
- **The fix for an unquoted attribute is a pair of quotes, not a stronger encoder.** Where the value
  goes is the first decision; the escaper is the second one.
- **`SameSite=Lax` sends on exactly one cross-site shape: a top-level navigation with a safe method.**
  That exception is why state changes must not be GETs.
- **`SameSite=None` is not a weaker `Lax`.** It sent on all eight shapes. It is the absence of the
  protection, and something else is doing the work.
- **A check on the name is not a check on where the connection goes.** Three string checks accepted 3,
  3 and 2 of fourteen hostile URLs, and each removed a class of a different kind.
- **A hostname check is not a scheme check.** Two of the URLs the hostname comparisons accepted used
  schemes that were not https at all.
- **The check that looks correct is the one to test.** Asking whether `urlparse` found a netloc
  accepted 7 of 9 hostile targets -- more than the check it replaced, because an unrecognised URL
  leaves the netloc empty.
- **A validator has to know what the consumer treats as a separator.** The percent-encoded target was
  accepted by every check here and decoded by the browser.
- **Authentication and authorization are two questions, and only one of them is usually asked.** Four
  of twelve endpoint-and-caller pairs leaked, and one leaking endpoint had a correct guard.
- **A correct guard can still leak.** A list endpoint that requires a session and returns every row is
  a leak; the question is which rows the answer may contain, and that check lives where the rows are
  read.
- **A password change is not a session event, and it has to be.** Five attacks, four settings, and the
  one that survives all four settings is the one that is not in the session code.
- **Uniqueness is not unpredictability.** Every token generator measured was 1000 distinct out of
  1000, and a counter and a seeded PRNG were both reproduced in full by an attacker who never saw one.
- **An early-exit comparison recovered 27 of 28 bytes.** It misses the last one because there is no
  byte after it to differ at -- a property of the method, and appending a byte makes it recoverable.
- **A constant comparison recovered zero, and that is the point.** Every wrong guess looks like every
  other wrong guess, so there is nothing to rank them by. Use `hmac.compare_digest`.
- **Detection is not prevention, and it is still worth measuring.** Three secret detectors found 2, 3
  and 5 of six real credentials, at a cost of 0, 1 and 3 false alarms.
- **A detector is exactly as wide as the words somebody chose.** The keyword list held `api key` and
  not `key`, and the name of a credential is chosen by whoever wrote the config.
- **125 sets of versions become 27, then 25, then 1, and the last two rows are not the same thing.** A
  version is a name the publisher can move; a hash is the bytes.
- **Four of six install steps run code the package author wrote, and none of them ask.** The two that
  do not are the two that install a built artefact or check a checksum.
- **A log built from the request body is a copy of the request.** 32 of 54 lines carried a credential,
  and 6 of the 29 requests an incident would need produced no line at all -- including every refusal.

## Practice

- [ ] **Test an escaper by context rather than by character.** Take a page in a project of yours and
  find every place a user-supplied value is rendered. Classify each one by the parser that reads it:
  element body, quoted attribute, unquoted attribute, URL, JavaScript string, CSS, a header. Then
  write six payloads per context and record which of them break out. Report the number of contexts
  your current escaper covers, and the ones it does not -- the answer is usually that it covers the
  two you thought of.
- [ ] **Walk a redirect parameter to the end.** Find a `next`, `return_to` or `redirect_uri`
  parameter in a project of yours. Collect twelve values it should refuse, including a
  protocol-relative URL, a backslash form, a percent-encoded form, a scheme with no slashes and a
  value that is a valid URL to a host that merely starts with yours. Run them through the check, then
  through the check after decoding the value the way the consumer will. Report how many each version
  accepts, and name the consumer you assumed.
- [ ] **Count the places one feature asks about identity.** Take the feature with the most endpoints
  in a project of yours -- a resource with a list, a detail, a nested child and a bulk read. For each
  endpoint, write down the question its guard asks and the question its query answers. Then write a
  test that calls each endpoint as a second user and as an anonymous caller, and report the number of
  pairs where a caller receives data that is not theirs. Fix one endpoint by moving the rule from the
  route to the query and report the number again.
- [ ] **Write the list of events that must leave a trace.** For a project of yours, list every event
  that an incident review would ask about: every refusal, every privilege change, every credential
  change, every lockout, every export. Then list every event that currently writes a line. Report the
  events in the first list and not the second -- that number is the gap, and it is invisible in the
  output because the output is what you would check it against. Then add the missing lines and
  confirm each one carries a named field rather than a request body.

## Solutions

:::solution Exercise 1

Three rendering contexts, four escapers, and the two questions that are not the same question.

```python run
"""Chapter 53 -- practice 1.

Three rendering contexts, four escapers, and the two questions that are
not the same question: did the value break out of its context, and did
the consumer read back what was written. An escaper can fail either one
on its own.
"""

import html
import json

PAYLOADS = [
    "</script><img src=x onerror=alert(1)>",
    '"+(alert(1))+"',
    "\\",
    "line1\nline2",
    "&lt;b&gt;",
    "O'Brien",
]

CONTEXTS = ["title text", "href, double-quoted", "js string"]


def esc_none(v):
    return v


def esc_html(v):
    return html.escape(v)


def esc_json(v):
    return json.dumps(v)[1:-1]


def esc_json_html(v):
    out = json.dumps(v)[1:-1]
    return (out.replace("<", "\\u003c").replace(">", "\\u003e")
               .replace("&", "\\u0026"))


ESCAPERS = [
    ("none", esc_none),
    ("html", esc_html),
    ("json", esc_json),
    ("json+<", esc_json_html),
]


def as_js_string(inserted):
    """The JS parser does not decode entities, so this is the only way to
    ask what the string literal evaluates to."""
    try:
        return json.loads('"' + inserted + '"')
    except ValueError:
        return None


def breaks(context, inserted):
    if context == "title text":
        return "<" in inserted
    if context == "href, double-quoted":
        return '"' in inserted
    return "</script" in inserted.lower() or as_js_string(inserted) is None


def survives(context, inserted, payload):
    if context == "js string":
        return as_js_string(inserted) == payload
    return html.unescape(inserted) == payload


def main():
    print(f"  contexts                            {len(CONTEXTS)}")
    print(f"  payloads                            {len(PAYLOADS)}")
    print(f"  escapers                            {len(ESCAPERS)}")
    print(f"  renders                             "
          f"{len(CONTEXTS) * len(ESCAPERS) * len(PAYLOADS)}")
    print()

    total = len(PAYLOADS)
    for heading, test in (("broke out of its context", breaks),
                          ("came back unchanged", survives)):
        print("    " + heading)
        print("    {:<22}".format("") +
              "".join("{:>9}".format(name) for name, _ in ESCAPERS))
        for context in CONTEXTS:
            row = "    {:<22}".format(context)
            for name, esc in ESCAPERS:
                n = 0
                for payload in PAYLOADS:
                    inserted = esc(payload)
                    if test is survives:
                        n += 1 if survives(context, inserted, payload) else 0
                    else:
                        n += 1 if breaks(context, inserted) else 0
                row += "{:>9}".format("%d of %d" % (n, total))
            print(row)
        print()

    print("    held and preserved the value")
    print("    {:<22}".format("") +
          "".join("{:>9}".format(name) for name, _ in ESCAPERS))
    covered = {}
    for context in CONTEXTS:
        row = "    {:<22}".format(context)
        for name, esc in ESCAPERS:
            ok = 0
            for payload in PAYLOADS:
                inserted = esc(payload)
                if not breaks(context, inserted) and survives(
                        context, inserted, payload):
                    ok += 1
            row += "{:>9}".format("%d of %d" % (ok, total))
            if ok == total:
                covered.setdefault(name, []).append(context)
        print(row)
    print()
    for name, _ in ESCAPERS:
        print("    {:<9} covers {} of {}".format(
            name, len(covered.get(name, [])), len(CONTEXTS)))
    print()

    named = [(n, covered[n]) for n, _ in ESCAPERS if n in covered]
    print("  the last table is the only one that is a verdict. a value has")
    print("  to do both things, and no escaper manages it everywhere:")
    for name, contexts in named:
        print("    {:<8} {}".format(name, ", ".join(contexts)))
    print()
    print("  `html` is the right answer for the two html contexts and the")
    print("  wrong one for the script, where it does not break out and does")
    print("  not survive either -- the browser never decodes the entities,")
    print("  so the value arrives as `&quot;`.")
    print()
    print("  `json` is the mirror image. it survives in the script, where")
    print("  the parser does understand a backslash, and it breaks out of")
    print("  the other two, which are read by an html parser that does not.")
    print("  adding the three character escapes makes it safe in the script")
    print("  -- and it is still not safe in a quoted attribute, for exactly")
    print("  the reason it was not before.")
    print()
    print("  the rule is not which escaper is strongest. it is that the")
    print("  escaper is chosen by the parser that will read the value, and")
    print("  a page that renders one value into three contexts needs three")
    print("  of them, chosen per context rather than once at the top.")


main()
```

```text
  contexts                            3
  payloads                            6
  escapers                            4
  renders                             72

    broke out of its context
                               none     html     json   json+<
    title text               1 of 6   0 of 6   1 of 6   0 of 6
    href, double-quoted      1 of 6   0 of 6   1 of 6   1 of 6
    js string                4 of 6   2 of 6   1 of 6   0 of 6

    came back unchanged
                               none     html     json   json+<
    title text               5 of 6   6 of 6   2 of 6   1 of 6
    href, double-quoted      5 of 6   6 of 6   2 of 6   1 of 6
    js string                3 of 6   0 of 6   6 of 6   6 of 6

    held and preserved the value
                               none     html     json   json+<
    title text               4 of 6   6 of 6   1 of 6   1 of 6
    href, double-quoted      4 of 6   6 of 6   2 of 6   1 of 6
    js string                2 of 6   0 of 6   5 of 6   6 of 6

    none      covers 0 of 3
    html      covers 2 of 3
    json      covers 0 of 3
    json+<    covers 1 of 3

  the last table is the only one that is a verdict. a value has
  to do both things, and no escaper manages it everywhere:
    html     title text, href, double-quoted
    json+<   js string

  `html` is the right answer for the two html contexts and the
  wrong one for the script, where it does not break out and does
  not survive either -- the browser never decodes the entities,
  so the value arrives as `&quot;`.

  `json` is the mirror image. it survives in the script, where
  the parser does understand a backslash, and it breaks out of
  the other two, which are read by an html parser that does not.
  adding the three character escapes makes it safe in the script
  -- and it is still not safe in a quoted attribute, for exactly
  the reason it was not before.

  the rule is not which escaper is strongest. it is that the
  escaper is chosen by the parser that will read the value, and
  a page that renders one value into three contexts needs three
  of them, chosen per context rather than once at the top.
```

:::

:::solution Exercise 2

Five ways to reach an address inside, and four validators whose only difference is when the question
is asked.

```python run
"""Chapter 53 -- practice 2.

A fetch service that takes a url from a user. Five ways to reach an
address the service should not reach, against four validators whose only
difference is the moment each question is asked.
"""

import ipaddress

PUBLIC = "93.184.216.34"
INTERNAL = "10.0.0.7"
MAPPED = "::ffff:10.0.0.7"

ALLOWED = ["cdn.example.com", "files.example.com",
           "internal.example.com", "mapped.example.com"]


def looks_private(addr):
    """The version that knows the spellings somebody wrote down."""
    return (addr.startswith("10.") or addr.startswith("192.168.")
            or addr.startswith("127.") or addr == "::1")


def is_internal(addr):
    """The version that asks the address what it is."""
    ip = ipaddress.ip_address(addr)
    if ip.version == 6 and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return ip.is_private or ip.is_loopback or ip.is_link_local


class Net:
    def __init__(self, answers):
        self.answers = {h: list(v) for h, v in answers.items()}
        self.reached = []

    def resolve(self, host):
        try:
            ipaddress.ip_address(host)
            return host
        except ValueError:
            pass
        seq = self.answers.get(host)
        if not seq:
            return PUBLIC
        return seq.pop(0) if len(seq) > 1 else seq[0]

    def connect(self, address):
        self.reached.append(address)
        return address


def by_name(net, host):
    if host not in ALLOWED:
        return None
    return net.connect(net.resolve(host))


def by_name_then_address(net, host):
    if host not in ALLOWED:
        return None
    addr = net.resolve(host)
    if looks_private(addr):
        return None
    return net.connect(net.resolve(host))


def by_pinned_address(net, host):
    if host not in ALLOWED:
        return None
    addr = net.resolve(host)
    if is_internal(addr):
        return None
    return net.connect(addr)


VALIDATORS = [
    ("name", by_name, False),
    ("+addr", by_name_then_address, False),
    ("pin", by_pinned_address, False),
    ("hop", by_pinned_address, True),
]

ATTACKS = [
    ("the name rebinds between the check and the connect",
     "cdn.example.com", {"cdn.example.com": [PUBLIC, INTERNAL]}, {}),
    ("a redirect to an address inside",
     "files.example.com", {"files.example.com": [PUBLIC]},
     {"files.example.com": INTERNAL}),
    ("a redirect to a name that points inside",
     "cdn.example.com",
     {"cdn.example.com": [PUBLIC], "internal.example.com": [INTERNAL]},
     {"cdn.example.com": "internal.example.com"}),
    ("the name is on the list and points inside",
     "internal.example.com", {"internal.example.com": [INTERNAL]}, {}),
    ("an allowed name resolving to an IPv4-mapped address",
     "mapped.example.com", {"mapped.example.com": [MAPPED]}, {}),
]


def attempt(attack, fetch, revalidate):
    """True if the connection ended up somewhere inside."""
    _, start, answers, redirects = attack
    net = Net(answers)
    host = start
    for _ in range(4):
        if fetch(net, host) is None:
            return False
        target = redirects.get(host)
        if target is None:
            break
        if not revalidate:
            net.connect(net.resolve(target))
            break
        host = target
    return any(is_internal(a) for a in net.reached)


def main():
    print(f"  attacks                             {len(ATTACKS)}")
    print(f"  validators                          {len(VALIDATORS)}")
    print()

    print("    {:<49}".format("attack") +
          "".join("{:>7}".format(n) for n, _, _ in VALIDATORS))
    results = []
    for attack in ATTACKS:
        row = "    {:<49}".format(attack[0])
        row_results = []
        for _, fetch, revalidate in VALIDATORS:
            reached = attempt(attack, fetch, revalidate)
            row_results.append(reached)
            row += "{:>7}".format("in" if reached else "-")
        results.append(row_results)
        print(row)
    totals = [sum(1 for r in results if r[i]) for i in range(len(VALIDATORS))]
    through = [[ATTACKS[j][0] for j in range(len(ATTACKS)) if results[j][i]]
               for i in range(len(VALIDATORS))]
    print()
    print("    {:<49}".format("attacks that reach an internal address") +
          "".join("{:>7}".format(n) for n in totals))
    print()
    print("  `name` and `+addr` let {} and {} through, and {}".format(
        totals[0], totals[1],
        "not the same ones" if set(through[0]) != set(through[1])
        else "the same ones"))
    print("  the second one closes the name that points inside and opens")
    print("  the window between the check and the connect, because the")
    print("  check resolves the name and the connect resolves it again --")
    print("  two lookups, two answers, one decision made in between.")
    print("  adding a check is not the same as making it safer.")
    print()
    print("  `pin` is the row where the answer stops moving: the address")
    print("  that was checked is the address that is connected to, so the")
    print("  second lookup never happens.")
    print()
    print("  `hop` is the row where every redirect target is put through")
    print("  the same question, which is the only thing that closes a")
    print("  redirect -- a redirect is a second url, and a validator that")
    print("  runs once has validated one url.")
    print()

    print("    address              looks_private   is_internal")
    for addr in (PUBLIC, INTERNAL, MAPPED):
        print("    {:<21}{:>14}{:>13}".format(
            addr, str(looks_private(addr)), str(is_internal(addr))))
    disagree = [a for a in (PUBLIC, INTERNAL, MAPPED)
                if looks_private(a) != is_internal(a)]
    print()
    print(f"  the two address checks disagree on {len(disagree)} of the "
          f"{len((PUBLIC, INTERNAL, MAPPED))},")
    print("  and the one they disagree on is the one that gets through")
    print("  `+addr`. a private range written as a list of prefixes is a")
    print("  list of the spellings somebody thought of, and an address has")
    print("  more spellings than that.")
    print()
    print("  the fourth attack is worth reading twice, because it is also")
    print("  what a legitimate call to an internal service looks like. the")
    print("  reason the fix is an allow-list of addresses rather than a")
    print("  rule about private ranges is that the two are the same")
    print("  request, and only the deployment knows which one it is.")


main()
```

```text
  attacks                             5
  validators                          4

    attack                                              name  +addr    pin    hop
    the name rebinds between the check and the connect      -     in      -      -
    a redirect to an address inside                       in     in     in      -
    a redirect to a name that points inside               in     in     in      -
    the name is on the list and points inside             in      -      -      -
    an allowed name resolving to an IPv4-mapped address     in     in      -      -

    attacks that reach an internal address                 4      4      2      0

  `name` and `+addr` let 4 and 4 through, and not the same ones
  the second one closes the name that points inside and opens
  the window between the check and the connect, because the
  check resolves the name and the connect resolves it again --
  two lookups, two answers, one decision made in between.
  adding a check is not the same as making it safer.

  `pin` is the row where the answer stops moving: the address
  that was checked is the address that is connected to, so the
  second lookup never happens.

  `hop` is the row where every redirect target is put through
  the same question, which is the only thing that closes a
  redirect -- a redirect is a second url, and a validator that
  runs once has validated one url.

    address              looks_private   is_internal
    93.184.216.34                 False        False
    10.0.0.7                       True         True
    ::ffff:10.0.0.7               False         True

  the two address checks disagree on 1 of the 3,
  and the one they disagree on is the one that gets through
  `+addr`. a private range written as a list of prefixes is a
  list of the spellings somebody thought of, and an address has
  more spellings than that.

  the fourth attack is worth reading twice, because it is also
  what a legitimate call to an internal service looks like. the
  reason the fix is an allow-list of addresses rather than a
  rule about private ranges is that the two are the same
  request, and only the deployment knows which one it is.
```

:::

:::solution Exercise 3

A route guard and a row scope, and the endpoint whose guard is correct and still leaks.

```python run
"""Chapter 53 -- practice 3.

A route guard and a row scope are two different checks in two different
places. Every endpoint here has a guard; the question is which rows the
answer is allowed to contain.
"""

CALLERS = ["u1", "u2", None]

# label, the guard on the route, who owns the thing the guard is about,
# and the rows the handler ends up reading, as id -> owner
ENDPOINTS = [
    ("GET /notes/12", "parent is the caller's", "u1", {12: "u1"}),
    ("GET /notes/12/comments", "parent is the caller's", "u1", {5: "u1"}),
    ("GET /notes/12/comments/6", "parent is the caller's", "u1", {6: "u2"}),
    ("GET /notes?ids=12,13", "caller has a session", None, {12: "u1", 13: "u2"}),
    ("POST /notes/12/share", "none", None, {12: "u1"}),
]


def serve(endpoint, caller, scope):
    """Return the rows the caller receives, or None if the route guard
    refused the request before the rows were read."""
    _, guard, parent_owner, rows = endpoint
    if guard.startswith("parent") and caller != parent_owner:
        return None
    if guard == "caller has a session" and caller is None:
        return None
    got = []
    for row_id, owner in rows.items():
        if scope == "none" or owner == caller:
            got.append(row_id)
    return got


def verdict(endpoint, caller, scope):
    got = serve(endpoint, caller, scope)
    if got is None:
        return "refused"
    if not got:
        return "no rows"
    _, _, _, rows = endpoint
    if all(rows[r] == caller for r in got):
        return "own"
    return "LEAK"


def count_leaks(scope):
    return sum(1 for e in ENDPOINTS for c in CALLERS
               if verdict(e, c, scope) == "LEAK")


def main():
    print(f"  endpoints                           {len(ENDPOINTS)}")
    print(f"  callers                             {len(CALLERS)}")
    print(f"  pairs tested                        "
          f"{len(ENDPOINTS) * len(CALLERS)}")
    print()

    print("    {:<25}{:<24}{:>8}{:>8}{:>8}".format(
        "endpoint", "the guard", "owner", "other", "anon"))
    for endpoint in ENDPOINTS:
        row = "    {:<25}{:<24}".format(endpoint[0], endpoint[1])
        for caller in CALLERS:
            row += "{:>8}".format(verdict(endpoint, caller, "none"))
        print(row)
    print()

    guarded = count_leaks("none")
    scoped = count_leaks("row")
    print(f"  pairs where a non-owner got data         {guarded}")
    print()
    print("  the same rows, with the scope applied where they are read")
    print(f"    pairs where a non-owner got data       {scoped}")
    print()
    print("  every endpoint above has a guard, and the guard is the part")
    print("  somebody wrote while looking at the route. the third one has")
    print("  a guard that is correct and still leaks: it asks whether the")
    print("  note belongs to the caller, and then reads a comment by id")
    print("  without asking whether that comment belongs to the note. the")
    print("  guard was on the parent and the row was the child, and the")
    print("  two were never connected.")
    print()
    print("  the fourth is the same mistake at the level of a query: the")
    print("  ids came from the caller, so the set of rows is caller-")
    print("  chosen, and a session check does not narrow it. the fifth")
    print("  has no guard at all and is the only one where an anonymous")
    print("  caller reads somebody's data.")
    print()
    print("  the second count is what the fix costs, and it is the same")
    print("  move as putting the rule at the repository instead of at the")
    print("  handler: one scope, applied where the rows are read, and the")
    print("  guard above it becomes a separate question about whether the")
    print("  request should be served at all.")


main()
```

```text
  endpoints                           5
  callers                             3
  pairs tested                        15

    endpoint                 the guard                  owner   other    anon
    GET /notes/12            parent is the caller's       own refused refused
    GET /notes/12/comments   parent is the caller's       own refused refused
    GET /notes/12/comments/6 parent is the caller's      LEAK refused refused
    GET /notes?ids=12,13     caller has a session        LEAK    LEAK refused
    POST /notes/12/share     none                         own    LEAK    LEAK

  pairs where a non-owner got data         5

  the same rows, with the scope applied where they are read
    pairs where a non-owner got data       0

  every endpoint above has a guard, and the guard is the part
  somebody wrote while looking at the route. the third one has
  a guard that is correct and still leaks: it asks whether the
  note belongs to the caller, and then reads a comment by id
  without asking whether that comment belongs to the note. the
  guard was on the parent and the row was the child, and the
  two were never connected.

  the fourth is the same mistake at the level of a query: the
  ids came from the caller, so the set of rows is caller-
  chosen, and a session check does not narrow it. the fifth
  has no guard at all and is the only one where an anonymous
  caller reads somebody's data.

  the second count is what the fix costs, and it is the same
  move as putting the rule at the repository instead of at the
  handler: one scope, applied where the rows are read, and the
  guard above it becomes a separate question about whether the
  request should be served at all.
```

:::

:::solution Exercise 4

A field allow-list and a list of events that must produce a line, checked against each other.

```python run
"""Chapter 53 -- practice 4.

The constructive half of the logging block: a recorder with a field
allow-list and a list of events that must always produce a line, checked
against each other. Nothing here writes a value out, which is also what
the recorder is for.
"""

CORE = {"actor": "u1", "action": "read", "resource": "note 12",
        "outcome": "ok"}

FROM_BODY = "(from the request body)"

# The names the request body uses for the three fields that must never
# reach a log line. They are held as data rather than written as keyword
# arguments, so that this file is a list of names and not a set of
# assignments.
BODY_NAMES = ("password", "token", "card")

# the fields a log line is allowed to contain
ALLOWED = ("actor", "action", "resource", "outcome", "reason", "address")

# the events that must produce a line, whether or not anyone thought to
# add a call for them
REQUIRED = [
    "permission denied",
    "role changed",
    "account locked",
    "export downloaded",
    "password changed",
]


def fields(**extra):
    out = dict(CORE)
    out.update(extra)
    return out


def from_body(**extra):
    """A handler that hands the recorder the whole request rather than
    the fields it needs."""
    out = fields(**extra)
    for name in BODY_NAMES:
        out[name] = FROM_BODY
    return out


# name, the fields offered to the recorder, and whether it is required
EVENTS = [
    ("login success",
     from_body(action="login", resource="session"), False),
    ("login failure",
     from_body(action="login", resource="session", outcome="refused",
               reason="bad password"), False),
    ("password reset",
     from_body(action="reset", resource="session"), False),
    ("token refresh",
     from_body(action="refresh", resource="session"), False),
    ("page view", fields(resource="note 12", trace="a4f1"), False),
    ("note created", fields(action="create", trace="a4f1"), False),
    ("permission denied",
     fields(action="read", outcome="refused", reason="not the owner"), True),
    ("role changed",
     from_body(action="grant", resource="account"), True),
    ("account locked",
     fields(action="lock", resource="account", outcome="refused",
            reason="too many attempts"), True),
    ("export downloaded",
     fields(action="export", resource="all notes", trace="a4f1"), True),
]


def record(offered):
    """The allow-list is the whole of the first fix: the line is built
    from named fields rather than from the request."""
    kept = {k: v for k, v in offered.items() if k in ALLOWED}
    dropped = [k for k in offered if k not in ALLOWED]
    return kept, dropped


def main():
    print(f"  events                              {len(EVENTS)}")
    print(f"  events that must produce a line     {len(REQUIRED)}")
    print(f"  fields a line may contain           {len(ALLOWED)}")
    print()

    print("    {:<22}{:>9}{:>9}{:>11}{:>14}".format(
        "event", "offered", "written", "dropped", "from the body"))
    written_records = []
    offered = written = dropped = body = 0
    for name, offered_fields, _ in EVENTS:
        kept, lost = record(offered_fields)
        written_records.append((name, kept))
        offered += len(offered_fields)
        written += len(kept)
        dropped += len(lost)
        body += sum(1 for k in lost if k in BODY_NAMES)
        print("    {:<22}{:>9}{:>9}{:>11}{:>14}".format(
            name, len(offered_fields), len(kept), len(lost),
            sum(1 for k in lost if k in BODY_NAMES)))
    print()

    print(f"  fields offered                      {offered}")
    print(f"  fields written                      {written}")
    print(f"  fields dropped                      {dropped}")
    print(f"  of the dropped, from the request body   {body}")
    print(f"  lines written                       "
          f"{len(written_records)} of {len(EVENTS)}")
    with_line = [r for r in REQUIRED if any(n == r for n, _ in written_records)]
    missing = [r for r in REQUIRED if not any(n == r for n, _ in written_records)]
    print(f"  required events with a line         "
          f"{len(with_line)} of {len(REQUIRED)}")
    print()

    questions = [
        ("who acted", lambda r: "actor" in r),
        ("on what", lambda r: "resource" in r),
        ("what happened", lambda r: "outcome" in r),
        ("why it was refused",
         lambda r: r.get("outcome") != "refused" or "reason" in r),
    ]
    print("    the questions the written lines answer")
    for label, ok in questions:
        answerable = all(ok(kept) for _, kept in written_records)
        print("    {:<28}{}".format(label, "yes" if answerable else "no"))
    carried = sum(1 for _, kept in written_records
                  if any(k in BODY_NAMES for k in kept))
    print("    {:<28}{}".format("what the credential was",
                                "yes" if carried else "no"))
    print()
    print(f"  {body} of the {dropped} dropped fields came from the request body, and")
    print("  the rest are the ones somebody will want during the incident.")
    print("  that is the cost of an allow-list, and it is the right trade: a")
    print("  field that is missing from a log can be added, and a credential")
    print("  that was written into one cannot be unwritten.")
    print()
    print(f"  the required list has {len(REQUIRED)} entries and "
          f"{len(with_line)} of them produced a line.")
    print(f"  the one that did not is `{missing[0]}`, which is a gap the field")
    print("  allow-list cannot see and the event list found. nothing in this")
    print("  service writes a line when a credential changes, and that is the")
    print("  same missing event the session block could not find either -- a")
    print("  password change is a route, and nothing about it looks like a")
    print("  session event until you write the list of events that have to")
    print("  leave a trace.")
    print()
    print("  that list is the only part of this recorder that is a")
    print("  requirement rather than an implementation. the allow-list can be")
    print("  reviewed by reading it. the list of events cannot, because what")
    print("  is missing from it is missing from the output too, and the")
    print("  output is what you would check it against.")
    print()
    print("  the last row of the questions table is the whole argument. the")
    print("  only question the request body would have answered is the one")
    print("  nobody should be asking, and every question an incident review")
    print("  actually asks is answered by a named field that was there")
    print("  before the request arrived.")


main()
```

```text
  events                              10
  events that must produce a line     5
  fields a line may contain           6

    event                   offered  written    dropped from the body
    login success                 7        4          3             3
    login failure                 8        5          3             3
    password reset                7        4          3             3
    token refresh                 7        4          3             3
    page view                     5        4          1             0
    note created                  5        4          1             0
    permission denied             5        5          0             0
    role changed                  7        4          3             3
    account locked                5        5          0             0
    export downloaded             5        4          1             0

  fields offered                      61
  fields written                      43
  fields dropped                      18
  of the dropped, from the request body   15
  lines written                       10 of 10
  required events with a line         4 of 5

    the questions the written lines answer
    who acted                   yes
    on what                     yes
    what happened               yes
    why it was refused          yes
    what the credential was     no

  15 of the 18 dropped fields came from the request body, and
  the rest are the ones somebody will want during the incident.
  that is the cost of an allow-list, and it is the right trade: a
  field that is missing from a log can be added, and a credential
  that was written into one cannot be unwritten.

  the required list has 5 entries and 4 of them produced a line.
  the one that did not is `password changed`, which is a gap the field
  allow-list cannot see and the event list found. nothing in this
  service writes a line when a credential changes, and that is the
  same missing event the session block could not find either -- a
  password change is a route, and nothing about it looks like a
  session event until you write the list of events that have to
  leave a trace.

  that list is the only part of this recorder that is a
  requirement rather than an implementation. the allow-list can be
  reviewed by reading it. the list of events cannot, because what
  is missing from it is missing from the output too, and the
  output is what you would check it against.

  the last row of the questions table is the whole argument. the
  only question the request body would have answered is the one
  nobody should be asking, and every question an incident review
  actually asks is answered by a named field that was there
  before the request arrived.
```

:::
