



#ifndef DFT_FUNC_PY_H
#define DFT_FUNC_PY_H


#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

#include "DFT_func.hpp"
namespace Lotus_core {


void DFT_func_def_boost_py(){
  using namespace boost::python;

  class_<DFT_func>("DFT_func",init<>())
    .def("F_Screened_Slater1",    &DFT_func::F_Screened_Slater1)  .staticmethod("F_Screened_Slater1")
    .def("F_Screened_Slater3",    &DFT_func::F_Screened_Slater3)  .staticmethod("F_Screened_Slater3")

    .def("func_Slater",           &DFT_func::func_Slater)         .staticmethod("func_Slater")
    .def("func_USlater",          &DFT_func::func_USlater)        .staticmethod("func_USlater")

    .def("func_g_B88",            &DFT_func::func_g_B88)          .staticmethod("func_g_B88")
    .def("func_B88",              &DFT_func::func_B88)            .staticmethod("func_B88")
    .def("func_UB88",             &DFT_func::func_UB88)           .staticmethod("func_UB88")
    .def("func_g_B88_TDDFT",      &DFT_func::func_g_B88_TDDFT)    .staticmethod("func_g_B88_TDDFT")
    .def("func_B88_TDDFT",        &DFT_func::func_B88_TDDFT)      .staticmethod("func_B88_TDDFT")

    .def("func_PFA_VWN",          &DFT_func::func_PFA_VWN)        .staticmethod("func_PFA_VWN")
    .def("func_g_VWN",            &DFT_func::func_g_VWN)          .staticmethod("func_g_VWN")
    .def("func_h_VWN",            &DFT_func::func_h_VWN)          .staticmethod("func_h_VWN")
    .def("func_f_VWN",            &DFT_func::func_f_VWN)          .staticmethod("func_f_VWN")
    .def("func_VWN",              &DFT_func::func_VWN)            .staticmethod("func_VWN")
    .def("func_UVWN",             &DFT_func::func_UVWN)           .staticmethod("func_UVWN")
    .def("func_VWN_TDDFT",        &DFT_func::func_VWN_TDDFT)      .staticmethod("func_VWN_TDDFT")
  
    .def("func_LYP",              &DFT_func::func_LYP)            .staticmethod("func_LYP")
    .def("func_ULYP",             &DFT_func::func_ULYP)           .staticmethod("func_ULYP")
    .def("func_LYP_TDDFT",        &DFT_func::func_LYP_TDDFT)      .staticmethod("func_LYP_TDDFT")
  ;  

  


}


}   // end of namespace "Lotus_core"
#endif  // end of include-guard


