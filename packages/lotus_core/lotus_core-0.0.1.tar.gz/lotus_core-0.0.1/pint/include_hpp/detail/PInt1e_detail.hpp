
#ifndef PINT1E_DETAIL_HPP
#define PINT1E_DETAIL_HPP


#define _USE_MATH_DEFINES
#include <math.h>
#include <stdlib.h>

#include <iostream>

#include "Table_Fm_T.hpp"

namespace PInt {

using namespace std;

template <int in_tN>
void PInt1e_base<in_tN>::show_state(){
  cout<<"  g1,g2  "<<g1<<" "<<g2<<endl;
  cout<<"  R1  "<<R1[0]<<"  "<<R1[1]<<"  "<<R1[2]<<endl;
  cout<<"  R2  "<<R2[0]<<"  "<<R2[1]<<"  "<<R2[2]<<endl;
  cout<<"  Rc  "<<Rc[0]<<"  "<<Rc[1]<<"  "<<Rc[2]<<endl;
  cout<<"   P  "<< P[0]<<"  "<< P[1]<<"  "<< P[2]<<endl;
  cout<<" overlap_ss "<<overlap_ss<<endl;
  cout<<" nai_ss "<<nai_ss[0]<<" "<<nai_ss[1]<<" "<<nai_ss[2]<<endl;
}


template <int in_tN>
double PInt1e_base<in_tN>::cal_I(double in_g,const std::vector<int> &in_n){
  // nnn = n!!
  int nnn[12];
  nnn[0] =1;  nnn[1] =1;  nnn[2] =1;  nnn[3] =2;  nnn[4] =3; nnn[5] =8;
  nnn[6] =15; nnn[7] =48; nnn[8] =105;nnn[9] =384;nnn[10] =945;
  return pow((2*in_g/M_PI),3.0/4.0)*pow(4*in_g,(in_n[0]+in_n[1]+in_n[2])/2.0)/
             sqrt(nnn[2*in_n[0]]*nnn[2*in_n[1]]*nnn[2*in_n[2]]);
}


template <int in_tN>
std::vector<double> PInt1e_base<in_tN>::cal_dI(int in_st,double in_g,double in_d){
  std::vector<double> ret_dI;
  int num=get_num(in_st);
  for(int i=0;i<num;i++){
    std::vector<int> tmp_n = get_no_to_n(in_st,i);
    ret_dI.push_back(in_d*cal_I(in_g,tmp_n));
  }
  return ret_dI;
}

template <int in_tN>
void PInt1e_base<in_tN>::set_gR_12(double in_g1,const std::vector<double> &in_R1,double in_g2,const std::vector<double> &in_R2){
  // for overlap
  g1=in_g1; g2=in_g2;
  R1[0]=in_R1[0]; R1[1]=in_R1[1]; R1[2]=in_R1[2];
  R2[0]=in_R2[0]; R2[1]=in_R2[1]; R2[2]=in_R2[2];
  P[0]=(g1*R1[0]+g2*R2[0])/(g1+g2);
  P[1]=(g1*R1[1]+g2*R2[1])/(g1+g2);
  P[2]=(g1*R1[2]+g2*R2[2])/(g1+g2);

  double alpha=g1+g2;
  double beta=g1*g2/(g1+g2);
  overlap_ss = pow(M_PI/alpha,1.5)*
    exp(-beta*((R1[0]-R2[0])*(R1[0]-R2[0])+(R1[1]-R2[1])*(R1[1]-R2[1])+(R1[2]-R2[2])*(R1[2]-R2[2])));
}


template <int in_tN>
void PInt1e_base<in_tN>::set_gR_12_nuc(double in_g1,const std::vector<double> &in_R1,double in_g2,const std::vector<double> &in_R2,
                           int max_m,const std::vector<double> &in_Rc,MODE mode_erfc,double omega){
  // for nai
  g1=in_g1; g2=in_g2;
  R1[0]=in_R1[0]; R1[1]=in_R1[1]; R1[2]=in_R1[2];
  R2[0]=in_R2[0]; R2[1]=in_R2[1]; R2[2]=in_R2[2];
  Rc[0]=in_Rc[0]; Rc[1]=in_Rc[1]; Rc[2]=in_Rc[2];

  double alpha=g1+g2;
  double beta=g1*g2/(g1+g2);
  P[0]=(g1*R1[0]+g2*R2[0])/(g1+g2);
  P[1]=(g1*R1[1]+g2*R2[1])/(g1+g2);
  P[2]=(g1*R1[2]+g2*R2[2])/(g1+g2);
  overlap_ss = pow(M_PI/alpha,1.5)*
    exp(-beta*((R1[0]-R2[0])*(R1[0]-R2[0])+(R1[1]-R2[1])*(R1[1]-R2[1])+(R1[2]-R2[2])*(R1[2]-R2[2])));

  double U,v_omega;
  if(mode_erfc==Normal){
    U=alpha*((P[0]-Rc[0])*(P[0]-Rc[0])+(P[1]-Rc[1])*(P[1]-Rc[1])+(P[2]-Rc[2])*(P[2]-Rc[2]));
    for(int m=0;m<=max_m;m++)
      nai_ss[m]=2.0*sqrt(alpha/M_PI)*overlap_ss*cal_Fm_T<double>(m,U);
  }else if(mode_erfc==Erfc){ // short range
    U=alpha*((P[0]-Rc[0])*(P[0]-Rc[0])+(P[1]-Rc[1])*(P[1]-Rc[1])+(P[2]-Rc[2])*(P[2]-Rc[2]));
    for(int m=0;m<=max_m;m++)
      nai_ss[m]=2.0*sqrt(alpha/M_PI)*overlap_ss*cal_Fm_T<double>(m,U);
    v_omega=alpha*omega*omega/(alpha+omega*omega);
    U=v_omega*((P[0]-Rc[0])*(P[0]-Rc[0])+(P[1]-Rc[1])*(P[1]-Rc[1])+(P[2]-Rc[2])*(P[2]-Rc[2]));
    for(int m=0;m<=max_m;m++)
      nai_ss[m]-=2.0*sqrt(1.0/M_PI)*overlap_ss*pow(v_omega,m+0.5)*pow(1.0/alpha,m)*cal_Fm_T<double>(m,U);
  }else if(mode_erfc==Erf){ // long range
    v_omega=alpha*omega*omega/(alpha+omega*omega);
    U=v_omega*((P[0]-Rc[0])*(P[0]-Rc[0])+(P[1]-Rc[1])*(P[1]-Rc[1])+(P[2]-Rc[2])*(P[2]-Rc[2]));
    for(int m=0;m<=max_m;m++)
      nai_ss[m]=2.0*sqrt(1.0/M_PI)*overlap_ss*pow(v_omega,m+0.5)*pow(1.0/alpha,m)*cal_Fm_T<double>(m,U);
  }

}


template <int in_tN>
double PInt1e_base<in_tN>::kinetic_simple(const std::vector<int> &n1,const std::vector<int> &n2){
  double ret_kei,kei_x,kei_y,kei_z;
  double value_00;
  double value_02x,value_0m2x;
  double value_02y,value_0m2y;
  double value_02z,value_0m2z;
  std::vector<int> nx_2plus(3),nx_2minus(3);
  nx_2plus[0]=nx_2minus[0]=n2[0]; nx_2plus[1]=nx_2minus[1]=n2[1]; nx_2plus[2]=nx_2minus[2]=n2[2];
  nx_2plus[0]+=2; nx_2minus[0]-=2;
  std::vector<int> ny_2plus(3),ny_2minus(3);
  ny_2plus[0]=ny_2minus[0]=n2[0]; ny_2plus[1]=ny_2minus[1]=n2[1]; ny_2plus[2]=ny_2minus[2]=n2[2];
  ny_2plus[1]+=2; ny_2minus[1]-=2;
  std::vector<int> nz_2plus(3),nz_2minus(3);
  nz_2plus[0]=nz_2minus[0]=n2[0]; nz_2plus[1]=nz_2minus[1]=n2[1]; nz_2plus[2]=nz_2minus[2]=n2[2];
  nz_2plus[2]+=2; nz_2minus[2]-=2;
  value_00   = overlap_simple(n1,n2);
  value_02x  = overlap_simple(n1,nx_2plus);
  value_02y  = overlap_simple(n1,ny_2plus);
  value_02z  = overlap_simple(n1,nz_2plus);
  if(nx_2minus[0]>=0) value_0m2x = overlap_simple(n1,nx_2minus);
  else                value_0m2x = 0.0;
  if(ny_2minus[1]>=0) value_0m2y = overlap_simple(n1,ny_2minus);
  else                value_0m2y = 0.0;
  if(nz_2minus[2]>=0) value_0m2z = overlap_simple(n1,nz_2minus);
  else                value_0m2z = 0.0;

  kei_x=g2*(2*n2[0]+1)*value_00 - 2*g2*g2*value_02x - 0.5*n2[0]*(n2[0]-1)*value_0m2x;
  kei_y=g2*(2*n2[1]+1)*value_00 - 2*g2*g2*value_02y - 0.5*n2[1]*(n2[1]-1)*value_0m2y;
  kei_z=g2*(2*n2[2]+1)*value_00 - 2*g2*g2*value_02z - 0.5*n2[2]*(n2[2]-1)*value_0m2z;
  ret_kei=(kei_x+kei_y+kei_z);
  return ret_kei;
}



template <int in_tN>
void PInt1e_base<in_tN>::kinetic(std::vector<double> &ret_kei,int tn1,int tn2){
  
  int num1=get_num(tn1);
  int num2=get_num(tn2);
  ret_kei.reserve(num1*num2);
  ret_kei.clear();
  int num2_p2=get_num(tn2+2);
  int max_num=num1;
  if(num2_p2>max_num) max_num=num2_p2;
  std::vector<double> dI_one(max_num);
  for(int i=0;i<max_num;i++)    dI_one[i]=1.0;
  std::vector<double> s_00,s_02,s_02m;
 
  overlap(s_00,tn1,tn2,dI_one,dI_one);
  overlap(s_02,tn1,tn2+2,dI_one,dI_one);

  int num2_m2=-1000;
  if(tn2>=2){
    num2_m2=get_num(tn2-2);
    overlap(s_02m,tn1,tn2-2,dI_one,dI_one);
  }

  for(int i1=0;i1<num1;i1++){
    for(int i2=0;i2<num2;i2++){
      std::vector<int> n2_px(3),n2_py(3),n2_pz(3),n2_mx(3),n2_my(3),n2_mz(3);
      std::vector<int> n2=get_no_to_n(tn2,i2);
      n2_px[0]=n2[0];  n2_px[1]=n2[1];  n2_px[2]=n2[2];
      n2_py[0]=n2[0];  n2_py[1]=n2[1];  n2_py[2]=n2[2];
      n2_pz[0]=n2[0];  n2_pz[1]=n2[1];  n2_pz[2]=n2[2];
      n2_px[0]+=2;
      n2_py[1]+=2;
      n2_pz[2]+=2;
      int i2_px=basis_index::n_to_no[n2_px[0]][n2_px[1]][n2_px[2]];
      int i2_py=basis_index::n_to_no[n2_py[0]][n2_py[1]][n2_py[2]];
      int i2_pz=basis_index::n_to_no[n2_pz[0]][n2_pz[1]][n2_pz[2]];
      double kei_x=g2*(2*n2[0]+1)*s_00[i1*num2+i2] - 2*g2*g2*s_02[i1*num2_p2+i2_px];
      double kei_y=g2*(2*n2[1]+1)*s_00[i1*num2+i2] - 2*g2*g2*s_02[i1*num2_p2+i2_py];
      double kei_z=g2*(2*n2[2]+1)*s_00[i1*num2+i2] - 2*g2*g2*s_02[i1*num2_p2+i2_pz];
      n2_mx[0]=n2[0];  n2_mx[1]=n2[1];  n2_mx[2]=n2[2];
      n2_my[0]=n2[0];  n2_my[1]=n2[1];  n2_my[2]=n2[2];
      n2_mz[0]=n2[0];  n2_mz[1]=n2[1];  n2_mz[2]=n2[2];
      n2_mx[0]-=2;
      n2_my[1]-=2;
      n2_mz[2]-=2;
      if(n2_mx[0]>=0){
        int i2_mx=basis_index::n_to_no[n2_mx[0]][n2_mx[1]][n2_mx[2]];
        kei_x -= 0.5*n2[0]*(n2[0]-1)*s_02m[i1*num2_m2+i2_mx];
      }
      if(n2_my[1]>=0){
        int i2_my=basis_index::n_to_no[n2_my[0]][n2_my[1]][n2_my[2]];
        kei_y -= 0.5*n2[1]*(n2[1]-1)*s_02m[i1*num2_m2+i2_my];
      }
      if(n2_mz[2]>=0){
        int i2_mz=basis_index::n_to_no[n2_mz[0]][n2_mz[1]][n2_mz[2]];
        kei_z -= 0.5*n2[2]*(n2[2]-1)*s_02m[i1*num2_m2+i2_mz];
      }
      ret_kei.push_back((kei_x+kei_y+kei_z));
    }
  }

}

 
template <int in_tN>
void PInt1e_base<in_tN>::mult_dI_c(std::vector<double> &ret_v,int tn1,int tn2,int tc,
                       const std::vector<double> &dI_a,const std::vector<double> &dI_b){
  int num1=get_num(tn1);
  int num2=get_num(tn2);
  int Nc=1;
  if(tc==1) Nc=3;
  if(tc==2) Nc=6;
  if(tc>2){ std::cout<<" ERROR in mult_dI_c of PInt1e_base<double> class tc="<<tc<<std::endl; }
  
  //int N12=num1*num2;
  for(int i1=0;i1<num1;i1++){
    for(int i2=0;i2<num2;i2++){
      for(int c=0;c<Nc;c++){
        int ind=i1*num2+i2;
        ret_v[ind*Nc+c]*=dI_a[i1]*dI_b[i2];
      }
    }
  }
}


template <int in_tN>
void PInt1e_base<in_tN>::overlap_dp(double *ret_ss,int tn1,int tn2){
  int num1=get_num(tn1);
  int num2=get_num(tn2);
  int N12=num1*num2;


  for(int i1=0;i1<=tn1;i1++){
    for(int i2=0;i2<=tn2;i2++){
      double *tmp_ss = new double [N12];
      overlap_dp_sub(tmp_ss,i1,i2);
      ptr_overlap_dp[i1][i2]=tmp_ss;
    }
  }
 
  for(int i1=0;i1<num1;i1++){
    for(int i2=0;i2<num2;i2++){
      int ind=i1*num2+i2;
      ret_ss[ind]=ptr_overlap_dp[tn1][tn2][ind];
    }
  }

  for(int i1=0;i1<=tn1;i1++){
    for(int i2=0;i2<=tn2;i2++){
      delete [] ptr_overlap_dp[i1][i2];
    }
  }

}


template <int in_tN>
void PInt1e_base<in_tN>::overlap_dp_sub(double *ret_ss,int tn1,int tn2){
  if(tn1+tn2==0){
    ret_ss[0]=overlap_ss;
    return;
  } 
  int n1[3],n2[3],n1_m[3],n2_m[3];
  int num1=get_num(tn1);
  int num2=get_num(tn2);
  double *t_ss_1,*t_ss_2,*t_ss_3;
  
  if(tn1>=1){
    t_ss_1=ptr_overlap_dp[tn1-1][tn2];
    if(tn1>=2) t_ss_2=ptr_overlap_dp[tn1-2][tn2];
    if(tn2>=1) t_ss_3=ptr_overlap_dp[tn1-1][tn2-1];
    for(int i1=0;i1<num1;i1++){
      for(int i2=0;i2<num2;i2++){
        set_n12(n1,n2,i1,i2,tn1,tn2);
        int xyz=get_xyz(n1);
        set_n12_m(n1_m,n2_m,n1,n2,xyz);
        
        int i1_m=basis_index::n_to_no[n1_m[0]][n1_m[1]][n1_m[2]];
        int ind_a=i1_m*num2+i2;
        double tmp_v=(P[xyz]-R1[xyz])*t_ss_1[ind_a];
    
        if(n1_m[xyz]>0){
          int n1_m2[3]={n1[0],n1[1],n1[2]};
          n1_m2[xyz]-=2;
          int i1_m2=basis_index::n_to_no[n1_m2[0]][n1_m2[1]][n1_m2[2]];
          int ind_b=i1_m2*num2+i2;
          tmp_v+=(0.5/(g1+g2))*((double)n1_m[xyz])*t_ss_2[ind_b];
        }

        if(n2_m[xyz]>=0){
          int num2_m=get_num(tn2-1);
          int i2_m=basis_index::n_to_no[n2_m[0]][n2_m[1]][n2_m[2]];
          int ind_c=i1_m*num2_m+i2_m;
          tmp_v+=(0.5/(g1+g2))*((double)n2[xyz])*t_ss_3[ind_c];
        }
        int ind=i1*num2+i2;
        ret_ss[ind]=tmp_v;
      }
    }

  }else if(tn2>=1){
    t_ss_1=ptr_overlap_dp[tn1][tn2-1];
    if(tn2>=2) t_ss_2=ptr_overlap_dp[tn1][tn2-2];
    int i1=0;
    for(int i2=0;i2<num2;i2++){
      set_n12(n1,n2,i1,i2,tn1,tn2);
      int xyz=get_xyz(n2);
      set_n12_m(n1_m,n2_m,n1,n2,xyz);

      int num2_m=get_num(tn2-1);
      int i2_m=basis_index::n_to_no[n2_m[0]][n2_m[1]][n2_m[2]];
      int ind_a=i1*num2_m+i2_m;
      double tmp_v=(P[xyz]-R2[xyz])*t_ss_1[ind_a];

      if(n2_m[xyz]>0){
        int n2_m2[3]={n2[0],n2[1],n2[2]};
        n2_m2[xyz]-=2;
        int num2_m2=get_num(tn2-2);
        int i2_m2=basis_index::n_to_no[n2_m2[0]][n2_m2[1]][n2_m2[2]];
        int ind_b=i1*num2_m2+i2_m2;
        tmp_v+=(0.5/(g1+g2))*((double)n2_m[xyz])*t_ss_2[ind_b];
      }

      int ind=i1*num2+i2;
      ret_ss[ind]=tmp_v;
    }

  }

}


template <int in_tN>
double PInt1e_base<in_tN>::overlap_simple(const std::vector<int> &n1,const std::vector<int> &n2){
  int tn1=n1[0]+n1[1]+n1[2];
  int tn2=n2[0]+n2[1]+n2[2];
  if(tn1<0 || tn2<0){
    cout<<" Error in overlap_naibu of overlap_simple of PInt1e_base<double> class "<<endl;
    exit(1);
  }else if(tn1==0 && tn2==0){
    return overlap_ss;
  }else{
    if(tn1>=1){
      if(n1[0]>0)      return overlap_simple_sub1(n1,n2,0);
      else if(n1[1]>0) return overlap_simple_sub1(n1,n2,1);
      else             return overlap_simple_sub1(n1,n2,2);
    }else{
      if(n2[0]>0)      return overlap_simple_sub2(n1,n2,0);
      else if(n2[1]>0) return overlap_simple_sub2(n1,n2,1);
      else             return overlap_simple_sub2(n1,n2,2);
    }
  }
  return 0.0; // dummy 
}

template <int in_tN>
double PInt1e_base<in_tN>::overlap_simple_sub1(const std::vector<int> &n1,const std::vector<int> &n2,int xyz){
  std::vector<int> na(3);
  na[0]=n1[0]; na[1]=n1[1]; na[2]=n1[2];
  na[xyz]--;
  std::vector<int> na_minus(3);
  na_minus[0]=na[0]; na_minus[1]=na[1]; na_minus[2]=na[2];
  na_minus[xyz]--;
  std::vector<int> nb_minus(3);
  nb_minus[0]=n2[0]; nb_minus[1]=n2[1]; nb_minus[2]=n2[2];
  nb_minus[xyz]--;
  double ret=(P[xyz]-R1[xyz])*overlap_simple(na,n2);
  if(na[xyz]!=0) ret+=(0.5/(g1+g2))*((double)na[xyz])*overlap_simple(na_minus,n2);
  if(n2[xyz]!=0) ret+=(0.5/(g1+g2))*((double)n2[xyz])*overlap_simple(na,nb_minus);
  return ret;
}

template <int in_tN>
double PInt1e_base<in_tN>::overlap_simple_sub2(const std::vector<int> &n1,const std::vector<int> &n2,int xyz){
  std::vector<int> nb(3);
  nb[0]=n2[0]; nb[1]=n2[1]; nb[2]=n2[2];
  nb[xyz]--;
  std::vector<int> na_minus(3);
  na_minus[0]=n1[0]; na_minus[1]=n1[1]; na_minus[2]=n1[2];
  na_minus[xyz]--;
  std::vector<int> nb_minus(3);
  nb_minus[0]=nb[0]; nb_minus[1]=nb[1]; nb_minus[2]=nb[2];
  nb_minus[xyz]--;
  double ret=(P[xyz]-R2[xyz])*overlap_simple(n1,nb);
  if(n1[xyz]!=0) ret+=(0.5/(g1+g2))*((double)n1[xyz])*overlap_simple(na_minus,nb);
  if(nb[xyz]!=0) ret+=(0.5/(g1+g2))*((double)nb[xyz])*overlap_simple(n1,nb_minus);			
  return ret;
}

//
//

//
//
//
template <int in_tN>
double PInt1e_base<in_tN>::mi_simple(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<double> &C,const std::vector<int> &klm){
  int tn1=n1[0]+n1[1]+n1[2];
  int tn2=n2[0]+n2[1]+n2[2];
  int tn3=klm[0]+klm[1]+klm[2];
  if(tn1<0 || tn2<0 || tn3<0){
    return 0;
  }else if(tn1==0 && tn2==0 && tn3==0){
    return overlap_ss;
  }else{
    double ret=0.0;
    if(tn1>0){
      if(n1[0]>0)       ret=mi_simple_sub1(n1,n2,C,klm,0);
      else if(n1[1]>0)  ret=mi_simple_sub1(n1,n2,C,klm,1);
      else if(n1[2]>0)  ret=mi_simple_sub1(n1,n2,C,klm,2);
      return ret;
    }else if(tn2>0){
      if(n2[0]>0)       ret=mi_simple_sub2(n1,n2,C,klm,0);
      else if(n2[1]>0)  ret=mi_simple_sub2(n1,n2,C,klm,1);
      else if(n2[2]>0)  ret=mi_simple_sub2(n1,n2,C,klm,2);
      return ret;
    }else{
      if(klm[0]>0)      ret=mi_simple_sub3(n1,n2,C,klm,0);
      else if(klm[1]>0) ret=mi_simple_sub3(n1,n2,C,klm,1);
      else if(klm[2]>0) ret=mi_simple_sub3(n1,n2,C,klm,2);
      return ret;
    } 
  }
}

template <int in_tN>
double PInt1e_base<in_tN>::mi_simple_sub1(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<double> &C,const std::vector<int> &klm,int xyz){
  std::vector<int> na(3),na_minus(3),nb_minus(3),klm_minus(3);
  na[0]=n1[0]; na[1]=n1[1]; na[2]=n1[2];
  na[xyz]--;
  na_minus[0]=na[0]; na_minus[1]=na[1]; na_minus[2]=na[2];
  na_minus[xyz]--;
  nb_minus[0]=n2[0]; nb_minus[1]=n2[1]; nb_minus[2]=n2[2];
  nb_minus[xyz]--;
  klm_minus[0]=klm[0]; klm_minus[1]=klm[1]; klm_minus[2]=klm[2];
  klm_minus[xyz]--;

  double ret=0;
  ret=(P[xyz]-R1[xyz])*mi_simple(na,n2,C,klm);
  if(na[xyz]!=0)  ret+=(0.5/(g1+g2))*((double)na[xyz])* (mi_simple(na_minus,n2,C,klm));
  if(n2[xyz]!=0)  ret+=(0.5/(g1+g2))*((double)n2[xyz])* (mi_simple(na,nb_minus,C,klm));
  if(klm[xyz]!=0) ret+=(0.5/(g1+g2))*((double)klm[xyz])*(mi_simple(na,n2,C,klm_minus));
  return ret;
}

template <int in_tN>
double PInt1e_base<in_tN>::mi_simple_sub2(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<double> &C,const std::vector<int> &klm,int xyz){
  std::vector<int> nb(3),na_minus(3),nb_minus(3),klm_minus(3);
  nb[0]=n2[0]; nb[1]=n2[1]; nb[2]=n2[2];
  nb[xyz]--;
  na_minus[0]=n1[0]; na_minus[1]=n1[1]; na_minus[2]=n1[2];
  na_minus[xyz]--;
  nb_minus[0]=nb[0]; nb_minus[1]=nb[1]; nb_minus[2]=nb[2];
  nb_minus[xyz]--;
  klm_minus[0]=klm[0]; klm_minus[1]=klm[1]; klm_minus[2]=klm[2];
  klm_minus[xyz]--;

  double ret=0;
  ret=(P[xyz]-R2[xyz])*mi_simple(n1,nb,C,klm);
  if(n1[xyz]!=0)  ret+=(0.5/(g1+g2))*((double)n1[xyz])* (mi_simple(na_minus,nb,C,klm));
  if(nb[xyz]!=0)  ret+=(0.5/(g1+g2))*((double)nb[xyz])* (mi_simple(n1,nb_minus,C,klm));
  if(klm[xyz]!=0) ret+=(0.5/(g1+g2))*((double)klm[xyz])*(mi_simple(n1,nb,C,klm_minus));
  return ret;
}

template <int in_tN>
double PInt1e_base<in_tN>::mi_simple_sub3(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<double> &C,const std::vector<int> &klm,int xyz){
  std::vector<int> nm(3),nm_minus(3);
  nm[0]=klm[0]; nm[1]=klm[1]; nm[2]=klm[2];
  nm[xyz]--;
  nm_minus[0]=nm[0]; nm_minus[1]=nm[1]; nm_minus[2]=nm[2];
  nm_minus[xyz]--;

  double ret=0;
  ret=(P[xyz]-C[xyz])*(mi_simple(n1,n2,C,nm));
  if(nm[xyz]!=0) ret+=(0.5/(g1+g2))*((double)nm[xyz])*(mi_simple(n1,n2,C,nm_minus));
  return ret;
}




//
//  nuclear-grad 
//


template <int in_tN>
void PInt1e_base<in_tN>::nuclear_c_dp(double *ret_nai,int tn1,int tn2,int tc){
  int num1=get_num(tn1);
  int num2=get_num(tn2);
  int N12=num1*num2;

  int N_c=1;
  if(tc==1) N_c=3;
  if(tc==2) N_c=6;
  if(tc>2){
    cout<<" Error in nuclear_c_dp of PInt1e_base<double> tc="<<tc<<endl;
    exit(1);
  }

  for(int i1=0;i1<=tn1;i1++){
    for(int i2=0;i2<=tn2;i2++){
      for(int ic=0;ic<=tc;ic++){
        for(int m=(tn1+tn2+tc-i1-i2-ic);m>=0;m--){
          double *tmp_nai = new double [N12*N_c];
          nuclear_c_dp_sub(tmp_nai,i1,i2,ic,m);
          ptr_nai_c_dp[i1][i2][ic][m]=tmp_nai;
        }
      }
    }
  }
 
  for(int i1=0;i1<num1;i1++){
    for(int i2=0;i2<num2;i2++){
      for(int c=0;c<N_c;c++){
        int ind=i1*num2+i2;
        ret_nai[ind*N_c+c]=ptr_nai_c_dp[tn1][tn2][tc][0][ind*N_c+c];
      }
    }
  }

  for(int i1=0;i1<=tn1;i1++){
    for(int i2=0;i2<=tn2;i2++){
      for(int ic=0;ic<=tc;ic++){
        for(int m=(tn1+tn2-i1-i2);m>=0;m--){
          delete [] ptr_nai_c_dp[i1][i2][ic][m];
        }
      }
    }
  }

}


template <int in_tN>
void PInt1e_base<in_tN>::nuclear_c_dp_sub(double *ret_nai,int tn1,int tn2,int tc,int m){


  if(tn1+tn2==0){
    if(tc==0){
      ret_nai[0]=nai_ss[m];
      return;
    }else if(tc==1){
      for(int xyz=0;xyz<3;xyz++) ret_nai[0*3+xyz]=2.0*(g1+g2)*(P[xyz]-Rc[xyz])*nai_ss[m+1];
    }else if(tc==2){
      for(int c=0;c<6;c++){
        int xyz1=c_to_xyz1[2][c];
        int xyz2=c_to_xyz2[2][c];
        double tmp_v1=-2.0*(g1+g2)*nai_ss[m+1];
        double tmp_v2=4.0*(g1+g2)*(g1+g2)*(P[xyz1]-Rc[xyz1])*(P[xyz2]-Rc[xyz2])*nai_ss[m+2];
        ret_nai[0*6+c]=tmp_v2;
        if(xyz1==xyz2)  ret_nai[0*6+c]+=tmp_v1;
      }
    }else if(tc>2){
      cout<<" ERROR nuclear_nc_recursion_sub: tc="<<tc<<endl;
      exit(1);
    }
  } 
  int n1[3],n2[3],n1_m[3],n2_m[3];
  int num1=get_num(tn1);
  int num2=get_num(tn2);
  int loop_c  =1;
  if(tc==1) loop_c=3; 
  if(tc==2) loop_c=6; 
  double *t_nai_1,*t_nai_2,*t_nai_3,*t_nai_4,*t_nai_5,*t_nai_6,*t_nai_7;
  
  if(tn1>=1){
    t_nai_1=ptr_nai_c_dp[tn1-1][tn2][tc][m  ];
    t_nai_2=ptr_nai_c_dp[tn1-1][tn2][tc][m+1];
    if(tn1>=2){
      t_nai_3=ptr_nai_c_dp[tn1-2][tn2][tc][m  ];
      t_nai_4=ptr_nai_c_dp[tn1-2][tn2][tc][m+1];
    }
    if(tn2>=1){
      t_nai_5=ptr_nai_c_dp[tn1-1][tn2-1][tc][m  ];
      t_nai_6=ptr_nai_c_dp[tn1-1][tn2-1][tc][m+1];
    } 
    if(tc>=1)  t_nai_7=ptr_nai_c_dp[tn1-1][tn2][tc-1][m+1];
    for(int i1=0;i1<num1;i1++){
      for(int i2=0;i2<num2;i2++){
        set_n12(n1,n2,i1,i2,tn1,tn2);
        int xyz=get_xyz(n1);
        set_n12_m(n1_m,n2_m,n1,n2,xyz);
 
        int i1_m=basis_index::n_to_no[n1_m[0]][n1_m[1]][n1_m[2]];
        int ind_a=i1_m*num2+i2;
        double tmp_v[6];
        for(int c=0;c<loop_c;c++){ 
          tmp_v[c]=(P[xyz]-R1[xyz])*t_nai_1[ind_a*loop_c+c]-(P[xyz]-Rc[xyz])*t_nai_2[ind_a*loop_c+c];

        }
    
        if(n1_m[xyz]>0){
          int n1_m2[3]={n1[0],n1[1],n1[2]};
          n1_m2[xyz]-=2;
          int i1_m2=basis_index::n_to_no[n1_m2[0]][n1_m2[1]][n1_m2[2]];
          int ind_b=i1_m2*num2+i2;
          for(int c=0;c<loop_c;c++) 
            tmp_v[c]+=(0.5/(g1+g2))*((double)n1_m[xyz])*(t_nai_3[ind_b*loop_c+c]-t_nai_4[ind_b*loop_c+c]);
        }

        if(n2_m[xyz]>=0){
          int num2_m=get_num(tn2-1);
          int i2_m=basis_index::n_to_no[n2_m[0]][n2_m[1]][n2_m[2]];
          int ind_c=i1_m*num2_m+i2_m;
          for(int c=0;c<loop_c;c++) 
            tmp_v[c]+=(0.5/(g1+g2))*((double)n2[xyz])*(t_nai_5[ind_c*loop_c+c]-t_nai_6[ind_c*loop_c+c]);
        }

        if(tc==1){
          for(int c=0;c<3;c++){
            int nc[3]={0,0,0};
            int c_xyz1=c_to_xyz1[tc][c];
            nc[c_xyz1]++;
            if(nc[xyz]>0) tmp_v[c]+=((double)nc[xyz])*t_nai_7[ind_a];
          }
        }else if(tc==2){
          for(int c=0;c<loop_c;c++){
            int nc[3]={0,0,0};
            int c_xyz1=c_to_xyz1[tc][c];
            int c_xyz2=c_to_xyz2[tc][c];
            nc[c_xyz1]++;
            nc[c_xyz2]++;
            if(nc[xyz]>0){
              int nc_m[3]={nc[0],nc[1],nc[2]};
              nc_m[xyz]--;
              tmp_v[c]+=((double)nc[xyz])*t_nai_7[ind_a*3+2*nc_m[2]+nc_m[1]];
            }
          }
        }


        int ind=i1*num2+i2;
        for(int c=0;c<loop_c;c++) 
          ret_nai[ind*loop_c+c]=tmp_v[c];
      }
    }

  }else if(tn2>=1){
    t_nai_1=ptr_nai_c_dp[tn1][tn2-1][tc][m  ];
    t_nai_2=ptr_nai_c_dp[tn1][tn2-1][tc][m+1];
    if(tn2>=2){
      t_nai_3=ptr_nai_c_dp[tn1][tn2-2][tc][m  ];
      t_nai_4=ptr_nai_c_dp[tn1][tn2-2][tc][m+1];
    }
    if(tc>=1) t_nai_5=ptr_nai_c_dp[tn1][tn2-1][tc-1][m+1];
    int i1=0;
    for(int i2=0;i2<num2;i2++){
      set_n12(n1,n2,i1,i2,tn1,tn2);
      int xyz=get_xyz(n2);
      set_n12_m(n1_m,n2_m,n1,n2,xyz);

      int num2_m=get_num(tn2-1);
      int i2_m=basis_index::n_to_no[n2_m[0]][n2_m[1]][n2_m[2]];
      int ind_a=i1*num2_m+i2_m;

      double tmp_v[6];
      for(int c=0;c<loop_c;c++){ 
        tmp_v[c]=(P[xyz]-R2[xyz])*t_nai_1[ind_a*loop_c+c]-(P[xyz]-Rc[xyz])*t_nai_2[ind_a*loop_c+c];
      }

      if(n2_m[xyz]>0){
        int n2_m2[3]={n2[0],n2[1],n2[2]};
        n2_m2[xyz]-=2;
        int num2_m2=get_num(tn2-2);
        int i2_m2=basis_index::n_to_no[n2_m2[0]][n2_m2[1]][n2_m2[2]];
        int ind_b=i1*num2_m2+i2_m2;
        for(int c=0;c<loop_c;c++) 
          tmp_v[c]+=(0.5/(g1+g2))*((double)n2_m[xyz])*(t_nai_3[ind_b*loop_c+c]-t_nai_4[ind_b*loop_c+c]);
      }

      if(tc==1){
        for(int c=0;c<3;c++){
          int nc[3]={0,0,0};
          int c_xyz1=c_to_xyz1[tc][c];
          nc[c_xyz1]++;
          if(nc[xyz]>0) tmp_v[c]+=((double)nc[xyz])*t_nai_5[ind_a];
        }
      }else if(tc==2){
        for(int c=0;c<loop_c;c++){
          int nc[3]={0,0,0};
          int c_xyz1=c_to_xyz1[tc][c];
          int c_xyz2=c_to_xyz2[tc][c];
          nc[c_xyz1]++;
          nc[c_xyz2]++;
          if(nc[xyz]>0){
            int nc_m[3]={nc[0],nc[1],nc[2]};
            nc_m[xyz]--;
            tmp_v[c]+=((double)nc[xyz])*t_nai_5[ind_a*3+2*nc_m[2]+nc_m[1]];
          }
        }
      }

      int ind=i1*num2+i2;
      for(int c=0;c<loop_c;c++) 
        ret_nai[ind*loop_c+c]=tmp_v[c];
    }
  }


}


template <int in_tN>
double PInt1e_base<in_tN>::nuclear_c_simple(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<int> &nc,int m){
  int tn1=n1[0]+n1[1]+n1[2];
  int tn2=n2[0]+n2[1]+n2[2];
  int tnc=nc[0]+nc[1]+nc[2];
  double ret=0.0;

  if(tn1>0){
    if(n1[0]>0)       ret=nuclear_c_simple_sub1(n1,n2,nc,m,0);
    else if(n1[1]>0)  ret=nuclear_c_simple_sub1(n1,n2,nc,m,1);
    else              ret=nuclear_c_simple_sub1(n1,n2,nc,m,2);
    return ret;
  }else if(tn2>0){
    if(n2[0]>0)       ret=nuclear_c_simple_sub2(n1,n2,nc,m,0);
    else if(n2[1]>0)  ret=nuclear_c_simple_sub2(n1,n2,nc,m,1);
    else              ret=nuclear_c_simple_sub2(n1,n2,nc,m,2);
    return ret;
    
  }else{
    double P_minus_C_1;
    double P_minus_C_2;
    if(tnc==0){
      return nai_ss[m];
    }else if(tnc==1){
      if(nc[0]==1)      P_minus_C_1=P[0]-Rc[0]; 
      else if(nc[1]==1) P_minus_C_1=P[1]-Rc[1]; 
      else              P_minus_C_1=P[2]-Rc[2]; 
      return 2.0*(g1+g2)*P_minus_C_1*nai_ss[m+1];
    }else if(tnc==2){
      if(nc[0]==2){
        P_minus_C_1=P[0]-Rc[0]; 
        P_minus_C_2=P[0]-Rc[0];
        ret= -2*(g1+g2)*nai_ss[m+1];
      }else if(nc[1]==2){ 
        P_minus_C_1=P[1]-Rc[1]; 
        P_minus_C_2=P[1]-Rc[1];
        ret= -2*(g1+g2)*nai_ss[m+1];
      }else if(nc[2]==2){ 
        P_minus_C_1=P[2]-Rc[2]; 
        P_minus_C_2=P[2]-Rc[2];
        ret= -2*(g1+g2)*nai_ss[m+1];
      }else if(nc[0]==1 && nc[1]==1){ 
        P_minus_C_1=P[0]-Rc[0]; 
        P_minus_C_2=P[1]-Rc[1];
      }else if(nc[0]==1 && nc[2]==1){ 
        P_minus_C_1=P[0]-Rc[0]; 
        P_minus_C_2=P[2]-Rc[2];
      }else{ 
        P_minus_C_1=P[1]-Rc[1]; 
        P_minus_C_2=P[2]-Rc[2];
      }
      ret+=4.0*(g1+g2)*(g1+g2)*P_minus_C_1*P_minus_C_2*nai_ss[m+2];
      return ret;
    }else{
      cout<<"error no implementation yet in nai_deri_m_simple of PInt1e_base<double> class tnc>2: tnc"<<tnc<<endl;
      exit(1);
    }
  }
  return 0.0; //dummy
}

template <int in_tN>
double PInt1e_base<in_tN>::nuclear_c_simple_sub1(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<int> &nc,int m,int xyz){
  std::vector<int> na(3),na_minus(3),nb_minus(3),nc_minus(3);
  na[0]=n1[0]; na[1]=n1[1]; na[2]=n1[2];
  na[xyz]--;
  na_minus[0]=na[0]; na_minus[1]=na[1]; na_minus[2]=na[2];
  na_minus[xyz]--;
  nb_minus[0]=n2[0]; nb_minus[1]=n2[1]; nb_minus[2]=n2[2];     
  nb_minus[xyz]--;
  nc_minus[0]=nc[0]; nc_minus[1]=nc[1]; nc_minus[2]=nc[2];
  nc_minus[xyz]--;

  double ret=0;
  ret=(P[xyz]-R1[xyz])*nuclear_c_simple(na,n2,nc,m)
     -(P[xyz]-Rc[xyz])*nuclear_c_simple(na,n2,nc,m+1);

  if(na[xyz]!=0){
    ret+=(0.5/(g1+g2))*((double)na[xyz])*(nuclear_c_simple(na_minus,n2,nc,m)
                                         -nuclear_c_simple(na_minus,n2,nc,m+1));
  }
  if(n2[xyz]!=0){
    ret+=(0.5/(g1+g2))*((double)n2[xyz])*(nuclear_c_simple(na,nb_minus,nc,m)
                                         -nuclear_c_simple(na,nb_minus,nc,m+1));
  }
  if(nc[xyz]>0){
    ret+=((double)nc[xyz])*nuclear_c_simple(na,n2,nc_minus,m+1);
  }
  return ret;
}
 

template <int in_tN>
double PInt1e_base<in_tN>::nuclear_c_simple_sub2(const std::vector<int> &n1,const std::vector<int> &n2,const std::vector<int> &nc,int m,int xyz){
  std::vector<int> nb(3),na_minus(3),nb_minus(3),nc_minus(3);
  nb[0]=n2[0]; nb[1]=n2[1]; nb[2]=n2[2];
  nb[xyz]--;
  nb_minus[0]=nb[0]; nb_minus[1]=nb[1]; nb_minus[2]=nb[2];
  nb_minus[xyz]--;
  na_minus[0]=n1[0]; na_minus[1]=n1[1]; na_minus[2]=n1[2];     
  na_minus[xyz]--;
  nc_minus[0]=nc[0]; nc_minus[1]=nc[1]; nc_minus[2]=nc[2];
  nc_minus[xyz]--;

  double ret=0;
  ret=(P[xyz]-R2[xyz])*nuclear_c_simple(n1,nb,nc,m)
     -(P[xyz]-Rc[xyz])*nuclear_c_simple(n1,nb,nc,m+1);

  if(n1[xyz]!=0){
    ret+=(0.5/(g1+g2))*((double)n1[xyz])*(nuclear_c_simple(na_minus,nb,nc,m)
                                         -nuclear_c_simple(na_minus,nb,nc,m+1));
  }
  if(nb[xyz]!=0){
    ret+=(0.5/(g1+g2))*((double)nb[xyz])*(nuclear_c_simple(n1,nb_minus,nc,m)
                                         -nuclear_c_simple(n1,nb_minus,nc,m+1));
  }
  if(nc[xyz]>0){
    ret+=((double)nc[xyz])*nuclear_c_simple(n1,nb,nc_minus,m+1);
  }
  return ret;
}

//
//  DEBUG_DRIVER
//


int DEBUG_PInt1e::debug_driver_overlap(int max_ij){

  std::cout<<" ========== debug_driver_overlap of PInt1e_base ========== "<<std::endl;

  std::vector<double> Ri(3),Rj(3);
  Ri[0]=0.3;      Ri[1]=0.4;      Ri[2]=0.1;
  Rj[0]=-0.1;     Rj[1]=0.2;      Rj[2]=-0.3;

  double gi=0.7;
  double gj=0.6;

  PInt1e_base<0> pint1e;

  pint1e.set_gR_12(gi,Ri,gj,Rj);

//  cout<<" ----- pint1e ----- "<<endl;
//  pint1e.show_state();

  std::vector<double> dI_A(100),dI_B(100);
  std::vector<double> debug_overlap1;

  


  for(int i=0;i<=max_ij;i++){
    for(int j=0;j<=max_ij;j++){
      std::vector<int> ni(3),nj(3);
      int num_ia=PInt1e_base<0>::get_num(i);
      int num_ib=PInt1e_base<0>::get_num(j);
      // dI_A
      for(int ia=0;ia<num_ia;ia++){
        ni=pint1e.get_no_to_n(i,ia);
        dI_A[ia]=pint1e.cal_I(gi,ni);
      }
      // dI_B
      for(int ib=0;ib<num_ib;ib++){
        nj=pint1e.get_no_to_n(j,ib);
        dI_B[ib]=pint1e.cal_I(gj,nj);
      }
 
      pint1e.overlap(debug_overlap1,i,j,dI_A,dI_B);

      for(int ia=0;ia<num_ia;ia++){
        for(int ib=0;ib<num_ib;ib++){
          ni=pint1e.get_no_to_n(i,ia);
          nj=pint1e.get_no_to_n(j,ib);
                  
          int cc=ia*num_ib+ib; 

          double v_comp1=pint1e.overlap_simple(ni,nj)
                       *pint1e.cal_I(gi,ni)*pint1e.cal_I(gj,nj);

          if(fabs(v_comp1-debug_overlap1[cc])>1.0e-10){
            cout<<" ********* ERROR *******"<<endl;
            cout<<" i,j,k  "<<i<<" "<<j<<" num "<<num_ia<<" "<<num_ib<<" "<<endl;
            cout<<"   ia="<<ia<<" ni "<<ni[0]<<" "<<ni[1]<<" "<<ni[2]<<endl;
            cout<<"   ib="<<ib<<" nj "<<nj[0]<<" "<<nj[1]<<" "<<nj[2]<<endl;
            cout<<"  v_comp1             :  "<<v_comp1<<endl;
            cout<<"  debug_overlap1      :  "<<debug_overlap1[cc]<<endl;
            return 1;
          }


        }
      }

    }
  }

  cout<<" ok "<<endl;
  return 0;
}



int DEBUG_PInt1e::debug_driver_kinetic(int max_ij=3){

  std::cout<<" ========== debug_driver_kinetic of PInt1e_base ========== "<<std::endl;

  std::vector<double> Ri(3),Rj(3);
  Ri[0]=0.3;      Ri[1]=0.4;      Ri[2]=0.1;
  Rj[0]=-0.1;     Rj[1]=0.2;      Rj[2]=-0.3;

  double gi=0.7;
  double gj=0.6;

  PInt1e_base<0> pint1e;

  pint1e.set_gR_12(gi,Ri,gj,Rj);

//  cout<<" ----- pint1e ----- "<<endl;
//  pint1e.show_state();

  std::vector<double> dI_A(100),dI_B(100);
  std::vector<double> debug_kinetic1,debug_kinetic2;


  for(int i=0;i<=max_ij;i++){
    for(int j=0;j<=max_ij;j++){
      std::vector<int> ni(3),nj(3);
      int num_ia=PInt1e_base<0>::get_num(i);
      int num_ib=PInt1e_base<0>::get_num(j);
      // dI_A
      for(int ia=0;ia<num_ia;ia++){
        ni=pint1e.get_no_to_n(i,ia);
        dI_A[ia]=pint1e.cal_I(gi,ni);
      }
      // dI_B
      for(int ib=0;ib<num_ib;ib++){
        nj=pint1e.get_no_to_n(j,ib);
        dI_B[ib]=pint1e.cal_I(gj,nj);
      }
 
      pint1e.kinetic(debug_kinetic1,i,j,dI_A,dI_B);

      for(int ia=0;ia<num_ia;ia++){
        for(int ib=0;ib<num_ib;ib++){
          ni=pint1e.get_no_to_n(i,ia);
          nj=pint1e.get_no_to_n(j,ib);
                  
          int cc=ia*num_ib+ib; 

          double v_comp1=pint1e.kinetic_simple(ni,nj)
                       *pint1e.cal_I(gi,ni)*pint1e.cal_I(gj,nj);

          if(fabs(v_comp1-debug_kinetic1[cc])>1.0e-10){
            cout<<" ********* ERROR *******"<<endl;
            cout<<" i,j,k  "<<i<<" "<<j<<" num "<<num_ia<<" "<<num_ib<<" "<<endl;
            cout<<"   ia="<<ia<<" ni "<<ni[0]<<" "<<ni[1]<<" "<<ni[2]<<endl;
            cout<<"   ib="<<ib<<" nj "<<nj[0]<<" "<<nj[1]<<" "<<nj[2]<<endl;
            cout<<"  v_comp1             :  "<<v_comp1<<endl;
            cout<<"  debug_kinetic1      :  "<<debug_kinetic1[cc]<<endl;
            cout<<"  debug_kinetic2      :  "<<debug_kinetic2[cc]<<endl;
            return 1;
          }


        }
      }

    }
  }

  cout<<" ok "<<endl;
  return 0;
}


int DEBUG_PInt1e::debug_driver_nuclear(int max_ij=3){

  std::cout<<" ========== debug_driver_nuclear of PInt1e_base ========== "<<std::endl;

  std::vector<double> Ri(3),Rj(3),Rc(3);
  Ri[0]=0.3;      Ri[1]=0.4;      Ri[2]=0.1;
  Rj[0]=-0.1;     Rj[1]=0.2;      Rj[2]=-0.3;
  Rc[0]=-1.1;     Rc[1]=2.2;      Rc[2]=-1.3;

  double gi=0.7;
  double gj=0.6;

  PInt1e_base<0> pint1e;


//  cout<<" ----- pint1e ----- "<<endl;
//  pint1e.show_state();

  std::vector<double> dI_A(100),dI_B(100);
  std::vector<double> debug_nuclear1;


  for(int i=0;i<=max_ij;i++){
    for(int j=0;j<=max_ij;j++){
      std::vector<int> ni(3),nj(3);
      int num_ia=PInt1e_base<0>::get_num(i);
      int num_ib=PInt1e_base<0>::get_num(j);
      // dI_A
      for(int ia=0;ia<num_ia;ia++){
        ni=pint1e.get_no_to_n(i,ia);
        dI_A[ia]=pint1e.cal_I(gi,ni);
      }
      // dI_B
      for(int ib=0;ib<num_ib;ib++){
        nj=pint1e.get_no_to_n(j,ib);
        dI_B[ib]=pint1e.cal_I(gj,nj);
      }
 
      int tn=i+j;
      pint1e.set_gR_12(gi,Ri,gj,Rj,tn+2,Rc);
      pint1e.nuclear(debug_nuclear1,i,j,dI_A,dI_B);

      for(int ia=0;ia<num_ia;ia++){
        for(int ib=0;ib<num_ib;ib++){
          ni=pint1e.get_no_to_n(i,ia);
          nj=pint1e.get_no_to_n(j,ib);
                  
          int cc=ia*num_ib+ib; 

          double v_comp1=pint1e.nuclear_simple(ni,nj,0)
                       *pint1e.cal_I(gi,ni)*pint1e.cal_I(gj,nj);

          if(fabs(v_comp1-debug_nuclear1[cc])>1.0e-10){
            cout<<" ********* ERROR *******"<<endl;
            cout<<" i,j,k  "<<i<<" "<<j<<" num "<<num_ia<<" "<<num_ib<<" "<<endl;
            cout<<"   ia="<<ia<<" ni "<<ni[0]<<" "<<ni[1]<<" "<<ni[2]<<endl;
            cout<<"   ib="<<ib<<" nj "<<nj[0]<<" "<<nj[1]<<" "<<nj[2]<<endl;
            cout<<"  v_comp1             :  "<<v_comp1<<endl;
            cout<<"  debug_nuclear1      :  "<<debug_nuclear1[cc]<<endl;
            return 1;
          }


        }
      }

    }
  }


  cout<<" ok "<<endl;
  return 0;
}



int DEBUG_PInt1e::debug_driver_nuclear_c(int max_ij=3){

  std::cout<<" ========== debug_driver_nuclear_c of PInt1e_base ========== "<<std::endl;

  std::vector<double> Ri(3),Rj(3),Rc(3);
  Ri[0]=0.3;      Ri[1]=0.4;      Ri[2]=0.1;
  Rj[0]=-0.1;     Rj[1]=0.2;      Rj[2]=-0.3;
  Rc[0]=-1.1;     Rc[1]=2.2;      Rc[2]=-1.3;

  double gi=0.7;
  double gj=0.6;

  PInt1e_base<0> pint1e;

//  cout<<" ----- pint1e ----- "<<endl;
//  pint1e.show_state();

  std::vector<double> dI_A(100),dI_B(100);
  std::vector<double> debug_nuclear1,debug_nuclear2;


  for(int i=0;i<=max_ij;i++){
    for(int j=0;j<=max_ij;j++){
      std::vector<int> ni(3),nj(3);
      int num_ia=PInt1e_base<0>::get_num(i);
      int num_ib=PInt1e_base<0>::get_num(j);
      // dI_A
      for(int ia=0;ia<num_ia;ia++){
        ni=pint1e.get_no_to_n(i,ia);
        dI_A[ia]=pint1e.cal_I(gi,ni);
      }
      // dI_B
      for(int ib=0;ib<num_ib;ib++){
        nj=pint1e.get_no_to_n(j,ib);
        dI_B[ib]=pint1e.cal_I(gj,nj);
      }
 
      int tn=i+j+2;
      pint1e.set_gR_12(gi,Ri,gj,Rj,tn,Rc);
      pint1e.nuclear_c(debug_nuclear1,i,j,1,dI_A,dI_B);
      pint1e.nuclear_c(debug_nuclear2,i,j,2,dI_A,dI_B);

      for(int ia=0;ia<num_ia;ia++){
        for(int ib=0;ib<num_ib;ib++){
          ni=pint1e.get_no_to_n(i,ia);
          nj=pint1e.get_no_to_n(j,ib);
          int cc=ia*num_ib+ib; 

          int loop_c=3;
          for(int c=0;c<3;c++){
            std::vector<int> nc=PInt1e_base<0>::get_nc(1,c);
            double v_comp1=pint1e.nuclear_c_simple(ni,nj,nc,0)
                          *pint1e.cal_I(gi,ni)*pint1e.cal_I(gj,nj);
            if(fabs(v_comp1-debug_nuclear1[cc*loop_c+c])>1.0e-10){ 
              cout<<" ********* ERROR *******"<<endl;
              cout<<" nc "<<nc[0]<<" "<<nc[1]<<" "<<nc[2]<<endl;
              cout<<" i,j,k  "<<i<<" "<<j<<" num "<<num_ia<<" "<<num_ib<<" "<<endl;
              cout<<"   ia="<<ia<<" ni "<<ni[0]<<" "<<ni[1]<<" "<<ni[2]<<endl;
              cout<<"   ib="<<ib<<" nj "<<nj[0]<<" "<<nj[1]<<" "<<nj[2]<<endl;
              cout<<"  v_comp1             :  "<<v_comp1<<endl;
              cout<<"  debug_nuclear1      :  "<<debug_nuclear1[cc*loop_c+c]<<endl;
              return 1;
            }
          }

          loop_c=6; 
          for(int c=0;c<6;c++){
            std::vector<int> nc=PInt1e_base<0>::get_nc(2,c);
            double v_comp1=pint1e.nuclear_c_simple(ni,nj,nc,0)
                          *pint1e.cal_I(gi,ni)*pint1e.cal_I(gj,nj);
            if(fabs(v_comp1-debug_nuclear2[cc*loop_c+c])>1.0e-10){
              cout<<" ********* ERROR *******"<<endl;
              cout<<" nc "<<nc[0]<<" "<<nc[1]<<" "<<nc[2]<<endl;
              cout<<" i,j,k  "<<i<<" "<<j<<" num "<<num_ia<<" "<<num_ib<<" "<<endl;
              cout<<"   ia="<<ia<<" ni "<<ni[0]<<" "<<ni[1]<<" "<<ni[2]<<endl;
              cout<<"   ib="<<ib<<" nj "<<nj[0]<<" "<<nj[1]<<" "<<nj[2]<<endl;
              cout<<"  v_comp1             :  "<<v_comp1<<endl;
              cout<<"  debug_nuclear2      :  "<<debug_nuclear2[cc*loop_c+c]<<endl;
              return 1;
            }
 
          }
        }
      }

    }
  }


  cout<<" ok "<<endl;
  return 0;
}

}  // end of namespace "PInt"

#endif // end of include-guard
