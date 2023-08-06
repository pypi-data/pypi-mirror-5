

 



#ifndef GRID_PY_H
#define GRID_PY_H


#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

#include "Grid.hpp"
namespace Lotus_core {


void Grid_def_boost_py(){
  using namespace boost::python;

  class_<Grid>("Grid",init<>())
    .def("set_GL",                   &Grid::set_GL)                .staticmethod("set_GL")
    .def("radial_grid_GL",           &Grid::radial_grid_GL)        .staticmethod("radial_grid_GL")
    .def("angular_grid_GL",          &Grid::angular_grid_GL)       .staticmethod("angular_grid_GL")
    .def("radial_grid_GC",           &Grid::radial_grid_GC)        .staticmethod("radial_grid_GC")
    .def("angular_grid_LEBEDEV",     &Grid::angular_grid_LEBEDEV)  .staticmethod("angular_grid_LEBEDEV")
    .def("construct_grid_LEB",       &Grid::construct_grid_LEB)    .staticmethod("construct_grid_LEB")
    .def("construct_grid_GL",        &Grid::construct_grid_GL)     .staticmethod("construct_grid_GL")
    .def("cal_Ran",                  &Grid::cal_Ran)               .staticmethod("cal_Ran")
    .def("grid_weight_ATOM",         &Grid::grid_weight_ATOM)      .staticmethod("grid_weight_ATOM")
  ;

}


}   // end of namespace "Lotus_core"
#endif // include-guard


