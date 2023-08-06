




#ifndef Fock1e_TMPL_PY_H
#define Fock1e_TMPL_PY_H

//#define BOOST_PYTHON_STATIC_LIB




#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>


#include "Fock1e_tmpl.hpp"
#include "Matrixs_tmpl.hpp"
#include "Integ_py.hpp"


#define MACRO_FOR_LOTUS_CORE_FOCK1E(DMATRIX, MODULE_NAME)                                \
  class_< Fock1e_tmpl<DMATRIX,Integ1e> >(MODULE_NAME, init<>())                          \
    .def("show",              &Fock1e_tmpl<DMATRIX,Integ1e>::show)                       \
    .def("set_CUTOFF_Fock1e", &Fock1e_tmpl<DMATRIX,Integ1e>::set_CUTOFF_Fock1e)          \
    .def("cal_s_shell",       &Fock1e_tmpl<DMATRIX,Integ1e>::cal_s_shell)                \
    .def("cal_cutoffM",       &Fock1e_tmpl<DMATRIX,Integ1e>::cal_cutoffM)                \
    .def("cal_cutoffM_PBC",   &Fock1e_tmpl<DMATRIX,Integ1e>::cal_cutoffM_PBC)            \
    .def("cal_S",             &Fock1e_tmpl<DMATRIX,Integ1e>::cal_S)                      \
    .def("cal_S_PBC",         &Fock1e_tmpl<DMATRIX,Integ1e>::_cal_S_PBC_bp1)             \
    .def("cal_S_PBC",         &Fock1e_tmpl<DMATRIX,Integ1e>::_cal_S_PBC_bp2)             \
    .def("cal_K",             &Fock1e_tmpl<DMATRIX,Integ1e>::cal_K)                      \
    .def("cal_K_PBC",         &Fock1e_tmpl<DMATRIX,Integ1e>::_cal_K_PBC_bp1)             \
    .def("cal_K_PBC",         &Fock1e_tmpl<DMATRIX,Integ1e>::_cal_K_PBC_bp2)             \
    .def("cal_NA",            &Fock1e_tmpl<DMATRIX,Integ1e>::cal_NA)                     \
    .def("cal_NA_PBC",        &Fock1e_tmpl<DMATRIX,Integ1e>::_cal_NA_PBC_bp1)            \
    .def("cal_NA_PBC",        &Fock1e_tmpl<DMATRIX,Integ1e>::_cal_NA_PBC_bp2)            \
    .def("cal_NA_erfc",       &Fock1e_tmpl<DMATRIX,Integ1e>::cal_NA_erfc)                \
    .def("cal_NA_erfc_PBC",   &Fock1e_tmpl<DMATRIX,Integ1e>::_cal_NA_erfc_PBC_bp1)       \
    .def("cal_NA_erfc_PBC",   &Fock1e_tmpl<DMATRIX,Integ1e>::_cal_NA_erfc_PBC_bp2)       \
    .def("cal_NA_erf",        &Fock1e_tmpl<DMATRIX,Integ1e>::cal_NA_erf)                 \
    .def("cal_NA_erf_PBC",    &Fock1e_tmpl<DMATRIX,Integ1e>::_cal_NA_erf_PBC_bp1)        \
    .def("cal_NA_erf_PBC",    &Fock1e_tmpl<DMATRIX,Integ1e>::_cal_NA_erf_PBC_bp2)        \
    .def("cal_grad_S",        &Fock1e_tmpl<DMATRIX,Integ1e>::cal_grad_S)                 \
    .def("cal_grad_K",        &Fock1e_tmpl<DMATRIX,Integ1e>::cal_grad_K)                 \
    .def("cal_grad_NA",       &Fock1e_tmpl<DMATRIX,Integ1e>::cal_grad_NA)                \
    .def("cal_grad_NA_erfc",  &Fock1e_tmpl<DMATRIX,Integ1e>::cal_grad_NA_erfc)           \
    .def("cal_grad_NA_erf",   &Fock1e_tmpl<DMATRIX,Integ1e>::cal_grad_NA_erf)            \
                                                                                         \



namespace Lotus_core {


void Fock1e_def_boost_py(){
  using namespace boost::python;

  MACRO_FOR_LOTUS_CORE_FOCK1E(dMatrix,     "Fock1e");
  MACRO_FOR_LOTUS_CORE_FOCK1E(dMatrix_map, "Fock1e_map");

}



}   // end of namespace "Lotus_core"
#endif

