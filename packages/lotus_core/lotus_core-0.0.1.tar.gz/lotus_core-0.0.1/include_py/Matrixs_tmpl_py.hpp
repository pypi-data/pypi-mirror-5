




#ifndef MATRIXS_TMPL_PY_H
#define MATRIXS_TMPL_PY_H


#include <iostream>
#include <string>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>


#include "Matrixs_tmpl.hpp"



#define MACRO_FOR_LOTUS_CORE_DMATRIX(DMATRIX, MODULE_NAME)                             \
  class_< DMATRIX,bases<dMatrix_base> >(MODULE_NAME, init<>())                         \
    .def(init<int, int>())                                                             \
    .def("mat_clear",    &DMATRIX::mat_clear)                                          \
    .def("get_I",        &DMATRIX::get_I)                                              \
    .def("get_J",        &DMATRIX::get_J)                                              \
    .def("set_IJ",       &DMATRIX::set_IJ)                                             \
    .def("set_zero",     &DMATRIX::set_zero)                                           \
    .def("add",          (void(DMATRIX::*)(int, int, double))&DMATRIX::add)            \
    .def("set_value",    (void(DMATRIX::*)(int, int, double))&DMATRIX::set_value)      \
    .def("get_value",    &DMATRIX::get_value)                                          \
    .def("trace",        &DMATRIX::trace)                                              \
    .def("show_state",   &DMATRIX::show_state)                                         \
    .def("show",         &DMATRIX::show)                                               \
                                                                                       \


#define MACRO_FOR_LOTUS_CORE_ZMATRIX(ZMATRIX, MODULE_NAME)                             \
  class_< ZMATRIX,bases<zMatrix_base> >(MODULE_NAME, init<>())                         \
    .def(init<int, int>())                                                             \
    .def("mat_clear",    &ZMATRIX::mat_clear)                                          \
    .def("get_I",        &ZMATRIX::get_I)                                              \
    .def("get_J",        &ZMATRIX::get_J)                                              \
    .def("set_IJ",       &ZMATRIX::set_IJ)                                             \
    .def("set_zero",     &ZMATRIX::set_zero)                                           \
    .def("add",          (void(ZMATRIX::*)(int, int, double))   &ZMATRIX::add)         \
    .def("add",          (void(ZMATRIX::*)(int, int, dcomplex)) &ZMATRIX::add)         \
    .def("set_value",    (void(ZMATRIX::*)(int, int, double))   &ZMATRIX::set_value)   \
    .def("set_value",    (void(ZMATRIX::*)(int, int, dcomplex)) &ZMATRIX::set_value)   \
    .def("get_value",    &ZMATRIX::get_value)                                          \
    .def("trace",        &ZMATRIX::trace)                                              \
    .def("show_state",   &ZMATRIX::show_state)                                         \
    .def("show",         &ZMATRIX::show)                                               \
                                                                                       \
  




