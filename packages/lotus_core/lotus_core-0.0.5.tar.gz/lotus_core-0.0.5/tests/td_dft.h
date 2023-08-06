

#include "gto.hpp"
#include "Util.hpp"
#include "Fock1e_tmpl.hpp"
#include "Matrixs_tmpl.hpp"
#include "Grid_Inte.hpp"
#include "PInt1e.hpp"

using namespace Lotus_core;

typedef PInt::PInt1e  PInt1e;

int td_dft_mat_base(const char *filename, double exact_v[3], int mode_u, int mode){
  using namespace std;

  vector<Shell_Cgto> scgtos = Util_GTO::get_scgtos_from_file<PInt1e>(filename);
  Fock1e_tmpl<dMatrix_map,PInt1e>  fock1e;
  Grid_Inte<dMatrix_map,PInt1e>           grid_inte;
  dMatrix_map S;
  fock1e.cal_S(S,scgtos);
  dMatrix_map Vxc_a, Vxc_b;
  double ene_dft;

  Slater_Functor Slater_functor;
  B88_Functor    B88_functor;
  SVWN_Functor   SVWN_functor;
  BLYP_Functor   BLYP_functor;
  B3LYP_Functor  B3LYP_functor;

  if(mode_u==0 && mode==0) ene_dft = grid_inte.grid_integral_mat(Vxc_a, S, scgtos, Slater_functor);
  if(mode_u==0 && mode==1) ene_dft = grid_inte.grid_integral_mat(Vxc_a, S, scgtos, B88_functor);
  if(mode_u==0 && mode==2) ene_dft = grid_inte.grid_integral_mat(Vxc_a, S, scgtos, SVWN_functor);
  if(mode_u==0 && mode==3) ene_dft = grid_inte.grid_integral_mat(Vxc_a, S, scgtos, BLYP_functor);
  if(mode_u==0 && mode==4) ene_dft = grid_inte.grid_integral_mat(Vxc_a, S, scgtos, B3LYP_functor);
  if(mode_u==1 && mode==0) ene_dft = grid_inte.grid_integral_mat_u(Vxc_a, Vxc_b, S, S, scgtos, Slater_functor);
  if(mode_u==1 && mode==1) ene_dft = grid_inte.grid_integral_mat_u(Vxc_a, Vxc_b, S, S, scgtos, B88_functor);
  if(mode_u==1 && mode==2) ene_dft = grid_inte.grid_integral_mat_u(Vxc_a, Vxc_b, S, S, scgtos, SVWN_functor);
  if(mode_u==1 && mode==3) ene_dft = grid_inte.grid_integral_mat_u(Vxc_a, Vxc_b, S, S, scgtos, BLYP_functor);
  if(mode_u==1 && mode==4) ene_dft = grid_inte.grid_integral_mat_u(Vxc_a, Vxc_b, S, S, scgtos, B3LYP_functor);

  double svxc_a, svxc_b;
  if(mode_u==0){
   svxc_a = Util::cal_DV(S,Vxc_a);
   svxc_b = svxc_a;
  }else{
   svxc_a = Util::cal_DV(S,Vxc_a);
   svxc_b = Util::cal_DV(S,Vxc_b);
  }


  int ret;
  if(fabs(ene_dft - exact_v[0])>1.0e-8 || fabs(svxc_a - exact_v[1])>1.0e-8 || fabs(svxc_b - exact_v[2])>1.0e-8){
    cout.precision(15);
    cout<<"   -----> error in td_fock1e_K_mat, filename "<<filename<<endl;
    cout<<"     exact_v[0] "<<exact_v[0]<<" ene_dft "<<ene_dft<<" diff "<<exact_v[0]-ene_dft<<endl;
    cout<<"     exact_v[1] "<<exact_v[1]<<" svxc_a  "<<svxc_a <<" diff "<<exact_v[1]-svxc_a<<endl;
    cout<<"     exact_v[2] "<<exact_v[2]<<" svxc_b  "<<svxc_b <<" diff "<<exact_v[2]-svxc_b<<endl;
    ret=1;
  }else{
    ret=0;
  }

  return ret;
}

int td_dft_mat_Slater(int mode_u){
  double exact_v[3];
  exact_v[0] = -8.68918462925892;
  exact_v[1] = -5.79278975283834;
  exact_v[2] = -5.79278975283834;
  return td_dft_mat_base("h2o_sbkjc.mol", exact_v, mode_u, 0);
}

int td_dft_mat_B88(int mode_u){
  double exact_v[3];
  exact_v[0] = -9.2876235408606;
  exact_v[1] = -6.03693727770248;
  exact_v[2] = -6.03693727770248;
  return td_dft_mat_base("h2o_sbkjc.mol", exact_v, mode_u, 1);
}

