
"""
It makes sense to isolate plugin tests in the same folder as the plugin themselves.
(After all, the plugins in the plugins folder are mostly here as an example
- though they should, also, be quite useful).
They will (mostly) be distributed as completely separate packages.
However, some level of integration with the main testing package would be highly desirable.
If nothing else, it would be nice to be able to run all the tests along with the main
test suite.
"""