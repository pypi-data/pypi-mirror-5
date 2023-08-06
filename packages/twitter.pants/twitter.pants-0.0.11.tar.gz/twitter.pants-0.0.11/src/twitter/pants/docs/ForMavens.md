If you're used to Maven and learning Pants, you're part of a growing crowd.
Here are some things that helped other folks come up to speed.

[TOC]

#Overview

The three distinguishing features of pants that are most unfamiliar to maven
users are:

* pants has a first-class mechanism for targets depending on other targets on
  the local file system
* pants targets do not specify version numbers; versions are only determined
  during release
* BUILD files are python code that pants evaluates dynamically

The first two points are a significant departure from Maven's handling of
inter-project dependencies. The last point isn't necessary for understanding
how to read and write most BUILD files, but is helpful to be aware of.

#Pants Equivalents

`exec:java` run a binary
: `goal run`

`-Xdebug` run a binary in the debugger
: `goal run --jvm-run-debug`

`-Dtest=com.foo.BarSpec -Dmaven.surefire.debug=true test` run one test in the debugger
: `goal test --test-junit-debug --test-junit-test=com.foo.BarSpec` or `goal test --test-specs-debug --test-specs-test=com.foo.BarSpec`

#Depending on Source, not Jars

Pants arose in an environment of a big multi-project repo. Several teams
contributed code to the same source tree; projects depended on each other.
Getting those dependencies to work with Maven was tricky. As the number of
engineers grew, it wasn't so easy to have one team ask another team to release
a new jar. Using snapshot dependencies mostly worked, but it wasn't always clear
what needed rebuilding when pulling fresh code from origin; if you weren't sure
and didn't want to investigate, the safe thing was to rebuild everything your
project depended upon. Alas, for a big tree of Scala code, that might take 45
minutes.

Pants has a first-class concept of "depend on whatever version of this project
is defined on disk," and caches targets based on their fingerprints (i.e. SHAs
of the contents of the files and command line options used to build the
target). When code changes (e.g., after a git pull), pants recompiles only
those targets whose source files have differing contents.