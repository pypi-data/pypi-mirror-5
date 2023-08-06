





#ifndef Util_PBC_PY_H
#define Util_PBC_PY_H

#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>


#include "Util_PBC.hpp"
#include "Matrixs_tmpl.hpp"
namespace Lotus_core {

void Util_PBC_def_boost_py(){
  using namespace boost::python;

  class_<Util_PBC>("Util_PBC",init<>())
    .def("cal_n_from_q",     &Util_PBC::cal_n_from_q_bp)                       .staticmethod("cal_n_from_q")
    .def("cal_q",            &Util_PBC::cal_q_bp)                              .staticmethod("cal_q")
    .def("check_range",      &Util_PBC::check_range)                           .staticmethod("check_range")
    .def("check_range2",     &Util_PBC::check_range2)                          .staticmethod("check_range2")
    .def("get_zero_q",       &Util_PBC::get_zero_q)                            .staticmethod("get_zero_q")
    .def("cal_DV",           &Util_PBC::cal_DV_bp1<dMatrix,dMatrix>)          
    .def("cal_DV",           &Util_PBC::cal_DV_bp2<dMatrix,dMatrix>)         
    .def("cal_DV",           &Util_PBC::cal_DV_bp1<dMatrix_map,dMatrix_map>) 
    .def("cal_DV",           &Util_PBC::cal_DV_bp2<dMatrix_map,dMatrix_map>)   .staticmethod("cal_DV")
    .def("get_T_matrix",     &Util_PBC::get_T_matrix<dMatrix>)              
    .def("get_T_matrix",     &Util_PBC::get_T_matrix<dMatrix_map>)             .staticmethod("get_T_matrix")
    .def("cal_volume",       &Util_PBC::cal_volume_bp1)                    
    .def("cal_volume",       &Util_PBC::cal_volume_bp2)                        .staticmethod("cal_volume")
    .def("cal_reciprocal_lattice_vector",  &Util_PBC::cal_reciprocal_lattice_vector)  .staticmethod("cal_reciprocal_lattice_vector")
    .def("get_kxyz_from_k_lc",             &Util_PBC::get_kxyz_from_k_lc)             .staticmethod("get_kxyz_from_k_lc")
    .def("get_k_lc_from_kxyz",             &Util_PBC::get_k_lc_from_kxyz<dMatrix>)    .staticmethod("get_k_lc_from_kxyz")
    .def("cal_zincblende_a",               &Util_PBC::cal_zincblende_a)               .staticmethod("cal_zincblende_a") 
    .def("cal_graphite_a",                 &Util_PBC::cal_graphite_a)                 .staticmethod("cal_graphite_a") 
  ;

  class_<CTRL_PBC>("CTRL_PBC",init<>())
    .def("show",                          &CTRL_PBC::show)
    .def("set_T123",                      &CTRL_PBC::set_T123)
    .def("set_max_Nc",                    &CTRL_PBC::set_max_Nc)
    .def("set_max_Nt",                    &CTRL_PBC::set_max_Nt)
    .def("set_max_Nc_and_Nt",             &CTRL_PBC::set_max_Nc_and_Nt)
    .def("set_beta_Gaussian_broad",       &CTRL_PBC::set_beta_Gaussian_broad)
    .def("get_beta_Gaussian_broad",       &CTRL_PBC::get_beta_Gaussian_broad)
    .def("get_T123",                      &CTRL_PBC::get_T123)
    .def("get_max_Nc",                    &CTRL_PBC::get_max_Nc_bp)
    .def("get_max_Nt",                    &CTRL_PBC::get_max_Nt_bp)
    .def("get_N123_c",                    &CTRL_PBC::get_N123_c)
    .def("get_N123_t",                    &CTRL_PBC::get_N123_t)
    .def("get_zero_qc",                   &CTRL_PBC::get_zero_qc)
    .def("get_zero_qt",                   &CTRL_PBC::get_zero_qt)
    .def("get_nc_from_q",                 &CTRL_PBC::get_nc_from_q)
    .def("get_nt_from_q",                 &CTRL_PBC::get_nt_from_q)
    .def("get_R_pbc",                     &CTRL_PBC::get_R_pbc)
    .def("set_Nk123",                     &CTRL_PBC::set_Nk123)
    .def("get_Nk123",                     &CTRL_PBC::get_Nk123)
    .def("get_dk",                        &CTRL_PBC::get_dk)
    .def("get_nth_dk",                    &CTRL_PBC::get_nth_dk)
    .def("get_k_lc",                      &CTRL_PBC::get_k_lc)
    .def("get_nth_k_lc",                  &CTRL_PBC::get_nth_k_lc)
    .def("cal_volume",                    &CTRL_PBC::cal_volume)
    .def("get_reciprocal_lattic_vector",  &CTRL_PBC::get_reciprocal_lattice_vector)
    .def("get_kxyz_from_k_lc",            &CTRL_PBC::get_kxyz_from_k_lc)
    .def("get_k_lc_from_kxyz",            &CTRL_PBC::get_k_lc_from_kxyz<dMatrix>)
    .def("cal_zincblende_a",              &CTRL_PBC::cal_zincblende_a)
    .def("cal_graphite_a",                &CTRL_PBC::cal_graphite_a)
    .def("cal_1D_lattice_constant",       &CTRL_PBC::cal_1D_lattice_constant)
  ;

}


}   // end of namespace "Lotus_core"
#endif //include-guard

