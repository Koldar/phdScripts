Installation
============

To create the pdf (in build):

```
make
```

To clean the build directory

```
make clean
```

Note that this Makefile is **not** windows compliant!

Advance Usage
=============

To make a release of the document:

```
make release
```

Making a release will just put a copy of the generated pdf in the release/ folder (together with a version). However, it will do **nothing** about version control!
For further tweaking, see `make show-variables`. If you happen to change the internals of the Makefile, please fill the `NOTES` macro: the content of the macro will always be printed before running the compilation so future developers can see what you have changed.