# Copyright 2013 The py-lmdb authors, all rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted only as authorized by the OpenLDAP
# Public License.
# 
# A copy of this license is available in the file LICENSE in the
# top-level directory of the distribution or, alternatively, at
# <http://www.OpenLDAP.org/license.html>.
# 
# OpenLDAP is a registered trademark of the OpenLDAP Foundation.
# 
# Individual files and/or contributed packages may be copyright by
# other parties and/or subject to additional restrictions.
# 
# This work also contains materials derived from public sources.
# 
# Additional information about OpenLDAP can be obtained at
# <http://www.openldap.org/>.

"""
cffi wrapper for OpenLDAP's "Lightning" MDB database.

Please see http://lmdb.readthedocs.org/
"""

import os
import sys

try:
    # Hack: disable speedups while testing or reading docstrings.
    if os.path.basename(sys.argv[0]) in ('sphinx-build', 'pydoc') or \
            os.getenv('LMDB_FORCE_CFFI') is not None:
        raise ImportError
    from lmdb.cpython import *
except ImportError:
    from lmdb.cffi import *
    from lmdb.cffi import __doc__

del os
__all__ = ['Environment', 'Cursor', 'Transaction', 'open', 'Error',
           'enable_drop_gil']
__version__ = '0.64'
