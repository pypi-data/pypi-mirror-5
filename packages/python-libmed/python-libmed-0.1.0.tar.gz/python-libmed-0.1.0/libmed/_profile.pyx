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
Cython bindings to the MED library for profiles handling.
"""
import cython as c
import numpy as np
cimport numpy as np
cimport cmed
from cmed cimport (MED_COMMENT_SIZE, med_int, med_float, MED_SNAME_SIZE,
                   med_parameter_type, MED_NAME_SIZE)
from _utils import (MEDError, sequence_time_convert)
import _medtypes
from base import MEDString

@c.locals(indices=np.ndarray)
def write_profile(medfileid, name, indices):
    indices = indices + 1 # MED 1-indexing
    ret = cmed.MEDprofileWr(medfileid, name, len(indices),
                            <med_int *>indices.data)
    if ret < 0:
        raise MEDError("Could not create profile %s." % name)

def read_number_of_profiles(medfileid, medfilename):
    ret = cmed.MEDnProfile(medfileid)
    if ret < 0:
        raise MEDError("Could not read the number of profiles in %s"
                       % medfilename)
    return ret

@c.locals(profile_size=med_int)
def read_info_from_index(medfileid, idx):
    profile_name = MEDString(MED_NAME_SIZE)
    ret = cmed.MEDprofileInfo(medfileid, idx + 1, profile_name,
                              c.address(profile_size))
    if ret < 0:
        raise MEDError("Could not read info for profile #%d." % idx)
    return str(profile_name), profile_size

def read_size_from_name(medfileid, name):
    ret = cmed.MEDprofileSizeByName(medfileid, name)
    if ret < 0:
        raise MEDError("Could not read size of profile %s" % name)
    return ret

def read_indices_from_name(medfileid, name, order='C'):
    psize = read_size_from_name(medfileid, name)
    entid = c.declare(np.ndarray,
                      np.zeros(psize, order=order,
                               dtype=np.int32)) # force int32
    ret = cmed.MEDprofileRd(medfileid, name, <med_int *>entid.data)
    if ret < 0:
        raise MEDError("Could not read values of profile %s." % name)
    return np.array(entid - 1, dtype=np.int) # force int, return to 0-indexing
