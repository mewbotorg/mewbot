### Errors

Components are intended to interface with the registry system - they are registratable objects.
The intent of this is that the system knows what objects have been registered so it can present to the user on an API level all the components which can be included in a bot configuration.
However, setting this up does mean adding some definitions in a couple of different places.

### If you are changing a declared API

Firstly, consider not doing this.
Mewbot supports running multiple different API versions at the same time.
So it might be worth considering making a new one instead of modifying an old one.
However, there are times when you need to - and you might get the following error (or something like it) from the linters.

```shell
src\mewbot\api\v1.py:285: error: Argument 1 has incompatible type "Type[Manager]"; expected
"Union[Type[BehaviourInterface], Type[IOConfigInterface], Type[TriggerInterface], Type[ConditionInterface], Type[ActionInterface], Type[ManagerInterface]]"
```

This means that there is a "mismatch" between the interface declared in the api (e.g. in `v1.py`) and the class found in the core.
I say "mismatch", because the linting system is very easily confused and the error message is not the most helpful.
Things which can confuse it
 - Having properties in the core definitions
 - mismatch between the method definitions in the api def and the core
 - Not providing type information in either place
 - The type info not matching in either place (sometimes)
Try correcting any of these and hopefully it should fix it.




