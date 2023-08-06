
#ifndef PINT2E_VHRR_DETAIL_HPP
#define PINT2E_VHRR_DETAIL_HPP

#define _USE_MATH_DEFINES
#include <math.h>
#include <time.h>
#include <stdlib.h>

#include <iostream>
#include <iomanip>
#include <fstream>


namespace PInt {

using namespace std;

//template <typename double>
void PInt2e_vhrr_dp::ERI_hrr_recursion_sub(double *ret_eri,int tn1,int tn2,int tn3,int tn4,int m){

  int num1=get_num(tn1);
  int num2=get_num(tn2);
  int num3=get_num(tn3);
  int num4=get_num(tn4);

  if(tn1==0 && tn3==0){
    int cc=0;
    for(int i2=0;i2<num2;i2++){
      for(int i4=0;i4<num4;i4++){
        ret_eri[cc]=eri_dp[0][tn2][0][tn4][m][cc];
        cc++;
      }
    }
    return;
  }

  if(tn1>=1){
    int num2_p=get_num(tn2+1);
    int num1_m=get_num(tn1-1);
    double *t_eri_1 = new double [num1_m*num2_p*num3*num4];
    double *t_eri_2 = new double [num1_m*num2  *num3*num4];
    ERI_hrr_recursion_sub(t_eri_1,tn1-1,tn2+1,tn3,tn4,m);
    ERI_hrr_recursion_sub(t_eri_2,tn1-1,tn2,tn3,tn4,m);
    int cc=0;
    for(int i1=0;i1<num1;i1++){
      for(int i2=0;i2<num2;i2++){
        for(int i3=0;i3<num3;i3++){
          for(int i4=0;i4<num4;i4++){
            int n1[3],n2[3],n3[3],n4[3];
            set_n1234(n1,n2,n3,n4,i1,i2,i3,i4,tn1,tn2,tn3,tn4);
            int xyz=get_xyz(n1);
            if(n1[xyz]>0){
              int n1_m[3];
              set_n_m(n1_m, n1, xyz);
              int i1_m = calc_m(n1_m);
              int n2_p[3];
              set_n_p(n2_p, n2, xyz);
              int i2_p = calc_m(n2_p);
              int ind_1 = i1_m*num2_p*num3*num4 + i2_p*num3*num4 + i3*num4 + i4;
              int ind_2 = i1_m*num2  *num3*num4 + i2  *num3*num4 + i3*num4 + i4;
              ret_eri[cc]=t_eri_1[ind_1]+(R2[xyz]-R1[xyz])*t_eri_2[ind_2];
            }else{
              ret_eri[cc]=0.0;
            }
            cc++;
          }
        }
      }
    }
    delete [] t_eri_1;
    delete [] t_eri_2;
  }else if(tn3>=1){
    int num4_p=get_num(tn4+1);
    int num3_m=get_num(tn3-1);
    double *t_eri_1 = new double [num1*num2*num3_m*num4_p];
    double *t_eri_2 = new double [num1*num2*num3_m*num4];
    ERI_hrr_recursion_sub(t_eri_1,tn1,tn2,tn3-1,tn4+1,m);
    ERI_hrr_recursion_sub(t_eri_2,tn1,tn2,tn3-1,tn4,  m);

    int cc=0;
    // tn1=1, i1=0
    for(int i2=0;i2<num2;i2++){
      for(int i3=0;i3<num3;i3++){
        for(int i4=0;i4<num4;i4++){
          int n1[3],n2[3],n3[3],n4[3];
          set_n1234(n1,n2,n3,n4,0,i2,i3,i4,1,tn2,tn3,tn4);
          int xyz=get_xyz(n3);
          if(n3[xyz]>0){
            int n3_m[3];
            set_n_m(n3_m, n3, xyz);
            int i3_m = calc_m(n3_m);
            int n4_p[3];
            set_n_p(n4_p, n4, xyz);
            int i4_p = calc_m(n4_p);
            int ind_1 = i2*num3_m*num4_p + i3_m*num4_p + i4_p;
            int ind_2 = i2*num3_m*num4   + i3_m*num4   + i4;
            ret_eri[cc]=t_eri_1[ind_1]+(R4[xyz]-R3[xyz])*t_eri_2[ind_2];
          }else{
            ret_eri[cc]=0.0;
          }
          cc++;
        }
      }
    }
    delete [] t_eri_1;
    delete [] t_eri_2;
  }

}


//template <typename double>
void PInt2e_vhrr_dp::ERI_hrr_dp_sub(double *ret_eri,int tn1,int tn2,int tn3,int tn4,int m){

  int num1=get_num(tn1);
  int num2=get_num(tn2);
  int num3=get_num(tn3);
  int num4=get_num(tn4);

  if(tn1==0 && tn3==0){
    int cc=0;
    for(int i2=0;i2<num2;i2++){
      for(int i4=0;i4<num4;i4++){
        ret_eri[cc]=eri_dp[0][tn2][0][tn4][m][cc];
        cc++;
      }
    }
    return;
  }

  double *t_eri_1,*t_eri_2;

  if(tn1>=1){
    int num2_p=get_num(tn2+1);
    int num1_m=get_num(tn1-1);

    t_eri_1 = eri_dp[tn1-1][tn2+1][tn3][tn4][m];
    t_eri_2 = eri_dp[tn1-1][tn2  ][tn3][tn4][m];
    int cc=0;
    for(int i1=0;i1<num1;i1++){
      for(int i2=0;i2<num2;i2++){
        for(int i3=0;i3<num3;i3++){
          for(int i4=0;i4<num4;i4++){
            int n1[3],n2[3],n3[3],n4[3];
            set_n1234(n1,n2,n3,n4,i1,i2,i3,i4,tn1,tn2,tn3,tn4);
            int xyz=get_xyz(n1);
            if(n1[xyz]>0){
              int n1_m[3];
              set_n_m(n1_m, n1, xyz);
              int i1_m = calc_m(n1_m);
              int n2_p[3];
              set_n_p(n2_p, n2, xyz);
              int i2_p = calc_m(n2_p);
              int ind_1 = i1_m*num2_p*num3*num4 + i2_p*num3*num4 + i3*num4 + i4;
              int ind_2 = i1_m*num2  *num3*num4 + i2  *num3*num4 + i3*num4 + i4;
              ret_eri[cc]=t_eri_1[ind_1]+(R2[xyz]-R1[xyz])*t_eri_2[ind_2];
            }else{
              ret_eri[cc]=0.0;
            }
            cc++;
          }
        }
      }
    }
  }else if(tn3>=1){
    int num4_p=get_num(tn4+1);
    int num3_m=get_num(tn3-1);

    t_eri_1 = eri_dp[tn1][tn2][tn3-1][tn4+1][m];
    t_eri_2 = eri_dp[tn1][tn2][tn3-1][tn4  ][m];
    int cc=0;
    // tn1=1, i1=0
    for(int i2=0;i2<num2;i2++){
      for(int i3=0;i3<num3;i3++){
        for(int i4=0;i4<num4;i4++){
          int n1[3],n2[3],n3[3],n4[3];
          set_n1234(n1,n2,n3,n4,0,i2,i3,i4,1,tn2,tn3,tn4);
          int xyz=get_xyz(n3);
          if(n3[xyz]>0){
            int n3_m[3];
            set_n_m(n3_m, n3, xyz);
            int i3_m = calc_m(n3_m);
            int n4_p[3];
            set_n_p(n4_p, n4, xyz);
            int i4_p = calc_m(n4_p);
            int ind_1 = i2*num3_m*num4_p + i3_m*num4_p + i4_p;
            int ind_2 = i2*num3_m*num4   + i3_m*num4   + i4;
            ret_eri[cc]=t_eri_1[ind_1]+(R4[xyz]-R3[xyz])*t_eri_2[ind_2];
          }else{
            ret_eri[cc]=0.0;
          }
          cc++;
        }
      }
    }
  }

}



//template <typename double>
void PInt2e_vhrr_dp::ERI_dp_clear_flags(int tn1, int tn2, int tn3, int tn4,int max_m=0)
{

  for(int i2=0;i2<=tn1+tn2;i2++){
    for(int i4=0;i4<=tn3+tn4;i4++){
      for(int m=(tn1+tn2+tn3+tn4-i2-i4);m>=0;m--){
        eri_dp_vrr_flags[i2][i4][m] = false;
        eri_dp_hrr_flags[0][i2][0][i4][m] = false;
      }
    }
  }

  for(int i1=0;i1<=tn1;i1++){
    for(int i2=0;i2<=tn2+tn1-i1;i2++){
      for(int i3=0;i3<=tn3;i3++){
        for(int i4=0;i4<=tn4+tn3-i3;i4++){
          if(i1!=0 || i3!=0){
            for(int m=0;m<=max_m;m++){
              eri_dp_hrr_flags[i1][i2][i3][i4][m] = false;
            }
          }
        }
      }
    }
  }

}


//template <typename double>
void PInt2e_vhrr_dp::ERI_dp_mark_vrr_flags(int tn2, int tn4, int m)
{
  // tn1=0, tn3=0
  if (eri_dp_vrr_flags[tn2][tn4][m]) {
    return;
  }

  eri_dp_vrr_flags[tn2][tn4][m] = true;
  eri_dp_hrr_flags[0][tn2][0][tn4][m] = true;
  if (tn2 + tn4 == 0) {
    return;
  }

  // vrr
  if (tn2 >= 1) {  // t1=0, t3=0
    ERI_dp_mark_vrr_flags(tn2 - 1, tn4, m + 0);
    ERI_dp_mark_vrr_flags(tn2 - 1, tn4, m + 1);
    if (tn2 >= 2) {
      ERI_dp_mark_vrr_flags(tn2 - 2,  tn4, m + 0);
      ERI_dp_mark_vrr_flags(tn2 - 2,  tn4, m + 1);
    }
    if (tn4 >= 1) {
      ERI_dp_mark_vrr_flags(tn2 - 1,  tn4 - 1, m + 1);
    }
  } else if (tn4 >= 1) {  // t1=0, t2=0, t3=0
    ERI_dp_mark_vrr_flags(0, tn4 - 1, m + 0);
    ERI_dp_mark_vrr_flags(0, tn4 - 1, m + 1);
    if (tn4 >= 2) {
      ERI_dp_mark_vrr_flags(0, tn4 - 2, m + 0);
      ERI_dp_mark_vrr_flags(0, tn4 - 2, m + 1);
    }
  }

}


//template <typename double>
void PInt2e_vhrr_dp::ERI_dp_mark_flags(int tn1, int tn2, int tn3, int tn4, int m){
  if (eri_dp_hrr_flags[tn1][tn2][tn3][tn4][m]) {
    return;
  }

  eri_dp_hrr_flags[tn1][tn2][tn3][tn4][m] = true;

  if(tn1==0 && tn3==0){
    ERI_dp_mark_vrr_flags(tn2,tn4,m);
  }

  // hrr
  if(tn1>=1){
    ERI_dp_mark_flags(tn1-1,tn2+1,tn3,tn4,m);
    ERI_dp_mark_flags(tn1-1,tn2,  tn3,tn4,m);
  }else if(tn3>=1){
    ERI_dp_mark_flags(tn1,tn2,tn3-1,tn4+1,m);
    ERI_dp_mark_flags(tn1,tn2,tn3-1,tn4  ,m);
  } 

}



void PInt2e_vhrr_dp::ERI_init(int tn1, int tn2, int tn3, int tn4)
{

  ERI_dp_clear_flags(tn1, tn2, tn3, tn4, 0);
  ERI_dp_mark_flags(tn1, tn2, tn3, tn4, 0);


  // vrr-loop
  for(int i1=0;i1<=0;i1++){
    for(int i2=0;i2<=tn1+tn2;i2++){
      for(int i3=0;i3<=0;i3++){
        for(int i4=0;i4<=tn3+tn4;i4++){
          for(int m=(tn1+tn2+tn3+tn4-i1-i2-i3-i4);m>=0;m--){
            // We skip the unnecessary entries by examing the "eri_dp_flags" table.
            if (eri_dp_vrr_flags[i2][i4][m]) {
              if(i2<=max_tn_array && i4<=max_tn_array){
                eri_dp[0][i2][0][i4][m] = eri_array[i1][i2][i3][i4][m];
              }else{
                eri_dp[0][i2][0][i4][m] = new double [get_num(i2)*get_num(i4)];
              }
            }
          }
        }
      }
    }
  }

  // hrr-loop
  for(int i1=0;i1<=tn1;i1++){
    for(int i2=0;i2<=tn2+tn1-i1;i2++){
      for(int i3=0;i3<=tn3;i3++){
        for(int i4=0;i4<=tn4+tn3-i3;i4++){
          if(i1!=0 || i3!=0){
            // We skip the unnecessary entries by examing the "eri_dp_flags" table.
            if (eri_dp_hrr_flags[i1][i2][i3][i4][0]) {
              if(i1<=max_tn_array && i2<=max_tn_array && i3<=max_tn_array && i4<=max_tn_array){
                eri_dp[i1][i2][i3][i4][0] = eri_array[i1][i2][i3][i4][0];
              }else{
                eri_dp[i1][i2][i3][i4][0] = new double [get_num(i1)*get_num(i2)*get_num(i3)*get_num(i4)];
              }
            }
          }
        }
      }
    }
  }

}



void PInt2e_vhrr_dp::ERI_finalize(int tn1, int tn2, int tn3, int tn4)
{

  for(int i1=0;i1<=0;i1++){
    for(int i2=0;i2<=tn1+tn2;i2++){
      for(int i3=0;i3<=0;i3++){
        for(int i4=0;i4<=tn3+tn4;i4++){
          for(int m=(tn1+tn2+tn3+tn4-i1-i2-i3-i4);m>=0;m--){
            // We skip the unnecessary entries by examing the "eri_dp_flags" table.
            if (eri_dp_vrr_flags[i2][i4][m]) {
              if(i2<=max_tn_array && i4<=max_tn_array){
              }else{
                delete [] eri_dp[0][i2][0][i4][m];
                eri_dp[0][i2][0][i4][m] = 0;
              }
            }
          }
        }
      }
    }
  }

  for(int i1=0;i1<=tn1;i1++){
    for(int i2=0;i2<=tn2+tn1-i1;i2++){
      for(int i3=0;i3<=tn3;i3++){
        for(int i4=0;i4<=tn4+tn3-i3;i4++){
          if(i1!=0 || i3!=0){
            // We skip the unnecessary entries by examing the "eri_dp_flags" table.
            if (eri_dp_hrr_flags[i1][i2][i3][i4][0]) {
              if(i1<=max_tn_array && i2<=max_tn_array && i3<=max_tn_array && i4<=max_tn_array){
              }else{
                delete [] eri_dp[i1][i2][i3][i4][0];
                eri_dp[i1][i2][i3][i4][0] = 0;
              }
            }
          }
        }
      }
    }
  }

} 


//template <typename double>
//void PInt2e_vhrr_dp::ERI_dp(std::vector<double> &ret_eri,int tn1,int tn2,int tn3,int tn4,
//                            const std::vector<double> &dI_a,const std::vector<double> &dI_b,
//                            const std::vector<double> &dI_c,const std::vector<double> &dI_d)
void PInt2e_vhrr_dp::ERI_dp(double *ret_eri, int tn1, int tn2, int tn3, int tn4,
                            const double *dI_a, const double *dI_b, const double *dI_c, const double *dI_d)
{
  int num1=get_num(tn1);
  int num2=get_num(tn2);
  int num3=get_num(tn3);
  int num4=get_num(tn4);

  // vrr-loop
  for(int i1=0;i1<=0;i1++){
    for(int i2=0;i2<=tn1+tn2;i2++){
      for(int i3=0;i3<=0;i3++){
        for(int i4=0;i4<=tn3+tn4;i4++){
          for(int m=(tn1+tn2+tn3+tn4-i1-i2-i3-i4);m>=0;m--){
            // We skip the unnecessary entries by examing the "eri_dp_flags" table.
            if (eri_dp_vrr_flags[i2][i4][m]) {
              ERI_vrr_dp_sub(eri_dp[0][i2][0][i4][m], i2, i4, m);
            }
          }
        }
      }
    }
  }

  // hrr-loop
  for(int i1=0;i1<=tn1;i1++){
    for(int i2=0;i2<=tn2+tn1-i1;i2++){
      for(int i3=0;i3<=tn3;i3++){
        for(int i4=0;i4<=tn4+tn3-i3;i4++){
          if(i1!=0 || i3!=0){
            // We skip the unnecessary entries by examing the "eri_dp_flags" table.
            if (eri_dp_hrr_flags[i1][i2][i3][i4][0]) {
              ERI_hrr_dp_sub(eri_dp[i1][i2][i3][i4][0], i1, i2, i3, i4, 0);
            }
          }
        }
      }
    }
  }
 
  for(int i1=0;i1<num1;i1++){
    for(int i2=0;i2<num2;i2++){
      for(int i3=0;i3<num3;i3++){
        for(int i4=0;i4<num4;i4++){
          int ind=i1*num2*num3*num4+i2*num3*num4+i3*num4+i4;
          ret_eri[ind]=eri_dp[tn1][tn2][tn3][tn4][0][ind]*dI_a[i1]*dI_b[i2]*dI_c[i3]*dI_d[i4];
        }
      }
    }
  }
 
}


//template <typename double>
void PInt2e_vhrr_dp::ERI_vrr_dp_sub(double *ret_eri,int tn2,int tn4,int m){
  if(tn2+tn4==0){
    ret_eri[0]=vrr4_ssss[m];
    return;
  }

  if(tn2>=1){
    ERI_vrr_dp_sub_tn2(ret_eri, tn2, tn4, m);
  }else if(tn4>=1){
    ERI_vrr_dp_sub_tn4(ret_eri, tn4, m);
  }
}





//template <typename double>
void PInt2e_vhrr_dp::ERI_vrr_dp_sub_tn2(double* ret_eri, int tn2, int tn4, int m)
{
  double* t_eri_1;
  double* t_eri_2;
  double* t_eri_3;
  double* t_eri_4;
//  double* t_eri_7;
  double* t_eri_8;

  const int tn1 = 0;
  const int tn3 = 0;

  const int num2=get_num(tn2);
  const int num3=get_num(tn3);
  const int num4=get_num(tn4);

  // Optimization: we move only 'num4_m' out of the loop.
  const int num4_m = get_num(tn4-1);

  t_eri_1=eri_dp[tn1][tn2-1][tn3][tn4][m+0];
  t_eri_2=eri_dp[tn1][tn2-1][tn3][tn4][m+1];
  if(tn2>=2) t_eri_3=eri_dp[tn1][tn2-2][tn3][tn4][m+0];
  if(tn2>=2) t_eri_4=eri_dp[tn1][tn2-2][tn3][tn4][m+1];
  if(tn4>=1) t_eri_8=eri_dp[tn1][tn2-1][tn3][tn4-1][m+1];

  const int i1=0;

  // Optimization: operator strength reduction for 'ind'.
  int ind = 0;

  int n1[3];
  set_n(n1, i1, tn1);

  for(int i2=0;i2<num2;i2++){
    int n2[3];
    set_n(n2, i2, tn2);

    int xyz=get_xyz(n2);

    int n1_m[3];
    int n2_m[3];
    set_n_m(n1_m, n1, xyz);
    set_n_m(n2_m, n2, xyz);

    int i2_m = calc_m(n2_m); 

    double c_P_minus_R2 = P[xyz] - R2[xyz];
    double c_W_minus_P  = W[xyz] - P[xyz];

    // Optimization: operator strength reduction for 'ind_a'.
    int ind_a = i2_m * num4;

    for(int i4=0;i4<num4;i4++){
      int n4[3];
      set_n(n4, i4, tn4);

      int n4_m[3];
      set_n_m(n4_m, n4, xyz);

      // Optimization: operator strength reduction for 'num2_m'.
      //const int num2_m = get_num(tn2-1);
      //const int num2_m = num2 - (tn2 + 1);

      int i2_m = calc_m(n2_m); 

      // Optimization: operator strength reduction for 'ind_a'.
      //int ind_a = calc_ind(i1, i2_m, i3, i4, num2_m, num3, num4);

      double tmp_v = c_P_minus_R2 * t_eri_1[ind_a]
                   + c_W_minus_P  * t_eri_2[ind_a];

      if (n2_m[xyz] > 0) {
        // Optimization: operator strength reduction for 'num3_m'.
        //const int num2_m2 = get_num(tn2-2);
        //const int num2_m2 = num2_m - (tn2 + 1);
        int i2_m2 = calc_m2(n2, xyz);
        int i = i2_m2 * num4 + i4;;
        double t = c_0_5_div_t1 * n2_m[xyz] * (t_eri_3[i] - rou_div_t1 * t_eri_4[i]);
        tmp_v += t;
      }

      if(n4_m[xyz] >= 0){
        // Optimization: we move only 'num4_m' out of the loop.
        //const int num4_m = get_num(tn4-1);
        int i4_m = calc_m(n4_m);
        int i = i2_m * num4_m + i4_m;
        double t = c_0_5_div_t1_plus_t2 * n4[xyz] * t_eri_8[i];
        tmp_v += t;
      }

      // Optimization: operator strength reduction for 'ind'.
      //int ind = calc_ind(i1, i2, i3, i4, num2, num3, num4);
      ret_eri[ind]=tmp_v;

      // Optimization: operator strength reduction for 'ind' and 'ind_a'.
      ind++;
      ind_a++;
    }
  }
}


//template <typename double>
void PInt2e_vhrr_dp::ERI_vrr_dp_sub_tn4(double* ret_eri, int tn4, int m)
{
  double* t_eri_1;
  double* t_eri_2;
  double* t_eri_3;
  double* t_eri_4;

  const int tn1 = 0;
  const int tn2 = 0;
  const int tn3 = 0;

  const int num2=get_num(tn2);
  const int num3=get_num(tn3);
  const int num4=get_num(tn4);

  const int num4_m2=get_num(tn4-2);

  t_eri_1=eri_dp[tn1][tn2][tn3][tn4-1][m+0];
  t_eri_2=eri_dp[tn1][tn2][tn3][tn4-1][m+1];
  if(tn4>=2) t_eri_3=eri_dp[tn1][tn2][tn3][tn4-2][m+0];
  if(tn4>=2) t_eri_4=eri_dp[tn1][tn2][tn3][tn4-2][m+1];

  const int i1=0;
  const int i2=0;
  const int i3=0;

  int n1[3];
  int n2[3];
  int n3[3];
  set_n(n1, i1, tn1);
  set_n(n2, i2, tn2);
  set_n(n3, i3, tn3);

  // Optimization: operator strength reduction for 'ind'.
  int ind = 0;

  for(int i4=0;i4<num4;i4++){
    int n4[3];
    set_n(n4, i4, tn4);

    int xyz=get_xyz(n4);

    int n1_m[3],n2_m[3],n3_m[3],n4_m[3];
    set_n1234_m(n1_m,n2_m,n3_m,n4_m,n1,n2,n3,n4,xyz);
 
    // Optimization: operator strength reduction for 'num4_m'.
    //int num4_m = num4 - (tn4 + 1);

    int ind_a = calc_m(n4_m);
 
    double tmp_v=(Q[xyz]-R4[xyz])*t_eri_1[ind_a]
                +(W[xyz]- Q[xyz])*t_eri_2[ind_a];

    if (n4_m[xyz] > 0) {
      int i = calc_m2(n4, xyz);
      double t = c_0_5_div_t2 * n4_m[xyz] * (t_eri_3[i] - rou_div_t2 * t_eri_4[i]);
      tmp_v += t;
    }

    // Optimization: operator strength reduction for 'ind'.
    //int ind = calc_ind(i1, i2, i3, i4, num2, num3, num4);
    ret_eri[ind]=tmp_v;

    // Optimization: operator strength reduction for 'ind'.
    ind++;
  }
}

void PInt2e_vhrr_dp::grad_init(int tn1, int tn2, int tn3, int tn4)
{
  // First, we determine which entries (in the DP table) to be filled
  // by mimicing recursion (the results is stored in "eri_dp_flags").

  for(int i2=0;i2<=tn1+tn2+1;i2++){
    for(int i4=0;i4<=tn3+tn4+1;i4++){
      if(i2+i4<=tn1+tn2+tn3+tn4+1){ 
        for(int m=(tn1+tn2+tn3+tn4-i2-i4)+1;m>=0;m--){
          eri_dp_hrr_flags[0][i2][0][i4][m]=false;
          eri_dp_vrr_flags[i2][i4][m]=false;
        }
      }
    }
  }
  for(int i1=0;i1<=tn1+1;i1++){
    for(int i2=0;i2<=tn2+tn1-i1+1;i2++){
      for(int i3=0;i3<=tn3+1;i3++){
        for(int i4=0;i4<=tn4+tn3-i3+1;i4++){
          if(i1+i2+i3+i4<=tn1+tn2+tn3+tn4+1){
            if(i1!=0 || i3!=0){
              eri_dp_hrr_flags[i1][i2][i3][i4][0]=false;
              eri_dp_hrr_flags[i1][i2][i3][i4][1]=false;
            }
          }
        }
      }
    }
  }
  ERI_dp_mark_flags(tn1+1, tn2, tn3, tn4, 0);
  ERI_dp_mark_flags(tn1, tn2+1, tn3, tn4, 0);
  ERI_dp_mark_flags(tn1, tn2, tn3+1, tn4, 0);
  ERI_dp_mark_flags(tn1, tn2, tn3, tn4+1, 0);
  if(tn1>=1) ERI_dp_mark_flags(tn1-1, tn2, tn3, tn4,0);
  if(tn2>=1) ERI_dp_mark_flags(tn1, tn2-1, tn3, tn4,0);
  if(tn3>=1) ERI_dp_mark_flags(tn1, tn2, tn3-1, tn4,0);
  if(tn4>=1) ERI_dp_mark_flags(tn1, tn2, tn3, tn4-1,0);


  // vrr-loop
  for(int i2=0;i2<=tn1+tn2+1;i2++){
    for(int i4=0;i4<=tn3+tn4+1;i4++){
      if(i2+i4<=tn1+tn2+tn3+tn4+1){ 
        for(int m=(tn1+tn2+tn3+tn4-i2-i4)+1;m>=0;m--){
          // We skip the unnecessary entries by examing the "eri_dp_flags" table.
          if (eri_dp_vrr_flags[i2][i4][m]) {
            double *tmp_eri;
            if(i2<=max_tn_array && i4<=max_tn_array){
              tmp_eri=eri_array[0][i2][0][i4][m];
            }else{
              tmp_eri = new double [get_num(i2)*get_num(i4)];
            }
            eri_dp[0][i2][0][i4][m]=tmp_eri;
          }
        }
      }
    }
  }

  // hrr-loop
  for(int i1=0;i1<=tn1+1;i1++){
    for(int i2=0;i2<=tn2+tn1-i1+1;i2++){
      for(int i3=0;i3<=tn3+1;i3++){
        for(int i4=0;i4<=tn4+tn3-i3+1;i4++){
          if(i1+i2+i3+i4<=tn1+tn2+tn3+tn4+1){
            if(i1!=0 || i3!=0){
              for(int m=0;m<=1;m++){
                if (eri_dp_hrr_flags[i1][i2][i3][i4][m]) {
                  double *tmp_eri;
                  if(i1<=max_tn_array && i2<=max_tn_array && i3<=max_tn_array && i4<=max_tn_array){
                    tmp_eri=eri_array[i1][i2][i3][i4][m];
                  }else{
                    tmp_eri = new double [get_num(i1)*get_num(i2)*get_num(i3)*get_num(i4)];
                  }
                  eri_dp[i1][i2][i3][i4][m]=tmp_eri;
                }
              }
            }
          }
        }
      }
    }
  }

}


void PInt2e_vhrr_dp::grad_finalize(int tn1, int tn2, int tn3, int tn4)
{
  for(int i2=0;i2<=tn1+tn2;i2++){
    for(int i4=0;i4<=tn3+tn4;i4++){
      if(i2+i4<=tn1+tn2+tn3+tn4+1){ 
        for(int m=(tn1+tn2+tn3+tn4-i2-i4)+1;m>=0;m--){
          // We skip the unnecessary entries by examing the "eri_dp_flags" table.
          if (eri_dp_vrr_flags[i2][i4][m]) {
            if(i2<=max_tn_array && i4<=max_tn_array){
            }else{
              delete [] eri_dp[0][i2][0][i4][m];
              eri_dp[0][i2][0][i4][m] = 0;
            }
          }
        }
      }
    }
  }

  for(int i1=0;i1<=tn1;i1++){
    for(int i2=0;i2<=tn2+tn1-i1;i2++){
      for(int i3=0;i3<=tn3;i3++){
        for(int i4=0;i4<=tn4+tn3-i3;i4++){
          if(i1+i2+i3+i4<=tn1+tn2+tn3+tn4+1){
            if(i1!=0 || i3!=0){
              for(int m=0;m<=1;m++){
                // We skip the unnecessary entries by examing the "eri_dp_flags" table.
                if (eri_dp_hrr_flags[i1][i2][i3][i4][m]) {
                  if(i1<=max_tn_array && i2<=max_tn_array && i3<=max_tn_array && i4<=max_tn_array){
                  }else{
                    delete [] eri_dp[i1][i2][i3][i4][m];
                    eri_dp[i1][i2][i3][i4][m] = 0;
                  }
                }
              }
            }
          }
        }
      }
    }
  }



} 


//template <typename double>
void PInt2e_vhrr_dp::grad_ERI_dp(std::vector<double> &ret_grad,int tn1,int tn2,int tn3,int tn4,
                                 const std::vector<double> &dI_a,const std::vector<double> &dI_b,
                                 const std::vector<double> &dI_c,const std::vector<double> &dI_d){

  int num1=get_num(tn1);
  int num2=get_num(tn2);
  int num3=get_num(tn3);
  int num4=get_num(tn4);
  ret_grad.reserve(num1*num2*num3*num4*12);
  ret_grad.clear();

  // vrr-loop
  for(int i2=0;i2<=tn1+tn2+1;i2++){
    for(int i4=0;i4<=tn3+tn4+1;i4++){
      if(i2+i4<=tn1+tn2+tn3+tn4+1){ 
        for(int m=(tn1+tn2+tn3+tn4-i2-i4)+1;m>=0;m--){
          // We skip the unnecessary entries by examing the "eri_dp_flags" table.
        //  if (eri_dp_hrr_flags[0][i2][0][i4][m]) {
          if (eri_dp_vrr_flags[i2][i4][m]) {
              ERI_vrr_dp_sub(eri_dp[0][i2][0][i4][m], i2, i4, m);
          }
        }
      }
    }
  }

  // hrr-loop
  for(int i1=0;i1<=tn1+1;i1++){
    for(int i2=0;i2<=tn2+tn1-i1+1;i2++){
      for(int i3=0;i3<=tn3+1;i3++){
        for(int i4=0;i4<=tn4+tn3-i3+1;i4++){
          if(i1+i2+i3+i4<=tn1+tn2+tn3+tn4+1){
            if(i1!=0 || i3!=0){
              for(int m=0;m<=1;m++){
                // We skip the unnecessary entries by examing the "eri_dp_flags" table.
                if (eri_dp_hrr_flags[i1][i2][i3][i4][m]) {
                  ERI_hrr_dp_sub(eri_dp[i1][i2][i3][i4][m], i1, i2, i3, i4, m);
                }
              }
            }
          }
        }
      }
    }
  }


  int num1_p=get_num(tn1+1);
  int num2_p=get_num(tn2+1);
  int num3_p=get_num(tn3+1);
  int num4_p=get_num(tn4+1);
 
  for(int i1=0;i1<num1;i1++){
    for(int i2=0;i2<num2;i2++){
      for(int i3=0;i3<num3;i3++){
        for(int i4=0;i4<num4;i4++){
          int ind=i1*num2*num3*num4+i2*num3*num4+i3*num4+i4;
          int n1[3],n2[3],n3[3],n4[3];
          set_n1234(n1,n2,n3,n4,i1,i2,i3,i4,tn1,tn2,tn3,tn4);
          for(int xyz=0;xyz<3;xyz++){
            int n1_p[3],n2_p[3],n3_p[3],n4_p[3];
            int n1_m[3],n2_m[3],n3_m[3],n4_m[3];
            set_n1234_p(n1_p,n2_p,n3_p,n4_p,n1,n2,n3,n4,xyz);
            set_n1234_m(n1_m,n2_m,n3_m,n4_m,n1,n2,n3,n4,xyz);
            int i1_p=get_no(n1_p);
            int i2_p=get_no(n2_p);
            int i3_p=get_no(n3_p);
            int i4_p=get_no(n4_p);
            int ind1_p=i1_p*num2*num3*num4   +i2  *num3*num4 +i3*num4   +i4;
            int ind2_p=i1  *num2_p*num3*num4 +i2_p*num3*num4 +i3*num4   +i4;
            int ind3_p=i1  *num2*num3_p*num4 +i2*num3_p*num4 +i3_p*num4 +i4;
            int ind4_p=i1  *num2*num3*num4_p +i2*num3*num4_p +i3*num4_p +i4_p;
            ret_grad[ind*12+xyz*4+0]=2.0*g1*eri_dp[tn1+1][tn2][tn3][tn4][0][ind1_p];
            ret_grad[ind*12+xyz*4+1]=2.0*g2*eri_dp[tn1][tn2+1][tn3][tn4][0][ind2_p];
            ret_grad[ind*12+xyz*4+2]=2.0*g3*eri_dp[tn1][tn2][tn3+1][tn4][0][ind3_p];
            ret_grad[ind*12+xyz*4+3]=2.0*g4*eri_dp[tn1][tn2][tn3][tn4+1][0][ind4_p];

            if(n1_m[xyz]>=0){
              int i1_m=get_no(n1_m);
              int ind1_m=i1_m*num2*num3*num4   +i2  *num3*num4 +i3*num4   +i4;
              ret_grad[ind*12+xyz*4+0]-=n1[xyz]*eri_dp[tn1-1][tn2][tn3][tn4][0][ind1_m];
            }
            if(n2_m[xyz]>=0){
              int i2_m=get_no(n2_m);
              int num2_m=get_num(tn2-1);
              int ind2_m=i1  *num2_m*num3*num4 +i2_m*num3*num4 +i3*num4   +i4;
              ret_grad[ind*12+xyz*4+1]-=n2[xyz]*eri_dp[tn1][tn2-1][tn3][tn4][0][ind2_m];
            }
            if(n3_m[xyz]>=0){
              int i3_m=get_no(n3_m);
              int num3_m=get_num(tn3-1);
              int ind3_m=i1  *num2*num3_m*num4 +i2*num3_m*num4 +i3_m*num4   +i4;
              ret_grad[ind*12+xyz*4+2]-=n3[xyz]*eri_dp[tn1][tn2][tn3-1][tn4][0][ind3_m];
            }

            if(n4_m[xyz]>=0){
              int i4_m=get_no(n4_m);
              int num4_m=get_num(tn4-1);
              int ind4_m=i1  *num2*num3*num4_m +i2*num3*num4_m +i3*num4_m  +i4_m;
              ret_grad[ind*12+xyz*4+3]-=n4[xyz]*eri_dp[tn1][tn2][tn3][tn4-1][0][ind4_m];
            }

            ret_grad[ind*12+xyz*4+0]*=dI_a[i1]*dI_b[i2]*dI_c[i3]*dI_d[i4];
            ret_grad[ind*12+xyz*4+1]*=dI_a[i1]*dI_b[i2]*dI_c[i3]*dI_d[i4];
            ret_grad[ind*12+xyz*4+2]*=dI_a[i1]*dI_b[i2]*dI_c[i3]*dI_d[i4];
            ret_grad[ind*12+xyz*4+3]*=dI_a[i1]*dI_b[i2]*dI_c[i3]*dI_d[i4];

          }
        }
      }
    }
  }


}




//template <typename double>
int PInt2e_vhrr_dp::debug_driver_vhrr_dp(int max_ijkl){


  std::cout<<" ========== debug_driver_vhrr_dp of PInt2e_vhrr_dp ========== "<<std::endl;

  std::vector<double> Ri(3),Rj(3),Rk(3),Rl(3);
  Ri[0]=0.3;      Ri[1]=0.4;      Ri[2]=0.1;
  Rj[0]=-0.1;     Rj[1]=0.2;      Rj[2]=-0.3;
  Rk[0]=0.5;      Rk[1]=-0.4;     Rk[2]=0.2;
  Rl[0]=0.3;      Rl[1]=-0.2;     Rl[2]=-0.6;

  double gi=0.7;
  double gj=0.6;
  double gk=0.8;
  double gl=0.2;

  PInt2e_os_dp   pint2e_os;
  PInt2e_vhrr_dp pint2e_vhrr;

  pint2e_os.set_gR_12(gi,Ri,gj,Rj);
  pint2e_os.set_gR_34(gk,Rk,gl,Rl);

  pint2e_vhrr.set_gR_12(gi,Ri,gj,Rj);
  pint2e_vhrr.set_gR_34(gk,Rk,gl,Rl);

  int     mode_erfc=0;
  double  omega_erfc=0.7;
  std::vector<double> dI_A(100),dI_B(100),dI_C(100),dI_D(100);
  std::vector<double> debug_eri1(100000),debug_eri2(100000);

  for(int i=0;i<=max_ijkl;i++){
    for(int j=0;j<=max_ijkl;j++){
      for(int k=0;k<=max_ijkl;k++){
        for(int l=0;l<=max_ijkl;l++){
          //int t_ni=0,t_nj=0,t_nk=0,t_nl=0;
          std::vector<int> ni,nj,nk,nl;
          int num_ia=pint2e_os.get_num(i);
          int num_ib=pint2e_os.get_num(j);
          int num_ic=pint2e_os.get_num(k);
          int num_id=pint2e_os.get_num(l);
          // dI_A
          for(int ia=0;ia<num_ia;ia++){
            ni=pint2e_os.get_no_to_n(i,ia);
            dI_A[ia]=PInt2e_base<0>::cal_I(gi,ni);
          }
          // dI_B
          for(int ib=0;ib<num_ib;ib++){
            nj=pint2e_os.get_no_to_n(j,ib);
            dI_B[ib]=PInt2e_base<0>::cal_I(gj,nj);
          }
          // dI_C
          for(int ic=0;ic<num_ic;ic++){
            nk=pint2e_os.get_no_to_n(k,ic);
            dI_C[ic]=PInt2e_base<0>::cal_I(gk,nk);
          }
          // dI_D
          for(int id=0;id<num_id;id++){
            nl=pint2e_os.get_no_to_n(l,id);
            dI_D[id]=PInt2e_base<0>::cal_I(gl,nl);
          }
  
          int tn=i+j+k+l;

          pint2e_os.set_eri_ssss(tn,mode_erfc,omega_erfc);
          pint2e_vhrr.set_eri_ssss(tn,mode_erfc,omega_erfc);
 
//	  pint2e_os.set_flags(i, j, k, l);
//        pint2e_vhrr.set_flags(i, j, k, l);

	  pint2e_os.ERI_init(i, j, k, l);
          pint2e_os.ERI(debug_eri1,i,j,k,l,dI_A,dI_B,dI_C,dI_D);
          pint2e_os.ERI_finalize(i, j, k, l);

	  pint2e_vhrr.ERI_init(i, j, k, l);
          pint2e_vhrr.ERI(debug_eri2,i,j,k,l,dI_A,dI_B,dI_C,dI_D);
	  pint2e_vhrr.ERI_finalize(i, j, k, l);


          int cc=0;
          for(int ia=0;ia<num_ia;ia++){
            for(int ib=0;ib<num_ib;ib++){
              for(int ic=0;ic<num_ic;ic++){
                for(int id=0;id<num_id;id++){
                  if(fabs(debug_eri1[cc]-debug_eri2[cc])>1.0e-10){
                    cout<<" ****** ERROR  cc="<<cc<<" "<<endl;
                    cout<<"   ia="<<ia<<" ni "<<ni[0]<<" "<<ni[1]<<" "<<ni[2]<<endl;
                    cout<<"   ib="<<ib<<" nj "<<nj[0]<<" "<<nj[1]<<" "<<nj[2]<<endl;
                    cout<<"   ic="<<ic<<" nk "<<nk[0]<<" "<<nk[1]<<" "<<nk[2]<<endl;
                    cout<<"   id="<<id<<" nl "<<nl[0]<<" "<<nl[1]<<" "<<nl[2]<<endl;
                    cout<<"   debug_eri1   "<<debug_eri1[cc]<<endl;
                    cout<<"   debug_eri2   "<<debug_eri2[cc]<<endl;
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



//template <typename double>
int PInt2e_vhrr_dp::debug_driver_grad(int max_ijkl){
  int ret=0;
  std::cout<<" ========== debug_driver_vhrr_dp_grad of PInt2e_vhrr_dp ========== "<<std::endl;

  std::vector<double> Ri(3),Rj(3),Rk(3),Rl(3);
  Ri[0]=0.3;      Ri[1]=0.4;      Ri[2]=0.1;
  Rj[0]=-0.1;     Rj[1]=0.2;      Rj[2]=-0.3;
  Rk[0]=0.5;      Rk[1]=-0.4;     Rk[2]=0.2;
  Rl[0]=0.3;      Rl[1]=-0.2;     Rl[2]=-0.6;

  double gi=0.7;
  double gj=0.6;
  double gk=0.8;
  double gl=0.2;

  PInt2e_vhrr_dp pint2e;

  pint2e.set_gR_12(gi,Ri,gj,Rj);
  pint2e.set_gR_34(gk,Rk,gl,Rl);

//  cout<<" ----- pint2e ----- "<<endl;
//  pint2e.show_state();

  int     mode_erfc=0;
  double  omega_erfc=0.7;
  std::vector<double> dI_A(100),dI_B(100),dI_C(100),dI_D(100);
  std::vector<double> debug_grad(200000);

  //int num_ia,num_ib,num_ic,num_id;

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
  
          int tn=i+j+k+l+1;
          pint2e.set_eri_ssss(tn+1,mode_erfc,omega_erfc);
          pint2e.grad_init(i, j, k, l);
          pint2e.grad_ERI_dp(debug_grad,i,j,k,l,dI_A,dI_B,dI_C,dI_D);
          pint2e.grad_finalize(i, j, k, l);
                                       
          for(int ia=0;ia<num_ia;ia++){
            for(int ib=0;ib<num_ib;ib++){
              for(int ic=0;ic<num_ic;ic++){
                for(int id=0;id<num_id;id++){
                  ni=pint2e.get_no_to_n(i,ia);
                  nj=pint2e.get_no_to_n(j,ib);
                  nk=pint2e.get_no_to_n(k,ic);
                  nl=pint2e.get_no_to_n(l,id);
                  
                  int cc=ia*num_ib*num_ic*num_id+ib*num_ic*num_id+ic*num_id+id;

                  for(int xyz=0;xyz<3;xyz++){ 
                    std::vector<int> ni_p(3,0),nj_p(3,0),nk_p(3,0),nl_p(3,0);
                    std::vector<int> ni_m(3,0),nj_m(3,0),nk_m(3,0),nl_m(3,0);
                    pint2e.set_n1234_p(&ni_p[0],&nj_p[0],&nk_p[0],&nl_p[0],&ni[0],&nj[0],&nk[0],&nl[0],xyz);
                    pint2e.set_n1234_m(&ni_m[0],&nj_m[0],&nk_m[0],&nl_m[0],&ni[0],&nj[0],&nk[0],&nl[0],xyz);
                    double v_comp_a=2.0*gi*pint2e.ERI_m_simple(&ni_p[0],&nj[0],&nk[0],&nl[0],0);
                    double v_comp_b=2.0*gj*pint2e.ERI_m_simple(&ni[0],&nj_p[0],&nk[0],&nl[0],0);
                    double v_comp_c=2.0*gk*pint2e.ERI_m_simple(&ni[0],&nj[0],&nk_p[0],&nl[0],0);
                    double v_comp_d=2.0*gl*pint2e.ERI_m_simple(&ni[0],&nj[0],&nk[0],&nl_p[0],0);
            

                    if(ni_m[xyz]>=0){
                      v_comp_a+=-1.0*ni[xyz]*pint2e.ERI_m_simple(&ni_m[0],&nj[0],&nk[0],&nl[0],0);
                    }
                     
                    if(nj_m[xyz]>=0){
                      v_comp_b+=-1.0*nj[xyz]*pint2e.ERI_m_simple(&ni[0],&nj_m[0],&nk[0],&nl[0],0);
                    }


                    if(nk_m[xyz]>=0){
                      v_comp_c+=-1.0*nk[xyz]*pint2e.ERI_m_simple(&ni[0],&nj[0],&nk_m[0],&nl[0],0);
                    }

                    if(nl_m[xyz]>=0){
                      v_comp_d+=-1.0*nl[xyz]*pint2e.ERI_m_simple(&ni[0],&nj[0],&nk[0],&nl_m[0],0);
                    }
                    v_comp_a*=pint2e.cal_I(gi,ni)*pint2e.cal_I(gj,nj)
                             *pint2e.cal_I(gk,nk)*pint2e.cal_I(gl,nl);
                    v_comp_b*=pint2e.cal_I(gi,ni)*pint2e.cal_I(gj,nj)
                             *pint2e.cal_I(gk,nk)*pint2e.cal_I(gl,nl);
                    v_comp_c*=pint2e.cal_I(gi,ni)*pint2e.cal_I(gj,nj)
                             *pint2e.cal_I(gk,nk)*pint2e.cal_I(gl,nl);
                    v_comp_d*=pint2e.cal_I(gi,ni)*pint2e.cal_I(gj,nj)
                             *pint2e.cal_I(gk,nk)*pint2e.cal_I(gl,nl);




                    if(fabs(v_comp_a-debug_grad[cc*12+xyz*4+0])>1.0e-8 || fabs(v_comp_b-debug_grad[cc*12+xyz*4+1])>1.0e-8 ||
                       fabs(v_comp_c-debug_grad[cc*12+xyz*4+2])>1.0e-8 || fabs(v_comp_d-debug_grad[cc*12+xyz*4+3])>1.0e-8){
                      cout<<" ********** ERROR !! **********"<<endl; 
                      cout<<"  xyz="<<xyz<<" cc="<<cc<<endl;
                      cout<<"  v_comp         :  "<<v_comp_a<<" "<<v_comp_b<<" "<<v_comp_c<<" "<<v_comp_d<<endl;
                      cout<<"  debug_grad     :  "<<debug_grad[cc*12+xyz*4+0]<<" "<<debug_grad[cc*12+xyz*4+1]<<" "
                                                  <<debug_grad[cc*12+xyz*4+2]<<" "<<debug_grad[cc*12+xyz*4+3]<<endl; 
                      ret=-1;
                      return ret;
//                      exit(1);
                    }

                  }
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
