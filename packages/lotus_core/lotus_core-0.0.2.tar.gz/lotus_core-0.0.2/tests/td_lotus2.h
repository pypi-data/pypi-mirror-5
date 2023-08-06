

#include "Mixin_core.hpp"
#include "Matrixs_tmpl.hpp"
#include "PInt1e.hpp"
#include "PInt2e.hpp"



#include <string>

using namespace Lotus_core;

typedef dMatrix M_tmpl;
typedef PInt::PInt1e PInt1e;
typedef PInt::PInt2e PInt2e;



template <typename M_tmpl,typename Integ1e,typename Integ2e>
class Lotus2: public Mixin_core< Lotus2<M_tmpl,Integ1e,Integ2e>,M_tmpl,Integ1e,Integ2e > {
public:
  SCF<Integ1e,Integ2e>        scf_class;
  double ene_total;
  MolData moldata;
  M_tmpl X_a, X_b;
  std::vector<double> lamda_a, lamda_b;


  template <typename select_ERI>
  void r_scf2(GInte_Functor &functor){
    select_ERI sel_eri;
    SCF<Integ1e,Integ2e> scf;
    scf.mix_dens=1.0;
    scf.r_scf(X_a, lamda_a, moldata, sel_eri, functor);
    ene_total=scf.get_ene_total();
  }


  
};




template <typename select_ERI>
int td_lotus_base2(const char *filename, double exact_v[10], GInte_Functor &functor)
{
  using namespace std;
  Lotus2<M_tmpl,PInt1e,PInt2e> lts;
  lts.read_in_file(filename);
  M_tmpl S;
  lts.cal_matrix("S", S);  
  lts.guess_h_core();


  double check_v[10]={0.0};
  double abs_error=1.0e-8;
  lts.guess_h_core();
  lts.r_scf2<select_ERI>(functor);
  check_v[0]=lts.ene_total;
  std::vector<double> force = lts.cal_force(functor);

  int process_num = Util_MPI::get_mpi_rank();
  cout<<" process_num "<<process_num<<" force "<<force.size()<<endl;

  if(process_num==0) cout<<"      force  "<<endl;
  for(int a=0;a<force.size()/3;a++){
    if(process_num==0) cout<<" a="<<a<<" "<<force[a*3+0]<<" "<<force[a*3+1]<<" "<<force[a*3+2]<<endl;
    check_v[1]+=sqrt(force[a*3+0]*force[a*3+0]);
    check_v[2]+=sqrt(force[a*3+1]*force[a*3+1]);
    check_v[3]+=sqrt(force[a*3+2]*force[a*3+2]);
  }

  
  int ret;
  if(fabs(check_v[0] - exact_v[0])>abs_error || fabs(check_v[1] - exact_v[1])>abs_error ||
     fabs(check_v[2] - exact_v[2])>abs_error || fabs(check_v[3] - exact_v[3])>abs_error ||
     fabs(check_v[4] - exact_v[4])>abs_error || fabs(check_v[5] - exact_v[5])>abs_error ||
     fabs(check_v[6] - exact_v[6])>abs_error || fabs(check_v[7] - exact_v[7])>abs_error ||
     fabs(check_v[8] - exact_v[8])>abs_error || fabs(check_v[9] - exact_v[9])>abs_error){
    cout.precision(15);
    cout<<"   -----> error in td_scf_base, filename "<<filename<<endl;
    cout<<"  exact_v[0] "<<exact_v[0]<<" check_v[0] "<<check_v[0]<<" diff "<<exact_v[0]-check_v[0]<<endl;
    cout<<"  exact_v[1] "<<exact_v[1]<<" check_v[1] "<<check_v[1]<<" diff "<<exact_v[1]-check_v[1]<<endl;
    cout<<"  exact_v[2] "<<exact_v[2]<<" check_v[2] "<<check_v[2]<<" diff "<<exact_v[2]-check_v[2]<<endl;
    cout<<"  exact_v[3] "<<exact_v[3]<<" check_v[3] "<<check_v[3]<<" diff "<<exact_v[3]-check_v[3]<<endl;
    cout<<"  exact_v[4] "<<exact_v[4]<<" check_v[4] "<<check_v[4]<<" diff "<<exact_v[4]-check_v[4]<<endl;
    cout<<"  exact_v[5] "<<exact_v[5]<<" check_v[5] "<<check_v[5]<<" diff "<<exact_v[5]-check_v[5]<<endl;
    cout<<"  exact_v[6] "<<exact_v[6]<<" check_v[5] "<<check_v[6]<<" diff "<<exact_v[6]-check_v[6]<<endl;
    cout<<"  exact_v[7] "<<exact_v[7]<<" check_v[5] "<<check_v[7]<<" diff "<<exact_v[7]-check_v[7]<<endl;
    cout<<"  exact_v[8] "<<exact_v[8]<<" check_v[5] "<<check_v[8]<<" diff "<<exact_v[8]-check_v[8]<<endl;
    cout<<"  exact_v[9] "<<exact_v[9]<<" check_v[5] "<<check_v[9]<<" diff "<<exact_v[9]-check_v[9]<<endl;
    ret=1;
  }else{
    ret=0;
  }

  return ret;

}



