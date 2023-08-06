


#ifndef GRADIENT_PY_H
#define GRADIENT_PY_H

//#define BOOST_PYTHON_STATIC_LIB




#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>


#include "Gradient.hpp"
#include "Matrixs_tmpl.hpp"
#include "Integ_py.hpp"



namespace Lotus_core {



void Gradiend_def_boost_py(){
  using namespace boost::python;
  
  class_< Gradient<Integ1e,Integ2e> >("Gradient",init<>())
    .def("cal_Vnn_deri",     &Gradient<Integ1e,Integ2e>::cal_Vnn_deri)
    .def("cal_force",        &Gradient<Integ1e,Integ2e>::cal_force_bp1<dMatrix>)
    .def("cal_force",        &Gradient<Integ1e,Integ2e>::cal_force_bp2<dMatrix>)
    .def("cal_force",        &Gradient<Integ1e,Integ2e>::cal_force_bp1<dMatrix_map>)
    .def("cal_force",        &Gradient<Integ1e,Integ2e>::cal_force_bp2<dMatrix_map>)
    .def("cal_force_u",      &Gradient<Integ1e,Integ2e>::cal_force_u_bp1<dMatrix>)
    .def("cal_force_u",      &Gradient<Integ1e,Integ2e>::cal_force_u_bp1<dMatrix_map>)
    .def("cal_force_u",      &Gradient<Integ1e,Integ2e>::cal_force_u_bp2<dMatrix>)
    .def("cal_force_u",      &Gradient<Integ1e,Integ2e>::cal_force_u_bp2<dMatrix_map>)
  ;
}

}   // end of namespace "Lotus_core"
#endif // include-guard


