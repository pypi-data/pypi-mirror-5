



#ifndef GTO_PY_H
#define GTO_PY_H

//#define BOOST_PYTHON_STATIC_LIB

#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

#include "gto.hpp"
#include "Matrixs_tmpl.hpp"
#include "PInt1e.hpp"

namespace Lotus_core {


void gto_def_boost_py(){
  using namespace boost::python;
  typedef PInt::PInt1e Integ1e;

  class_<Cgto_base>("Cgto_base",init<>())
    .def("set_atom_type",  &Cgto_base::set_atom_type)
    .def("set_atom_no",    &Cgto_base::set_atom_no)
    .def("set_R",          &Cgto_base::set_R)
    .def("set_nT_pbc",     &Cgto_base::set_nT_pbc)
    .def("set_gd",         &Cgto_base::set_gd)
    .def("set_new_d",      &Cgto_base::set_new_d)
    .def("get_num_pgto",   &Cgto_base::get_num_pgto)
    .def("get_atom_type",  &Cgto_base::get_atom_type)
    .def("get_atom_no",    &Cgto_base::get_atom_no)
    .def("get_nth_g",      &Cgto_base::get_nth_g)
    .def("get_nth_d",      &Cgto_base::get_nth_d)
    .def("get_g",          &Cgto_base::get_g)
    .def("get_d",          &Cgto_base::get_d)
    .def("get_R",          &Cgto_base::get_R)
    .def("get_nT_pbc",     &Cgto_base::get_nT_pbc_bp)
    .def("get_num",        &Cgto_base::get_num)
    .def("show",           &Cgto_base::show)
  ;
 
  class_<Cgto,bases<Cgto_base> >("Cgto",init<>())
    .def("set_n",                &Cgto::set_n)
    .def("set_gd",               &Cgto::set_gd)
    .def("get_nth_dI",           &Cgto::get_nth_dI)
    .def("get_total_n",          &Cgto::get_total_n)
    .def("cal_grid_value",       &Cgto::cal_grid_value)
    .def("cal_deri_grid_value",  &Cgto::cal_grid_value)
    .def("cal_deri2_grid_value", &Cgto::cal_grid_value)
    .def("show",                 &Cgto::show)
  ;
 
  class_<Shell_Cgto,bases<Cgto_base> >("Shell_Cgto",init<>())
    .def("set_shell_type",       &Shell_Cgto::set_shell_type)
    .def("set_min_cgto_no",      &Shell_Cgto::set_min_cgto_no)
    .def("get_shell_type",       &Shell_Cgto::get_shell_type)
    .def("get_max_tn",           &Shell_Cgto::get_max_tn)
    .def("get_num_cgto",         &Shell_Cgto::get_num_cgto)
    .def("get_min_cgto_no",      &Shell_Cgto::get_min_cgto_no)
    .def("get_max_cgto_no",      &Shell_Cgto::get_max_cgto_no)
    .def("set_dI",               &Shell_Cgto::set_dI<Integ1e>)
    .def("grid_value",           &Shell_Cgto::grid_value_bp<Integ1e>)
    .def("grid_deri_value",      &Shell_Cgto::grid_deri_value_bp<Integ1e>)
    .def("grid_deri2_value",     &Shell_Cgto::grid_deri2_value_bp<Integ1e>)
    .def("show",                 &Shell_Cgto::show)
    .def("get_cgtos",            &Shell_Cgto::get_cgtos<Integ1e>)
  ; 

  class_< std::vector<Cgto_base> >("vec_Cgto_base")
    .def(vector_indexing_suite< std::vector<Cgto_base> >() );

  class_< std::vector<Cgto> >("vec_Cgto")
    .def(vector_indexing_suite< std::vector<Cgto> >() );

  class_< std::vector<Shell_Cgto> >("vec_Shell_Cgto")
    .def(vector_indexing_suite< std::vector<Shell_Cgto> >() );


  class_<Util_GTO>("Util_GTO", init<>())
    .def("get_N_cgtos",          &Util_GTO::get_N_cgtos)                            .staticmethod("get_N_cgtos")
    .def("get_max_num_cgto",     &Util_GTO::get_max_num_cgto)                       .staticmethod("get_max_num_cgto")
    .def("get_N_scgtos_PBC",     &Util_GTO::get_N_scgtos_PBC)                       .staticmethod("get_N_scgtos_PBC")
    .def("get_scgtos",           &Util_GTO::get_scgtos)                             .staticmethod("get_scgtos")
    .def("get_cgtos",            &Util_GTO::get_cgtos<Integ1e>)                     .staticmethod("get_cgtos")
    .def("get_scgtos_PBC",       &Util_GTO::get_scgtos_PBC)                         .staticmethod("get_scgtos_PBC")
    .def("cal_cutoffM_base",     &Util_GTO::cal_cutoffM_base<dMatrix,    Integ1e>) 
    .def("cal_cutoffM_base",     &Util_GTO::cal_cutoffM_base<dMatrix_map,Integ1e>)  .staticmethod("cal_cutoffM_base")
    .def("get_N_atoms",          &Util_GTO::get_N_atoms<Cgto_base>)              
    .def("get_N_atoms",          &Util_GTO::get_N_atoms<Cgto>)                  
    .def("get_N_atoms",          &Util_GTO::get_N_atoms<Shell_Cgto>)                .staticmethod("get_N_atoms")
    .def("get_Rxyz",             &Util_GTO::get_Rxyz<Cgto_base>)                 
    .def("get_Rxyz",             &Util_GTO::get_Rxyz<Cgto>)                     
    .def("get_Rxyz",             &Util_GTO::get_Rxyz<Shell_Cgto>)                   .staticmethod("get_Rxyz")
    .def("cal_cutoffM",          &Util_GTO::cal_cutoffM<dMatrix,    Integ1e>)    
    .def("cal_cutoffM",          &Util_GTO::cal_cutoffM<dMatrix_map,Integ1e>)       .staticmethod("cal_cutoffM")
    .def("cal_cutoffM_PBC",      &Util_GTO::cal_cutoffM_PBC<dMatrix,    Integ1e>)
    .def("cal_cutoffM_PBC",      &Util_GTO::cal_cutoffM_PBC<dMatrix_map,Integ1e>)   .staticmethod("cal_cutoffM_PBC")
    .def("normalize_scgtos",     &Util_GTO::normalize_scgtos<Integ1e>)              .staticmethod("normalize_scgtos")
    .def("cal_s_shell",          &Util_GTO::cal_s_shell<Integ1e>)                   .staticmethod("cal_s_shell")
    .def("get_scgtos_from_string",  &Util_GTO::get_scgtos_from_string<Integ1e>)     .staticmethod("get_scgtos_from_string")
    .def("get_scgtos_from_file",    &Util_GTO::get_scgtos_from_file<Integ1e>)       .staticmethod("get_scgtos_from_file")
    .def("get_string_from_file",    &Util_GTO::get_string_from_file)                .staticmethod("get_string_from_file")
  ;
}



}   // end of namespace "Lotus_core"
#endif // end of include-guard
