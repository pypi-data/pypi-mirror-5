


#ifndef ECP_H
#define ECP_H

#include "gto.hpp"
#include "Util_PBC.hpp"
#include "Util_MPI.hpp"

#include <vector>
#include <iostream>

namespace Lotus_core {

class ECP{

  struct GKD {
    double g;
    int k;
    double d;
    GKD(double in_g,int in_k,double in_d){
      g=in_g;
      k=in_k;
      d=in_d;
    }
  };

  int atom_no;
  int core_ele;
  int L;
  double C[3];
  std::vector<GKD> gkd;
public:

  void show() const {
    std::cout<<"atom_no, "<<atom_no<<" L "<<L<<" core_ele "<<core_ele<<std::endl;
    std::cout<<"C[3]  "<<C[0]<<" "<<C[1]<<" "<<C[2]<<std::endl;
    std::cout<<"   g,k,d"<<std::endl;
    for(int j=0;j<gkd.size();j++){
      std::cout<<"   "<<gkd[j].g<<"  "<<gkd[j].k<<"  "<<gkd[j].d<<std::endl;
    }

  }

  void set_L(int in_L){  L=in_L; }
  
  void set_atom_no(int in_atom_no){
    atom_no=in_atom_no;
  }
  void set_C(std::vector<double> &in_C){
    C[0]=in_C[0];
    C[1]=in_C[1];
    C[2]=in_C[2];
  }
  void set_core_ele(int in_core_ele){ core_ele=in_core_ele; }

  void clear_gkd(){ gkd.clear(); }
  void set_gkd(double in_g,int in_k,double in_d){
    gkd.push_back(GKD(in_g,in_k,in_d));
  }

  int get_num_pc() const {return gkd.size();}
  int get_L() const {return L;}
  int get_atom_no() const {return atom_no;}
  int get_core_ele() const {return core_ele; }
  std::vector<double> get_C() const {
    std::vector<double> retC;
    retC.push_back(C[0]);
    retC.push_back(C[1]);
    retC.push_back(C[2]);
    return retC;
  }
  double get_nth_g(int nth) const {return gkd[nth].g;}
  int    get_nth_k(int nth) const {return gkd[nth].k;}
  double get_nth_d(int nth) const {return gkd[nth].d;}

  inline static std::vector<ECP> get_ecps_from_string(const char *qm_string);
  inline static std::vector<ECP> get_ecps_from_file(const char *filename);

  inline static int get_core_ele_from_ecps(const std::vector<ECP> &ecps,int in_atom_no){
    int ret=0;
    for(int i=0;i<ecps.size();i++){
      if(in_atom_no == ecps[i].get_atom_no()){
        ret=ecps[i].get_core_ele();
      }
    }
    return ret; 
  }

  bool operator==(const ECP &in){
    if((void*)this==(void*)&in) return true;
    else                        return false;
  }
};


class RealSphericalHarmonic{
  int num[7][13];
  int r[7][13][11];
  int s[7][13][11];
  int t[7][13][11];
  double keisu[7][13][11];

  inline void set_init();
public:
  RealSphericalHarmonic(){ set_init(); }
  double get_keisu(int l,int m,int nth){
    return keisu[l][m+l][nth];
  }
  int get_r(int l,int m,int nth){return r[l][m+l][nth];}
  int get_s(int l,int m,int nth){return s[l][m+l][nth];}
  int get_t(int l,int m,int nth){return t[l][m+l][nth];}
  int get_num(int l,int m){return num[l][m+l];}
};


template <typename Integ1e>
class ECP_integral{

  RealSphericalHarmonic rsh;
  double n_kaizyou[301];
  double nnn[301];
  double nnn_m1[301];
  double C_na[5][5];
  double alpha;
  double CA[3],CB[3];
  double k_xyz[3],k_xyz_A[3],k_xyz_B[3];
  double k_length,k_length_A,k_length_B;
  int n_dash;
  double Dabc;
 
  

  double v_xyz_integral_over_omega[15][15][15];
  double v_y_xyz_integral_over_omega[7][13][7][7][7];
  double v_yy_xyz_integral_over_omega[7][13][4][7][4][4][4];
  double v_xyz_Ylm_integral_over_omega[4][4][4][4][7];

  double v_y_k_xyz[7][13];
  int    check_type1_radial[8][7];
  double Omega_type1_radial[8][7];

  double Omega_type2_radial[10][7][7];
  int    check_type2_radial[10][7][7];

  double a_value,rc_div_sqrt_alpha;

  double v_y_k_xyz_A[7][13];
  double v_y_k_xyz_B[7][13];



