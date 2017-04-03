from __future__ import unicode_literals
from waddleadmin.version_utils import get_version, get_stable_branch_name

# major.minor.patch.release.number
# release must be one of alpha, beta, rc, or final
VERSION = (0, 0, 0, 'a', 1)
__version__ = get_version(VERSION)
stable_branch_name = get_stable_branch_name(VERSION)
