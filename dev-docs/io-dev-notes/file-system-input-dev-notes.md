<!--
SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: BSD-2-Clause
-->

Notes on the development of mewbot-io-file-system-input

Please see `file-system-dev-notes.md` for the notes for this project before it got split into two separate plugins -
an input and an output.

(If nothing else, this made sense - because it turned out we needed three different techniques.
 - monitoring files
 - monitoring folders
 - actually writing out to the file system

and all of these ended up using different libraries and method.
So this ended up being three different classes stuffed into a trench coat.
)

I also make no apologies for some of the doc strings containing monitor puns.
("File System monitor is monitoring the situation. Hisss!")

Really, the file and folder monitors are fairly different programs - but they're bundled together in a single plugin
to help deal with cases like, e.g. "I want to monitor this location. 
If there is a folder created there, I want to watch what happens inside of it.
If there is a file created there, I want to watch it for changes."
