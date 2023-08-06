




#ifdef USE_MKL_LAPACK_LIB
#include <mkl.h>
#define DOUBLE_COMPLEX_LOTUS_ MKL_Complex16
#define REAL_LOTUS_ real
#define IMAG_LOTUS_ imag
#define INTEGER_LOTUS_ int
#endif

#ifdef USE_CLAPACK_LIB
#include <stdlib.h>
extern "C" {
#include "f2c.h"
#include "blaswrap.h"
#include "clapack.h"
#undef long
#undef abs
#undef min
#undef max
}
#define DOUBLE_COMPLEX_LOTUS_ doublecomplex
#define REAL_LOTUS_ r
#define IMAG_LOTUS_ i
#define INTEGER_LOTUS_ integer
#endif

#ifdef USE_LAPACK_LIB
extern "C" {
#include "Lotus_lapack.h"
}
#define DOUBLE_COMPLEX_LOTUS_ doublecomplex_lotus
#define REAL_LOTUS_ r
#define IMAG_LOTUS_ i
#define INTEGER_LOTUS_ integer
#endif



#include <iostream>
#include "Matrixs_tmpl.h"

namespace Lotus_core {
using namespace std;

void mat_inverse(dMatrix_base &m){

  INTEGER_LOTUS_ I=(INTEGER_LOTUS_)m.get_I();
  INTEGER_LOTUS_ J=(INTEGER_LOTUS_)m.get_J();
  INTEGER_LOTUS_ lda=I;
  INTEGER_LOTUS_ lwork=4*I;
  INTEGER_LOTUS_ info;
 
  INTEGER_LOTUS_ *ipiv = new INTEGER_LOTUS_ [I];
  double *work         = new double[lwork];
  double *mat          = new double [I*J];

  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      mat[j*I+i]=m.get_value(i,j);
    }
  } 

  #ifdef USE_MKL_LAPACK_LIB
  dgetrf(&I,&J,mat,&lda,ipiv,&info);
  #else
  dgetrf_(&I,&J,mat,&lda,ipiv,&info);
  #endif
  if(info!=0){
    std::cout<<" CAUTION!!!!!!!  info="<<info<<" in dgetrf of dMatrix::inverse "<<std::endl;
    exit(1);
  }
  #ifdef USE_MKL_LAPACK_LIB
  dgetri(&I,mat,&lda,ipiv,work,&lwork,&info);
  #else
  dgetri_(&I,mat,&lda,ipiv,work,&lwork,&info);
  #endif
  if(info!=0){
    std::cout<<" CAUTION!!!!!!!  info="<<info<<" in dgetri of dMatrix::inverse "<<std::endl;
    exit(1);
  }

  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      m.set_value(i,j,mat[j*I+i]);
    }
  }

  delete [] ipiv;
  delete [] work;
  delete [] mat;


}

//   solve equations  AX=B  (X=A^-1 B)
int call_dgesv(Matrix_base<double> &A,Matrix_base<double> &X,Matrix_base<double> &B){
  INTEGER_LOTUS_ N;
  INTEGER_LOTUS_ nrhs;
  double *mat_A;
  INTEGER_LOTUS_ lda;
  INTEGER_LOTUS_ *ipiv;
  double *mat_B;
  INTEGER_LOTUS_ ldb;
  INTEGER_LOTUS_ info;

  N=(INTEGER_LOTUS_)A.get_I();
  nrhs=(INTEGER_LOTUS_)B.get_J();
  mat_A = new double[N*N];
  mat_B = new double[N*N];

  for(int i=0;i<N;i++){
    for(int j=0;j<N;j++){
      mat_A[j*N+i]=A.get_value(i,j);
      mat_B[j*N+i]=B.get_value(i,j);
    }
  }

  lda=N;
  ipiv = new INTEGER_LOTUS_ [N];
  ldb=N;
  
  #ifdef USE_MKL_LAPACK_LIB
  dgesv(&N,&nrhs,mat_A,&lda,ipiv,mat_B,&ldb,&info);
  #else
  dgesv_(&N,&nrhs,mat_A,&lda,ipiv,mat_B,&ldb,&info);
  #endif

  if(info!=0){
    std::cout<<" CAUTION!!!!!!!  info="<<info<<" in call_dgesv "<<std::endl;
    exit(1);
  }

  int x_I=X.get_I();
  int x_J=X.get_J();
  X.set_IJ(x_I, x_J);
  for(int i=0;i<x_I;i++){
    for(int j=0;j<x_J;j++){
      X.set_value(i,j,mat_B[j*N+i]);
    }
  }
  
  delete [] mat_A;
  delete [] mat_B;
  delete [] ipiv;

  return (int) info;
}

