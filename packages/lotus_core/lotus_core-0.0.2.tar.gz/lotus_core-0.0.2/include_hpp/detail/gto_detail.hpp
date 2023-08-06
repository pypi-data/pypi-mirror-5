

#ifndef GTO_DETAIL_HPP
#define GTO_DETAIL_HPP

#include "gto.hpp"
#include "Matrixs_tmpl.hpp"



namespace Lotus_core {

double Cgto::cal_grid_value(const std::vector<double> &xyz) const {
  double sq_R_ga=(xyz[0]-R[0])*(xyz[0]-R[0])+(xyz[1]-R[1])*(xyz[1]-R[1])+(xyz[2]-R[2])*(xyz[2]-R[2]);
  double ret=0.0;
  double x_n=1.0;
  for(int i=0;i<n[0];i++)
    x_n*=(xyz[0]-R[0]);
  double y_n=1.0;
  for(int i=0;i<n[1];i++)
    y_n*=(xyz[1]-R[1]);
  double z_n=1.0;
  for(int i=0;i<n[2];i++)
    z_n*=(xyz[2]-R[2]);
  for(int i=0;i<gd.size();i++)
    ret+=dI[i]*x_n*y_n*z_n*exp(-gd[i].g*sq_R_ga);
  return ret; 
}


std::vector<double> Cgto::cal_deri_grid_value(const std::vector<double> &xyz) const {
  std::vector<double> ret_deri(3, 0.0);

  double sq_R_ga=(xyz[0]-R[0])*(xyz[0]-R[0])+(xyz[1]-R[1])*(xyz[1]-R[1])+(xyz[2]-R[2])*(xyz[2]-R[2]);
                               
  double x_n,y_n,z_n;
  double x_n_p1,y_n_p1,z_n_p1;
  double x_n_m1,y_n_m1,z_n_m1;

  if(n[0]>=1){
    x_n_m1=1.0;
    for(int i=0;i<n[0]-1;i++) x_n_m1*=(xyz[0]-R[0]);
    x_n   =x_n_m1*(xyz[0]-R[0]);
    x_n_p1=x_n   *(xyz[0]-R[0]);
  }else{
    x_n_m1=0; x_n=1.0; x_n_p1=(xyz[0]-R[0]);
  }
  if(n[1]>=1){
    y_n_m1=1.0;
    for(int i=0;i<n[1]-1;i++) y_n_m1*=(xyz[1]-R[1]);
    y_n   =y_n_m1*(xyz[1]-R[1]);
    y_n_p1=y_n   *(xyz[1]-R[1]);
  }else{
    y_n_m1=0; y_n=1.0; y_n_p1=(xyz[1]-R[1]);
  }
  if(n[2]>=1){
    z_n_m1=1.0;
    for(int i=0;i<n[2]-1;i++) z_n_m1*=(xyz[2]-R[2]);
    z_n   =z_n_m1*(xyz[2]-R[2]);
    z_n_p1=z_n   *(xyz[2]-R[2]);
  }else{
    z_n_m1=0; z_n=1.0; z_n_p1=(xyz[2]-R[2]);
  }

  double tmp_x,tmp_y,tmp_z,tmp_exp_dI;
  for(int i=0;i<gd.size();i++){
    tmp_exp_dI=dI[i]*exp(-gd[i].g*sq_R_ga);
    tmp_x=-2.0*gd[i].g*x_n_p1;
    tmp_y=-2.0*gd[i].g*y_n_p1;
    tmp_z=-2.0*gd[i].g*z_n_p1;
    if(n[0]!=0) tmp_x+=n[0]*x_n_m1;
    if(n[1]!=0) tmp_y+=n[1]*y_n_m1;
    if(n[2]!=0) tmp_z+=n[2]*z_n_m1;
    ret_deri[0]+=tmp_x*y_n*z_n*tmp_exp_dI;
    ret_deri[1]+=x_n*tmp_y*z_n*tmp_exp_dI;
    ret_deri[2]+=x_n*y_n*tmp_z*tmp_exp_dI;
  }

  return ret_deri;
}



// ret_deri2[0]==xx, [1]==xy, [2]==xz, [3]==yy, [4]==yz, [5]==zz
std::vector<double> Cgto::cal_deri2_grid_value(const std::vector<double> &xyz) const {
   std::vector<double> ret_deri2(6, 0.0);

  double sq_R_ga=(xyz[0]-R[0])*(xyz[0]-R[0])+(xyz[1]-R[1])*(xyz[1]-R[1])+(xyz[2]-R[2])*(xyz[2]-R[2]);

  double x_n,y_n,z_n;
  double x_n_p1,y_n_p1,z_n_p1,x_n_p2,y_n_p2,z_n_p2;
  double x_n_m1,y_n_m1,z_n_m1,x_n_m2,y_n_m2,z_n_m2;

  if(n[0]>=2){
    x_n_m2=1.0;  for(int i=0;i<n[0]-2;i++) x_n_m2*=(xyz[0]-R[0]);
    x_n_m1=(xyz[0]-R[0])*x_n_m2;
    x_n   =(xyz[0]-R[0])*x_n_m1;
    x_n_p1=(xyz[0]-R[0])*x_n;
    x_n_p2=(xyz[0]-R[0])*x_n_p1;
  }else if(n[0]==1){
    x_n_m2=0.0;
    x_n_m1=1.0; 
    x_n   =(xyz[0]-R[0]);
    x_n_p1=(xyz[0]-R[0])*x_n;
    x_n_p2=(xyz[0]-R[0])*x_n_p1;
  }else{
    x_n_m2=0.0;
    x_n_m1=0.0;
    x_n   =1.0;
    x_n_p1=(xyz[0]-R[0]);
    x_n_p2=(xyz[0]-R[0])*x_n_p1;
  }
  if(n[1]>=2){
    y_n_m2=1.0;  for(int i=0;i<n[1]-2;i++) y_n_m2*=(xyz[1]-R[1]);
    y_n_m1=(xyz[1]-R[1])*y_n_m2;
    y_n   =(xyz[1]-R[1])*y_n_m1;
    y_n_p1=(xyz[1]-R[1])*y_n;
    y_n_p2=(xyz[1]-R[1])*y_n_p1;
  }else if(n[1]==1){
    y_n_m2=0.0;
    y_n_m1=1.0;  
    y_n   =(xyz[1]-R[1]);
    y_n_p1=(xyz[1]-R[1])*y_n;
    y_n_p2=(xyz[1]-R[1])*y_n_p1;
  }else{
    y_n_m2=0.0;
    y_n_m1=0.0;
    y_n   =1.0;
    y_n_p1=(xyz[1]-R[1]);
    y_n_p2=(xyz[1]-R[1])*y_n_p1;
  }
  if(n[2]>=2){
    z_n_m2=1.0;  for(int i=0;i<n[2]-2;i++) z_n_m2*=(xyz[2]-R[2]);
    z_n_m1=(xyz[2]-R[2])*z_n_m2;
    z_n   =(xyz[2]-R[2])*z_n_m1;
    z_n_p1=(xyz[2]-R[2])*z_n;
    z_n_p2=(xyz[2]-R[2])*z_n_p1;
  }else if(n[2]==1){
    z_n_m2=0.0;
    z_n_m1=1.0;  
    z_n   =(xyz[2]-R[2]);
    z_n_p1=(xyz[2]-R[2])*z_n;
    z_n_p2=(xyz[2]-R[2])*z_n_p1;
  }else{
    z_n_m2=0.0;
    z_n_m1=0.0;
    z_n   =1.0;
    z_n_p1=(xyz[2]-R[2]);
    z_n_p2=(xyz[2]-R[2])*z_n_p1;
  }

  double tmp_xx,tmp_yy,tmp_zz,tmp_xy,tmp_xz,tmp_yz,tmp_exp_dI;
  for(int i=0;i<gd.size();i++){
    double g=gd[i].g;
    tmp_exp_dI=dI[i]*exp(-g*sq_R_ga);
    tmp_xx=n[0]*(n[0]-1)*x_n_m2 -2.0*g*(n[0]+n[0]+1)*x_n +4.0*g*g*x_n_p2;
    tmp_yy=n[1]*(n[1]-1)*y_n_m2 -2.0*g*(n[1]+n[1]+1)*y_n +4.0*g*g*y_n_p2;
    tmp_zz=n[2]*(n[2]-1)*z_n_m2 -2.0*g*(n[2]+n[2]+1)*z_n +4.0*g*g*z_n_p2;
    tmp_xy=n[0]*n[1]*x_n_m1*y_n_m1 -2.0*g*n[0]*x_n_m1*y_n_p1 -2.0*g*n[1]*x_n_p1*y_n_m1 +4.0*g*g*x_n_p1*y_n_p1;
    tmp_xz=n[0]*n[2]*x_n_m1*z_n_m1 -2.0*g*n[0]*x_n_m1*z_n_p1 -2.0*g*n[2]*x_n_p1*z_n_m1 +4.0*g*g*x_n_p1*z_n_p1;
    tmp_yz=n[1]*n[2]*y_n_m1*z_n_m1 -2.0*g*n[1]*y_n_m1*z_n_p1 -2.0*g*n[2]*y_n_p1*z_n_m1 +4.0*g*g*y_n_p1*z_n_p1;
    
    ret_deri2[0]+=tmp_xx*y_n*z_n*tmp_exp_dI;
    ret_deri2[1]+=x_n*tmp_yy*z_n*tmp_exp_dI;
    ret_deri2[2]+=x_n*y_n*tmp_zz*tmp_exp_dI;
    ret_deri2[3]+=tmp_xy*z_n*tmp_exp_dI;
    ret_deri2[4]+=tmp_xz*y_n*tmp_exp_dI;
    ret_deri2[5]+=tmp_yz*x_n*tmp_exp_dI;
  }

  return ret_deri2;
}

template <typename Integ1e>
void Shell_Cgto::grid_value(double *ret,const double *xyz) const {
  int num_pgto=get_num_pgto();
  int num_cgto=get_num_cgto();
  for(int i=0;i<num_cgto;i++) ret[i]=0.0;

  double sq_R_ga=(xyz[0]-R[0])*(xyz[0]-R[0])+(xyz[1]-R[1])*(xyz[1]-R[1])+(xyz[2]-R[2])*(xyz[2]-R[2]);
  double x=(xyz[0]-R[0]);
  double y=(xyz[1]-R[1]);
  double z=(xyz[2]-R[2]);

  double pow_x[10],pow_y[10],pow_z[10],exp_g[200];
  pow_x[0]=pow_y[0]=pow_z[0]=1.0;
  for(int n=1;n<=shell_type;n++){
    pow_x[n]=pow_x[n-1]*x;
    pow_y[n]=pow_y[n-1]*y;
    pow_z[n]=pow_z[n-1]*z;
  }
  for(int i=0;i<num_pgto;i++){
    double tmp_g=gd[i].g;
    exp_g[i]=exp(-tmp_g*sq_R_ga);
  } 

  for(int cc=0;cc<num_cgto;cc++){
    int tmp_n[3];
    Integ1e::get_no_to_n(tmp_n, shell_type, cc);
    int n_x=tmp_n[0];  int n_y=tmp_n[1];  int n_z=tmp_n[2];
    double pow_xyz=pow_x[n_x]*pow_y[n_y]*pow_z[n_z];
    for(int i=0;i<num_pgto;i++){
      ret[cc]+=pow_xyz*dI[i*num_cgto+cc]*exp_g[i];
    }
  }
}

template <typename Integ1e>
void Shell_Cgto::grid_deri_value(double *ret_deri,const double *xyz) const{
  int num_pgto=get_num_pgto();
  int num_cgto=get_num_cgto();
  for(int i=0;i<3*num_cgto;i++) ret_deri[i]=0.0;

  double sq_R_ga=(xyz[0]-R[0])*(xyz[0]-R[0])+(xyz[1]-R[1])*(xyz[1]-R[1])+(xyz[2]-R[2])*(xyz[2]-R[2]);
  double x=(xyz[0]-R[0]);
  double y=(xyz[1]-R[1]);
  double z=(xyz[2]-R[2]);


  double pow_x[10],pow_y[10],pow_z[10],pow_xyz_p[3],pow_xyz_m[3],exp_g[200];
  pow_x[0]=pow_y[0]=pow_z[0]=1.0;
  for(int n=1;n<=shell_type+1;n++){
    pow_x[n]=pow_x[n-1]*x;
    pow_y[n]=pow_y[n-1]*y;
    pow_z[n]=pow_z[n-1]*z;
  }
  for(int i=0;i<num_pgto;i++){
    double tmp_g=gd[i].g; 
    exp_g[i]=exp(-tmp_g*sq_R_ga);
  } 

  for(int cc=0;cc<num_cgto;cc++){
//    std::vector<int> tmp_n = Integ1e::get_no_to_n(shell_type, cc);
    int tmp_n[3];
    Integ1e::get_no_to_n(&tmp_n[0], shell_type, cc);
    int n_x=tmp_n[0];  int n_y=tmp_n[1];  int n_z=tmp_n[2]; 
    for(int p=0;p<3;p++){
      int np[3],nm[3];
      np[0]=n_x; np[1]=n_y; np[2]=n_z;
      nm[0]=n_x; nm[1]=n_y; nm[2]=n_z;
      np[p]++;
      nm[p]--;
      pow_xyz_p[p]=-2.0*pow_x[np[0]]*pow_y[np[1]]*pow_z[np[2]];
      if(tmp_n[p]>0) pow_xyz_m[p]=tmp_n[p]*pow_x[nm[0]]*pow_y[nm[1]]*pow_z[nm[2]];
      else           pow_xyz_m[p]=0.0;      
    }
    for(int i=0;i<num_pgto;i++){
      double tmp_g=gd[i].g; 
      double dI_exp=dI[i*num_cgto+cc]*exp_g[i];
      for(int p=0;p<3;p++){
        ret_deri[cc*3+p]+=(tmp_g*pow_xyz_p[p]+pow_xyz_m[p])*dI_exp;
      }
    }
  }

}

template <typename Integ1e>
void Shell_Cgto::grid_deri2_value(double *ret_deri2,const double *xyz) const {
  int num_pgto=get_num_pgto();
  int num_cgto=get_num_cgto();
  for(int i=0;i<6*num_cgto;i++) ret_deri2[i]=0.0;

  double sq_R_ga=(xyz[0]-R[0])*(xyz[0]-R[0])+(xyz[1]-R[1])*(xyz[1]-R[1])+(xyz[2]-R[2])*(xyz[2]-R[2]);
  double x=(xyz[0]-R[0]);
  double y=(xyz[1]-R[1]);
  double z=(xyz[2]-R[2]);

  int cc_pq[3][3];
  cc_pq[0][0]=0;
  cc_pq[0][1]=1;
  cc_pq[0][2]=2;
  cc_pq[1][1]=3;
  cc_pq[1][2]=4;
  cc_pq[2][2]=5;

  double pow_x[10],pow_y[10],pow_z[10],pow_1[6],pow_2[6],pow_3[6],pow_4[6],exp_g[200];
  pow_x[0]=pow_y[0]=pow_z[0]=1.0;
  for(int n=1;n<=shell_type+2;n++){
    pow_x[n]=pow_x[n-1]*x;
    pow_y[n]=pow_y[n-1]*y;
    pow_z[n]=pow_z[n-1]*z;
  }
  for(int i=0;i<num_pgto;i++){
    double tmp_g=gd[i].g; 
    exp_g[i]=exp(-tmp_g*sq_R_ga);
  } 

  for(int cc=0;cc<num_cgto;cc++){
//    std::vector<int> tmp_n = Integ1e::get_no_to_n(shell_type, cc);
    int tmp_n[3];
    Integ1e::get_no_to_n(&tmp_n[0], shell_type, cc);
    int n_x=tmp_n[0];  int n_y=tmp_n[1];  int n_z=tmp_n[2]; 
    for(int p=0;p<3;p++){
      int np1[3],nm1[3];
      np1[0]=n_x; np1[1]=n_y; np1[2]=n_z;
      nm1[0]=n_x; nm1[1]=n_y; nm1[2]=n_z;
      np1[p]++;
      nm1[p]--;
      for(int q=p;q<3;q++){
        pow_3[cc_pq[p][q]]=0.0;
        pow_4[cc_pq[p][q]]=0.0;
        int np2[3],nm2[3];
        np2[0]=np1[0]; np2[1]=np1[1]; np2[2]=np1[2];
        nm2[0]=np1[0]; nm2[1]=np1[1]; nm2[2]=np1[2];
        np2[q]++;
        nm2[q]--;
        pow_1[cc_pq[p][q]]=4.0*pow_x[np2[0]]*pow_y[np2[1]]*pow_z[np2[2]];
        if(np1[q]>0) pow_2[cc_pq[p][q]]=-2.0*np1[q]*pow_x[nm2[0]]*pow_y[nm2[1]]*pow_z[nm2[2]];
        else         pow_2[cc_pq[p][q]]=0.0;
      }
      if(tmp_n[p]>0){
        for(int q=p;q<3;q++){
          int np2[3],nm2[3];
          np2[0]=nm1[0]; np2[1]=nm1[1]; np2[2]=nm1[2];
          nm2[0]=nm1[0]; nm2[1]=nm1[1]; nm2[2]=nm1[2];
          np2[q]++;
          nm2[q]--;
          pow_3[cc_pq[p][q]]=-2.0*tmp_n[p]*pow_x[np2[0]]*pow_y[np2[1]]*pow_z[np2[2]];
          if(nm1[q]>0) pow_4[cc_pq[p][q]]=tmp_n[p]*nm1[q]*pow_x[nm2[0]]*pow_y[nm2[1]]*pow_z[nm2[2]];
          else         pow_4[cc_pq[p][q]]=0.0;
        }
      }
    }
    for(int i=0;i<num_pgto;i++){
      double dI_exp=dI[i*num_cgto+cc]*exp_g[i];
      double tmp_g=gd[i].g; 
      for(int p=0;p<3;p++){
        for(int q=p;q<3;q++){
          ret_deri2[cc*6+cc_pq[p][q]]+=(tmp_g*tmp_g*pow_1[cc_pq[p][q]]
                                       +tmp_g*(pow_2[cc_pq[p][q]]+pow_3[cc_pq[p][q]])+pow_4[cc_pq[p][q]])*dI_exp;
        }
      }
    }

  }

}


//
//  Util_GTO class
//

std::vector<Shell_Cgto> Util_GTO::get_scgtos_PBC(const std::vector<Shell_Cgto> &scgtos,  
                                            const std::vector<int> &max_Nc,const std::vector<double> &T123){
  int N123_c=(2*max_Nc[0]+1)*(2*max_Nc[1]+1)*(2*max_Nc[2]+1);
  int N_scgtos=scgtos.size();
  std::vector<Shell_Cgto> scgtos_pbc;               
  scgtos_pbc.reserve(N123_c*N_scgtos);

  //  for n1=0,n2=0,n3=3
  int min_cn=0;
  for(int cc=0;cc<N_scgtos;cc++){
    scgtos_pbc.push_back(scgtos[cc]);
    min_cn+=scgtos[cc].get_num_cgto();
  }

  int N_atoms=scgtos[N_scgtos-1].get_atom_no()+1;
  int nnn=1;
  for(int q=0;q<N123_c;q++){
    std::vector<int> tmp_n=Util_PBC::cal_n_from_q(q,max_Nc);
     int n1=tmp_n[0];
     int n2=tmp_n[1];
     int n3=tmp_n[2];
    if(n1==0 && n2==0 && n3==0){
    }else{
      for(int cc=0;cc<N_scgtos;cc++){
        std::vector<double> tmpR(3),tmpR_pbc(3);
        tmpR = scgtos[cc].get_R();
        tmpR_pbc[0]=tmpR[0]+n1*T123[0*3+0]+n2*T123[1*3+0]+n3*T123[2*3+0];
        tmpR_pbc[1]=tmpR[1]+n1*T123[0*3+1]+n2*T123[1*3+1]+n3*T123[2*3+1];
        tmpR_pbc[2]=tmpR[2]+n1*T123[0*3+2]+n2*T123[1*3+2]+n3*T123[2*3+2];
        std::vector<int> tmp_nT_pbc(3);  
        tmp_nT_pbc[0]=n1; tmp_nT_pbc[1]=n2; tmp_nT_pbc[2]=n3;
        Shell_Cgto tmp_scgto=scgtos[cc];
        tmp_scgto.set_R(tmpR_pbc);
        tmp_scgto.set_nT_pbc(tmp_nT_pbc);
        tmp_scgto.set_min_cgto_no(min_cn);
        int tmp_atom_no = scgtos[cc].get_atom_no();
        int an_pbc      =tmp_atom_no+N_atoms*nnn;
        tmp_scgto.set_atom_no(an_pbc);
        scgtos_pbc.push_back(tmp_scgto);
        min_cn+=scgtos[cc].get_num_cgto();
      }
      nnn++;
    }
  }

  return scgtos_pbc;
}



template <typename M_tmpl,typename Integ1e>
void Util_GTO::cal_cutoffM_base(std::vector<M_tmpl*> &cutoffM,const std::vector<Shell_Cgto> &scgtos,const CTRL_PBC &ctrl_pbc){
  int N_scgtos=scgtos.size();
  std::vector<int> n_zero(3,0);
  int zero_q=ctrl_pbc.get_zero_qc();
  int N123_c=ctrl_pbc.get_N123_c();

  cutoffM.clear();
  cutoffM.reserve(N123_c);                       
  for(int i=0;i<N123_c;i++) cutoffM[i]->set_IJ(N_scgtos,N_scgtos);

  #ifdef _OPENMP
  #pragma omp parallel
  {
  #endif

  std::vector<M_tmpl> omp_M(N123_c);
  for(int t=0;t<=zero_q;t++){
    omp_M[t].set_IJ(N_scgtos, N_scgtos);
  }

  Integ1e pint1e;
  for(int t=0;t<=zero_q;t++){
    std::vector<int> nc=ctrl_pbc.get_nc_from_q(t);

    for(int p=0;p<N_scgtos;p++){
      int start_q=0;
      if(t==zero_q) start_q=p;
      #ifdef _OPENMP
      #pragma omp for schedule(dynamic)
      #endif
      for(int q=start_q;q<N_scgtos;q++){

        int N_p=scgtos[p].get_num_pgto();
        int N_q=scgtos[q].get_num_pgto();
        std::vector<double> Rp     = scgtos[p].get_R();
        std::vector<double> Rq     = scgtos[q].get_R();
        std::vector<double> Rq_pbc = ctrl_pbc.get_R_pbc(Rq,nc);

        std::vector<double> g_p = scgtos[p].get_g();
        std::vector<double> d_p = scgtos[p].get_d();
        std::vector<double> g_q = scgtos[q].get_g();
        std::vector<double> d_q = scgtos[q].get_d();

        double tmp_v=0.0;
        for(int a=0;a<N_p;a++){
          for(int b=0;b<N_q;b++){
            pint1e.set_gR_12(g_p[a],Rp,g_q[b],Rq_pbc);
            double I_a=Integ1e::cal_I(g_p[a],n_zero);
            double I_b=Integ1e::cal_I(g_q[b],n_zero);
            tmp_v+=d_p[a]*I_a*d_q[b]*I_b*pint1e.overlap_simple(n_zero,n_zero);
          }
        }
//        cutoffM[t]->set_value(p,q,tmp_v);
        omp_M[t].set_value(p,q,tmp_v);
      }
    }
  }  


  #ifdef _OPENMP
  #pragma omp critical(mat_add)
  #endif
  {
    for(int t=0;t<=zero_q;t++){
      for(int p=0;p<N_scgtos;p++){
        for(int q=0;q<N_scgtos;q++){
          cutoffM[t]->add(p,q,omp_M[t].get_value(p,q));
        }
      }
    }
  }


  #ifdef _OPENMP
  }  // end of openMP parallel-loop
  #endif

  for(int p=0;p<N_scgtos;p++){
    for(int q=p;q<N_scgtos;q++){
      double tmp_v=cutoffM[zero_q]->get_value(p,q);
      cutoffM[zero_q]->set_value(q,p,tmp_v);
    }
  }

  for(int t=1;t<=zero_q;t++) mat_transpose(*cutoffM[zero_q+t],*cutoffM[zero_q-t]);
 
}

template <typename Integ1e>
std::vector<double> Util_GTO::cal_s_shell(int p, const std::vector<Shell_Cgto> &scgtos)
{

  using namespace std;
   
  std::vector<double> Rp     = scgtos[p].get_R();

  int tn_p=scgtos[p].get_max_tn();

  int n_cgto_p=scgtos[p].get_num_cgto();
  int n_cgto_pp=n_cgto_p*n_cgto_p;
  std::vector<double> ret_shell(n_cgto_pp, 0.0), tmp_shell;

  std::vector<double> g_p = scgtos[p].get_g();
  std::vector<double> d_p = scgtos[p].get_d();

  //
  // loop for pgto
  Integ1e pint1e;
  for(int a=0;a<scgtos[p].get_num_pgto();a++){
    for(int b=0;b<scgtos[p].get_num_pgto();b++){
      std::vector<double> dI_1=pint1e.cal_dI(tn_p,g_p[a],d_p[a]);
      std::vector<double> dI_2=pint1e.cal_dI(tn_p,g_p[b],d_p[b]);
      pint1e.set_gR_12(g_p[a],Rp,g_p[b],Rp);
      pint1e.overlap(tmp_shell,tn_p,tn_p,dI_1,dI_2);
      for(int i=0;i<n_cgto_pp;i++) ret_shell[i]+=tmp_shell[i];
    } 
  }

  return ret_shell;
}


template <typename Integ1e>
std::vector<Shell_Cgto> Util_GTO::get_scgtos_from_string(const char *qm_string)
{
  std::vector<Shell_Cgto> ret_scgtos;

  std::istringstream is(qm_string);
//  std::ifstream is(filename);
//  if(!is){
//    std::cout<<" Error: cannnot open (get_scgtos_from_file) "<<filename<<std::endl;
//    exit(1);
//  }

  int N_scgtos,N_ecps,N_atoms;
  char nop[512]="";
  N_scgtos=N_ecps=N_atoms=0;
 
  is>>nop;
  is>>nop;
  is>>N_scgtos;  is>>N_ecps;  is>>N_atoms;

  // MOLECULE_COORDINATE
  is>>nop;
  int atom_no,in_atom_Z;
  double x,y,z;
  for(int a=0;a<N_atoms;a++){
    is>>nop;  is>>in_atom_Z; is>>nop; is>>atom_no; is>>nop; 
    is>>x;  is>>y;  is>>z;
  }

  // SCGTOS
  int no_scgtos,num_pgto,shell_type;
  int atom_type,min_cgto_no=0;
  double g,d;
  std::vector<double> R(3);
  is>>nop;
  for(int i=0;i<N_scgtos;i++){
    is>>nop; is>>nop; is>>no_scgtos; is>>nop; is>>shell_type; 
    is>>nop; is>>atom_no; is>>nop; is>>nop; is>>nop; is>>atom_type; is>>nop;
    is>>x; is>>y; is>>z;
    is>>num_pgto;
    R[0]=x; R[1]=y; R[2]=z;
    Shell_Cgto tmp_scgto;

    tmp_scgto.set_shell_type(shell_type);
    tmp_scgto.set_atom_type(atom_type);
    tmp_scgto.set_atom_no(atom_no);  
    tmp_scgto.set_R(R); 
    tmp_scgto.set_min_cgto_no(min_cgto_no);
    min_cgto_no+=tmp_scgto.get_num_cgto();



    std::vector<double> vec_g,vec_d;
    for(int j=0;j<num_pgto;j++){
      is>>g; is>>d;
      vec_g.push_back(g);
      vec_d.push_back(d);
    }
    tmp_scgto.set_gd(vec_g,vec_d);

    ret_scgtos.push_back(tmp_scgto);     
  }

  normalize_scgtos<Integ1e>(ret_scgtos);

  for(int i=0;i<ret_scgtos.size();i++) ret_scgtos[i].set_dI<Integ1e>();

  return ret_scgtos;
}






}  // end of namespace "Lotus_core"


#endif // end of include-guard