int td_dft_mat_SVWN(int mode_u){
  double exact_v[3];
  exact_v[0] = -9.87546262859488;
  exact_v[1] = -6.4459186067467;
  exact_v[2] = -6.4459186067467;
  return td_dft_mat_base("h2o_sbkjc.mol", exact_v, mode_u, 2);
}

int td_dft_mat_BLYP(int mode_u){
  double exact_v[3];
  exact_v[0] = -9.77158715290214;
  exact_v[1] = -6.34018173640426;
  exact_v[2] = -6.34018173640426;
  return td_dft_mat_base("h2o_sbkjc.mol", exact_v, mode_u, 3);
}

int td_dft_mat_B3LYP(int mode_u){
  double exact_v[3];
  exact_v[0] = -7.99962706538783;
  exact_v[1] = -5.17974051396373;
  exact_v[2] = -5.17974051396373;
  return td_dft_mat_base("h2o_sbkjc.mol", exact_v, mode_u, 4);
}

//
// plus_d

int td_dft_mat_Slater_d(int mode_u){
  double exact_v[3];
  exact_v[0] = -28.7225990726249;
  exact_v[1] = -19.1483993817468;
  exact_v[2] = -19.1483993817468;
  return td_dft_mat_base("h2o_sbkjc_plus_d.mol", exact_v, mode_u, 0);
}

int td_dft_mat_B88_d(int mode_u){
  double exact_v[3];
  exact_v[0] = -29.8278342726607;
  exact_v[1] = -19.5962495878738;
  exact_v[2] = -19.5962495878738;
  return td_dft_mat_base("h2o_sbkjc_plus_d.mol", exact_v, mode_u, 1);
}


int td_dft_mat_SVWN_d(int mode_u){
  double exact_v[3];
  exact_v[0] = -32.0105268520034;
  exact_v[1] = -20.9500806637708;
  exact_v[2] = -20.9500806637708;
  return td_dft_mat_base("h2o_sbkjc_plus_d.mol", exact_v, mode_u, 2);
}


int td_dft_mat_BLYP_d(int mode_u){
  double exact_v[3];
  exact_v[0] = -31.3144744951157;
  exact_v[1] = -20.4694869661171;
  exact_v[2] = -20.4694869661171;
  return td_dft_mat_base("h2o_sbkjc_plus_d.mol", exact_v, mode_u, 3);
}


int td_dft_mat_B3LYP_d(int mode_u){
  double exact_v[3];
  exact_v[0] = -25.6027334603965;
  exact_v[1] = -16.69081337377;
  exact_v[2] = -16.69081337377;
  return td_dft_mat_base("h2o_sbkjc_plus_d.mol", exact_v, mode_u, 4);
}


//
//  grad
//

int td_dft_grad_base(const char *filename, double exact_v[3], int mode_u, int mode){
  using namespace std;

  vector<Shell_Cgto> scgtos = Util_GTO::get_scgtos_from_file<PInt1e>(filename);
  Fock1e_tmpl<dMatrix_map,PInt1e>  fock1e;
  Grid_Inte<dMatrix_map,PInt1e>    grid_inte;
  dMatrix_map S;
  fock1e.cal_S(S,scgtos);
  vector<double> grad;

  Slater_Functor Slater_functor;
  B88_Functor    B88_functor;
  SVWN_Functor   SVWN_functor;
  BLYP_Functor   BLYP_functor;
  B3LYP_Functor  B3LYP_functor;

  if(mode_u==0 && mode==0) grad=grid_inte.cal_grad(scgtos, S, Slater_functor);
  if(mode_u==0 && mode==1) grad=grid_inte.cal_grad(scgtos, S, B88_functor);
  if(mode_u==0 && mode==2) grad=grid_inte.cal_grad(scgtos, S, SVWN_functor);
  if(mode_u==0 && mode==3) grad=grid_inte.cal_grad(scgtos, S, BLYP_functor);
  if(mode_u==0 && mode==4) grad=grid_inte.cal_grad(scgtos, S, B3LYP_functor);
  if(mode_u==1 && mode==0) grad=grid_inte.cal_grad_u(scgtos, S, S, Slater_functor);
  if(mode_u==1 && mode==1) grad=grid_inte.cal_grad_u(scgtos, S, S, B88_functor);
  if(mode_u==1 && mode==2) grad=grid_inte.cal_grad_u(scgtos, S, S, SVWN_functor);
  if(mode_u==1 && mode==3) grad=grid_inte.cal_grad_u(scgtos, S, S, BLYP_functor);
  if(mode_u==1 && mode==4) grad=grid_inte.cal_grad_u(scgtos, S, S, B3LYP_functor);

  
  std::vector<double> check_v(3, 0.0);
  for(int a=0;a<grad.size()/3;a++){
    check_v[0]+=sqrt(grad[a*3+0]*grad[a*3+0]);
    check_v[1]+=sqrt(grad[a*3+1]*grad[a*3+1]);
    check_v[2]+=sqrt(grad[a*3+2]*grad[a*3+2]);
//    cout<<"a="<<a<<" grad: "<<grad[a*3+0]<<" "<<grad[a*3+1]<<" "<<grad[a*3+2]<<endl;
  }
//  cout<<" check_v "<<check_v[0]<<" "<<check_v[1]<<" "<<check_v[2]<<endl;
   
 
  int ret=1;
  if(fabs(check_v[0]-exact_v[0])>1.0e-12 || fabs(check_v[1]-exact_v[1])>1.0e-12 || fabs(check_v[2]-exact_v[2])>1.0e-12){
    cout.precision(15);
    cout<<"   -----> error in td_fock1e_K_mat, filename "<<filename<<endl;
    cout<<" exact_v[0] "<<exact_v[0]<<" check_v[0] "<<check_v[0]<<" diff "<<exact_v[0]-check_v[0]<<endl;
    cout<<" exact_v[1] "<<exact_v[1]<<" check_v[1] "<<check_v[1]<<" diff "<<exact_v[1]-check_v[1]<<endl;
    cout<<" exact_v[2] "<<exact_v[2]<<" check_v[2] "<<check_v[2]<<" diff "<<exact_v[2]-check_v[2]<<endl;
    ret=1;
  }else{
    ret=0;
  }


  return ret;
}


