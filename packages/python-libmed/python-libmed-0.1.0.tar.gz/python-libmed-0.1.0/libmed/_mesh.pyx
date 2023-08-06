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
Cython bindings to the MED library for meshes handling.
"""
import cython as c
cimport numpy as np
import numpy as np
cimport cmed
from cmed cimport (MED_COMMENT_SIZE, med_int, med_float, med_bool,
                   MED_SORT_DTIT, MED_CARTESIAN,
                   MED_NAME_SIZE, MED_SNAME_SIZE,
                   med_mesh_type, med_sorting_type, med_axis_type,
                   MED_NODE, MED_NO_GEOTYPE, MED_COORDINATE, MED_NO_CMODE,
                   MED_CELL, MED_NODAL, MED_CONNECTIVITY,
                   med_geometry_type, MED_GEO_ALL, med_grid_type)
from _utils import (MEDError, MEDUnsupportedError, raveldata_switchmode,
                    sequence_time_convert)
import _medtypes
from base import MEDString

def create(medfileid, meshname, spacedim, meshdim, structured=False,
           desc=""):
    """ Create the mesh in the MED file """
    # sorting sequence
    sort_seq = MED_SORT_DTIT
    # cartesian frame
    axisnames = ' '.join(['x', 'y', 'z'][:spacedim])
    # metric units
    units = ['m'] * spacedim
    unitnames = ' '.join(units)
    dtunit = ""
    if len(meshname) > MED_NAME_SIZE:
        raise ValueError("mesh name exceeds %d." % MED_NAME_SIZE)
    if len(desc) > MED_COMMENT_SIZE:
        desc = desc[:MED_COMMENT_SIZE]
    if structured:
        meshtype = "structured"
    else:
        meshtype = "unstructured"
    ret = cmed.MEDmeshCr(medfileid, meshname, spacedim, meshdim,
                         _medtypes.to_meshtype(meshtype), desc, dtunit,
                         sort_seq, MED_CARTESIAN, axisnames, unitnames)
    if ret < 0:
        raise MEDError("Could not create mesh.")

def write_default_family(medfileid, meshname):
    # TODO use MED_NO_NAME and MED_NO_GROUP instead of ""
    ret = cmed.MEDfamilyCr(medfileid, meshname, "", 0, 0, "")
    if ret < 0:
        raise MEDError("Could define the default family for %s." %
                       meshname)

@c.locals(coords=np.ndarray)
def write_nodes_coord(medfileid, meshname, nodes, numdt=None, numit=None,
                      dt=None):
    numdt, numit, dt = sequence_time_convert(numdt, numit, dt)
    coords, switch_mode = raveldata_switchmode(np.asfarray(nodes))
    ret = cmed.MEDmeshNodeCoordinateWr(medfileid, meshname, numdt, numit,
                                       dt, switch_mode, nodes.shape[0],
                                       <med_float *>coords.data)
    if ret < 0:
        raise MEDError("Could not set nodes coordinates.")

def is_structured(medfileid, meshname):
    return read_info_from_name(medfileid, meshname)[2] == 'structured'

def write_grid_type(medfileid, meshname, grid_type):
    ret = cmed.MEDmeshGridTypeWr(medfileid, meshname,
                                 _medtypes.to_gridtype(grid_type))
    if ret < 0:
        raise MEDError("Could not set grid type for %s" % meshname)

@c.locals(gridindex=np.ndarray)
def write_grid_coord(medfileid, meshname, axis, gridindex, numdt=None,
                     numit=None, dt=None):
    numdt, numit, dt = sequence_time_convert(numdt, numit, dt)
    gridindex = np.asfarray(gridindex)
    ret = cmed.MEDmeshGridIndexCoordinateWr(medfileid, meshname, numdt,
                                            numit, dt, axis + 1,
                                            len(gridindex),
                                            <med_float *>gridindex.data)
    if ret < 0:
        raise MEDError("Could not set grid for axis %d in %s." %
                       (axis + 1, meshname))

@c.locals(grid_type=med_grid_type)
def read_grid_type(medfileid, meshname):
    ret = cmed.MEDmeshGridTypeRd(medfileid, meshname, c.address(grid_type))
    if ret < 0:
        raise MEDError("Could read grid type in %s." % meshname)
    return _medtypes.from_gridtype(grid_type)

@c.locals(spacedim=med_int, meshdim=med_int,
          meshtype=med_mesh_type,
          sort_seq=med_sorting_type, nstep=med_int,
          axistype=med_axis_type)
def read_info_from_name(medfileid, meshname):
    desc   = MEDString(MED_COMMENT_SIZE)
    dtunit = MEDString(MED_SNAME_SIZE)
    sdim = read_spacedim(medfileid, meshname)
    axisnames = MEDString(sdim * MED_SNAME_SIZE)
    axisunits = MEDString(sdim * MED_SNAME_SIZE)
    ret = cmed.MEDmeshInfoByName(medfileid, meshname,
                                 c.address(spacedim), c.address(meshdim),
                                 c.address(meshtype), desc, dtunit,
                                 c.address(sort_seq), c.address(nstep),
                                 c.address(axistype), axisnames,
                                 axisunits)
    if ret < 0:
        raise MEDError("Could not retrieve mesh info for %s." % meshname)
    axisnames, axisunits = map(str, (axisnames.split_every(MED_SNAME_SIZE),
                                     axisunits.split_every(MED_SNAME_SIZE)))
    return (spacedim, meshdim, _medtypes.from_meshtype(meshtype), str(desc),
            sort_seq, nstep, axistype, axisnames, axisunits, str(dtunit))

def read_number_of_meshes(fid):
    nmesh = cmed.MEDnMesh(fid)
    if nmesh < 0:
        raise MEDError("Could not retrieve the number of meshes", nmesh)
    return nmesh

@c.locals(spacedim=med_int, meshdim=med_int,
          meshtype=med_mesh_type,
          sort_seq=med_sorting_type, nstep=med_int,
          axistype=med_axis_type)
def read_info_from_index(fid, imesh):
    name     = MEDString(MED_NAME_SIZE)
    desc     = MEDString(MED_COMMENT_SIZE)
    dtunit   = MEDString(MED_SNAME_SIZE)
    axisnames = MEDString(3*MED_SNAME_SIZE)
    axisunits = MEDString(3*MED_SNAME_SIZE)
    ret = cmed.MEDmeshInfo(fid, imesh + 1, name,
                           c.address(spacedim), c.address(meshdim),
                           c.address(meshtype), desc, dtunit,
                           c.address(sort_seq), c.address(nstep),
                           c.address(axistype), axisnames,
                           axisunits)
    if ret < 0:
        raise MEDError("Could not retrieve information for mesh at %i" % imesh)
    axisnames, axisunits = map(str, (axisnames.split_every(MED_SNAME_SIZE),
                                     axisunits.split_every(MED_SNAME_SIZE)))
    return (str(name), spacedim, meshdim, _medtypes.from_meshtype(meshtype),
            str(desc), str(dtunit), sort_seq, nstep, axistype, axisnames,
                           axisunits)

def read_spacedim(medfileid, meshname):
    """ Returns the number of space dimension. """
    return cmed.MEDmeshnAxisByName(medfileid, meshname)

@c.locals(has_changed=med_bool, transformation=med_bool)
def read_number_of_nodes(medfileid, meshname, axis=None, numdt=None, numit=None):
    numdt, numit = sequence_time_convert(numdt, numit)
    coord = _medtypes.to_axis(axis)
    ret = cmed.MEDmeshnEntity(medfileid, meshname, numdt, numit, MED_NODE,
                              MED_NO_GEOTYPE, coord, MED_NO_CMODE,
                              c.address(has_changed),
                              c.address(transformation))
    if ret < 0:
        raise MEDError("Could not retrieve the number of nodes of "
                       "mesh: %s" % meshname)
    return ret

@c.locals(has_changed=med_bool, transformation=med_bool)
def read_number_of_elements(medfileid, meshname, elm_type=None, numdt=None,
                            numit=None):
    """ Reads the number of elements of type elm_type or total number of
    elements if elm_type is None """
    numdt, numit = sequence_time_convert(numdt, numit)
    if elm_type is None:
        geotype = MED_GEO_ALL
    else:
        geotype = _medtypes.to_geotype(elm_type)
    ret = cmed.MEDmeshnEntity(medfileid, meshname, numdt, numit, MED_CELL,
                              geotype, MED_CONNECTIVITY, MED_NODAL,
                              c.address(has_changed),
                              c.address(transformation))
    if ret < 0:
        raise MEDError("Could not retrieve the number of %s of "
                       "mesh: %s" % (elm_type, meshname))
    return ret

def read_nodes_coord(medfileid, meshname, numdt=None, numit=None,
                     order='C'):
    numdt, numit = sequence_time_convert(numdt, numit)
    meshdim = read_info_from_name(medfileid, meshname)[1]
    nnodes = read_number_of_nodes(medfileid, meshname)
    coords = c.declare(np.ndarray,
                       np.zeros((nnodes, meshdim), order=order,
                                dtype=np.float))
    ret = cmed.MEDmeshNodeCoordinateRd(medfileid, meshname,
                                       numdt, numit,
                                       _medtypes.to_switchmode(order),
                                       <med_float *>coords.data)
    if ret < 0:
        raise MEDError("Could not get nodes coordinates.")
    return coords

def read_grid_coord(medfileid, meshname, numdt=None, numit=None):
    numdt, numit = sequence_time_convert(numdt, numit)
    spacedim = read_spacedim(medfileid, meshname)
    # number of nodes by axis
    nnodes = [read_number_of_nodes(medfileid, meshname, axis=axis+1,
                                   numdt=numdt, numit=numit)
              for axis in range(spacedim)]
    grid_coords = []
    for axis in range(spacedim):
        cgrid = c.declare(np.ndarray, np.zeros(nnodes[axis], dtype=np.float))
        ret = cmed.MEDmeshGridIndexCoordinateRd(medfileid, meshname, numdt,
                                                numit, axis+1,
                                                <med_float *>cgrid.data)
        if ret < 0:
            raise MEDError("Could retrieve grid coordinates in axis %d" % axis)
        grid_coords.append(cgrid)
    return grid_coords

@c.locals(conns=np.ndarray)
def write_elements_connect(medfileid, meshname, etype, connects,
                           numdt=None, numit=None, dt=None):
    numdt, numit, dt = sequence_time_convert(numdt, numit, dt)
    conns, switch_mode = raveldata_switchmode(connects)
    conns = np.array(conns, dtype=np.int32) # force int32
    ret = cmed.MEDmeshElementConnectivityWr(medfileid, meshname, numdt,
                                            numit, dt, MED_CELL,
                                            _medtypes.to_geotype(etype),
                                            MED_NODAL, switch_mode,
                                            connects.shape[0],
                                            <med_int *>conns.data)
    if ret < 0:
        raise MEDError("Could not set connectivity for %s elements." %
                       etype)

@c.locals(geotype=med_geometry_type)
def read_entity_info_from_index(medfileid, meshname, enttype, ient,
                                numdt=None, numit=None):
    numdt, numit = sequence_time_convert(numdt, numit)
    geotypename = MEDString(MED_NAME_SIZE)
    ret = cmed.MEDmeshEntityInfo(medfileid, meshname,
                                 numdt, numit,
                                 _medtypes.to_entitytype(enttype), ient + 1,
                                 geotypename, c.address(geotype))
    if ret < 0:
        raise MEDError("Could not retrieve info for entity #%d in %s."
                       % (ient, meshname))
    return _medtypes.from_geotype(geotype), str(geotypename)

def read_elements_connect(medfileid, meshname, etype, nelm, nnodes,
                          numdt=None, numit=None, order='C'):
    numdt, numit = sequence_time_convert(numdt, numit)
    conns = c.declare(np.ndarray,
                      np.zeros((nelm, nnodes), order=order,
                               dtype=np.int32)) # force int32
    ret = cmed.MEDmeshElementConnectivityRd(medfileid, meshname, numdt,
                                            numit, MED_CELL,
                                            _medtypes.to_geotype(etype),
                                            MED_NODAL,
                                            _medtypes.to_switchmode(order),
                                            <med_int *>conns.data)
    if ret < 0:
        raise MEDError("Could not retrieve connectivity for %s "
                       "elements in %s." % (etype, meshname))
    return np.array(conns, dtype=np.int) # return regular int
