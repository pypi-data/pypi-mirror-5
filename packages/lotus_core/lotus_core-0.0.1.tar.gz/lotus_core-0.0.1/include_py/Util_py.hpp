




#ifndef UTIL_PY_H
#define UTIL_PY_H


#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>


#include "Util.hpp"
#include "Matrixs_tmpl.hpp"

namespace Lotus_core {


void Util_def_boost_py(){
  using namespace boost::python;

  class_<Util>("Util",init<>())
    .def("get_string_from_file",    &Util::get_string_from_file)            
    .staticmethod("get_string_from_file")
    .def("cal_DV",                  &Util::cal_DV<dMatrix,     dMatrix>)    
    .def("cal_DV",                  &Util::cal_DV<dMatrix_map, dMatrix_map>)
    .staticmethod("cal_DV")
    .def("cal_D",                   &Util::cal_D<dMatrix>)                 
    .def("cal_D",                   &Util::cal_D<dMatrix_map>)               
    .staticmethod("cal_D")
    .def("cal_W",                   &Util::cal_W<dMatrix>)                
    .def("cal_W",                   &Util::cal_W<dMatrix_map>)       
    .staticmethod("cal_W")
    .def("cal_occ_ab",              &Util::cal_occ_ab_bp1)               
    .def("cal_occ_ab",              &Util::cal_occ_ab_bp2)                
    .staticmethod("cal_occ_ab")
    .def("cal_occ",                 &Util::cal_occ_bp1)                 
    .def("cal_occ",                 &Util::cal_occ_bp2)                 
    .staticmethod("cal_occ")
    .def("get_charges",             &Util::get_charges_bp1<Shell_Cgto>)   
    .def("get_charges",             &Util::get_charges_bp1<Cgto>)        
    .def("get_charges",             &Util::get_charges_bp1<Cgto_base>)   
    .def("get_charges",             &Util::get_charges_bp2<Shell_Cgto>)      
    .def("get_charges",             &Util::get_charges_bp2<Cgto>)           
    .def("get_charges",             &Util::get_charges_bp2<Cgto_base>)    
    .staticmethod("get_charges")
    .def("get_total_charge",        &Util::get_total_charge_bp1<Shell_Cgto>) 
    .def("get_total_charge",        &Util::get_total_charge_bp1<Cgto>)      
    .def("get_total_charge",        &Util::get_total_charge_bp1<Cgto_base>) 
    .def("get_total_charge",        &Util::get_total_charge_bp2<Shell_Cgto>)
    .def("get_total_charge",        &Util::get_total_charge_bp2<Cgto>)      
    .def("get_total_charge",        &Util::get_total_charge_bp2<Cgto_base>) 
    .staticmethod("get_total_charge")
    .def("cal_energy_repul_nn",     &Util::cal_energy_repul_nn<Shell_Cgto>)  
    .def("cal_energy_repul_nn",     &Util::cal_energy_repul_nn<Cgto>)       
    .def("cal_energy_repul_nn",     &Util::cal_energy_repul_nn<Cgto_base>)   
    .staticmethod("cal_energy_repul_nn")
    .def("get_max_d",               &Util::get_max_d<dMatrix>)   
    .def("get_max_d",               &Util::get_max_d<dMatrix_map>)   
    .staticmethod("get_max_d")


  ;

}


}   // end of namespace "Lotus_core"
#endif // include-guard

