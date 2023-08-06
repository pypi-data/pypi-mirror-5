

#ifndef Util_PBC_H
#define Util_PBC_H

#include <vector>
#include <iostream>

#include <math.h>

namespace Lotus_core {

class Util_PBC {
public:


  static std::vector<int> cal_n_from_q(int q,const std::vector<int> &max_N){
    std::vector<int> ret_n(3);
    cal_n_from_q(&ret_n[0], q, static_cast<const int*>(&max_N[0])); 
    return ret_n;
  }


  static void cal_n_from_q(int *ret_n, int q, const int *max_N){
    int tmp_n[3];
    tmp_n[0]=q/((2*max_N[1]+1)*(2*max_N[2]+1));
    tmp_n[1]=(q-tmp_n[0]*((2*max_N[1]+1)*(2*max_N[2]+1)))/(2*max_N[2]+1);
    tmp_n[2]=q%(2*max_N[2]+1);
    ret_n[0]=tmp_n[0]-max_N[0];
    ret_n[1]=tmp_n[1]-max_N[1];
    ret_n[2]=tmp_n[2]-max_N[2];
  }

  // for boost-python
  static std::vector<int> cal_n_from_q_bp(int q,const std::vector<int> &max_N){
    return cal_n_from_q(q, max_N);
  }
  //


  static int get_N123(const std::vector<int> &n){
    return (2*n[0]+1)*(2*n[1]+1)*(2*n[2]+1);
  }


  static int cal_q(const std::vector<int> &n,const std::vector<int> &max_N){
    int ret_q  = (2*max_N[1]+1)*(2*max_N[2]+1)*(n[0] + max_N[0])
                              + (2*max_N[2]+1)*(n[1] + max_N[1])
                                             + (n[2] + max_N[2]); 
      return ret_q;
  }
  static int cal_q(const int *n, const int *max_N){
    int ret_q  = (2*max_N[1]+1)*(2*max_N[2]+1)*(n[0] + max_N[0])
                              + (2*max_N[2]+1)*(n[1] + max_N[1])
                                             + (n[2] + max_N[2]); 
      return ret_q;
  }

  // boost-python
  static int cal_q_bp(const std::vector<int> &n,const std::vector<int> &max_N){
    return cal_q(n, max_N);
  } 
  //


  static bool check_range(int qc,int qt,const std::vector<int> &max_Nc,const std::vector<int> &max_Nt){
    int start_nt1,stop_nt1,start_nt2,stop_nt2,start_nt3,stop_nt3;
    std::vector<int> Nc=cal_n_from_q(qc,max_Nc);
    std::vector<int> Nt=cal_n_from_q(qt,max_Nt);
    if(Nc[0]<=0){ start_nt1=-max_Nt[0];       stop_nt1=max_Nt[0]+Nc[0]; }
    else{         start_nt1=-max_Nt[0]+Nc[0]; stop_nt1=max_Nt[0];       }
    if(Nc[1]<=0){ start_nt2=-max_Nt[1];       stop_nt2=max_Nt[1]+Nc[1]; }
    else{         start_nt2=-max_Nt[1]+Nc[1]; stop_nt2=max_Nt[1];       }
    if(Nc[2]<=0){ start_nt3=-max_Nt[2];       stop_nt3=max_Nt[2]+Nc[2]; }
    else{         start_nt3=-max_Nt[2]+Nc[2]; stop_nt3=max_Nt[2];       }
    bool ret=false;
    if(start_nt1<=Nt[0] && Nt[0]<=stop_nt1 && start_nt2<=Nt[1] && Nt[1]<=stop_nt2
    && start_nt3<=Nt[2] && Nt[2]<=stop_nt3) ret=true;
    return ret;
  } 

  static bool check_range2(const std::vector<int> &nc,const std::vector<int> &max_nc){
    bool ret=true;
    if(nc[0]<max_nc[0] || nc[0]>max_nc[0] || nc[1]<max_nc[1] || nc[1]>max_nc[1] ||
       nc[2]<max_nc[2] || nc[2]>max_nc[2]) ret=false;
    return ret;
  }