int td_dft_grad_Slater(int mode_u){
  double exact_v[3];
  exact_v[0] = 1.05296460949943;
  exact_v[1] = 0.0;
  exact_v[2] = 1.55725111110006;
  return td_dft_grad_base("h2o_sbkjc.mol", exact_v, mode_u, 0);
}

int td_dft_grad_B88(int mode_u){
  double exact_v[3];
  exact_v[0] = 1.04847620377321;
  exact_v[1] = 0.0;
  exact_v[2] = 1.56017486613892;
  return td_dft_grad_base("h2o_sbkjc.mol", exact_v, mode_u, 1);
}

int td_dft_grad_SVWN(int mode_u){
  double exact_v[3];
  exact_v[0] = 1.14533141423903;
  exact_v[1] = 0.0;
  exact_v[2] = 1.69443739285219;
  return td_dft_grad_base("h2o_sbkjc.mol", exact_v, mode_u, 2);
}

int td_dft_grad_BLYP(int mode_u){
  double exact_v[3];
  exact_v[0] = 1.10246933713149;
  exact_v[1] = 0.0;
  exact_v[2] = 1.63759463570879;
  return td_dft_grad_base("h2o_sbkjc.mol", exact_v, mode_u, 3);
}

int td_dft_grad_B3LYP(int mode_u){
  double exact_v[3];
  exact_v[0] = 0.900424166397432;
  exact_v[1] = 0.0;
  exact_v[2] = 1.3366813993925;
  return td_dft_grad_base("h2o_sbkjc.mol", exact_v, mode_u, 4);
}

//
//  plus_d
//

int td_dft_grad_Slater_d(int mode_u){
  double exact_v[3];
  exact_v[0] = 2.87484447384673;
  exact_v[1] = 0.0;
  exact_v[2] = 4.16771240491097;
  return td_dft_grad_base("h2o_sbkjc_plus_d.mol", exact_v, mode_u, 0);
}

int td_dft_grad_B88_d(int mode_u){
  double exact_v[3];
  exact_v[0] = 2.91520808450086;
  exact_v[1] = 0.0;
  exact_v[2] = 4.22884556905654;
  return td_dft_grad_base("h2o_sbkjc_plus_d.mol", exact_v, mode_u, 1);
}

int td_dft_grad_SVWN_d(int mode_u){
  double exact_v[3];
  exact_v[0] = 3.08784188862778;
  exact_v[1] = 0.0;
  exact_v[2] = 4.4766019037608;
  return td_dft_grad_base("h2o_sbkjc_plus_d.mol", exact_v, mode_u, 2);
}

int td_dft_grad_BLYP_d(int mode_u){
  double exact_v[3];
  exact_v[0] = 3.02653535330202;
  exact_v[1] = 0.0;
  exact_v[2] = 4.38957440364052;
  return td_dft_grad_base("h2o_sbkjc_plus_d.mol", exact_v, mode_u, 3);
}

int td_dft_grad_B3LYP_d(int mode_u){
  double exact_v[3];
  exact_v[0] = 2.45958197528588;
  exact_v[1] = 0.0;
  exact_v[2] = 3.56706516290775;
  return td_dft_grad_base("h2o_sbkjc_plus_d.mol", exact_v, mode_u, 4);
}

