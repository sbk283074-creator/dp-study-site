---
chapter: 55
part: 10
title: Dependency Injection and Inversion of Control
summary: What injection changes, counted rather than asserted -- the behaviours a test can hand a stand-in to, the tests whose result depends on the order, the modules that name a concrete type, and the direction of the reference between a policy and a mechanism. Several of the counts come out against the practice, and two of them come out in its favour for reasons the usual argument does not mention.
minutes: 100
tags: [architecture, dependency injection, inversion of control, Protocol, seams, composition root, service locator, lifetimes, testing, wiring]
---

Injection is usually taught as a style, or as something a framework does to you. It is neither. It is
a change to where an object comes from, and the consequences of that change are countable: how many
behaviours a test can hand a stand-in to, how many tests depend on the order they run in, how many
modules have to be edited when a dependency is replaced.

This chapter counts those, and the counts do not all point the same way. Injection moves the vendor's
name out of a service and into every caller, which makes one number better and another worse. A
container turns wiring into data and replaces a class reference with a string. The word inversion
turns out to describe a direction rather than a reduction, and the count of references is identical
either way.

There is also a case where injection is the wrong answer, and it is the same case as the last
chapter's: a collaborator with one implementation and no seam to cut.

## The object that arrives as an argument

Start with the measurement that decides the whole subject, because it is the one a test suite
already knows how to take.

<<BLOCK:constructs_its_own>>

Six behaviours, and both designs pass all six. That is the part worth pausing on: a suite that
constructs its own dependencies is green, so nothing in it reports a problem. What it cannot do is
replace anything. The object that builds its own database handle accepts a stand-in in zero of the
six behaviours, and the object that takes one accepts it in all six, and the difference between
them is a single line that names a concrete type.

## The handle nobody chose

The second half of what injection is for has nothing to do with replacing anything. It is about
lifetime.

<<BLOCK:global_singleton>>

Three behaviours and three orders. Under the module-level handle, all three change their result
depending on what ran before them, and the first order is the one that passes -- which is the order
somebody would write them in, and therefore the order in which the problem is invisible. Under the
handle that arrives as an argument, none of the three changes.

The tempting fix is a fixture that clears the handle, and it is worth seeing why that is not the
same thing. A fixture that clears it is a fixture that knows which handle to clear, which is the
knowledge the caller was supposed to not need. And it works only while every test remembers to use
it, which is a property of the tests rather than of the design.

## The seam, and what it does not promise

An interface is what makes the swap possible. It is not what makes the swap safe.

<<BLOCK:protocol_seam>>

The consumer names none of the three implementations, so the seam does exactly what it is for: the
implementation can be replaced without the consumer being edited, and the count of places that would
have to change is zero. That is the whole claim and it holds.

The second table is what the claim does not cover. Two of the three return a value for every key and
the third returns two and a `None`, and the interface said nothing about which of those is allowed.
It named two methods, and their names are all it named: no signature, no postcondition, and no way
for the consumer to find out without calling one.

## Which way the arrow points

The word inversion is the part of this subject that gets said without being explained. It is easier
to explain as a direction than as a principle.

<<BLOCK:inversion_direction>>

Each design holds exactly one reference between the two modules, and they point in opposite
directions. So inversion is not a reduction in coupling: the count is the same, and a chapter that
claimed otherwise would be measuring the wrong thing.

What changes is which module is on the receiving end. In the first design the policy names the
mechanism, so the stable thing depends on the unstable one, and replacing the database edits the
business rule. In the second the mechanism names the policy's interface, so the arrow runs from the
thing that will be replaced towards the thing that will not. That is why the interface belongs to the
consumer: a `Store` defined in the database module would point the wrong way no matter where the
`import` statement sits.

## Where the wiring lives

Once the dependencies are parameters, something has to supply them, and the shape of that something
is a decision with a measurable consequence.

<<BLOCK:container_wiring>>

Six services, six dependencies, and one name in the graph that was never declared. The hand-written
root and the container that resolves on demand get through the same number of services before they
fail, so the container is not better at this by being a container. The one that checks the graph
first constructs nothing, and that is the whole difference: the graph is data, so it can be checked
as a whole before any of it runs.

The cost is in the error. The hand-written root raises `NameError` and names the thing, because it
is a name. The container raises `KeyError` and names a string, because that is all a registry has --
and a string is not checked by anything until the lookup happens. That is the trade in one line: a
container turns wiring into data so that the wiring can be checked, and in exchange it turns a class
reference into a string nothing checks for you.

