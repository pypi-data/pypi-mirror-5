
#ifndef PINT2E_H
#define PINT2E_H

#include <math.h>
#include "basis_index.h"

#include <vector>

namespace PInt {

template <int in_tN>
class PInt2e_base {
protected:
  static const int tN=in_tN;   // This template value is dummy, it is not used in this class.

  int save_tn; 
  double g1,g2,g3,g4;
  double R1[3],R2[3],R3[3],R4[3];
  double P[3],Q[3],W[3],G[3];
  double t1,t2,rou,ss1,ss2,CC,T;


  double c_0_5_div_t1;
  double c_0_5_div_t2;
  double c_0_5_div_t1_plus_t2;
  double rou_div_t1;
  double rou_div_t2;


  double vrr4_ssss[22];
  double vrr3_sss[22];
  double to_sss;


  static double cal_ss(double in_g1,const double in_R1[3],double in_g2,const double in_R2[3]);


  inline int get_xyz(const int n[3]){
    int xyz;
    if(n[0]>0)   xyz=0;
    else if(n[1]>0) xyz=1;
    else if(n[2]>0) xyz=2;
    return xyz;
  }

  inline void set_n1234(int n1[3],int n2[3],int n3[3],int n4[3],int i1,int i2,int i3,int i4,int tn1,int tn2,int tn3,int tn4){
    set_n(n1, i1, tn1);
    set_n(n2, i2, tn2);
    set_n(n3, i3, tn3);
    set_n(n4, i4, tn4);
  }

  inline void set_n(int n[3], int i, int tn)
  {
    n[0] = basis_index::no_to_n0[tn][i];
    n[1] = basis_index::no_to_n1[tn][i];
    n[2] = basis_index::no_to_n2[tn][i];
  }

  inline void set_n1234_p(int n1_p[3],int n2_p[3],int n3_p[3],int n4_p[3],const int n1[3],const int n2[3],const int n3[3],const int n4[3],int xyz){
    set_n_p(n1_p, n1, xyz);
    set_n_p(n2_p, n2, xyz);
    set_n_p(n3_p, n3, xyz);
    set_n_p(n4_p, n4, xyz);
  }

  inline void set_n1234_m(int n1_m[3],int n2_m[3],int n3_m[3],int n4_m[3],const int n1[3],const int n2[3],const int n3[3],const int n4[3],int xyz){
    set_n_m(n1_m, n1, xyz);
    set_n_m(n2_m, n2, xyz);
    set_n_m(n3_m, n3, xyz);
    set_n_m(n4_m, n4, xyz);
  }

  inline void set_n_m(int n_m[3], const int n[3], int xyz)
  {
    n_m[0] = n[0];
    n_m[1] = n[1];
    n_m[2] = n[2];
    n_m[xyz]--;
  }

  inline void set_n_p(int n_p[3], const int n[3], int xyz)
  {
    n_p[0] = n[0];
    n_p[1] = n[1];
    n_p[2] = n[2];
    n_p[xyz]++;
  }
  inline int get_no(int *n){
    return basis_index::n_to_no[n[0]][n[1]][n[2]];
  }

  inline int calc_m(int* n)
  {
    return basis_index::n_to_no[n[0]][n[1]][n[2]];
  }

  inline int calc_m2(int* n, int xyz)
  {
    int n_m2[3] = {n[0], n[1], n[2]};
    n_m2[xyz] -= 2;
    return calc_m(n_m2);
  }


  //
  //  simple_sub
  //
  double ERI_m_simple(const int n1[3],const int n2[3],const int n3[3],const int n4[3],int m);
  double ERI_m_simple_sub1(const int n1[3],const int n2[3],const int n3[3],const int n4[3],int m,int xyz); 
  double ERI_m_simple_sub2(const int n1[3],const int n2[3],const int n3[3],const int n4[3],int m,int xyz); 
  double ERI_m_simple_sub3(const int n1[3],const int n2[3],const int n3[3],const int n4[3],int m,int xyz); 
  double ERI_m_simple_sub4(const int n1[3],const int n2[3],const int n3[3],const int n4[3],int m,int xyz); 
  //
  //  recursion
  void ERI_recursion_sub(double *ret_v,int tn1,int tn2,int tn3,int tn4,int m);


