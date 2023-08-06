

#ifndef GRID_INTE_PY_H
#define GRID_INTE_PY_H


#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

#include "Grid_Inte.hpp"
#include "Matrixs_tmpl.hpp"
#include "Integ_py.hpp"


#define MACRO_FOR_LOTUS_CORE_GRID_INTE(DMATRIX, MODULE_NAME)                            \
  class_< Grid_Inte<DMATRIX,Integ1e> >(MODULE_NAME, init<>())                           \
    .def("set_clear",              &Grid_Inte<DMATRIX,Integ1e>::set_clear)              \
    .def("grid_integral_mat_u",    &Grid_Inte<DMATRIX,Integ1e>::grid_integral_mat)      \
    .def("grid_integral_mat",      &Grid_Inte<DMATRIX,Integ1e>::grid_integral_mat_u)    \
    .def("grid_integral_mat_PBC",  &Grid_Inte<DMATRIX,Integ1e>::grid_integral_mat_PBC)  \
    .def("cal_grad_u",             &Grid_Inte<DMATRIX,Integ1e>::cal_grad_u)             \
    .def("cal_grad",               &Grid_Inte<DMATRIX,Integ1e>::cal_grad)               \
                                                                                        \


namespace Lotus_core {


void Grid_Inte_def_boost_py(){
  using namespace boost::python;

  MACRO_FOR_LOTUS_CORE_GRID_INTE(dMatrix,     "Grid_Inte");
  MACRO_FOR_LOTUS_CORE_GRID_INTE(dMatrix_map, "Grid_Inte_map");

/*
  class_< Grid_Inte<dMatrix,Integ1e> >("Grid_Inte", init<>())
    .def("set_clear",              &Grid_Inte<dMatrix,Integ1e>::set_clear)
    .def("grid_integral_mat_u",    &Grid_Inte<dMatrix,Integ1e>::grid_integral_mat)
    .def("grid_integral_mat",      &Grid_Inte<dMatrix,Integ1e>::grid_integral_mat_u)
    .def("grid_integral_mat_PBC",  &Grid_Inte<dMatrix,Integ1e>::grid_integral_mat_PBC)
    .def("cal_grad_u",             &Grid_Inte<dMatrix,Integ1e>::cal_grad_u)
    .def("cal_grad",               &Grid_Inte<dMatrix,Integ1e>::cal_grad)
  ;
*/


}




}   // end of namespace "Lotus_core"
#endif  // end of include-guard


