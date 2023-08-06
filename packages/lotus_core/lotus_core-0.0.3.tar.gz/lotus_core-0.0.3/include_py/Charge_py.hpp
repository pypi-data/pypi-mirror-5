


#ifndef CHARGE_PY_H
#define CHARGE_PY_H

//#define BOOST_PYTHON_STATIC_LIB




#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>


#include "Charge.hpp"
namespace Lotus_core {

std::vector<Charge> get_vector_Charge(int n){
  std::vector<Charge> ret;
  for(int i=0;i<n;i++)  ret.push_back(Charge(0.0,  0.0, 0.0, 0.0));
  return ret; 
}

void Charge_def_boost_py(){
  using namespace boost::python;

  class_<Charge>("Charge",init<>())
    .def(init<double, double, double, double>())
    .def(init<double, double, double, double, int>())
    .def_readwrite("charge",  &Charge::charge) 
    .def_readwrite("x",       &Charge::x) 
    .def_readwrite("y",       &Charge::y) 
    .def_readwrite("z",       &Charge::z) 
    .def_readwrite("atom_no", &Charge::atom_no) 
    .def("show",              &Charge::show)
    .def("get_Rxyz",          &Charge::get_Rxyz)
  ;

  class_< std::vector<Charge> >("vec_Charge")
    .def(vector_indexing_suite< std::vector<Charge> >() );

  def("get_vector_Charge",       &get_vector_Charge);

}


}   // end of namespace "Lotus_core"
#endif // end of include-guard