  //
  //  Three-Overlap : sub-functions
  //
  double cal_to_simple(const int n1[3],const int n2[3],const int n3[3]);
  double cal_to_simple_sub1(const int n1[3],const int n2[3],const int n3[3],int xyz);
  double cal_to_simple_sub2(const int n1[3],const int n2[3],const int n3[3],int xyz);
  double cal_to_simple_sub3(const int n1[3],const int n2[3],const int n3[3],int xyz);

public:
  PInt2e_base(){  save_tn=-1; }
 

  void show_state();

  // common
//  static double cal_I(double g,const std::vector<int> &n);
 
  static double cal_I(double in_g1,const std::vector<int> &in_n);

  std::vector<double> cal_dI(int in_st,double in_g,double in_d);

  static std::vector<int> get_no_to_n(int in_st,int no){
    std::vector<int> ret_n;
    ret_n.push_back(basis_index::no_to_n0[in_st][no]); 
    ret_n.push_back(basis_index::no_to_n1[in_st][no]); 
    ret_n.push_back(basis_index::no_to_n2[in_st][no]); 
    return ret_n;
  }


  void set_gR_12(double in_g1, const double *in_R1, double in_g2, const double *in_R2);
  void set_gR_12(double in_g1, const std::vector<double> &in_R1, double in_g2, const std::vector<double> &in_R2){
    set_gR_12(in_g1, &in_R1[0], in_g2, &in_R2[0]);
  }
  void set_gR_34(double in_g3, const double *in_R3, double in_g4, const double *in_R4);
  void set_gR_34(double in_g3, const std::vector<double> &in_R3, double in_g4, const std::vector<double> &in_R4){
    set_gR_34(in_g3, &in_R3[0], in_g4, &in_R4[0]);
  }
  void set_eri_ssss(int tn,int mode_erfc,double omega_erfc);
  double get_T(){ return T; }


  //
  // simple 
  int get_num(int tn){
    int ret=(tn+2)*(tn+1)/2;
    return ret;
  }


  void ERI_recursion(std::vector<double> &ret_eri,int tn1,int tn2,int tn3,int tn4,
                     const std::vector<double> &dI_a,const std::vector<double> &dI_b,
                     const std::vector<double> &dI_c,const std::vector<double> &dI_d);

  virtual void ERI(std::vector<double> &ret_eri,int tn1,int tn2,int tn3,int tn4,
                   const std::vector<double> &dI_a,const std::vector<double> &dI_b,
                   const std::vector<double> &dI_c,const std::vector<double> &dI_d){
    ERI_recursion(ret_eri,tn1,tn2,tn3,tn4,dI_a,dI_b,dI_c,dI_d);
  }


  double ERI_simple(double in_g1,const std::vector<int> &n1,double in_g2,const std::vector<int> &n2,
                    double in_g3,const std::vector<int> &n3,double in_g4,const std::vector<int> &n4){
    double I1=cal_I(in_g1,n1);
    double I2=cal_I(in_g2,n2);
    double I3=cal_I(in_g3,n3);
    double I4=cal_I(in_g4,n4);
    return I1*I2*I3*I4*ERI_m_simple(&n1[0],&n2[0],&n3[0],&n4[0],0);
  } 
  double ERI_m_simple(const std::vector<int> &n1,const std::vector<int> &n2,
                      const std::vector<int> &n3,const std::vector<int> &n4,int m){
    return ERI_m_simple(&n1[0],&n2[0],&n3[0],&n4[0],m);
  } 
  double ERI_simple(const std::vector<int> &n1,const std::vector<int> &n2,
                    const std::vector<int> &n3,const std::vector<int> &n4){
    return ERI_m_simple(n1,n2,n3,n4,0);
  } 


  // 
  //  three vrr
  double ERI_m_simple(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<int> &n3,int m){
    std::vector<int> n_zero(3,0);
    return ERI_m_simple(n1,n2,n3,n_zero,m);
  }
  double ERI_simple(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<int> &n3){
    return ERI_m_simple(n1,n2,n3,0);
  } 
  void set_gR_3(double in_g3,const std::vector<double> &in_R3){
    set_gR_34(in_g3,in_R3,0.0,in_R3);
  }
  void set_eri_sss(int tn,int mode_erfc,double omega_erfc){
    set_eri_ssss(tn,mode_erfc,omega_erfc);
    for(int m=0;m<=tn;m++) vrr3_sss[m]=vrr4_ssss[m];
  }


