 

#ifndef PINT1E_H
#define PINT1E_H

#include "stdlib.h"
#include "basis_index.h"
#include "c_to_xyz.h"
#include <vector>
#include <iostream>

namespace PInt {

template <int in_tN>
class PInt1e_base {
  static const int tN=in_tN;   // This template value is dummy, it is not used in this class.

  double g1,g2;
  double R1[3],R2[3],P[3],Rc[3];

  // common
  inline void set_n12(int n1[3],int n2[3],int i1,int i2,int tn1,int tn2){
    n1[0]=basis_index::no_to_n0[tn1][i1];  n1[1]=basis_index::no_to_n1[tn1][i1];  n1[2]=basis_index::no_to_n2[tn1][i1];
    n2[0]=basis_index::no_to_n0[tn2][i2];  n2[1]=basis_index::no_to_n1[tn2][i2];  n2[2]=basis_index::no_to_n2[tn2][i2];
  }

  inline void set_n12_m(int n1_m[3],int n2_m[3],const int n1[3],const int n2[3],int xyz){
    n1_m[0]=n1[0];  n1_m[1]=n1[1];  n1_m[2]=n1[2];  n1_m[xyz]--;
    n2_m[0]=n2[0];  n2_m[1]=n2[1];  n2_m[2]=n2[2];  n2_m[xyz]--;
  }

  int get_xyz(const int n[3]){
    int xyz=0;
    if(n[0]>0)      xyz=0;
    else if(n[1]>0) xyz=1;
    else if(n[2]>0) xyz=2;
    return xyz;
  }

  //
  // overlap
  double overlap_ss;
  double *ptr_overlap_dp[10][10];

  //
  // nai
  double nai_ss[20];
  double *ptr_nai_c_dp[10][10][3][20];

  // nai-c

  //
  // overlap sub-functions
  double overlap_simple_sub1(const std::vector<int> &n1,const std::vector<int> &n2,int xyz);
  double overlap_simple_sub2(const std::vector<int> &n1,const std::vector<int> &n2,int xyz);
  void overlap_dp(double *ret_ss,int tn1,int tn2);
  void overlap_dp_sub(double *ret_ss,int tn1,int tn2);

  //
  // mi sub-functions
  double mi_simple_sub1(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<double> &in_C,const std::vector<int> &klm,int xyz); 
  double mi_simple_sub2(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<double> &in_C,const std::vector<int> &klm,int xyz); 
  double mi_simple_sub3(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<double> &in_C,const std::vector<int> &klm,int xyz); 

  // 
  // nai sub-functions
  double nuclear_c_simple_sub1(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<int> &nc,int m,int xyz);
  double nuclear_c_simple_sub2(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<int> &nc,int m,int xyz);
  void nuclear_c_dp(double *ret_nai,int tn1,int tn2,int tc);
  void nuclear_c_dp_sub(double *ret_nai,int tn1,int tn2,int tc,int m);
 
  
public:

  void  show_state();
  static int get_num(int tn){  return (tn+2)*(tn+1)/2; }
  static double cal_I(double in_g1,const std::vector<int> &in_n);
  static std::vector<int> get_no_to_n(int in_st,int no){
    std::vector<int> ret_n;
    ret_n.push_back(basis_index::no_to_n0[in_st][no]); 
    ret_n.push_back(basis_index::no_to_n1[in_st][no]); 
    ret_n.push_back(basis_index::no_to_n2[in_st][no]); 
    return ret_n;
  }
  static void get_no_to_n(int *ret_n, int in_st, int no){
    ret_n[0]=basis_index::no_to_n0[in_st][no];
    ret_n[1]=basis_index::no_to_n1[in_st][no];
    ret_n[2]=basis_index::no_to_n2[in_st][no];
  }

  static int get_n_to_no(const std::vector<int> &in_n){ return basis_index::n_to_no[in_n[0]][in_n[1]][in_n[2]]; }

  std::vector<double> cal_dI(int in_st,double in_g,double in_d);
  void   set_gR_12(double in_g1,const std::vector<double> &in_R1,double in_g2,const std::vector<double> &in_R2);


  static std::vector<int> get_nc(int tc,int c){
    std::vector<int> nc(3);
    nc[0]=0;   nc[1]=0;   nc[2]=0; 
    if(tc==1){       nc[c_to_xyz1[1][c]]++; }
    else if(tc==2){  nc[c_to_xyz1[2][c]]++; nc[c_to_xyz2[2][c]]++; }
    else{
      std::cout<<"  ERROR in get_tc of PInt1e_base<double>  tc="<<tc<<std::endl;
      exit(1);
    }
    return nc;
  }

  void mult_dI(std::vector<double> &ret_v,int tn1,int tn2,
               const std::vector<double> &dI_a,const std::vector<double> &dI_b){
    mult_dI_c(ret_v,tn1,tn2,0,dI_a,dI_b);
  }
  void mult_dI_c(std::vector<double> &ret_v,int tn1,int tn2,int tc,
                 const std::vector<double> &dI_a,const std::vector<double> &dI_b);
  //
  // overlap
  double overlap_simple(const std::vector<int> &n1,const std::vector<int> &n2);
  
