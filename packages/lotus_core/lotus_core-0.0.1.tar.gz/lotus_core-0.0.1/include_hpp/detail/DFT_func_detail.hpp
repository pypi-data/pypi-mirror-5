
#ifndef DFT_FUNC_DETAIL_HPP
#define DFT_FUNC_DETAIL_HPP

#define _USE_MATH_DEFINES
#include <math.h>

#include "DFT_func.hpp"

#include <iostream>

namespace Lotus_core {
//
//  DFT functionals


//  Screened Slater
double DFT_func::F_Screened_Slater1(double x){
  double ret=1.0-(1.0/6.0)*x*x-(4.0/3.0)*x*atan(2.0/x)+0.5*x*x*log(1.0+4.0/(x*x))+(1.0/24.0)*x*x*x*x*log(1.0+4.0/(x*x));
  return ret;
}


double DFT_func::F_Screened_Slater3(double rou,double epsilon,double b_Bechstedt){
  double k_f       =pow(3.0*M_PI*M_PI*rou,1.0/3.0);
  double k_tf      =(2.0/sqrt(M_PI))*pow(3.0*M_PI*rou,1.0/6.0);
  double es=epsilon;
  if(epsilon<1.0+1.0e-10) es=1.0+1.0e-10; 
  double k_tf_tild =k_tf*sqrt((1.0/b_Bechstedt)*(1.0+1.0/(es-1.0)));
  double x=k_tf_tild/k_f;
  return F_Screened_Slater1(x); 
}

//  Slater


void DFT_func::func_Slater(double &ret_ene,std::vector<double> &ret_v123,double rou){
  const double CC=-1.0*pow(3.0/M_PI,1.0/3.0);
  const double CCene=-2.0*(3.0/4.0)*pow(2.0*3.0/M_PI,1.0/3.0);
  ret_v123[0] = CC*pow(2.0*rou,1.0/3.0);
  ret_v123[1] = 0.0;
  ret_v123[2] = 0.0;
  ret_ene = CCene*pow(rou,4.0/3.0);
}

void DFT_func::func_USlater(double &ret_ene, std::vector<double> &ret_v123_a, std::vector<double> &ret_v123_b,
                  double rou_a, double rou_b){
  const double CC   =-pow(2.0,1.0/3.0)          *pow(3.0/M_PI,1.0/3.0);
  const double CCene=-pow(2.0,1.0/3.0)*(3.0/4.0)*pow(3.0/M_PI,1.0/3.0);
  ret_v123_a[0] = CC*pow(rou_a,1.0/3.0);
  ret_v123_a[1] = 0.0;
  ret_v123_a[2] = 0.0;
  ret_v123_b[0] = CC*pow(rou_b,1.0/3.0);
  ret_v123_b[1] = 0.0;
  ret_v123_b[2] = 0.0;
  ret_ene   = CCene*( pow(rou_a,4.0/3.0)+pow(rou_b,4.0/3.0) );
}



//  Beck 88
void DFT_func::func_g_B88(double &ret,double &ret_deri,double x_gga){
  const double b=0.0042;
  double v_asinh=asinh(x_gga);
  double div=1.0/(1+6.0*b*x_gga*v_asinh);
  ret = -1.5*pow(3.0/(4.0*M_PI),1.0/3.0) - b*x_gga*x_gga*div;
  ret_deri=(6.0*b*b*x_gga*x_gga*(x_gga/sqrt(x_gga*x_gga+1.0)-v_asinh)-2.0*b*x_gga)*div*div;
}
void DFT_func::func_B88(double &ret_b88,double &ret_f_rou,double &ret_f_gamma,
                   double rou,double gamma_gga){
  ret_f_rou=0.0;
  ret_f_gamma=0.0;
  ret_b88=0.0;
  if(rou>1.0e-10){
    double sqrt_gamma_gga=sqrt(gamma_gga);
    double g,g_deri;
    double x_gga=sqrt_gamma_gga/pow(rou,4.0/3.0);
    DFT_func::func_g_B88(g,g_deri,x_gga); 
    ret_f_rou   = 4.0/3.0*pow(rou,1.0/3.0)*(g-x_gga*g_deri); 
    if(gamma_gga>1.0e-8) ret_f_gamma = (0.5/sqrt_gamma_gga)*g_deri;
    ret_b88     = 2.0*pow(rou,4.0/3.0)*g;
  }
}
void DFT_func::func_UB88(double &ret_b88,double &ret_f_rou_a,double &ret_f_rou_b,
                    double &ret_f_gamma_aa,double &ret_f_gamma_bb,
                    double rou_a,double rou_b,double gamma_aa,double gamma_bb){
  ret_b88=0.0;
  ret_f_rou_a=0.0;
  ret_f_rou_b=0.0;
  ret_f_gamma_aa=0.0;
  ret_f_gamma_bb=0.0;
  if(rou_a>1.0e-10){
    double sqrt_gamma_aa = sqrt(gamma_aa);  
    double x_aa          = sqrt_gamma_aa/pow(rou_a,4.0/3.0);
    double g_a, g_deri_a;
    DFT_func::func_g_B88(g_a,g_deri_a,x_aa); 
    ret_f_rou_a    = 4.0/3.0*pow(rou_a,1.0/3.0)*(g_a-x_aa*g_deri_a); 
    if(gamma_aa>1.0e-8) ret_f_gamma_aa = 0.5/sqrt_gamma_aa*g_deri_a;
    ret_b88 += pow(rou_a,4.0/3.0)*g_a;
  }
  if(rou_b>1.0e-10){
    double sqrt_gamma_bb=sqrt(gamma_bb);  
    double x_bb=sqrt_gamma_bb/pow(rou_b,4.0/3.0);
    double g_b, g_deri_b;
    DFT_func::func_g_B88(g_b,g_deri_b,x_bb); 
    ret_f_rou_b    = 4.0/3.0*pow(rou_b,1.0/3.0)*(g_b-x_bb*g_deri_b); 
    if(gamma_bb>1.0e-8) ret_f_gamma_bb = 0.5/sqrt_gamma_bb*g_deri_b;
    ret_b88 += pow(rou_b,4.0/3.0)*g_b;
  }
}

void DFT_func::func_g_B88_TDDFT(double &ret,double &ret_deri,double &ret_deri2,double x_gga){
  const double b=0.0042;
  double v_asinh=asinh(x_gga);
  double div=1.0/(1+6.0*b*x_gga*v_asinh);
  ret       = -1.5*pow(3.0/(4.0*M_PI),1.0/3.0) - b*x_gga*x_gga*div;
  ret_deri  = (6.0*b*b*x_gga*x_gga*(x_gga/sqrt(x_gga*x_gga+1.0)-v_asinh)-2.0*b*x_gga)*div*div;
  ret_deri2 = -2.0*(-2.0*b*x_gga+6.0*b*b*x_gga*x_gga*(x_gga/sqrt(1.0+x_gga*x_gga)-v_asinh))
                  *(6.0*b*x_gga/sqrt(1.0+x_gga*x_gga)+6.0*b*v_asinh)
                  /pow(1.0+6.0*b*x_gga*v_asinh,3.0)
              +(-2.0*b-6.0*b*b*x_gga*x_gga*x_gga*x_gga/pow(1.0+x_gga*x_gga,1.5)
                +12.0*b*b*x_gga*(x_gga/sqrt(1.0+x_gga*x_gga)-v_asinh))/pow(1.0+6.0*b*x_gga*v_asinh,2); 
}

void DFT_func::func_B88_TDDFT(double &ret_B_gamma,double &ret_B_rou2,double &ret_B_gamma2,double &ret_B_gamma_rou,
                         double rou,double gamma_gga){
  if(gamma_gga>1.0e-13){
    double sqrt_gamma_gga=sqrt(gamma_gga);
    double g,g_deri,g_deri2;
    double x_gga=sqrt_gamma_gga/pow(rou,4.0/3.0);
    DFT_func::func_g_B88_TDDFT(g,g_deri,g_deri2,x_gga);
    ret_B_gamma     = (0.5/sqrt_gamma_gga)*g_deri;
    ret_B_rou2      = (4.0/9.0)*pow(rou,-2.0/3.0)*(g-x_gga*g_deri+4.0*x_gga*x_gga*g_deri2);
    ret_B_gamma2    = (1.0/(4.0*gamma_gga))*(pow(rou,-4.0/3.0)*g_deri2-g_deri/sqrt_gamma_gga);
    ret_B_gamma_rou = (-2.0/3.0)*x_gga*g_deri2/(sqrt_gamma_gga*rou);
  }
}


// VWN

void DFT_func::func_PFA_VWN(double &ret,double &ret_deri,double x,int sel){
  // sel==0,1,2 for P,F,A
  const double  A[3] = { 0.0310907,  0.01554535, -0.016886864};
  const double x0[3] = {-0.409286,  -0.743294,   -0.00475840};
  const double  b[3] = {  13.0720,   20.1231,     1.13107};
  const double  c[3] = {  42.7198,   101.578,     13.0045};
//  const double  A[3] = { 0.0310907, 0.01554535, -0.016886864};
//  const double x0[3] = {-0.10498,  -0.32500,    -0.00475840};
//  const double  b[3] = { 3.72744,   7.06042,     1.13107};
//  const double  c[3] = { 12.9352,   18.0578,     13.0045};
  double Q=sqrt(4.0*c[sel]-b[sel]*b[sel]);
  double X =x*x+b[sel]*x+c[sel]; 
  double X0=x0[sel]*x0[sel]+b[sel]*x0[sel]+c[sel]; 
  double v_atan=atan(Q/(2.0*x+b[sel]));
  double B =2.0*x+b[sel];
  double B0=2.0*x0[sel]+b[sel];

  ret=A[sel]*(log(x*x/X)+(2.0*b[sel]/Q)*v_atan-(b[sel]*x0[sel]/X0)*(log((x-x0[sel])*(x-x0[sel])/X)+(2.0*B0/Q)*v_atan));
  ret_deri=A[sel]*(2.0/x-B/X-4.0*b[sel]/(B*B+Q*Q)-(b[sel]*x0[sel]/X0)*(2.0/(x-x0[sel])-B/X-(4.0*B0)/(B*B+Q*Q)));
 
}
void DFT_func::func_g_VWN(double &ret,double &ret_deri,double sa){
  ret      = (9.0/8.0)*( pow((1.0+sa),4.0/3.0) + pow((1.0-sa),4.0/3.0) - 2.0);
  ret_deri = (3.0/2.0)*( pow((1.0+sa),1.0/3.0) - pow((1.0-sa),1.0/3.0) );
}
void DFT_func::func_h_VWN(double &ret,double &ret_deri,double ep,double ef,double ea,
                     double ep_deri,double ef_deri,double ea_deri){
  ret      = (4.0/(9.0*( pow(2.0,1.0/3.0) - 1.0)))*((ef-ep)/ea)-1.0;
  ret_deri = (4.0/(9.0*( pow(2.0,1.0/3.0) - 1.0)))*( (ef_deri-ep_deri) - ea_deri*(ef-ep)/ea )/ea;
}
void DFT_func::func_f_VWN(double &ret,double &ret_deri,double sa){
  ret      = (1.0/(2.0*(pow(2.0,1.0/3.0)-1)))*( pow((1.0+sa),4.0/3.0) + pow((1.0-sa),4.0/3.0) - 2.0);
  ret_deri = (4.0/3.0)*(1.0/(2.0*(pow(2.0,1.0/3.0)-1)))*( pow((1.0+sa),1.0/3.0) - pow((1.0-sa),1.0/3.0) );
}
void DFT_func::func_VWN(double &ret_vwn,double &ret_f_rou,double rou){
  double t_rou=2.0*rou;
  double x_VWN=pow(3.0/(4.0*M_PI*t_rou),1.0/6.0);  // t_rou = rou_alpha + rou_beta;
  double ep,ep_deri;
  DFT_func::func_PFA_VWN(ep,ep_deri,x_VWN,0);
  ret_f_rou = ep+t_rou*(-x_VWN/(6.0*t_rou))*ep_deri;
  ret_vwn   = 2.0*rou*ep;
}

void DFT_func::func_UVWN(double &ret_vwn,double &ret_f_rou_a,double &ret_f_rou_b,double rou_a,double rou_b){
  double rou_t=rou_a+rou_b; // t_rou = rou_alpha + rou_beta;
  double x=pow(3.0/(4.0*M_PI*rou_t),1.0/6.0);  
  double sa=(rou_a-rou_b)/rou_t;
  double sa3=sa*sa*sa;
  double sa4=sa3*sa;
  double ep,ef,ea,ep_deri,ef_deri,ea_deri;
  double ec,ec_deri_a,ec_deri_b;
  DFT_func::func_PFA_VWN(ep,ep_deri,x,0);
  DFT_func::func_PFA_VWN(ef,ef_deri,x,1);
  DFT_func::func_PFA_VWN(ea,ea_deri,x,2);
  double f,f_deri;
  const double f_zero=(8.0/9.0)*(1.0/(2.0*(pow(2.0,1.0/3.0)-1.0)));
  DFT_func::func_f_VWN(f,f_deri,sa);
  double tmp1 = -1.0*(x/(6.0*rou_t))*( ep_deri + ea_deri*f/f_zero*(1-sa4) + (ef_deri-ep_deri)*f*sa4);
  double tmp2 = ea*f_deri/f_zero*(1-sa4)-4.0*ea*f/f_zero*sa3+(ef-ep)*(f_deri*sa4+f*4.0*sa3);
  ec=ep+ea*f/f_zero*(1-sa4)+(ef-ep)*f*sa4;

  ec_deri_a = tmp1 + tmp2*(1.0-sa)/rou_t;
  ec_deri_b = tmp1 - tmp2*(1.0+sa)/rou_t;

  ret_f_rou_a = ec+rou_t*ec_deri_a;
  ret_f_rou_b = ec+rou_t*ec_deri_b;
  ret_vwn     = rou_t*ec;
}

void DFT_func::func_VWN_TDDFT(double &ret_v_aa,double &ret_v_ab,double rou){
  const double  A[3] = { 0.0310907,  0.01554535, -0.016886864};
  const double x0[3] = {-0.409286,  -0.743294,   -0.00475840};
  const double  b[3] = {  13.0720,   20.1231,     1.13107};
  const double  c[3] = {  42.7198,   101.578,     13.0045};
//  const double  A[3] = { 0.0310907, 0.01554535, -0.016886864};
//  const double x0[3] = {-0.10498,  -0.32500,    -0.00475840};
//  const double  b[3] = { 3.72744,   7.06042,     1.13107};
//  const double  c[3] = { 12.9352,   18.0578,     13.0045};
  int sel=0;

  double t_rou=2.0*rou;
  double x=pow(3.0/(4.0*M_PI*t_rou),1.0/6.0);  // t_rou = rou_alpha + rou_beta;
  double x_deri_a =-1.0*pow((3.0/(4.0*M_PI)),1.0/6.0)*(1.0/6.0)*pow(t_rou,-7.0/6.0);
  double x_deri2_a=(7.0/36.0)*pow((3.0/(4.0*M_PI)),1.0/6.0)*pow(t_rou,-13.0/6.0);
  double Q=sqrt(4.0*c[sel]-b[sel]*b[sel]);
  double X =x*x+b[sel]*x+c[sel]; 
  double X0=x0[sel]*x0[sel]+b[sel]*x0[sel]+c[sel]; 
  double B =2.0*x+b[sel];
  double B0=2.0*x0[sel]+b[sel];
 
  double ec_deri =A[sel]*(2.0/x-B/X-4.0*b[sel]/(B*B+Q*Q)-(b[sel]*x0[sel]/X0)*(2.0/(x-x0[sel])-B/X-(4.0*B0)/(B*B+Q*Q)));
  double ec_deri2=A[sel]*(-2.0/(x*x)-2.0/X+B*B/(X*X)+16.0*b[sel]*B/((B*B+Q*Q)*(B*B+Q*Q))
                         -(1.0*b[sel]*x0[sel]/X0)*(-2.0/((x-x0[sel])*(x-x0[sel]))-2.0/X+B*B/(X*X)+16.0*B*B0/((B*B+Q*Q)*(B*B+Q*Q))));

  ret_v_aa=2.0*ec_deri*x_deri_a+t_rou*ec_deri2*x_deri_a*x_deri_a+t_rou*ec_deri*x_deri2_a;
  ret_v_ab=2.0*ec_deri*x_deri_a+t_rou*ec_deri2*x_deri_a*x_deri_a+t_rou*ec_deri*x_deri2_a;

}


// LYP
void  DFT_func::func_LYP(double &ret_lyp,double &ret_f_rou,double &ret_f_gamma_aa,double &ret_f_gamma_ab,
                         double rou_a,double rou_b,double gamma_aa,double gamma_ab,double gamma_bb){
  const double a=0.04918;   const double b=0.132;
  const double c=0.2533;     const double d=0.349;

  ret_f_rou=0.0;
  ret_f_gamma_aa=0.0;
  ret_f_gamma_ab=0.0;
  const double cutoff=1.0e-7;
  rou_a = rou_a-fmod(rou_a, 1.0e-10);
  rou_b = rou_b-fmod(rou_b, 1.0e-10);
  gamma_aa = gamma_aa - fmod(gamma_aa, 1.0e-10);
  gamma_bb = gamma_bb - fmod(gamma_bb, 1.0e-10);
  gamma_ab = gamma_ab - fmod(gamma_ab, 1.0e-10);
  double rou=rou_a+rou_b;
  if(rou<cutoff) return ;
   
  double rou_1_3=pow(rou,1.0/3.0);
  double rou_m1_3=pow(rou,-1.0/3.0);
  double rou_m4_3=rou_m1_3*rou_m1_3*rou_m1_3*rou_m1_3;
  double rou_m5_3=rou_m4_3*rou_m1_3;
  double rou_a_8_3=pow(rou_a,8.0/3.0);
  double rou_b_8_3=pow(rou_b,8.0/3.0);

  const double C1=pow(2.0,11.0/3.0)*(3.0/10.0)*pow(3.0*M_PI*M_PI,2.0/3.0)*a*b;
  double omega=(exp(-c*rou_m1_3)/(1.0+d*rou_m1_3))*pow(rou_m1_3,11.0);
  double delta=c*rou_m1_3+d*rou_m1_3/(1.0+d*rou_m1_3);
  double C2=a*b*omega;
  double C3=(1.0/9.0)*rou_a*rou_b;
  double LYP_aa=-C2*(C3*(1.0-3.0*delta-(delta-11.0)*rou_a/rou)-rou_b*rou_b);
  double LYP_bb=-C2*(C3*(1.0-3.0*delta-(delta-11.0)*rou_b/rou)-rou_a*rou_a);
  double LYP_ab=-C2*(C3*(47.0-7.0*delta)-(4.0/3.0)*rou*rou);

  double omega_deri=-(1.0/3.0)*rou_m4_3*omega*(11.0*rou_1_3-c-d/(1.0+d*rou_m1_3));
  double delta_deri=(1.0/3.0)*(d*d*rou_m5_3/((1.0+d*rou_m1_3)*(1.0+d*rou_m1_3))-delta/rou); 
  double LYP_aaa=0.0,LYP_aab=0.0,LYP_abb=0.0;

  if(fabs(omega)>cutoff){
    LYP_aaa=(omega_deri/omega)*LYP_aa-C2*((1.0/9.0)*rou_b*(1.0-3.0*delta-(delta-11.0)*rou_a/rou)
           -C3*((3.0+rou_a/rou)*delta_deri+(delta-11.0)*rou_b/(rou*rou)));
    LYP_aab=(omega_deri/omega)*LYP_ab-C2*((1.0/9.0)*rou_b*(47.0-7.0*delta)
                                          -7.0*C3*delta_deri-(8.0/3.0)*rou);
    LYP_abb=(omega_deri/omega)*LYP_bb-C2*((1.0/9.0)*rou_b*(1.0-3.0*delta-(delta-11.0)*rou_b/rou)
           -C3*((3.0+rou_b/rou)*delta_deri-(delta-11.0)*rou_b/(rou*rou))-2.0*rou_a);
  }

  ret_lyp=-(4.0*a/(1.0+d*rou_m1_3))*(rou_a*rou_b/rou)-C1*omega*rou_a*rou_b*(rou_a_8_3+rou_b_8_3)
         +LYP_aa*gamma_aa+LYP_ab*gamma_ab+LYP_bb*gamma_bb;
 
  double termA=LYP_aaa*gamma_aa+LYP_aab*gamma_ab+LYP_abb*gamma_bb;
  termA = termA - fmod(termA, 1.0e-10);
  ret_f_rou=-(4.0*a/(1.0+d*rou_m1_3))*(rou_a*rou_b/rou)*((1.0/3.0)*(d*rou_m4_3/(1.0+d*rou_m1_3))+(1.0/rou_a)-(1.0/rou))
           -C1*(omega_deri*rou_a*rou_b*(rou_a_8_3+rou_b_8_3)+omega*rou_b*((11.0/3.0)*rou_a_8_3+rou_b_8_3))+termA;

  ret_f_gamma_aa=LYP_aa;
  ret_f_gamma_ab=LYP_ab;

}

void DFT_func::func_ULYP(double &ret_lyp,double &ret_f_rou_a,double &ret_f_rou_b,
                         double &ret_f_gamma_aa,double &ret_f_gamma_ab,double &ret_f_gamma_bb,
                         double rou_a,double rou_b,double gamma_aa,double gamma_ab,double gamma_bb){
  const double a=0.04918;    const double b=0.132;
  const double c=0.2533;     const double d=0.349;
  int flag_a=1;
  int flag_b=1;
  ret_lyp=0.0;
  ret_f_rou_a=0.0;
  ret_f_rou_b=0.0;
  ret_f_gamma_aa=0.0;
  ret_f_gamma_ab=0.0;

  const double cutoff=1.0e-7;
  rou_a = rou_a-fmod(rou_a, 1.0e-10);
  rou_b = rou_b-fmod(rou_b, 1.0e-10);
  gamma_aa = gamma_aa - fmod(gamma_aa, 1.0e-10);
  gamma_bb = gamma_bb - fmod(gamma_bb, 1.0e-10);
  gamma_ab = gamma_ab - fmod(gamma_ab, 1.0e-10);

  double rou=rou_a+rou_b;
  if(rou<cutoff)  return ;
  if(rou_a<cutoff*0.5){
    flag_a=0; 
  } 
  if(rou_b<cutoff*0.5){
    flag_b=0; 
  }
  
  double rou_1_3=pow(rou,1.0/3.0);
  double rou_m1_3=pow(rou,-1.0/3.0);
  double rou_m4_3=rou_m1_3*rou_m1_3*rou_m1_3*rou_m1_3;
  double rou_m5_3=rou_m4_3*rou_m1_3;
  double rou_a_8_3=pow(rou_a,8.0/3.0);
  double rou_b_8_3=pow(rou_b,8.0/3.0);

  const double C1=pow(2.0,11.0/3.0)*(3.0/10.0)*pow(3.0*M_PI*M_PI,2.0/3.0)*a*b;
  double omega=(exp(-c*rou_m1_3)/(1.0+d*rou_m1_3))*pow(rou_m1_3,11.0);
  double delta=c*rou_m1_3+d*rou_m1_3/(1.0+d*rou_m1_3);
  double C2=a*b*omega;
  double C3=(1.0/9.0)*rou_a*rou_b;
  double LYP_aa=-C2*(C3*(1.0-3.0*delta-(delta-11.0)*rou_a/rou)-rou_b*rou_b);
  double LYP_bb=-C2*(C3*(1.0-3.0*delta-(delta-11.0)*rou_b/rou)-rou_a*rou_a);
  double LYP_ab=-C2*(C3*(47.0-7.0*delta)-(4.0/3.0)*rou*rou);

  double omega_deri=-(1.0/3.0)*rou_m4_3*omega*(11.0*rou_1_3-c-d/(1.0+d*rou_m1_3));
  double delta_deri=(1.0/3.0)*(d*d*rou_m5_3/((1.0+d*rou_m1_3)*(1.0+d*rou_m1_3))-delta/rou); 
  double LYP_aaa,LYP_aab,LYP_abb;
  double LYP_baa,LYP_bab,LYP_bbb;
  LYP_aaa=LYP_aab=LYP_abb=LYP_baa=LYP_bab=LYP_bbb=0.0;

  if(fabs(omega)>cutoff){
    LYP_aaa=(omega_deri/omega)*LYP_aa-C2*((1.0/9.0)*rou_b*(1.0-3.0*delta-(delta-11.0)*rou_a/rou)
           -C3*((3.0+rou_a/rou)*delta_deri+(delta-11.0)*rou_b/(rou*rou)));
    LYP_bbb=(omega_deri/omega)*LYP_bb-C2*((1.0/9.0)*rou_a*(1.0-3.0*delta-(delta-11.0)*rou_b/rou)
           -C3*((3.0+rou_b/rou)*delta_deri+(delta-11.0)*rou_a/(rou*rou)));

    LYP_aab=(omega_deri/omega)*LYP_ab-C2*((1.0/9.0)*rou_b*(47.0-7.0*delta)
                                          -7.0*C3*delta_deri-(8.0/3.0)*rou);
    LYP_bab=(omega_deri/omega)*LYP_ab-C2*((1.0/9.0)*rou_a*(47.0-7.0*delta)
                                          -7.0*C3*delta_deri-(8.0/3.0)*rou);

    LYP_abb=(omega_deri/omega)*LYP_bb-C2*((1.0/9.0)*rou_b*(1.0-3.0*delta-(delta-11.0)*rou_b/rou)
           -C3*((3.0+rou_b/rou)*delta_deri-(delta-11.0)*rou_b/(rou*rou))-2.0*rou_a);
    LYP_baa=(omega_deri/omega)*LYP_aa-C2*((1.0/9.0)*rou_a*(1.0-3.0*delta-(delta-11.0)*rou_a/rou)
           -C3*((3.0+rou_a/rou)*delta_deri-(delta-11.0)*rou_a/(rou*rou))-2.0*rou_b);
  }
 
  ret_lyp=-(4.0*a/(1.0+d*rou_m1_3))*(rou_a*rou_b/rou)-C1*omega*rou_a*rou_b*(rou_a_8_3+rou_b_8_3)
         +LYP_aa*gamma_aa+LYP_ab*gamma_ab+LYP_bb*gamma_bb;


  if(flag_a==1){ 
    double termA=LYP_aaa*gamma_aa+LYP_aab*gamma_ab+LYP_abb*gamma_bb;
    termA = termA - fmod(termA, 1.0e-10);
    ret_f_rou_a=-(4.0*a/(1.0+d*rou_m1_3))*(rou_a*rou_b/rou)*((1.0/3.0)*(d*rou_m4_3/(1.0+d*rou_m1_3))+(1.0/rou_a)-(1.0/rou))
               -C1*(omega_deri*rou_a*rou_b*(rou_a_8_3+rou_b_8_3)+omega*rou_b*((11.0/3.0)*rou_a_8_3+rou_b_8_3))+termA;
  }
  if(flag_b==1){
    double termB=LYP_baa*gamma_aa+LYP_bab*gamma_ab+LYP_bbb*gamma_bb;
    termB = termB - fmod(termB, 1.0e-10);
    ret_f_rou_b=-(4.0*a/(1.0+d*rou_m1_3))*(rou_a*rou_b/rou)*((1.0/3.0)*(d*rou_m4_3/(1.0+d*rou_m1_3))+(1.0/rou_b)-(1.0/rou))
               -C1*(omega_deri*rou_a*rou_b*(rou_a_8_3+rou_b_8_3)+omega*rou_a*((11.0/3.0)*rou_b_8_3+rou_a_8_3))+termB;
  }
  ret_f_gamma_aa=LYP_aa;
  ret_f_gamma_bb=LYP_bb;
  ret_f_gamma_ab=LYP_ab;

}


void  DFT_func::func_LYP_TDDFT(std::vector<double> &ret_v_aa,std::vector<double> &ret_v_ab,
                               double rou_a,double rou_b,double gamma_aa,double gamma_ab,double gamma_bb,double integ_w){

  const double a=0.04918;    const double b=0.132;
  const double c=0.2533;     const double d=0.349;

  double rou=rou_a+rou_b;
  if(rou<1.0e-10){
    for(int i=0;i<8; i++) ret_v_aa[i]=0.0;
    for(int i=0;i<10;i++) ret_v_ab[i]=0.0;
    return ;
  } 
  double rou_1_3=pow(rou,1.0/3.0);
  double rou_m1_3=pow(rou,-1.0/3.0);
  double rou_m4_3=rou_m1_3*rou_m1_3*rou_m1_3*rou_m1_3;
  double rou_m5_3=rou_m4_3*rou_m1_3;
  double rou_a_8_3=pow(rou_a,8.0/3.0);
  double rou_b_8_3=pow(rou_b,8.0/3.0);

  const double C1=pow(2.0,11.0/3.0)*(3.0/10.0)*pow(3.0*M_PI*M_PI,2.0/3.0)*a*b;
  double omega=(exp(-c*rou_m1_3)/(1.0+d*rou_m1_3))*pow(rou_m1_3,11.0);
  double delta=c*rou_m1_3+d*rou_m1_3/(1.0+d*rou_m1_3);
  double C2=a*b*omega;
  double C3=(1.0/9.0)*rou_a*rou_b;
  double LYP_aa=-C2*(C3*(1.0-3.0*delta-(delta-11.0)*rou_a/rou)-rou_b*rou_b);
  double LYP_bb=-C2*(C3*(1.0-3.0*delta-(delta-11.0)*rou_b/rou)-rou_a*rou_a);
  double LYP_ab=-C2*(C3*(47.0-7.0*delta)-(4.0/3.0)*rou*rou);

  double omega_deri=-(1.0/3.0)*rou_m4_3*omega*(11.0*rou_1_3-c-d/(1.0+d*rou_m1_3));
  double delta_deri=(1.0/3.0)*(d*d*rou_m5_3/((1.0+d*rou_m1_3)*(1.0+d*rou_m1_3))-delta/rou); 
  double LYP_aaa,LYP_aab,LYP_abb,LYP_baa,LYP_bab;
  double omega_deri2=0.0;
  double LYP_aaaa=0.0,LYP_aaab=0.0,LYP_aabb=0.0,LYP_abaa=0.0,LYP_abab=0.0,LYP_abbb=0.0;

  if(fabs(omega)<1.0e-10){
    LYP_aaa=0.0;
    LYP_aab=0.0;
    LYP_abb=0.0;
    // tddft
    LYP_baa=0.0;
    LYP_bab=0.0;
  }else{
    LYP_aaa=(omega_deri/omega)*LYP_aa-C2*((1.0/9.0)*rou_b*(1.0-3.0*delta-(delta-11.0)*rou_a/rou)
           -C3*((3.0+rou_a/rou)*delta_deri+(delta-11.0)*rou_b/(rou*rou)));
    LYP_aab=(omega_deri/omega)*LYP_ab-C2*((1.0/9.0)*rou_b*(47.0-7.0*delta)
                                          -7.0*C3*delta_deri-(8.0/3.0)*rou);
    LYP_abb=(omega_deri/omega)*LYP_bb-C2*((1.0/9.0)*rou_b*(1.0-3.0*delta-(delta-11.0)*rou_b/rou)
           -C3*((3.0+rou_b/rou)*delta_deri-(delta-11.0)*rou_b/(rou*rou))-2.0*rou_a);
    // tddft
    LYP_baa=LYP_abb;
    LYP_bab=LYP_aab;
    double LYP_bbb=LYP_aaa;

    omega_deri2=((4.0/9.0)*omega*pow(rou,-7.0/3.0)-(1.0/3.0)*omega_deri*rou_m4_3)
               *(11.0*rou_1_3-c-d/(1.0+d*rou_m1_3))
               -(1.0/3.0)*rou_m4_3*omega*((11.0/3.0)*rou_m1_3*rou_m1_3-(1.0/3.0)*d*d*rou_m4_3/((1.0+d*rou_m1_3)*(1.0+d*rou_m1_3)));
    double delta_deri2=(1.0/3.0)*(-((5.0/3.0)*d*d*pow(rou,-8.0/3.0)+d*d*d*pow(rou,-9.0/3.0))/((1.0+d*rou_m1_3)*(1.0+d*rou_m1_3)*(1.0+d*rou_m1_3))
                      +delta/(rou*rou)-delta_deri/rou); 

    LYP_aaaa=LYP_aa*(-1.0*omega_deri*omega_deri+omega_deri2*omega)/(omega*omega)+(omega_deri/omega)*LYP_aaa
            -a*b*omega_deri*((1.0/9.0)*rou_b*(1.0-3.0*delta-(delta-11.0)*rou_a/rou)
                            -(1.0/9.0)*rou_a*rou_b*((3.0+rou_a/rou)*delta_deri+(delta-11.0)*rou_b/(rou*rou)))
                   -a*b*omega*((1.0/9.0)*rou_b*(-6.0*delta_deri-2.0*delta_deri*rou_a/rou-2.0*(delta-11.0)*rou_b/(rou*rou))
                              -(1.0/9.0)*rou_a*rou_b*((3.0+rou_a/rou)*delta_deri2+2.0*delta_deri*rou_b/(rou*rou)-2.0*(delta-11.0)*rou_b/(rou*rou*rou)));
    LYP_aaab=LYP_ab*(-1.0*omega_deri*omega_deri+omega_deri2*omega)/(omega*omega)+(omega_deri/omega)*LYP_aab
            -a*b*omega_deri*((1.0/9.0)*rou_b*(47.0-7.0*delta)-(7.0/9.0)*rou_a*rou_b*delta_deri-(8.0/3.0)*rou)
            -a*b*omega*((-14.0/9.0)*rou_b*delta_deri-(7.0/9.0)*rou_a*rou_b*delta_deri2-(8.0/3.0));
    LYP_aabb=LYP_bb*(-1.0*omega_deri*omega_deri+omega_deri2*omega)/(omega*omega)+(omega_deri/omega)*LYP_abb
            -a*b*omega_deri*((1.0/9.0)*rou_b*(1.0-3.0*delta-(delta-11.0)*rou_b/rou)
                            -(1.0/9.0)*rou_a*rou_b*((3.0+rou_b/rou)*delta_deri-(delta-11.0)*rou_b/(rou*rou))-2.0*rou_a)
            -a*b*omega*((1.0/9.0)*rou_b*(-6.0*delta_deri-2.0*delta_deri*rou_b/rou+2.0*(delta-11.0)*rou_b/(rou*rou))
                       -(1.0/9.0)*rou_a*rou_b*((-2.0*rou_b/(rou*rou))*delta_deri+(3.0+rou_b/rou)*delta_deri2
                                               +2.0*(delta-11.0)*rou_b/(rou*rou*rou))-2.0);
    LYP_abaa=LYP_aa*(-1.0*omega_deri*omega_deri+omega_deri2*omega)/(omega*omega)+(omega_deri/omega)*LYP_baa
            -a*b*omega_deri*((1.0/9.0)*rou_b*(1.0-3.0*delta-(delta-11.0)*rou_a/rou)
                            -(1.0/9.0)*rou_a*rou_b*((3.0+rou_a/rou)*delta_deri+(delta-11.0)*rou_b/(rou*rou)))
            -a*b*omega*((1.0/9.0)*(1.0-3.0*delta-(delta-11.0)*rou_a/rou)
                       +(1.0/9.0)*rou_b*(-3.0*delta_deri-delta_deri*rou_a/rou+(delta-11.0)*rou_a/(rou*rou))
                       -(1.0/9.0)*rou_a*((3.0+rou_a/rou)*delta_deri+(delta-11.0)*rou_b/(rou*rou))
                       -(1.0/9.0)*rou_a*rou_b*((3.0+rou_a/rou)*delta_deri2+(rou_b-rou_a)*delta_deri/(rou*rou)+(delta-11.0)*(1.0/(rou*rou)-2.0*rou_b/(rou*rou*rou))));
    LYP_abab=LYP_ab*(-1.0*omega_deri*omega_deri+omega_deri2*omega)/(omega*omega)+(omega_deri/omega)*LYP_bab
            -a*b*omega_deri*((1.0/9.0)*rou_b*(47.0-7.0*delta)-(7.0/9.0)*rou_a*rou_b*delta_deri-(8.0/3.0)*rou)
            -a*b*omega*((-7.0/9.0)*delta-(7.0/9.0)*rou*delta_deri-(7.0/9.0)*rou_a*rou_b*delta_deri2+23.0/9.0);
    LYP_abbb=LYP_bb*(-1.0*omega_deri*omega_deri+omega_deri2*omega)/(omega*omega)+(omega_deri/omega)*LYP_bbb
            -a*b*omega_deri*((1.0/9.0)*rou_b*(1.0-3.0*delta-(delta-11.0)*rou_b/rou)
                            -(1.0/9.0)*rou_a*rou_b*((3.0+rou_b/rou)*delta_deri-(delta-11.0)*rou_b/(rou*rou))-2.0*rou_a)
            -a*b*omega*((1.0/9.0)*(1.0-3.0*delta-(delta-11.0)*rou_b/rou)
                       +(1.0/9.0)*rou_b*(-3.0*delta_deri-delta_deri*rou_b/rou-(delta-11.0)*(rou_a/(rou*rou)))
                       -(1.0/9.0)*rou_a*((3.0+rou_b/rou)*delta_deri-(delta-11.0)*rou_b/(rou*rou))
                       -(1.0/9.0)*rou_a*rou_b*((3.0+rou_b/rou)*delta_deri2+(rou_a-rou_b)/(rou*rou)*delta_deri
                                              -(delta-11.0)*(1.0/(rou*rou)-2.0*rou_b/(rou*rou*rou))));
  }

 
  double LYP_rou_aa,LYP_rou_ab;
  LYP_rou_aa=(-4.0/3.0)*a*d*pow(rou,-4.0/3.0)/((1.0+d*rou_m1_3)*(1.0+d*rou_m1_3))*rou_a*rou_b/rou*((1.0/3.0)*d*rou_m4_3/(1.0+d*rou_m1_3)+1.0/rou_a-1.0/rou)
            -(4.0*a/(1.0+d*rou_m1_3))*rou_b*rou_b/(rou*rou)*((1.0/3.0)*d*rou_m4_3/(1.0+d*rou_m1_3)+1.0/rou_a-1.0/rou) 
            -(4.0*a/(1.0+d*rou_m1_3))*(rou_a*rou_b/rou)*((-1.0/3.0)*(d*d*pow(rou,-8.0/3.0)+(4.0/3.0)*d*pow(rou,-7.0/3.0))/((1.0+d*rou_m1_3)*(1.0+d*rou_m1_3))
                                                         -1.0/(rou_a*rou_a)+1.0/(rou*rou) )
            -C1*(omega_deri2*rou_a*rou_b*(rou_a_8_3+rou_b_8_3)+2.0*omega_deri*rou_b*((11.0/3.0)*rou_a_8_3+rou_b_8_3)+omega*rou_b*(88.0/9.0)*pow(rou_a,5.0/3.0))
            +LYP_aaaa*gamma_aa+LYP_aaab*gamma_ab+LYP_aabb*gamma_bb;

  LYP_rou_ab=(-4.0/3.0)*a*d*pow(rou,-4.0/3.0)/((1.0+d*rou_m1_3)*(1.0+d*rou_m1_3))*rou_a*rou_b/rou*((1.0/3.0)*d*rou_m4_3/(1.0+d*rou_m1_3)+1.0/rou_a-1.0/rou)
            -(4.0*a/(1.0+d*rou_m1_3))*rou_a*rou_a/(rou*rou)*((1.0/3.0)*d*rou_m4_3/(1.0+d*rou_m1_3)+1.0/rou_a-1.0/rou) 
            -(4.0*a/(1.0+d*rou_m1_3))*(rou_a*rou_b/rou)*((-1.0/3.0)*(d*d*pow(rou,-8.0/3.0)+(4.0/3.0)*d*pow(rou,-7.0/3.0))/((1.0+d*rou_m1_3)*(1.0+d*rou_m1_3))+1.0/(rou*rou))
            -C1*(omega_deri2*rou_a*rou_b*(rou_a_8_3+rou_b_8_3)+omega_deri*rou_a*(rou_a_8_3+(11.0/3.0)*rou_b_8_3)
                                         +omega_deri*rou_b*((11.0/3.0)*rou_a_8_3+rou_b_8_3)+omega*(11.0/3.0)*(rou_a_8_3+rou_b_8_3))
            +LYP_abaa*gamma_aa+LYP_abab*gamma_ab+LYP_abbb*gamma_bb;

  ret_v_aa.reserve(8);
  ret_v_ab.reserve(8);
  ret_v_aa.clear();
  ret_v_ab.clear();
  for(int i=0;i<8;i++){
    ret_v_aa.push_back(0.0);
    ret_v_ab.push_back(0.0);
  }

  ret_v_aa[0]=LYP_rou_aa;
  ret_v_aa[1]=LYP_aa;
  ret_v_aa[2]=LYP_aaa;
  ret_v_aa[3]=LYP_aab;
  ret_v_aa[4]=0.0;
  ret_v_aa[5]=0.0;
  ret_v_aa[6]=0.0;
  ret_v_aa[7]=0.0;

  ret_v_ab[0]=LYP_rou_ab;
  ret_v_ab[1]=LYP_ab;
  ret_v_ab[2]=LYP_abb;
  ret_v_ab[3]=LYP_baa;
  ret_v_ab[4]=LYP_aab;
  ret_v_ab[5]=LYP_bab;
  ret_v_ab[6]=0.0;
  ret_v_ab[7]=0.0;
  ret_v_ab[8]=0.0;
  ret_v_ab[9]=0.0;

}




}  // end of namespace "Lotus_core"

#endif // end of include-guard



