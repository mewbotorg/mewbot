
_Very_ occasionally it might be necessary to add new component types to mewbot.
These would be new fundamental objects on the same level as the IOConfigs, Inputs, e.t.c.
(You may well have forked mewbot, and want to change it fundamentally).

# Stage 1 - Architecture

There's a number of questions you need to answer before you start.

1) Do you _actually_ need a new component? Or can you reuse an existing one
2) What does this component look like? What are its functions? What are its methods?

# Stage 2 - Interface 

The initial work needs to be done in the core module.
This holds the interface protocols for mewbot components.
Start off by writing a Protocol to define how implementations of your component will interact with the world.

This should descend from typing.Protocol.

Go through and write the protocol interface for it.

# Stage 3 - Add to "Component"

The Component variable is a basic type - if a Component conforms to an interface store in this variable it _is_ a 
mewbot component.

It looks something like this

```python
Component = Union[
    IOConfigInterface,
    TriggerInterface,
    ConditionInterface,
    ConditionInterface2,
    ActionInterface,
    BehaviourInterface,
]
```

Add your interface to the definiton of a Component.

# Stage 4 - Update "ComponentKind"

ComponentKind contains the canonical names of mewbot components and maps them to their interfaces.

It'll look something like this

```python
class ComponentKind(str, enum.Enum):
    """
    Enumeration of all the meta-types of Component.

    These are all the components that a bot is built out of.
    These all have a matching interface above (except for DataSource
    and Template which are not yet implemented, but in the specification)
    """

    Behaviour = "Behaviour"
    Trigger = "Trigger"
    Condition = "Condition"
    Action = "Action"
    IOConfig = "IOConfig"
    Template = "Template"
    DataSource = "DataSource"

    @classmethod
    def values(cls) -> list[str]:
        """List of named values."""

        return list(e for e in cls)

    @classmethod
    def interface(cls, value: ComponentKind) -> type[Component]:
        """Maps a value in this enum to the Interface for that component type."""

        _map: dict[ComponentKind, type[Component]] = {
            cls.Behaviour: BehaviourInterface,
            cls.Trigger: TriggerInterface,
            cls.Condition: ConditionInterface,
            cls.Action: ActionInterface,
            cls.IOConfig: IOConfigInterface,
        }

        if value in _map:
            return _map[value]

        raise ValueError(f"Invalid value {value}")
```

You need to add the name of your new component to the enum itself.
You'll also need to add it to the `interface` method - which maps component names to their interface protocol.

# Stage 5 - Allow your component interface to be exported by the core

Add your componet's interface to the `__all__` property of the core.

# Stage 6 - Updating the api

If you've added a new component, you should consider changing the api as well.
However, here, assuming you're just working with an existing one, for simplicity.

Add a class, descending from Component, with the same interface as the declared protocol.
Decorate the class methods as appropriate with abc.abstractmethod.

Here is the place to include additional logic which will be common to all instances of the new component.

# Stage 7 - Wrapup

Run mypy to check that it reports no errors with the class installation.

# Common errors

If you get an error like

```shell
src\mewbot\api\v1.py:495: error: Argument 1 has incompatible type
"Type[DataSource]"; expected
"Union[Type[IOConfigInterface], Type[TriggerInterface], Type[ConditionInterface], Type[ActionInterface], Type[BehaviourInterface], Type[DataSourceInterface[Any]]]"
 [arg-type]
    @ComponentRegistry.register_api_version(ComponentKind.DataSource, "v1"...
```

you may be confused as to how to fix it.

Mypy is being slightly unhelpful.
The root of the problem is a mismatch between the interface declared as a Protocol in core and the interface for the
actual component declared in `v1.py`.

Change the interface of the protocol and the interface of the component to match, and the problem should go away.


