
#ifndef MATRIXS_TMPL_H
#define MATRIXS_TMPL_H

#include <iostream>
#include <vector>
#include <algorithm>
#include <complex>
#include <map>
//#ifndef BOOST_UNORDERED_MAP_HPP
//#define BOOST_UNORDERED_MAP_HPP
//#include <boost/unordered_map.hpp>
//#endif

#define   EIGEN_MPL2_ONLY
#include "Eigen/Dense"
#include "Eigen/Eigenvalues"

namespace Lotus_core {

typedef std::complex<double>      dcomplex;

namespace funs_for_matrixs {
  using namespace std;
  template <typename T>
  void show_matrix(const T &m){
    int I=m.get_I();
    int J=m.get_J();
    for(int i=0;i<I;i++){
      for(int j=0;j<J;j++){
     //   printf("%7.4f ",m.get_value(i,j));
        cout.width(10);
        cout.precision(4);
        cout.setf(ios::fixed,ios::floatfield);
        cout<<m.get_value(i,j)<<" ";
      }
      cout<<endl;
    }
    cout<<endl;

  }

  template <typename M1,typename M2>
  void copy_matrix(M1 &dest,M2 &orig){
    int I=dest.get_I();
    int J=dest.get_J();
    for(int i=0;i<I;i++){
      for(int j=0;j<J;j++){
        dest.set_value(i,j,orig.get_value(i,j));
      }
    }
  }


}

template <typename T>
class Matrix_base {
private:
  virtual void set_value_imp(int i,int j,T in_v){};
  virtual void add_imp(int i,int j,T in_v){};
public:
  virtual ~Matrix_base(){};
  void set_value(int i,int j,T in_v){ set_value_imp(i,j,in_v); }
  void add(int i,int j,T in_v){       add_imp(i,j,in_v); }
  virtual T get_value(int i,int j) const { T dummy=0.0; return dummy;}
  virtual int get_I() const { return -1;}
  virtual int get_J() const { return -1;}
  virtual void set_zero() {}
  virtual void set_IJ(int in_I,int in_J){}
  virtual void show() const {}
};


template <typename U=double>
class Matrix_t : public Matrix_base<U> {
  std::vector<U> mat;
  int I,J;
  void mat_reserve(int in_I,int in_J){  mat.reserve(in_I*in_J); }
  void set_value_imp(int i,int j,U in_v){ set_value(i,j,in_v); }
  void add_imp(int i,int j,U in_v){ add(i,j,in_v); }
public:
  typedef U type;


  Matrix_t() : I(1), J(1) { 
    this->mat_reserve(I,J); 
    this->set_zero();
  }
  Matrix_t(int in_I,int in_J){
    I=in_I;
    J=in_J;
    this->mat_reserve(I,J);
    this->set_zero();
  }
  ~Matrix_t(){ mat_clear(); }

  Matrix_t(const Matrix_t<U>& copy){
    if((void*)this==(void*)&copy) return;
    I=copy.get_I();
    J=copy.get_J();
    mat_clear();
    mat_reserve(I,J);
    for(int i=0;i<I;i++){
      for(int j=0;j<J;j++){ 
        mat[i*J+j]=copy.get_value(i,j);
      }
    }
  }

  template <typename T>
  Matrix_t<U> &operator=(T &in_m){
    if((void*)this==(void*)&in_m) return *this;
    this->mat_clear();
    this->set_IJ(in_m.get_I(),in_m.get_J());
    funs_for_matrixs::copy_matrix(*this,in_m); 
    return *this;
  }
  template <typename T>
  bool operator==(const T &in_m){ 
    if((void*)this==(void*)&in_m) return true;
    else                          return false;
  }

  void mat_clear(){  std::vector<U> tmp_mat; tmp_mat.swap(mat); }

  int get_I() const { return I; }
  int get_J() const { return J; }
  void set_IJ(int in_I,int in_J){
    I=in_I;
    J=in_J;
    this->mat_clear();
    this->mat_reserve(I,J);
    this->set_zero();
  }
  void set_zero(){
    for(int i=0;i<I;i++){
      for(int j=0;j<J;j++){
        this->set_value(i,j,0.0);
      }
    }
  }
  template <typename T>
  void add(int i,int j,T in_v){           mat[i*J+j]+=in_v; }
  template <typename T>
  void set_value(int i,int j,T v){        mat[i*J+j]=v; }
    


