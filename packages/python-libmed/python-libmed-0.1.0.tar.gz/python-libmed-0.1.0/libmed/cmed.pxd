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
MED: Cython declarations for the MED library interface.
"""
cdef extern from "med.h":
    ctypedef int hid_t  # from H5Ipublic.h
    ctypedef int herr_t # from H5public.h
    ctypedef hid_t med_idt
    ctypedef herr_t med_err
    ctypedef int med_int
    ctypedef double med_float
    ctypedef int med_geometry_type
    cdef enum:
        MED_POINT1 = 001
        MED_SEG2 = 102
        MED_SEG3 = 103
        MED_SEG4 = 104
        MED_TRIA3 = 203
        MED_QUAD4 = 204
        MED_TRIA6 = 206
        MED_TRIA7 = 207
        MED_QUAD8 = 208
        MED_QUAD9 = 209
        MED_TETRA4 = 304
        MED_PYRA5 = 305
        MED_PENTA6 = 306
        MED_HEXA8 = 308
        MED_TETRA10 = 310
        MED_OCTA12 = 312
        MED_PYRA13 = 313
        MED_PENTA15 = 315
        MED_HEXA20 = 320
        MED_HEXA27 = 327
        MED_POLYGON = 400
        MED_POLYHEDRON = 500
        MED_STRUCT_GEO_INTERNAL = 600
        MED_STRUCT_GEO_SUP_INTERNAL = 700
        MED_ALL_GEOTYPE = -1
        MED_GEO_ALL = MED_ALL_GEOTYPE
    ctypedef enum med_bool:
        MED_FALSE
        MED_TRUE
    ctypedef enum med_access_mode:
        MED_ACC_RDONLY
        MED_ACC_RDWR
        MED_ACC_RDEXT
        MED_ACC_CREAT
        MED_ACC_UNDEF
    cdef enum:
        MED_COMMENT_SIZE = 200
    cdef enum:
        MED_NAME_SIZE = 64
    cdef enum:
        MED_SNAME_SIZE = 16
    ctypedef enum med_mesh_type:
        MED_UNSTRUCTURED_MESH
        MED_STRUCTURED_MESH
        MED_UNDEF_MESH_TYPE=-1
    ctypedef enum med_sorting_type:
        MED_SORT_DTIT
        MED_SORT_ITDT
        MED_SORT_UNDEF=-1
    ctypedef enum med_axis_type:
        MED_CARTESIAN
        MED_CYLINDRICAL
        MED_SPHERICAL
        MED_UNDEF_AXIS_TYPE=-1
    ctypedef enum med_switch_mode:
        MED_FULL_INTERLACE
        MED_NO_INTERLACE
        MED_UNDEF_INTERLACE=-1
    cdef enum:
        MED_NO_DT = -1
    cdef enum:
        MED_NO_IT = -1
    cdef enum:
        MED_NONE = 0
    cdef enum:
        MED_UNDEF_DT = 0
    cdef enum:
        MED_NO_GEOTYPE = MED_NONE
    cdef enum:
        MED_ALL_CONSTITUENT = 0
    ctypedef enum med_entity_type:
        MED_CELL
        MED_DESCENDING_FACE
        MED_DESCENDING_EDGE
        MED_NODE
        MED_NODE_ELEMENT
        MED_STRUCT_ELEMENT
        MED_ALL_ENTITY_TYPE
        MED_UNDEF_ENTITY_TYPE
    ctypedef enum med_data_type:
        MED_COORDINATE
        MED_CONNECTIVITY
        MED_NAME
        MED_NUMBER
        MED_FAMILY_NUMBER
        MED_COORDINATE_AXIS1
        MED_COORDINATE_AXIS2
        MED_COORDINATE_AXIS3
        MED_INDEX_FACE
        MED_INDEX_NODE
        MED_GLOBAL_NUMBER
        MED_VARIABLE_ATTRIBUTE
        MED_COORDINATE_TRSF
        MED_UNDEF_DATATYPE
    ctypedef enum med_connectivity_mode:
        MED_NODAL
        MED_DESCENDING
        MED_UNDEF_CONNECTIVITY_MODE
        MED_NO_CMODE
    ctypedef enum med_internal_type:
        MED_INTERNAL_FLOAT64 = 6
        MED_INTERNAL_INT32   = 24
        MED_INTERNAL_INT64   = 26
        MED_INTERNAL_INT     = 28
        MED_INTERNAL_NAME    = 30
        MED_INTERNAL_SNAME   = 32
        MED_INTERNAL_LNAME   = 34
        MED_INTERNAL_IDENT   = 38
        MED_INTERNAL_CHAR    = 40
        MED_INTERNAL_UNDEF   = 0
    ctypedef enum med_field_type:
        MED_FLOAT64 = MED_INTERNAL_FLOAT64
        MED_INT32   = MED_INTERNAL_INT32
        MED_INT64   = MED_INTERNAL_INT64
        MED_INT     = MED_INTERNAL_INT
    ctypedef med_field_type med_parameter_type
    ctypedef enum med_grid_type:
        MED_CARTESIAN_GRID
        MED_POLAR_GRID
        MED_CURVILINEAR_GRID
        MED_UNDEF_GRID_TYPE
    ctypedef enum med_storage_mode:
        MED_UNDEF_STMODE
        MED_GLOBAL_STMODE
        MED_COMPACT_STMODE
        MED_GLOBAL_PFLMODE = MED_GLOBAL_STMODE
        MED_COMPACT_PFLMODE = MED_COMPACT_STMODE
        MED_UNDEF_PFLMODE = MED_UNDEF_STMODE

    # file
    med_idt MEDfileOpen(char *, med_access_mode)
    med_idt MEDfileClose(med_idt)
    med_err MEDfileCommentRd(med_idt, char [MED_COMMENT_SIZE])
    med_err MEDfileCommentWr(med_idt, char *)
    med_err MEDfileNumVersionRd(med_idt, med_int *, med_int *, med_int *)
    med_err MEDlibraryNumVersion(med_int *, med_int *, med_int *)
    med_err MEDfileCompatibility(char *, med_bool *, med_bool *)

    # mesh
    med_err MEDmeshCr(med_idt, char *, med_int, med_int, med_mesh_type,
                      char *, char *, med_sorting_type, med_axis_type,
                      char *, char *)
    med_err MEDmeshNodeCoordinateWr(med_idt, char *, med_int, med_int,
                                    med_float, med_switch_mode, med_int,
                                    med_float *)
    med_err MEDmeshNodeCoordinateRd(med_idt, char *, med_int, med_int,
                                    med_switch_mode, med_float *)
    med_err MEDmeshInfo(med_idt, int, char *, med_int *, med_int *,
                        med_mesh_type *, char *, char *,
                        med_sorting_type *, med_int *,
                        med_axis_type *, char *, char *)
    med_err MEDmeshInfoByName(med_idt, char *, med_int *, med_int *,
                              med_mesh_type *, char *, char *,
                              med_sorting_type *, med_int *,
                              med_axis_type *, char *, char *)
    med_int MEDmeshnEntity(med_idt, char *, med_int, med_int,
                           med_entity_type, med_geometry_type,
                           med_data_type, med_connectivity_mode,
                           med_bool *, med_bool *)
    med_int MEDmeshnAxisByName(med_idt, char *)
    med_err MEDmeshElementConnectivityWr(med_idt, char *, med_int, med_int,
                                         med_float, med_entity_type,
                                         med_geometry_type,
                                         med_connectivity_mode,
                                         med_switch_mode, med_int,
                                         med_int *)
    med_err MEDmeshElementConnectivityRd(med_idt, char *, med_int, med_int,
                                         med_entity_type, med_geometry_type,
                                         med_connectivity_mode,
                                         med_switch_mode, med_int *)
    med_err MEDfamilyCr(med_idt, char *, char *, med_int, med_int, char *)
    med_int MEDnMesh(med_idt)
    med_err MEDmeshEntityInfo(med_idt, char *, med_int, med_int,
                              med_entity_type, int, char *,
                              med_geometry_type *)
    med_err MEDmeshGridTypeWr(med_idt, char *, med_grid_type)
    med_err MEDmeshGridIndexCoordinateWr(med_idt, char *, med_int, med_int,
                                         med_float, med_int, med_int,
                                         med_float *)
    med_err MEDmeshEntityNameWr(med_idt, char *, med_int, med_int,
                                med_entity_type, med_geometry_type,
                                med_int, char *)
    med_err MEDmeshGridTypeRd(med_idt, char *, med_grid_type *)
    med_err MEDmeshGridIndexCoordinateRd(med_idt, char *, med_int, med_int,
                                         med_int, med_float *)

    # field
    med_err MEDfieldCr(med_idt, char *, med_field_type, med_int, char *,
                       char *, char *, char *)
    med_err MEDfieldInfo(med_idt, int, char *, char *, med_bool *,
                         med_field_type *, char *, char *, char *,
                         med_int *)
    med_err MEDfieldInfoByName(med_idt, char *, char *, med_bool *,
                               med_field_type *, char *, char *, char *,
                               med_int *)
    med_err MEDfieldValueWr(med_idt, char *, med_int, med_int, med_float,
                            med_entity_type, med_geometry_type,
                            med_switch_mode, med_int, med_int, unsigned char *)
    med_err MEDfieldValueWithProfileWr(med_idt, char *, med_int, med_int,
                                       med_float, med_entity_type,
                                       med_geometry_type, med_storage_mode,
                                       char *, char *, med_switch_mode,
                                       med_int, med_int, unsigned char *)
    med_int MEDfieldnValue(med_idt, char *, med_int, med_int,
                           med_entity_type, med_geometry_type)
    med_err MEDfieldValueRd(med_idt, char *, med_int, med_int,
                            med_entity_type, med_geometry_type,
                            med_switch_mode, med_int, unsigned char *)
    med_int MEDfieldnComponent(med_idt, int)
    med_int MEDfieldnComponentByName(med_idt, char *)
    med_int MEDnField(med_idt)
    med_int MEDfieldnProfile(med_idt, char *, med_int, med_int,
                             med_entity_type, med_geometry_type,
                             char *, char *)
    med_int MEDfieldnValueWithProfile(med_idt, char *, med_int, med_int,
                                      med_entity_type, med_geometry_type, int,
                                      med_storage_mode, char *, med_int *,
                                      char *, med_int *)
    med_err MEDfieldValueWithProfileRd(med_idt, char *, med_int, med_int,
                                       med_entity_type, med_geometry_type,
                                       med_storage_mode, char *,
                                       med_switch_mode, med_int, unsigned char *)

    # parameters
    med_err MEDparameterCr(med_idt, char *, med_parameter_type, char *,
                           char *)
    med_err MEDparameterValueWr(med_idt, char *, med_int, med_int,
                                med_float, unsigned char *)
    med_err MEDparameterInfoByName(med_idt, char *, med_parameter_type *,
                                   char *, char *, med_int *)
    med_int MEDnParameter(med_idt)
    med_err MEDparameterInfo(med_idt, int, char *, med_parameter_type *,
                             char *, char *, med_int *)
    med_err MEDparameterValueRd(med_idt, char *, med_int, med_int,
                                unsigned char *)
    med_err MEDparameterComputationStepInfo(med_idt, char *, int,
                                            med_int *, med_int *,
                                            med_float *)

    # profiles
    med_int MEDnProfile(med_idt)
    med_err MEDprofileInfo(med_idt, int, char *, med_int *)
    med_err MEDprofileRd(med_idt, char *, med_int *)
    med_int MEDprofileSizeByName(med_idt, char *)
    med_err MEDprofileWr(med_idt, char *, med_int, med_int *)