  static int get_zero_q(const std::vector<int> &n){
    std::vector<int> zero(3,0);
    return cal_q(zero,n);
  }


  template <typename M_tmpl1, typename M_tmpl2>
  static double cal_DV(const std::vector<M_tmpl1> &D_PBC,const std::vector<M_tmpl2> &V_PBC,int N123_c){
    int N_cgtos=V_PBC[0].get_I();
    double ret=0.0;
    for(int q=0;q<N123_c;q++){
      for(int i=0;i<N_cgtos;i++){
        for(int j=0;j<N_cgtos;j++){
          ret  +=D_PBC[q].get_value(i,j)*V_PBC[q].get_value(i,j);
        }
      }
    }
    return ret;
  }


  template <typename M_tmpl1, typename M_tmpl2>
  static double cal_DV(const std::vector<M_tmpl1*> &D_PBC,const std::vector<M_tmpl2*> &V_PBC,int N123_c){
    int N_cgtos=V_PBC[0]->get_I();
    double ret=0.0;
    for(int q=0;q<N123_c;q++){
      for(int i=0;i<N_cgtos;i++){
        for(int j=0;j<N_cgtos;j++){
          ret  +=D_PBC[q]->get_value(i,j)*V_PBC[q]->get_value(i,j);
        }
      }
    }
    return ret;
  }

  // for boost-python
  template <typename M_tmpl1, typename M_tmpl2>
  static double cal_DV_bp1(const std::vector<M_tmpl1> &D_PBC,const std::vector<M_tmpl2> &V_PBC,int N123_c){
    return cal_DV(D_PBC, V_PBC, N123_c);
  }
  template <typename M_tmpl1, typename M_tmpl2>
  static double cal_DV_bp2(const std::vector<M_tmpl1*> &D_PBC,const std::vector<M_tmpl2*> &V_PBC,int N123_c){
    return cal_DV_bp2(D_PBC, V_PBC, N123_c);
  }
  //

  template <typename M_tmpl>
  static void get_T_matrix(M_tmpl &T, M_tmpl &T_rev,const std::vector<double> &T123){
    // 
    // set transform matrix
    double T1[3],T2[3],T3[3];
    T1[0]=T123[0*3+0]; T1[1]=T123[0*3+1]; T1[2]=T123[0*3+2];
    T2[0]=T123[1*3+0]; T2[1]=T123[1*3+1]; T2[2]=T123[1*3+2];
    T3[0]=T123[2*3+0]; T3[1]=T123[2*3+1]; T3[2]=T123[2*3+2];
    double lc_1,lc_2,lc_3;
    lc_1 = sqrt(T1[0]*T1[0]+T1[1]*T1[1]+T1[2]*T1[2]);
    lc_2 = sqrt(T2[0]*T2[0]+T2[1]*T2[1]+T2[2]*T2[2]);
    lc_3 = sqrt(T3[0]*T3[0]+T3[1]*T3[1]+T3[2]*T3[2]);
    double Tu[3],Tv[3],Tw[3];
    Tu[0]=T1[0]/lc_1; Tu[1]=T1[1]/lc_1; Tu[2]=T1[2]/lc_1;
    Tv[0]=T2[0]/lc_2; Tv[1]=T2[1]/lc_2; Tv[2]=T2[2]/lc_2;
    Tw[0]=T3[0]/lc_3; Tw[1]=T3[1]/lc_3; Tw[2]=T3[2]/lc_3;
 
    T_rev.set_value(0,0,Tu[0]);  T_rev.set_value(0,1,Tv[0]);  T_rev.set_value(0,2,Tw[0]);
    T_rev.set_value(1,0,Tu[1]);  T_rev.set_value(1,1,Tv[1]);  T_rev.set_value(1,2,Tw[1]);
    T_rev.set_value(2,0,Tu[2]);  T_rev.set_value(2,1,Tv[2]);  T_rev.set_value(2,2,Tw[2]);
    T=T_rev;
    mat_inverse(T);
  }