  U get_value(int i,int j) const { return mat[i*J+j]; }  

  U trace() const {
    U ret=0.0;
    for(int i=0;i<I;i++) ret+=get_value(i,i);
    return ret;
  }


  void show_state(){
    std::cout<<" I,J "<<I<<" "<<J<<std::endl;
    std::cout<<" mat size,capacity "<<mat.size()<<" "<<mat.capacity()<<std::endl;
  }
  void show() const { funs_for_matrixs::show_matrix< Matrix_t<U> >(*this); }


};



template <typename U>
class Matrix_map : public Matrix_base<U> {
//  typedef boost::unordered_map<int,U> map_type;
  typedef std::map<int,U> map_type;
  map_type mat;
  int I,J;
  void set_value_imp(int i,int j,U in_v){ set_value(i,j,in_v); }
  void add_imp(int i,int j,U in_v){ add(i,j,in_v); }
public:
  Matrix_map() : I(1), J(1) {} 
  Matrix_map(int in_I,int in_J) : I(in_I), J(in_J) {}
  ~Matrix_map(){ mat_clear(); }

  Matrix_map(const Matrix_map<U>& copy){
    if((void*)this==(void*)&copy) return;
    I=copy.get_I();
    J=copy.get_J();
    mat_clear();
    funs_for_matrixs::copy_matrix(*this,copy); 
  }


  template <typename T>
  Matrix_map<U> &operator=(T &in_m){
    if((void*)this==(void*)&in_m) return *this;
    this->mat_clear();
    this->set_IJ(in_m.get_I(),in_m.get_J());
    funs_for_matrixs::copy_matrix(*this,in_m); 
    return *this;
  }
  template <typename T>
  bool operator==(T &in_m){ 
    if((void*)this==(void*)&in_m) return true;
    else            return false;
  }

  void mat_clear(){  map_type tmp_mat; tmp_mat.swap(mat); }
  

  int get_I() const { return I; }
  int get_J() const { return J; }
  void set_IJ(int in_I,int in_J){
    I=in_I;
    J=in_J;
    this->mat_clear();
  }
  void set_zero(){ this->mat_clear(); }
  
  template <typename T>
  void add(int i,int j,T in_v){
    if(std::abs(in_v)>1.0e-15){
      mat[i*J+j]+=in_v;
    }
  }


  template <typename T>
  void set_value(int i,int j,T in_v){
    if(std::abs(in_v)>1.0e-15){
      mat[i*J+j]=in_v;
    }else{
      typename map_type::const_iterator itr = mat.find(i*J+j);
      if(itr!=mat.end()){
        mat[i*J+j]=0.0;
      }
    }
  }

  U get_value(int i,int j) const {
    typename map_type::const_iterator itr = mat.find(i*J+j);
    if(itr!=mat.end()) return itr->second;
    else               return 0.0;
  }

  U trace() const {
    U ret=0.0;
    for(int i=0;i<I;i++) ret+=get_value(i,i);
    return ret;
  }

  void show_state() const {
    std::cout<<" I,J "<<I<<" "<<J<<std::endl;
    std::cout<<" mat size "<<mat.size()<<std::endl;
  }

  void show() const { funs_for_matrixs::show_matrix< Matrix_map<U> >(*this); }

};

typedef Matrix_base<double>           dMatrix_base;
typedef Matrix_base<dcomplex>         zMatrix_base;
typedef Matrix_t<double>              dMatrix;
typedef Matrix_t<dcomplex>            zMatrix;
typedef Matrix_map<double>            dMatrix_map;
typedef Matrix_map< std::complex<double> > zMatrix_map;

//
// vector<Matrix>
//
template <typename C>
std::vector<C> vector_matrix(int n,int I=1,int J=1){
  std::vector<C> ret;
  for(int i=0;i<n;i++){
    C m(I,J);
    ret.push_back(m);
  }
  return ret; 
}

//
// copy
//
template <typename M1,typename M2>
void mat_copy(M1 &m1,M2 &m2){
  M1 *m1_ptr = &m1;
  M2 *m2_ptr = &m2;
  int I=m2.get_I();
  int J=m2.get_J();
  m1_ptr->set_IJ(I,J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      m1_ptr->set_value(i,j,m2_ptr->get_value(i,j));
    }
  }
}

