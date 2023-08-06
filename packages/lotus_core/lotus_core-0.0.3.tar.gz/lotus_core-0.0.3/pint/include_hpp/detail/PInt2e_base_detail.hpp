
#ifndef PINT2E_DETAIL_HPP
#define PINT2E_DETAIL_HPP


#define _USE_MATH_DEFINES
#include <math.h>
#include <time.h>
#include <stdlib.h>

#include <iostream>
#include <iomanip>
#include <fstream>

#include "Table_Fm_T.hpp"

namespace PInt {

using namespace std;

template <int in_tN>
void PInt2e_base<in_tN>::show_state(){
  cout<<" ----- PInt2e_base<double> ----- "<<endl;
  cout<<"   g  "<<g1<<" "<<g2<<" "<<g3<<" "<<g4<<endl;
  cout<<"   R1 "<<R1[0]<<" "<<R1[1]<<" "<<R1[2]<<endl;
  cout<<"   R2 "<<R2[0]<<" "<<R2[1]<<" "<<R2[2]<<endl;
  cout<<"   R3 "<<R3[0]<<" "<<R3[1]<<" "<<R3[2]<<endl;
  cout<<"   R4 "<<R4[0]<<" "<<R4[1]<<" "<<R4[2]<<endl;
  cout<<"   P  "<<P[0]<<" "<<P[1]<<" "<<P[2]<<endl;
  cout<<"   Q  "<<Q[0]<<" "<<Q[1]<<" "<<Q[2]<<endl;
  cout<<"   W  "<<W[0]<<" "<<W[1]<<" "<<W[2]<<endl;
  cout<<"   t1,t2,rou "<<t1<<" "<<t2<<" "<<rou<<endl;
  cout<<"   ss1,ss2,CC,T "<<ss1<<" "<<ss2<<" "<<CC<<" "<<T<<endl;
  cout<<"   save_tn "<<save_tn<<endl;
  for(int m=0;m<=save_tn;m++){
    cout<<"     m="<<m<<"  vrr4_ssss "<<vrr4_ssss[m]<<" vrr3_sss "<<vrr3_sss[m]<<endl;
  }
}

//
//  Common
//

template <int in_tN>
double PInt2e_base<in_tN>::cal_ss(double in_g1,const double in_R1[3],
                               double in_g2,const double in_R2[3]){

  double tt1=in_g1+in_g2;

  double bb=in_g1*in_g2/tt1;
  double ret_ss = (M_PI/tt1)*sqrt(M_PI/tt1)*
           exp(-bb*((in_R1[0]-in_R2[0])*(in_R1[0]-in_R2[0])
                   +(in_R1[1]-in_R2[1])*(in_R1[1]-in_R2[1])+
                    (in_R1[2]-in_R2[2])*(in_R1[2]-in_R2[2])));
  return ret_ss;
}


template <int in_tN>
double PInt2e_base<in_tN>::cal_I(double in_g,const std::vector<int> &in_n){
  // nnn = n!!
  int nnn[12];
  nnn[0] =1;  nnn[1] =1;  nnn[2] =1;  nnn[3] =2;  nnn[4] =3; nnn[5] =8;
  nnn[6] =15; nnn[7] =48; nnn[8] =105;nnn[9] =384;nnn[10] =945;
  return pow((2*in_g/M_PI),3.0/4.0)*pow(4*in_g,(in_n[0]+in_n[1]+in_n[2])/2.0)/
             sqrt(nnn[2*in_n[0]]*nnn[2*in_n[1]]*nnn[2*in_n[2]]);
}



template <int in_tN>
std::vector<double> PInt2e_base<in_tN>::cal_dI(int in_st,double in_g,double in_d){
  std::vector<double> ret_dI;
  int num=get_num(in_st);
  for(int i=0;i<num;i++){
    std::vector<int> tmp_n = get_no_to_n(in_st,i);
    ret_dI.push_back(in_d*cal_I(in_g,tmp_n));
  }
  return ret_dI;
}



template <int in_tN>
//void PInt2e_base<in_tN>::set_gR_12(double in_g1,const std::vector<double> &in_R1,
//                                    double in_g2,const std::vector<double> &in_R2){
void PInt2e_base<in_tN>::set_gR_12(double in_g1,const double *in_R1,
                                    double in_g2,const double *in_R2){
  g1=in_g1;
  g2=in_g2;
  R1[0]=in_R1[0];
  R1[1]=in_R1[1];
  R1[2]=in_R1[2];
  R2[0]=in_R2[0];
  R2[1]=in_R2[1];
  R2[2]=in_R2[2];

  t1=g1+g2;
  c_0_5_div_t1 = 0.5 / t1;

  P[0]=(g1*R1[0]+g2*R2[0])/(g1+g2);
  P[1]=(g1*R1[1]+g2*R2[1])/(g1+g2);
  P[2]=(g1*R1[2]+g2*R2[2])/(g1+g2);

  ss1=PInt2e_base<in_tN>::cal_ss(g1,R1,g2,R2);
}

template <int in_tN>
//void PInt2e_base<in_tN>::set_gR_34(double in_g3,const std::vector<double> &in_R3,
//                                    double in_g4,const std::vector<double> &in_R4){
void PInt2e_base<in_tN>::set_gR_34(double in_g3,const double *in_R3,
                                    double in_g4,const double *in_R4){

  g3=in_g3;
  g4=in_g4;
  R3[0]=in_R3[0];
  R3[1]=in_R3[1];
  R3[2]=in_R3[2];
  R4[0]=in_R4[0];
  R4[1]=in_R4[1];
  R4[2]=in_R4[2];

  t2=g3+g4;
  c_0_5_div_t2 = 0.5 / t2;
  c_0_5_div_t1_plus_t2 = 0.5 / (t1 + t2);
  rou=t1*t2/(t1+t2);
  rou_div_t1 = rou / t1;
  rou_div_t2 = rou / t2;

  Q[0]=(g3*R3[0]+g4*R4[0])/(g3+g4);
  Q[1]=(g3*R3[1]+g4*R4[1])/(g3+g4);
  Q[2]=(g3*R3[2]+g4*R4[2])/(g3+g4);

  W[0]=(t1*P[0]+t2*Q[0])/(t1+t2);
  W[1]=(t1*P[1]+t2*Q[1])/(t1+t2);
  W[2]=(t1*P[2]+t2*Q[2])/(t1+t2);

  ss2=PInt2e_base<in_tN>::cal_ss(g3,R3,g4,R4);
  T=rou*((P[0]-Q[0])*(P[0]-Q[0])+(P[1]-Q[1])*(P[1]-Q[1])+(P[2]-Q[2])*(P[2]-Q[2]));
  CC=(2.0/sqrt(M_PI))*sqrt(rou)*ss1*ss2;
}


template <int in_tN>
void PInt2e_base<in_tN>::set_eri_ssss(int tn,int mode_erfc,double omega_erfc){
  save_tn=tn;
  if(mode_erfc==0){
    for(int m=0;m<=tn;m++)  vrr4_ssss[m]=CC*cal_Fm_T<double>(m,T);
  }else if(mode_erfc==1){ // short range
    double erf_v1=1.0/rou;
    double erf_v2=1.0/(erf_v1+1.0/(omega_erfc*omega_erfc));
    double T_erf=erf_v2*((P[0]-Q[0])*(P[0]-Q[0])+(P[1]-Q[1])*(P[1]-Q[1])+(P[2]-Q[2])*(P[2]-Q[2])); 
    double CC_erf=(2.0/sqrt(M_PI))*sqrt(erf_v2)*ss1*ss2;
    for(int m=0;m<=tn;m++)  vrr4_ssss[m]=CC*cal_Fm_T<double>(m,T);
    for(int m=0;m<=tn;m++)  vrr4_ssss[m]-=CC_erf*pow(erf_v1*erf_v2,m)*cal_Fm_T<double>(m,T_erf);
  }else if(mode_erfc==2){ // long range
    double erf_v1=1.0/rou;
    double erf_v2=1.0/(erf_v1+1.0/(omega_erfc*omega_erfc));
    double T_erf=erf_v2*((P[0]-Q[0])*(P[0]-Q[0])+(P[1]-Q[1])*(P[1]-Q[1])+(P[2]-Q[2])*(P[2]-Q[2])); 
    double CC_erf=(2.0/sqrt(M_PI))*sqrt(erf_v2)*ss1*ss2;
    for(int m=0;m<=tn;m++)  vrr4_ssss[m]=CC_erf*pow(erf_v1*erf_v2,m)*cal_Fm_T<double>(m,T_erf);
  }
}

template <int in_tN>
void PInt2e_base<in_tN>::ERI_recursion(std::vector<double> &ret_eri,int tn1,int tn2,int tn3,int tn4,
                                const std::vector<double> &dI_a,const std::vector<double> &dI_b,
                                const std::vector<double> &dI_c,const std::vector<double> &dI_d){
  int num1=get_num(tn1);
  int num2=get_num(tn2);
  int num3=get_num(tn3);
  int num4=get_num(tn4);
  //int N1234=num1*num2*num3*num4;
  ERI_recursion_sub(&ret_eri[0],tn1,tn2,tn3,tn4,0);
  for(int i1=0;i1<num1;i1++){
    for(int i2=0;i2<num2;i2++){
      for(int i3=0;i3<num3;i3++){
        for(int i4=0;i4<num4;i4++){
          ret_eri[i1*num2*num3*num4+i2*num3*num4+i3*num4+i4]*=dI_a[i1]*dI_b[i2]*dI_c[i3]*dI_d[i4];
        }
      }
    }
  }


}



template <int in_tN>
void PInt2e_base<in_tN>::ERI_recursion_sub(double *ret_eri,int tn1,int tn2,int tn3,int tn4,int m){
  if(tn1+tn2+tn3+tn4==0){
    ret_eri[0]=vrr4_ssss[m];
    return;
  }
  //int n1[3],n2[3],n3[3],n4[3];
  int num1=get_num(tn1);
  int num2=get_num(tn2);
  int num3=get_num(tn3);
  int num4=get_num(tn4);
  int N1234=num1*num2*num3*num4;
  double *t_eri_1 = new double [N1234];
  double *t_eri_2 = new double [N1234];
  double *t_eri_3 = new double [N1234];
  double *t_eri_4 = new double [N1234];
  double *t_eri_5 = new double [N1234];
  double *t_eri_6 = new double [N1234];
  double *t_eri_7 = new double [N1234];
  double *t_eri_8 = new double [N1234];
  if(tn1>=1){
    ERI_recursion_sub(t_eri_1,tn1-1,tn2,  tn3,  tn4,m  );
    ERI_recursion_sub(t_eri_2,tn1-1,tn2,  tn3,  tn4,m+1);
    if(tn1>=2) ERI_recursion_sub(t_eri_3,tn1-2,tn2  ,tn3,  tn4,m  );
    if(tn1>=2) ERI_recursion_sub(t_eri_4,tn1-2,tn2  ,tn3,  tn4,m+1);
    if(tn2>=1) ERI_recursion_sub(t_eri_5,tn1-1,tn2-1,tn3,  tn4,m  );
    if(tn2>=1) ERI_recursion_sub(t_eri_6,tn1-1,tn2-1,tn3,  tn4,m+1);
    if(tn3>=1) ERI_recursion_sub(t_eri_7,tn1-1,tn2,  tn3-1,tn4,m+1);
    if(tn4>=1) ERI_recursion_sub(t_eri_8,tn1-1,tn2,  tn3,tn4-1,m+1);

    for(int i1=0;i1<num1;i1++){
      for(int i2=0;i2<num2;i2++){
        for(int i3=0;i3<num3;i3++){
          for(int i4=0;i4<num4;i4++){
            int n1[3],n2[3],n3[3],n4[3],n1_m[3],n2_m[3],n3_m[3],n4_m[3];
            set_n1234(n1,n2,n3,n4,i1,i2,i3,i4,tn1,tn2,tn3,tn4);
            int xyz=get_xyz(n1);
            set_n1234_m(n1_m,n2_m,n3_m,n4_m,n1,n2,n3,n4,xyz);

            int num1_m=get_num(tn1-1);
            int i1_m=basis_index::n_to_no[n1_m[0]][n1_m[1]][n1_m[2]];
            int ind_a=i1_m*num2*num3*num4+i2*num3*num4+i3*num4+i4;
 
            double tmp_v=(P[xyz]-R1[xyz])*t_eri_1[ind_a]
                        +(W[xyz]- P[xyz])*t_eri_2[ind_a];

            if(n1_m[xyz]>0){
              int n1_m2[3]={n1[0],n1[1],n1[2]};
              n1_m2[xyz]-=2;
              int num1_m2=get_num(tn1-2);
              int i1_m2=basis_index::n_to_no[n1_m2[0]][n1_m2[1]][n1_m2[2]];
              int ind_b=i1_m2*num2*num3*num4+i2*num3*num4+i3*num4+i4;
              tmp_v+=(0.5/t1)*n1_m[xyz]*(t_eri_3[ind_b]-(rou/t1)*t_eri_4[ind_b]);
            }

            if(n2_m[xyz]>=0){
              int num2_m=get_num(tn2-1);
              int i2_m=basis_index::n_to_no[n2_m[0]][n2_m[1]][n2_m[2]];
              int ind_c=i1_m*num2_m*num3*num4+i2_m*num3*num4+i3*num4+i4;
              tmp_v+=(0.5/t1)*n2[xyz]*(t_eri_5[ind_c]-(rou/t1)*t_eri_6[ind_c]);
                            
            }

            if(n3_m[xyz]>=0){
              int num3_m=get_num(tn3-1);
              int i3_m=basis_index::n_to_no[n3_m[0]][n3_m[1]][n3_m[2]];
              int ind_d=i1_m*num2*num3_m*num4+i2*num3_m*num4+i3_m*num4+i4;
              tmp_v+=(0.5/(t1+t2))*n3[xyz]*t_eri_7[ind_d];
            }

            if(n4_m[xyz]>=0){
              int num4_m=get_num(tn4-1);
              int i4_m=basis_index::n_to_no[n4_m[0]][n4_m[1]][n4_m[2]];
              int ind_e=i1_m*num2*num3*num4_m+i2*num3*num4_m+i3*num4_m+i4_m;
              tmp_v+=(0.5/(t1+t2))*n4[xyz]*t_eri_8[ind_e];
            }
            int ind=i1*num2*num3*num4+i2*num3*num4+i3*num4+i4;
            ret_eri[ind]=tmp_v;
          }
        }
      }
    }


  }else if(tn2>=1){
  
  
    ERI_recursion_sub(t_eri_1,tn1,  tn2-1,tn3,  tn4,m  );
    ERI_recursion_sub(t_eri_2,tn1,  tn2-1,tn3,  tn4,m+1);
    if(tn2>=2) ERI_recursion_sub(t_eri_3,tn1,  tn2-2,tn3,  tn4,m  );
    if(tn2>=2) ERI_recursion_sub(t_eri_4,tn1,  tn2-2,tn3,  tn4,m+1);
    if(tn3>=1) ERI_recursion_sub(t_eri_7,tn1,  tn2-1,tn3-1,tn4,m+1);
    if(tn4>=1) ERI_recursion_sub(t_eri_8,tn1,  tn2-1,tn3,tn4-1,m+1);

    int i1=0;
    for(int i2=0;i2<num2;i2++){
      for(int i3=0;i3<num3;i3++){
        for(int i4=0;i4<num4;i4++){
          int n1[3],n2[3],n3[3],n4[3],n1_m[3],n2_m[3],n3_m[3],n4_m[3];
          set_n1234(n1,n2,n3,n4,i1,i2,i3,i4,tn1,tn2,tn3,tn4);
          int xyz=get_xyz(n2);
          set_n1234_m(n1_m,n2_m,n3_m,n4_m,n1,n2,n3,n4,xyz);

          int num2_m=get_num(tn2-1);
          int i2_m=basis_index::n_to_no[n2_m[0]][n2_m[1]][n2_m[2]];
          int ind_a=i1*num2_m*num3*num4+i2_m*num3*num4+i3*num4+i4;

          double tmp_v=(P[xyz]-R2[xyz])*t_eri_1[ind_a]
                      +(W[xyz]- P[xyz])*t_eri_2[ind_a];

          if(n2_m[xyz]>0){
            int n2_m2[3]={n2[0],n2[1],n2[2]};
            n2_m2[xyz]-=2;
            int num2_m2=get_num(tn2-2);
            int i2_m2=basis_index::n_to_no[n2_m2[0]][n2_m2[1]][n2_m2[2]];
            int ind_b=i1*num2_m2*num3*num4+i2_m2*num3*num4+i3*num4+i4;
            tmp_v+=(0.5/t1)*n2_m[xyz]*(t_eri_3[ind_b]-(rou/t1)*t_eri_4[ind_b]);
          }

          if(n3_m[xyz]>=0){
            int num3_m=get_num(tn3-1);
            int i3_m=basis_index::n_to_no[n3_m[0]][n3_m[1]][n3_m[2]];
            int ind_d=i1*num2_m*num3_m*num4+i2_m*num3_m*num4+i3_m*num4+i4;
            tmp_v+=(0.5/(t1+t2))*n3[xyz]*t_eri_7[ind_d];
          }

          if(n4_m[xyz]>=0){
            int num4_m=get_num(tn4-1);
            int i4_m=basis_index::n_to_no[n4_m[0]][n4_m[1]][n4_m[2]];
            int ind_e=i1*num2_m*num3*num4_m+i2_m*num3*num4_m+i3*num4_m+i4_m;
            tmp_v+=(0.5/(t1+t2))*n4[xyz]*t_eri_8[ind_e];
          }
          int ind=i1*num2*num3*num4+i2*num3*num4+i3*num4+i4;
          ret_eri[ind]=tmp_v;
        }
      }
    }

  }else if(tn3>=1){

    ERI_recursion_sub(t_eri_1,tn1,  tn2,  tn3-1,tn4  ,m  );
    ERI_recursion_sub(t_eri_2,tn1,  tn2,  tn3-1,tn4  ,m+1);
    if(tn3>=2) ERI_recursion_sub(t_eri_3,tn1,  tn2,  tn3-2,tn4  ,m  );
    if(tn3>=2) ERI_recursion_sub(t_eri_4,tn1,  tn2,  tn3-2,tn4  ,m+1);
    if(tn4>=1) ERI_recursion_sub(t_eri_5,tn1,  tn2,  tn3-1,tn4-1,m  );
    if(tn4>=1) ERI_recursion_sub(t_eri_6,tn1,  tn2,  tn3-1,tn4-1,m+1);

    int i1=0;
    int i2=0;
    for(int i3=0;i3<num3;i3++){
      for(int i4=0;i4<num4;i4++){
        int n1[3],n2[3],n3[3],n4[3],n1_m[3],n2_m[3],n3_m[3],n4_m[3];
        set_n1234(n1,n2,n3,n4,i1,i2,i3,i4,tn1,tn2,tn3,tn4);
        int xyz=get_xyz(n3);
        set_n1234_m(n1_m,n2_m,n3_m,n4_m,n1,n2,n3,n4,xyz);

        int num3_m=get_num(tn3-1);
        int i3_m=basis_index::n_to_no[n3_m[0]][n3_m[1]][n3_m[2]];
        int ind_a=i1*num2*num3_m*num4+i2*num3_m*num4+i3_m*num4+i4;
 
        double tmp_v=(Q[xyz]-R3[xyz])*t_eri_1[ind_a]
                    +(W[xyz]- Q[xyz])*t_eri_2[ind_a];

        if(n3_m[xyz]>0){
          int n3_m2[3]={n3[0],n3[1],n3[2]};
          n3_m2[xyz]-=2;
          int num3_m2=get_num(tn3-2);
          int i3_m2=basis_index::n_to_no[n3_m2[0]][n3_m2[1]][n3_m2[2]];
          int ind_b=i1*num2*num3_m2*num4+i2*num3_m2*num4+i3_m2*num4+i4;
          tmp_v+=(0.5/t2)*n3_m[xyz]*(t_eri_3[ind_b]-(rou/t2)*t_eri_4[ind_b]);
        }

        if(n4_m[xyz]>=0){
          int num4_m=get_num(tn4-1);
          int i4_m=basis_index::n_to_no[n4_m[0]][n4_m[1]][n4_m[2]];
          int ind_c=i1*num2*num3_m*num4_m+i2*num3_m*num4_m+i3_m*num4_m+i4_m;
          tmp_v+=(0.5/t2)*n4[xyz]*(t_eri_5[ind_c]-(rou/t2)*t_eri_6[ind_c]);
        }

        int ind=i1*num2*num3*num4+i2*num3*num4+i3*num4+i4;
        ret_eri[ind]=tmp_v;
      }
    }

  }else if(tn4>=1){

    ERI_recursion_sub(t_eri_1,tn1,  tn2,  tn3,  tn4-1,m  );
    ERI_recursion_sub(t_eri_2,tn1,  tn2,  tn3,  tn4-1,m+1);
    if(tn4>=2) ERI_recursion_sub(t_eri_3,tn1,  tn2,  tn3,  tn4-2,m  );
    if(tn4>=2) ERI_recursion_sub(t_eri_4,tn1,  tn2,  tn3,  tn4-2,m+1);

    int i1=0;
    int i2=0;
    int i3=0;
    for(int i4=0;i4<num4;i4++){
      int n1[3],n2[3],n3[3],n4[3],n1_m[3],n2_m[3],n3_m[3],n4_m[3];
      set_n1234(n1,n2,n3,n4,i1,i2,i3,i4,tn1,tn2,tn3,tn4);
      int xyz=get_xyz(n4);
      set_n1234_m(n1_m,n2_m,n3_m,n4_m,n1,n2,n3,n4,xyz);

      int num4_m=get_num(tn4-1);
      int i4_m=basis_index::n_to_no[n4_m[0]][n4_m[1]][n4_m[2]];
      int ind_a=i1*num2*num3*num4_m+i2*num3*num4_m+i3*num4_m+i4_m;
 
      double tmp_v=(Q[xyz]-R4[xyz])*t_eri_1[ind_a]
                  +(W[xyz]- Q[xyz])*t_eri_2[ind_a];

      if(n4_m[xyz]>0){
        int n4_m2[3]={n4[0],n4[1],n4[2]};
        n4_m2[xyz]-=2;
        int num4_m2=get_num(tn4-2);
        int i4_m2=basis_index::n_to_no[n4_m2[0]][n4_m2[1]][n4_m2[2]];
        int ind_b=i1*num2*num3*num4_m2+i2*num3*num4_m2+i3*num4_m2+i4_m2;
        tmp_v+=(0.5/t2)*n4_m[xyz]*(t_eri_3[ind_b]-(rou/t2)*t_eri_4[ind_b]);
      }

      int ind=i1*num2*num3*num4+i2*num3*num4+i3*num4+i4;
      ret_eri[ind]=tmp_v;
    }

  }


  delete [] t_eri_1;
  delete [] t_eri_2;
  delete [] t_eri_3;
  delete [] t_eri_4;
  delete [] t_eri_5;
  delete [] t_eri_6;
  delete [] t_eri_7;
  delete [] t_eri_8;

}

//
//  Simple
//

template <int in_tN>
double PInt2e_base<in_tN>::ERI_m_simple(const int n1[3],const int n2[3],const int n3[3],const int n4[3],int m){
  int tn1,tn2,tn3,tn4;
  tn1=n1[0]+n1[1]+n1[2];
  tn2=n2[0]+n2[1]+n2[2];
  tn3=n3[0]+n3[1]+n3[2];
  tn4=n4[0]+n4[1]+n4[2];
  if(tn1+tn2+tn3+tn4==0){
    return vrr4_ssss[m];
  }
  double ret;
 if(tn1>=1){
    if(n1[0]>0)      ret=ERI_m_simple_sub1(n1,n2,n3,n4,m,0);
    else if(n1[1]>0) ret=ERI_m_simple_sub1(n1,n2,n3,n4,m,1);
    else             ret=ERI_m_simple_sub1(n1,n2,n3,n4,m,2);
    return ret;
  }else if(tn2>=1){
    if(n2[0]>0)      ret=ERI_m_simple_sub2(n1,n2,n3,n4,m,0);
    else if(n2[1]>0) ret=ERI_m_simple_sub2(n1,n2,n3,n4,m,1);
    else             ret=ERI_m_simple_sub2(n1,n2,n3,n4,m,2);
    return ret;
  }else if(tn3>=1){
    if(n3[0]>0)      ret=ERI_m_simple_sub3(n1,n2,n3,n4,m,0);
    else if(n3[1]>0) ret=ERI_m_simple_sub3(n1,n2,n3,n4,m,1);
    else             ret=ERI_m_simple_sub3(n1,n2,n3,n4,m,2);
    return ret;
  }else{ 
    if(n4[0]>0)      ret=ERI_m_simple_sub4(n1,n2,n3,n4,m,0);
    else if(n4[1]>0) ret=ERI_m_simple_sub4(n1,n2,n3,n4,m,1);
    else             ret=ERI_m_simple_sub4(n1,n2,n3,n4,m,2);
    return ret;
  }
}


template <int in_tN>
double PInt2e_base<in_tN>::ERI_m_simple_sub1(const int n1[3],const int n2[3],
                                          const int n3[3],const int n4[3],int m,int xyz){ 
                                          

  int tmp_n0[3],tmp_n1[3],tmp_n2[3],tmp_n3[3],tmp_n4[3];
    tmp_n1[0]=n1[0];tmp_n0[0]=n1[0];
    tmp_n2[0]=n2[0];
    tmp_n3[0]=n3[0];
    tmp_n4[0]=n4[0];
    tmp_n1[1]=n1[1];tmp_n0[1]=n1[1];
    tmp_n2[1]=n2[1];
    tmp_n3[1]=n3[1];
    tmp_n4[1]=n4[1];
    tmp_n1[2]=n1[2];tmp_n0[2]=n1[2];
    tmp_n2[2]=n2[2];
    tmp_n3[2]=n3[2];
    tmp_n4[2]=n4[2];

  tmp_n0[xyz]--;
  tmp_n1[xyz]--; tmp_n1[xyz]--;
  tmp_n2[xyz]--;
  tmp_n3[xyz]--;
  tmp_n4[xyz]--;

  double ret=0;
  ret=(P[xyz]-R1[xyz])*ERI_m_simple(tmp_n0,n2,n3,n4,m)
     +(W[xyz]- P[xyz])*ERI_m_simple(tmp_n0,n2,n3,n4,m+1);
  if(tmp_n0[xyz]!=0){
    ret+=(0.5/t1)*tmp_n0[xyz]*(ERI_m_simple(tmp_n1,n2,n3,n4,m)
                     -(rou/t1)*ERI_m_simple(tmp_n1,n2,n3,n4,m+1));
  }
  if(n2[xyz]!=0)
    ret+=(0.5/t1)*n2[xyz]*(ERI_m_simple(tmp_n0,tmp_n2,n3,n4,m)
                 -(rou/t1)*ERI_m_simple(tmp_n0,tmp_n2,n3,n4,m+1));
  if(n3[xyz]!=0)
    ret+=(0.5/(t1+t2))*n3[xyz]*ERI_m_simple(tmp_n0,n2,tmp_n3,n4,m+1);
  if(n4[xyz]!=0)
    ret+=(0.5/(t1+t2))*n4[xyz]*ERI_m_simple(tmp_n0,n2,n3,tmp_n4,m+1);
  return ret;
}

template <int in_tN>
double PInt2e_base<in_tN>::ERI_m_simple_sub2(const int n1[3],const int n2[3],const int n3[3],const int n4[3],int m,int xyz){ 
                                          
                                          
	
  int tmp_n0[3],tmp_n1[3],tmp_n2[3],tmp_n3[3],tmp_n4[3];
    tmp_n1[0]=n1[0];
    tmp_n2[0]=n2[0];tmp_n0[0]=n2[0];
    tmp_n3[0]=n3[0];
    tmp_n4[0]=n4[0];
    tmp_n1[1]=n1[1];
    tmp_n2[1]=n2[1];tmp_n0[1]=n2[1];
    tmp_n3[1]=n3[1];
    tmp_n4[1]=n4[1];
    tmp_n1[2]=n1[2];
    tmp_n2[2]=n2[2];tmp_n0[2]=n2[2];
    tmp_n3[2]=n3[2];
    tmp_n4[2]=n4[2];

  tmp_n0[xyz]--;
  tmp_n1[xyz]--;
  tmp_n2[xyz]--; tmp_n2[xyz]--;
  tmp_n3[xyz]--;
  tmp_n4[xyz]--;

  double ret=0;
  ret=(P[xyz]-R2[xyz])*ERI_m_simple(n1,tmp_n0,n3,n4,m)
     +(W[xyz]- P[xyz])*ERI_m_simple(n1,tmp_n0,n3,n4,m+1);
  if(n1[xyz]!=0)
    ret+=(0.5/t1)*n1[xyz]*(ERI_m_simple(tmp_n1,tmp_n0,n3,n4,m)
                 -(rou/t1)*ERI_m_simple(tmp_n1,tmp_n0,n3,n4,m+1));
  if(tmp_n0[xyz]!=0)
    ret+=(0.5/t1)*tmp_n0[xyz]*(ERI_m_simple(n1,tmp_n2,n3,n4,m)
                   -(rou/t1)*ERI_m_simple(n1,tmp_n2,n3,n4,m+1));
  if(n3[xyz]!=0)
    ret+=(0.5/(t1+t2))*n3[xyz]*ERI_m_simple(n1,tmp_n0,tmp_n3,n4,m+1);
  if(n4[xyz]!=0)
    ret+=(0.5/(t1+t2))*n4[xyz]*ERI_m_simple(n1,tmp_n0,n3,tmp_n4,m+1);
  return ret;
}


template <int in_tN>
double PInt2e_base<in_tN>::ERI_m_simple_sub3(const int n1[3],const int n2[3],const int n3[3],const int n4[3],int m,int xyz){ 

  int tmp_n0[3],tmp_n1[3],tmp_n2[3],tmp_n3[3],tmp_n4[3];
    tmp_n1[0]=n1[0];
    tmp_n2[0]=n2[0];
    tmp_n3[0]=n3[0];tmp_n0[0]=n3[0];
    tmp_n4[0]=n4[0];
    tmp_n1[1]=n1[1];
    tmp_n2[1]=n2[1];
    tmp_n3[1]=n3[1];tmp_n0[1]=n3[1];
    tmp_n4[1]=n4[1];
    tmp_n1[2]=n1[2];
    tmp_n2[2]=n2[2];
    tmp_n3[2]=n3[2];tmp_n0[2]=n3[2];
    tmp_n4[2]=n4[2];

  tmp_n0[xyz]--;
  tmp_n1[xyz]--;
  tmp_n2[xyz]--;
  tmp_n3[xyz]--; tmp_n3[xyz]--;
  tmp_n4[xyz]--;

  double ret=0;
  ret=(Q[xyz]-R3[xyz])*ERI_m_simple(n1,n2,tmp_n0,n4,m)
     +(W[xyz]- Q[xyz])*ERI_m_simple(n1,n2,tmp_n0,n4,m+1);

   if(tmp_n0[xyz]!=0)
     ret+=(0.5/t2)*tmp_n0[xyz]*(ERI_m_simple(n1,n2,tmp_n3,n4,m)
                      -(rou/t2)*ERI_m_simple(n1,n2,tmp_n3,n4,m+1));
   if(n4[xyz]!=0)
     ret+=(0.5/t2)*n4[xyz]*(ERI_m_simple(n1,n2,tmp_n0,tmp_n4,m)
                  -(rou/t2)*ERI_m_simple(n1,n2,tmp_n0,tmp_n4,m+1));
   if(n1[xyz]!=0)
     ret+=(0.5/(t1+t2))*n1[xyz]*ERI_m_simple(tmp_n1,n2,tmp_n0,n4,m+1);
   if(n2[xyz]!=0)
     ret+=(0.5/(t1+t2))*n2[xyz]*ERI_m_simple(n1,tmp_n2,tmp_n0,n4,m+1);
   return ret;
}		


template <int in_tN>
double PInt2e_base<in_tN>::ERI_m_simple_sub4(const int n1[3],const int n2[3],const int n3[3],const int n4[3],int m,int xyz){ 
	
  int tmp_n0[3],tmp_n1[3],tmp_n2[3],tmp_n3[3],tmp_n4[3];
    tmp_n1[0]=n1[0];
    tmp_n2[0]=n2[0];
    tmp_n3[0]=n3[0];
    tmp_n4[0]=n4[0];tmp_n0[0]=n4[0];
    tmp_n1[1]=n1[1];
    tmp_n2[1]=n2[1];
    tmp_n3[1]=n3[1];
    tmp_n4[1]=n4[1];tmp_n0[1]=n4[1];
    tmp_n1[2]=n1[2];
    tmp_n2[2]=n2[2];
    tmp_n3[2]=n3[2];
    tmp_n4[2]=n4[2];tmp_n0[2]=n4[2];

  tmp_n0[xyz]--;
  tmp_n1[xyz]--;
  tmp_n2[xyz]--;
  tmp_n3[xyz]--;
  tmp_n4[xyz]--; tmp_n4[xyz]--;

  double ret=0;
  ret=(Q[xyz]-R4[xyz])*ERI_m_simple(n1,n2,n3,tmp_n0,m)
     +(W[xyz]- Q[xyz])*ERI_m_simple(n1,n2,n3,tmp_n0,m+1);

  if(n3[xyz]!=0)
    ret+=(0.5/t2)*n3[xyz]*(ERI_m_simple(n1,n2,tmp_n3,tmp_n0,m)
                 -(rou/t2)*ERI_m_simple(n1,n2,tmp_n3,tmp_n0,m+1));
  if(tmp_n0[xyz]!=0)
    ret+=(0.5/t2)*tmp_n0[xyz]*(ERI_m_simple(n1,n2,n3,tmp_n4,m)
                     -(rou/t2)*ERI_m_simple(n1,n2,n3,tmp_n4,m+1));
  if(n1[xyz]!=0)
    ret+=(0.5/(t1+t2))*n1[xyz]*ERI_m_simple(tmp_n1,n2,n3,tmp_n0,m+1);
  if(n2[xyz]!=0)	
    ret+=(0.5/(t1+t2))*n2[xyz]*ERI_m_simple(n1,tmp_n2,n3,tmp_n0,m+1);
  return ret;
}





//
//  three vrr
// 


template <int in_tN>
void PInt2e_base<in_tN>::set_to_sss(double in_g1,  const std::vector<double> &in_R1,
                             double in_g2,  const std::vector<double> &in_R2,
                             double in_g3,  const std::vector<double> &in_R3){
  g1=in_g1;
  g2=in_g2;
  g3=in_g3;
  t1=g1+g2;

  R1[0]=in_R1[0];  R1[1]=in_R1[1];  R1[2]=in_R1[2];
  R2[0]=in_R2[0];  R2[1]=in_R2[1];  R2[2]=in_R2[2];
  R3[0]=in_R3[0];  R3[1]=in_R3[1];  R3[2]=in_R3[2];

  P[0]=(g1*R1[0]+g2*R2[0])/(g1+g2);
  P[1]=(g1*R1[1]+g2*R2[1])/(g1+g2);
  P[2]=(g1*R1[2]+g2*R2[2])/(g1+g2);

  ss1=PInt2e_base<in_tN>::cal_ss(g1,R1,g2,R2);

  double bb1=t1*g3/(t1+g3);
  double bb2=bb1*( (P[0]-R3[0])*(P[0]-R3[0]) + (P[1]-R3[1])*(P[1]-R3[1]) 
                 + (P[2]-R3[2])*(P[2]-R3[2]) );
  to_sss=pow(t1/(t1+g3),1.5)*ss1*exp(-1.0*bb2);


  G[0]=(t1*P[0]+g3*R3[0])/(t1+g3);
  G[1]=(t1*P[1]+g3*R3[1])/(t1+g3);
  G[2]=(t1*P[2]+g3*R3[2])/(t1+g3);

}

template <int in_tN>
double PInt2e_base<in_tN>::cal_to_simple(const int n1[3],const int n2[3],const int n3[3]){
  int tn1=n1[0]+n1[1]+n1[2];
  int tn2=n2[0]+n2[1]+n2[2];
  int tn3=n3[0]+n3[1]+n3[2];
  double ret=0.0;

  if(tn1+tn2+tn3==0){
    return to_sss;
  }else if(tn1>0){
    if(n1[0]>0)      ret=cal_to_simple_sub1(n1,n2,n3,0);
    else if(n1[1]>0) ret=cal_to_simple_sub1(n1,n2,n3,1);
    else if(n1[2]>0) ret=cal_to_simple_sub1(n1,n2,n3,2);
  }else if(tn2>0){
    if(n2[0]>0)      ret=cal_to_simple_sub2(n1,n2,n3,0);
    else if(n2[1]>0) ret=cal_to_simple_sub2(n1,n2,n3,1);
    else if(n2[2]>0) ret=cal_to_simple_sub2(n1,n2,n3,2);
  }else if(tn3>0){
    if(n3[0]>0)      ret=cal_to_simple_sub3(n1,n2,n3,0);
    else if(n3[1]>0) ret=cal_to_simple_sub3(n1,n2,n3,1);
    else if(n3[2]>0) ret=cal_to_simple_sub3(n1,n2,n3,2);
  }else{
    // dummy 
    cout<<" Error in Three_Overlap_simple "<<endl;
    exit(1);
  }
  return ret;
}


template <int in_tN>
double PInt2e_base<in_tN>::cal_to_simple_sub1(const int n1[3],const int n2[3],const int n3[3],int xyz){

  int tmp_n1[3],tmp_n1_m[3],tmp_n2_m[3],tmp_n3_m[3];
  tmp_n1[0]=n1[0];
  tmp_n1[1]=n1[1];
  tmp_n1[2]=n1[2];
  tmp_n1[xyz]--;
  tmp_n1_m[0]=tmp_n1[0];
  tmp_n1_m[1]=tmp_n1[1];
  tmp_n1_m[2]=tmp_n1[2];
  tmp_n1_m[xyz]--;
  tmp_n2_m[0]=n2[0];
  tmp_n2_m[1]=n2[1];
  tmp_n2_m[2]=n2[2];
  tmp_n2_m[xyz]--;
  tmp_n3_m[0]=n3[0];
  tmp_n3_m[1]=n3[1];
  tmp_n3_m[2]=n3[2];
  tmp_n3_m[xyz]--;

  double ret=0.0;

  ret+=(G[xyz]-R1[xyz])*cal_to_simple(tmp_n1,n2,n3);

  if(tmp_n1[xyz]>0){
    ret+=(0.5*tmp_n1[xyz]/(g1+g2+g3))*cal_to_simple(tmp_n1_m,n2,n3);
  } 
  if(n2[xyz]>0){
    ret+=(0.5*n2[xyz]/(g1+g2+g3))*cal_to_simple(tmp_n1,tmp_n2_m,n3);
  }
  if(n3[xyz]>0){
    ret+=(0.5*n3[xyz]/(g1+g2+g3))*cal_to_simple(tmp_n1,n2,tmp_n3_m);
  }

  return ret;
}


template <int in_tN>
double PInt2e_base<in_tN>::cal_to_simple_sub2(const int n1[3],const int n2[3],const int n3[3],int xyz){
  int tn1=n1[0]+n1[1]+n1[2];

  int tmp_n2[3],tmp_n2_m[3],tmp_n3_m[3];
  tmp_n2[0]=n2[0]; 
  tmp_n2[1]=n2[1]; 
  tmp_n2[2]=n2[2]; 
  tmp_n2[xyz]--;
  tmp_n2_m[0]=tmp_n2[0];
  tmp_n2_m[1]=tmp_n2[1];
  tmp_n2_m[2]=tmp_n2[2];
  tmp_n2_m[xyz]--;
  tmp_n3_m[0]=n3[0];
  tmp_n3_m[1]=n3[1];
  tmp_n3_m[2]=n3[2];
  tmp_n3_m[xyz]--;

  double ret=0.0;

  if(tn1!=0){
    cout<<" Error in Three_Overlap_simple_sub2 tn1 : "<<tn1<<endl;
    exit(1);
  }else{
    ret+=(G[xyz]-R2[xyz])*cal_to_simple(n1,tmp_n2,n3);
    if(tmp_n2[xyz]>0){
      ret+=(0.5*tmp_n2[xyz]/(g1+g2+g3))*cal_to_simple(n1,tmp_n2_m,n3);
    }
    if(n3[xyz]>0){
      ret+=(0.5*n3[xyz]/(g1+g2+g3))*cal_to_simple(n1,tmp_n2,tmp_n3_m);
    }
  }
 
  return ret;

}


template <int in_tN>
double PInt2e_base<in_tN>::cal_to_simple_sub3(const int n1[3],const int n2[3],const int n3[3],int xyz){
  int tn1=n1[0]+n1[1]+n1[2];
  int tn2=n2[0]+n2[1]+n2[2];

  int tmp_n3[3],tmp_n3_m[3];
  tmp_n3[0]=n3[0];
  tmp_n3[1]=n3[1];
  tmp_n3[2]=n3[2];
  tmp_n3[xyz]--;
  tmp_n3_m[0]=tmp_n3[0];
  tmp_n3_m[1]=tmp_n3[1];
  tmp_n3_m[2]=tmp_n3[2];
  tmp_n3_m[xyz]--;

  double ret=0.0;
  if(tn1!=0 || tn2!=0){
    cout<<" Error in Three_Overlap_simple_sub3 tn1,tn2 : "<<tn1<<"  "<<tn2<<endl;
    exit(1);
  }else{
    ret+=(G[xyz]-R3[xyz])*cal_to_simple(n1,n2,tmp_n3);
    if(tmp_n3[xyz]>0){
      ret+=(0.5*tmp_n3[xyz]/(g1+g2+g3))*cal_to_simple(n1,n2,tmp_n3_m);
    }
  }
  return ret;
}


//
//


template <int in_tN>
int PInt2e_base<in_tN>::debug_driver_os_recursion(int max_ijkl){


  std::cout<<" ========== debug_driver_os_recusrion of PInt2e_base ========== "<<std::endl;

  std::vector<double> Ri(3),Rj(3),Rk(3),Rl(3);
  Ri[0]=0.3;      Ri[1]=0.4;      Ri[2]=0.1;
  Rj[0]=-0.1;     Rj[1]=0.2;      Rj[2]=-0.3;
  Rk[0]=0.5;      Rk[1]=-0.4;     Rk[2]=0.2;
  Rl[0]=0.3;      Rl[1]=-0.2;     Rl[2]=-0.6;

  double gi=0.7;
  double gj=0.6;
  double gk=0.8;
  double gl=0.2;

  PInt2e_base<0> pint2e;

  pint2e.set_gR_12(gi,Ri,gj,Rj);
  pint2e.set_gR_34(gk,Rk,gl,Rl);

//  cout<<" ----- pint2e ----- "<<endl;
//  pint2e.show_state();

  int     mode_erfc=0;
  double  omega_erfc=0.7;
  std::vector<double> dI_A(100),dI_B(100),dI_C(100),dI_D(100);
  std::vector<double> debug_eri(20000);

  for(int i=0;i<=max_ijkl;i++){
    for(int j=0;j<=max_ijkl;j++){
      for(int k=0;k<=max_ijkl;k++){
        for(int l=0;l<=max_ijkl;l++){
          //int t_ni=0,t_nj=0,t_nk=0,t_nl=0;
          std::vector<int> ni,nj,nk,nl;
          int num_ia=pint2e.get_num(i);
          int num_ib=pint2e.get_num(j);
          int num_ic=pint2e.get_num(k);
          int num_id=pint2e.get_num(l);
          // dI_A
          for(int ia=0;ia<num_ia;ia++){
            ni=pint2e.get_no_to_n(i,ia);
            dI_A[ia]=PInt2e_base<0>::cal_I(gi,ni);
          }
          // dI_B
          for(int ib=0;ib<num_ib;ib++){
            nj=pint2e.get_no_to_n(j,ib);
            dI_B[ib]=PInt2e_base<0>::cal_I(gj,nj);
          }
          // dI_C
          for(int ic=0;ic<num_ic;ic++){
            nk=pint2e.get_no_to_n(k,ic);
            dI_C[ic]=PInt2e_base<0>::cal_I(gk,nk);
          }
          // dI_D
          for(int id=0;id<num_id;id++){
            nl=pint2e.get_no_to_n(l,id);
            dI_D[id]=PInt2e_base<0>::cal_I(gl,nl);
          }
  
          int tn=i+j+k+l;

          pint2e.set_eri_ssss(tn,mode_erfc,omega_erfc);

//        cout<<"======>  loop_i,j,k,l  "<<loop_a[i]<<" "<<loop_a[j]<<" "<<loop_a[k]<<" "<<loop_a[l]<<" sel "<<sel<<endl;
//        cout<<" i,j,k,l  "<<i<<" "<<j<<" "<<k<<" "<<l<<" num "<<num_ia<<" "<<num_ib<<" "<<num_ic<<" "<<num_id<<endl;
 
          pint2e.ERI_recursion(debug_eri,i,j,k,l,dI_A,dI_B,dI_C,dI_D);


          int cc=0;
          for(int ia=0;ia<num_ia;ia++){
            for(int ib=0;ib<num_ib;ib++){
              for(int ic=0;ic<num_ic;ic++){
                for(int id=0;id<num_id;id++){
                  std::vector<int> ni,nj,nk,nl;
                  ni=pint2e.get_no_to_n(i,ia);
                  nj=pint2e.get_no_to_n(j,ib);
                  nk=pint2e.get_no_to_n(k,ic);
                  nl=pint2e.get_no_to_n(l,id);
                  double comp_eri = pint2e.ERI_simple(ni,nj,nk,nl)
                                   *pint2e.cal_I(gi,ni)*pint2e.cal_I(gj,nj)
                                   *pint2e.cal_I(gk,nk)*pint2e.cal_I(gl,nl);

 
                  if(fabs(debug_eri[cc]-comp_eri)>1.0e-10){
                    cout<<" ****** ERROR  cc="<<cc<<" "<<endl;
                    cout<<"   ia="<<ia<<" ni "<<ni[0]<<" "<<ni[1]<<" "<<ni[2]<<endl;
                    cout<<"   ib="<<ib<<" nj "<<nj[0]<<" "<<nj[1]<<" "<<nj[2]<<endl;
                    cout<<"   ic="<<ic<<" nk "<<nk[0]<<" "<<nk[1]<<" "<<nk[2]<<endl;
                    cout<<"   id="<<id<<" nl "<<nl[0]<<" "<<nl[1]<<" "<<nl[2]<<endl;
                    cout<<"   debug_eri   "<<debug_eri[cc]<<endl;
                    cout<<"   comp_eri    "<<comp_eri<<endl;
                    return 1;
                  }
                  cc++;
                }
              }
            }
          }
 
                                       
        }
      }
    }
  }

  std::cout<<" ok "<<std::endl;
  return 0;

}

}  // end of namespace "PInt"


#endif // end of include-guard
