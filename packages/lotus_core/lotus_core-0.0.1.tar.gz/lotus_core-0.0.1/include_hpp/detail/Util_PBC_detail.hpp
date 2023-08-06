

#ifndef UTIL_PBC_DETAIL
#define UTIL_PBC_DETAIL

namespace Lotus_core {


double Util_PBC::cal_volume(const std::vector<double> &T123, const std::vector<int> &max_Nc)
{
  if(max_Nc[0]==0 || max_Nc[1]==0 || max_Nc[2]==0) return 0.0;

  double T1[3],T2[3],T3[3];
  T1[0]=T123[0*3+0];  T1[1]=T123[0*3+1];  T1[2]=T123[0*3+2];
  T2[0]=T123[1*3+0];  T2[1]=T123[1*3+1];  T2[2]=T123[1*3+2];
  T3[0]=T123[2*3+0];  T3[1]=T123[2*3+1];  T3[2]=T123[2*3+2];

  double e[3];
  e[0]=(T2[1]*T3[2]-T3[1]*T2[2]);
  e[1]=(T2[2]*T3[0]-T3[2]*T2[0]);
  e[2]=(T2[0]*T3[1]-T3[0]*T2[1]);

  double volume=T1[0]*e[0]+T1[1]*e[1]+T1[2]*e[2];

  return volume;
}



std::vector<double> Util_PBC::cal_reciprocal_lattice_vector(const std::vector<double> &T123)
{
  std::vector<double> ret_G123(9);

  double V=cal_volume(T123);
  double T1[3],T2[3],T3[3];
  T1[0]=T123[0*3+0];  T1[1]=T123[0*3+1];  T1[2]=T123[0*3+2];
  T2[0]=T123[1*3+0];  T2[1]=T123[1*3+1];  T2[2]=T123[1*3+2];
  T3[0]=T123[2*3+0];  T3[1]=T123[2*3+1];  T3[2]=T123[2*3+2];

  double G1[3],G2[3],G3[3];
  G1[0]=(2.0*M_PI/V)*(T2[1]*T3[2]-T2[2]*T3[1]);
  G1[1]=(2.0*M_PI/V)*(T2[2]*T3[0]-T2[0]*T3[2]);
  G1[2]=(2.0*M_PI/V)*(T2[0]*T3[1]-T2[1]*T3[0]);
  G2[0]=(2.0*M_PI/V)*(T3[1]*T1[2]-T3[2]*T1[1]);
  G2[1]=(2.0*M_PI/V)*(T3[2]*T1[0]-T3[0]*T1[2]);
  G2[2]=(2.0*M_PI/V)*(T3[0]*T1[1]-T3[1]*T1[0]);
  G3[0]=(2.0*M_PI/V)*(T1[1]*T2[2]-T1[2]*T2[1]);
  G3[1]=(2.0*M_PI/V)*(T1[2]*T2[0]-T1[0]*T2[2]);
  G3[2]=(2.0*M_PI/V)*(T1[0]*T2[1]-T1[1]*T2[0]);

  ret_G123[0*3+0]=G1[0];  ret_G123[0*3+1]=G1[1];  ret_G123[0*3+2]=G1[2];
  ret_G123[1*3+0]=G2[0];  ret_G123[1*3+1]=G2[1];  ret_G123[1*3+2]=G2[2];
  ret_G123[2*3+0]=G3[0];  ret_G123[2*3+1]=G3[1];  ret_G123[2*3+2]=G3[2];

  return ret_G123;
}




std::vector<double> Util_PBC::get_kxyz_from_k_lc(const std::vector<double> &in_k_lc,
                                                 const std::vector<double> &T123)
{
  std::vector<double> ret_kxyz(3);
  
  double G1[3],G2[3],G3[3];
  std::vector<double> G123 = cal_reciprocal_lattice_vector(T123);
  G1[0]=G123[0*3+0];  G1[1]=G123[0*3+1];  G1[2]=G123[0*3+2]; 
  G2[0]=G123[1*3+0];  G2[1]=G123[1*3+1];  G2[2]=G123[1*3+2]; 
  G3[0]=G123[2*3+0];  G3[1]=G123[2*3+1];  G3[2]=G123[2*3+2]; 

  double a00,a01,a02,a10,a11,a12,a20,a21,a22;
  a00=G1[0];  a01=G2[0];  a02=G3[0];
  a10=G1[1];  a11=G2[1];  a12=G3[1];
  a20=G1[2];  a21=G2[2];  a22=G3[2];
  ret_kxyz[0] = 2.0*M_PI*(a00*in_k_lc[0] + a01*in_k_lc[1] + a02*in_k_lc[2]);
  ret_kxyz[1] = 2.0*M_PI*(a10*in_k_lc[0] + a11*in_k_lc[1] + a12*in_k_lc[2]);
  ret_kxyz[2] = 2.0*M_PI*(a20*in_k_lc[0] + a21*in_k_lc[1] + a22*in_k_lc[2]);

  return ret_kxyz;
}

template <typename M_tmpl>
std::vector<double> Util_PBC::get_k_lc_from_kxyz(
       const std::vector<double> &in_kxyz, const std::vector<double> &T123)
{
  std::vector<double> ret_k_lc(3);  

  double G1[3],G2[3],G3[3];
  std::vector<double> G123 = cal_reciprocal_lattice_vector(T123);
  G1[0]=G123[0*3+0];  G1[1]=G123[0*3+1];  G1[2]=G123[0*3+2]; 
  G2[0]=G123[1*3+0];  G2[1]=G123[1*3+1];  G2[2]=G123[1*3+2]; 
  G3[0]=G123[2*3+0];  G3[1]=G123[2*3+1];  G3[2]=G123[2*3+2]; 

  M_tmpl A(3,3);
  A.set_value(0,0,G1[0]);  A.set_value(0,1,G2[0]);  A.set_value(0,2,G3[0]);
  A.set_value(1,0,G1[1]);  A.set_value(1,1,G2[1]);  A.set_value(1,2,G3[1]);
  A.set_value(2,0,G1[2]);  A.set_value(2,1,G2[2]);  A.set_value(2,2,G3[2]);
  mat_inverse(A);
  double a00,a01,a02,a10,a11,a12,a20,a21,a22;
  a00=A.get_value(0,0);  a01=A.get_value(0,1);  a02=A.get_value(0,2);
  a10=A.get_value(1,0);  a11=A.get_value(1,1);  a12=A.get_value(1,2);
  a20=A.get_value(2,0);  a21=A.get_value(2,1);  a22=A.get_value(2,2);
  ret_k_lc[0] = 2.0*M_PI*(a00*in_kxyz[0] + a01*in_kxyz[1] + a02*in_kxyz[2]);
  ret_k_lc[1] = 2.0*M_PI*(a10*in_kxyz[0] + a11*in_kxyz[1] + a12*in_kxyz[2]);
  ret_k_lc[2] = 2.0*M_PI*(a20*in_kxyz[0] + a21*in_kxyz[1] + a22*in_kxyz[2]);

  return ret_k_lc;
}


double Util_PBC::cal_zincblende_a(const std::vector<double> &T123)
{
  double T1[3],T2[3],T3[3];
  T1[0]=T123[0*3+0];  T1[1]=T123[0*3+1];  T1[2]=T123[0*3+2];
  T2[0]=T123[1*3+0];  T2[1]=T123[1*3+1];  T2[2]=T123[1*3+2];
  T3[0]=T123[2*3+0];  T3[1]=T123[2*3+1];  T3[2]=T123[2*3+2];
  double len_T1=sqrt(T1[0]*T1[0]+T1[1]*T1[1]+T1[2]*T1[2]);
  double len_T2=sqrt(T2[0]*T2[0]+T2[1]*T2[1]+T2[2]*T2[2]);
  double len_T3=sqrt(T3[0]*T3[0]+T3[1]*T3[1]+T3[2]*T3[2]);
  double a_1=sqrt(2)*len_T1;
  double a_2=sqrt(2)*len_T2;
  double a_3=sqrt(2)*len_T3;
  if( fabs(a_1-a_2)<1.0e-10 && fabs(a_2-a_3)<1.0e-10){
    return a_1;
  }else{
    std::cout<<" error in cal_zincblende_a of Util_PBC class, a="<<a_1<<" "<<a_2<<" "<<a_3<<std::endl;
    return 0.0;
  }
}


double Util_PBC::cal_graphite_a(const std::vector<int> &max_Nc,
                                const std::vector<double> &T123)
{
  double T1[3],T2[3],T3[3];
  T1[0]=T123[0*3+0];  T1[1]=T123[0*3+1];  T1[2]=T123[0*3+2];
  T2[0]=T123[1*3+0];  T2[1]=T123[1*3+1];  T2[2]=T123[1*3+2];
  T3[0]=T123[2*3+0];  T3[1]=T123[2*3+1];  T3[2]=T123[2*3+2];
  double len_T1=sqrt(T1[0]*T1[0]+T1[1]*T1[1]+T1[2]*T1[2]);
  double len_T2=sqrt(T2[0]*T2[0]+T2[1]*T2[1]+T2[2]*T2[2]);
  double len_T3=sqrt(T3[0]*T3[0]+T3[1]*T3[1]+T3[2]*T3[2]);
  double a_1=len_T1;
  double a_2=len_T2;
  double a_3=len_T3;
  if( fabs(a_1-a_2)<1.0e-10 && max_Nc[0]!=0){ return a_1; }
  if( fabs(a_2-a_3)<1.0e-10 && max_Nc[1]!=0){ return a_2; }
  if( fabs(a_3-a_1)<1.0e-10 && max_Nc[2]!=0){ return a_3; }
  else{
    std::cout<<" error in cal_graphite_a of Util_PBC class, a="<<a_1<<" "<<a_2<<" "<<a_3<<std::endl;
    return 0.0;
  }
}




std::vector<double> CTRL_PBC::get_k_lc() const 
{
  int Nk = get_Nk_pbc();
  std::vector<double> ret_k_lc(Nk);
 
  int nk_1=Nk123[0]/2;
  int nk_2=Nk123[1]/2;
  int nk_3=Nk123[2]/2;

  int start_k1,stop_k1;
  int start_k2,stop_k2;
  int start_k3,stop_k3;
  if(nk_1==0){ start_k1=0;     stop_k1=0; }
  else{        start_k1=-nk_1; stop_k1=nk_1-1; }
  if(nk_2==0){ start_k2=0;     stop_k2=0; }
  else{        start_k2=-nk_2; stop_k2=nk_2-1; }
  if(nk_3==0){ start_k3=0;     stop_k3=0; }
  else{        start_k3=-nk_3; stop_k3=nk_3-1; }

  int cc=0;
  for(int k1=start_k1;k1<=stop_k1;k1++){
    for(int k2=start_k2;k2<=stop_k2;k2++){
      for(int k3=start_k3;k3<=stop_k3;k3++){
        ret_k_lc[cc*3+0]=2.0*M_PI*k1/Nk123[0];
        ret_k_lc[cc*3+1]=2.0*M_PI*k2/Nk123[1];
        ret_k_lc[cc*3+2]=2.0*M_PI*k3/Nk123[2];
        cc++;
      }
    }
  }
  return ret_k_lc;
}
  


std::vector<double> CTRL_PBC::get_nth_k_lc(int nth) const
{
  std::vector<double> ret_k_lc(3, 0.0);
 
  int nk_1=Nk123[0]/2;
  int nk_2=Nk123[1]/2;
  int nk_3=Nk123[2]/2;

  int start_k1,stop_k1;
  int start_k2,stop_k2;
  int start_k3,stop_k3;
  if(nk_1==0){ start_k1=0;     stop_k1=0; }
  else{        start_k1=-nk_1; stop_k1=nk_1-1; }
  if(nk_2==0){ start_k2=0;     stop_k2=0; }
  else{        start_k2=-nk_2; stop_k2=nk_2-1; }
  if(nk_3==0){ start_k3=0;     stop_k3=0; }
  else{        start_k3=-nk_3; stop_k3=nk_3-1; }

  int cc=0;
  for(int k1=start_k1;k1<=stop_k1;k1++){
    for(int k2=start_k2;k2<=stop_k2;k2++){
      for(int k3=start_k3;k3<=stop_k3;k3++){
        if(cc==nth){
          ret_k_lc[0]=2.0*M_PI*k1/Nk123[0];
          ret_k_lc[1]=2.0*M_PI*k2/Nk123[1];
          ret_k_lc[2]=2.0*M_PI*k3/Nk123[2];
          return ret_k_lc;
        }
        cc++;
      }
    }
  }
  return ret_k_lc;
}
  






}  // end of namespace "Lotus_core"

#endif // end of include-guard