//
// add
//
template <typename M1,typename M2,typename M3>
void mat_add(M1 &m1,M2 &m2,M3 &m3){
  M1 *m1_ptr = &m1;
  M2 *m2_ptr = &m2;
  M3 *m3_ptr = &m3;
  int I=m2.get_I();
  int J=m2.get_J();
  M1 tmpM;
  tmpM.set_IJ(I,J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      tmpM.set_value(i,j,m2_ptr->get_value(i,j)+m3_ptr->get_value(i,j));
    }
  }
  m1_ptr->set_IJ(I, J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      m1_ptr->set_value(i,j,tmpM.get_value(i,j));
    }
  }
}
template <typename T,typename M2,typename M3>
void mat_add(Matrix_base<T> &m1, M2 &m2, M3 &m3){
  Matrix_base<T> *m1_ptr = &m1;
  M2 *m2_ptr = &m2;
  M3 *m3_ptr = &m3;
  int I=m2.get_I();
  int J=m3.get_J();
  std::vector<T> tmp;
  tmp.reserve(I*J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      tmp[i*J+j]=m2_ptr->get_value(i,j)+m3_ptr->get_value(i,j);
    }
  }
  m1_ptr->set_IJ(I, J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      m1_ptr->set_value(i,j,tmp[i*J+j]);
    }
  }
}


//
// sub
//
template <typename M1,typename M2,typename M3>
void mat_sub(M1 &m1,M2 &m2,M3 &m3){
  M1 *m1_ptr = &m1;
  M2 *m2_ptr = &m2;
  M3 *m3_ptr = &m3;
  int I=m2.get_I();
  int J=m2.get_J();
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      m1_ptr->set_value(i,j,m2_ptr->get_value(i,j)-m3_ptr->get_value(i,j));
    }
  }
}
template <typename T,typename M2,typename M3>
void mat_sub(Matrix_base<T> &m1, M2 &m2, M3 &m3){
  Matrix_base<T> *m1_ptr = &m1;
  M2 *m2_ptr = &m2;
  M3 *m3_ptr = &m3;
  int I=m2.get_I();
  int J=m3.get_J();
  std::vector<T> tmp;
  tmp.reserve(I*J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      tmp[i*J+j]=m2_ptr->get_value(i,j)-m3_ptr->get_value(i,j);
    }
  }
  m1_ptr->set_IJ(I, J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      m1_ptr->set_value(i,j,tmp[i*J+j]);
    }
  }
}


//
//  mul
//
template <typename M1,typename M2,typename M3>
void mat_mul(M1 &m1,M2 &m2,M3 &m3){
  M1 *m1_ptr = &m1;
  M2 *m2_ptr = &m2;
  M3 *m3_ptr = &m3;
  int I=m2.get_I();
  int J=m3.get_J();
  int K=m3.get_I();
  M2 tmpM;
  tmpM.set_IJ(I,J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      for(int k=0;k<K;k++){
        tmpM.add(i,j,m2_ptr->get_value(i,k)*m3_ptr->get_value(k,j));
      }
    }
  }
  m1.set_IJ(I,J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      m1_ptr->set_value(i,j,tmpM.get_value(i,j));
    }
  }
}
template <typename T,typename M2,typename M3>
void mat_mul(Matrix_base<T> &m1,M2 &m2,M3 &m3){
  Matrix_base<T> *m1_ptr = &m1;
  M2 *m2_ptr = &m2;
  M3 *m3_ptr = &m3;
  int I=m2.get_I();
  int J=m3.get_J();
  int K=m3.get_I();
  std::vector<T> tmp;
  tmp.reserve(I*J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      tmp[i*J+j]=0.0;
      for(int k=0;k<K;k++){
        tmp[i*J+j]+=m2_ptr->get_value(i,k)*m3_ptr->get_value(k,j);
      }
    }
  }
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      m1_ptr->set_value(i,j,tmp[i*J+j]);
    }
  }
}


