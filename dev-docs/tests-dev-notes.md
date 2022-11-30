
Due to some slightly annoying technical issues with coverage - and in line with the overall project goals of modularizing as far as possible - the tests will be shifted out into their own module.

```
mewbot-tests
```

which will be provided in the `plugins` folder of the main repo - for the moment - but may be shifted out into its own repo at some point.

The aim of this module - aside from getting round some annoying features of coverage (such as the fact that pytest seems to no longer be able to find the main `tests` module when its in use) is to allow the tests to be self-contained.
This provides several advantages
 - its neater
 - it allows for more flexible deployments ("I want to test this cythonized mewbot on this weird ARM CPU. I'll just download mewbot-tests and run it!")
 - it may make --cov actually work.

Should I split the tests for my mewbot projects down in this way?

You can!
But it's often more effort than it's worth.
mewbot does it because it allows easier testing of the core modules in unusual deployments.
If this might be something that you want to do?
It's probably also a good idea to split your tests out into a seperate module as the main program does.
If not, then there's no real reason to bother.

After some work

 - pytest seems to default to assuming every directory one level up should be included for coverage, if not explicit argument is passed to `--cov`
 - If you pass any arguments to `--cov` (in the form `--cov=some_path`) then you need to pass all relevant paths in this way - the implicit inclusion of the parent path from where pytest is being run will not survive.
 - So you need to explicitly add the appropriate locations using `mewbot_dev_hook_impl`
 - You can add the location of tests to the end of the pytest command and it should all work out (tests are added in the form of a list of paths - no prefix or anything).
 - This has been tested with all the test distribution mechanisms, and seems to work.

Public interface

As part of the `mewbot_dev_hook_impl` the functions `declare_test_locs` and `declare_src_locs` are provided.
These allow you to declare a tuple of tests locations and a tuple of src code locations (in case that's relevant to your project).
These will then be picked up and run by the testing infrastructure.
In particular
Linting
 - By default linting lints all the declare src locations
 - (Might be an idea to add a `--tests` option to linting - so that the linting can include the tests if desired)