  //
  //   three overlap
  void   set_to_sss(double in_g1,const std::vector<double> &in_R1,double in_g2,const std::vector<double> &in_R2,
                    double in_g3,const std::vector<double> &in_R3);
  double cal_to_simple(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<int> &n3){
    return cal_to_simple(&n1[0],&n2[0],&n3[0]);
  }


  //
  //   debug_driver
  static int debug_driver_os_recursion(int max_ijkl);


};

//template <typename double>
class PInt2e_os_dp : public PInt2e_base<0> {


  // FOR DP
  const static int max_tn_ptr=6;
  const static int max_tn_array=1;
  const static int max_m_array=(max_tn_ptr+1)*4+2-4*max_tn_array;
  const static int max_num_array=(max_tn_array+2)*(max_tn_array+1)/2;
  const static int max_data_array=max_num_array*max_num_array*max_num_array*max_num_array;
  double eri_array[max_tn_array+1][max_tn_array+1][max_tn_array+1][max_tn_array+1][max_m_array][max_data_array];


  double *eri_dp[max_tn_ptr+1][max_tn_ptr+1][max_tn_ptr+1][max_tn_ptr+1][(max_tn_ptr+1)*4+2];
  bool eri_dp_flags[max_tn_ptr+1][max_tn_ptr+1][max_tn_ptr+1][max_tn_ptr+1][(max_tn_ptr+1)*4+2];

  inline void ERI_dp_sub(double *ret_v, int tn1, int tn2, int tn3, int tn4, int m);
  inline void ERI_dp_sub_tn1(double *ret_v, int tn1, int tn2, int tn3, int tn4, int m);
  inline void ERI_dp_sub_tn2(double *ret_v, int tn2, int tn3, int tn4, int m);
  inline void ERI_dp_sub_tn3(double *ret_v, int tn3, int tn4, int m);
  inline void ERI_dp_sub_tn4(double *ret_v, int tn4, int m);

  inline void ERI_dp_clear_flags(int tn1, int tn2, int tn3, int tn4,int M);
  inline void ERI_dp_mark_flags(int tn1, int tn2, int tn3, int tn4, int m);


public:

//  inline void ERI_dp(std::vector<double> &ret_eri,int tn1,int tn2,int tn3,int tn4,
//                     const std::vector<double> &dI_a,const std::vector<double> &dI_b,
//                     const std::vector<double> &dI_c,const std::vector<double> &dI_d);
  inline void ERI_dp(double *ret_eri, int tn1, int tn2, int tn3, int tn4,
                     const double *dI_a, const double *dI_b, const double *dI_c, const double *dI_d);
  
  inline void ERI_init(int tn1, int tn2, int tn3, int tn4);
  inline void ERI_finalize(int tn1, int tn2, int tn3, int tn4);

  void ERI(std::vector<double> &ret_eri,int tn1,int tn2,int tn3,int tn4,
           const std::vector<double> &dI_a,const std::vector<double> &dI_b,
           const std::vector<double> &dI_c,const std::vector<double> &dI_d){
    ERI_dp(&ret_eri[0], tn1, tn2, tn3, tn4, &dI_a[0], &dI_b[0], &dI_c[0], &dI_d[0]);
  }
  
  inline void grad_ERI_dp(std::vector<double> &ret_grad,int tn1,int tn2,int tn3,int tn4,
                          const std::vector<double> &dI_a,const std::vector<double> &dI_b,
                          const std::vector<double> &dI_c,const std::vector<double> &dI_d);

  void grad_init(int nt1, int tn2, int tn3, int tn4);
  void grad_finalize(int tn1, int tn2, int tn3, int tn4);

  void grad_ERI(std::vector<double> &ret_grad,int tn1,int tn2,int tn3,int tn4,
                const std::vector<double> &dI_a,const std::vector<double> &dI_b,
                const std::vector<double> &dI_c,const std::vector<double> &dI_d){
    grad_ERI_dp(ret_grad,tn1,tn2,tn3,tn4,dI_a,dI_b,dI_c,dI_d);
  }


