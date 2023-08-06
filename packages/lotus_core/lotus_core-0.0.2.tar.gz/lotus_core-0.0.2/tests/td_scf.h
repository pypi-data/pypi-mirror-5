

#include "Matrixs_tmpl.hpp"
#include "SCF.hpp"
#include "Fock1e_tmpl.hpp"
#include "Fock2e_tmpl.hpp"
#include "Util.hpp"
#include "PInt1e.hpp"
#include "PInt2e.hpp"

#include <string>

using namespace Lotus_core;
typedef PInt::PInt1e PInt1e;
typedef PInt::PInt2e PInt2e;

template <typename select_ERI>
int td_scf_base(const char *filename, double exact_v[2], int mode, select_ERI &sel_eri, GInte_Functor &functor)
{
  using namespace std;

  vector<Shell_Cgto> scgtos = Util_GTO::get_scgtos_from_file<PInt1e>(filename);
  vector<ECP> ecps          = ECP::get_ecps_from_file(filename);

  Fock1e_tmpl<dMatrix_map,PInt1e>         fock1e;
  SCF<PInt1e,PInt2e>                      scf;

  dMatrix_map S, checkM_a, checkM_b;
  std::vector<double> lamda;
  double check_a, check_b;

  double abs_error=1.0e-8;

  fock1e.cal_S(S,scgtos);
  if(mode==0){ // cal_h_core
    scf.cal_h_core(checkM_a, scgtos, ecps);
    check_a = Util::cal_DV(S,checkM_a);
    check_b = 0.0;
  }
  if(mode==1){ // guess_h_core
    scf.guess_h_core(checkM_a, lamda, scgtos, ecps);
    std::vector<double> occ = Util::cal_occ(scgtos, ecps, 0, 1);
    check_a=0.0; 
    for(int i=0;i<lamda.size();i++) check_a+=sqrt(lamda[i]*lamda[i]);
    dMatrix_map D;
    Util::cal_D(D, checkM_a, occ);
    check_b = Util::cal_DV(S,D);
  }
  if(mode==2){  // cal_Fock_sub
    scf.prepare_eri<dMatrix_map,select_ERI>(sel_eri, scgtos);
    scf.cal_Fock_sub(checkM_a, S, scgtos, sel_eri, functor);

    check_a = Util::cal_DV(S, checkM_a);
    check_b = 0.0;
  }
  if(mode==3){  // r_scf
    MolData moldata;
    moldata.set_basis_from_file<PInt1e>(filename);
    scf.guess_h_core(checkM_a, lamda, moldata.scgtos, moldata.ecps);
    scf.r_scf(checkM_a, lamda, moldata, sel_eri, functor);
    abs_error=1.0e-5;
    check_a = scf.get_ene_total();
    check_b=0.0; 
    for(int i=0;i<lamda.size();i++) check_b+=sqrt(lamda[i]*lamda[i]);

  }
  if(mode==4){  // cal_Fock_sub_u
    scf.prepare_eri<dMatrix_map,select_ERI>(sel_eri, scgtos);
    scf.cal_Fock_sub_u(checkM_a, checkM_b, S, S, scgtos, sel_eri, functor);
    check_a = Util::cal_DV(S, checkM_a);
    check_b = Util::cal_DV(S, checkM_b);
  }
  if(mode==5){  // u_scf
    MolData moldata;
    moldata.set_basis_from_file<PInt1e>(filename);
    scf.guess_h_core(checkM_a, lamda, moldata.scgtos, moldata.ecps);
    checkM_b=checkM_a;
    std::vector<double> lamda_a, lamda_b;

    scf.u_scf(checkM_a, checkM_b, lamda_a, lamda_b, moldata, sel_eri, functor);
    abs_error=1.0e-5;
    check_a = scf.get_ene_total();
    check_b=0.0; 
    for(int i=0;i<lamda.size();i++) check_b+=sqrt(lamda_a[i]*lamda_a[i]);

  }
  if(mode==6){  // r_scf, ediis
    MolData moldata;
    moldata.set_basis_from_file<PInt1e>(filename);
    scf.guess_h_core(checkM_a, lamda, moldata.scgtos, moldata.ecps);
    scf.do_ediis();
    scf.r_scf(checkM_a, lamda, moldata, sel_eri, functor);
    abs_error=1.0e-5;
    check_a = scf.get_ene_total();
    check_b=0.0; 
    for(int i=0;i<lamda.size();i++) check_b+=sqrt(lamda[i]*lamda[i]);

  }
  if(mode==7){  // u_scf, ediis
    MolData moldata;
    moldata.set_basis_from_file<PInt1e>(filename);
    scf.guess_h_core(checkM_a, lamda, moldata.scgtos, moldata.ecps);
    checkM_b=checkM_a;
    std::vector<double> lamda_a, lamda_b;

    scf.do_ediis();
    scf.u_scf(checkM_a, checkM_b, lamda_a, lamda_b, moldata, sel_eri, functor);
    abs_error=1.0e-5;
    check_a = scf.get_ene_total();
    check_b=0.0; 
    for(int i=0;i<lamda.size();i++) check_b+=sqrt(lamda_a[i]*lamda_a[i]);

  }
  
  
  int ret;
  if(fabs(check_a - exact_v[0])>abs_error || fabs(check_b - exact_v[1])>abs_error){
    cout.precision(15);
    cout<<"   -----> error in td_scf_base, filename "<<filename<<endl;
    cout<<"     exact_v[0] "<<exact_v[0]<<" check_a "<<check_a<<" diff "<<exact_v[0]-check_a<<endl;
    cout<<"     exact_v[1] "<<exact_v[1]<<" check_b "<<check_b<<" diff "<<exact_v[1]-check_b<<endl;
    ret=1;
  }else{
    ret=0;
  }

  return ret;
}



