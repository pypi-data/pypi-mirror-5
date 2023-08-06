Pants Conceptual Overview
*************************

Pants is a build system for software.
It works particularly well for a source code repository
that contains many distinct but interdependent pieces.

Pants is similar to ``make``, ``maven``, ``ant``, ``gradle``, ``sbt``, etc.;
but pants pursues different design goals. Pants optimizes for

* building multiple, dependent things from source
* building code in a variety of languages
* speed of build execution

A Pants build "sees" only the target it's building and the transitive
dependencies of that target.
This approach works well for a big repository containing several things;
a tool that builds everything would bog down.

Goals and Targets
=================

To use Pants, you must understand a few concepts:

**Goals** are the "verbs" of Pants.
  When you invoke Pants, you name
  goals on the command line to say what Pants should do. For example,
  to run tests, you would invoke Pants with the ``test`` goal.

**Targets** are the "nouns" of Pants, build-able things.
  You annotate
  your source code with ``BUILD`` files to define these targets.
  For example, if your ``tests/com/twitter/mybird/`` directory contains
  JUnit tests, you have a ``tests/com/twitter/mybird/BUILD`` file with
  a ``junit_tests`` target definition.

When you invoke Pants, you specify goals and targets: the actions to
take, and the build-able things to carry out those actions upon.

Goals can "depend" on other goals. For example, there
are ``test`` and ``compile`` goals. If you invoke Pants with the ``test``
goal, Pants "knows" it must compile tests before it can run them, and
does so.

Targets can "depend" on other targets. For example, if your ``foo`` code
imports code from another target ``bar``, then ``foo`` depends on ``bar``.
You specify this dependency in ``foo``\'s target definition in its ``BUILD``
file. If you invoke Pants to compile ``foo``, it "knows" it also needs to
compile ``bar``, and does so.

Target Types
============

Each Pants build target has a *type*, such as ``java_library`` or
``python_binary``. Pants uses the type to determine how to apply
goals to that target.

**Library Targets**
  To define an "importable" thing, you want a library target type, such as
  ``java_library`` or ``python_library``.
  Another target whose code imports a library target's code should list
  the library target in its ``dependencies``.

**Binary Targets**
  To define a "runnable" thing, you want a ``jvm_binary`` or ``python_binary``
  target.
  A binary probably has a ``main`` and dependencies. (We encourage a binary's
  main to be separate from the libraries it uses to run, if any.)

**External Dependencies**
  Not everything's source code is in your repository.
  Your targets can depend on ``.jar``\s or ``.eggs``\s from elsewhere.

**Test Targets**
  To define a collection of tests, you want a ``junit_tests``, ``scala_specs``,
  ``python_tests``, or ``python_test_suite`` target.
  The test target depends upon the targets whose code it tests. This isn't just
  logical, it's handy, too: you can compute dependencies to figure out what
  tests to run if you change some target's code.

For a list of all Target types (and other things that can go in ``BUILD``
files), see :doc:`build_dictionary`.

Next Step
=========

If you're ready to give Pants a try, go to :doc:`first_tutorial`.
