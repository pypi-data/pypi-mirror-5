
1.0.5
=====

  * In several dot-releases, have added support for Travis-CI 
    cloud-based continuous integration testing, Sphinx-based 
    documentation, and readthedocs.org hosted documentation.
    The Travis bit has required a separate Github repository
    be created. It is managed out of the same development
    directory, overlaying the existing Mercurial / Bitbucket
    repo. So far, that has caused no problems.

  * Documentation somewhat improved.


1.0
===

  * Cleaned up source for better PEP8 conformance
  * Bumped version number to 1.0 as part of move to `semantic 
    versioning <http://semver.org>`_, or at least enough of it so
    as to not screw up Python installation procedures (which don't
    seem to understand 0.401 is a lesser version that 0.5, because
    401 > 5).