template <typename U,typename T,typename M2>
void mat_mul_v(Matrix_base<U> &m1, T v, M2 &m2){
  Matrix_base<U> *m1_ptr = &m1;
  M2 *m2_ptr             = &m2;
  int I=m2.get_I();
  int J=m2.get_J();
  std::vector<U> tmp;
  tmp.reserve(I*J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      tmp[i*J+j]=v*m2_ptr->get_value(i,j);
    }
  }
  m1_ptr->set_IJ(I,J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      m1_ptr->set_value(i, j, tmp[i*J+j]); 
    }
  }
}



template <typename M1,typename T,typename M2>
void mat_mul_v(M1 &m1, T v, M2 &m2){
  M1 *m1_ptr = &m1;
  M2 *m2_ptr = &m2;
  int I=m2.get_I();
  int J=m2.get_J();
  M1 tmpM;
  tmpM.set_IJ(I, J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      tmpM.set_value(i,j,v*m2_ptr->get_value(i,j));
    }
  }
  m1_ptr->set_IJ(I,J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      m1_ptr->set_value(i, j, tmpM.get_value(i, j)); 
    }
  }
}

//
// transpose
//
template <typename M1,typename M2>
void mat_transpose(M1 &b,M2 &a){  // b=a^t
  if((void*)&b==(void*)&a){
    std::cout<<"can't use a:=a^T by this function  "<<&a<<" "<<&b<<std::endl;
    exit(1);
  }
  M1 *b_ptr = &b;
  M2 *a_ptr = &a;
  int I=a.get_I();
  int J=a.get_J();
  b_ptr->set_IJ(J,I);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      b_ptr->set_value(j,i,a_ptr->get_value(i,j));
    }
  }
}




//
//  LAPACK
//
/*
template <typename M_tmpl>
void mat_inverse(M_tmpl &m);

//   solve equations  AX=B  (X=A^-1 B)
template <typename M_tmpl>
int call_dgesv(M_tmpl &A, M_tmpl &X, M_tmpl &B);


// Ax = lamda x: obtain eigene value and eigene vector
template <typename M_tmpl>
int call_dsyev(M_tmpl &A, M_tmpl &X,std::vector<double> &ret_lamda);


// obtain eigene valeu and vector for Ax=lamda Sx
template <typename M_tmpl>
int call_dsygv(M_tmpl &A, M_tmpl &S, M_tmpl &X,std::vector<double> &ret_lamda);
*/

//
//  Eigen
//



//   solve invese matrix
template <typename M_tmpl>
void mat_inverse(M_tmpl &m){

  M_tmpl *m_ptr = &m;
  int I=m_ptr->get_I();
  int J=m_ptr->get_J();
  Eigen::MatrixXd eM(I,J), eM_inv(I,J);

  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      eM(i,j)=m_ptr->get_value(i,j);
    }
  }

  eM_inv=eM.inverse();

  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      m_ptr->set_value(i,j,eM_inv(i,j));
    }
  }

}


//   solve invese matrix
template <typename M_tmpl>
void mat_z_inverse(M_tmpl &m){

  M_tmpl *m_ptr = &m;
  int I=m_ptr->get_I();
  int J=m_ptr->get_J();
  Eigen::MatrixXcd eM(I,J), eM_inv(I,J);

  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      eM(i,j)=m_ptr->get_value(i,j);
    }
  }

  eM_inv=eM.inverse();

  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      m_ptr->set_value(i,j,eM_inv(i,j));
    }
  }

}



//   solve equations  AX=B  (X=A^-1 B)
template <typename M_tmpl>
void cal_simultaneous_eq(const M_tmpl &A, M_tmpl &X, const M_tmpl &B)
{

  M_tmpl *A_ptr = const_cast<M_tmpl*>(&A);
  M_tmpl *X_ptr = &X;
  M_tmpl *B_ptr = const_cast<M_tmpl*>(&B);

  int aI=A_ptr->get_I();
  int aJ=A_ptr->get_J();
  int bI=B_ptr->get_I();
  int bJ=B_ptr->get_J();

  Eigen::MatrixXd eA(aI,aJ);
  Eigen::MatrixXd eB(bI,bJ);
 
  for(int i=0;i<aI;i++){
    for(int j=0;j<aJ;j++){
      eA(i,j)=A_ptr->get_value(i,j);
    }
  }
  for(int i=0;i<bI;i++){
    for(int j=0;j<bJ;j++){
      eB(i,j)=B_ptr->get_value(i,j);
    }
  }

  Eigen::MatrixXd eX(bI,bJ);
  eX = eA.colPivHouseholderQr().solve(eB);

  for(int i=0;i<bI;i++){
    for(int j=0;j<bJ;j++){
      X_ptr->set_value(i,j,eX(i,j));
    }
  }

}

