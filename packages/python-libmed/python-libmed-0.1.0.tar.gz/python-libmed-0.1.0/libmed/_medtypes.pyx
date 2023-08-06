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
Type conversion utilities for MED.
"""
import numpy
from cmed cimport (MED_FULL_INTERLACE, MED_NO_INTERLACE,
                   MED_POINT1, MED_SEG2, MED_SEG3, MED_SEG4, MED_TRIA3,
                   MED_TRIA6, MED_TRIA7, MED_QUAD4, MED_QUAD8, MED_QUAD9,
                   MED_TETRA4, MED_TETRA10, MED_PYRA5, MED_PYRA13,
                   MED_PENTA6, MED_PENTA15, MED_OCTA12, MED_HEXA8,
                   MED_HEXA20, MED_HEXA27,
                   MED_FLOAT64, MED_INT32, MED_INT64,
                   MED_INTERNAL_FLOAT64, MED_INTERNAL_INT64,
                   MED_INTERNAL_INT32, MED_INTERNAL_INT, MED_INT, MED_TRUE,
                   MED_FALSE, MED_NODE, MED_CELL, MED_NONE,
                   MED_STRUCTURED_MESH, MED_UNSTRUCTURED_MESH,
                   MED_CARTESIAN_GRID, MED_POLAR_GRID,
                   MED_CURVILINEAR_GRID, MED_UNDEF_GRID_TYPE,
                   MED_COORDINATE, MED_COORDINATE_AXIS1,
                   MED_COORDINATE_AXIS2, MED_COORDINATE_AXIS3)

def type_converter(medtypes, typename):
    """
    Returns two functions: `from_medtype` and `to_medtype` which converts
    from and to MED types. `medtypes` is a dict which defines the
    correspondance between MED types and readable types, `typename` is a
    string describing the type of type to deal with.
    """
    def from_medtype(medtype):
        "Type conversion from MED types."
        try:
            return medtypes[medtype]
        except KeyError:
            raise ValueError("Unknown MED %s type %s." % (typename, medtype))

    def to_medtype(stype):
        "Type conversion to MED types."
        assert len(set(medtypes.values())) == len(medtypes.values())
        stypes = dict((v, k) for k, v in medtypes.iteritems())
        if isinstance(stype, numpy.dtype):
            # for numpy.dtype, use there name attribute since these cannot
            # be used as dict keys
            stype = stype.name
        try:
            return stypes[stype]
        except KeyError:
            try:
                return stypes[stype.lower()]
            except KeyError:
                raise ValueError("Cannot convert %s as a MED %s type." %
                                 (stype, typename))
            except:
                print stypes, stype

    return from_medtype, to_medtype

MEDGEOTYPE = {MED_NONE: 'node', # allows similar handling of nodes and elements
              MED_POINT1: 'pt1',
              MED_SEG2: 'seg2',
              MED_SEG3: 'seg3',
              MED_SEG4: 'seg4',
              MED_TRIA3: 'tria3',
              MED_TRIA6: 'tria6',
              MED_TRIA7: 'tria7',
              MED_QUAD4: 'quad4',
              MED_QUAD8: 'quad8',
              MED_QUAD9: 'quad9',
              MED_TETRA4: 'tet4',
              MED_TETRA10: 'tet10',
              MED_PYRA5: 'pyra5',
              MED_PYRA13: 'pyra13',
              MED_PENTA6: 'penta6',
              MED_PENTA15: 'penta15',
              MED_OCTA12: 'octa12',
              MED_HEXA8: 'hexa8',
              MED_HEXA20: 'hexa20',
              MED_HEXA27: 'hexa27'}
from_geotype, to_geotype = type_converter(MEDGEOTYPE, "geometry")

MEDSWITCHMODE = {MED_FULL_INTERLACE: 'C', MED_NO_INTERLACE: 'F'}
from_switchmode, to_switchmode = type_converter(MEDSWITCHMODE, "switch mode")

MEDDTYPE = {MED_INTERNAL_FLOAT64: 'float64',
            MED_INTERNAL_INT32: 'int32',
            MED_INTERNAL_INT64: 'int64',
            MED_INTERNAL_INT: 'int'}
from_dtype, to_dtype = type_converter(MEDDTYPE, "data type")

MEDBOOL = {MED_TRUE: True, MED_FALSE: False}
from_bool, to_bool = type_converter(MEDBOOL, "boolean")

MEDENTITYTYPE = {MED_NODE: 'node', MED_CELL: 'element'}
from_entitytype, to_entitytype = type_converter(MEDENTITYTYPE, "entity type")
def to_entity_and_geotype(entity):
    """
    Retrieve the med_entity_type and med_geometry_type from an string
    description of the entity.
    """
    if entity.lower() == 'node':
        enttype = to_entitytype('node')
    else:
        enttype = to_entitytype('element')
    geotype = to_geotype(entity)
    return enttype, geotype

MEDMESHTYPE = {MED_UNSTRUCTURED_MESH: 'unstructured',
               MED_STRUCTURED_MESH: 'structured'}
from_meshtype, to_meshtype = type_converter(MEDMESHTYPE, "mesh type")

MEDGRIDTYPE = {MED_CARTESIAN_GRID: "cartesian",
               MED_POLAR_GRID: "polar",
               MED_CURVILINEAR_GRID: "curvilinear",
               MED_UNDEF_GRID_TYPE: "undefined"}
from_gridtype, to_gridtype = type_converter(MEDGRIDTYPE, "grid type")

MEDAXIS = {MED_COORDINATE: None,
           MED_COORDINATE_AXIS1: 1,
           MED_COORDINATE_AXIS2: 2,
           MED_COORDINATE_AXIS3: 3}
from_axis, to_axis = type_converter(MEDAXIS, "axis")

