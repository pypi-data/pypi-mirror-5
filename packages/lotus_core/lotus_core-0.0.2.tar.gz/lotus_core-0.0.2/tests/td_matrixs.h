

#include "Mixin_core.hpp"
#include "PInt.hpp"

using namespace Lotus_core;

typedef PInt::PInt1e  PInt1e;
typedef PInt::PInt2e  PInt2e;


template <typename M_tmpl, typename U>
double check_M(M_tmpl &A, M_tmpl &X, std::vector<double> lamda)
{
  using namespace std;
  int N_cgtos = lamda.size();
  std::vector<U> Ax(N_cgtos);

  double abs_error=0.0;
  for(int q=0;q<N_cgtos;q++){
    for(int i=0;i<N_cgtos;i++){
      U tmp_v_i=0.0;
      for(int j=0;j<N_cgtos;j++){
        tmp_v_i+=A.get_value(i, j)*X.get_value(j,q);
      } 
      Ax[i]=tmp_v_i;
    }

    for(int i=0;i<N_cgtos;i++){
      std::complex<double> tmp_c = Ax[i] - lamda[q]*X.get_value(i,q);
      abs_error +=std::abs(tmp_c);
    } 

  }

  return abs_error;
}


template <typename M_tmpl>
double check_M2(M_tmpl &A, M_tmpl &B){
  int I=A.get_I();
  int J=A.get_J();
  double abs_error=0.0;
  for(int i=0;i<I;i++){
    for(int j=0;j<J;j++){
      complex<double> tmp_v = A.get_value(i,j) - B.get_value(i,j);
      abs_error += std::abs(tmp_v);
    }
  }

  return abs_error;
}


template <typename M_tmpl, typename U>
double check_M2(M_tmpl &A, M_tmpl &S, M_tmpl &X, std::vector<double> lamda)
{
  using namespace std;
  int N_cgtos = lamda.size();
  std::vector<U> Ax(N_cgtos);

  M_tmpl SX;
  mat_mul(SX, S, X);

  double abs_error=0.0;
  for(int q=0;q<N_cgtos;q++){
    for(int i=0;i<N_cgtos;i++){
      U tmp_v_i=0.0;
      for(int j=0;j<N_cgtos;j++){
        tmp_v_i+=A.get_value(i, j)*X.get_value(j,q);
      } 
      Ax[i]=tmp_v_i;
    }

    for(int i=0;i<N_cgtos;i++){
      std::complex<double> tmp_c = Ax[i] - lamda[q]*SX.get_value(i,q);
      abs_error +=std::abs(tmp_c);
    } 

  }

  return abs_error;
}




int td_matrix_base(const char *filename, double exact_v[10]){
  using namespace std;

  Lotus_class<dMatrix_map,PInt1e,PInt2e>    lotus;
  dMatrix_map S, H_core, X;
  std::vector<double> lamda;
  
  double check_v[10]={0.0};

  lotus.read_in_file(filename);
  lotus.cal_matrix("S", S);
  lotus.cal_matrix("H_core", H_core);

  zMatrix_map zS, zH_core, zX;

  mat_copy(zS, S);
  mat_copy(zH_core, H_core);


  cal_eigen(H_core, X, lamda);
  check_v[0] = check_M<dMatrix_map, double>(H_core, X, lamda); 

  cal_z_eigen(zH_core, zX, lamda);
  check_v[1] = check_M<zMatrix_map, std::complex<double> >(zH_core, zX, lamda); 

  zMatrix_map zS_sqrt, debug_zM;
  cal_sqrt_zM(zS_sqrt, zS);
  mat_mul(debug_zM, zS_sqrt, zS_sqrt);
  check_v[2] = check_M2(zS, debug_zM);
  
  cal_eigen(H_core, S, X, lamda);
  check_v[3] = check_M2<dMatrix_map, double>(H_core, S, X, lamda);

  cal_z_eigen(zH_core, zS, zX, lamda);
  check_v[4] = check_M2<zMatrix_map, std::complex<double> >(zH_core, zS, zX, lamda);


  int ret=0;
  double abs_error=5.0e-11;
  if(fabs(check_v[0] - exact_v[0])>abs_error || fabs(check_v[1] - exact_v[1])>abs_error ||
     fabs(check_v[2] - exact_v[2])>abs_error || fabs(check_v[3] - exact_v[3])>abs_error ||
     fabs(check_v[4] - exact_v[4])>abs_error || fabs(check_v[5] - exact_v[5])>abs_error ||
     fabs(check_v[6] - exact_v[6])>abs_error || fabs(check_v[7] - exact_v[7])>abs_error ||
     fabs(check_v[8] - exact_v[8])>abs_error || fabs(check_v[9] - exact_v[9])>abs_error){
    ret=1;
    cout.precision(15);
    cout<<"  exact_v[0] "<<exact_v[0]<<" check_v "<<check_v[0]<<" diff "<<exact_v[0]-check_v[0]<<endl; 
    cout<<"  exact_v[1] "<<exact_v[1]<<" check_v "<<check_v[1]<<" diff "<<exact_v[1]-check_v[1]<<endl; 
    cout<<"  exact_v[2] "<<exact_v[2]<<" check_v "<<check_v[2]<<" diff "<<exact_v[2]-check_v[2]<<endl; 
    cout<<"  exact_v[3] "<<exact_v[3]<<" check_v "<<check_v[3]<<" diff "<<exact_v[3]-check_v[3]<<endl; 
    cout<<"  exact_v[4] "<<exact_v[4]<<" check_v "<<check_v[4]<<" diff "<<exact_v[4]-check_v[4]<<endl; 
    cout<<"  exact_v[5] "<<exact_v[5]<<" check_v "<<check_v[5]<<" diff "<<exact_v[5]-check_v[5]<<endl; 
    cout<<"  exact_v[6] "<<exact_v[6]<<" check_v "<<check_v[6]<<" diff "<<exact_v[6]-check_v[6]<<endl; 
    cout<<"  exact_v[7] "<<exact_v[7]<<" check_v "<<check_v[7]<<" diff "<<exact_v[7]-check_v[7]<<endl; 
    cout<<"  exact_v[8] "<<exact_v[8]<<" check_v "<<check_v[8]<<" diff "<<exact_v[8]-check_v[8]<<endl; 
    cout<<"  exact_v[9] "<<exact_v[9]<<" check_v "<<check_v[9]<<" diff "<<exact_v[9]-check_v[9]<<endl; 
  }

  return ret;

}



int td_matrix(){
  double exact_v[10]={0.0};
  return td_matrix_base("h2o_sbkjc_plus_d.in", exact_v);
}