// Ax = lamda x: obtain eigene value and eigene vector
template <typename M_tmpl>
void cal_eigen(const M_tmpl &A, M_tmpl &X, std::vector<double> &ret_lamda){

  using namespace std;
  M_tmpl *A_ptr = const_cast<M_tmpl*>(&A);
  M_tmpl *X_ptr = &X;
  int I=A_ptr->get_I();
  int J=A_ptr->get_J();

  ret_lamda.clear();
  ret_lamda.reserve(I);
  X_ptr->set_IJ(I,J);

  Eigen::MatrixXd eA(I,J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      eA(i,j)=A_ptr->get_value(i,j);
    }
  }

  Eigen::EigenSolver<Eigen::MatrixXd> es(eA);
  Eigen::Matrix<complex<double>,Eigen::Dynamic,Eigen::Dynamic>  eX = es.eigenvectors();

  std::vector< std::pair<double,int> > data;
  std::vector< std::pair<double,int> >::iterator it;

  for(int i=0;i<I;i++){
    std::complex<double> tmp_v=es.eigenvalues()[i];
    data.push_back( std::pair<double,int>( (double)tmp_v.real(), i) );
  }

  std::sort(data.begin(), data.end()); 
  for(it=data.begin(); it!=data.end(); it++){
    ret_lamda.push_back(it->first);
  }

  int index_j=0; 
  for(it=data.begin(); it!=data.end(); it++){
    for(int i=0;i<I;i++){
      int j=it->second;
      std::complex<double> tmp_v=eX(i,j); 
      X_ptr->set_value(i,index_j,tmp_v.real());
    }
    index_j++;
  }

}


// obtain eigene valeu and vector for Ax=lamda Sx
template <typename M_tmpl>
void cal_eigen(const M_tmpl &A, const M_tmpl &S, M_tmpl &X, std::vector<double> &ret_lamda)
{

  using namespace std;
  M_tmpl *A_ptr = const_cast<M_tmpl*>(&A);
  M_tmpl *S_ptr = const_cast<M_tmpl*>(&S);
  M_tmpl *X_ptr = &X;
  int I=A_ptr->get_I();
  int J=A_ptr->get_J();

  ret_lamda.clear();
  ret_lamda.reserve(I);
  X_ptr->set_IJ(I,J);

  Eigen::MatrixXd eA(I,J), eS(I,J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      eA(i,j)=A_ptr->get_value(i,j);
      eS(i,j)=S_ptr->get_value(i,j);
    }
  }

  Eigen::GeneralizedSelfAdjointEigenSolver<Eigen::MatrixXd> es(eA,eS);
  Eigen::Matrix<double,Eigen::Dynamic,Eigen::Dynamic>  eX = es.eigenvectors();


  std::vector< std::pair<double,int> > data;
  std::vector< std::pair<double,int> >::iterator it;

  for(int i=0;i<I;i++){
    double tmp_v=es.eigenvalues()[i];
    data.push_back( std::pair<double,int>( (double)tmp_v, i) );
  }

  std::sort(data.begin(), data.end()); 
  for(it=data.begin(); it!=data.end(); it++){
    ret_lamda.push_back(it->first);
  }

  int index_j=0; 
  for(it=data.begin(); it!=data.end(); it++){
    for(int i=0;i<I;i++){
      int j=it->second;
      double tmp_v=eX(i,j); 
      X_ptr->set_value(i,index_j,tmp_v);
    }
    index_j++;
  }

}


