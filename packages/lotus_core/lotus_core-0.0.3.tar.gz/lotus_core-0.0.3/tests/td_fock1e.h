
#include "gto.hpp"
#include "Util.hpp"
#include "Fock1e_tmpl.hpp"
#include "ECP_tmpl.hpp"
#include "Matrixs_tmpl.hpp"
#include "PInt1e.hpp"
#include "Util.hpp"


#include <math.h>

#include <iostream>
#include <vector>

using namespace Lotus_core;

typedef PInt::PInt1e PInt1e;

int td_fock1e_K_mat_base(const char *filename, double exact_v){
  using namespace std;

  vector<Shell_Cgto> scgtos = Util_GTO::get_scgtos_from_file<PInt1e>(filename);
  Fock1e_tmpl<dMatrix_map,PInt1e> fock1e;
  dMatrix_map S, K;
  fock1e.cal_S(S,scgtos);
  fock1e.cal_K(K,scgtos);
  double sk = Util::cal_DV(S,K);
 
 
  int ret;
  if(fabs(sk - exact_v)>1.0e-13){
    cout<<"   -----> error in td_fock1e_K_mat, filename "<<filename<<" exact_v "<<exact_v<<" sk "<<sk<<endl;
    ret=1;
  }else{
    ret=0;
  }

  return ret;
}

int td_fock1e_K_mat(){
  return td_fock1e_K_mat_base("h2o_sbkjc.mol",15.209924623687);
}


int td_fock1e_K_mat2(){
  return td_fock1e_K_mat_base("h2o_sbkjc_plus_d.mol",35.305943879327);
}


int td_fock1e_NA_mat_base(const char *filename, double exact_v){
  using namespace std;

  vector<Shell_Cgto> scgtos = Util_GTO::get_scgtos_from_file<PInt1e>(filename);
  Fock1e_tmpl<dMatrix_map,PInt1e> fock1e;
  dMatrix_map S, NA;

  std::vector<Charge> charges;
  charges.push_back(Charge(1, 0.1,  0.2,  0.3,  0));
  charges.push_back(Charge(2, 1.0,  1.1,  1.2,  1));

  fock1e.cal_S(S,scgtos);
  fock1e.cal_NA(NA,scgtos,charges);


  double sna = Util::cal_DV(S,NA);
  cout.precision(15);
 
 
  int ret;
  if(fabs(sna - exact_v)>1.0e-13){
    cout<<"   -----> error in td_fock1e_NA_mat, filename "<<filename<<" exact_v "<<exact_v<<" sna "<<sna<<endl;
    ret=1;
  }else{
    ret=0;
  }

  return ret;
}

int td_fock1e_NA_mat(){
  return td_fock1e_NA_mat_base("h2o_sbkjc.mol",-14.6450507433424);
}


int td_fock1e_NA_mat2(){
  return td_fock1e_NA_mat_base("h2o_sbkjc_plus_d.mol",-35.5342442165267);
}




int td_fock1e_ECP_mat_base(const char *filename,double exact_v){
  using namespace std;

  vector<Shell_Cgto> scgtos = Util_GTO::get_scgtos_from_file<PInt1e>(filename);
  vector<ECP>        ecps   = ECP::get_ecps_from_file(filename);
  Fock1e_tmpl<dMatrix_map,PInt1e> fock1e;
  dMatrix_map S, M_ecp;

  fock1e.cal_S(S,scgtos);
  ECP_matrix<dMatrix_map,PInt1e>().cal_ECP(M_ecp,scgtos,ecps);
  double secp = Util::cal_DV(S,M_ecp);

  int ret;
  if(fabs(secp - exact_v)>1.0e-13){
    cout<<"   -----> error in td_fock1e_ECP_mat, filename "<<filename<<" exact_v "<<exact_v<<" secp "<<secp<<endl;
    ret=1;
  }else{
    ret=0;
  }

  return ret;

}


int td_fock1e_ECP_mat(){
  return td_fock1e_ECP_mat_base("h2o_sbkjc.mol",0.668115104438203);
}


int td_fock1e_ECP_mat2(){
  return td_fock1e_ECP_mat_base("h2o_sbkjc_plus_d.mol",1.64195529039806);
}


//
//  gradient
//





