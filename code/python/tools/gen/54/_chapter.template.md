---
chapter: 54
part: 10
title: Patterns You Will Actually Use
summary: Six shapes that get written again and again, and what each one costs rather than what it is called. Every block measures the pattern against the thing it replaced -- comparisons, lines, frames, functions that must change -- and the measurements keep disagreeing with the usual argument for the pattern.
minutes: 100
tags: [architecture, strategy, dispatch, observer, adapter, factory, registry, composite, decorator, protocol, interfaces, layers, abstraction]
---

A pattern is a name for a shape somebody already wrote. That is the whole of what the catalogue is,
and it is worth saying plainly because the usual way the subject is taught turns the names into
targets: you learn twenty-three of them and then go looking for somewhere to put one.

The useful question about any shape is not which pattern it is. It is what the shape costs, what it
buys, and whether the thing it buys is something this program needs. All three of those are
countable, and this chapter counts them. Every block compares a pattern against the thing it
replaced, and several of the comparisons come out against the pattern.

There is a second theme, and it is specific to Python. Several of the catalogue's patterns exist
because the languages it was written for had no first-class functions. This one does. A dispatch
table is a dictionary, `@` is the decorator pattern, `with` is the template method, and
`functools.singledispatch` is the strategy pattern with the selection already written. Recognising
the pattern is still worth doing -- a name is how you talk about a design -- but recognising it is
not the same as needing to build it.

## The conditional that selects behaviour

Start with the shape everybody writes first, because the measurement is the easiest to take and the
result is not the one the pattern's advocates claim.

<<BLOCK:strategy_branches>>

Five shipping methods. The chain compares the method name 15 times to resolve five calls and the
table compares it once per call, which is the argument everybody makes and it is true.

The line count goes the other way. The chain region is 24 lines and the table region is 35, and the
third column says the same thing from a different angle: the table mentions every name twice -- once
as a function and once as a key -- where the chain mentions each of them once. So the table is more
code, not less, and "tidier" is not what was bought.

What was bought is in the last table. An unknown method is refused by both, and the chain whose last
branch is a default charges it the standard rate instead. The request succeeds, the customer is
billed, and the only signal is a number that looks plausible. That is the difference: a chain has a
place where a case can be forgotten, and forgetting it is a fall-through to whichever branch happens
to be last. A table has no such place, because a missing key is a `KeyError` on the first call.

## Dispatch that is already in the language

`functools.singledispatch` is the strategy pattern as a library function, and the two things worth
knowing about it are which argument it looks at and what it does with a subclass.

<<BLOCK:singledispatch_dispatch>>

Nine values, four handlers registered, and four of the nine reach the default. The one to read twice
is `True`: `bool` is a subclass of `int`, so it reached the int handler, and so did a `Money` class
defined a few lines above. The dispatch walks the mro rather than matching the class, which is the
behaviour you want and also the behaviour that makes "register `int`" mean something wider than it
looks.

The second table is the limit. `combine(1, "a")` and `combine(1, 1)` reach the same handler and
`combine("a", 1)` reaches another, because the type of the second argument is never consulted. That
is the mechanism's boundary and also its documentation: the function is dispatched on one value and
every other argument is data.

The trade is the same as the table's. The dispatch is a registration rather than a branch, and a type
nobody registered is a default rather than a silent fall-through -- as long as you decide what the
default is. The default here returns a string, which is the wrong answer that looks like the right
one. Raising would have been better, and that decision is the one the pattern does not make for you.

## The list of callbacks

A subscriber list is the observer pattern and it is three lines. What it does not answer is what
happens when one of them raises, and whether the order they run in is part of the contract.

<<BLOCK:observer_fanout>>

Six subscribers, the third of which raises. The loop that does not isolate failures raised after 2 of
the 6 had run, so the last three never hear about the event -- and because the exception left the
loop, the caller does not get the list of who did run either. The loop that isolates failures ran 5
of the 6 and returned the failure as data.

Both loops are three lines. The difference is that the second treats a subscriber as something that
can be wrong, which is the only assumption a list of callbacks needs.

The second half is the question nobody writes down. Three subscribers that each fold a shared value
leave a different result in every one of the 6 orderings. So the order is not an implementation
detail, it is part of the result -- and nothing in the pattern says what it is. If the subscribers
only report, any order will do and isolation is the whole fix. If any of them can change the value
the others see, the order is a contract, and a contract that is not written down is one a later
refactor will change.