  static int debug_driver_os_dp(int max_ijkl);
  static int debug_driver_grad(int max_ijkl);

};


class PInt2e_vhrr_dp : public PInt2e_base<0> {
private:
  inline void ERI_vrr_dp_sub(double *ret_eri,int tn2,int tn4,int m);
  inline void ERI_vrr_dp_sub_tn2(double* ret_eri, int tn2, int tn4, int m);
  inline void ERI_vrr_dp_sub_tn4(double* ret_eri, int tn4, int m);

  const static int max_tn_ptr=6;
  const static int max_tn_array=1;
  const static int max_m_array=(max_tn_ptr+1)*4+2-4*max_tn_array;
  const static int max_num_array=(max_tn_array+2)*(max_tn_array+1)/2;
  const static int max_data_array=max_num_array*max_num_array*max_num_array*max_num_array;
  double eri_array[max_tn_array+1][max_tn_array+1][max_tn_array+1][max_tn_array+1][max_m_array][max_data_array];


  double *eri_dp[max_tn_ptr+1][(max_tn_ptr+1)*2][max_tn_ptr+1][(max_tn_ptr+1)*2][(max_tn_ptr+1)*4+2];

  bool    eri_dp_hrr_flags[max_tn_ptr+1][(max_tn_ptr+1)*2][max_tn_ptr+1][(max_tn_ptr+1)*2][(max_tn_ptr+1)*4+2];
  bool    eri_dp_vrr_flags[(max_tn_ptr+1)*2][(max_tn_ptr+1)*2][(max_tn_ptr+1)*4+2];

  inline void ERI_dp_clear_flags(int tn1, int tn2, int tn3, int tn4,int max_m);
  inline void ERI_dp_mark_vrr_flags(int tn2, int tn4, int m);
  inline void ERI_dp_mark_flags(int tn1, int tn2, int tn3, int tn4, int m);

  inline void ERI_hrr_recursion_sub(double *ret_eri,int tn1,int tn2,int tn3,int tn4,int m);
  inline void ERI_hrr_dp_sub(double *ret_eri,int tn1,int tn2,int tn3,int tn4,int m);

public:

//  inline void ERI_dp(std::vector<double> &ret_eri,int tn1,int tn2,int tn3,int tn4,
//                     const std::vector<double> &dI_a,const std::vector<double> &dI_b,
//                     const std::vector<double> &dI_c,const std::vector<double> &dI_d);

  inline void ERI_dp(double *ret_eri, int tn1, int tn2, int tn3, int tn4,
                     const double *dI_a, const double *dI_b, const double *dI_c, const double *dI_d);

  inline void ERI_init(int tn1, int tn2, int tn3, int tn4);
  inline void ERI_finalize(int tn1, int tn2, int tn3, int tn4);

  inline void ERI(std::vector<double> &ret_eri,int tn1,int tn2,int tn3,int tn4,
                  const std::vector<double> &dI_a,const std::vector<double> &dI_b,
                  const std::vector<double> &dI_c,const std::vector<double> &dI_d){
    ERI_dp(&ret_eri[0], tn1, tn2, tn3, tn4, &dI_a[0], &dI_b[0], &dI_c[0], &dI_d[0]);
  }

  inline void grad_ERI_dp(std::vector<double> &ret_grad,int tn1,int tn2,int tn3,int tn4,
                          const std::vector<double> &dI_a,const std::vector<double> &dI_b,
                          const std::vector<double> &dI_c,const std::vector<double> &dI_d);

  void grad_init(int nt1, int tn2, int tn3, int tn4);
  void grad_finalize(int tn1, int tn2, int tn3, int tn4);

  inline void grad_ERI(std::vector<double> &ret_grad,int tn1,int tn2,int tn3,int tn4,
                const std::vector<double> &dI_a,const std::vector<double> &dI_b,
                const std::vector<double> &dI_c,const std::vector<double> &dI_d){
    grad_ERI_dp(ret_grad,tn1,tn2,tn3,tn4,dI_a,dI_b,dI_c,dI_d);
  }


  static int debug_driver_vhrr_dp(int max_ijkl);
  static int debug_driver_grad(int max_ijkl);

};

typedef PInt2e_os_dp PInt2e;

}  // end of namespace "PInt"

#include "detail/PInt2e_base_detail.hpp"
#include "detail/PInt2e_os_dp_detail.hpp"
#include "detail/PInt2e_vhrr_dp_detail.hpp"

#endif // end of ifndef PINT2E_H

