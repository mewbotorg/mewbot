The architectural decision to ship the tests for a package as a seperate module is an unusual one.
It was taken because of some problems encountered when trying to incorporate independant module tests into the test framework.
The flow was
 - discover paths to the test modules - declared by the plugin modules
 - add them to pytest (with `.\tests` at the beginning, to ensure the mewbot test folder was prepended to the path first - which helped some of the technical issues)
 - run pytest with the additional paths - and the paths to the mewbot tests themsevles - added

This worked well enough, but was somewhat less than elegant.

However, things broke badly when the --cov flag was applied.
This seemed to be some kind of consequence of the way --cov handles itself - all intensely annoying.
(In particular, the problem seemed to originate in some of the path hacking pytest does. 
With --cov enabled, the system could no longer find the `tests` `module` to import from - so the run failed at collection time with ModuleNotFound errors. 
All intensely annoying.)

There were a number of solutions available, but splitting the tests down into a separate module seemed to be both the most elegant and in keeping with the modular design of the overall system.