## The dependency whose names are everywhere

An adapter is the answer to a question you can ask before writing it, and the question is a count.

<<BLOCK:adapter_surface>>

Four fields, four places in the direct version and one in the adapted one. Under v1 both work, which
is exactly why the pattern gets skipped -- the two are indistinguishable in the output and the
direct one is shorter. Under v2 the direct version has four reads to fix and the adapted one has one,
in a function whose only job is that translation.

The number that matters is not four. It is that the four are spread across the consumer, wherever a
field happened to be needed, and the one is adjacent to itself. And the honest version of the
argument is that with a single call site there is no difference at all: the adapter only divides a
number that is greater than one.

## The registry, and what builds it

The factory pattern in Python is a dictionary with a decorator in front of it. Two things go wrong
with it and neither of them is in the decorator.

<<BLOCK:factory_registry>>

Five handlers are defined and three are in the registry, because the other two live in a module
nothing has imported. The registration is a side effect of an import that nobody wrote for that
reason, so which handlers exist depends on which modules the process happened to touch -- and the
failure is a missing key at request time, in a different file from the handler that was never
registered. Importing the handler modules explicitly, for that reason, is the fix.

The second table is the reason to prefer the registry over a lookup that goes through the module's
own namespace. The registry resolved 5 of 8 requests and `globals()` resolved 6, and they are not
the same five. `globals()` answers for `handles`, `main` and `REGISTRY`, none of which is a format
handler, and it has no answer for `read_xml` or `read_yaml`, which are handlers defined inside a list
rather than at module level. So the two lookups disagree in both directions, and the direction that
matters is the first one: a lookup that goes through `globals()` cannot tell a handler from anything
else the module happens to define, which is the same failure as the resolver in the untrusted-data
chapter, one layer up.

## The tree that answers the same question

The composite pattern gives a leaf and a branch the same interface. The claim is that a new kind of
node is one new class, and that is measurable: count the implementations against the number of
nodes.

<<BLOCK:composite_walk>>

Twelve nodes, two node types in the tree, three implementations of the interface. A leaf answers
`size` and a directory answers `size`, and the directory's answer is a fold over its children -- so
asking the root a question is asking the whole tree that question, every time. Every query visited
all twelve nodes.

The caching node is the pattern working exactly as advertised: it implements the same interface,
nothing above it changed, and nothing above it can tell. It is also the node that has to be told when
the answer stops being true, and the interface has no method for that. The pattern made the tree
uniform and left invalidation as the thing the uniform interface cannot express.

## Punctuation that is a pattern

`@` is the decorator pattern, and what it does not do by itself is preserve anything about the
function it wraps.

<<BLOCK:decorator_wraps>>

Five things a function carries, and a bare decorator loses four of them: the name, the docstring, the
qualified name and the signature. The module is the one that survives, and it survives by accident
rather than by design -- the decorator was defined in the same module as the function it wraps, so the
wrapper's `__module__` happens to be the right answer. It is the one entry in that column that the
decorator is not responsible for. `functools.wraps` restores all five.

The one that matters most in practice is the signature, and it matters because nothing in the code
fails. A wrapped function still runs and a caller who passes the wrong argument still gets the
original's own error. What breaks is every tool that reads the function rather than calls it -- a
help page, an editor, a schema generator -- and all of them report the wrapper.

The fourth variant in the table is there because the factory is the shape that gets it wrong. A
decorator that takes arguments is three nested functions, and putting `functools.wraps` on the outer
one instead of the inner one is the mistake that looks like a fix.

## What a check on an interface is worth

An interface is a name for a set of methods. What `isinstance` does with that name depends on which
kind of interface it is, and the difference is what the word "structural" costs.

<<BLOCK:protocol_check>>

Four objects and three ways of naming the interface. A plain `Protocol` raises `TypeError` for all
four, which is a decision rather than an oversight: a structural check walks the attributes on every
call and the default is not to pay for it.

`runtime_checkable` accepted all four, including the object whose method takes no arguments and the
object whose `get` is the number five. The ABC accepted one -- the subclass written to satisfy it
-- and it is the strictest of the three in the way that costs the most, because a class that already
does the right thing has to be edited to say so.

