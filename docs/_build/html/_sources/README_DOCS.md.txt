
# Welcome to the mewbot docs!

Mewbot is a plugin friendly, multi-platform, chatbot framework which can load bots from YAML definitions.

The docs are built using `sphinx`.

# What should go in here?

Anything and everything related to mewbot
 - installing it 
 - running it
 - debugging it

This should be the primary knowledge repository for mewbot.
(Things like github issues are all well and good, but github itself may go away one day.)

# Why are there a mix of md files and rst files in here?

`sphinx`, by default, uses`.rst` files.
However it can use `.md` files, and others, with appropriate plugins.
Some of the files are legacy files which where written in a certain format.
As such they have not, yet, been translated.

# How do I build this documentation?

1) Make sure you've run `pip install -r requirements-dev.txt` sometime recently.
2) This will install `sphinx` and the plugins it needs to build
3) `cd` into `./docs` (the folder containing this file)
4) Run `sphinx-apidoc -o source_mewbot/ ../src/mewbot` - This will recursively generate sphinx docs for the entire code base off the docstrings embedded in the code itself.
5) Run `sphinx-apidoc -o source_examples/ ../src/examples` - This will do the same for the examples .
6) The output of this will be stored in the `source_mewbot` and `source_examples` folders respectively.
7) NOTE - doc strings in the source are considered a source of truth. Please DO NOT edit the generated files - please edit the doc strings in `src` directly.
8) Run `python generate_sub_indexes.py` - this will generate index files for `design-docs`, `dev-docs` e.t.c. as well as the auto generated fies in `source_mewbot` and `source_examples`
9) Run `python purge_sphinx_cache.py` - to actually make these changes show up anywhere.
10) Run `make html` (or any of the other output methods supported by `sphinx` - for a full list see their documentation)
11) The doc files will be generated in the `_build/html` in this directory
12) Open `_build\html\index.html` with your favourite web browser, and enjoy!

# How to I contribute to these docs?

More documentation is always welcome!
These docs are intended as a living document.
Feel free to add to them.
In particular, details of problems you encountered - and how you solved them - would be most welcome.

# Doc strings

Another very helpful thing you can do is add to, or further build out, the doc strings at module, class and function level.
Sphinx uses the reStructuredText Docstring Format.

See https://peps.python.org/pep-0287/ for more information.

For the use of rst with sphinx, please see  https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html.
Note this is a typed library, so we should not have to explicitly type our variables in the doc string.

# Troubleshooting

## Help! My doc changes are not showing up!?

https://stackoverflow.com/questions/17366625/sphinx-uses-old-module-code

Delete the `_build/doctrees` folder.
Additional functionality will be added to `conf.py` which should render this unnecessary to do manually.
If in doubt, delete it anyway.
There seems to be some issues with `sphinx` caching.

## Help! Sphinx is complaining about `WARNING: Field list ends without a blank line; unexpected unindent.`

Or similar error.

This is regretfully common, and something in the `sphinx` parser seems positively allergic to reporting the correct line which is causing the error.

NOTE - This, sometimes, _does not_ seem to meaningfully change output when the error is resolved.
It may be safe to ignore.

### Adding lines before the error does not seem to move where the error occurs

E.g. The error is reported on line 54, and adding more lines before line 54 does not seem to move the line reporting the error.
(In this case, the error was well before - around line 23. 
Notably _removing lines 23->End _did not resolve the error_. 
The error was still reported on line 54 when line 54 was beyond the end of the document).

This seems to be a valid problem.
Perhaps something about the `.md -> .rst` conversion is confusing `sphinx`.
The upshot of this is it cannot determine where the line which is causing the difficulty is _actually_ found.
So this means that there is a badly indented line _somewhere_ in the file it's complaining about.

The best way I have currently found to track it down is a binary search.

### The error seems to be meaningful, but on the wrong line

(In this example, the problem was, eventually, tracked to a line which read

```md
> :warning: This project is still in the very early stages. Some basic bots can be built
> and run, but we currently consider all parts of the framework to be unstable.
```
Which was just not translating properly.
In particular, the `:warning:` emoji was not rendering, and throwing the error.
An alternative method of emphasis was adopted.
However, directly entering the unicode value of the desired emoji was also found to work in subsequent testing).

## I'm worried about using `sphinx`. It seems a little tricky.

This is understandable and natural.
However, it is _quite good_ at generating documentation.
Although considerable effort in configuration and troubleshooting seems to be sometimes needed.

Can I recommend some resources to get you started?

1) https://www.sphinx-doc.org/en/master/ (bit deep end, but very comprehensive)
2) https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html (good introduction, but assumes `sphinx` is being used in the context of `readthedocs` - which is not our current intent)
3) https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs/ (same problem as above, but a better introduction)
4) https://pythonhosted.org/an_example_pypi_project/sphinx.html (working example)

# Things to look into later

https://towardsdatascience.com/five-tips-for-automatic-python-documentation-7513825b760e
