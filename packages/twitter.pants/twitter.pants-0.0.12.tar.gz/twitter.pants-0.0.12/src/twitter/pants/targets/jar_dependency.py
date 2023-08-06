# ==================================================================================================
# Copyright 2011 Twitter, Inc.
# --------------------------------------------------------------------------------------------------
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==================================================================================================

from twitter.pants.base import manual
from twitter.pants.targets.exclude import Exclude

from .external_dependency import ExternalDependency


class Artifact(object):
  """
  Specification for an Ivy Artifact for this jar dependency.

  See: http://ant.apache.org/ivy/history/latest-milestone/ivyfile/artifact.html
  """
  def __init__(self, name, type_=None, ext=None, conf=None, url=None, classifier=None):
    """
    :param name: The name of the published artifact. This name must not include revision.
    :param type_: The type of the published artifact. It's usually its extension, but not
      necessarily. For instance, ivy files are of type 'ivy' but have 'xml' extension.
    :param ext: The extension of the published artifact.
    :param conf: The public configuration in which this artifact is published. The '*' wildcard can
      be used to designate all public configurations.
    :param url: The url at which this artifact can be found if it isn't located at the standard
      location in the repository
    :param classifier: The maven classifier of this artifact.
    """
    self.name = name
    self.type_ = type_ or 'jar'
    self.ext = ext
    self.url = url
    self.classifier = classifier
    self.conf = conf

  def __repr__(self):
    return ('Artifact(%r, type_=%r, ext=%r, conf=%r, url=%r, classifier=%r)'
            % (self.name, self.type_, self.ext, self.conf, self.url, self.classifier))


@manual.builddict(tags=["jvm"])
class  JarDependency(ExternalDependency):
  """Represents a binary jar dependency ala maven or ivy.  For the ivy dependency defined by:
  ..

    <dependency org="com.google.guava" name="guava" rev="r07"/>

  The equivalent Dependency object could be created with:
    JarDependency(org = "com.google.guava", name = "guava", rev = "r07")

  If the rev keyword argument is left out, the revision is assumed to be the latest available.

  If the rev is specified and force = True is also specified, this will force the artifact revision
  to be rev even if other transitive deps specify a different revision for the same artifact.

  The extension of the artifact can be over-ridden if it differs from the artifact type with the ext
  keyword argument.  This is sometimes needed for artifacts packaged with maven bundle type but
  stored as jars.

  The url of the artifact can be over-ridden if non-standard by specifying the url keyword argument.

  If the dependency has API docs available online, these can be noted with apidocs and generated
  javadocs with {@link}s to the jar's classes will be properly hyperlinked.

  If the dependency is mutable this must be explicitly noted.  A common use-case is to inhibit
  caching of maven -SNAPSHOT style artifacts in an active development/integration cycle.

  If you want to use a maven classifier variant of a jar, use the classifier param. If you want
  to include multiple artifacts with differing classifiers, use with_artifact.
  """
  _JAR_HASH_KEYS = (
    'org',
    'name',
    'rev',
    'force',
    'excludes',
    'transitive',
    'ext',
    'url',
    'mutable',
    '_configurations'
  )

  def __init__(self, org, name, rev=None, force=False, ext=None, url=None, apidocs=None,
               type_=None, classifier=None, mutable=None):
    self.org = org
    self.name = name
    self.rev = rev
    self.force = force
    self.excludes = []
    self.transitive = True
    self.apidocs = apidocs
    self.mutable = mutable
    self._classifier = classifier

    self.artifacts = []
    if ext or url or type_ or classifier:
      self.with_artifact(name=name, type_=type_, ext=ext, url=url, classifier=classifier)

    self.id = repr(self)
    self._configurations = ['default']

    # Support legacy method names
    # TODO(John Sirois): introduce a deprecation cycle for these and then kill
    self.withSources = self.with_sources
    self.withDocs = self.with_sources

  @property
  def classifier(self):
    """Returns the maven classifier for this jar dependency.

    If the classifier is ambiguous; ie: there was no classifier set in the constructor and the jar
    dependency has multiple attached artifacts, a :class:`ValueError` is raised.
    """
    if self._classifier or len(self.artifacts) == 0:
      return self._classifier
    elif len(self.artifacts) == 1:
      return self.artifacts[0].classifier
    else:
      raise ValueError('Cannot determine classifier. No explicit classifier is set and this jar '
                       'has more than 1 artifact: %s\n\t%s'
                       % (self, '\n\t'.join(map(str, self.artifacts))))

  @manual.builddict()
  def exclude(self, org, name=None):
    """Adds a transitive dependency of this jar to the exclude list."""

    self.excludes.append(Exclude(org, name))
    return self

  @manual.builddict()
  def intransitive(self):
    """Declares this Dependency intransitive, indicating only the jar for the dependency itself
    should be downloaded and placed on the classpath"""

    self.transitive = False
    return self

  @manual.builddict()
  def with_sources(self):
    """This requests the artifact have its source jar fetched.
    (This implies there *is* a source jar to fetch.) Used in contexts
    that can use source jars (as of 2013, just eclipse and idea goals)."""
    self._configurations.append('sources')
    return self

  def with_docs(self):
    self._configurations.append('docs')
    return self

  def with_artifact(self, name=None, type_=None, ext=None, url=None, configuration=None,
                    classifier=None):
    """Sets an alternative artifact to fetch or adds additional artifacts if called multiple times.
    """
    artifact = Artifact(name or self.name, type_=type_, ext=ext, url=url, conf=configuration,
                        classifier=classifier)
    self.artifacts.append(artifact)
    return self

  def __eq__(self, other):
    result = (isinstance(other, JarDependency)
              and self.org == other.org
              and self.name == other.name
              and self.rev == other.rev)
    return result

  def __hash__(self):
    return hash((self.org, self.name, self.rev))

  def __ne__(self, other):
    return not self.__eq__(other)

  def __repr__(self):
    return "%s-%s-%s" % (self.org, self.name, self.rev)

  def cache_key(self):
    return ''.join(getattr(self, key) for key in self._JAR_HASH_KEYS)

  def resolve(self):
    yield self

  def walk(self, work, predicate=None):
    if not predicate or predicate(self):
      work(self)

  def _as_jar_dependencies(self):
    yield self