## The marker a framework looks for

If a framework is doing the injecting, this is what it is doing.

<<BLOCK:depends_marker>>

Five parameters across four handlers, four of them marked, and the handler bodies name a provider in
none of them. The value arrives and the code that uses it does not know where from, which is the
whole of the mechanism.

The marker is not a type. It is a default value that the caller recognises and replaces, and that is
precisely why the handler can be called with a stand-in without being edited. The cost is that
nothing checks it: a parameter whose default is `Depends(f)` is a dependency and a parameter whose
default is a real object is a default, and the two look the same to everything except the caller
that knows to look. A framework's injection is this and nothing more -- it reads a signature, fills
what is marked, and calls an ordinary function, which is worth saying because the frameworks that do
it are the ones that make it look like magic.

## How long the object is allowed to live

A scope is an answer to one question, and getting it wrong produces a bug with no symptom.

<<BLOCK:lifetime_scopes>>

Three requests and three scopes, giving one instance, three and six. Then the mistake: a singleton
that captured a per-request object at construction time hands two of the three requests the wrong
session, and the one it gets right is the request that built it. Nothing raises. Every call returns
a session, and a session from the wrong request is a value of the right shape.

That is why the scope belongs to the wiring rather than to the implementation. A singleton may hold
a singleton; a singleton may not hold something that is rebuilt per request, because the container
builds the singleton once and there is no later moment at which it could be given a new one. The fix
is not a longer lifetime -- it is that the per-request object stops being held at all.

## The global that answers for everything

The pattern that injection replaces, and the reason it is worth replacing, measured by what a
signature can tell you.

<<BLOCK:service_locator>>

The locator names no dependency in the signature, and that is the property it is chosen for. The bill
arrives in the third column: one override reached all four callers, because all four read the same
global. A change meant for one test reaches production code, and the signature of the thing that
changed says nothing about it.

The zero in the first column is not a coincidence either. A dependency fetched inside a method body
is not a dependency the caller knows about, so the caller cannot provide it, cannot replace it, and
cannot read the method and find out. And the error surfaces in the wrong frame: `get` raises
`KeyError` in the middle of a method that belongs to the report, rather than at the call site that
forgot to register something.

## The dependency that is not a dependency

Every block so far has found injection paying for itself. This one is the case where it does not.

<<BLOCK:pitfall>>

Four amounts, formatted the same way by both designs. The interface adds two classes, two functions
and ten lines, and there is still one implementation of the thing being replaced.

The distinction that decides it is whether the collaborator has a seam to cut. A mailer, a clock, a
store and a session all do: they have a boundary where the real world is, and a test wants to be on
the other side of it. Formatting a number does not -- it is a function from a number to a string, and
there is nothing on the far side to replace. Injecting it anyway is not neutral: the parameter is a
promise that a second implementation might arrive, and every reader of the signature holds that
possibility in mind while nothing arrives.

The rule is the last chapter's rule applied to a parameter instead of a class: introduce the seam
when there is something to put on the other side of it, and not before.

:::pitfall The parameter that wires itself

The subtler version of the same mistake, and the one that gets written by people who would never
write a global.

<<BLOCK:hidden_default>>

Three of the four call sites build the real object without naming it, and the one that does name one
is the test. So the default did not save the production sites any work -- they still construct a real
mailer, on the line inside the function instead of the line at the call site.

What it changed is who can see the choice. With the default, the decision lives inside the function,
one copy of it for every caller, and the call site that wanted something else is indistinguishable
from the three that did not. With a required parameter there is no hidden copy, and the number of
places the choice appears is the number of call sites. It is the same shape as the resolver and the
registry in the earlier chapters: a default that produces a working object makes the wrong call site
look exactly like the right one.

:::

:::scenario The checkout, wired three ways

A checkout service, three call sites, three tests, and a vendor client that cannot be constructed in
a test. Three designs, and the count is of the tests that run and of the files that name the vendor.

<<BLOCK:scenario>>

The first design runs none of the three tests, because the object cannot be built. That is the
loudest version of the problem and the easiest to notice.

The second design runs all three and moves the vendor's name out of the service -- into every
caller. The number of files that name the vendor goes from one to three, so replacing the vendor now
edits three modules instead of one. This is where most refactors stop, because the tests pass and
the class looks clean.

The third design is the second one plus a composition root, and it is the only one that gets both
counts right: three tests run, and one file names the vendor. The service names an interface it
defined itself, the composition root names the vendor, and the callers name neither. The cost is one
new module and one new file, and what decides whether it is worth paying is the number of callers --
which is knowable before the refactor starts.