namespace Lotus_core {

//
//  vector
std::vector<dMatrix>     get_vector_dMatrix_bp(int n){     return vector_matrix<dMatrix>(n);  }
std::vector<zMatrix>     get_vector_zMatrix_bp(int n){     return vector_matrix<zMatrix>(n);  }
std::vector<dMatrix_map> get_vector_dMatrix_map_bp(int n){ return vector_matrix<dMatrix_map>(n);  }
std::vector<zMatrix_map> get_vector_zMatrix_map_bp(int n){ return vector_matrix<zMatrix_map>(n);  }
std::vector<dMatrix>     get_vector_dMatrix_bp2(int n,int I,int J){     return vector_matrix<dMatrix>(n,I,J);  }
std::vector<zMatrix>     get_vector_zMatrix_bp2(int n,int I,int J){     return vector_matrix<zMatrix>(n,I,J);  }
std::vector<dMatrix_map> get_vector_dMatrix_map_bp2(int n,int I,int J){ return vector_matrix<dMatrix_map>(n,I,J);  }
std::vector<zMatrix_map> get_vector_zMatrix_map_bp2(int n,int I,int J){ return vector_matrix<zMatrix_map>(n,I,J);  }


//
//  copy
void mat_copy_bp1(Matrix_base<double> &m1,Matrix_base<double> &m2){      mat_copy(m1,m2); }
void mat_copy_bp2(Matrix_base<dcomplex> &m1,Matrix_base<double> &m2){    mat_copy(m1,m2); }
void mat_copy_bp3(Matrix_base<dcomplex> &m1,Matrix_base<dcomplex> &m2){  mat_copy(m1,m2); }

//
//  add
void mat_add_bp1(Matrix_base<double> &m1,Matrix_base<double> &m2,Matrix_base<double> &m3){        mat_add(m1,m2,m3); }
void mat_add_bp2(Matrix_base<dcomplex> &m1,Matrix_base<double> &m2,Matrix_base<double> &m3){      mat_add(m1,m2,m3); }
void mat_add_bp3(Matrix_base<dcomplex> &m1,Matrix_base<dcomplex> &m2,Matrix_base<double> &m3){    mat_add(m1,m2,m3); }
void mat_add_bp4(Matrix_base<dcomplex> &m1,Matrix_base<double> &m2,Matrix_base<dcomplex> &m3){    mat_add(m1,m2,m3); }
void mat_add_bp5(Matrix_base<dcomplex> &m1,Matrix_base<dcomplex> &m2,Matrix_base<dcomplex> &m3){  mat_add(m1,m2,m3); }

//
//  sub
void mat_sub_bp1(Matrix_base<double> &m1,Matrix_base<double> &m2,Matrix_base<double> &m3){        mat_sub(m1,m2,m3); }
void mat_sub_bp2(Matrix_base<dcomplex> &m1,Matrix_base<double> &m2,Matrix_base<double> &m3){      mat_sub(m1,m2,m3); }
void mat_sub_bp3(Matrix_base<dcomplex> &m1,Matrix_base<dcomplex> &m2,Matrix_base<double> &m3){    mat_sub(m1,m2,m3); }
void mat_sub_bp4(Matrix_base<dcomplex> &m1,Matrix_base<double> &m2,Matrix_base<dcomplex> &m3){    mat_sub(m1,m2,m3); }
void mat_sub_bp5(Matrix_base<dcomplex> &m1,Matrix_base<dcomplex> &m2,Matrix_base<dcomplex> &m3){  mat_sub(m1,m2,m3); }

//
//  mul
void mat_mul_bp1(Matrix_base<double> &m1,Matrix_base<double> &m2,Matrix_base<double> &m3){        mat_mul(m1,m2,m3); }
void mat_mul_bp2(Matrix_base<dcomplex> &m1,Matrix_base<double> &m2,Matrix_base<double> &m3){      mat_mul(m1,m2,m3); }
void mat_mul_bp3(Matrix_base<dcomplex> &m1,Matrix_base<dcomplex> &m2,Matrix_base<double> &m3){    mat_mul(m1,m2,m3); }
void mat_mul_bp4(Matrix_base<dcomplex> &m1,Matrix_base<double> &m2,Matrix_base<dcomplex> &m3){    mat_mul(m1,m2,m3); }
void mat_mul_bp5(Matrix_base<dcomplex> &m1,Matrix_base<dcomplex> &m2,Matrix_base<dcomplex> &m3){  mat_mul(m1,m2,m3); }

void mat_mul_bp6(Matrix_base<double> &m1,double v,Matrix_base<double> &m2){         mat_mul_v(m1,v,m2); }
void mat_mul_bp7(Matrix_base<dcomplex> &m1,double v,Matrix_base<double> &m2){       mat_mul_v(m1,v,m2); }
void mat_mul_bp8(Matrix_base<dcomplex> &m1,double v,Matrix_base<dcomplex> &m2){     mat_mul_v(m1,v,m2); }
void mat_mul_bp9(Matrix_base<dcomplex> &m1,dcomplex v,Matrix_base<double> &m2){     mat_mul_v(m1,v,m2); }
void mat_mul_bp10(Matrix_base<dcomplex> &m1,dcomplex v,Matrix_base<dcomplex> &m2){  mat_mul_v(m1,v,m2); }

//
//  transpose
void mat_transpose_bp1(Matrix_base<double> &m1,Matrix_base<double> &m2){      mat_transpose(m1,m2); }
void mat_transpose_bp2(Matrix_base<dcomplex> &m1,Matrix_base<double> &m2){    mat_transpose(m1,m2); }
void mat_transpose_bp3(Matrix_base<dcomplex> &m1,Matrix_base<dcomplex> &m2){  mat_transpose(m1,m2); }


//
//  eigen
void cal_eigen_bp1(const Matrix_base<double> &A, const Matrix_base<double> &S,  Matrix_base<double> &X,
                   std::vector<double> &ret_lamda){
  cal_eigen(A, S, X, ret_lamda);
} 



void Matrixs_def_boost_py(){
  using namespace boost::python;


  class_<dMatrix_base>("dMatrix_base",init<>())
  ;
  class_<zMatrix_base>("zMatrix_base",init<>())
  ;

  MACRO_FOR_LOTUS_CORE_DMATRIX(dMatrix,     "dMatrix");
  MACRO_FOR_LOTUS_CORE_DMATRIX(dMatrix_map, "dMatrix_map");
  MACRO_FOR_LOTUS_CORE_ZMATRIX(zMatrix,     "zMatrix");
  MACRO_FOR_LOTUS_CORE_ZMATRIX(zMatrix_map, "zMatrix_map");


  class_< std::vector<dMatrix> >("vec_dMatrix")
    .def(vector_indexing_suite< std::vector<dMatrix> >() );

  class_< std::vector<dMatrix_map> >("vec_dMatrix_map")
    .def(vector_indexing_suite< std::vector<dMatrix_map> >() );

  class_< std::vector<zMatrix> >("vec_zMatrix")
    .def(vector_indexing_suite< std::vector<zMatrix> >() );

  class_< std::vector<zMatrix_map> >("vec_zMatrix_map")
    .def(vector_indexing_suite< std::vector<zMatrix_map> >() );


  def("get_vector_dMatrix",    &get_vector_dMatrix_bp);
  def("get_vector_dMatrix",    &get_vector_dMatrix_bp2);
  def("get_vector_zMatrix",    &get_vector_zMatrix_bp);
  def("get_vector_zMatrix",    &get_vector_zMatrix_bp2);
  def("get_vector_dMatrix_map",&get_vector_dMatrix_map_bp);
  def("get_vector_dMatrix_map",&get_vector_dMatrix_map_bp2);
  def("get_vector_zMatrix_map",&get_vector_zMatrix_map_bp);
  def("get_vector_zMatrix_map",&get_vector_zMatrix_map_bp2);

  // copy
  def("mat_copy", &mat_copy_bp1);
  def("mat_copy", &mat_copy_bp2);
  def("mat_copy", &mat_copy_bp3);
  // add
  def("mat_add",  &mat_add_bp1);
  def("mat_add",  &mat_add_bp2);
  def("mat_add",  &mat_add_bp3);
  def("mat_add",  &mat_add_bp4);
  def("mat_add",  &mat_add_bp5);
  // sub
  def("mat_sub",  &mat_sub_bp1);
  def("mat_sub",  &mat_sub_bp2);
  def("mat_sub",  &mat_sub_bp3);
  def("mat_sub",  &mat_sub_bp4);
  def("mat_sub",  &mat_sub_bp5);
  // mul
  def("mat_mul",  &mat_mul_bp1);
  def("mat_mul",  &mat_mul_bp2);
  def("mat_mul",  &mat_mul_bp3);
  def("mat_mul",  &mat_mul_bp4);
  def("mat_mul",  &mat_mul_bp5);

  def("mat_mul",  &mat_mul_bp6);
  def("mat_mul",  &mat_mul_bp7);
  def("mat_mul",  &mat_mul_bp8);
  def("mat_mul",  &mat_mul_bp9);
  def("mat_mul",  &mat_mul_bp10);

  // transpose
  def("mat_transpose",&mat_transpose_bp1);
  def("mat_transpose",&mat_transpose_bp2);
  def("mat_transpose",&mat_transpose_bp3);

  // cal_eigen 
  def("cal_eigen",    &cal_eigen_bp1);

/*
  // inverse
//  def("mat_inverse",&mat_inverse<dMatrix>);
  def("mat_inverse",&mat_inverse<dMatrix_base>);

  //  solve equations  AX=B  (X=A^-1 B)
//  def("call_dgesv", &call_dgesv<dMatrix>);
  def("call_dgesv", &call_dgesv<dMatrix_base>);

  // Ax = lamda x: obtain eigene value and eigene vector
//  def("call_dsyev",&call_dsyev<dMatrix>);
  def("call_dsyev",&call_dsyev<dMatrix_base>);

  // obtain eigene valeu and vector for Ax=lamda Sx
//  def("call_dsygv",&call_dsygv<dMatrix>);
  def("call_dsygv",&call_dsygv<dMatrix_base>);
*/
  ;
}

//BOOST_PYTHON_MODULE(Matrixs){
//  Matrixs_def_boost_py();
//}

}   // end of namespace "Lotus_core"
#endif

  