So the one check available at runtime is a check on names. The interface is for the reader and the
type checker, both of which can see the signature. The runtime check catches the collaborator that
is missing the attribute entirely, which is the mistake that actually happens when a dependency is
swapped -- and it is not strong enough to be the only thing standing between a request and a call.

## What a layer costs

The last teaching block is the one that turns the chapter's method on the chapter's subject. A layer
is a claim about a change that might happen, and the claim can be checked.

<<BLOCK:layer_cost>>

One expression, reached through five frames from the outside. Four of those frames only forward
their argument to the next one, and each layer has exactly one implementation, so every seam has one
thing on each side.

That is not an argument against layers. It is the number to put next to them, because the number is
the rent and the implementations are the tenant. Swapping the rule changes one line with the layers
and one line without them; what would make the count go up is a second implementation at some layer,
and not one of the five here has one. The seam each layer creates is a seam with one thing on each
side of it, which is the definition of a seam that is not being used.

The direction is the part the frames cannot show. If the rule is at the bottom and the layers point
down at it, the thing at the top can be replaced without touching it. If the rule ever imports the
handler, the stack has become a cycle and the layers are no longer a boundary -- they are a detour.

:::pitfall The pattern where a function would do

Every block so far has compared a pattern against something simpler and found the pattern paying for
itself somewhere. This one is the case where it does not.

Three notification channels, built twice: once as a hierarchy with a factory, once as a dictionary of
functions.

<<BLOCK:pitfall>>

Four classes, six functions and 33 lines against no classes, one function and 9 lines. Both produce
the same string for all three channels, and both refuse an unknown channel the same way -- because
both of them end in a dictionary lookup. The hierarchy is a dictionary with four extra names in front
of it.

A fourth channel costs a class and a registry entry against a key. And the class is not doing
anything the function does not do: it holds no state, it has one method, and it is constructed and
thrown away on every call.

The hierarchy starts paying on the day a notifier needs to remember something -- a retry count, a
client handle, a rate limit. A function can hold that too, in a closure or a default argument, and
the moment it does, the difference between the two is that one of them is a class and the other is
not. That is the whole of what was bought, and it is worth naming before paying for it.

The rule to carry away is not "do not use patterns". It is that the class was introduced to hold
behaviour, and behaviour in this language is a value. Introduce the class when it holds something
else -- state, a configuration, an identity that matters -- and not before.

:::

:::scenario The plugin host

A plugin host is where this chapter's patterns all turn up at once, because it is the feature whose
entire job is to let code you did not write run inside your process. Eight plugins, four of which are
broken in four different ways.

<<BLOCK:scenario>>

Five hosts. The first calls each plugin and lets it fail, and it answered four of the eight requests
before the host came down. Isolation keeps the host up and still answers four. Adding the interface
check changes nothing at all -- it accepted all eight, including the plugin whose `handle` is the
number five, because a runtime protocol check asks whether the name is there and it is. The adapter
gets one more plugin answering, which is what an adapter is for.

The last row answers the same number as the one above it, and the difference is *when* the broken
plugins are found: before the first request rather than during it. That is the whole gain and it is
the largest single gain in the table.

So a plugin host is a place where the patterns give you the shape -- a registry, an interface, a
dispatch, an adapter -- and the shape is not the part that decides whether the system works. The
part that decides is the one line nobody writes: the probe that calls every plugin once, at startup,
and names the ones that did not answer.

:::

## Key takeaways

- **A pattern is a name for a shape, not a target to aim at.** The question is what the shape costs,
  what it buys, and whether this program needs the thing it buys.
- **The table is the longer of the two.** 24 lines of chain against 35 lines of table, and every
  method name appears twice in the table -- once as a function and once as a key.
- **What a table buys is not brevity, it is that a missing case cannot be forgotten.** A chain whose
  last branch is a default charged an unknown method the standard rate, silently and plausibly.
- **A chain compares 15 times over 5 calls; a table compares once per call.** That is the argument
  everybody makes and it is true, and it is not the one that matters.
- **`functools.singledispatch` dispatches on one argument and walks the mro.** `True` reached the int
  handler, and so did a subclass of `int` written in the same file.
- **The second argument of a singledispatch function decides nothing.** The type of every argument
  after the first is never consulted, which is the mechanism's limit and its documentation.