int td_h_core(){
  double exact_v[2];
  exact_v[0] = -35.78070460897100;
  exact_v[1] =   0.00000000000000;
  ERI_direct dmy;
  HF_Functor functor;
  return td_scf_base("h2o_sbkjc.mol", exact_v, 0, dmy, functor);
}


int td_h_core_d(){
  double exact_v[2];
  exact_v[0] = -83.2612514756841;
  exact_v[1] =   0.0000000000000;
  ERI_direct dmy;
  HF_Functor functor;
  return td_scf_base("h2o_sbkjc_plus_d.mol", exact_v, 0, dmy, functor);
}


int td_guess_h_core(){
  double exact_v[2];
  exact_v[0] =  29.374285177441323;
  exact_v[1] =   4.000000000000000;
  ERI_direct dmy;
  HF_Functor functor;
  return td_scf_base("h2o_sbkjc.mol", exact_v, 1, dmy, functor);
}


int td_guess_h_core_d(){
  double exact_v[2];
  exact_v[0] =  43.520839858474474; 
  exact_v[1] =   4.000000000000000;
  ERI_direct dmy;
  HF_Functor functor;
  return td_scf_base("h2o_sbkjc_plus_d.mol", exact_v, 1, dmy, functor);
}

//
//  fock_sub

int td_fock_sub_hf(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] =  56.2569474715606;
    exact_v[1] =   0.000000000000000;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = 358.004821713946512;
    exact_v[1] =   0.000000000000000;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  HF_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 2, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 2, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 2, eri_incore, functor);
  }
}


int td_fock_sub_slater(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] = 63.7215726251014;
    exact_v[1] = 0.0;
    filename   = "h2o_sbkjc.mol";
  }else{
     exact_v[0] = 421.3833226925;
     exact_v[1] = 0.0;
    filename    = "h2o_sbkjc_plus_d.mol";
  }
  Slater_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 2, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 2, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 2, eri_incore, functor);
  }
}


int td_fock_sub_svwn(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] = 63.0684437711931;
    exact_v[1] = 0.0;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = 419.581641410476;
    exact_v[1] =    0.000000000000000;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  SVWN_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 2, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 2, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 2, eri_incore, functor);
  }
}


int td_fock_sub_b3lyp(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] = 61.6831388827002;
    exact_v[1] =   0.000000000000000;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = 407.335528628417;
    exact_v[1] =    0.000000000000000;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  B3LYP_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 2, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 2, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 2, eri_incore, functor);
  }
}

//
//  r_scf

int td_scf_hf(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] = -15.997926929989090;
    exact_v[1] =   4.074002074868483;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = -16.049785900583380; 
    exact_v[1] =  23.509691116412167;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  HF_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 3, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 3, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 3, eri_incore, functor);
  }
}


