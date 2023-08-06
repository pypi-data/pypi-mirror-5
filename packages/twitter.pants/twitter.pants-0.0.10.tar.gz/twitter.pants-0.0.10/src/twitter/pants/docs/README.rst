Pants Build: Read Me First
==========================

(For more introductory material, see
:doc:`first_concepts` and :doc:`first_tutorial`.)

Installing and Troubleshooting Pants Installations
--------------------------------------------------

See :doc:`install`

Using Pants
-----------

Pants is invoked via the `pants` script, usually located in the root of
your source repository. When you invoke pants, you specify one or more
goals, one or more targets to run those goals against, and zero or
more command line options.

A pants command line has the general form::

    pants goal <goal(s)> <target(s)> <option(s)>

Options don't need to be at the end. These both work::

    pants goal compile --compile-scalac-warnings test src/main/scala/myproject
    pants goal compile test src/main/scala/myproject --compile-scalac-warnings

To see a goal's configuration flags, use `pants goal help _goal_`, e.g.::

    pants goal help compile

(The `goal` command is an intermediate artifact of the
migration from "pants.old" to "pants.new". In the near future, the `goal`
command will disappear. We'll use `pants` *foo* instead of `pants goal` *foo*.)

**Goals available:** Run `pants goal` to list all installed goals::

    [local ~/projects/science]$ ./pants goal
    Installed goals:
      binary: Create a jvm binary jar.
      bundle: Create an application bundle from binary targets.
      checkstyle: Run checkstyle against java source code.
      ......


Library Targets
```````````````

To define an "importable" thing, you want a library target type, such as
`java_library`, `python_library`, `jar`, or `python_dependency` (Python egg). ::

  scala_library(
    name = 'util',
    dependencies = [pants('3rdparty:commons-math'),
                    pants('3rdparty:thrift'),
                    pants('core/src/main/scala/com/foursquare/auth'),
                    pants(':base')],
    sources = globs('*.scala'),
  )

A target whose code imports this target's code should list this target
in its `dependencies`.

Binary Targets
``````````````

To define a "runnable" thing, you want a `jvm_binary` or `python_binary` target.
A binary probably has a `main` and dependencies. (We encourage a binary's
main to be separate from the libraries it uses to run, if any.)::

  jvm_binary(name = 'junit-runner-main',
    main = 'com.twitter.common.testing.runner.JUnitConsoleRunner',
    dependencies = [ pants(':junit-runner') ])

External Dependencies
`````````````````````

Not everything's source code is in your repository.
By convention, we keep build information about external libraries in a
directory tree whose root is called `3rdparty.` For example *java jars*::

    jar_library(name='jackson',
      dependencies=[
        jar(org='org.codehaus.jackson', name='jackson-core-asl', rev='1.8.8').withSources(),
        jar(org='org.codehaus.jackson', name='jackson-mapper-asl', rev='1.8.8').withSources(),
        jar(org='org.codehaus.jackson', name='jackson-xc', rev='1.8.8').withSources()
      ]
    )

The target name is a convenient alias for an external
jar (or, as in this example, multiple jars). These `jar`
targets have no `sources` argument, but instead the
information `ivy` uses to fetch the jars.

The 3rdparty idiom arose to mitigate the "diamond-dependency" problem.
If a program transitively-depends on two versions of the same jar, ivy
picks a version; those versions might not be compatible. By specifying
a jar version in a common place, all the repo's targets depend on the
same version.  (Since external jars might depend on different versions
of other jars, 3rdparty doesn't eliminate the problem; just makes it
much rarer.) For python libraries this might look like::

    python_library(
      name='beautifulsoup',
      dependencies=[python_requirement('BeautifulSoup==3.2.0')]
    )
    python_library(
      name='markdown',
      dependencies=[python_requirement('markdown')]
    )

The target name is a convenient alias. The `dependencies` is a list of one
or more `python_requirement` targets. The `python_requirement` can refer
to a `pkg_resources` `requirements string`_.
Pants looks in a few places for Python `.egg`\ s as configured in your
`python.ini` file's `python-repos` section.

.. _`requirements string`: http://packages.python.org/distribute/pkg_resources.html#requirements-parsing

To use the external Python module, another python target could have a
dependency::

    python_binary(name = 'mach_turtle',
      source = 'mach_turtle.py',
      dependencies = [pants('3rdparty/python:beautifulsoup')]
    )

...and the Python script's import would look like::


    from BeautifulSoup import BeautifulSoup

Test Targets
````````````

Your test code might live in a directory separate from the main source tree.
BUILD files defining test targets probably live in that directory tree.::

    # in test/scala/com/twitter/common/args/BUILD
    scala_tests(name = 'args',
      dependencies = [
        pants('3rdparty:specs'),
        pants('src/scala/com/twitter/common/args:flags'),
        pants('src/java/com/twitter/common/args:args'),
      ],
      sources = globs('*Spec.scala'))

The test target depends upon the targets whose code it tests. This isn't just
logical, it's handy, too: you can compute dependencies to figure out what tests
to run if you change some target's code.::

    # Forgot your test's name but know you changed src/main/python/foo:foo?
    pants goal test `./pants goal dependees src/main/python/foo:foo`

    # Run dependees' tests, for src/main/python/foo:foo too.
    pants goal test `./pants goal dependees src/main/python/foo:foo --dependees-transitive`

Common Tasks
------------

**Compiling**
    pants goal compile src/main/java/yourproject

**Running Tests**
    pants goal test src/test/java/yourproject

**Packaging Binaries**
  To create a jar containing just the code built by a target, use the
  `jar` goal::

      pants goal jar src/main/java/yourproject

  To deploy a "fat" jar that contains code for a `jvm_binary` target and its
  dependencies, use the `binary` goal and the `--binary-deployjar` flag::

      pants goal binary --binary-deployjar src/main/java/yourproject

**Invalidation**
  The `invalidate` goal clears pants' internal state.::

      pants goal invalidate compile src/main/java/yourproject

  invalidates pants' caches. In most cases, this forces a clean build.

**Cleaning Up**
  The `clean-all` goal does a more vigorous cleaning of pants' state.::

      pants goal clean-all

  Actually removes the pants workdir, and kills any background processes
  used by pants in the current repository.

**Publishing**
  TODO: this

**Adding jar dependencies**
  TODO: this

**Generating Source**
  TODO: this

Credits
-------

Pants was originally written by John Sirois.

Major contributors in alphabetical order:

- Alec Thomas
- Benjy Weinberger
- Bill Farner
- Brian Wickman
- David Buchfuhrer
- John Sirois
- Mark McBride

If you are a contributor, please add your name to the list!
