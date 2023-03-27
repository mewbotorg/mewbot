
### Help! ASCII colour codes are not working on Windows!

Windows has some buggy handling when it comes to ASCII colour codes.
In particular when colouring strings by directly printing them to the command line.

If you are getting symbols like `←[2m` - then you are encountering this problem.

See https://stackoverflow.com/questions/12492810/python-how-can-i-make-the-ansi-escape-codes-to-work-also-in-windows

Long story short, the workaround is to run

```python
import os
os.system("")
```

before printing ASCII colour codes.

This seems extremely unfortunate to me, but happens to be the world we live in.

Moving on to a general fix

https://unix.stackexchange.com/questions/249723/how-to-trick-a-command-into-thinking-its-output-is-going-to-a-terminal