int td_lotus_scf_hcch_hf(){
  double exact_v[10]={0.0};
  HF_Functor functor;
  exact_v[0] = -7.680140602139556e+01;
  exact_v[1] =  0.0;
  exact_v[2] =  0.0;
  exact_v[3] =  2.849170884926731e-01;
  return td_lotus_base2<ERI_incore>("hcch_6-31gs.in", exact_v, functor);
}


int td_lotus_scf_hcch_svwn(){
  double exact_v[10]={0.0};
  SVWN_Functor functor;
  exact_v[0] = -7.683983310700512e+01;
  exact_v[1] =  0.0;
  exact_v[2] =  0.0;
  exact_v[3] =  2.756369560779042e-01; 
  return td_lotus_base2<ERI_incore>("hcch_6-31gs.in", exact_v, functor);
}


int td_lotus_scf_hcch_b88(){
  double exact_v[10]={0.0};
  B88_Functor functor;
  exact_v[0] = -7.683293574418317e+01;
  exact_v[1] =  0.0;
  exact_v[2] =  0.0;
  exact_v[3] =  2.719936081708922e-01;
  return td_lotus_base2<ERI_incore>("hcch_6-31gs.in", exact_v, functor);
}


int td_lotus_scf_hcch_b3lyp(){
  double exact_v[10]={0.0};
  B3LYP_Functor functor;
  exact_v[0] = -7.731144645033552e+01;
  exact_v[1] =  0.0;
  exact_v[2] =  0.0;
  exact_v[3] =  2.730583258161785e-01;
  return td_lotus_base2<ERI_incore>("hcch_6-31gs.in", exact_v, functor);
}



int td_lotus_scf_alanine_hf(){
  double exact_v[10]={0.0};
  HF_Functor functor;
  exact_v[0] = -2.481285984093691e+02;
  exact_v[1] =  8.330032027968924e-02;
  exact_v[2] =  1.256274027153565e-01;
  exact_v[3] =  6.616315844422377e-02;
  return td_lotus_base2<ERI_incore>("alanine_6-31gs.in", exact_v, functor);
}


int td_lotus_scf_alanine_b3lyp(){
  double exact_v[10]={0.0};
  B3LYP_Functor functor;
  exact_v[0] = -2.496889632812021e+02;
  exact_v[1] =  4.761406741095729e-02;
  exact_v[2] =  5.353982718038575e-02;
  exact_v[3] =  4.609678623533991e-02;
  return td_lotus_base2<ERI_incore>("alanine_6-31gs.in", exact_v, functor);
}



int td_lotus_scf_benzene_hf(){
  double exact_v[10]={0.0};
  HF_Functor functor;
  exact_v[0] = -2.306870098715535e+02;
  exact_v[1] =  4.608961796313462e-01;
  exact_v[2] =  3.991697000901296e-01;
  exact_v[3] =  4.798649697481912e-14;
  return td_lotus_base2<ERI_incore>("benzene_6-31gs.in", exact_v, functor);
}


int td_lotus_scf_benzene_b3lyp(){
  double exact_v[10]={0.0};
  B3LYP_Functor functor;
  exact_v[0] = -2.322297719351925e+02;
  exact_v[1] =  4.628016024795332e-01;
  exact_v[2] =  4.008556467263605e-01;
  exact_v[3] =  0.0;
  return td_lotus_base2<ERI_incore>("benzene_6-31gs.in", exact_v, functor);
}

