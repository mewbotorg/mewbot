The fundamental purpose of the Manager class is simple.
I wanted to be able to type "!status" into discord and get a useful answer.

### Command triggering

So one of the manager's functions should be "system commands" - things like
 - !status
 - !help (marshalled all in one place, but also help for the sub-commands)
 - !disable [command-name]
 - !listcommands
e.t.c - things which require introspection of the state of the bot to construct.

Another approach would be something like a new class IntrospectiveBehavior - which can introspect the bot.
This might be more appropriate for !help and !listcommands.

But there definitely also needs to be a Manager - if we want to disable and enable commands

So the Manager needs to act like a Trigger and a Behavior.
Because it needs to respond to a command with some behavior.

#### Approach 1

However, how, exactly, does it know how to deal with all the input methods that _might_ get defined?
There needs to be some way to do manager command acceptance for all the input methods ... and this should, ideally, be
defined with the input method.
(Allowing access to the manager for some of them doesn't even make much sense  - you _probably_ don't want a manager 
which responds to RSS input events, for example. Probably).
So it seemed to make sense to define those triggers as part of the IO method itself.
That way it's the implementers' responsibility to define them - or not.
In which case that input cannot trigger manager commands.

The details of that trigger should be, definitely, stored in the manager - so they only need to updated in one
place if a new command e.t.c is added to the manager.

So there's two components of the acceptance
 - the standardizer in the input
 - the actual acceptance in the manager

Output needs to also be handled - probably in the IOConfig again (outputs could take a lot of forms - probably also want
to allow people to just put an output event on the queue)

NOTE - PrintOutputEvent just built into the bot to print to shell? Seems to make sense - but not right now.

Thus, something lik this seems to make sense
1) The input generates an Incoming message event and passes it to the bot
2) Manager (if it exists) - at the bot level - snags the message before it's passed to the triggers
3) Manager calls the inputs which could have produced the input and asks "is this a manager call?" (currently by calling a method)
   1) The way the inputs do this, internally (e.g. for discord)
   2) Render the message into a text string
   3) Pass it to the manager's acceptance function - so knowing if the manager responds to that event is just up to the manager
   4) Return the result - so the manager can actually trigger an internal behavior
4) Manager executes the call
5) Manager passes the results of the call back to the IOConfig - which has to handle output (note - output could be producing a queue event)

MAJOR DISADVANTAGE - Strongly couples the program - which is less than ideal as it currently all communicates via qeues.
Which is a real advantage.

#### Approach 2

ANOTHER APPROACH WHICH MIGHT BE BETTER

Keep the program loosely coupled.
1) The input generates an incoming message event
2) Manager (if it exists) - at the bot level - snags the message and passes it back to the input - with the info the IOManager needed to determine if it's a manager message
3) The input determines if it's a manager message and puts and Manager command event on the wire
4) Manager snags the command event and responds to it

The bounce backwards and forwards needs to happen for two reasons.
1) There might not be a manager - in which case the message is never passed back.
2) Only the IOConfig knows how to test to see if a message is, potentially, a manager message 

To elaborate on 2) - because the inputs could be in many forms - either the manager needs to know what all 
these forms could be or the IOConfig needs to know, and be used, to bring it into the same form as the manager
 - an elegant way to do this might be to store a ManagerInputAdapter in the same file as the io config ... then let the manager import it
 - Or pass the message back to the IOConfig for processing

#### Approach 3

YET ANOTHER APPROACH

Which cuts down on the number of hops and may make things simpler.
Prime the IOConfig with the info it needs to decide if an incoming message event is for the manager or not.
It can then generate a ManagerCommand event and put it on the wire.

Advantages 
 - conceptually simple (though may be slightly harder to implement)
 - probably more efficient - involves less hops backwards and forward
 - All trigger logic can be contained in the Input - just don't bother impementing the logic if you do not want the input to be able to trigger the manager

Disadvantages
 - We're doing the triggering in the Input itself - it's conceptually mismatched to the current design ethos
 - Means more computation is occurring in the Input - which might not be where people expect.






### 



