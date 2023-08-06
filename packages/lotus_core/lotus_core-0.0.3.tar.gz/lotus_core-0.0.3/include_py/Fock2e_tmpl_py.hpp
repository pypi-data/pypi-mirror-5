




#ifndef Fock2e_TMPL_PY_H
#define Fock2e_TMPL_PY_H



#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>


#include "Fock2e_tmpl.hpp"
#include "Matrixs_tmpl.hpp"
#include "Integ_py.hpp"

#define MACRO_FOR_LOTUS_CORE_FOCK2E(DMATRIX, MODULE_NAME)                                    \
  class_< Fock2e_tmpl<DMATRIX,Integ2e> >(MODULE_NAME, init<>())                              \
    .def("set_CUTOFF_Fock2e",            &Fock2e_tmpl<DMATRIX,Integ2e>::set_CUTOFF_Fock2e)   \
    .def("get_CUTOFF_Fock2e",            &Fock2e_tmpl<DMATRIX,Integ2e>::get_CUTOFF_Fock2e)   \
    .def("show",                         &Fock2e_tmpl<DMATRIX,Integ2e>::show)                \
    .def("prepare_eri",                  &Fock2e_tmpl<DMATRIX,Integ2e>::prepare_eri_bp1)     \
    .def("prepare_eri",                  &Fock2e_tmpl<DMATRIX,Integ2e>::prepare_eri_bp2)     \
    .def("prepare_eri",                  &Fock2e_tmpl<DMATRIX,Integ2e>::prepare_eri_bp3)     \
    .def("cal_Vh_and_Vx",                &Fock2e_tmpl<DMATRIX,Integ2e>::cal_Vh_and_Vx_bp1)   \
    .def("cal_Vh_and_Vx",                &Fock2e_tmpl<DMATRIX,Integ2e>::cal_Vh_and_Vx_bp2)   \
    .def("cal_Vh_and_Vx",                &Fock2e_tmpl<DMATRIX,Integ2e>::cal_Vh_and_Vx_bp3)   \
    .def("cal_Vh_and_Vx_u",              &Fock2e_tmpl<DMATRIX,Integ2e>::cal_Vh_and_Vx_u_bp1) \
    .def("cal_Vh_and_Vx_u",              &Fock2e_tmpl<DMATRIX,Integ2e>::cal_Vh_and_Vx_u_bp2) \
    .def("cal_Vh_and_Vx_u",              &Fock2e_tmpl<DMATRIX,Integ2e>::cal_Vh_and_Vx_u_bp3) \
    .def("cal_grad",                     &Fock2e_tmpl<DMATRIX,Integ2e>::cal_grad)            \
    .def("cal_grad_u",                   &Fock2e_tmpl<DMATRIX,Integ2e>::cal_grad_u)          \
                                                                                             \


namespace Lotus_core {


void Fock2e_def_boost_py(){
  using namespace boost::python;

  enum_< Fock2e_Enum::MODE >("Fock2e_Enum_MODE")
    .value("Normal",      Fock2e_Enum::Normal)
    .value("Erfc",        Fock2e_Enum::Erfc)
    .value("Erf",         Fock2e_Enum::Erf)
  ;
  enum_< Fock2e_Enum::MODE_U >("Fock2e_Enum_MODE_U")
    .value("Restricted",  Fock2e_Enum::Restricted)
    .value("Unestricted", Fock2e_Enum::Unrestricted)
  ;

  class_< ERI_direct >("ERI_direct",init<>())
    .def(init<Fock2e_Enum::MODE,double>())
    .def("get_mode",                     &ERI_direct::get_mode)
    .def("get_omega",                    &ERI_direct::get_omega)
    .def("show",                         &ERI_direct::show)
  ;


  class_< ERI_file >("ERI_file",init<>())
    .def(init<Fock2e_Enum::MODE,double>())
    .def("get_mode",                     &ERI_file::get_mode)
    .def("get_omega",                    &ERI_file::get_omega)
    .def("get_filename",                 &ERI_file::get_filename)
    .def("show",                         &ERI_file::show)
  ;


  class_< ERI_incore >("ERI_incore",init<>())
    .def(init<Fock2e_Enum::MODE,double>())
    .def("get_mode",                     &ERI_incore::get_mode)
    .def("get_omega",                    &ERI_incore::get_omega)
    .def("show",                         &ERI_incore::show)
  ;

  
  MACRO_FOR_LOTUS_CORE_FOCK2E(dMatrix,     "Fock2e");
  MACRO_FOR_LOTUS_CORE_FOCK2E(dMatrix_map, "Fock2e_map");


}



}   // end of namespace "Lotus_core"
#endif


