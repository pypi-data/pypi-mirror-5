

#include "gto.hpp"
#include "Util.hpp"
#include "Fock1e_tmpl.hpp"
#include "Matrixs_tmpl.hpp"
#include "Grid_Inte.hpp"
#include "PInt1e.hpp"

using namespace Lotus_core;

typedef PInt::PInt1e  PInt1e;


int td_dft_pbc_base(const char *filename, double exact_v[10],GInte_Functor &functor){
  using namespace std;

  CTRL_PBC ctrl_pbc;
  std::vector<double> T123(9);
  T123[0]= 1.0;  T123[1]=-0.5;  T123[2]= 0.0;
  T123[3]= 0.0;  T123[4]=-1.5;  T123[5]= 0.0;
  T123[6]= 0.0;  T123[7]= 1.5;  T123[8]= 1.0;
  std::vector<int> max_Nc(3, 0);

  ctrl_pbc.set_T123(T123);
//  ctrl_pbc.show();

  vector<Shell_Cgto> scgtos = Util_GTO::get_scgtos_from_file<PInt1e>(filename);
  Fock1e_tmpl<dMatrix,PInt1e>         fock1e;
  Grid_Inte<dMatrix,PInt1e>           grid_inte;

  vector<dMatrix> S_PBC, Vx_PBC;

  double check_v[10];
   
  max_Nc[0]=0;  max_Nc[1]=0;  max_Nc[2]=0;
  ctrl_pbc.set_max_Nc(max_Nc);
  fock1e.cal_S_PBC(S_PBC,scgtos,ctrl_pbc); 
  check_v[0] = grid_inte.grid_integral_mat_PBC(Vx_PBC, S_PBC, scgtos, ctrl_pbc, functor);
  check_v[1] = Util_PBC::cal_DV(Vx_PBC, S_PBC, ctrl_pbc.get_N123_c() );

  max_Nc[0]=1;  max_Nc[1]=0;  max_Nc[2]=0;
  ctrl_pbc.set_max_Nc(max_Nc);
  fock1e.cal_S_PBC(S_PBC,scgtos,ctrl_pbc); 
  check_v[2] = grid_inte.grid_integral_mat_PBC(Vx_PBC, S_PBC, scgtos, ctrl_pbc, functor);
  check_v[3] = Util_PBC::cal_DV(Vx_PBC, S_PBC, ctrl_pbc.get_N123_c() );
  
  max_Nc[0]=1;  max_Nc[1]=1;  max_Nc[2]=0;
  ctrl_pbc.set_max_Nc(max_Nc);
  fock1e.cal_S_PBC(S_PBC,scgtos,ctrl_pbc); 
  check_v[4] = grid_inte.grid_integral_mat_PBC(Vx_PBC, S_PBC, scgtos, ctrl_pbc, functor);
  check_v[5] = Util_PBC::cal_DV(Vx_PBC, S_PBC, ctrl_pbc.get_N123_c() );

  max_Nc[0]=1;  max_Nc[1]=1;  max_Nc[2]=1;
  ctrl_pbc.set_max_Nc(max_Nc);
  fock1e.cal_S_PBC(S_PBC,scgtos,ctrl_pbc); 
  check_v[6] = grid_inte.grid_integral_mat_PBC(Vx_PBC, S_PBC, scgtos, ctrl_pbc, functor);
  check_v[7] = Util_PBC::cal_DV(Vx_PBC, S_PBC, ctrl_pbc.get_N123_c() );

  max_Nc[0]=0;  max_Nc[1]=2;  max_Nc[2]=2;
  ctrl_pbc.set_max_Nc(max_Nc);
  fock1e.cal_S_PBC(S_PBC,scgtos,ctrl_pbc); 
  check_v[8] = grid_inte.grid_integral_mat_PBC(Vx_PBC, S_PBC, scgtos, ctrl_pbc, functor);
  check_v[9] = Util_PBC::cal_DV(Vx_PBC, S_PBC, ctrl_pbc.get_N123_c() );

  int ret=0;
  double abs_error=1.0e-10;
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



int td_dft_pbc_slater(){
  double exact_v[10]={0.0};
  Slater_Functor Slater_functor;
  B88_Functor    B88_functor;
  SVWN_Functor   SVWN_functor;
  BLYP_Functor   BLYP_functor;
  B3LYP_Functor  B3LYP_functor;
  exact_v[0] = -8.68918462925892;
  exact_v[1] = -5.79278975283924;
  exact_v[2] = -27.9470595016986;
  exact_v[3] = -18.3924381013131;
  exact_v[4] = -68.2891368400923;
  exact_v[5] = -40.7319674149235;
  exact_v[6] = -247.966315093019;
  exact_v[7] = -138.684446232039;
  exact_v[8] = -66.7011109320874;
  exact_v[9] = -44.9884398391664;
  return td_dft_pbc_base("h2o_sbkjc.mol", exact_v, Slater_functor);
}


int td_dft_pbc_svwn(){
  double exact_v[10]={0.0};
  SVWN_Functor   SVWN_functor;
  exact_v[0] = -32.0105268520034;
  exact_v[1] = -20.9500806637737;
  exact_v[2] = -118.27853809234;
  exact_v[3] = -73.9886286096848;
  exact_v[4] = -345.455974988649;
  exact_v[5] = -195.890365412771;
  exact_v[6] = -1259.35881653829;
  exact_v[7] = -674.86594442786;
  exact_v[8] = -360.996815911785;
  exact_v[9] = -240.620223087907;
  return td_dft_pbc_base("h2o_sbkjc_plus_d.mol", exact_v, SVWN_functor);
}


int td_dft_pbc_blyp(){
  double exact_v[10]={0.0};
  BLYP_Functor   BLYP_functor;
  exact_v[0] = -31.3144744951157;
  exact_v[1] = -20.4694869661198;
  exact_v[2] = -115.190027883041;
  exact_v[3] = -72.1824246518356;
  exact_v[4] = -336.759674739418;
  exact_v[5] = -191.604790643238;
  exact_v[6] = -1234.31848438909;
  exact_v[7] = -663.667927459116;
  exact_v[8] = -352.107236868374;
  exact_v[9] = -235.516086217432;
  return td_dft_pbc_base("h2o_sbkjc_plus_d.mol", exact_v, BLYP_functor);
}


int td_dft_pbc_b3lyp(){
  double exact_v[10]={0.0};
  B3LYP_Functor   B3LYP_functor;
  exact_v[0] = -25.6027334603965;
  exact_v[1] = -16.6908133737727;
  exact_v[2] = -93.6980535024515;
  exact_v[3] = -58.5599510952698;
  exact_v[4] = -272.91806864864;
  exact_v[5] = -154.938239837276;
  exact_v[6] = -996.492587711361;
  exact_v[7] = -534.829799499708;
  exact_v[8] = -285.197210945696;
  exact_v[9] = -190.333328397354;
  return td_dft_pbc_base("h2o_sbkjc_plus_d.mol", exact_v, B3LYP_functor);
}



