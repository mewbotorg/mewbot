<!--
SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: BSD-2-Clause
-->

# Typing issues

The main problem with DataSources/DataStores (DSS) is the typing.
Which I'm not sure _can_ be solved.

## 1 - General problems with typing arbitary structures

Adding a conformance function to the DataSource/Store has helped a lot.
(A function which assures that the return is of the type declared when the Data structure is initialized.)
You can use this before return functions, and for data validation on the way in.
Which seems to keep the type checkers (mostly) happy.

Doing this automatically would be nice, but requires some heavy type introspection which seems either quite hard, or
impossible.

It would also (e.g. for Json) be nice to allow arbitrary data structures to be expressed and accessed through stores.
This is, however, extremely difficult to square the circle with type checkers.
I think the best compromise is to build out the base cases, and to try and make the base classes easily extendable.
People can then create custom a DSS for the structure they want to express in json (with some, potentially quite gnarly, 
checking code to validate the structure as it's loaded/accessed/modified by the DSS).

## 2 - Typing structures loaded out of yaml

DSSs are unlike the other components, in that they have more divergent interfaces.
Probably the best way, if an Action/Trigger e.t.c. requires a certain DataStore, is to ship protocols for each of the 
base types of DataStore - people can then use these in place of _specific_ DSSs to make their code more portable.
Probably going to need a guide to using Data in your bot...
And one for writing new DSSs.

Hey, ho.
We need persistent data - and we need it to be easy as possible.