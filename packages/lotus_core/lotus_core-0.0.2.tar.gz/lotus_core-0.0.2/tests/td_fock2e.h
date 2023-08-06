
#include "gto.hpp"
#include "Util.hpp"
#include "Fock1e_tmpl.hpp"
#include "Fock2e_tmpl.hpp"
#include "Matrixs_tmpl.hpp"
#include "PInt1e.hpp"
#include "PInt2e.hpp"
#include "Util.hpp"


#include <math.h>

#include <iostream>
#include <vector>

using namespace Lotus_core;
typedef PInt::PInt1e PInt1e;
typedef PInt::PInt2e PInt2e;

int td_fock2e_Vh_and_Vx_base(const char *filename, double exact_v[3], int mode_u, int mode){
  using namespace std;

  vector<Shell_Cgto> scgtos = Util_GTO::get_scgtos_from_file<PInt1e>(filename);
  Fock1e_tmpl<dMatrix_map,PInt1e> fock1e;
  Fock2e_tmpl<dMatrix_map,PInt2e> fock2e;
  dMatrix_map S;
  fock1e.cal_S(S,scgtos);
  dMatrix_map Vh, Vx_a, Vx_b;

  ERI_file   eri_file;
  ERI_incore eri_incore;
  if(mode==1) fock2e.prepare_eri(eri_file,   scgtos);
  if(mode==2) fock2e.prepare_eri(eri_incore, scgtos);

  if(mode_u==0 && mode==0) fock2e.cal_Vh_and_Vx(Vh, Vx_a, S, scgtos, ERI_direct() ); 
  if(mode_u==0 && mode==1) fock2e.cal_Vh_and_Vx(Vh, Vx_a, S, scgtos, eri_file ); 
  if(mode_u==0 && mode==2) fock2e.cal_Vh_and_Vx(Vh, Vx_a, S, scgtos, eri_incore ); 
  if(mode_u==1 && mode==0) fock2e.cal_Vh_and_Vx_u(Vh, Vx_a, Vx_b, S, S, scgtos, ERI_direct() ); 
  if(mode_u==1 && mode==1) fock2e.cal_Vh_and_Vx_u(Vh, Vx_a, Vx_b, S, S, scgtos, eri_file ); 
  if(mode_u==1 && mode==2) fock2e.cal_Vh_and_Vx_u(Vh, Vx_a, Vx_b, S, S, scgtos, eri_incore ); 

  double svh, svh_b, svx_a, svx_b;
  if(mode_u==0){
   svh   = Util::cal_DV(S,Vh);
   svx_a = Util::cal_DV(S,Vx_a);
   svx_b = svx_a;
  }else{
   svh   = Util::cal_DV(S,Vh);
   svx_a = Util::cal_DV(S,Vx_a);
   svx_b = Util::cal_DV(S,Vx_b);
  }

  int ret;
  if(fabs(svh   - exact_v[0])>1.0e-12 ||
     fabs(svx_a - exact_v[1])>1.0e-12 || fabs(svx_b - exact_v[2])>1.0e-12){
    cout.precision(15);
    cout<<"   -----> error in td_fock1e_K_mat, filename "<<filename<<endl;
    cout<<"     exact_v[0] "<<exact_v[0]<<" svh   "<<svh  <<" diff "<<exact_v[0]-svh  <<endl;
    cout<<"     exact_v[1] "<<exact_v[1]<<" svx_a "<<svx_a<<" diff "<<exact_v[1]-svx_a<<endl;
    cout<<"     exact_v[2] "<<exact_v[2]<<" svx_b "<<svx_b<<" diff "<<exact_v[2]-svx_b<<endl;
    ret=1;
  }else{
    ret=0;
  }

  return ret;
}


int td_fock2e_Vh_and_Vx_mat(int mode_u, int mode){
  double check_v[3];
  check_v[0]=69.514362377939790;
  check_v[1]=-13.257414906379237;
  check_v[2]=-13.257414906379237;
  return td_fock2e_Vh_and_Vx_base("h2o_sbkjc.mol", check_v, mode_u, mode);
}



int td_fock2e_Vh_and_Vx_mat2(int mode_u, int mode){
  double check_v[3];
  check_v[0]=440.531722074247114;
  check_v[1]=-82.526900360300203;
  check_v[2]=-82.526900360300203;
  return td_fock2e_Vh_and_Vx_base("h2o_sbkjc_plus_d.mol", check_v, mode_u, mode);
}