  static double cal_volume(const std::vector<double> &T123){
    std::vector<int> nc(3, 1);
    return cal_volume(T123, nc);
  }

  static inline double cal_volume(const std::vector<double> &T123, const std::vector<int> &max_Nc);

  // for boost-python
  static double cal_volume_bp1(const std::vector<double> &T123){
    return cal_volume(T123);
  }
  static double cal_volume_bp2(const std::vector<double> &T123, const std::vector<int> &max_Nc){
    return cal_volume(T123, max_Nc);
  }
  //

  static inline std::vector<double> cal_reciprocal_lattice_vector(const std::vector<double> &T123);

  static inline std::vector<double> get_kxyz_from_k_lc(const std::vector<double> &in_k_lc,
                                                       const std::vector<double> &T123);

  template <typename M_tmpl>
  static inline std::vector<double> get_k_lc_from_kxyz(const std::vector<double> &in_kxyz, 
                                                       const std::vector<double> &T123);

  static inline double cal_zincblende_a(const std::vector<double> &T123);

  static inline double cal_graphite_a(const std::vector<int> &max_Nc, const std::vector<double> &T123);
                                
};



class CTRL_PBC{
  std::vector<int> max_Nc;
  std::vector<int> max_Nt;
  std::vector<double> T123;
  std::vector<int> Nk123;
  double beta_Gaussian_broad;

public:
  CTRL_PBC() : max_Nc(3,0), max_Nt(3,0), Nk123(3, 1) { 
    T123.reserve(9);
    T123[0]=1.0;  T123[1]=0.0;  T123[2]=0.0;
    T123[3]=0.0;  T123[4]=1.0;  T123[5]=0.0;
    T123[6]=0.0;  T123[7]=0.0;  T123[8]=1.0;
    beta_Gaussian_broad=3000;}

  CTRL_PBC(const CTRL_PBC &copy){
    if((void*)this==(void*)&copy) return;
    max_Nc              = copy.get_max_Nc();
    max_Nt              = copy.get_max_Nt();
    T123                = copy.get_T123();
    Nk123               = copy.get_Nk123();
    beta_Gaussian_broad = copy.get_beta_Gaussian_broad();
  }

  CTRL_PBC &operator=(const CTRL_PBC &in){
    if((void*)this==(void*)&in) return *this;
    this->max_Nc = in.get_max_Nc();
    this->max_Nt = in.get_max_Nt();
    this->T123   = in.get_T123();
    this->Nk123  = in.get_Nk123();
    this->beta_Gaussian_broad = in.get_beta_Gaussian_broad();
    return *this;
  }
  CTRL_PBC &operator=(CTRL_PBC &in){
    if((void*)this==(void*)&in) return *this;
    this->max_Nc = in.get_max_Nc();
    this->max_Nt = in.get_max_Nt();
    this->T123   = in.get_T123();
    this->Nk123  = in.get_Nk123();
    this->beta_Gaussian_broad = in.get_beta_Gaussian_broad();
    return *this;
  }
  

  void show() const {
    std::cout<<"   max_Nc "<<max_Nc[0]<<" "<<max_Nc[1]<<" "<<max_Nc[2]<<std::endl;
    std::cout<<"   max_Nt "<<max_Nt[0]<<" "<<max_Nt[1]<<" "<<max_Nt[2]<<std::endl;
    std::cout<<"   T1     "<<T123[0]<<"  "<<T123[1]<<"  "<<T123[2]<<std::endl;
    std::cout<<"   T2     "<<T123[3]<<"  "<<T123[4]<<"  "<<T123[5]<<std::endl;
    std::cout<<"   T3     "<<T123[6]<<"  "<<T123[7]<<"  "<<T123[8]<<std::endl;
    std::cout<<"   Nk123  "<<Nk123[0]<<"  "<<Nk123[1]<<"  "<<Nk123[2]<<std::endl;
    std::cout<<"   beta_Gaussian_broad "<<beta_Gaussian_broad<<std::endl;
  }    
  void set_T123(const std::vector<double> &in){
    T123.clear();
    for(int i=0;i<9;i++) T123.push_back(in[i]);
  }

