


#ifndef GINTE_FUNCTOR_PY_H
#define GINTE_FUNCTOR_PY_H

//#define BOOST_PYTHON_STATIC_LIB




#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

#include "GInte_Functor.hpp"
namespace Lotus_core {


void GInte_Functor_def_boost_py(){
  using namespace boost::python;

  class_<GInte_Functor>("GInte_Functor",init<>())
    .def("get_use_potential_energy",     &GInte_Functor::get_use_potential_energy)
    .def("get_flag_gga",                 &GInte_Functor::get_flag_gga)
    .def("get_use_grid_inte",            &GInte_Functor::get_use_grid_inte)
    .def("get_hybrid_hf_x",              &GInte_Functor::get_hybrid_hf_x)
    .def("__call__",                     &GInte_Functor::op_bp1)            
    .def("__call__",                     &GInte_Functor::op_bp2)            
  ;

  class_< HF_Functor,bases<GInte_Functor> >("HF_Functor",init<>())
    .def("__call__",                     &HF_Functor::op_bp1)            
    .def("__call__",                     &HF_Functor::op_bp2)            
  ;

  class_< Slater_Functor,bases<GInte_Functor> >("Slater_Functor",init<>())
    .def("__call__",                     &Slater_Functor::op_bp1)            
    .def("__call__",                     &Slater_Functor::op_bp2)            
  ;

  class_< B88_Functor,bases<GInte_Functor> >("B88_Functor",init<>())
    .def("__call__",                     &B88_Functor::op_bp1)            
    .def("__call__",                     &B88_Functor::op_bp2)            
  ;

  class_< SVWN_Functor,bases<GInte_Functor> >("SVWN_Functor",init<>())
    .def("__call__",                     &SVWN_Functor::op_bp1)            
    .def("__call__",                     &SVWN_Functor::op_bp2)            
  ;

  class_< BLYP_Functor,bases<GInte_Functor> >("BLYP_Functor",init<>())
    .def("__call__",                     &BLYP_Functor::op_bp1)            
    .def("__call__",                     &BLYP_Functor::op_bp2)            
  ;

  class_< B3LYP_Functor,bases<GInte_Functor> >("B3LYP_Functor",init<>())
    .def(init< const std::vector<double> &>())
    .def("__call__",                     &B3LYP_Functor::op_bp1)            
    .def("__call__",                     &B3LYP_Functor::op_bp2)            
  ;

}


}   // end of namespace "Lotus_core"
#endif // include-guard