int td_fock2e_grad_base(const char *filename, double exact_v_h[3],double exact_v_x[3],int mode_u){
  using namespace std;

  vector<Shell_Cgto> scgtos = Util_GTO::get_scgtos_from_file<PInt1e>(filename);
  Fock1e_tmpl<dMatrix_map,PInt1e> fock1e;
  Fock2e_tmpl<dMatrix_map,PInt2e> fock2e;
  dMatrix_map S;
  fock1e.cal_S(S,scgtos);
  vector<double> grad_h, grad_x;


  if(mode_u==0) fock2e.cal_grad(grad_h, grad_x, scgtos, S);
  if(mode_u==1) fock2e.cal_grad_u(grad_h, grad_x, scgtos, S, S);

  
  std::vector<double> check_v_h(3, 0.0), check_v_x(3, 0.0);
  for(int a=0;a<grad_h.size()/3;a++){
    check_v_h[0]+=sqrt(grad_h[a*3+0]*grad_h[a*3+0]);
    check_v_h[1]+=sqrt(grad_h[a*3+1]*grad_h[a*3+1]);
    check_v_h[2]+=sqrt(grad_h[a*3+2]*grad_h[a*3+2]);
    check_v_x[0]+=sqrt(grad_x[a*3+0]*grad_x[a*3+0]);
    check_v_x[1]+=sqrt(grad_x[a*3+1]*grad_x[a*3+1]);
    check_v_x[2]+=sqrt(grad_x[a*3+2]*grad_x[a*3+2]);
//    cout<<"a="<<a<<" grad_h: "<<grad_h[a*3+0]<<" "<<grad_h[a*3+1]<<" "<<grad_h[a*3+2]
//                 <<" grad_x: "<<grad_x[a*3+0]<<" "<<grad_x[a*3+1]<<" "<<grad_x[a*3+2]<<endl;
  }
//  cout<<" check_v_h "<<check_v_h[0]<<" "<<check_v_h[1]<<" "<<check_v_h[2]
//      <<" check_v_x "<<check_v_x[0]<<" "<<check_v_x[1]<<" "<<check_v_x[2]<<endl;
   
 
  int ret=1;
  if(fabs(check_v_h[0]-exact_v_h[0])>1.0e-13 || fabs(check_v_h[1]-exact_v_h[1])>1.0e-13 || fabs(check_v_h[2]-exact_v_h[2])>1.0e-13 ||
     fabs(check_v_x[0]-exact_v_x[0])>1.0e-13 || fabs(check_v_x[1]-exact_v_x[1])>1.0e-13 || fabs(check_v_x[2]-exact_v_x[2])>1.0e-13){
    cout.precision(15);
    cout<<"   -----> error in td_fock1e_K_mat, filename "<<filename<<endl;
    cout<<" exact_v_h[0] "<<exact_v_h[0]<<" check_v_h[0] "<<check_v_h[0]<<endl;
    cout<<" exact_v_h[1] "<<exact_v_h[1]<<" check_v_h[1] "<<check_v_h[1]<<endl;
    cout<<" exact_v_h[2] "<<exact_v_h[2]<<" check_v_h[2] "<<check_v_h[2]<<endl;
    cout<<" exact_v_x[0] "<<exact_v_x[0]<<" check_v_x[0] "<<check_v_x[0]<<endl;
    cout<<" exact_v_x[1] "<<exact_v_x[1]<<" check_v_x[1] "<<check_v_x[1]<<endl;
    cout<<" exact_v_x[2] "<<exact_v_x[2]<<" check_v_x[2] "<<check_v_x[2]<<endl;
    ret=1;
  }else{
    ret=0;
  }


  return ret;
}

int td_fock2e_grad(int mode_u){
  double check_v_h[3], check_v_x[3];
  check_v_h[0]=13.5690070385031;
  check_v_h[1]=0.0;
  check_v_h[2]=18.791046595282;
  check_v_x[0]=3.37495707732413;
  check_v_x[1]=0.0;
  check_v_x[2]=4.90195505988168;
  return td_fock2e_grad_base("h2o_sbkjc.mol", check_v_h, check_v_x, mode_u);
}


int td_fock2e_grad2(int mode_u){
  double check_v_h[3], check_v_x[3];
  check_v_h[0]=61.2241334993477;
  check_v_h[1]=0.0;
  check_v_h[2]=86.6223405609601;
  check_v_x[0]=16.1830503526459;
  check_v_x[1]=0.0;
  check_v_x[2]=23.2646314515965;
  return td_fock2e_grad_base("h2o_sbkjc_plus_d.mol", check_v_h, check_v_x, mode_u);
}





