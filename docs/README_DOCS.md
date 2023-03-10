
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

## Help! Sphin is complaining about `WARNING: Field list ends without a blank line; unexpected unindent.`

### And adding lines before the error does not seem to move where the error occurs

E.g. The error is reported on line 54, and adding more lines before line 54 does not seem to move the line reporting the error.
(In this case, the error was well before - around line 23. 
Notably _removing lines 23->End _did not resolve the error_. 
The error was still reported on line 54 when line 54 was beyond the end of the document).

This seems to be a valid problem.
Something about the `.md` -> `.rst` conversion is confusing `sphinx`.
The upshot of this is it cannot determine where the line which is causing the difficulty is _actually_ found.
So this means that there is a badly indented line _somewhere_ in the file it's complaining about.
Might I suggest a binary search?

(In this example, the problem was, eventually, tracked to a line which read

```md
> :warning: This project is still in the very early stages. Some basic bots can be built
> and run, but we currently consider all parts of the framework to be unstable.
```
Which was just not translating properly.
An alternative method of emphasis was adopted.)

## I fear sphinx!

This is understandable and natural.

Can I recommend some resources to get you started?

https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs/
https://pythonhosted.org/an_example_pypi_project/sphinx.html


# Things to look into later

https://towardsdatascience.com/five-tips-for-automatic-python-documentation-7513825b760e
