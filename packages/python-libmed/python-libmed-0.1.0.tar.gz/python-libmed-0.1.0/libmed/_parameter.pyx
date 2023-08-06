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
Cython bindings to the MED library for numerical parameters handling.
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

def create(medfileid, paramname, dtype, desc="", dtunit=""):
    if len(desc) > MED_COMMENT_SIZE:
        desc = desc[:MED_COMMENT_SIZE]
    if len(dtunit) > MED_SNAME_SIZE:
        desc = desc[:MED_SNAME_SIZE]
    ret = cmed.MEDparameterCr(medfileid, paramname,
                              _medtypes.to_dtype(dtype), desc, dtunit)
    if ret < 0:
        raise MEDError("Could not create parameter %s." % paramname)

@c.locals(vals=np.ndarray)
def write_value(medfileid, paramname, vals, numdt=None, numit=None, dt=None):
    numdt, numit, dt = sequence_time_convert(numdt, numit, dt)
    ret = cmed.MEDparameterValueWr(medfileid, paramname, numdt, numit, dt,
                                   <unsigned char *>vals.data)
    if ret < 0:
        raise MEDError("Could not set parameter value %s in %s." % paramname)

def read_number_of_parameters(fid):
    nparams = cmed.MEDnParameter(fid)
    if nparams < 0:
        raise MEDError("Could not retrieve the number of parameters", nparams)
    return nparams

@c.locals(dtype=med_parameter_type, nstep=med_int)
def read_info_from_index(fid, iparam):
    name   = MEDString(MED_NAME_SIZE)
    desc   = MEDString(MED_COMMENT_SIZE)
    dtunit = MEDString(MED_SNAME_SIZE)
    ret = cmed.MEDparameterInfo(fid, iparam + 1, name,
                                c.address(dtype), desc, dtunit,
                                c.address(nstep))
    if ret < 0:
        raise MEDError("Could not retrieve info for parameter at %i." % iparam)
    return str(name), dtype, str(desc), str(dtunit), nstep

@c.locals(dtype=med_parameter_type, nstep=med_int)
def read_info_from_name(medfileid, paramname):
    desc   = MEDString(MED_COMMENT_SIZE)
    dtunit = MEDString(MED_SNAME_SIZE)
    ret = cmed.MEDparameterInfoByName(medfileid, paramname,
                                      c.address(dtype), desc, dtunit,
                                      c.address(nstep))
    if ret < 0:
        raise MEDError("Could not retrieve info for parameter %s in %s."
                       % paramname)
    return (_medtypes.from_dtype(dtype), nstep, str(desc), str(dtunit))

@c.locals(numdt=med_int, numit=med_int, dt=med_float)
def read_value(medfileid, paramname, csit, dtype):
    ret = cmed.MEDparameterComputationStepInfo(medfileid,
                                               paramname, csit + 1,
                                               c.address(numdt),
                                               c.address(numit),
                                               c.address(dt))
    if ret < 0:
        raise MEDError("Could not retrieve computation info at step #%d "
                       "for parameter %s." % (csit - 1, paramname))
    val = c.declare(np.ndarray, np.zeros(1, dtype=dtype))
    ret = cmed.MEDparameterValueRd(medfileid, paramname, numdt, numit,
                                   <unsigned char *>val.data)
    if ret < 0:
        raise MEDError("Could not retrieve value of parameter %s." %
                       paramname)
    return numdt, numit, dt, val[0]
