


#ifndef ECP_TMPL_PY_H
#define ECP_TMPL_PY_H

//#define BOOST_PYTHON_STATIC_LIB




#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

#include "ECP_tmpl.hpp"
#include "Matrixs_tmpl.hpp"
#include "Integ_py.hpp"


namespace Lotus_core {


void ECP_def_boost_py(){
  using namespace boost::python;

   
  class_<ECP>("ECP",init<>())
    .def("show",                    &ECP::show)
    .def("set_L",                   &ECP::set_L)
    .def("set_atom_no",             &ECP::set_atom_no)
    .def("set_C",                   &ECP::set_C)
    .def("set_core_ele",            &ECP::set_core_ele)
    .def("clear_gkd",               &ECP::clear_gkd)
    .def("set_gkd",                 &ECP::set_gkd)
    .def("get_num_pc",              &ECP::get_num_pc)
    .def("get_L",                   &ECP::get_L)
    .def("get_atom_no",             &ECP::get_atom_no)
    .def("get_core_ele",            &ECP::get_core_ele)
    .def("get_C",                   &ECP::get_C)
    .def("get_nth_g",               &ECP::get_nth_g)
    .def("get_nth_k",               &ECP::get_nth_k)
    .def("get_nth_d",               &ECP::get_nth_d)
    .def("get_ecps_from_string",    &ECP::get_ecps_from_string)   .staticmethod("get_ecps_from_string")
    .def("get_ecps_from_file",      &ECP::get_ecps_from_file)     .staticmethod("get_ecps_from_file")
    .def("get_core_ele_from_ecps",  &ECP::get_core_ele_from_ecps) .staticmethod("get_core_ele_from_ecps")
  ;

  class_< std::vector<ECP> >("vec_ECP")
    .def(vector_indexing_suite< std::vector<ECP> >() );


  class_<RealSphericalHarmonic>("RealSphericalHarmonic",init<>())
    .def("get_keisu",               &RealSphericalHarmonic::get_keisu)
    .def("get_r",                   &RealSphericalHarmonic::get_r)
    .def("get_s",                   &RealSphericalHarmonic::get_s)
    .def("get_t",                   &RealSphericalHarmonic::get_t)
    .def("get_num",                 &RealSphericalHarmonic::get_num)
  ;

  class_< ECP_integral<Integ1e> >("ECP_integral",init<>())
    .def("set_primitives4_sub1",                   &ECP_integral<Integ1e>::set_primitives4_sub1)
    .def("set_primitives4_sub2",                   &ECP_integral<Integ1e>::set_primitives4_sub2)
    .def("get_Dabc",                               &ECP_integral<Integ1e>::get_Dabc)
    .def("cal_ECP_type1_integral_for_primitive3",  &ECP_integral<Integ1e>::cal_ECP_type1_integral_for_primitive3)
    .def("cal_ECP_type2_integral_for_primitive3",  &ECP_integral<Integ1e>::cal_ECP_type2_integral_for_primitive3)
    .def("cal_I",                                  &ECP_integral<Integ1e>::cal_I)
    .def("get_no_to_n",                            &ECP_integral<Integ1e>::get_no_to_n)
    .def("show",                                   &ECP_integral<Integ1e>::show)
  ;


  class_< ECP_matrix<dMatrix,Integ1e> >("ECP_matrix",init<>())
    .def("set_CUTOFF_ECP",                         &ECP_matrix<dMatrix,Integ1e>::set_CUTOFF_ECP)
    .def("cal_ECP",                                &ECP_matrix<dMatrix,Integ1e>::cal_ECP)
    .def("cal_ECP_PBC",                            &ECP_matrix<dMatrix,Integ1e>::cal_ECP_PBC)
    .def("cal_grad_ECP",                           &ECP_matrix<dMatrix,Integ1e>::cal_grad_ECP)
  ;

  class_< ECP_matrix<dMatrix_map,Integ1e> >("ECP_matrix_map",init<>())
    .def("set_CUTOFF_ECP",                         &ECP_matrix<dMatrix_map,Integ1e>::set_CUTOFF_ECP)
    .def("cal_ECP",                                &ECP_matrix<dMatrix_map,Integ1e>::cal_ECP)
    .def("cal_ECP_PBC",                            &ECP_matrix<dMatrix_map,Integ1e>::cal_ECP_PBC)
    .def("cal_grad_ECP",                           &ECP_matrix<dMatrix_map,Integ1e>::cal_grad_ECP)
  ;


}


}   // end of namespace "Lotus_core"
#endif  // end of include-guard



