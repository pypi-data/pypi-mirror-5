
 
#ifndef DFT_FUNC_H
#define DFT_FUNC_H

#define _USE_MATH_DEFINES
#include <math.h>

#include <vector>


namespace Lotus_core {


class DFT_func {
public:

  //
  //  DFT functionals
  //
  
  // Screened Slater
  inline static double F_Screened_Slater1(double x);
  inline static double F_Screened_Slater3(double rou,double epsilon,double b_Bechstedt);

  inline static void func_Slater(double &ret_ene,std::vector<double> &ret_v123,double rou);

  inline static void func_USlater(double &ret_ene, std::vector<double> &ret_v123_a, std::vector<double> &ret_v123_b,
                           double rou_a, double rou_b);


  // Beck 88
  inline static void func_g_B88(double &ret,double &ret_deri,double x_gga);
  inline static void func_B88(double &ret_b88,double &f_rou,double &f_gamma,double rou,double gamma_gga);
  inline static void func_UB88(double &ret_b88,double &ret_f_rou_a,double &ret_f_rou_b,
                               double &ret_f_gamma_aa,double &ret_f_gamma_bb,
                               double rou_a,double rou_b,double gamma_aa,double gammma_bb);
  inline static void func_g_B88_TDDFT(double &ret,double &ret_deri,double &ret_deri2,double x_gga);
  inline static void func_B88_TDDFT(double &ret_B_gamma,double &ret_B_rou2,double &ret_B_gamma2,double &ret_B_gamma_rou,
                                    double rou,double gamma_gga);

  
  // VWM
  inline static void func_PFA_VWN(double &ret,double &ret_deri,double x,int sel);  // sel==0,1,2 for P,F,A
  inline static void func_g_VWN(double &ret,double &ret_deri,double sa);
  inline static void func_h_VWN(double &ret,double &ret_deri,double ep,double ef,double ea,
                                double ep_deri,double ef_deri,double ea_deri);
  inline static void func_f_VWN(double &ret,double &ret_deri,double sa);
  inline static void func_VWN(double &ret_vwn,double &ret_rou,double rou);
  inline static void func_UVWN(double &ret_vwn,double &ret_rou_a,double &ret_rou_b,double rou_a,double rou_b);
  inline static void func_VWN_TDDFT(double &ret_v_aa,double &ret_v_ab,double rou);


  // LYP
  inline static void func_LYP(double &ret_lyp,double &ret_f_rou,double &ret_f_gamma_aa,double &ret_f_gamma_ab,
                       double rou_a,double rou_b,double gamma_aa,double gamma_ab,double gamma_bb);
  inline static void func_ULYP(double &ret_lyp,double &ret_f_rou_a,double &ret_f_rou_b,
                        double &ret_f_gamma_aa,double &ret_f_gamma_ab,double &ret_f_gamma_bb,
                        double rou_a,double rou_b,double gamma_aa,double gamma_ab,double gamma_bb);
  inline static void func_LYP_TDDFT(std::vector<double> &ret_v_aa,std::vector<double> &ret_v_ab,
                             double rou_a,double rou_b,double gamma_aa,double gamma_ab,double gammma_bb,double integ_w);



};

}  // end of namespace "Lotus_core"

#include "detail/DFT_func_detail.hpp"

#endif // end of ifndef DFT_FUNC_H