// Ax = lamda x: obtain eigene value and eigene vector
int call_dsyev(Matrix_base<double> &A,Matrix_base<double> &X,std::vector<double> &ret_lamda){
  char jobz='V';
  char uplo='U';
  INTEGER_LOTUS_ N=(INTEGER_LOTUS_)A.get_I();
  INTEGER_LOTUS_ lda=N;
  INTEGER_LOTUS_ lwork=4*N;
  INTEGER_LOTUS_ info;

  double *mat_X = new double[N*N];
  double *work  = new double[lwork];
  double *lamda = new double [N];

  for(int i=0;i<N;i++){
    for(int j=0;j<N;j++){
      mat_X[j*N+i]=A.get_value(i,j);
    }
  }
  
  #ifdef USE_MKL_LAPACK_LIB
  dsyev(&jobz,&uplo,&N,mat_X,&lda,lamda,work,&lwork,&info);
  #else
  dsyev_(&jobz,&uplo,&N,mat_X,&lda,lamda,work,&lwork,&info);
  #endif
  
  X.set_IJ(N, N);
  ret_lamda.resize(N, 0.0);
  for(int i=0;i<N;i++){
    for(int j=0;j<N;j++){
      X.set_value(i,j,mat_X[j*N+i]);
    }
    ret_lamda[i]=lamda[i];
  }

  delete [] lamda;
  delete [] work;
  delete [] mat_X; 
  return (int) info;  
}




// obtain eigene valeu and vector for Ax=lamda Sx
int call_dsygv(Matrix_base<double> &A,Matrix_base<double> &S,Matrix_base<double> &X,std::vector<double> &ret_lamda){

  INTEGER_LOTUS_ itype=1;
  char jobz='V';
  char uplo='U';
  INTEGER_LOTUS_ N=(INTEGER_LOTUS_)A.get_I();
  INTEGER_LOTUS_ lda=N;
  INTEGER_LOTUS_ ldb=N;
  INTEGER_LOTUS_ lwork=4*N+100;
  INTEGER_LOTUS_ info;

  double *mat_X        = new double[N*N];
  double *mat_B_half   = new double[N*N];
  double *lamda        = new double [N];
  double *work         = new double[lwork];

  for(int i=0;i<N;i++){
    for(int j=0;j<N;j++){
      mat_X[j*N+i]     =A.get_value(i,j);
      mat_B_half[j*N+i]=S.get_value(i,j);
    }
  }

  #ifdef USE_MKL_LAPACK_LIB
  dsygv(&itype,&jobz,&uplo,&N,mat_X,&lda,mat_B_half,&ldb,lamda,work,&lwork,&info);
  #else
  dsygv_(&itype,&jobz,&uplo,&N,mat_X,&lda,mat_B_half,&ldb,lamda,work,&lwork,&info);
  #endif
        
  if(info!=0){
    std::cout<<"   ********* caution in call_dsygv info="<<info<<std::endl;
  }

  X.set_IJ(N, N);
  ret_lamda.resize(N, 0.0);
  for(int i=0;i<N;i++){
    for(int j=0;j<N;j++){
      X.set_value(i,j,mat_X[j*N+i]);
    }
    ret_lamda[i]=lamda[i];
  }

  delete [] mat_X;
  delete [] mat_B_half;
  delete [] lamda;
  delete [] work;

  return (int) info;
}  


}  // end of namespace "Lotus_core"
//template void mat_inverse<dMatrix_base>(dMatrix_base &m);
//template class Matrix_base<double>;
