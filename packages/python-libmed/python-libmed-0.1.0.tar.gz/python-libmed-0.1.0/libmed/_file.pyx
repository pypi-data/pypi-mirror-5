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
Cython bindings to the MED library for file handling.
"""
import cython as c
cimport cmed
cimport numpy as np
import numpy as np
from _utils import MEDVersion, MEDError, MEDIOError, MEDVersionError
from cmed cimport (MED_COMMENT_SIZE, med_int, med_bool, MED_TRUE,
                   MED_NAME_SIZE, MED_SNAME_SIZE, med_mesh_type,
                   med_sorting_type, med_axis_type, med_field_type,
                   med_parameter_type)
from base import MEDString

def open(mode, path):
    mmode = {'r': cmed.MED_ACC_RDONLY,
             'w': cmed.MED_ACC_CREAT,
             'w+': cmed.MED_ACC_RDWR,
             'a': cmed.MED_ACC_RDEXT
             }.get(mode, 'r')
    fid = cmed.MEDfileOpen(path, mmode)
    if fid < 0:
        raise MEDIOError("Error opening MED file %s." % path)
    return fid

def close(fid):
    ier = cmed.MEDfileClose(fid)
    if ier < 0:
        raise MEDIOError("Error closing MED file", ier)

def read_comment(fid):
    # prefill the comment array with char termination symbol, strip
    # them on return
    comment = MEDString(MED_COMMENT_SIZE)
    ret = cmed.MEDfileCommentRd(fid, comment)
    if ret < 0:
        raise MEDError("Could not retrieve comment.", ret)
    return str(comment)

def write_comment(fid, comment):
    comment = MEDString(MED_COMMENT_SIZE, comment)
    ret = cmed.MEDfileCommentWr(fid, comment)
    if ret < 0:
        raise MEDError("Could not set comment.", ret)
    return comment

@c.locals(major=med_int, minor=med_int, release=med_int)
def read_version(fid):
    ret = cmed.MEDfileNumVersionRd(fid,
                                   c.address(major),
                                   c.address(minor),
                                   c.address(release))
    if ret < 0:
        raise MEDError("Could not retrieve MED version.", ret)
    return major, minor, release

@c.locals(hdfok=med_bool, medok=med_bool)
def read_compatibility(filepath):
    ret = cmed.MEDfileCompatibility(filepath,
                                    c.address(hdfok),
                                    c.address(medok))
    if ret < 0:
        raise MEDError("Could not check compatibility", ret)
    return hdfok == MED_TRUE, medok == MED_TRUE
