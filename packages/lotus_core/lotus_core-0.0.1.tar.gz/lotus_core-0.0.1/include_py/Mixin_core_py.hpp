


#ifndef MIXIN_CORE_PY_HPP
#define MIXIN_CORE_PY_HPP


#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

#include "Mixin_core.hpp"
#include "Matrixs_tmpl.hpp"
#include "Integ_py.hpp"



#define  MACRO_FOR_LOTUS_CORE_MIXIN(TYPE_NAME,MODULE_NAME)               \
  class_<TYPE_NAME>(MODULE_NAME,init<>())                                \
    .def("get_N_cgtos",          &TYPE_NAME::get_N_cgtos)                \
    .def("get_N_atoms",          &TYPE_NAME::get_N_atoms)                \
    .def("get_N_scgtos",         &TYPE_NAME::get_N_scgtos)               \
    .def("get_N_ecps",           &TYPE_NAME::get_N_ecps)                 \
    .def("get_Rxyz",             &TYPE_NAME::get_Rxyz)                   \
    .def("get_charges",          &TYPE_NAME::get_charges)                \
    .def("get_occ",              &TYPE_NAME::get_occ)                    \
    .def("get_occ_ab",           &TYPE_NAME::get_occ_ab)                 \
    .def("cal_matrix",           &TYPE_NAME::cal_matrix)                 \
    .def("prepare_eri",          &TYPE_NAME::prepare_eri<ERI_direct>)    \
    .def("prepare_eri",          &TYPE_NAME::prepare_eri<ERI_file>)      \
    .def("prepare_eri",          &TYPE_NAME::prepare_eri<ERI_incore>)    \
    .def("cal_Fock_sub",         &TYPE_NAME::cal_Fock_sub<ERI_direct>)   \
    .def("cal_Fock_sub",         &TYPE_NAME::cal_Fock_sub<ERI_file>)     \
    .def("cal_Fock_sub",         &TYPE_NAME::cal_Fock_sub<ERI_incore>)   \
    .def("cal_Fock_sub_u",       &TYPE_NAME::cal_Fock_sub_u<ERI_direct>) \
    .def("cal_Fock_sub_u",       &TYPE_NAME::cal_Fock_sub_u<ERI_file>)   \
    .def("cal_Fock_sub_u",       &TYPE_NAME::cal_Fock_sub_u<ERI_incore>) \
    .def("guess_h_core",         &TYPE_NAME::guess_h_core_bp1)           \
    .def("guess_h_core",         &TYPE_NAME::guess_h_core_bp2)           \
    .def("r_guess_h_core",       &TYPE_NAME::r_guess_h_core)             \
    .def("u_guess_h_core",       &TYPE_NAME::u_guess_h_core)             \
    .def("cal_force",            &TYPE_NAME::cal_force)                  \
    .def("cal_force_r",          &TYPE_NAME::cal_force_r)                \
    .def("cal_force_u",          &TYPE_NAME::cal_force_u)                \
    .def("cal_energy",           &TYPE_NAME::cal_energy)                 \
    .def("cal_energy_u",         &TYPE_NAME::cal_energy_u)               \
    .def("cal_show_energy",      &TYPE_NAME::cal_show_energy)            \
    .def("cal_show_energy_u",    &TYPE_NAME::cal_show_energy_u)          \
    .def("diis",                 &TYPE_NAME::diis)                       \
                                                                         \



namespace Lotus_core {


void Mixin_core_def_boost_py(){
  using namespace boost::python;

  typedef Lotus<dMatrix,    Integ1e,Integ2e> class_Lotus;
  typedef Lotus<dMatrix_map,Integ1e,Integ2e> class_Lotus_map;
  typedef Mixin_core< class_Lotus,    dMatrix,    Integ1e,Integ2e >  module_core;
  typedef Mixin_core< class_Lotus_map,dMatrix_map,Integ1e,Integ2e >  module_core_map;

  MACRO_FOR_LOTUS_CORE_MIXIN(module_core,    "Mixin_core");
  MACRO_FOR_LOTUS_CORE_MIXIN(module_core_map,"Mixin_core_map");

  class_<class_Lotus,bases<module_core> >("Lotus_core",init<>())
    .def_readwrite("scf_class",  &class_Lotus::scf_class)
    .def_readwrite("ene_total",  &class_Lotus::ene_total)
    .def_readwrite("moldata",    &class_Lotus::moldata)
    .def_readwrite("X_a",        &class_Lotus::X_a)
    .def_readwrite("X_b",        &class_Lotus::X_b)
    .def_readwrite("lamda_a",    &class_Lotus::lamda_a)
    .def_readwrite("lamda_b",    &class_Lotus::lamda_b)
  ;


  class_<class_Lotus_map,bases<module_core_map> >("Lotus_core_map",init<>())
    .def_readwrite("scf_class",  &class_Lotus_map::scf_class)
    .def_readwrite("ene_total",  &class_Lotus_map::ene_total)
    .def_readwrite("moldata",    &class_Lotus_map::moldata)
    .def_readwrite("X_a",        &class_Lotus_map::X_a)
    .def_readwrite("X_b",        &class_Lotus_map::X_b)
    .def_readwrite("lamda_a",    &class_Lotus_map::lamda_a)
    .def_readwrite("lamda_b",    &class_Lotus_map::lamda_b)
  ;


}


}   // end of namespace "Lotus_core"
#endif // include-guard


