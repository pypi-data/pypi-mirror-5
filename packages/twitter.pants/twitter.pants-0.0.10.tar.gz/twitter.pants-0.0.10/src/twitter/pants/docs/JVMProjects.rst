Using Pants with JVM Projects
=============================

Some Pants details especially interesting to folks working in Java, Scala, and
other JVM languages.

.. No need for toc. Auto generated on the sidebar

Relevant BUILD targets
----------------------

**Assembly**

* **jvm_binary** Executable, has a `main`
* **jvm_app** A binary plus bundles of files.

**Library**

* **java_library** produces and optionally exports a java jar, supports monolithic deploy jars, resources, and exporting a public maven artifact
* **scala_library** produces and optionally exports a scala or mixed scala and java jar, supports monolithic deploy jars, resources, and exporting a public maven artifact
* **dependencies** Target that "wraps" one or more dependencies, e.g., `jars`.
* **jar_library** Synonym for `dependencies` historically used in `twitter/commons` to "wrap" `jar` dependencies.

**Test**

* **java_tests** produces a runnable junit test suite
* **scala_tests** produces a runnable scala spec suite

**IDL**

* **java_thrift_library** produces and optionally exports a jar of generated java thrift stubs, supports exporting a public maven artifact
* **java_protobuf_library** produces and optionally exports a jar of generated java protobuf messages, supports exporting a public maven artifact

**Support**

* **jar** Reference to a jar fetchable from a maven repository.
* **annotation_processor** produces and optionally exports a javac annotation processor library
* **artifact** artifact a `java_library` or `scala_library` exports to an Ivy/Maven repo.
* **repo** Repository used by an `artifact`
* **exclude** Exclusion pattern for transitive dependencies.


BUILD for a Simple Binary
-------------------------

The pingpong_ sample code shows the BUILD file for a simple Java binary.

.. _pingpong: https://github.com/twitter/commons/blob/master/src/java/com/twitter/common/examples/pingpong/BUILD


The binary doesn't have any source files; it *does* depend on another build
target, `pingpong-lib`, and that library does have source files. (This
no-sources-for-binary pattern is common; it makes more sense for binaries that
depend on more things.) ::

    jvm_binary(name='pingpong',
      basename='pingpong',
      main='com.twitter.common.examples.pingpong.Main',
      dependencies=[
        pants(':pingpong-lib')
      ]
    )

This small program has just one `java_library`. The rule of thumb is that
each directory of `.java` or `.scala` files has a library target. If you find
yourself thinking "we should move some of this code to another directory,"
you probably also want to set up a `BUILD` file with a `java_library`
(or `scala_library`) target. ::

    java_library(name = 'pingpong-lib',
      dependencies = [
        pants('3rdparty:guice'),
        jar(org = 'com.sun.jersey', name = 'jersey-client',
            rev = 1.12).with_sources(),
        pants('src/java/com/twitter/common/application'),
        # ...many more dependencies...
      ],
      sources = globs('*.java'))

This library depends on other build targets and jars; if your code imports
something, that implies a `BUILD` dependency.
Some of the depended-upon targets come from the same repository; for example
`.../common/application`. If we peeked at that `BUILD` target, we'd see it was
another `java_library`.)
Some of these dependencies are `jar`\ s built elsewhere.

Depending on a Jar
------------------

The `pingpong-lib` example depends on some jars. Instead of compiling
from source, Pants invokes `ivy` to fetch these jars. A `jar` in a
dependencies list specifies the Maven repo from which to fetch. If several
things depend on the same jar, it's wrapped in a target.

Since the example `pingpong-lib` is the only thing in commons to depend on
jersey-client, that dependency is a `jar` in `pingpong-lib`'s `dependencies`
list::

    java_library(name = 'pingpong-lib',
      dependencies = [
        jar(org = 'com.sun.jersey', name = 'jersey-client',
            rev = 1.12).with_sources(),
        ...

If several things depend on the same jar, the usual pattern is to define a
`dependencies` target that depends on one (or, rarely, more) jars.
(In `twitter/commons`, most use the `jar_library` synonym for `dependencies`.)
`pingpong-lib` *could* depend on the Guice `jar` directly.
However, if several things did so and we then want to upgrade to Guice 4.0,
we would have to bump the `rev` number in several places or risk diamond
dependency problems.::

    jar_library(name = 'guice',
      dependencies = [
        jar(org = 'com.google.inject', name = 'guice', rev = '3.0',
            apidocs = 'http://google-guice.googlecode.com/svn/tags/3.0/javadoc/'
        ).with_sources()])

Java7 vs Java6, Which Java
--------------------------

Pants uses the java on your `PATH` (not `JAVA_HOME`).
To specify a specific java version for just one pants invocation::

    PATH=/usr/lib/jvm/java-1.7.0-openjdk7/bin:${PATH} ./pants goal ...

If you sometimes need to compile some code in Java 6 and sometimes Java 7,
you can use a command-line arg to specify Java version::

    --compile-javac-args='-target 7 -source 7'

*BUT* beware: if you switch between Java versions, Pants doesn't realize when
it needs to rebuild. If you build with version 7, change some code, then build
with version 6, java 6 will try to understand java 7-generated classfiles
and fail. Thus, if you've been building with one Java version and are switching
to another, you probably need to::

    ./pants goal clean-all

so that the next build starts from scratch.
