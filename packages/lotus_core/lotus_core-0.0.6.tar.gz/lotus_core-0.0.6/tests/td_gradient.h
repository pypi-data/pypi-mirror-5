


#include "Matrixs_tmpl.hpp"
#include "SCF.hpp"
#include "Fock1e_tmpl.hpp"
#include "Fock2e_tmpl.hpp"
#include "Util.hpp"
#include "Gradient.hpp"
#include "PInt1e.hpp"
#include "PInt2e.hpp"

#include <string>

using namespace Lotus_core;
typedef PInt::PInt1e PInt1e;
typedef PInt::PInt2e PInt2e;

int td_grad_base(const char *filename, double exact_v[3], int mode_u, GInte_Functor &functor)
{
  using namespace std;
  
  int process_num = Util_MPI::get_mpi_rank();

  vector<Shell_Cgto> scgtos = Util_GTO::get_scgtos_from_file<PInt1e>(filename);
  vector<ECP> ecps          = ECP::get_ecps_from_file(filename);

  Fock1e_tmpl<dMatrix_map,PInt1e>         fock1e;
  SCF<PInt1e,PInt2e>                      scf;
  Gradient<PInt1e,PInt2e>                 grad;

  dMatrix_map S, X_a, X_b;
  std::vector<double> lamda;
  double check_v[3]={0.0, 0.0, 0.0};

  double abs_error=1.0e-7;
  if(mode_u==0){  // r_scf
    MolData moldata;
    moldata.set_basis_from_file<PInt1e>(filename);
    scf.guess_h_core(X_a, lamda, moldata.scgtos, moldata.ecps);
    ERI_direct eri_direct;
    scf.r_scf(X_a, lamda, moldata, eri_direct, functor);

    std::vector<double> occ = Util::cal_occ(scgtos, ecps, 0, 1);
    std::vector<double> force = grad.cal_force(moldata.scgtos, moldata.ecps, X_a, occ, lamda, functor); 
  
    if(process_num==0) cout<<"      force  "<<endl;
    for(int a=0;a<force.size()/3;a++){
      check_v[0]+=sqrt(force[a*3+0]*force[a*3+0]);
      check_v[1]+=sqrt(force[a*3+1]*force[a*3+1]);
      check_v[2]+=sqrt(force[a*3+2]*force[a*3+2]);
      if(process_num==0) cout<<" a="<<a<<" "<<force[a*3+0]<<" "<<force[a*3+1]<<" "<<force[a*3+2]<<endl;
    }
     
  }

  if(mode_u==1){  // u_scf
    MolData moldata;
    moldata.set_basis_from_file<PInt1e>(filename);
    scf.guess_h_core(X_a, lamda, moldata.scgtos, moldata.ecps);
    X_b=X_a;
    std::vector<double> lamda_a, lamda_b;
    ERI_direct eri_direct;
    scf.u_scf(X_a, X_b, lamda_a, lamda_b, moldata, eri_direct, functor);

    std::vector<double> occ_a, occ_b;
    Util::cal_occ_ab(occ_a, occ_b, moldata.scgtos, moldata.ecps, moldata.mol_charge, moldata.spin);
    std::vector<double> force = grad.cal_force_u(moldata.scgtos, moldata.ecps, X_a, X_b, occ_a, occ_b, lamda_a, lamda_b, functor);
 
    if(process_num==0) cout<<"      force  "<<endl;
    for(int a=0;a<force.size()/3;a++){
      if(process_num==0) cout<<" a="<<a<<" "<<force[a*3+0]<<" "<<force[a*3+1]<<" "<<force[a*3+2]<<endl;
      check_v[0]+=sqrt(force[a*3+0]*force[a*3+0]);
      check_v[1]+=sqrt(force[a*3+1]*force[a*3+1]);
      check_v[2]+=sqrt(force[a*3+2]*force[a*3+2]);
    }
  }

  
  int ret=0;
  if(fabs(check_v[0] - exact_v[0])>abs_error || fabs(check_v[1] - exact_v[1])>abs_error || fabs(check_v[2] - exact_v[2])>abs_error){
    if(process_num==0){
      cout<<"   -----> error in td_grad_base, filename "<<filename<<endl;
      cout.precision(15);
      cout<<"     exact_v[0] "<<exact_v[0]<<" check_v[0] "<<check_v[0]<<" diff "<<exact_v[0]-check_v[0]<<endl;
      cout<<"     exact_v[1] "<<exact_v[1]<<" check_v[1] "<<check_v[1]<<" diff "<<exact_v[1]-check_v[1]<<endl;
      cout<<"     exact_v[2] "<<exact_v[2]<<" check_v[2] "<<check_v[2]<<" diff "<<exact_v[2]-check_v[2]<<endl;
    }
    ret=1;
  }

  return ret;

}


int td_grad_hf(int mode_u){
  double exact_v[3];
  exact_v[0] =   0.3493498502009253;
  exact_v[1] =   0.0000000000000000;
  exact_v[2] =   0.4544301004312827;
  HF_Functor functor;
  return td_grad_base("h2o_sbkjc.mol", exact_v, mode_u, functor);
}


int td_grad_hf_d(int mode_u){
  double exact_v[3];
  exact_v[0] =   0.3427749363440474;
  exact_v[1] =   0.0000000000000000;
  exact_v[2] =   0.4309958979772428;
  HF_Functor functor;
  return td_grad_base("h2o_sbkjc_plus_d.mol", exact_v, mode_u, functor);
}



int td_grad_svwn(int mode_u){
  double exact_v[3];
  exact_v[0] = 2.405923838182816e-01;
  exact_v[1] = 1.871035635904355e-16;
  exact_v[2] = 2.895087230952800e-01;
  SVWN_Functor functor;
  return td_grad_base("h2o_sbkjc.mol", exact_v, mode_u, functor);
}


int td_grad_svwn_d(int mode_u){
  double exact_v[3];
  exact_v[0] = 2.448015576864108e-01;
  exact_v[1] = 1.141218317447252e-15;
  exact_v[2] = 2.818207168152005e-01;
  SVWN_Functor functor;
  return td_grad_base("h2o_sbkjc_plus_d.mol", exact_v, mode_u, functor);
}


int td_grad_blyp_d(int mode_u){
  double exact_v[3];
  exact_v[0] = 2.220973708021526e-01;
  exact_v[1] = 1.383643614355288e-15;
  exact_v[2] = 2.539773201615168e-01;
  BLYP_Functor functor;
  return td_grad_base("h2o_sbkjc_plus_d.mol", exact_v, mode_u, functor);
}


int td_grad_b3lyp_d(int mode_u){
  double exact_v[3];
  exact_v[0] = 2.516472744362920e-01;
  exact_v[1] = 1.467998644063969e-14;
  exact_v[2] = 2.974812046657984e-01;
  B3LYP_Functor functor;
  return td_grad_base("h2o_sbkjc_plus_d.mol", exact_v, mode_u, functor);
}

