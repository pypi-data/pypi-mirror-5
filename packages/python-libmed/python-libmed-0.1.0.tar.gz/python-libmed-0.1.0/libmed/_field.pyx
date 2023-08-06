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
Cython bindings to the MED library for fields handling.
"""
import cython as c
cimport numpy as np
import numpy as np
cimport cmed
from cmed cimport (med_int, med_bool, MED_NAME_SIZE, MED_SNAME_SIZE,
                   med_field_type, MED_ALL_CONSTITUENT, MED_COMPACT_STMODE)
from _utils import (MEDError, raveldata_switchmode, sequence_time_convert)
import _medtypes
from base import MEDString

def create(medfileid, fieldname, meshname, ncomp, dtype, compnames,
           units, dtunit):
    if len(fieldname) > MED_NAME_SIZE:
        raise ValueError("field name exceeds %d." % MED_NAME_SIZE)
    compnames = ''.join([s.ljust(MED_SNAME_SIZE)[:MED_SNAME_SIZE]
                         for s in compnames])
    units = ''.join([s.ljust(MED_SNAME_SIZE)[:MED_SNAME_SIZE]
                     for s in units])
    ret = cmed.MEDfieldCr(medfileid, fieldname,
                          _medtypes.to_dtype(dtype), ncomp,
                          compnames, units, dtunit, meshname)

    if ret < 0:
        raise MEDError("Could not create field %s." % fieldname)

@c.locals(vals=np.ndarray)
def write_values(medfileid, fieldname, entity_type, values, numdt=None,
                 numit=None, dt=None):
    numdt, numit, dt = sequence_time_convert(numdt, numit, dt)
    enttype, geotype = _medtypes.to_entity_and_geotype(entity_type)
    nentities = values.shape[0]
    vals, switch_mode = raveldata_switchmode(values)
    # TODO check that this is consistent with the number of entities in
    #      the mesh
    ret = cmed.MEDfieldValueWr(medfileid, fieldname, numdt,
                               numit, dt, enttype, geotype,
                               switch_mode, MED_ALL_CONSTITUENT,
                               nentities, <unsigned char *>vals.data)
    if ret < 0:
        raise MEDError("Could not set values of type %s for field %s" %
                       (entity_type, fieldname))

@c.locals(vals=np.ndarray)
def write_values_with_profile(medfileid, fieldname, entity_type, values,
                              profilename, numdt=None, numit=None, dt=None):
    # assumes MED_COMPACT_STMODE, i.e. values contains only a subset of field
    # values corresponding to entities defined in the profile.
    numdt, numit, dt = sequence_time_convert(numdt, numit, dt)
    enttype, geotype = _medtypes.to_entity_and_geotype(entity_type)
    nentities = values.shape[0]
    vals, switch_mode = raveldata_switchmode(values)
    # TODO check that this is consistent with the number of entities in
    #      the mesh
    ret = cmed.MEDfieldValueWithProfileWr(medfileid, fieldname, numdt, numit,
                                          dt, enttype, geotype,
                                          MED_COMPACT_STMODE, profilename,
                                          "", switch_mode,
                                          MED_ALL_CONSTITUENT, nentities,
                                          <unsigned char *>vals.data)
    if ret < 0:
        raise MEDError("Could not set values of type %s for field %s" %
                       (entity_type, fieldname))

def read_number_of_fields(fid):
    nfields = cmed.MEDnField(fid)
    if nfields < 0:
        raise MEDError("Could not retrieve the number of fields", nfields)
    return nfields

@c.locals(nstep=med_int, localmesh=med_bool, field_type=med_field_type)
def read_info_from_index(fid, ifield):
    ncomp = read_number_of_components_by_index(fid, ifield + 1)
    name      = MEDString(MED_NAME_SIZE)
    meshname  = MEDString(MED_NAME_SIZE)
    compnames = MEDString(MED_SNAME_SIZE * ncomp)
    unitnames = MEDString(MED_SNAME_SIZE * ncomp)
    dtunit    = MEDString(MED_SNAME_SIZE)
    ret = cmed.MEDfieldInfo(fid, ifield + 1, name,
                            meshname, c.address(localmesh),
                            c.address(field_type), unitnames,
                            compnames, dtunit, c.address(nstep))
    if ret < 0:
        raise MEDError("Could not retrieve field info at %i." % ifield)
    cnames = map(str, compnames.split_every(MED_SNAME_SIZE))
    unames = map(str, unitnames.split_every(MED_SNAME_SIZE))
    name, meshname, dtunit = map(str, (name, meshname, dtunit))
    return (name, meshname, localmesh, field_type, cnames, unames, dtunit,
            nstep)

@c.locals(nstep=med_int, localmesh=med_bool, field_type=med_field_type)
def read_info_from_name(medfileid, fieldname):
    ncomp = read_number_of_components_by_name(medfileid, fieldname)
    meshname  = MEDString(MED_NAME_SIZE)
    compnames = MEDString(MED_SNAME_SIZE * ncomp)
    unitnames = MEDString(MED_SNAME_SIZE * ncomp)
    dtunit    = MEDString(MED_SNAME_SIZE)
    ret = cmed.MEDfieldInfoByName(medfileid, fieldname,
                                  meshname, c.address(localmesh),
                                  c.address(field_type),
                                  compnames, unitnames,
                                  dtunit, c.address(nstep))
    if ret < 0:
        raise MEDError("Could not retrieve field info for %s." % fieldname)
    cnames = map(str, compnames.split_every(MED_SNAME_SIZE))
    unames = map(str, unitnames.split_every(MED_SNAME_SIZE))
    return (str(meshname), cnames, unames, nstep,
            _medtypes.from_dtype(field_type), _medtypes.from_bool(localmesh),
            str(dtunit))

def read_number_of_values(medfileid, fieldname, entity_type, numdt=None,
                          numit=None):
    """ Retrieve the number of field values by entity type. """
    numdt, numit = sequence_time_convert(numdt, numit)
    enttype, geotype = _medtypes.to_entity_and_geotype(entity_type)
    ret = cmed.MEDfieldnValue(medfileid, fieldname, numdt, numit, enttype,
                              geotype)
    if ret < 0:
        raise MEDError("Could not retrieve the number of %s entities "
                       "in field %s." % (entity_type, fieldname))
    return ret

@c.locals(profsize=med_int, nb_integ_pts=med_int)
def read_number_of_values_with_profile(medfileid, fieldname, entity_type,
                                       profile_index, numdt=None, numit=None):
    numdt, numit = sequence_time_convert(numdt, numit)
    enttype, geotype = _medtypes.to_entity_and_geotype(entity_type)
    profname = MEDString(MED_NAME_SIZE)
    locname = MEDString(MED_NAME_SIZE)
    ret = cmed.MEDfieldnValueWithProfile(medfileid, fieldname, numdt, numit,
                                         enttype, geotype, profile_index,
                                         MED_COMPACT_STMODE, profname,
                                         c.address(profsize), locname,
                                         c.address(nb_integ_pts))
    if ret < 0:
        raise MEDError("Could not retrieve the number of %s entities "
                       "in field %s." % (entity_type, fieldname))
    return ret, str(profname), str(locname), profsize, nb_integ_pts

def read_number_of_components_by_index(medfileid, ifield):
    """ Retrieve the number of field components. """
    ret = cmed.MEDfieldnComponent(medfileid, ifield)
    if ret < 0:
        raise MEDError("Could not retrieve the number of components in "
                       "field #%d." % ifield)
    return ret

def read_number_of_components_by_name(medfileid, fieldname):
    """ Retrieve the number of field components. """
    ret = cmed.MEDfieldnComponentByName(medfileid, fieldname)
    if ret < 0:
        raise MEDError("Could not retrieve the number of components in "
                       "field %s." % fieldname)
    return ret

def read_values(medfileid, fieldname, etype, numdt=None, numit=None,
                dt=None, order='C'):
    ncomp = read_number_of_components_by_name(medfileid, fieldname)
    enttype, geotype = _medtypes.to_entity_and_geotype(etype)
    dtype = read_info_from_name(medfileid, fieldname)[4]
    nvals = read_number_of_values(medfileid, fieldname, etype, numdt=numdt,
                                  numit=numit)
    if nvals == 0: # no field value on this etype
        return None
    vals = c.declare(np.ndarray,
                     np.zeros((nvals, ncomp), order=order,
                              dtype=dtype))
    numdt, numit, dt = sequence_time_convert(numdt, numit, dt)
    ret = cmed.MEDfieldValueRd(medfileid, fieldname, numdt, numit, enttype,
                               geotype, _medtypes.to_switchmode(order),
                               MED_ALL_CONSTITUENT,
                               <unsigned char *>vals.data)
    if ret < 0:
        raise MEDError("Could not retrieve values of type %s in field %s."
                       % (etype, fieldname))
    return vals

def read_values_with_profile(medfileid, fieldname, etype, profile_index,
                             numdt=None, numit=None, dt=None, order='C'):
    ncomp = read_number_of_components_by_name(medfileid, fieldname)
    enttype, geotype = _medtypes.to_entity_and_geotype(etype)
    dtype = read_info_from_name(medfileid, fieldname)[4]
    nvals, profname, locname = read_number_of_values_with_profile(medfileid,
                                                                  fieldname,
                                                                  etype,
                                                                  profile_index,
                                                                  numdt=numdt,
                                                                  numit=numit)[:3]
    if nvals < 0:
        raise MEDError("Could not retrieve the number of values of type %s in "
                       "field %s." % (etype, fieldname))
    if nvals == 0: # no field value on this etype
        return None
    vals = c.declare(np.ndarray,
                     np.zeros((nvals, ncomp), order=order,
                              dtype=dtype))
    numdt, numit, dt = sequence_time_convert(numdt, numit, dt)
    ret = cmed.MEDfieldValueWithProfileRd(medfileid, fieldname, numdt, numit,
                                          enttype, geotype,
                                          MED_COMPACT_STMODE, profname,
                                          _medtypes.to_switchmode(order),
                                          MED_ALL_CONSTITUENT,
                                          <unsigned char *>vals.data)
    if ret < 0:
        raise MEDError("Could not retrieve values of type %s in field %s."
                       % (etype, fieldname))
    return vals

def read_number_of_profiles(medfileid, fieldname, etype, numdt=None,
                            numit=None, dt=None):
    defaultprofile      = MEDString(MED_NAME_SIZE)
    defaultlocalization = MEDString(MED_NAME_SIZE)
    numdt, numit, dt = sequence_time_convert(numdt, numit, dt)
    enttype, geotype = _medtypes.to_entity_and_geotype(etype)
    ret = cmed.MEDfieldnProfile(medfileid, fieldname, numdt, numit, enttype,
                                geotype, defaultprofile, defaultlocalization)
    if ret < 0:
        raise MEDError("Could not read the number of profiles in field %s"
                       % fieldname)
    return ret, str(defaultprofile), str(defaultlocalization)