  //
  //  for type1
  double cal_xyz_integral_over_omega(int i,int j,int k);
  double cal_ECP_type1_ANGULAR_integral(int I,int J,int K,int lamda);
  double cal_ECP_type1_ANGULAR_integral2(int I,int J,int K,int lamda);
  double hypergeometric_function(double a, double c,double z);
  double cal_ECP_type1_RADIAL_integral(double k_length,double alpha,int n,int l);
  //
  //  for type2
  double cal_ECP_type2_ANGULAR_integral(int a,int b,int c,int lamda,int l,int m,double *k_xyz);
  double cal_ECP_type2_ANGULAR_integral_A(int a,int b,int c,int lamda,int l,int m);
  double cal_ECP_type2_ANGULAR_integral_B(int a,int b,int c,int lamda,int l,int m);
  double cal_ECP_type2_RADIAL_integral(int n,int lamda,int lamda_bar);
                                       
  double cal_xyz_Ylm_integral_over_omega(int I,int J,int K,int l,int m);

  void set_init();
public:
  void set_primitives4_sub1(double g1,const double R1[3],double g2,const double R2[3],double gc,const double C[3]);
  void set_primitives4_sub2(double g1,double g2,int n_dash_c,int t_n1,int t_n2,int cth_L);
  double get_Dabc(){ return Dabc; }
  double cal_ECP_type1_integral_for_primitive3(int *n1,int *n2);
  double cal_ECP_type2_integral_for_primitive3(int *n1,int *n2,int L);

  double cal_I(double in_g1,const std::vector<int> &in_n);

  std::vector<int> get_no_to_n(int in_st,int no){
    std::vector<int> ret_n = Integ1e::get_no_to_n(in_st,no);
    return ret_n;
  }

  ECP_integral(){  set_init(); }
  

  void show(){
    std::cout<<" alpha,k_length,k_length_A,k_length_B "<<alpha<<" "<<k_length_A<<" "<<k_length_B<<std::endl;
    std::cout<<" n_dash "<<n_dash<<" Dabc "<<Dabc<<std::endl;
    std::cout<<" CA "<<CA[0]<<" "<<CA[1]<<" "<<CA[2]<<" CB "<<CB[0]<<" "<<CB[1]<<" "<<CB[2]<<std::endl;
  }
};

template <typename M_tmpl,typename Integ1e>
class ECP_matrix {
  double CUTOFF_ECP;

  void cal_ECP_matrix_base(std::vector<M_tmpl*> &ret_ecpM,const std::vector<Shell_Cgto> &scgtos,const std::vector<ECP> &ecps,const CTRL_PBC &ctrl_pbc);
  std::vector<double> cal_grad_ECP_base(const std::vector<Shell_Cgto> &scgtos,const std::vector<ECP> &ecps,const std::vector<M_tmpl*> &D_PBC,const CTRL_PBC &ctrl_pbc);


  void cal_shell(std::vector<double> &ret_shell,int p,int q,int cth,const std::vector<int> &nc,const std::vector<int> &nt,
                 const std::vector<Shell_Cgto> &scgtos,const std::vector<ECP> &ecps,const CTRL_PBC &ctrl_pbc,ECP_integral<Integ1e> &ecp_integ);

  void cal_grad_shell(std::vector<double> &ret_grad_shell, int p, int q, int cth, const std::vector<int> &nc, const std::vector<int> &nt,
                      const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, 
                      const std::vector<M_tmpl*> &D_PBC, const CTRL_PBC &ctrl_pbc, ECP_integral<Integ1e> &ecp_integ);
public:
  ECP_matrix(){ CUTOFF_ECP=1.0e-13; }
  void set_CUTOFF_ECP(double in){ CUTOFF_ECP=in; }

                      
  void cal_ECP(M_tmpl &retM,const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps){
    CTRL_PBC ctrl_pbc;
    std::vector<M_tmpl*> tmpM(1);
    tmpM[0]=&retM;
    cal_ECP_matrix_base(tmpM,scgtos,ecps,ctrl_pbc);
  }
  void cal_ECP_PBC(std::vector<M_tmpl> &retM,const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, const CTRL_PBC &ctrl_pbc){
    int N123_c=ctrl_pbc.get_N123_c();
    retM.clear();
    retM.reserve(N123_c);
    retM.resize(N123_c); 
    std::vector<M_tmpl*> tmpM(N123_c);
    for(int q=0;q<N123_c;q++) tmpM[q]=&retM[q];
    cal_ECP_matrix_base(tmpM,scgtos,ecps,ctrl_pbc); 
  }

  std::vector<double> cal_grad_ECP(const std::vector<Shell_Cgto> &scgtos,const std::vector<ECP> &ecps,const M_tmpl &D){
    CTRL_PBC ctrl_pbc;
    std::vector<M_tmpl*> tmpD(1);
    tmpD[0]=const_cast<M_tmpl*>(&D);
    return cal_grad_ECP_base(scgtos,ecps,tmpD,ctrl_pbc); 
  }
                                        

   

};


}  // end of namespace "Lotus_core"

#include "detail/ECP_detail.hpp"

#endif // include-guard 

