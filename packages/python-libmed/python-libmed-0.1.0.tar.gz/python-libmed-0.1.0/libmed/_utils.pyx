# Copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of python-libmed.
#
# python-libmed is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# python-libmed is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with python-libmed.  If not, see <http://www.gnu.org/licenses/>.

"""
MED: utilities and exceptions.
"""
import collections
import cython as c
import numpy as np
from cmed cimport (med_int, MED_NODE, MED_NONE, MED_CELL, MED_NO_DT, MED_NO_IT,
                   MED_UNDEF_DT, MED_NAME_SIZE, MED_SNAME_SIZE,
                   MED_COMMENT_SIZE)
cimport cmed
import _medtypes

__all__ = ['MEDError', 'MEDIOError', 'MEDVersionError', 'MEDUnsupportedError']
__all__.append('medlib_version')
__all__.extend(['NAME_SIZE', 'SNAME_SIZE', 'COMMENT_SIZE'])

NAME_SIZE = MED_NAME_SIZE
SNAME_SIZE = MED_SNAME_SIZE
COMMENT_SIZE = MED_COMMENT_SIZE

MEDVersion = collections.namedtuple('version_info',
                                    ['major', 'minor', 'release'])

class MEDError(Exception):
    """
    Based exception for MED library.

    :ivar ier: MED error return code
    """
    def __init__(self, msg, ier=None):
        if ier is not None:
            msg = "[%d] %s" % (ier, msg)
        super(MEDError, self).__init__(msg)
        self.ier = ier

class MEDIOError(IOError, MEDError):
    """MED file IO error."""

class MEDVersionError(AssertionError, MEDError):
    """MED file version error."""

class MEDUnsupportedError(NotImplementedError, MEDError):
    """Operation not supported in this library."""

def reverse_dict(d):
    return dict((v, k) for k, v in d.iteritems())

def truncate_name(name):
    return name[:MED_NAME_SIZE]

@c.locals(major=med_int, minor=med_int, release=med_int)
def medlib_version():
    ret = cmed.MEDlibraryNumVersion(c.address(major),
                                    c.address(minor),
                                    c.address(release))
    return MEDVersion(major, minor, release)

def raveldata_switchmode(data):
    order = {True: 'F', False: 'C'}[np.isfortran(data)]
    return np.ravel(data, order), _medtypes.to_switchmode(order)

def sequence_time_convert(*args):
    " Convert numdt, (numit, (dt)) into MED itetation types. "
    defaults = [MED_NO_DT, MED_NO_IT, MED_UNDEF_DT]
    return [a if a is not None else d for a, d in zip(args, defaults)]
