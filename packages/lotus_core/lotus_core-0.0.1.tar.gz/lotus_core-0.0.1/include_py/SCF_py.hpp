




#ifndef SCF_PY_H
#define SCF_PY_H


#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>


#include "SCF.hpp"
#include "Matrixs_tmpl.hpp"
#include "Fock2e_tmpl.hpp"
#include "Integ_py.hpp"


namespace Lotus_core {


void SCF_def_boost_py(){
  using namespace boost::python;

  class_<MolData>("MolData",init<>())
    .def_readwrite("scgtos",                &MolData::scgtos)
    .def_readwrite("ecps",                  &MolData::ecps)
    .def_readwrite("mol_charge",            &MolData::mol_charge)
    .def_readwrite("spin",                  &MolData::spin)
    .def("set_basis_from_file",             &MolData::set_basis_from_file<Integ1e>)
    .def("set_basis_from_string",           &MolData::set_basis_from_string<Integ1e>)
   
  ;

  class_< SCF<Integ1e,Integ2e> >("SCF",init<>())
//    .def_readwrite("max_diis",              &SCF<Integ1e,Integ2e>::max_diis)
//    .def_readwrite("max_scf",               &SCF<Integ1e,Integ2e>::max_scf)
//    .def_readwrite("threshold_scf",         &SCF<Integ1e,Integ2e>::threshold_scf)
//    .def_readwrite("mix_dens",              &SCF<Integ1e,Integ2e>::mix_dens)


    .def("get_ene_vh",                      &SCF<Integ1e,Integ2e>::get_ene_vh)
    .def("get_ene_vx",                      &SCF<Integ1e,Integ2e>::get_ene_vx)
    .def("get_ene_dft",                     &SCF<Integ1e,Integ2e>::get_ene_dft)
    .def("get_ene_h_core",                  &SCF<Integ1e,Integ2e>::get_ene_h_core)
    .def("get_ene_ele",                     &SCF<Integ1e,Integ2e>::get_ene_ele)
    .def("get_ene_vnn",                     &SCF<Integ1e,Integ2e>::get_ene_vnn)
    .def("get_ene_total",                   &SCF<Integ1e,Integ2e>::get_ene_total)

    .def("do_diis",                         &SCF<Integ1e,Integ2e>::do_diis)
    .def("do_ediis",                        &SCF<Integ1e,Integ2e>::do_ediis)

    .def("cal_h_core",                      &SCF<Integ1e,Integ2e>::cal_h_core<dMatrix>)
    .def("cal_h_core",                      &SCF<Integ1e,Integ2e>::cal_h_core<dMatrix_map>)

    .def("guess_h_core",                    &SCF<Integ1e,Integ2e>::guess_h_core<dMatrix>)
    .def("guess_h_core",                    &SCF<Integ1e,Integ2e>::guess_h_core<dMatrix_map>)

    .def("prepare_eri",                     &SCF<Integ1e,Integ2e>::prepare_eri<dMatrix,    ERI_direct>)
    .def("prepare_eri",                     &SCF<Integ1e,Integ2e>::prepare_eri<dMatrix,    ERI_file>)
    .def("prepare_eri",                     &SCF<Integ1e,Integ2e>::prepare_eri<dMatrix,    ERI_incore>)
    .def("prepare_eri",                     &SCF<Integ1e,Integ2e>::prepare_eri<dMatrix_map,ERI_direct>)
    .def("prepare_eri",                     &SCF<Integ1e,Integ2e>::prepare_eri<dMatrix_map,ERI_file>)
    .def("prepare_eri",                     &SCF<Integ1e,Integ2e>::prepare_eri<dMatrix_map,ERI_incore>)

    .def("cal_Fock_sub",                    &SCF<Integ1e,Integ2e>::cal_Fock_sub<dMatrix, ERI_direct>)
    .def("cal_Fock_sub",                    &SCF<Integ1e,Integ2e>::cal_Fock_sub<dMatrix, ERI_file>)
    .def("cal_Fock_sub",                    &SCF<Integ1e,Integ2e>::cal_Fock_sub<dMatrix, ERI_incore>)
    .def("cal_Fock_sub",                    &SCF<Integ1e,Integ2e>::cal_Fock_sub<dMatrix_map, ERI_direct>)
    .def("cal_Fock_sub",                    &SCF<Integ1e,Integ2e>::cal_Fock_sub<dMatrix_map, ERI_file>)
    .def("cal_Fock_sub",                    &SCF<Integ1e,Integ2e>::cal_Fock_sub<dMatrix_map, ERI_incore>)

    .def("cal_Fock_sub_u",                  &SCF<Integ1e,Integ2e>::cal_Fock_sub_u<dMatrix,ERI_direct>)
    .def("cal_Fock_sub_u",                  &SCF<Integ1e,Integ2e>::cal_Fock_sub_u<dMatrix,ERI_file>)
    .def("cal_Fock_sub_u",                  &SCF<Integ1e,Integ2e>::cal_Fock_sub_u<dMatrix,ERI_incore>)
    .def("cal_Fock_sub_u",                  &SCF<Integ1e,Integ2e>::cal_Fock_sub_u<dMatrix_map,ERI_direct>)
    .def("cal_Fock_sub_u",                  &SCF<Integ1e,Integ2e>::cal_Fock_sub_u<dMatrix_map,ERI_file>)
    .def("cal_Fock_sub_u",                  &SCF<Integ1e,Integ2e>::cal_Fock_sub_u<dMatrix_map,ERI_incore>)

    .def("diis",                            &SCF<Integ1e,Integ2e>::diis< std::vector<dMatrix>,     dMatrix >)
    .def("diis",                            &SCF<Integ1e,Integ2e>::diis< std::vector<dMatrix_map>, dMatrix_map >)
    
    .def("ediis_sub",                       &SCF<Integ1e,Integ2e>::ediis_sub<dMatrix>)
    .def("ediis_sub",                       &SCF<Integ1e,Integ2e>::ediis_sub<dMatrix_map>)
    .def("ediis",                           &SCF<Integ1e,Integ2e>::ediis< std::vector<dMatrix>, dMatrix >)
    .def("ediis",                           &SCF<Integ1e,Integ2e>::ediis< std::vector<dMatrix_map>, dMatrix_map >)

    .def("get_max_d",                       &SCF<Integ1e,Integ2e>::get_max_d< std::vector<dMatrix> >)
    .def("get_max_d",                       &SCF<Integ1e,Integ2e>::get_max_d< std::vector<dMatrix_map> >)
    .def("cal_energy",                      &SCF<Integ1e,Integ2e>::cal_energy<dMatrix>)
    .def("cal_energy",                      &SCF<Integ1e,Integ2e>::cal_energy<dMatrix_map>)
    .def("cal_energy_u",                    &SCF<Integ1e,Integ2e>::cal_energy_u<dMatrix>)
    .def("cal_energy_u",                    &SCF<Integ1e,Integ2e>::cal_energy_u<dMatrix_map>)
    .def("cal_show_energy",                 &SCF<Integ1e,Integ2e>::cal_show_energy<dMatrix>)
    .def("cal_show_energy",                 &SCF<Integ1e,Integ2e>::cal_show_energy<dMatrix_map>)
    .def("cal_show_energy_u",               &SCF<Integ1e,Integ2e>::cal_show_energy_u<dMatrix>)
    .def("cal_show_energy_u",               &SCF<Integ1e,Integ2e>::cal_show_energy_u<dMatrix_map>)
  
//    .def("r_scf_direct",                    &SCF<Integ1e,Integ2e>::r_scf<dMatrix, ERI_direct>) 
//    .def("r_scf_file",                      &SCF<Integ1e,Integ2e>::r_scf<dMatrix, ERI_file>) 
//    .def("r_scf_incore",                    &SCF<Integ1e,Integ2e>::r_scf<dMatrix, ERI_incore>) 
//    .def("r_scf_direct_map",                &SCF<Integ1e,Integ2e>::r_scf<dMatrix_map, ERI_direct>) 
//    .def("r_scf_file_map",                  &SCF<Integ1e,Integ2e>::r_scf<dMatrix_map, ERI_file>) 
//    .def("r_scf_incore_map",                &SCF<Integ1e,Integ2e>::r_scf<dMatrix_map, ERI_incore>) 

//    .def("u_scf_direct",                    &SCF<Integ1e,Integ2e>::u_scf<dMatrix, ERI_direct>) 
//    .def("u_scf_file",                      &SCF<Integ1e,Integ2e>::u_scf<dMatrix, ERI_file>) 
//    .def("u_scf_incore",                    &SCF<Integ1e,Integ2e>::u_scf<dMatrix, ERI_incore>) 
//    .def("u_scf_direct_map",                &SCF<Integ1e,Integ2e>::u_scf<dMatrix_map, ERI_direct>) 
//    .def("u_scf_file_map",                  &SCF<Integ1e,Integ2e>::u_scf<dMatrix_map, ERI_file>) 
//    .def("u_scf_incore_map",                &SCF<Integ1e,Integ2e>::u_scf<dMatrix_map, ERI_incore>) 


  ;

}


}   // end of namespace "Lotus_core"
#endif // end of include-guard

