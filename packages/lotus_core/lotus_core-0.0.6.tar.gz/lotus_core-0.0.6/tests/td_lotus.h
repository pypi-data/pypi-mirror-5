

#include "Mixin_core.hpp"
#include "Matrixs_tmpl.hpp"
#include "PInt1e.hpp"
#include "PInt2e.hpp"



#include <string>

using namespace Lotus_core;

typedef dMatrix M_tmpl;
typedef PInt::PInt1e PInt1e;
typedef PInt::PInt2e PInt2e;

template <typename select_ERI>
int td_lotus_base(const char *filename, double exact_v[10], int mode, GInte_Functor &functor)
{
  using namespace std;
  Lotus_class<M_tmpl,PInt1e,PInt2e> lts;
  lts.read_in_file(filename);
  M_tmpl S;
  lts.cal_matrix("S", S);  
  lts.guess_h_core();


  double check_v[10]={0.0};
  double abs_error=1.0e-8;
  if(mode==0){
    M_tmpl K, NA, ecpM, H_core, D, D_a, D_b;
    lts.cal_matrix("K", K); 
    lts.cal_matrix("NA", NA); 
    lts.cal_matrix("ECP", ecpM); 
    lts.cal_matrix("H_core", H_core); 
    lts.cal_matrix("D", D); 
    lts.cal_matrix("D_a", D_a); 
    check_v[0] = lts.get_N_cgtos();
    check_v[1] = lts.get_N_ecps();
    check_v[2] = lts.get_N_atoms();
    check_v[3] = Util::cal_DV(S,K); 
    check_v[4] = Util::cal_DV(S,NA); 
    check_v[5] = Util::cal_DV(S,ecpM); 
    check_v[6] = Util::cal_DV(S,H_core); 
    check_v[7] = Util::cal_DV(S,D); 
    check_v[8] = Util::cal_DV(S,D_a); 
  }
  if(mode==1){
    lts.guess_h_core();
    lts.scf<select_ERI>(functor);
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


  }

  
  int ret;
  if(fabs(check_v[0] - exact_v[0])>abs_error || fabs(check_v[1] - exact_v[1])>abs_error ||
     fabs(check_v[2] - exact_v[2])>abs_error || fabs(check_v[3] - exact_v[3])>abs_error ||
     fabs(check_v[4] - exact_v[4])>abs_error || fabs(check_v[5] - exact_v[5])>abs_error ||
     fabs(check_v[6] - exact_v[6])>abs_error || fabs(check_v[7] - exact_v[7])>abs_error ||
     fabs(check_v[8] - exact_v[8])>abs_error || fabs(check_v[9] - exact_v[9])>abs_error){
    cout.precision(15);
    cout<<"   -----> error in td_scf_base, filename "<<filename<<endl;
    cout<<"     exact_v[0] "<<exact_v[0]<<" check_v[0] "<<check_v[0]<<" diff "<<exact_v[0]-check_v[0]<<endl;
    cout<<"     exact_v[1] "<<exact_v[1]<<" check_v[1] "<<check_v[1]<<" diff "<<exact_v[1]-check_v[1]<<endl;
    cout<<"     exact_v[2] "<<exact_v[2]<<" check_v[2] "<<check_v[2]<<" diff "<<exact_v[2]-check_v[2]<<endl;
    cout<<"     exact_v[3] "<<exact_v[3]<<" check_v[3] "<<check_v[3]<<" diff "<<exact_v[3]-check_v[3]<<endl;
    cout<<"     exact_v[4] "<<exact_v[4]<<" check_v[4] "<<check_v[4]<<" diff "<<exact_v[4]-check_v[4]<<endl;
    cout<<"     exact_v[5] "<<exact_v[5]<<" check_v[5] "<<check_v[5]<<" diff "<<exact_v[5]-check_v[5]<<endl;
    cout<<"     exact_v[6] "<<exact_v[6]<<" check_v[5] "<<check_v[6]<<" diff "<<exact_v[6]-check_v[6]<<endl;
    cout<<"     exact_v[7] "<<exact_v[7]<<" check_v[5] "<<check_v[7]<<" diff "<<exact_v[7]-check_v[7]<<endl;
    cout<<"     exact_v[8] "<<exact_v[8]<<" check_v[5] "<<check_v[8]<<" diff "<<exact_v[8]-check_v[8]<<endl;
    cout<<"     exact_v[9] "<<exact_v[9]<<" check_v[5] "<<check_v[9]<<" diff "<<exact_v[9]-check_v[9]<<endl;
    ret=1;
  }else{
    ret=0;
  }

  return ret;

}



int td_lotus_matrix(){
  double exact_v[10]={0.0};
  exact_v[0] =  12.0;
  exact_v[1] =   2.0;
  exact_v[2] =   3.0;
  exact_v[3] =  35.305943879326982;
  exact_v[4] =-120.209150645409;
  exact_v[5] =   1.64195529039806;
  exact_v[6] = -83.2612514756841;
  exact_v[7] =   4.0;
  exact_v[8] =   4.0;
  HF_Functor functor;
  return td_lotus_base<ERI_direct>("h2o_sbkjc_plus_d.in", exact_v, 0, functor);
}


int td_lotus_scf(){
  double exact_v[10]={0.0};
  exact_v[0] = -1.638284192429845e+01;
  exact_v[1] =  2.516472743173441e-01;
  exact_v[2] =  1.374635307336817e-14;
  exact_v[3] =  2.974812044609201e-01;
  B3LYP_Functor functor;
  return td_lotus_base<ERI_incore>("h2o_sbkjc_plus_d.in", exact_v, 1, functor);
}