int td_fock1e_grad_base(const char *filename, double exact_v[3],int mode){
  using namespace std;

  vector<Shell_Cgto> scgtos = Util_GTO::get_scgtos_from_file<PInt1e>(filename);
  vector<ECP> ecps = ECP::get_ecps_from_file(filename);
  Fock1e_tmpl<dMatrix_map,PInt1e> fock1e;
  ECP_matrix<dMatrix_map,PInt1e>  ecp_mat;
  dMatrix_map S;
  fock1e.cal_S(S,scgtos);
  vector<double> grad;

  std::vector<Charge> charges;
  charges.push_back(Charge(1, 0.1,  0.2,  0.3,  0));
  charges.push_back(Charge(2, 1.0,  1.1,  1.2,  1));

  if(mode==0) grad = fock1e.cal_grad_S(scgtos,S);
  if(mode==1) grad = fock1e.cal_grad_K(scgtos,S);
  if(mode==2) grad = fock1e.cal_grad_NA(scgtos,S,charges);
  if(mode==3) grad = ecp_mat.cal_grad_ECP(scgtos,ecps,S);

  double check_v[3]={0.0, 0.0, 0.0};
  for(int a=0;a<grad.size()/3;a++){
    check_v[0]+=sqrt(grad[a*3+0]*grad[a*3+0]);
    check_v[1]+=sqrt(grad[a*3+1]*grad[a*3+1]);
    check_v[2]+=sqrt(grad[a*3+2]*grad[a*3+2]);
//    cout<<"a="<<a<<" grad: "<<grad[a*3+0]<<" "<<grad[a*3+1]<<" "<<grad[a*3+2]<<endl;
  }
//  cout<<" check_v "<<check_v[0]<<" "<<check_v[1]<<" "<<check_v[2]<<endl;
   
 
  int ret=1;
  if(fabs(check_v[0] - exact_v[0])>1.0e-13 ||
     fabs(check_v[1] - exact_v[1])>1.0e-13 ||
     fabs(check_v[2] - exact_v[2])>1.0e-13){
    cout<<"   -----> error in td_fock1e_K_mat, filename "<<filename<<endl;
    cout<<" exact_v[0] "<<exact_v[0]<<" check_v[0] "<<check_v[0]<<endl;
    cout<<" exact_v[1] "<<exact_v[1]<<" check_v[1] "<<check_v[1]<<endl;
    cout<<" exact_v[2] "<<exact_v[2]<<" check_v[2] "<<check_v[2]<<endl;
    ret=1;
  }else{
    ret=0;
  }

  return ret;
}




int td_fock1e_grad_S(){
  double exact_v[3];
  exact_v[0]=0.797858610874905;
  exact_v[1]=0.0;
  exact_v[2]=1.19156682184131;
  return td_fock1e_grad_base("h2o_sbkjc.mol",exact_v,0);
}


int td_fock1e_grad_S2(){
  double exact_v[3];
  exact_v[0]=1.76573600226019;
  exact_v[1]=0.0;
  exact_v[2]=2.55888122805177;
  return td_fock1e_grad_base("h2o_sbkjc_plus_d.mol",exact_v,0);
}



int td_fock1e_grad_K(){
  double exact_v[3];
  exact_v[0]=1.25963801096052;
  exact_v[1]=0.0;
  exact_v[2]=1.91082703634836;
  return td_fock1e_grad_base("h2o_sbkjc.mol",exact_v,1);
}


int td_fock1e_grad_K2(){
  double exact_v[3];
  exact_v[0]=3.20462307132361;
  exact_v[1]=0.0;
  exact_v[2]=4.67643987627959;
  return td_fock1e_grad_base("h2o_sbkjc_plus_d.mol",exact_v,1);
}


int td_fock1e_grad_NA(){
  double exact_v[3];
  exact_v[0]=3.89035924054393;
  exact_v[1]=5.48287225486067;
  exact_v[2]=6.43108061233738;
  return td_fock1e_grad_base("h2o_sbkjc.mol",exact_v,2);
}

int td_fock1e_grad_NA2(){
  double exact_v[3];
  exact_v[0]=9.73663174932849;
  exact_v[1]=12.7737287310335;
  exact_v[2]=16.1902064506491;
  return td_fock1e_grad_base("h2o_sbkjc_plus_d.mol",exact_v,2);
}


int td_fock1e_grad_ECP(){
  double exact_v[3];
  exact_v[0]=0.435739119392969;
  exact_v[1]=0.0;
  exact_v[2]=0.657556467625155;
  return td_fock1e_grad_base("h2o_sbkjc.mol",exact_v,3);
}


