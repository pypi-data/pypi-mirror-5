



#ifndef PINT1E_PY_H
#define PINT1E_PY_H

#define BOOST_PYTHON_STATIC_LIB




#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>


#include "PInt1e.hpp"
namespace PInt {

BOOST_PYTHON_MODULE(PInt1e){
  using namespace boost::python;

  class_< PInt1e >("PInt1e",init<>())
    .def("show_state",              &PInt1e::show_state)
    .def("get_num",                 &PInt1e::get_num)      .staticmethod("get_num")
    .def("cal_I",                   &PInt1e::cal_I)        .staticmethod("cal_I")
//    .def("get_no_to_n",             &PInt1e::get_no_to_n)  .staticmethod("get_no_to_n")
    .def("get_n_to_no",             &PInt1e::get_n_to_no)  .staticmethod("get_n_to_no")
    .def("get_nc",                  &PInt1e::get_nc)       .staticmethod("get_nc")
    .def("cal_dI",                  &PInt1e::cal_dI)
    .def("set_gR_12",               (void(PInt1e::*)(double,const std::vector<double>&,double,const std::vector<double>&))&PInt1e::set_gR_12)
    // overlap
    .def("overlap_simple",          &PInt1e::overlap_simple)
//    .def("overlap",                 &PInt1e::overlap)
    // kinetic
    .def("kinetic_simple",          &PInt1e::kinetic_simple) 
//    .def("kinetic",                 &PInt1e::kinetic)
    // nuclear
    .def("set_gR_12",               (void(PInt1e::*)(double,const std::vector<double>&,double,const std::vector<double>&,int,const std::vector<double>&))&PInt1e::set_gR_12)
    .def("set_gR_12_erfc",          (void(PInt1e::*)(double,const std::vector<double>&,double,const std::vector<double>&,int,const std::vector<double>&,double))&PInt1e::set_gR_12_erfc)
    .def("set_gR_12_erf",           (void(PInt1e::*)(double,const std::vector<double>&,double,const std::vector<double>&,int,const std::vector<double>&,double))&PInt1e::set_gR_12_erf)
    .def("nuclear_simple",          &PInt1e::nuclear_simple) 
//    .def("nuclear",                 &PInt1e::nuclear)
    .def("nuclear_c_simple",        &PInt1e::nuclear_c_simple) 
//    .def("nuclear_c",               &PInt1e::nuclear_c)
    // momentum integral
    .def("mi_simple",               &PInt1e::mi_simple)
    // debug_driver
    .def("debug_driver_overlap",    &DEBUG_PInt1e::debug_driver_overlap)  .staticmethod("debug_driver_overlap")
    .def("debug_driver_kinetic",    &DEBUG_PInt1e::debug_driver_overlap)  .staticmethod("debug_driver_kinetic")
    .def("debug_driver_nuclear",    &DEBUG_PInt1e::debug_driver_overlap)  .staticmethod("debug_driver_nuclear")
    .def("debug_driver_nuclear_c",  &DEBUG_PInt1e::debug_driver_overlap)  .staticmethod("debug_driver_nuclear_c")
  ;
}


}  // end of namespace "PInt"

#endif  // end of include-guard