- **A default that returns a plausible value is worse than one that raises.** The default here
  returns a string, which is the wrong answer that looks like the right one.
- **A subscriber list is three lines, and the second version of it treats a subscriber as something
  that can be wrong.** The first raised after 2 of 6 had run, and the three after the failing one
  never heard about the event at all.
- **Order is part of the result when subscribers share state.** All 6 orderings of three folding
  subscribers left a different value, and nothing in the pattern says what the order is.
- **An adapter divides a number, so it does nothing when the number is one.** Four reads in four
  places against four reads in one, and with a single call site there is no difference at all.
- **A registry is built by import side effects.** Five handlers defined, three registered, and the
  missing two are missing because a module was not imported -- reported as a missing key at request
  time, in a different file.
- **A lookup through `globals()` cannot tell a handler from anything else.** It resolved 6 of 8
  requests where the registry resolved 5, and they were not the same five: three of the names it
  answered for were not handlers, and two of the registry's handlers were not module-level names.
- **A composite gives a leaf and a branch the same interface and not the same cost.** Every query on
  the root visited all twelve nodes.
- **A caching node implements the same interface, so nothing above it can tell.** It is also the node
  that has to be invalidated, and the interface has no method for that.
- **A bare decorator loses four of the five things a function carries.** The module survives, by
  accident rather than by design, because the decorator was defined in the same module. `functools.wraps`
  restores all five, and the one that matters is the signature, because nothing in the code fails
  without it.
- **A decorator with arguments is three nested functions.** Putting `functools.wraps` on the outer
  one instead of the inner one is the mistake that looks like a fix.
- **A plain `Protocol` raises on `isinstance` for every object.** That is a decision about cost, not
  an oversight, and `runtime_checkable` is the switch that pays it.
- **The runtime check is a check on names.** It accepted an object whose method takes no arguments
  and an object whose method name is bound to the number five, because it does not call anything.
- **An ABC is the strictest and costs the most.** One of the four objects accepted, and every class
  that already satisfied the interface had to be edited to say so.
- **Five frames for one expression, and four of them only forward.** A layer is rent and the
  implementations are the tenant; a layer whose implementation count stays at one has been paying
  rent without a tenant.

## Practice

- [ ] **Replace one conditional with a table, and check the last branch first.** Find an `if`/`elif`
  chain of four or more branches in a project of yours that selects behaviour. Before rewriting it,
  look at what the final branch does with a value it does not recognise -- if it returns a default
  rather than raising, write down how many inputs would be silently accepted. Then write the table
  version, count the comparisons per call in both, and count the lines in both. Report all three
  numbers.
- [ ] **Count the places a dependency's names appear.** Pick a third-party library or a service
  client. List the field or method names it defines that your code reads. Then count the *functions*
  in your code that mention any of them. If the number is more than one, write the adapter and count
  again. Report the two numbers and say whether the adapter earned its place.
- [ ] **Survey the layers on one call path.** Take a request handler or a command entry point in a
  project of yours. List every function between it and the rule that decides the answer. For each
  one, record how many implementations it has. Report the number of frames in the path and the number
  of functions with exactly one implementation -- and then say which of those you would delete, and
  what you would have to be sure of first.
- [ ] **Audit the interface you rely on.** Take a collaborator your code is duck-typed against. Write
  five stand-ins: one correct, one with the right method name and the wrong signature, one with the
  name bound to something that is not callable, one missing the name entirely, and one that subclasses
  an ABC you write. Run all five through `hasattr`, a plain `Protocol`, a `runtime_checkable`
  `Protocol`, and the ABC. Report how many each check accepts, and name the one check that catches
  the mistake you would actually make.

## Solutions

:::solution Exercise 1

A field-validation chain and the table that replaces it, and the three fields the chain accepts
because it has never heard of them.

<<BLOCK:sol1>>

:::

:::solution Exercise 2

Three consumers reading a vendor's names, written twice, with the count taken from the source of the
file.

<<BLOCK:sol2>>

:::

:::solution Exercise 3

A five-frame call path, and the two layers that have more than one implementation behind them.

<<BLOCK:sol3>>

:::

:::solution Exercise 4

Five collaborators and four ways of asking whether each of them satisfies the interface.

<<BLOCK:sol4>>

:::
