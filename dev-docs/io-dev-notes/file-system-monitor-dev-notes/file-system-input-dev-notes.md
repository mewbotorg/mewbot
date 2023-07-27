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

# Enhancement - where did my watched file come from?

While I was re-writing this method to break it down, it occurred to me that events such as

FileMovedToWatchLocationFSInputEvent
FileMovedFromWatchLocationFSInputEvent

would make sense to include.
But how?

The only good way to do this seems to be to monitor the folder the target file is in for changes.
Then generate events off these changes.

Doing this efficiently is something of a challenge.
Because the location we're being asked to monitor does not have to exist.

 - Could just monitor the root of the file system and then filter for events of interest.
 - But this seems really inefficient.
 - Alternatively, need to work back up from the given location - until we find a dir to monitor.
 - We can monitor from this location, looking for something to be moved into the target loc
 - Until something appears there - or one of the directory's needed between the current loc and there does - then we can jump there.
 - For the purposes of efficiency.

The ordering of the jump when a folder in the chain is detected is important.
So that we can be _reasonably_ sure of not missing events.
(Though we should also add some kind of warning that these monitors are less than perfect).

Program flow - for enhanced file monitoring (monitoring which allows us to tell - if a file is copied into the monitored location - where it came from).

1. Check - does the target file exist?
2. If yes - monitor that using current methods - job done.
3. If no - then find the highest dir up in the file hierarchy that does exist - monitor that
4. If this dir gets deleted 
   1. jump up till we find one which still exists
5. If a dir is created in this one
   1. If it matches the next key in the path we're expecting, jump down to it
   2. Otherwise, stay put

If we're moving the monitor.
1. There might be an interruption as the old monitor shuts down and the new one starts up
2. So need to take account of that

All this seems both complicated and fragile.
So it seems better to try and use watchdog to do this more directly.

Monitor the entire file system by watching the root, and filter for events in the file we actually care about.

Watchdog has a "pattern matching event handler" - this seems the right tool to use.

However, it turned out to be a more major re-write than expected.

Excised the following events from fs_events - will deal with it later.

```python

@dataclasses.dataclass
class FileMovedToWatchLocationFSInputEvent(FileAtWatchLocInputEvent):
    """
    A file has been moved to the location being watched.
    """

    file_src: str


@dataclasses.dataclass
class FileMovedFromWatchLocationFSInputEvent(FileAtWatchLocInputEvent):
    """
    A file has been moved to the location being watched.
    """

    file_src: str

```



















