


#ifndef CVector_PY_H
#define CVector_PY_H

//#define BOOST_PYTHON_STATIC_LIB




#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
namespace Lotus_core {



std::vector<double> get_vector_double_bp(int n){
  std::vector<double> ret;
  for(int i=0;i<n;i++)  ret.push_back(0.0);
  return ret; 
}

std::vector<int> get_vector_int_bp(int n){
  std::vector<int> ret;
  for(int i=0;i<n;i++)  ret.push_back(0);
  return ret; 
}


template <typename T>
boost::python::list vector2list(std::vector<T> &vec){
  boost::python::list ret_li;
  int N_vec = vec.size();
  for(int i=0;i<N_vec;i++){
    ret_li.append(vec[i]);
  }
  return ret_li;
}


template <typename T>
std::vector<T> list2vector(boost::python::list &in_li){
  std::vector<T> ret_vec;
  int N_li=(int) boost::python::len((boost::python::object)in_li);
  for(int i=0;i<N_li;i++){
    ret_vec.push_back( boost::python::extract<T>(in_li[i]) );
  }
  return ret_vec;
}


void CVector_def_boost_py(){
  using namespace boost::python;


  class_< std::vector<double> >("vec_double")
    .def(vector_indexing_suite< std::vector<double> >() );

  class_< std::vector<int> >("vec_int")
    .def(vector_indexing_suite< std::vector<int> >() );

  def("get_vector_double",     &get_vector_double_bp);
  def("get_vector_int",        &get_vector_double_bp);

  def("vector2list",           &vector2list<int>);
  def("vector2list",           &vector2list<double>);

  def("list2vector_int",       &list2vector<int>);
  def("list2vector_double",    &list2vector<double>);

}


}   // end of namespace "Lotus_core"
#endif // end of include-guard