int td_scf_svwn(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] = -16.31968247914776;
    exact_v[1] =   3.021254946143811;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = -16.38449153649990;
    exact_v[1] =  19.61019670025221;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  SVWN_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 3, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 3, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 3, eri_incore, functor);
  }
}


int td_scf_b88(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] = -1.604226179160642e+01;
    exact_v[1] = 3.061640994030337e+00;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = -1.609867110753819e+01;
    exact_v[1] =  1.999830828181901e+01;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  B88_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 3, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 3, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 3, eri_incore, functor);
  }
}


int td_scf_blyp(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] = -1.628869168612131e+01;
    exact_v[1] =  2.994283808452439e+00;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = -1.634477586490963e+01;
    exact_v[1] =  1.972139477046332e+01;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  BLYP_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 3, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 3, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 3, eri_incore, functor);
  }
}


int td_scf_b3lyp(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] = -1.632746012006390e+01;
    exact_v[1] =  3.122207493754346e+00;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = -1.638284192429592e+01;
    exact_v[1] =  2.028712129082399e+01;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  B3LYP_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 3, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 3, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 3, eri_incore, functor);
  }
}


//
//  fock_sub_u

int td_fock_sub_hf_u(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] =  56.2569474715606;
    exact_v[1] =  56.2569474715606;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = 358.004821713946512;
    exact_v[1] = 358.004821713946512;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  HF_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 4, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 4, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 4, eri_incore, functor);
  }
}


int td_fock_sub_b3lyp_u(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] = 61.6831388827002;
    exact_v[1] = 61.6831388827002;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = 407.335528628417;
    exact_v[1] = 407.335528628417;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  B3LYP_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 4, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 4, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 4, eri_incore, functor);
  }
}

//
// u_scf

int td_scf_hf_u(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] = -15.997926929989090;
    exact_v[1] =   4.074002074868483;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = -16.049785900583380; 
    exact_v[1] =  23.509691116412167;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  HF_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 5, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 5, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 5, eri_incore, functor);
  }
}


int td_scf_svwn_u(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] = -16.31968247914776;
    exact_v[1] =   3.021254946143811;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = -16.38449153649990;
    exact_v[1] =  19.61019670025221;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  SVWN_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 5, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 5, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 5, eri_incore, functor);
  }
}


int td_scf_b88_u(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] = -1.604226179160642e+01;
    exact_v[1] = 3.061640994030337e+00;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = -1.609867110753819e+01;
    exact_v[1] =  1.999830828181901e+01;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  B88_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 5, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 5, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 5, eri_incore, functor);
  }
}


int td_scf_blyp_u(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] = -1.628869168612131e+01;
    exact_v[1] =  2.994283808452439e+00;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = -1.634477586490963e+01;
    exact_v[1] =  1.972139477046332e+01;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  BLYP_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 5, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 5, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 5, eri_incore, functor);
  }
}


int td_scf_b3lyp_u(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] = -1.632746012006390e+01;
    exact_v[1] =  3.122207493754346e+00;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = -1.638284192429592e+01;
    exact_v[1] =  2.028712129082399e+01;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  B3LYP_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 5, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 5, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 5, eri_incore, functor);
  }
}


//
//  r_scf_ediis

int td_scf_hf_ediis(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] = -15.997926929989090;
    exact_v[1] =   4.074002074868483;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = -16.049785900583380; 
    exact_v[1] =  23.509691116412167;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  HF_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 6, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 6, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 6, eri_incore, functor);
  }
}


int td_scf_hf_ediis_u(int mode, int mode_d){
  using namespace std;
  double exact_v[2];
  string filename;
  if(mode_d==0){
    exact_v[0] = -15.997926929989090;
    exact_v[1] =   4.074002074868483;
    filename   = "h2o_sbkjc.mol";
  }else{
    exact_v[0] = -16.049785900583380; 
    exact_v[1] =  23.509691116412167;
    filename   = "h2o_sbkjc_plus_d.mol";
  }
  HF_Functor functor;
  if(mode==0){
    ERI_direct eri_direct;
    return td_scf_base(filename.c_str(), exact_v, 7, eri_direct, functor);
  }else if(mode==1){
    ERI_file eri_file;
    return td_scf_base(filename.c_str(), exact_v, 7, eri_file, functor);
  }else{
    ERI_incore eri_incore;
    return td_scf_base(filename.c_str(), exact_v, 7, eri_incore, functor);
  }
}

