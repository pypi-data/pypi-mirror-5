FileTranscriber
===============

A small utility that simulates user typing to aid plaintext file transcription
in limited environments

  Usage:

    transcribe <file> [--interval=<time>] [--pause=<time>]

    transcribe (--help | --version)

  Options:

    -i --interval=<time>  Interval between keystrokes (in seconds). Typing too

                          quickly may break applications processing the

                          keystrokes. [default: 0.1]

    -p --pause=<time>     How long the script should wait before starting (in

                          seconds). Increase this if you need more time to enter

                          the typing field. [default: 5]

What it does
------------

Sometimes you find yourself unable to copy text data into a field or application
but with a keyboard you *could* type it all in by hand... what a hassle.

Let this do tedious work and avoid typos.

When you launch this script, you give it the location of a file and (optionally)
a between-keystroke time interval to control the rate of typing. It will then ask
you to press "Enter" when you are ready for it to begin typing. After a short
pause (default is 5s), it will begin typing; use the pause time to enter the field
for the text. To abort the typing in progress, click any mouse button.

More information
----------------

[docopt](https://github.com/docopt/docopt) is used for the commandline argument
parsing. If you install by pip, this should install automatically if you do not
already have it.

FileTranscriber relies on [PyUserInput](https://github.com/SavinaRoja/PyUserInput),
which is a python module for cross-platform simulation and tracking of user input.
This should also install automatically with pip if you do not already have it.

The dependencies for PyUserInput depend on your platform and will probably require
manual installation, search for the versions appropriate for your computer and
version of python:

  * Linux - Xlib
  * Mac - Quartz, AppKit
  * Windows - pywin32, pyHook

If you experience any problems with the use of this script or PyUserInput, please
let me know. I would also appreciate helpful suggestions for improvement.