:::

## Key takeaways

- **Injection is a change to where an object comes from, and its consequences are countable.** The
  numbers to take are behaviours a stand-in can be handed, tests that depend on the order, and
  modules that name a concrete type.
- **A suite that constructs its own dependencies is green, and that is the trap.** Both designs
  passed all six behaviours; only one of them could be handed a stand-in in any of the six.
- **The one line that names the concrete type is the line that decides everything.** Remove it and
  the count goes from zero behaviours replaceable to all of them.
- **A dependency reached for by name is a dependency whose lifetime nobody chose.** The module-level
  handle made all 3 of 3 behaviours a function of what ran before them.
- **A fixture that clears shared state is not the fix.** It knows which state to clear, and it works
  only while every test remembers the line -- which is a property of the tests, not the design.
- **An interface buys the swap and not the behaviour.** The consumer named none of the three
  implementations, and it could still tell all three apart once it called them.
- **Two of three implementations returned a value for every key and the third returned two and a
  `None`.** The protocol named two methods and nothing else, so nothing in it said which was allowed.
- **Inversion does not reduce the number of references.** Each design held exactly one, and they
  pointed in opposite directions.
- **What inversion changes is which module is on the receiving end.** The unstable module ends up
  naming the stable one's interface, which is why the interface belongs to the consumer.
- **A container is worth having because the graph becomes data.** The eager one constructed nothing
  and reported the missing name before anything ran.
- **The hand-written root and the lazy container failed at the same point.** Being a container is not
  what made the difference; checking the whole graph first is.
- **A container replaces a class reference with a string.** `NameError` names the thing, `KeyError`
  names a string, and a string is not checked until the lookup happens.
- **A framework's injection is a marker in a default position.** 4 of 5 parameters were marked and
  the handler bodies named a provider in none of them.
- **Nothing checks the marker.** A parameter defaulting to `Depends(f)` is a dependency and one
  defaulting to a real object is a default, and they look identical to everything but the caller.
- **A scope is how long the object is allowed to live, and the wrong answer has no symptom.** The
  captured cache gave 2 of 3 requests the wrong session and nothing raised.
- **A singleton may not hold something rebuilt per request.** The container builds it once, and there
  is no later moment at which it could be given a new one.
- **A service locator hides the dependency from the signature, which is what it is chosen for.** It
  names 0 of 3 in the signature and one override reached all 4 callers.
- **A locator also moves the error into the wrong frame.** It raises inside the object rather than at
  the call site that forgot to register something.
- **The optional parameter did not save the call sites any work.** 3 of the 4 sites still built the
  real object; what changed is that the choice became invisible.
- **Injection is the wrong answer when the collaborator has no seam.** A pure function behind an
  interface added an interface, a class and a parameter, and no test needed a second implementation.

## Practice

- [ ] **Count the names a class reaches for.** Take a class in a project of yours whose methods call
  module-level functions or construct collaborators inside the body. List every name it depends on
  that does not arrive as an argument. Then rewrite it to take them and count again. Report both
  numbers -- and then pick one of the names you *would not* inject, and say why.
- [ ] **Measure order dependence in a suite of your own.** Take three tests that touch the same
  object. Run them in three different orders and record which results change. Then make the smallest
  change you can and measure again. Report the count before and after, and say what the change was.
- [ ] **Find the composition root, or find that there is not one.** Pick a service in a project of
  yours. Count how many modules name a concrete implementation of its dependencies. Move the
  construction into one module and count again. Report both numbers and the number of modules that
  name nothing concrete in either version.
- [ ] **Audit one interface for what it does not promise.** Take a protocol your code depends on.
  Write three implementations that all satisfy the names and behave differently in one observable
  way. Report which of the three your consumer can tell apart, which difference the protocol names,
  and what catches the ones it does not.

## Solutions

:::solution Exercise 1

A pricer whose methods reach for four names that do not arrive as arguments, and the same pricer
with them as constructor arguments.

<<BLOCK:sol1>>

:::

:::solution Exercise 2

Three tests against a shared object, run in three orders under four arrangements -- including the one
where two of the three tests remember to clear it.

<<BLOCK:sol2>>

:::

:::solution Exercise 3

Six modules and three concrete types, with the wiring in the callers and then in one module.

<<BLOCK:sol3>>

:::

:::solution Exercise 4

Three implementations of one protocol, all of which have the names and only one of which the
consumer can use as written.

<<BLOCK:sol4>>

:::