int td_fock1e_grad_ECP2(){
  double exact_v[3];
  exact_v[0]=0.581764645449941;
  exact_v[1]=0.0;
  exact_v[2]=0.877934978556851;
  return td_fock1e_grad_base("h2o_sbkjc_plus_d.mol",exact_v,3);
}


//
//  PBC
//


int td_fock1e_pbc_base(const char *filename, double exact_v,int mode){
  using namespace std;

  CTRL_PBC ctrl_pbc;
  std::vector<double> T123(9);
  T123[0]= 1.0;  T123[1]=-0.5;  T123[2]= 0.0;
  T123[3]= 0.0;  T123[4]=-1.5;  T123[5]= 0.0;
  T123[6]= 0.0;  T123[7]= 1.5;  T123[8]= 1.0;
  std::vector<int> max_Nc(3, 0);
  max_Nc[0]=1;
  max_Nc[1]=2;
  max_Nc[2]=1;
  std::vector<int> max_Nt(3, 0);
  max_Nt[0]=2;
  max_Nt[1]=2;
  max_Nt[2]=2;
  ctrl_pbc.set_T123(T123);
  ctrl_pbc.set_max_Nc(max_Nc);
  ctrl_pbc.set_max_Nt(max_Nt);
//  ctrl_pbc.show();

  std::vector<Charge> charges;
  charges.push_back(Charge(1, 0.1,  0.2,  0.3,  0));
  charges.push_back(Charge(2, 1.0,  1.1,  1.2,  1));

  vector<Shell_Cgto> scgtos = Util_GTO::get_scgtos_from_file<PInt1e>(filename);
  vector<ECP> ecps = ECP::get_ecps_from_file("h2o_sbkjc.mol");
  Fock1e_tmpl<dMatrix_map,PInt1e> fock1e;
  ECP_matrix<dMatrix_map,PInt1e> ecp_mat;
  vector<dMatrix_map> S_PBC, K_PBC, NA_PBC, ECP_PBC;
   
  fock1e.cal_S_PBC(S_PBC,scgtos,ctrl_pbc); 
  if(mode==0) fock1e.cal_K_PBC(K_PBC, scgtos, ctrl_pbc); 
  if(mode==1) fock1e.cal_NA_PBC(NA_PBC, scgtos, charges, ctrl_pbc); 
  if(mode==2) ecp_mat.cal_ECP_PBC(ECP_PBC, scgtos, ecps, ctrl_pbc);

  int N123_c = ctrl_pbc.get_N123_c();
  double check_v;
  if(mode==0) check_v = Util_PBC::cal_DV(S_PBC, K_PBC, N123_c);
  if(mode==1) check_v = Util_PBC::cal_DV(S_PBC, NA_PBC, N123_c);
  if(mode==2) check_v = Util_PBC::cal_DV(S_PBC, ECP_PBC, N123_c);
/*
  for(int i=0;i<N123_c;i++){
    cout<<" ----- i="<<i<<" ECP ----"<<endl;
    ECP_PBC[i].show();
  }
*/

  int ret;
  if(fabs(check_v - exact_v)>1.0e-10){
    cout<<"   -----> error in td_fock1e_pbc_base, filename "<<filename<<" exact_v "<<exact_v<<" check_v "<<check_v<<endl;
    ret=1;
  }else{
    ret=0;
  }

  return ret;

}

int td_fock1e_K_PBC(){
  return td_fock1e_pbc_base("h2o_sbkjc.mol", 57.266002474008, 0);
}


int td_fock1e_K_PBC2(){
  return td_fock1e_pbc_base("h2o_sbkjc_plus_d.mol", 202.146619381262, 0);
}


int td_fock1e_NA_PBC(){
  return td_fock1e_pbc_base("h2o_sbkjc.mol", -4711.62478666429, 1);
}

int td_fock1e_NA_PBC2(){
  return td_fock1e_pbc_base("h2o_sbkjc_plus_d.mol", -15073.7573775886, 1);
}

int td_fock1e_ECP_PBC(){
  return td_fock1e_pbc_base("h2o_sbkjc.mol", 165.112814886142, 2);
}


int td_fock1e_ECP_PBC2(){
  return td_fock1e_pbc_base("h2o_sbkjc_plus_d.mol", 644.769597094371, 2);
}



