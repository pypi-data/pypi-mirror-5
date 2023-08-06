

#ifndef FOCK2E_DETAIL_HPP
#define FOCK2E_DETAIL_HPP

#ifdef _OPENMP
#include <omp.h>
#endif

#include "Fock2e_tmpl.hpp"
#include "Util.hpp"


#include <fstream>
#include <iostream>

namespace Lotus_core {
using namespace std;




template <typename M_tmpl,typename Integ2e>
void Fock2e_tmpl<M_tmpl,Integ2e>::cal_cutoffM_base(std::vector<M_tmpl*> &cutoffM,const std::vector<Shell_Cgto> &scgtos,const CTRL_PBC &ctrl_pbc){
                                                   
  int N_scgtos=scgtos.size();
  std::vector<int> n_zero(3,0);
  int zero_q=ctrl_pbc.get_zero_qc();
  int N123_c=ctrl_pbc.get_N123_c();

  cutoffM.clear();
  cutoffM.reserve(N123_c);                       
  for(int i=0;i<N123_c;i++) cutoffM[i]->set_IJ(N_scgtos,N_scgtos);

  #ifdef _OPENMP
  #pragma omp parallel
  {  // start of openMP parallel-loop
  #endif

  std::vector<M_tmpl> omp_M(N123_c);
  for(int t=0;t<=zero_q;t++){
    omp_M[t].set_IJ(N_scgtos, N_scgtos);
  }


  Integ2e pint2e;
  for(int t=0;t<=zero_q;t++){
    std::vector<int> nc=ctrl_pbc.get_nc_from_q(t);

    for(int p=0;p<N_scgtos;p++){
      int start_q=0;
      if(t==zero_q) start_q=p;
      #ifdef _OPENMP
      #pragma omp for schedule(static)
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

        double eri=0.0;
        for(int a=0;a<N_p;a++){
          for(int b=0;b<N_q;b++){
            pint2e.set_gR_12(g_p[a],Rp,g_q[b],Rq_pbc);
            double I_a=Integ2e::cal_I(g_p[a],n_zero);
            double I_b=Integ2e::cal_I(g_q[b],n_zero);
            for(int c=0;c<N_p;c++){
              for(int d=0;d<N_q;d++){
                double I_c=Integ2e::cal_I(g_p[a],n_zero);
                double I_d=Integ2e::cal_I(g_q[b],n_zero);
                pint2e.set_gR_34(g_p[c],Rp,g_q[d],Rq_pbc);
                if(_mode==Fock2e_Enum::Normal) pint2e.set_eri_ssss(0,0,0.0);
                if(_mode==Fock2e_Enum::Erfc)   pint2e.set_eri_ssss(0,1,_omega);
                if(_mode==Fock2e_Enum::Erf)    pint2e.set_eri_ssss(0,2,_omega);
                eri+=d_p[a]*I_a*d_q[b]*I_b*d_p[c]*I_c*d_q[d]*I_d*pint2e.ERI_simple(n_zero,n_zero,n_zero,n_zero);
              }
            }
          }
        }
        double sqrt_eri=sqrt(fabs(eri));
//        cutoffM[t]->set_value(p,q,sqrt_eri);
        omp_M[t].set_value(p,q,sqrt_eri);
   
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





template <typename M_tmpl,typename Integ2e>
void Fock2e_tmpl<M_tmpl,Integ2e>::cal_eri_shell(std::vector<double> &ret_eri,int p,int q,int r,int s,const std::vector<Shell_Cgto> &scgtos,
                                                const std::vector<int> &Q_q, const std::vector<int> &Q_r,
                                                const std::vector<int> &Q_s, const CTRL_PBC &ctrl_pbc)
{

  double Rp[3], Rq[3], Rr[3], Rs[3];
  scgtos[p].get_R_array(Rp);
  scgtos[q].get_R_array(Rq);
  scgtos[r].get_R_array(Rr);
  scgtos[s].get_R_array(Rs);

  double Rq_pbc[3], Rr_pbc[3], Rs_pbc[3];
  ctrl_pbc.get_R_pbc_array(Rq_pbc, Rq, &Q_q[0]);
  ctrl_pbc.get_R_pbc_array(Rr_pbc, Rr, &Q_r[0]);
  ctrl_pbc.get_R_pbc_array(Rs_pbc, Rs, &Q_s[0]);

  int tn_p=scgtos[p].get_max_tn();
  int tn_q=scgtos[q].get_max_tn();
  int tn_r=scgtos[r].get_max_tn();
  int tn_s=scgtos[s].get_max_tn();
  int tn=tn_p+tn_q+tn_r+tn_s;

  int N_p=scgtos[p].get_num_pgto();
  int N_q=scgtos[q].get_num_pgto();
  int N_r=scgtos[r].get_num_pgto();
  int N_s=scgtos[s].get_num_pgto();

  int n_cgto_p=scgtos[p].get_num_cgto();
  int n_cgto_q=scgtos[q].get_num_cgto();
  int n_cgto_r=scgtos[r].get_num_cgto();
  int n_cgto_s=scgtos[s].get_num_cgto();
  int n_cgto_pqrs=n_cgto_p*n_cgto_q*n_cgto_r*n_cgto_s;

  ret_eri.reserve(n_cgto_pqrs);
  ret_eri.clear();
  for(int i=0;i<n_cgto_pqrs;i++) ret_eri.push_back(0.0);

  std::vector<double> tmp_eri(n_cgto_pqrs);
  std::vector<double> dI_1, dI_2, dI_3, dI_4;

  Integ2e pint2e;
  int pint2e_mode=0;
  if(_mode==Fock2e_Enum::Normal)  pint2e_mode=0; 
  if(_mode==Fock2e_Enum::Erfc)    pint2e_mode=1; 
  if(_mode==Fock2e_Enum::Erf)     pint2e_mode=2; 

  pint2e.ERI_init(tn_p, tn_q, tn_r, tn_s);

  for(int a=0;a<N_p;a++){
    scgtos[p].get_dI(dI_1,a);
    double g_a = scgtos[p].get_nth_g(a);
    for(int b=0;b<N_q;b++){
      scgtos[q].get_dI(dI_2,b);
      double g_b = scgtos[q].get_nth_g(b);
      pint2e.set_gR_12(g_a, Rp, g_b, Rq_pbc);
      for(int c=0;c<N_r;c++){
        scgtos[r].get_dI(dI_3,c);
        double g_c = scgtos[r].get_nth_g(c);
        for(int d=0;d<N_s;d++){
          scgtos[s].get_dI(dI_4,d);
          double g_d = scgtos[s].get_nth_g(d);
          pint2e.set_gR_34(g_c, Rr_pbc, g_d, Rs_pbc);
          pint2e.set_eri_ssss(tn,pint2e_mode,_omega);
          pint2e.ERI(tmp_eri, tn_p, tn_q, tn_r, tn_s, dI_1, dI_2, dI_3, dI_4);
          for(int i=0;i<n_cgto_pqrs;i++) ret_eri[i]+=tmp_eri[i];
        }
      }
    } 
  }
  pint2e.ERI_finalize(tn_p, tn_q, tn_r, tn_s);

}




template <typename M_tmpl,typename Integ2e>
void Fock2e_tmpl<M_tmpl,Integ2e>::set_data_eri(std::vector<ERI_data> &ret_eri_data,int p,int q,int r,int s,
                                               const std::vector<Shell_Cgto> &scgtos,const std::vector<double> &eri_shell){

  int N_cgtos=Util_GTO::get_N_cgtos(scgtos);

  int min_i=scgtos[p].get_min_cgto_no();
  int min_j=scgtos[q].get_min_cgto_no();
  int min_k=scgtos[r].get_min_cgto_no();
  int min_l=scgtos[s].get_min_cgto_no();
  int max_i=scgtos[p].get_max_cgto_no();
  int max_j=scgtos[q].get_max_cgto_no();
  int max_k=scgtos[r].get_max_cgto_no();
  int max_l=scgtos[s].get_max_cgto_no();

//  ret_num_data=0;
  int cc_eri_ijkl=0;
  for(int i=min_i;i<=max_i;i++){
    for(int j=min_j;j<=max_j;j++){
      for(int k=min_k;k<=max_k;k++){
        for(int l=min_l;l<=max_l;l++){
          if(j>=i && l>=k && k>=i){
            if(i==k && j>l){   // do nothing
            }else{

              int write_ij=i+j*N_cgtos;
              int write_kl=k+l*N_cgtos;
              //
              //  for energy
              if(fabs(eri_shell[cc_eri_ijkl])>CUTOFF_Fock2e){
                if(i==k && j<l){
                  ret_eri_data.push_back(ERI_data(write_ij,write_kl,eri_shell[cc_eri_ijkl]));
                  ret_eri_data.push_back(ERI_data(write_kl,write_ij,eri_shell[cc_eri_ijkl]));
                }else{
                  ret_eri_data.push_back(ERI_data(write_ij,write_kl,eri_shell[cc_eri_ijkl]));
                }
              }
            }
          }
          cc_eri_ijkl++; 
        }
      }
    }
  }

}



template <typename M_tmpl,typename Integ2e> template <typename M_tmpl2>
void Fock2e_tmpl<M_tmpl,Integ2e>::cal_Vh_and_Vx_sub(M_tmpl2 &Vh,M_tmpl2 &Vx, const M_tmpl &D,const std::vector<ERI_data> &eri_data){
                                                    
  int N_cgtos=D.get_I();
  double D_ij,D_ik,D_jk,D_kl,D_il,D_jl;
  double D_ki,D_kj,D_li,D_lj;
  double tmp_eri,tmp_eri_1, tmp_eri_2, tmp_eri_3, tmp_eri_4;
  double         tmp_eri_1b,tmp_eri_2b,tmp_eri_3b,tmp_eri_4b;
  double eri_ijkl;
  int i,j,k,l;

  for(int cc=0;cc<eri_data.size();cc++){
    j=eri_data[cc].ij/N_cgtos;
    i=eri_data[cc].ij%N_cgtos;
    l=eri_data[cc].kl/N_cgtos;
    k=eri_data[cc].kl%N_cgtos;
    eri_ijkl=eri_data[cc].eri_ijkl;
 
    D_ij=D.get_value(i,j);  
    D_ik=D.get_value(i,k);    D_ki=D.get_value(k,i);
    D_jk=D.get_value(j,k);    D_kj=D.get_value(k,j);
    D_kl=D.get_value(k,l);  
    D_il=D.get_value(i,l);    D_li=D.get_value(l,i);
    D_jl=D.get_value(j,l);    D_lj=D.get_value(l,j);

    if(i==j && k==l){
      tmp_eri=2*D_kl*eri_ijkl;
      Vh.add(i,i,tmp_eri);
      tmp_eri_1 =-1*D_ik*eri_ijkl;
      tmp_eri_1b=-1*D_ki*eri_ijkl;
      Vx.add(i,k,tmp_eri_1);
      if(i!=k){
        tmp_eri=2*D_ij*eri_ijkl;
        Vh.add(k,k,tmp_eri);
        Vx.add(k,i,tmp_eri_1b);
      }
    }
    if(i!=j && k==l){
      tmp_eri=2*D_kl*eri_ijkl;
      Vh.add(i,j,tmp_eri);
      Vh.add(j,i,tmp_eri);
      tmp_eri_1 =-1*D_jk*eri_ijkl;
      tmp_eri_1b=-1*D_kj*eri_ijkl;
      Vx.add(i,l,tmp_eri_1);
      tmp_eri_2 =-1*D_ik*eri_ijkl;
      tmp_eri_2b=-1*D_ki*eri_ijkl;
      Vx.add(j,l,tmp_eri_2);
      if(i!=k){
        tmp_eri=4*D_ij*eri_ijkl;
        Vh.add(k,k,tmp_eri);
        Vx.add(k,i,tmp_eri_1b);
        Vx.add(k,j,tmp_eri_2b);
      }
    }
    if(i==j && k!=l){
      tmp_eri=4*D_kl*eri_ijkl;
      Vh.add(i,i,tmp_eri);
      tmp_eri_1 =-1*D_ik*eri_ijkl;
      tmp_eri_1b=-1*D_ki*eri_ijkl;
      Vx.add(i,l,tmp_eri_1);
      tmp_eri_2 =-1*D_il*eri_ijkl;
      tmp_eri_2b=-1*D_li*eri_ijkl;
      Vx.add(i,k,tmp_eri_2);
      if(i!=k){
        tmp_eri=2*D_ij*eri_ijkl;
        Vh.add(k,l,tmp_eri);
        Vh.add(l,k,tmp_eri);
        Vx.add(l,i,tmp_eri_1b);
        Vx.add(k,i,tmp_eri_2b);
      }
    }
    if(i!=j && k!=l){
      tmp_eri=4*D_kl*eri_ijkl;
      Vh.add(i,j,tmp_eri);
      Vh.add(j,i,tmp_eri);
      tmp_eri_1 =-1*D_jk*eri_ijkl;
      tmp_eri_1b=-1*D_kj*eri_ijkl;
      Vx.add(i,l,tmp_eri_1);
      tmp_eri_2 =-1*D_ik*eri_ijkl;
      tmp_eri_2b=-1*D_ki*eri_ijkl;
      Vx.add(j,l,tmp_eri_2);
      tmp_eri_3 =-1*D_jl*eri_ijkl;
      tmp_eri_3b=-1*D_lj*eri_ijkl;
      Vx.add(i,k,tmp_eri_3);
      tmp_eri_4 =-1*D_il*eri_ijkl;
      tmp_eri_4b=-1*D_li*eri_ijkl;
      Vx.add(j,k,tmp_eri_4);
      if(i!=k){
        tmp_eri=4*D_ij*eri_ijkl;
        Vh.add(k,l,tmp_eri);
        Vh.add(l,k,tmp_eri);
        Vx.add(l,i,tmp_eri_1b);
        Vx.add(l,j,tmp_eri_2b);
        Vx.add(k,i,tmp_eri_3b);
        Vx.add(k,j,tmp_eri_4b);
      }
    }
  }
}



template <typename M_tmpl,typename Integ2e> template <typename M_tmpl2>
void Fock2e_tmpl<M_tmpl,Integ2e>::cal_Vh_and_Vx_sub(M_tmpl2 &Vh, M_tmpl2 &Vx_a, M_tmpl2 &Vx_b, const M_tmpl &Da, const M_tmpl &Db,
                                                    const std::vector<ERI_data> &eri_data){

  int N_cgtos=Da.get_I();
  double Da_ij,Da_ik,Da_jk,Da_kl,Da_il,Da_jl;
  double Db_ij,Db_ik,Db_jk,Db_kl,Db_il,Db_jl;
  double Da_ki,Da_kj,Da_li,Da_lj;
  double Db_ki,Db_kj,Db_li,Db_lj;
  double tmp_eri,tmp_eri_1a, tmp_eri_2a, tmp_eri_3a, tmp_eri_4a;
  double         tmp_eri_1b, tmp_eri_2b, tmp_eri_3b, tmp_eri_4b;
  double         tmp_eri_1ax,tmp_eri_2ax,tmp_eri_3ax,tmp_eri_4ax;
  double         tmp_eri_1bx,tmp_eri_2bx,tmp_eri_3bx,tmp_eri_4bx;
  double eri_ijkl;
  int i,j,k,l;

  for(int cc=0;cc<eri_data.size();cc++){
    j=eri_data[cc].ij/N_cgtos;
    i=eri_data[cc].ij%N_cgtos;
    l=eri_data[cc].kl/N_cgtos;
    k=eri_data[cc].kl%N_cgtos;
    eri_ijkl=eri_data[cc].eri_ijkl;
 
    Da_ij=Da.get_value(i,j); 
    Da_ik=Da.get_value(i,k);    Da_ki=Da.get_value(k,i);
    Da_jk=Da.get_value(j,k);    Da_kj=Da.get_value(k,j);
    Da_kl=Da.get_value(k,l); 
    Da_il=Da.get_value(i,l);    Da_li=Da.get_value(l,i);
    Da_jl=Da.get_value(j,l);    Da_lj=Da.get_value(l,j);

    Db_ij=Db.get_value(i,j); 
    Db_ik=Db.get_value(i,k);    Db_ki=Db.get_value(k,i);
    Db_jk=Db.get_value(j,k);    Db_kj=Db.get_value(k,j);
    Db_kl=Db.get_value(k,l); 
    Db_il=Db.get_value(i,l);    Db_li=Db.get_value(l,i);
    Db_jl=Db.get_value(j,l);    Db_lj=Db.get_value(l,j);

    if(i==j && k==l){
      tmp_eri=(Da_kl+Db_kl)*eri_ijkl;
      Vh.add(i,i,tmp_eri);
      tmp_eri_1a =-1*Da_ik*eri_ijkl;
      tmp_eri_1ax=-1*Da_ki*eri_ijkl;
      tmp_eri_1b =-1*Db_ik*eri_ijkl;
      tmp_eri_1bx=-1*Db_ki*eri_ijkl;
      Vx_a.add(i,k,tmp_eri_1a);
      Vx_b.add(i,k,tmp_eri_1b);
      if(i!=k){
        tmp_eri=(Da_ij+Db_ij)*eri_ijkl;
        Vh.add(k,k,tmp_eri);
        Vx_a.add(k,i,tmp_eri_1ax);
        Vx_b.add(k,i,tmp_eri_1bx);
      }
    }
    if(i!=j && k==l){
      tmp_eri=(Da_kl+Db_kl)*eri_ijkl;
      Vh.add(i,j,tmp_eri);
      Vh.add(j,i,tmp_eri);
      tmp_eri_1a =-1*Da_jk*eri_ijkl;
      tmp_eri_1ax=-1*Da_kj*eri_ijkl;
      tmp_eri_1b =-1*Db_jk*eri_ijkl;
      tmp_eri_1bx=-1*Db_kj*eri_ijkl;
      Vx_a.add(i,l,tmp_eri_1a);
      Vx_b.add(i,l,tmp_eri_1b);
      tmp_eri_2a =-1*Da_ik*eri_ijkl;
      tmp_eri_2ax=-1*Da_ki*eri_ijkl;
      tmp_eri_2b =-1*Db_ik*eri_ijkl;
      tmp_eri_2bx=-1*Db_ki*eri_ijkl;
      Vx_a.add(j,l,tmp_eri_2a);
      Vx_b.add(j,l,tmp_eri_2b);
      if(i!=k){
        tmp_eri=2*(Da_ij+Db_ij)*eri_ijkl;
        Vh.add(k,k,tmp_eri);
        Vx_a.add(k,i,tmp_eri_1ax);
        Vx_a.add(k,j,tmp_eri_2ax);
        Vx_b.add(k,i,tmp_eri_1bx);
        Vx_b.add(k,j,tmp_eri_2bx);
      }
    }
    if(i==j && k!=l){
      tmp_eri=2*(Da_kl+Db_kl)*eri_ijkl;
      Vh.add(i,i,tmp_eri);
      tmp_eri_1a =-1*Da_ik*eri_ijkl;
      tmp_eri_1ax=-1*Da_ki*eri_ijkl;
      tmp_eri_1b =-1*Db_ik*eri_ijkl;
      tmp_eri_1bx=-1*Db_ki*eri_ijkl;
      Vx_a.add(i,l,tmp_eri_1a);
      Vx_b.add(i,l,tmp_eri_1b);
      tmp_eri_2a =-1*Da_il*eri_ijkl;
      tmp_eri_2ax=-1*Da_li*eri_ijkl;
      tmp_eri_2b =-1*Db_il*eri_ijkl;
      tmp_eri_2bx=-1*Db_li*eri_ijkl;
      Vx_a.add(i,k,tmp_eri_2a);
      Vx_b.add(i,k,tmp_eri_2b);
      if(i!=k){
        tmp_eri=(Da_ij+Db_ij)*eri_ijkl;
        Vh.add(k,l,tmp_eri);
        Vh.add(l,k,tmp_eri);
        Vx_a.add(l,i,tmp_eri_1ax);
        Vx_a.add(k,i,tmp_eri_2ax);
        Vx_b.add(l,i,tmp_eri_1bx);
        Vx_b.add(k,i,tmp_eri_2bx);
      }
    }
    if(i!=j && k!=l){
      tmp_eri=2*(Da_kl+Db_kl)*eri_ijkl;
      Vh.add(i,j,tmp_eri);
      Vh.add(j,i,tmp_eri);
      tmp_eri_1a =-1*Da_jk*eri_ijkl;
      tmp_eri_1ax=-1*Da_kj*eri_ijkl;
      tmp_eri_1b =-1*Db_jk*eri_ijkl;
      tmp_eri_1bx=-1*Db_kj*eri_ijkl;
      Vx_a.add(i,l,tmp_eri_1a);
      Vx_b.add(i,l,tmp_eri_1b);
      tmp_eri_2a =-1*Da_ik*eri_ijkl;
      tmp_eri_2ax=-1*Da_ki*eri_ijkl;
      tmp_eri_2b =-1*Db_ik*eri_ijkl;
      tmp_eri_2bx=-1*Db_ki*eri_ijkl;
      Vx_a.add(j,l,tmp_eri_2a);
      Vx_b.add(j,l,tmp_eri_2b);
      tmp_eri_3a =-1*Da_jl*eri_ijkl;
      tmp_eri_3ax=-1*Da_lj*eri_ijkl;
      tmp_eri_3b =-1*Db_jl*eri_ijkl;
      tmp_eri_3bx=-1*Db_lj*eri_ijkl;
      Vx_a.add(i,k,tmp_eri_3a);
      Vx_b.add(i,k,tmp_eri_3b);
      tmp_eri_4a =-1*Da_il*eri_ijkl;
      tmp_eri_4ax=-1*Da_li*eri_ijkl;
      tmp_eri_4b =-1*Db_il*eri_ijkl;
      tmp_eri_4bx=-1*Db_li*eri_ijkl;
      Vx_a.add(j,k,tmp_eri_4a);
      Vx_b.add(j,k,tmp_eri_4b);
      if(i!=k){
        tmp_eri=2*(Da_ij+Db_ij)*eri_ijkl;
        Vh.add(k,l,tmp_eri);
        Vh.add(l,k,tmp_eri);
        Vx_a.add(l,i,tmp_eri_1ax);
        Vx_a.add(l,j,tmp_eri_2ax);
        Vx_a.add(k,i,tmp_eri_3ax);
        Vx_a.add(k,j,tmp_eri_4ax);
        Vx_b.add(l,i,tmp_eri_1bx);
        Vx_b.add(l,j,tmp_eri_2bx);
        Vx_b.add(k,i,tmp_eri_3bx);
        Vx_b.add(k,j,tmp_eri_4bx);
      }
    }
  }
}


template <typename M_tmpl,typename Integ2e>
void Fock2e_tmpl<M_tmpl,Integ2e>::cal_cutoffD(M_tmpl &cutoffDa, M_tmpl &cutoffDb, const M_tmpl &Da, const M_tmpl &Db,
                                              const std::vector<Shell_Cgto> &scgtos)
{

  int N_scgtos=scgtos.size();
  cutoffDa.set_IJ(N_scgtos, N_scgtos);
  if(_mode_u==Fock2e_Enum::Unrestricted) cutoffDb.set_IJ(N_scgtos, N_scgtos);
  for(int p=0;p<N_scgtos;p++){
    for(int q=0;q<N_scgtos;q++){
      double max_pq_a=0.0;
      double max_pq_b=0.0;
      for(int i=scgtos[p].get_min_cgto_no();i<=scgtos[p].get_max_cgto_no();i++){
        for(int j=scgtos[q].get_min_cgto_no();j<=scgtos[q].get_max_cgto_no();j++){
          if(max_pq_a<fabs(Da.get_value(i, j))) max_pq_a=fabs(Da.get_value(i, j));
          if(_mode_u==Fock2e_Enum::Unrestricted && max_pq_b<fabs(Db.get_value(i, j)) ) max_pq_b=fabs(Db.get_value(i, j));
        }
      }
      cutoffDa.set_value(p, q, max_pq_a);
      if(_mode_u==Fock2e_Enum::Unrestricted) cutoffDb.set_value(p, q, max_pq_a);
    }
  }
}

template <typename M_tmpl,typename Integ2e>
bool Fock2e_tmpl<M_tmpl,Integ2e>::check_cutoffD(int p, int q, int r, int s, const M_tmpl &cutoffD)
{
  bool ret=false;
  // Hartree
  double v_pp = fabs( cutoffD.get_value(p,p) );
  double v_pq = fabs( cutoffD.get_value(p,q) );
  double v_qp = fabs( cutoffD.get_value(q,p) );
  double v_rr = fabs( cutoffD.get_value(r,r) );
  double v_rs = fabs( cutoffD.get_value(r,s) );
  double v_sr = fabs( cutoffD.get_value(s,r) );
  if( v_pp>CUTOFF_Fock2e || v_pq>CUTOFF_Fock2e || v_qp>CUTOFF_Fock2e ||
      v_rr>CUTOFF_Fock2e || v_rs>CUTOFF_Fock2e || v_sr>CUTOFF_Fock2e) ret=true; 
  // Exchange 
  double v_pr = fabs( cutoffD.get_value(p,r) );
  double v_ps = fabs( cutoffD.get_value(p,s) );
  double v_qr = fabs( cutoffD.get_value(q,r) );
  double v_qs = fabs( cutoffD.get_value(q,s) );
  double v_rp = fabs( cutoffD.get_value(r,p) );
  double v_rq = fabs( cutoffD.get_value(r,q) );
  double v_sp = fabs( cutoffD.get_value(s,p) );
  double v_sq = fabs( cutoffD.get_value(s,q) );
  if( v_pr>CUTOFF_Fock2e || v_ps>CUTOFF_Fock2e || v_qr>CUTOFF_Fock2e || v_qs>CUTOFF_Fock2e ||
      v_rp>CUTOFF_Fock2e || v_rq>CUTOFF_Fock2e || v_sp>CUTOFF_Fock2e || v_sq>CUTOFF_Fock2e) ret=true;  
  return ret;
}

template <typename M_tmpl,typename Integ2e>
bool Fock2e_tmpl<M_tmpl,Integ2e>::check_cutoffD_ab(int p, int q, int r, int s, const M_tmpl &cutoffDa, const M_tmpl &cutoffDb)
{
  bool check_a = check_cutoffD(p, q, r, s, cutoffDa);
  bool check_b = false;
  if(_mode_u==Fock2e_Enum::Unrestricted) check_b = check_cutoffD(p, q, r, s, cutoffDb);
  bool ret=false;
  if(check_a==true) ret=true;
  if(check_b==true) ret=true;
  return ret;
}


template <typename M_tmpl,typename Integ2e>
void Fock2e_tmpl<M_tmpl,Integ2e>::cal_Vh_and_Vx_base(M_tmpl &Vh, M_tmpl &Vx_a, M_tmpl &Vx_b, const M_tmpl &Da, const M_tmpl &Db,
                                                     const std::vector<Shell_Cgto> &scgtos){

  int N_process=1;
  int process_num=0;
  Util_MPI::get_size_rank(N_process,process_num);

  if(_mode!=Fock2e_Enum::Normal && process_num==0)  cout<<"    debug mode_erfc "<<_mode<<" omega "<<_omega<<endl;

  int N_scgtos=scgtos.size();
  int N_cgtos =Util_GTO::get_N_cgtos(scgtos);

  // set zero 
  Vh.set_IJ(N_cgtos,N_cgtos);
  Vx_a.set_IJ(N_cgtos,N_cgtos);
  if(_mode_u==Fock2e_Enum::Unrestricted) Vx_b.set_IJ(N_cgtos,N_cgtos);
  else                                   Vx_b.set_IJ(1,1);

  //  set cutoffM
  M_tmpl cutoffM;
  Fock2e_tmpl<M_tmpl,Integ2e>::cal_cutoffM(cutoffM,scgtos);

  //  set cutoffD
  M_tmpl cutoffDa, cutoffDb;
  cal_cutoffD(cutoffDa, cutoffDb, Da, Db, scgtos);

  // copy scgtos
  std::vector<Shell_Cgto> cp_scgtos;
  for(int i=0;i<N_scgtos;i++){  cp_scgtos.push_back(scgtos[i]);  cp_scgtos[i].set_dI<Integ2e>(); }

  time_t start_a,stop_a;
  time(&start_a);

  #ifdef _OPENMP
  #pragma omp parallel
  {  // start of openMP parallel-loop
  int N_threads =omp_get_num_threads();
  int thread_num=omp_get_thread_num();
  #else
  int N_threads =1;
  int thread_num=0;
  #endif

  std::vector<double>   eri_shell;
  std::vector<ERI_data> eri_data;
  eri_data.clear();

  if(thread_num==0 && process_num==0) 
    cout<<"    cal_Vh_and_Vx(direct, N_process="<<N_process<<", N_threads="<<N_threads<<") "<<flush;
  for(int p=0;p<N_scgtos;p++){
    if(thread_num==0 && process_num==0) cout<<p<<" "<<flush;
    for(int q=p;q<N_scgtos;q++){
      if((q*N_scgtos+p)%N_process==process_num){ // mpi
        #ifdef _OPENMP
        #pragma omp for schedule(dynamic)
        #endif
        for(int r=p;r<N_scgtos;r++){
          for(int s=r;s<N_scgtos;s++){
            double v_cutoff=cutoffM.get_value(p,q)*cutoffM.get_value(r,s);
            bool check_ab = check_cutoffD_ab(p, q, r, s, cutoffDa, cutoffDb);
            if(v_cutoff>CUTOFF_Fock2e && check_ab==true){
              cal_eri_shell(eri_shell,p,q,r,s,cp_scgtos);
              set_data_eri(eri_data,p,q,r,s,scgtos,eri_shell);
            }  
          }  
          #ifdef _OPENMP
          #pragma omp critical(mat_add)
          #endif
          { 
            int N_eri_data=eri_data.size(); 
            if(N_eri_data>0){
              if(_mode_u==Fock2e_Enum::Restricted){
                cal_Vh_and_Vx_sub(Vh,Vx_a,Da,eri_data);
              }else{ 
                cal_Vh_and_Vx_sub(Vh,Vx_a,Vx_b,Da,Db,eri_data); 
              }
              eri_data.clear();
            } 
          }
        }  
      }  
    }
  }

  #ifdef _OPENMP
  } // end of openMP parallel-loop
  #endif


  time(&stop_a);
  if(process_num==0) cout<<"  time: "<<difftime(stop_a,start_a)<<endl;

  #ifdef USE_MPI_LOTUS
  if(_mode_u==Fock2e_Enum::Restricted){
//    Util_MPI::allreduce(Vh);
//    Util_MPI::allreduce(Vx_a);
    Util_MPI::isendrecv(Vh);
    Util_MPI::isendrecv(Vx_a);
  }else{
//    Util_MPI::allreduce(Vh);
//    Util_MPI::allreduce(Vx_a);
//    Util_MPI::allreduce(Vx_b);
    Util_MPI::isendrecv(Vh);
    Util_MPI::isendrecv(Vx_a);
    Util_MPI::isendrecv(Vx_b);
  }
  #endif

}




//  store_eri_to_file 
template <typename M_tmpl,typename Integ2e>
void Fock2e_tmpl<M_tmpl,Integ2e>::store_eri_to_file(const ERI_file &eri_file,const std::vector<Shell_Cgto> &scgtos){
                               
  using namespace std;

  _mode=eri_file.get_mode(); _omega=eri_file.get_omega();

  int N_process=1;
  int process_num=0;
  Util_MPI::get_size_rank(N_process,process_num);

  // save file
  string prefix = eri_file.get_filename();

  if(process_num==0)  cout<<"    file_prefix "<<prefix<<" mode "<<_mode<<" omega "<<_omega<<endl;

  int N_scgtos = (int)scgtos.size();
 
  //  set cutoffM
  M_tmpl cutoffM;
  cal_cutoffM(cutoffM,scgtos);

  time_t start_a,stop_a;
  time(&start_a);


  std::vector<Shell_Cgto> cp_scgtos;
  for(int i=0;i<N_scgtos;i++){  cp_scgtos.push_back(scgtos[i]);  cp_scgtos[i].set_dI<Integ2e>(); }

  #ifdef _OPENMP
  #pragma omp parallel
  {  // start of openMP parallel-loop
  int N_threads =omp_get_num_threads();
  int thread_num=omp_get_thread_num();
  #else
  int N_threads =1;
  int thread_num=0;
  #endif

  std::vector<double>   eri_shell;
  std::vector<ERI_data> eri_data;
  eri_data.clear();

  //  prepare for file
  ofstream fout;
  const int io_buff_size=200000;
  char io_buff[io_buff_size];
  char buff[10];
  sprintf(buff,"%d",thread_num);
  string filename=prefix+string(buff); 
  fout.rdbuf()->pubsetbuf(io_buff,io_buff_size);
  fout.open(filename.c_str(),ios::binary);

  std::vector<double>   tmp_eri, dI_1, dI_2, dI_3, dI_4;
  CTRL_PBC dmy_ctrl_pbc;
  std::vector<int> Q_q(3,0), Q_r(3,0), Q_s(3,0);

  // write data to file
  int flush_cc=0;
  if(thread_num==0 && process_num==0) 
    cout<<"    store_eri_to_file(N_process="<<N_process<<", N_threads="<<N_threads<<") "<<prefix<<" : "<<flush;
  for(int p=0;p<N_scgtos;p++){
    if(thread_num==0 && process_num==0) cout<<p<<" "<<flush;
    for(int q=p;q<N_scgtos;q++){
      if((q*N_scgtos+p)%N_process==process_num){ // mpi
        #ifdef _OPENMP
        #pragma omp for schedule(dynamic)
        #endif
        for(int r=p;r<N_scgtos;r++){
          for(int s=r;s<N_scgtos;s++){
            double v_cutoff=cutoffM.get_value(p,q)*cutoffM.get_value(r,s);
            if(v_cutoff>CUTOFF_Fock2e){
              cal_eri_shell(eri_shell,p,q,r,s,cp_scgtos);
              set_data_eri(eri_data,p,q,r,s,scgtos,eri_shell);
            }  
          }  
          // write eri for save file
          int num_data=eri_data.size();
          if(num_data>0){
            fout.write((char*)&num_data,sizeof(int));
            for(int w=0;w<num_data;w++){
              fout.write((char*)&eri_data[w].ij,sizeof(int));
              fout.write((char*)&eri_data[w].kl,sizeof(int));
              fout.write((char*)&eri_data[w].eri_ijkl,sizeof(double));
            }
            eri_data.clear();
            if(flush_cc==10000){  fout<<flush;  flush_cc=0; }
            flush_cc++;
          }
        }  
      }  
    }
  }

  // save file
  int num_data=-1;
  fout.write((char*)&num_data,sizeof(int));
  fout.close();

  #ifdef _OPENMP
  } // end of openMP parallel-loop
  #endif

  time(&stop_a);
  if(process_num==0) cout<<"  time: "<<difftime(stop_a,start_a)<<endl;

  set_mode_clear();

}



//  cal_Vh_and_Vx
template <typename M_tmpl,typename Integ2e> //template <typename M_tmpl2>
void Fock2e_tmpl<M_tmpl,Integ2e>::cal_Vh_and_Vx_from_file_base(M_tmpl &Vh, M_tmpl &Vx_a, M_tmpl &Vx_b, const M_tmpl &Da, const M_tmpl &Db,
                                                               const std::vector<Shell_Cgto> &scgtos, const ERI_file &eri_file){

  int N_process=1;
  int process_num=0;
  Util_MPI::get_size_rank(N_process,process_num);

  // save file
  string prefix = eri_file.get_filename();

  int N_cgtos =Util_GTO::get_N_cgtos(scgtos);
  
  // set zero 
  Vh.set_IJ(N_cgtos,N_cgtos);
  Vx_a.set_IJ(N_cgtos,N_cgtos);
  if(_mode_u==Fock2e_Enum::Unrestricted) Vx_b.set_IJ(N_cgtos,N_cgtos);
  else                                   Vx_b.set_IJ(1,1);

  time_t start_a,stop_a;
  time(&start_a);

  #ifdef _OPENMP
  #pragma omp parallel
  {  // start of openMP parallel-loop
  int N_threads =omp_get_num_threads();
  int thread_num=omp_get_thread_num();
  #else
  int N_threads =1;
  int thread_num=0;
  #endif

  std::vector<ERI_data> eri_data;
  eri_data.clear();

  //  prepare for file
  ifstream fin;
  const int io_buff_size=200000;
  char io_buff[io_buff_size];
  char buff[10];
  sprintf(buff,"%d",thread_num);
  string filename=prefix+string(buff); 
  fin.rdbuf()->pubsetbuf(io_buff,io_buff_size);
  fin.open(filename.c_str(),ios::binary);

  // read data from save file
  if(thread_num==0 && process_num==0)  
    cout<<"    cal_Vh_and_Vx_from_file(N_process="<<N_process<<", N_threads="<<N_threads<<" : "<<prefix<<" ... ";
   
  M_tmpl omp_Vh,omp_Vx_a,omp_Vx_b;
  omp_Vh.set_IJ(N_cgtos,N_cgtos);
  omp_Vx_a.set_IJ(N_cgtos,N_cgtos);
  if(_mode_u==Fock2e_Enum::Unrestricted) omp_Vx_b.set_IJ(N_cgtos,N_cgtos);

  for(;;){
    int num_data,tmp_ij,tmp_kl;
    double tmp_eri;
    fin.read((char*)&num_data,sizeof(int));
    if(num_data<0) break;
    for(int w=0;w<num_data;w++){
      fin.read((char*)&tmp_ij,sizeof(int));
      fin.read((char*)&tmp_kl,sizeof(int));
      fin.read((char*)&tmp_eri,sizeof(double));
      eri_data.push_back(ERI_data(tmp_ij,tmp_kl,tmp_eri));
    }
    if(_mode_u==Fock2e_Enum::Restricted){
      cal_Vh_and_Vx_sub(omp_Vh,omp_Vx_a,Da,eri_data); 
    }else{
      cal_Vh_and_Vx_sub(omp_Vh,omp_Vx_a,omp_Vx_b,Da,Db,eri_data); 
    }
    eri_data.clear();
  }

  #ifdef _OPENMP
  #pragma omp critical(mat_add)
  #endif
  {
    for(int i=0;i<N_cgtos;i++){
      for(int j=0;j<N_cgtos;j++){
        Vh.add(i,j,omp_Vh.get_value(i,j));
        Vx_a.add(i,j,omp_Vx_a.get_value(i,j));
        if(_mode_u==Fock2e_Enum::Unrestricted) Vx_b.add(i,j,omp_Vx_b.get_value(i,j));
      }
    }
  }

  fin.close();
  #ifdef _OPENMP
  } // end of openMP parallel-loop
  #endif

  time(&stop_a);
  if(process_num==0) cout<<"  time: "<<difftime(stop_a,start_a)<<endl;

  #ifdef USE_MPI_LOTUS
  if(_mode_u==Fock2e_Enum::Restricted){
//    Util_MPI::allreduce(Vh);
//    Util_MPI::allreduce(Vx_a);
    Util_MPI::isendrecv(Vh);
    Util_MPI::isendrecv(Vx_a);
  }else{
//    Util_MPI::allreduce(Vh);
//    Util_MPI::allreduce(Vx_a);
//    Util_MPI::allreduce(Vx_b);
    Util_MPI::isendrecv(Vh);
    Util_MPI::isendrecv(Vx_a);
    Util_MPI::isendrecv(Vx_b);
  }
  #endif

}



//  store_eri_to_incore
template <typename M_tmpl,typename Integ2e>
void Fock2e_tmpl<M_tmpl,Integ2e>::store_eri_to_incore(ERI_incore &eri_incore,const std::vector<Shell_Cgto> &scgtos){

  using namespace std;
                                
  _mode=eri_incore.get_mode();; _omega=eri_incore.get_omega();

  int N_process=1;
  int process_num=0;
  Util_MPI::get_size_rank(N_process,process_num);

  if(process_num==0)  cout<<"    mode "<<_mode<<" omega "<<_omega<<endl;

  int N_scgtos = (int)scgtos.size();
 
  //  set cutoffM
  M_tmpl cutoffM;
  cal_cutoffM(cutoffM,scgtos);

  time_t start_a,stop_a;
  time(&start_a);

  // copy scgtos
  std::vector<Shell_Cgto> cp_scgtos;
  for(int i=0;i<N_scgtos;i++){  cp_scgtos.push_back(scgtos[i]);  cp_scgtos[i].set_dI<Integ2e>(); }

  #ifdef _OPENMP
  #pragma omp parallel
  {  // start of openMP parallel-loop
  int N_threads =omp_get_num_threads();
  int thread_num=omp_get_thread_num();
  #else
  int N_threads =1;
  int thread_num=0;
  #endif

  if(thread_num==0)  eri_incore.set_omp_N_threads(N_threads);
  #ifdef _OPENMP
  #pragma omp barrier
  #endif


  std::vector<double>   eri_shell;
  std::vector<ERI_data> eri_data;
  eri_data.clear();

  std::vector<double>   tmp_eri, dI_1, dI_2, dI_3, dI_4;
  CTRL_PBC dmy_ctrl_pbc;
  std::vector<int> Q_q(3,0), Q_r(3,0), Q_s(3,0);

  // write data to file
  if(thread_num==0 && process_num==0) 
    cout<<"    store_eri_to_incore(memory, N_process="<<N_process<<", N_threads="<<N_threads<<") : "<<flush;
  for(int p=0;p<N_scgtos;p++){
    if(thread_num==0 && process_num==0) cout<<p<<" "<<flush;
    for(int q=p;q<N_scgtos;q++){
      if((q*N_scgtos+p)%N_process==process_num){ // mpi
        #ifdef _OPENMP
        #pragma omp for schedule(dynamic)
        #endif
        for(int r=p;r<N_scgtos;r++){
          for(int s=r;s<N_scgtos;s++){
            double v_cutoff=cutoffM.get_value(p,q)*cutoffM.get_value(r,s);
            if(v_cutoff>CUTOFF_Fock2e){
              cal_eri_shell(eri_shell,p,q,r,s,cp_scgtos);
              set_data_eri(eri_data,p,q,r,s,scgtos,eri_shell);
            }  
          }  
          // write eri for save file
          int num_data=eri_data.size();
          for(int w=0;w<num_data;w++){
            eri_incore.set_data(thread_num,eri_data[w]);
          }
          eri_data.clear();
        }  
      }  
    }
  }


  #ifdef _OPENMP
  } // end of openMP parallel-loop
  #endif

  time(&stop_a);
  if(process_num==0) cout<<"  time: "<<difftime(stop_a,start_a)<<endl;

  set_mode_clear();
}



//  cal_Vh_and_Vx
template <typename M_tmpl,typename Integ2e> // template <typename M_tmpl2>
void Fock2e_tmpl<M_tmpl,Integ2e>::cal_Vh_and_Vx_from_incore_base(M_tmpl &Vh, M_tmpl &Vx_a, M_tmpl &Vx_b, const M_tmpl &Da, const M_tmpl &Db,
                                                                 const std::vector<Shell_Cgto> &scgtos, const ERI_incore &eri_incore){

  ERI_incore *ptr_eri_incore = const_cast<ERI_incore*>(&eri_incore);


  int N_process=1;
  int process_num=0;
  Util_MPI::get_size_rank(N_process,process_num);

  int N_cgtos =Util_GTO::get_N_cgtos(scgtos);

  // set zero 
  Vh.set_IJ(N_cgtos,N_cgtos);
  Vx_a.set_IJ(N_cgtos,N_cgtos);
  if(_mode_u==Fock2e_Enum::Unrestricted) Vx_b.set_IJ(N_cgtos,N_cgtos);
  else                                  Vx_b.set_IJ(1,1);

  time_t start_a,stop_a;
  time(&start_a);

  #ifdef _OPENMP
  #pragma omp parallel
  {  // start of openMP parallel-loop
  int N_threads =omp_get_num_threads();
  int thread_num=omp_get_thread_num();
  #else
  int N_threads =1;
  int thread_num=0;
  #endif

  std::vector<ERI_data> eri_data;
  eri_data.clear();

  // read data from save file
  if(thread_num==0 && process_num==0) 
     cout<<"    cal_Vh_and_Vx_from_incore(N_process="<<N_process<<", N_threads="<<N_threads<<") :  ... ";
   
  M_tmpl omp_Vh,omp_Vx_a,omp_Vx_b;
  omp_Vh.set_IJ(N_cgtos,N_cgtos);
  omp_Vx_a.set_IJ(N_cgtos,N_cgtos);
  if(_mode_u==Fock2e_Enum::Unrestricted) omp_Vx_b.set_IJ(N_cgtos,N_cgtos);

  if(_mode_u==Fock2e_Enum::Restricted){
    cal_Vh_and_Vx_sub(omp_Vh,omp_Vx_a,Da,*(ptr_eri_incore->get_ptr_eri_data(thread_num))); 
  }else{
    cal_Vh_and_Vx_sub(omp_Vh,omp_Vx_a,omp_Vx_b,Da,Db,*(ptr_eri_incore->get_ptr_eri_data(thread_num))); 
  }
  
  #ifdef _OPENMP
  #pragma omp critical(mat_add)
  #endif
  {
    for(int i=0;i<N_cgtos;i++){
      for(int j=0;j<N_cgtos;j++){
        Vh.add(i,j,omp_Vh.get_value(i,j));
        Vx_a.add(i,j,omp_Vx_a.get_value(i,j));
        if(_mode_u==Fock2e_Enum::Unrestricted) Vx_b.add(i,j,omp_Vx_b.get_value(i,j));
      }
    }
  }

  #ifdef _OPENMP
  } // end of openMP parallel-loop
  #endif

  time(&stop_a);
  if(process_num==0) cout<<"  time: "<<difftime(stop_a,start_a)<<endl;

  #ifdef USE_MPI_LOTUS
  if(_mode_u==Fock2e_Enum::Restricted){
//    Util_MPI::allreduce(Vx_a);
    Util_MPI::isendrecv(Vh);
    Util_MPI::isendrecv(Vx_a);
  }else{
//    Util_MPI::allreduce(Vh);
//    Util_MPI::allreduce(Vx_a);
//    Util_MPI::allreduce(Vx_b);
    Util_MPI::isendrecv(Vh);
    Util_MPI::isendrecv(Vx_a);
    Util_MPI::isendrecv(Vx_b);
  }
  #endif

}


//
//
//




//
//  Gradient
//

template <typename M_tmpl,typename Integ2e>
void Fock2e_tmpl<M_tmpl,Integ2e>::cal_grad_shell(std::vector<double> &ret_grad_shell, int p, int q, int r, int s,
                                                 const std::vector<Shell_Cgto> &scgtos)
{
                                                 

  double Rp[3], Rq[3], Rr[3], Rs[3];
  scgtos[p].get_R_array(Rp);
  scgtos[q].get_R_array(Rq);
  scgtos[r].get_R_array(Rr);
  scgtos[s].get_R_array(Rs);

  int tn_p=scgtos[p].get_max_tn();
  int tn_q=scgtos[q].get_max_tn();
  int tn_r=scgtos[r].get_max_tn();
  int tn_s=scgtos[s].get_max_tn();
  int tn=tn_p+tn_q+tn_r+tn_s;

  int n_cgto_pqrs=cal_n_cgto_pqrs(scgtos,p,q,r,s);
  ret_grad_shell.reserve(n_cgto_pqrs*12);
  ret_grad_shell.clear();
  for(int i=0;i<12*n_cgto_pqrs;i++) ret_grad_shell.push_back(0.0);

  std::vector<double> tmp_grad;
  std::vector<double> dI_1, dI_2, dI_3, dI_4;

  //
  // loop for pgto
  Integ2e pint2e;
  pint2e.grad_init(tn_p, tn_q, tn_r, tn_s);
  for(int a=0;a<scgtos[p].get_num_pgto();a++){
    scgtos[p].get_dI(dI_1,a);
    double g_a = scgtos[p].get_nth_g(a);
    for(int b=0;b<scgtos[q].get_num_pgto();b++){
      scgtos[q].get_dI(dI_2,b);
      double g_b = scgtos[q].get_nth_g(b);
      pint2e.set_gR_12(g_a, Rp, g_b, Rq);
      for(int c=0;c<scgtos[r].get_num_pgto();c++){
        scgtos[r].get_dI(dI_3,c);
        double g_c = scgtos[r].get_nth_g(c);
        for(int d=0;d<scgtos[s].get_num_pgto();d++){
          scgtos[s].get_dI(dI_4,d);
          double g_d = scgtos[s].get_nth_g(d);
          pint2e.set_gR_34(g_c, Rr, g_d, Rs);
          pint2e.set_eri_ssss(tn+1,_mode,_omega);
          pint2e.grad_ERI(tmp_grad,tn_p,tn_q,tn_r,tn_s,dI_1,dI_2,dI_3,dI_4);
          for(int i=0;i<12*n_cgto_pqrs;i++) ret_grad_shell[i]+=tmp_grad[i];
        }
      }
    } 
  }
  pint2e.grad_finalize(tn_p, tn_q, tn_r, tn_s);

}


template <typename M_tmpl,typename Integ2e>
void Fock2e_tmpl<M_tmpl,Integ2e>::set_data_grad(std::vector<GRAD_data> &ret_grad_data,int p,int q,int r,int s,
                                               const std::vector<Shell_Cgto> &scgtos,const std::vector<double> &grad_shell)
{
                                                
  ret_grad_data.clear();

  int N_cgtos=Util_GTO::get_N_cgtos(scgtos);

  int min_i=scgtos[p].get_min_cgto_no();
  int min_j=scgtos[q].get_min_cgto_no();
  int min_k=scgtos[r].get_min_cgto_no();
  int min_l=scgtos[s].get_min_cgto_no();
  int max_i=scgtos[p].get_max_cgto_no();
  int max_j=scgtos[q].get_max_cgto_no();
  int max_k=scgtos[r].get_max_cgto_no();
  int max_l=scgtos[s].get_max_cgto_no();

  //
  //  for gradient
  //
  int cc_for_eri_ijkl=0;
  for(int i=min_i;i<=max_i;i++){
    for(int j=min_j;j<=max_j;j++){
      for(int k=min_k;k<=max_k;k++){
        for(int l=min_l;l<=max_l;l++){
          if(j>=i && l>=k && k>=i){
            if(i==k && j>l){   // do nothing
            }else{

              int write_ij=i+j*N_cgtos;
              int write_kl=k+l*N_cgtos;
              double write_XYZ[3];
              int tmp_atom_no[4],check_write_deri[4];
              //
              //  for gradient
              for(int deri_n=0;deri_n<4;deri_n++) check_write_deri[deri_n]=1;
              tmp_atom_no[0]=scgtos[p].get_atom_no();
              tmp_atom_no[1]=scgtos[q].get_atom_no();
              tmp_atom_no[2]=scgtos[r].get_atom_no();
              tmp_atom_no[3]=scgtos[s].get_atom_no();
              for(int deri_n=0;deri_n<4;deri_n++){
                write_XYZ[0]=grad_shell[cc_for_eri_ijkl*3*4+0*4+deri_n];
                write_XYZ[1]=grad_shell[cc_for_eri_ijkl*3*4+1*4+deri_n];
                write_XYZ[2]=grad_shell[cc_for_eri_ijkl*3*4+2*4+deri_n];
                for(int deri_i=deri_n+1;deri_i<4;deri_i++){
                  if(tmp_atom_no[deri_n]==tmp_atom_no[deri_i] && check_write_deri[deri_i]==1){
                    check_write_deri[deri_i]=0;
                    write_XYZ[0]+=grad_shell[cc_for_eri_ijkl*3*4+0*4+deri_i];
                    write_XYZ[1]+=grad_shell[cc_for_eri_ijkl*3*4+1*4+deri_i];
                    write_XYZ[2]+=grad_shell[cc_for_eri_ijkl*3*4+2*4+deri_i];
                  }
                }

                if(check_write_deri[deri_n]==1){
                  if(fabs(write_XYZ[0])>CUTOFF_Fock2e || fabs(write_XYZ[1])>CUTOFF_Fock2e || fabs(write_XYZ[2])>CUTOFF_Fock2e){
                    if(i==k && j<l){
                      ret_grad_data.push_back(GRAD_data(tmp_atom_no[deri_n],write_ij,write_kl,write_XYZ));
                      ret_grad_data.push_back(GRAD_data(tmp_atom_no[deri_n],write_kl,write_ij,write_XYZ));
                    }else{
                      ret_grad_data.push_back(GRAD_data(tmp_atom_no[deri_n],write_ij,write_kl,write_XYZ));
                    } 
                  }

                }
              }
              //
              //

            }
          }
          cc_for_eri_ijkl++; 
        }
      }
    }
  }

}



template <typename M_tmpl,typename Integ2e> 
void Fock2e_tmpl<M_tmpl,Integ2e>::cal_gradient_sub(std::vector<double> &ret_grad_h,std::vector<double> &ret_grad_x,const M_tmpl &D,
                                                   const std::vector<GRAD_data> &grad_data)
{
  int N_cgtos=D.get_I();

  for(int cc=0;cc<grad_data.size();cc++){
    int j  = grad_data[cc].ij/N_cgtos; 
    int i  = grad_data[cc].ij%N_cgtos;
    int l  = grad_data[cc].kl/N_cgtos; 
    int k  = grad_data[cc].kl%N_cgtos;
    int an = grad_data[cc].atom_no;
    double gX=grad_data[cc].grad_ijkl[0];
    double gY=grad_data[cc].grad_ijkl[1];
    double gZ=grad_data[cc].grad_ijkl[2];

    double D_ij,D_kl,D_il,D_kj,D_ki,D_jl; 
    double DD_ijkl,DD_ilkj,DD_jlki;
    D_ij=D.get_value(i,j);  D_kl=D.get_value(k,l);  D_il=D.get_value(i,l);
    D_kj=D.get_value(k,j);  D_jl=D.get_value(j,l);  D_ki=D.get_value(k,i);
    DD_ijkl=D_ij*D_kl;  DD_ilkj=D_il*D_kj;  DD_jlki=D_jl*D_ki;

    if(i==j && k==l){
      ret_grad_h[an*3+0]+=     DD_ijkl*gX;  ret_grad_h[an*3+1]+=     DD_ijkl*gY;  ret_grad_h[an*3+2]+=     DD_ijkl*gZ;
      ret_grad_x[an*3+0]+=-0.5*DD_ilkj*gX;  ret_grad_x[an*3+1]+=-0.5*DD_ilkj*gY;  ret_grad_x[an*3+2]+=-0.5*DD_ilkj*gZ;
      if(i!=k){
        ret_grad_h[an*3+0]+=     DD_ijkl*gX;  ret_grad_h[an*3+1]+=     DD_ijkl*gY;  ret_grad_h[an*3+2]+=     DD_ijkl*gZ;
        ret_grad_x[an*3+0]+=-0.5*DD_ilkj*gX;  ret_grad_x[an*3+1]+=-0.5*DD_ilkj*gY;  ret_grad_x[an*3+2]+=-0.5*DD_ilkj*gZ;
      }
    }
    if(i!=j && k==l){
      ret_grad_h[an*3+0]+= 2.0*DD_ijkl*gX;  ret_grad_h[an*3+1]+= 2.0*DD_ijkl*gY;  ret_grad_h[an*3+2]+= 2.0*DD_ijkl*gZ;
      ret_grad_x[an*3+0]+=-1.0*DD_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DD_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DD_ilkj*gZ;
      if(i!=k){
        ret_grad_h[an*3+0]+= 2.0*DD_ijkl*gX;  ret_grad_h[an*3+1]+= 2.0*DD_ijkl*gY;  ret_grad_h[an*3+2]+= 2.0*DD_ijkl*gZ;
        ret_grad_x[an*3+0]+=-1.0*DD_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DD_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DD_ilkj*gZ;
      }
    }
    if(i==j && k!=l){
      ret_grad_h[an*3+0]+= 2.0*DD_ijkl*gX;  ret_grad_h[an*3+1]+= 2.0*DD_ijkl*gY;  ret_grad_h[an*3+2]+= 2.0*DD_ijkl*gZ;
      ret_grad_x[an*3+0]+=-1.0*DD_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DD_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DD_ilkj*gZ;
      if(i!=k){
        ret_grad_h[an*3+0]+= 2.0*DD_ijkl*gX;  ret_grad_h[an*3+1]+= 2.0*DD_ijkl*gY;  ret_grad_h[an*3+2]+= 2.0*DD_ijkl*gZ;
        ret_grad_x[an*3+0]+=-1.0*DD_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DD_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DD_ilkj*gZ;
      }
    }

    if(i!=j && k!=l){
      ret_grad_h[an*3+0]+= 4.0*DD_ijkl*gX;  ret_grad_h[an*3+1]+= 4.0*DD_ijkl*gY;  ret_grad_h[an*3+2]+= 4.0*DD_ijkl*gZ;
      ret_grad_x[an*3+0]+=-1.0*DD_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DD_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DD_ilkj*gZ;
      ret_grad_x[an*3+0]+=-1.0*DD_jlki*gX;  ret_grad_x[an*3+1]+=-1.0*DD_jlki*gY;  ret_grad_x[an*3+2]+=-1.0*DD_jlki*gZ;
      if(i!=k){
        ret_grad_h[an*3+0]+= 4.0*DD_ijkl*gX;  ret_grad_h[an*3+1]+= 4.0*DD_ijkl*gY;  ret_grad_h[an*3+2]+= 4.0*DD_ijkl*gZ;
        ret_grad_x[an*3+0]+=-1.0*DD_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DD_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DD_ilkj*gZ;
        ret_grad_x[an*3+0]+=-1.0*DD_jlki*gX;  ret_grad_x[an*3+1]+=-1.0*DD_jlki*gY;  ret_grad_x[an*3+2]+=-1.0*DD_jlki*gZ;
      }
    }
  }

}



template <typename M_tmpl,typename Integ2e> 
void Fock2e_tmpl<M_tmpl,Integ2e>::cal_gradient_sub(std::vector<double> &ret_grad_h,std::vector<double> &ret_grad_x,
                                                   const M_tmpl &Da,const M_tmpl &Db, const std::vector<GRAD_data> &grad_data)
{

  int N_cgtos=Da.get_I();

  for(int cc=0;cc<grad_data.size();cc++){
    int j  = grad_data[cc].ij/N_cgtos; 
    int i  = grad_data[cc].ij%N_cgtos;
    int l  = grad_data[cc].kl/N_cgtos; 
    int k  = grad_data[cc].kl%N_cgtos;
    int an = grad_data[cc].atom_no;
    double gX=grad_data[cc].grad_ijkl[0];
    double gY=grad_data[cc].grad_ijkl[1];
    double gZ=grad_data[cc].grad_ijkl[2];

    double Da_ij,Da_kl,Da_il,Da_kj,Da_ki,Da_jl; 
    double Db_ij,Db_kl,Db_il,Db_kj,Db_ki,Db_jl; 
    double Dt_ij,Dt_kl; 
    double DDa_ilkj,DDa_jlki;
    double DDb_ilkj,DDb_jlki;
    double DDt_ijkl;
    Da_ij=Da.get_value(i,j);  Da_kl=Da.get_value(k,l);  Da_il=Da.get_value(i,l);
    Da_kj=Da.get_value(k,j);  Da_jl=Da.get_value(j,l);  Da_ki=Da.get_value(k,i);
    Db_ij=Db.get_value(i,j);  Db_kl=Db.get_value(k,l);  Db_il=Db.get_value(i,l);
    Db_kj=Db.get_value(k,j);  Db_jl=Db.get_value(j,l);  Db_ki=Db.get_value(k,i);
    Dt_ij=0.5*(Da_ij+Db_ij);   Dt_kl=0.5*(Da_kl+Db_kl);  
    DDa_ilkj=0.5*Da_il*Da_kj;  DDa_jlki=0.5*Da_jl*Da_ki;
    DDb_ilkj=0.5*Db_il*Db_kj;  DDb_jlki=0.5*Db_jl*Db_ki;
    DDt_ijkl=Dt_ij*Dt_kl;

    if(i==j && k==l){
      ret_grad_h[an*3+0]+=     DDt_ijkl*gX;  ret_grad_h[an*3+1]+=     DDt_ijkl*gY;  ret_grad_h[an*3+2]+=     DDt_ijkl*gZ;
      ret_grad_x[an*3+0]+=-0.5*DDa_ilkj*gX;  ret_grad_x[an*3+1]+=-0.5*DDa_ilkj*gY;  ret_grad_x[an*3+2]+=-0.5*DDa_ilkj*gZ;
      ret_grad_x[an*3+0]+=-0.5*DDb_ilkj*gX;  ret_grad_x[an*3+1]+=-0.5*DDb_ilkj*gY;  ret_grad_x[an*3+2]+=-0.5*DDb_ilkj*gZ;
      if(i!=k){
        ret_grad_h[an*3+0]+=     DDt_ijkl*gX;  ret_grad_h[an*3+1]+=     DDt_ijkl*gY;  ret_grad_h[an*3+2]+=     DDt_ijkl*gZ;
        ret_grad_x[an*3+0]+=-0.5*DDa_ilkj*gX;  ret_grad_x[an*3+1]+=-0.5*DDa_ilkj*gY;  ret_grad_x[an*3+2]+=-0.5*DDa_ilkj*gZ;
        ret_grad_x[an*3+0]+=-0.5*DDb_ilkj*gX;  ret_grad_x[an*3+1]+=-0.5*DDb_ilkj*gY;  ret_grad_x[an*3+2]+=-0.5*DDb_ilkj*gZ;
      }
    }
    if(i!=j && k==l){
      ret_grad_h[an*3+0]+= 2.0*DDt_ijkl*gX;  ret_grad_h[an*3+1]+= 2.0*DDt_ijkl*gY;  ret_grad_h[an*3+2]+= 2.0*DDt_ijkl*gZ;
      ret_grad_x[an*3+0]+=-1.0*DDa_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DDa_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DDa_ilkj*gZ;
      ret_grad_x[an*3+0]+=-1.0*DDb_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DDb_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DDb_ilkj*gZ;
      if(i!=k){
        ret_grad_h[an*3+0]+= 2.0*DDt_ijkl*gX;  ret_grad_h[an*3+1]+= 2.0*DDt_ijkl*gY;  ret_grad_h[an*3+2]+= 2.0*DDt_ijkl*gZ;
        ret_grad_x[an*3+0]+=-1.0*DDa_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DDa_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DDa_ilkj*gZ;
        ret_grad_x[an*3+0]+=-1.0*DDb_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DDb_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DDb_ilkj*gZ;
      }
    }
    if(i==j && k!=l){
      ret_grad_h[an*3+0]+= 2.0*DDt_ijkl*gX;  ret_grad_h[an*3+1]+= 2.0*DDt_ijkl*gY;  ret_grad_h[an*3+2]+= 2.0*DDt_ijkl*gZ;
      ret_grad_x[an*3+0]+=-1.0*DDa_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DDa_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DDa_ilkj*gZ;
      ret_grad_x[an*3+0]+=-1.0*DDb_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DDb_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DDb_ilkj*gZ;
      if(i!=k){
        ret_grad_h[an*3+0]+= 2.0*DDt_ijkl*gX;  ret_grad_h[an*3+1]+= 2.0*DDt_ijkl*gY;  ret_grad_h[an*3+2]+= 2.0*DDt_ijkl*gZ;
        ret_grad_x[an*3+0]+=-1.0*DDa_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DDa_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DDa_ilkj*gZ;
        ret_grad_x[an*3+0]+=-1.0*DDb_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DDb_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DDb_ilkj*gZ;
      }
    }

    if(i!=j && k!=l){
      ret_grad_h[an*3+0]+= 4.0*DDt_ijkl*gX;  ret_grad_h[an*3+1]+= 4.0*DDt_ijkl*gY;  ret_grad_h[an*3+2]+= 4.0*DDt_ijkl*gZ;
      ret_grad_x[an*3+0]+=-1.0*DDa_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DDa_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DDa_ilkj*gZ;
      ret_grad_x[an*3+0]+=-1.0*DDa_jlki*gX;  ret_grad_x[an*3+1]+=-1.0*DDa_jlki*gY;  ret_grad_x[an*3+2]+=-1.0*DDa_jlki*gZ;
      ret_grad_x[an*3+0]+=-1.0*DDb_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DDb_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DDb_ilkj*gZ;
      ret_grad_x[an*3+0]+=-1.0*DDb_jlki*gX;  ret_grad_x[an*3+1]+=-1.0*DDb_jlki*gY;  ret_grad_x[an*3+2]+=-1.0*DDb_jlki*gZ;
      if(i!=k){
        ret_grad_h[an*3+0]+= 4.0*DDt_ijkl*gX;  ret_grad_h[an*3+1]+= 4.0*DDt_ijkl*gY;  ret_grad_h[an*3+2]+= 4.0*DDt_ijkl*gZ;
        ret_grad_x[an*3+0]+=-1.0*DDa_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DDa_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DDa_ilkj*gZ;
        ret_grad_x[an*3+0]+=-1.0*DDa_jlki*gX;  ret_grad_x[an*3+1]+=-1.0*DDa_jlki*gY;  ret_grad_x[an*3+2]+=-1.0*DDa_jlki*gZ;
        ret_grad_x[an*3+0]+=-1.0*DDb_ilkj*gX;  ret_grad_x[an*3+1]+=-1.0*DDb_ilkj*gY;  ret_grad_x[an*3+2]+=-1.0*DDb_ilkj*gZ;
        ret_grad_x[an*3+0]+=-1.0*DDb_jlki*gX;  ret_grad_x[an*3+1]+=-1.0*DDb_jlki*gY;  ret_grad_x[an*3+2]+=-1.0*DDb_jlki*gZ;
      }
    }
  }

}


template <typename M_tmpl,typename Integ2e> 
void Fock2e_tmpl<M_tmpl,Integ2e>::cal_grad_base(std::vector<double> &ret_grad_h,std::vector<double> &ret_grad_x,
                                                const std::vector<Shell_Cgto> &scgtos,const M_tmpl &Da, const M_tmpl &Db)
{
  using namespace std;
                               
  int N_process=1;
  int process_num=0;
  Util_MPI::get_size_rank(N_process,process_num);

  int N_scgtos=scgtos.size();
  int N_atoms=scgtos[N_scgtos-1].get_atom_no()+1;
                              
  if(_mode!=0 && process_num==0)  cout<<"  debug mode "<<_mode<<" omega "<<_omega<<endl;

  ret_grad_h.reserve(3*N_atoms);
  ret_grad_x.reserve(3*N_atoms);
  ret_grad_h.clear(); 
  ret_grad_x.clear(); 
  // set zero
  for(int i=0;i<N_atoms*3;i++){
     ret_grad_h.push_back(0.0); 
     ret_grad_x.push_back(0.0); 
  } 
 
  time_t start_a,stop_a;
  time(&start_a);

  //  set cutoffM
  M_tmpl cutoffM;
  Fock2e_tmpl<M_tmpl,Integ2e>::cal_cutoffM(cutoffM,scgtos);

  //  set cutoffD
  M_tmpl cutoffDa, cutoffDb;
  cal_cutoffD(cutoffDa, cutoffDb, Da, Db, scgtos);

  #ifdef _OPENMP
  #pragma omp parallel
  {  // start of openMP parallel-loop
  int N_threads  = omp_get_num_threads();
  int thread_num = omp_get_thread_num();
  #else
  int N_threads  = 1;
  int thread_num = 0;
  #endif

  std::vector<double> grad_shell;
  std::vector<GRAD_data> grad_data;
  std::vector<double> omp_grad_h(3*N_atoms,0.0),omp_grad_x(3*N_atoms,0.0);

  if(thread_num==0 && process_num==0)
    cout<<"    cal_eri_grad(N_process="<<N_process<<", N_threads="<<N_threads<<") : "<<flush;
  for(int p=0;p<N_scgtos;p++){
    if(thread_num==0 && process_num==0) cout<<p<<" "<<flush;
    for(int q=p;q<N_scgtos;q++){
      if((q*N_scgtos+p)%N_process==process_num){ // mpi
        #ifdef _OPENMP
        #pragma omp for schedule(dynamic)
        #endif
        for(int r=p;r<N_scgtos;r++){
          for(int s=r;s<N_scgtos;s++){
            double v_cutoff=cutoffM.get_value(p,q)*cutoffM.get_value(r,s);
            bool check_ab = check_cutoffD_ab(p, q, r, s, cutoffDa, cutoffDb);
            if(v_cutoff>CUTOFF_Fock2e && check_ab==true){
              cal_grad_shell(grad_shell, p, q, r, s, scgtos);
              set_data_grad(grad_data,p,q,r,s,scgtos,grad_shell);
              if(_mode_u==Fock2e_Enum::Unrestricted){
                cal_gradient_sub(omp_grad_h,omp_grad_x,Da,grad_data);
              }else{
                cal_gradient_sub(omp_grad_h,omp_grad_x,Da,Db,grad_data);
              }
            }  
          }
        }  
      }  
    }  
  }  

  #ifdef _OPENMP
  #pragma omp critical(add_cal_grad_Fock1e)
  #endif
  {
    for(int i=0;i<3*N_atoms;i++){
      ret_grad_h[i]+=omp_grad_h[i];
      ret_grad_x[i]+=omp_grad_x[i];
    }
  }

  #ifdef _OPENMP
  }  // end of openMP parallel-loop
  #endif 

  time(&stop_a);
  if(process_num==0) cout<<"  time: "<<difftime(stop_a,start_a)<<endl;

  #ifdef USE_MPI_LOTUS
  Util_MPI::allreduce(ret_grad_h);
  Util_MPI::allreduce(ret_grad_x);
  #endif

}



}  // end of namespace "Lotus_core"


#endif // end of include-guard