  void set_max_Nc(const std::vector<int> &in){
    max_Nc.clear();
    max_Nt.clear();
    for(int i=0;i<3;i++){
      max_Nc.push_back(in[i]);
      max_Nt.push_back(in[i]);
    }
  }
  void set_max_Nt(const std::vector<int> &in){
    max_Nt.clear();
    for(int i=0;i<3;i++) max_Nt.push_back(in[i]);
  }
  void set_max_Nc_and_Nt(const std::vector<int> &in_c, const std::vector<int> &in_t){
    set_max_Nc(in_c);
    set_max_Nt(in_t);
  }

  void   set_beta_Gaussian_broad(double in){ beta_Gaussian_broad=in; }
  double get_beta_Gaussian_broad() const {   return beta_Gaussian_broad; }

  std::vector<double> get_T123() const {
    std::vector<double> ret;
    for(int i=0;i<9;i++) ret.push_back(T123[i]);
    return ret;
  }

  std::vector<int> get_max_Nc() const {
    std::vector<int> ret;
    for(int i=0;i<3;i++) ret.push_back(max_Nc[i]);
    return ret; 
  }
  void get_max_Nc(int *ret_n) const {
    ret_n[0]=max_Nc[0];
    ret_n[1]=max_Nc[1];
    ret_n[2]=max_Nc[2];
  }


  std::vector<int> get_max_Nt() const {
    std::vector<int> ret;
    for(int i=0;i<3;i++) ret.push_back(max_Nt[i]);
    return ret; 
  }
  void get_max_Nt(int *ret_n) const {
    ret_n[0]=max_Nt[0];
    ret_n[1]=max_Nt[1];
    ret_n[2]=max_Nt[2];
  }

  // for boost-python
  std::vector<int> get_max_Nc_bp() const {
    return get_max_Nc();
  }
  std::vector<int> get_max_Nt_bp() const {
    return get_max_Nt();
  }
  //


  int get_N123_c() const {   return Util_PBC::get_N123(max_Nc); }
  int get_N123_t() const {   return Util_PBC::get_N123(max_Nt); }

  int get_zero_qc() const { 
    std::vector<int> n_zero(3,0);
    return Util_PBC::cal_q(n_zero,max_Nc);
  }
  int get_zero_qt() const { 
    std::vector<int> n_zero(3,0);
    return Util_PBC::cal_q(n_zero,max_Nt);
  }
  std::vector<int> get_nc_from_q(int q) const { return Util_PBC::cal_n_from_q(q,max_Nc); }
  std::vector<int> get_nt_from_q(int q) const { return Util_PBC::cal_n_from_q(q,max_Nt); }

  std::vector<double> get_R_pbc(const std::vector<double> &R,const std::vector<int> &n) const {
    std::vector<double> ret_R_pbc;
    ret_R_pbc.push_back(R[0]+n[0]*T123[0*3+0]+n[1]*T123[1*3+0]+n[2]*T123[2*3+0]);
    ret_R_pbc.push_back(R[1]+n[0]*T123[0*3+1]+n[1]*T123[1*3+1]+n[2]*T123[2*3+1]);
    ret_R_pbc.push_back(R[2]+n[0]*T123[0*3+2]+n[1]*T123[1*3+2]+n[2]*T123[2*3+2]);
    return ret_R_pbc;
  }