  void overlap(std::vector<double> &ret_ss,int tn1,int tn2){
    int N12=get_num(tn1)*get_num(tn2);
    ret_ss.reserve(N12);
    overlap_dp(&ret_ss[0],tn1,tn2);
  }
  void overlap(std::vector<double> &ret_ss,int tn1,int tn2,const std::vector<double> &dI_a,const std::vector<double> &dI_b){
    overlap(ret_ss,tn1,tn2);
    mult_dI(ret_ss,tn1,tn2,dI_a,dI_b);
  }
  //
  // kinetic energy integral
  double kinetic_simple(const std::vector<int> &n1,const std::vector<int> &n2);
  void   kinetic(std::vector<double> &ret_kei,int tn1,int tn2);
  void   kinetic(std::vector<double> &ret_kei,int tn1,int tn2,std::vector<double> dI_1,std::vector<double> dI_2){
    kinetic(ret_kei,tn1,tn2);
    mult_dI(ret_kei,tn1,tn2,dI_1,dI_2);
  }


  //
  // nuclear atraction integral
  enum MODE {Normal=0,Erfc=1,Erf=2};
  
  void   set_gR_12_nuc(double in_g1,const std::vector<double> &in_R1,double in_g2,const std::vector<double> &in_R2,
                       int max_m,const std::vector<double> &in_Rc,MODE mode_erfc,double omega);
  void   set_gR_12(double in_g1,const std::vector<double> &in_R1,double in_g2,const std::vector<double> &in_R2,
                   int max_m,const std::vector<double> &in_Rc){
    set_gR_12_nuc(in_g1,in_R1,in_g2,in_R2,max_m,in_Rc,Normal,0.0); }
  void   set_gR_12_erfc(double in_g1,const std::vector<double> &in_R1,double in_g2,const std::vector<double> &in_R2,
                        int max_m,const std::vector<double> &in_Rc,double omega){
    set_gR_12_nuc(in_g1,in_R1,in_g2,in_R2,max_m,in_Rc,Erfc,omega); }
  void   set_gR_12_erf(double in_g1,const std::vector<double> &in_R1,double in_g2,const std::vector<double> &in_R2,
                       int max_m,const std::vector<double> &in_Rc,double omega){
    set_gR_12_nuc(in_g1,in_R1,in_g2,in_R2,max_m,in_Rc,Erf,omega); }

  double nuclear_simple(const std::vector<int> &n1,const std::vector<int> &n2,int m){
    std::vector<int> nc(3);
    nc[0]=0; nc[1]=0; nc[2]=0;
    return nuclear_c_simple(n1,n2,nc,m);
  }

  void nuclear(std::vector<double> &ret_nai,int tn1,int tn2){
    int N12=get_num(tn1)*get_num(tn2);
    ret_nai.reserve(N12);
    nuclear_c_dp(&ret_nai[0],tn1,tn2,0);
  }
  void nuclear(std::vector<double> &ret_nai,int tn1,int tn2,const std::vector<double> &dI_a,const std::vector<double> &dI_b){
    nuclear(ret_nai,tn1,tn2);
    mult_dI(ret_nai,tn1,tn2,dI_a,dI_b);
  }

  //
  // momentum integral
  // C is center of coordinate
  // (x-Cx)^kx * (y-Cy)^l * (z-Cz)^m
  double mi_simple(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<double> &C,const std::vector<int> &klm);

  //
  // nai-grad
  double nuclear_c_simple(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<int> &nc,int m);
 
  void nuclear_c(std::vector<double> &ret_nai,int tn1,int tn2,int tc){
    int N_c=1;
    if(tc==1) N_c=3;
    if(tc==2) N_c=6;
    if(tc>2){ std::cout<<" ERROR in nuclear_c of PInt1e_base<double> class tc="<<tc<<std::endl; }
    int N12c=get_num(tn1)*get_num(tn2)*N_c;
    ret_nai.reserve(N12c);
    nuclear_c_dp(&ret_nai[0],tn1,tn2,tc);
  }
  
  void nuclear_c(std::vector<double> &ret_nai,int tn1,int tn2,int tc,const std::vector<double> &dI_a,const std::vector<double> &dI_b){

    nuclear_c(ret_nai,tn1,tn2,tc);
    mult_dI_c(ret_nai,tn1,tn2,tc,dI_a,dI_b);
  }

};
 
  // DEBUG
class DEBUG_PInt1e{
public:
  inline static int debug_driver_overlap(int max_ij);
  inline static int debug_driver_kinetic(int max_ij);
  inline static int debug_driver_nuclear(int max_ij);
  inline static int debug_driver_nuclear_c(int max_ij);
};


typedef PInt1e_base<0> PInt1e;

} // end of namespace "PInt"


#include "detail/PInt1e_detail.hpp"


#endif // end of ifndef PINT1E_H
