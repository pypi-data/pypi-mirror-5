#######################
JVM Projects with Pants
#######################

Assuming you know the :doc:`basic Pants concepts <first_concepts>` and have
gone through the :doc:`first_tutorial`, you've made a great start towards
using Pants to work with Java and Scala code. This page goes into some of
the details.

**************************
Relevant Goals and Targets
**************************

When working with JVM languages, the following goals and targets are
especially relevant.

**Deployable Binary** *Runnable Binary with non-JVM files*

  A ``jvm_app`` target specifies a runnable binary with its "helper" files
  (e.g.: start scripts, config files). Each ``jvm_app`` target needs a
  ``jvm_binary`` that describes the runnable Java code, and ``bundles``
  which describe the extra files to include.
  To build a zip containing the executable and resources, set up
  to be run, use the ``bundle`` goal;
  to run the app "in place" in your source tree, use the ``run`` goal.

**Runnable Binary**

  On its own, a ``jvm_binary`` BUILD target describes an executable ``.jar``
  (something you can run with ``java -jar``). The jar is described as
  executable because it contains a manifest file that specifies the main
  class as well as classpath for all dependencies. If your program
  contains only jars (and resources packaged in those jars), this is
  all you need to run the binary. Use ``./pants goal binary`` to
  compile its code; ``./pants goal run`` to run it "in place".

**Importable Code**

  ``java_library`` BUILD targets make Java source code ``import``\able. The
  rule of thumb is that each directory of ``.java`` files has a ``BUILD`` file
  with a ``java_library`` target. A JVM target that has a ``java_library`` in
  its ``dependencies`` can import its code. ``scala_library`` targets are
  similar, but compiled with Scala.

  To use pre-built ``.jar``\s, a JVM target can depend on a ``jar``, a
  reference to published code; these ``jar``\s normally live in a
  :doc:`directory called 3rdparty <3rdparty>`.

  Pants can ``publish`` a JVM library so code in other repos can use it;
  if the ``*_library`` target has a ``provides`` parameter, that specifies
  the repo/address at which to publish.

  An ``annotation_processor`` BUILD target defines a Java library
  one containing one or more annotation processors.

**Tests**

  A ``junit_tests`` BUILD target holds source code for some JUnit tests;
  typically, it would have one or more ``java_library`` targets as dependencies
  and would import and test their code.

  A ``scala_specs`` target is similar, but has source code for Scala specs.

  The Pants ``test`` goal runs tests.

**Generated Code**

  A ``java_thrift_library`` generates Java code from ``.thrift`` source; a JVM
  target that has this target in its ``dependencies`` can ``import`` the
  generated Java code. A ``java_protobuf_library`` is similar, but generates
  Java code from protobuffer source.

*************************
BUILD for a Simple Binary
*************************

The `Twitter Commons Java pingpong sample
<https://github.com/twitter/commons/tree/master/src/java/com/twitter/common/examples/pingpong>`_
code shows the BUILD file for a simple Java binary:

.. literalinclude:: ../../../../java/com/twitter/common/examples/pingpong/BUILD
   :start-after: jvm_binary:

This small program has just one `java_library`. The rule of thumb is that
each directory of ``.java`` or ``.scala`` files has a library target. If you
find
yourself thinking "we should move some of this code to another directory,"
you probably also want to set up a ``BUILD` file with a ``java_library``
(or ``scala_library``) target.

.. literalinclude:: ../../../../java/com/twitter/common/examples/pingpong/BUILD
   :start-after: java_library:
   :end-before: jvm_binary:

This library depends on other build targets and jars; if your code imports
something, that implies a ``BUILD`` dependency.
Some of the depended-upon targets come from the same repository; for example
``.../common/application``. If we peeked at that ``BUILD`` target, we'd see it
was another ``java_library``.)
Some of these dependencies are ``jar``\ s built elsewhere.

Depending on a Jar
==================

.. TODO in theory, our 3rdparty jvm deps all live under 3rdparty/jvm/ . In
   practice, none of pingpong-lib's deps live there.

The `pingpong-lib` example depends on some jars. Instead of compiling
from source, Pants invokes `ivy` to fetch these jars. To reduce danger
of version conflicts, we use the :doc:`3rdparty` idiom: we keep references
to these "third-party" jars together in ``BUILD`` files under the
``3rdparty/jvm/`` directory. Thus, ``pingpong-lib`` has a dependency::

    java_library(name = 'pingpong-lib',
      dependencies = [
        pants('3rdparty:guava'),
        ...

And ``3rdparty/BUILD`` has a target named ``guava``::

    dependencies(name='guava',
            dependencies = [
              jar(
                org='com.google.guava', name='guava', rev='14.0.1',
                apidocs = 'http://docs.guava-libraries.googlecode.com/git-history/v14.0.1/javadoc/'
              ).with_sources(),

              # Defined in provided scope so we provide here.
              pants(':jsr305'),
              jar(org='javax.inject', name='javax.inject', rev='1').with_sources(),
            ]
           )

Those :ref:`jar() things <bdict_jar>` are references to public jars.

*********
Toolchain
*********

Pants uses `Ivy <http://ant.apache.org/ivy/>`_ to resolve ``jar`` dependencies.
To change how Pants resolves these, use ``--ivy-*`` command-line
parameters along with ``--resolve-*`` parameters.

Pants uses `Nailgun <https://github.com/martylamb/nailgun>`_ to speed up
compiles. It's a JVM daemon that runs in the background; this saves time
for JVM startup and class loading.

.. TODO this is a good place to mention goal ng-killall, but I don't want**
   folks doing it willy-nilly. Would be good to prefix the mention with**
   something saying symptoms when you'd want to.

Pants uses Jmake, a dependency tracking compiler facade.

**************************
Java7 vs Java6, Which Java
**************************

Pants uses the java on your ``PATH`` (not ``JAVA_HOME``).
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