  void get_R_pbc_array(double *ret_R_pbc, const double *R,const int *n) const {
    ret_R_pbc[0] = (R[0]+n[0]*T123[0*3+0]+n[1]*T123[1*3+0]+n[2]*T123[2*3+0]);
    ret_R_pbc[1] = (R[1]+n[0]*T123[0*3+1]+n[1]*T123[1*3+1]+n[2]*T123[2*3+1]);
    ret_R_pbc[2] = (R[2]+n[0]*T123[0*3+2]+n[1]*T123[1*3+2]+n[2]*T123[2*3+2]);
  }
  

  void set_Nk123(const std::vector<int> &in){
    if(in[0]<=1){
      Nk123[0]=1;
    }else{
      if(in[0]%2==0) Nk123[0]=in[0];
      else           Nk123[0]=in[0]+1;
    }
    if(in[1]<=1){
      Nk123[1]=1;
    }else{
      if(in[1]%2==0) Nk123[1]=in[1];
      else           Nk123[1]=in[1]+1;
    }
    if(in[2]<=1){
      Nk123[2]=1;
    }else{
      if(in[2]%2==0) Nk123[2]=in[2];
      else           Nk123[2]=in[2]+1;
    }
  }

  std::vector<int> get_Nk123() const { 
    std::vector<int> ret(3);
    ret[0]=Nk123[0]; 
    ret[1]=Nk123[1]; 
    ret[2]=Nk123[2]; 
    return ret;
  }

  int get_Nk_pbc() const {  return Nk123[0]*Nk123[1]*Nk123[2]; }

  std::vector<double> get_dk() const {
    // dk
    int Nk=get_Nk_pbc();
    std::vector<double> ret_dk(Nk);
    for(int k=0;k<Nk;k++) ret_dk[k]=1.0/((double)Nk);
    return ret_dk;
  }

  double get_nth_dk(int nth) const { 
    int Nk=get_Nk_pbc();
    double ret=1.0/Nk;
    return ret; 
  }

  inline std::vector<double> get_k_lc() const;
  inline std::vector<double> get_nth_k_lc(int nth) const;


  double cal_volume() const {  return Util_PBC::cal_volume(T123, max_Nc); }

  std::vector<double> get_reciprocal_lattice_vector() const {
    return Util_PBC::cal_reciprocal_lattice_vector(T123);
  }

  std::vector<double> get_kxyz_from_k_lc(const std::vector<double> &in_k_lc) const {
    return Util_PBC::get_kxyz_from_k_lc(in_k_lc, T123);
  }

  template <typename M_tmpl>
  std::vector<double> get_k_lc_from_kxyz(const std::vector<double> &in_kxyz) const {
    return Util_PBC::get_k_lc_from_kxyz<M_tmpl>(in_kxyz, T123);
  }


  double cal_zincblende_a() const { return Util_PBC::cal_zincblende_a(T123); }
  double cal_graphite_a() const {   return Util_PBC::cal_graphite_a(max_Nc, T123); }

  double cal_1D_lattice_constant() const {
    double T1[3],T2[3],T3[3];
    T1[0]=T123[0*3+0];  T1[1]=T123[0*3+1];  T1[2]=T123[0*3+2];
    T2[0]=T123[1*3+0];  T2[1]=T123[1*3+1];  T2[2]=T123[1*3+2];
    T3[0]=T123[2*3+0];  T3[1]=T123[2*3+1];  T3[2]=T123[2*3+2];
    if(max_Nc[0]!=0) return sqrt( T1[0]*T1[0] + T1[1]*T1[1] + T1[2]*T1[2]);
    if(max_Nc[1]!=0) return sqrt( T2[0]*T2[0] + T2[1]*T2[1] + T2[2]*T2[2]);
    if(max_Nc[2]!=0) return sqrt( T3[0]*T3[0] + T3[1]*T3[1] + T3[2]*T3[2]);
    return 0.0; // dummy
  } 


};


}  // end of namespace "Lotus_core"


#include "detail/Util_PBC_detail.hpp"

#endif // include-guard
