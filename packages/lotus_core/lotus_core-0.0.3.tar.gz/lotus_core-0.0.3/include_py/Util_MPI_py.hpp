


#ifndef UTIL_MPI_PY_H
#define UTIL_MPI_PY_H

#ifdef USE_MPI_LOTUS
#include "mpi.h"
#endif

#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

#include <string.h>

#include "Util_MPI.hpp"
#include "Matrixs_tmpl.hpp"
namespace Lotus_core {


void Util_MPI_def_boost_py(){
  using namespace boost::python;

  
  class_<Util_MPI>("Util_MPI",init<>())


//    .def("set_MPI_COMM_LOTUS",      &Util_MPI::set_MPI_COMM_LOTUS_bp1)          
//    .def("set_MPI_COMM_LOTUS",      &Util_MPI::set_MPI_COMM_LOTUS_bp2)         
    .def("set_MPI_COMM_LOTUS",      &Util_MPI::set_MPI_COMM_LOTUS_bp3)        .staticmethod("set_MPI_COMM_LOTUS")

    .def("barrier",                 &Util_MPI::barrier)                       .staticmethod("barrier")
    .def("get_size_rank",           &Util_MPI::get_size_rank)                 .staticmethod("get_size_rank")
    .def("get_mpi_size",            &Util_MPI::get_mpi_size)                  .staticmethod("get_mpi_size")
    .def("get_mpi_rank",            &Util_MPI::get_mpi_rank)                  .staticmethod("get_mpi_rank")

    .def("allreduce",               &Util_MPI::allreduce_bp1<dMatrix>)       
    .def("allreduce",               &Util_MPI::allreduce_bp1<dMatrix_map>)  
    .def("allreduce",               &Util_MPI::allreduce_bp2)              
    .def("allreduce",               &Util_MPI::allreduce_bp3)                
    .def("allreduce",               &Util_MPI::allreduce_bp4<dMatrix>)       
    .def("allreduce",               &Util_MPI::allreduce_bp4<dMatrix_map>)    .staticmethod("allreduce")

    .def("isendrecv",               &Util_MPI::isendrecv_bp1<dMatrix>)      
    .def("isendrecv",               &Util_MPI::isendrecv_bp1<dMatrix_map>)  
    .def("isendrecv",               &Util_MPI::isendrecv_bp2<dMatrix>)      
    .def("isendrecv",               &Util_MPI::isendrecv_bp2<dMatrix_map>)  
    .def("isendrecv",               &Util_MPI::isendrecv_bp3<dMatrix>)      
    .def("isendrecv",               &Util_MPI::isendrecv_bp3<dMatrix_map>)  
    .def("isendrecv",               &Util_MPI::isendrecv_bp4<dMatrix>)      
    .def("isendrecv",               &Util_MPI::isendrecv_bp4<dMatrix_map>)    .staticmethod("isendrecv")

//    .def("broadcast_text",          &Util_MPI::broadcast_text_bp1)
    .def("broadcast_text",          &Util_MPI::broadcast_text_bp1)            .staticmethod("broadcast_text")
    .def("broadcast_int",           &Util_MPI::broadcast_int)                 .staticmethod("broadcast_int")
    .def("broadcast_double",        &Util_MPI::broadcast_double)              .staticmethod("broadcast_double")
  ;
}


}   // end of namespace "Lotus_core"
#endif // include-guard