// Ax = lamda x: obtain eigene value and eigene vector
template <typename M_tmpl>
void cal_z_eigen(const M_tmpl &A, M_tmpl &X, std::vector<double> &ret_lamda){

  using namespace std;
  M_tmpl *A_ptr = const_cast<M_tmpl*>(&A);
  M_tmpl *X_ptr = &X;
  int I=A_ptr->get_I();
  int J=A_ptr->get_J();

  ret_lamda.clear();
  ret_lamda.reserve(I);
  X_ptr->set_IJ(I,J);

  Eigen::MatrixXcd eA(I,J);
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      eA(i,j)=A_ptr->get_value(i,j);
    }
  }

  Eigen::ComplexEigenSolver<Eigen::MatrixXcd> es(eA);
  Eigen::Matrix<complex<double>,Eigen::Dynamic,Eigen::Dynamic>  eX = es.eigenvectors();



  std::vector< std::pair<double,int> > data;
  std::vector< std::pair<double,int> >::iterator it;

  for(int i=0;i<I;i++){
    std::complex<double> tmp_v=es.eigenvalues()[i];
    data.push_back( std::pair<double,int>( (double)tmp_v.real(), i) );
  }

  std::sort(data.begin(), data.end()); 
  for(it=data.begin(); it!=data.end(); it++){
    ret_lamda.push_back(it->first);
  }

  int index_j=0; 
  for(it=data.begin(); it!=data.end(); it++){
    for(int i=0;i<I;i++){
      int j=it->second;
      std::complex<double> tmp_v=eX(i,j); 
      X_ptr->set_value(i,index_j,tmp_v);
    }
    index_j++;
  }

  
}



template <typename M_tmpl, typename Functor>
void cal_fun_zM(M_tmpl &ret_A, const M_tmpl &A, Functor &functor)
{
  
  using namespace std;
  M_tmpl *A_ptr = const_cast<M_tmpl*>(&A);
  int I=A_ptr->get_I();
  int J=A_ptr->get_J();

  M_tmpl X;
  std::vector<double> lamda;

  cal_z_eigen(A, X, lamda);

  M_tmpl fun_L;
  fun_L.set_IJ(I, J);
  for(int i=0;i<I;i++){
    fun_L.set_value(i, i, functor(lamda[i]));   
  }
  

  M_tmpl X_inv;
  mat_copy(X_inv, X);
  mat_z_inverse(X_inv);
  mat_mul(ret_A, fun_L, X_inv);
  mat_mul(ret_A, X, ret_A);
  

}

struct Functor_sqrt{
  double operator()(double in){ return std::sqrt(in); } 
};


struct Functor_div_sqrt{
  double operator()(double in){ return 1.0/std::sqrt(in); } 
};


template <typename M_tmpl>
void cal_sqrt_zM(M_tmpl &ret_A, const M_tmpl &A)
{
  Functor_sqrt func;
  cal_fun_zM(ret_A, A, func);
}


template <typename M_tmpl>
void cal_div_sqrt_zM(M_tmpl &ret_A, const M_tmpl &A)
{
  Functor_div_sqrt func;
  cal_fun_zM(ret_A, A, func);
}




template <typename M_tmpl, typename U>
void mat_normalize(M_tmpl &X, M_tmpl &S){
  using namespace std;
  int I=S.get_I();
  M_tmpl tmpM;
  mat_mul(tmpM, S, X);
  std::vector<double> nv(S.get_I());
  for(int q=0;q<I;q++){
    U sum=0.0;
    for(int i=0;i<I;i++){
      U tmp_v = X.get_value(i,q)*tmpM.get_value(i,q);
      sum += tmp_v; 
    }
    nv[q]=1.0/std::sqrt( std::abs(sum) );
  }
}

template <typename M_tmpl>
void cal_z_eigen(M_tmpl &A, M_tmpl &S, M_tmpl &X, std::vector<double> &ret_lamda)
{


  using namespace std;
  M_tmpl *A_ptr          = &A;
  int I=A_ptr->get_I();
  int J=A_ptr->get_J();

  M_tmpl S_sqrt_inv;
  cal_div_sqrt_zM(S_sqrt_inv, S);

  M_tmpl A_tilda;
  A_tilda.set_IJ(I, J);
  mat_mul(A_tilda, A, S_sqrt_inv);
  mat_mul(A_tilda, S_sqrt_inv, A_tilda);

  cal_z_eigen(A_tilda, X, ret_lamda);
  mat_mul(X, S_sqrt_inv, X);

  mat_normalize< M_tmpl, std::complex<double> >(X, S); 

}





}  // end of namespace "Lotus_core"

//#include "detail/Matrixs_detail.hpp"

#endif // end of ifndef MATRIXS_TMPL_H
