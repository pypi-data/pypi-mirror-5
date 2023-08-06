
#ifndef FOCK1E_DETAIL_HPP
#define FOCK1E_DETAIL_HPP

#ifdef _OPENMP
#include <omp.h>
#endif


#include <iostream>



namespace Lotus_core {


template <typename M_tmpl,typename Integ1e>
void Fock1e_tmpl<M_tmpl,Integ1e>::cal_cutoffM_base(std::vector<M_tmpl*> &cutoffM,const std::vector<Shell_Cgto> &scgtos,const CTRL_PBC &ctrl_pbc){
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


                         
template <typename M_tmpl,typename Integ1e>
void Fock1e_tmpl<M_tmpl,Integ1e>::cal_shell(std::vector<double> &ret_shell,int p,int q,const std::vector<Shell_Cgto> &scgtos,
                                            const CTRL_PBC &ctrl_pbc,const _CTRL &ctrl){


  using namespace std;
   
  int tc=ctrl.qc;
  std::vector<double> Rp     = scgtos[p].get_R();
  std::vector<double> Rq     = scgtos[q].get_R();
  std::vector<int>    nc     = ctrl_pbc.get_nc_from_q(tc);
  std::vector<double> Rq_pbc = ctrl_pbc.get_R_pbc(Rq,nc);

  int tn_p=scgtos[p].get_max_tn();
  int tn_q=scgtos[q].get_max_tn();
  int tn=tn_p+tn_q;

  int n_cgto_p=scgtos[p].get_num_cgto();
  int n_cgto_q=scgtos[q].get_num_cgto();
  int n_cgto_pq=n_cgto_p*n_cgto_q;
  ret_shell.reserve(n_cgto_pq);
  ret_shell.clear();
  for(int i=0;i<n_cgto_pq;i++) ret_shell.push_back(0.0);
  std::vector<double> tmp_shell(n_cgto_pq,0.0);
  std::vector<double> dI_1, dI_2;

  std::vector<double> g_p = scgtos[p].get_g();
  std::vector<double> g_q = scgtos[q].get_g();

  //
  // loop for pgto
  Integ1e pint1e;
  for(int a=0;a<scgtos[p].get_num_pgto();a++){
    scgtos[p].get_dI(dI_1,a);
    for(int b=0;b<scgtos[q].get_num_pgto();b++){
      scgtos[q].get_dI(dI_2,b);
      if(ctrl.method==NA_Normal)      pint1e.set_gR_12_nuc(g_p[a],Rp,g_q[b],Rq_pbc,tn,ctrl.Rc,Integ1e::Normal,0.0);
      else if(ctrl.method==NA_Erfc)   pint1e.set_gR_12_nuc(g_p[a],Rp,g_q[b],Rq_pbc,tn,ctrl.Rc,Integ1e::Erfc,ctrl.omega);
      else if(ctrl.method==NA_Erf)    pint1e.set_gR_12_nuc(g_p[a],Rp,g_q[b],Rq_pbc,tn,ctrl.Rc,Integ1e::Erf,ctrl.omega);
      else                            pint1e.set_gR_12(g_p[a],Rp,g_q[b],Rq_pbc);
         


      if(ctrl.method==NA_Normal || ctrl.method==NA_Erfc || ctrl.method==NA_Erf) pint1e.nuclear(tmp_shell,tn_p,tn_q,dI_1,dI_2);
      else if(ctrl.method==Overlap)                                             pint1e.overlap(tmp_shell,tn_p,tn_q,dI_1,dI_2);
      else if(ctrl.method==Kinetic)                                             pint1e.kinetic(tmp_shell,tn_p,tn_q,dI_1,dI_2);
      else{
        cout<<" Error in cal_shell of Fock1e_tmpl class, ctrl.method="<<ctrl.method<<endl;
        exit(1);
      }
      if(ctrl.method==NA_Normal || ctrl.method==NA_Erfc || ctrl.method==NA_Erf){
        for(int i=0;i<n_cgto_pq;i++) ret_shell[i]+=-1.0*ctrl.Z*tmp_shell[i];
      }else if(ctrl.method==Overlap || ctrl.method==Kinetic){
        for(int i=0;i<n_cgto_pq;i++) ret_shell[i]+=tmp_shell[i];
      }
    } 
  }

}




template <typename M_tmpl,typename Integ1e>
void Fock1e_tmpl<M_tmpl,Integ1e>::cal_M_base(std::vector<M_tmpl*> &retM,const std::vector<Shell_Cgto> &scgtos,
                                             METHOD method,const CTRL_PBC &ctrl_pbc){
  using namespace std;

  int N_scgtos=scgtos.size();
  int N_cgtos=Util_GTO::get_N_cgtos(scgtos);
  std::vector<int> n_zero(3,0);
  int zero_q=ctrl_pbc.get_zero_qc();
  int N123_c=ctrl_pbc.get_N123_c();

  // cutoff
  std::vector<M_tmpl> cutoffM(N123_c);
  cal_cutoffM_PBC(cutoffM,scgtos,ctrl_pbc);

  retM.clear();
  retM.reserve(N123_c);                       
  for(int i=0;i<N123_c;i++) retM[i]->set_IJ(N_cgtos,N_cgtos);

  int max_num_cgto=Util_GTO::get_max_num_cgto(scgtos);

  // copy scgto
  std::vector<Shell_Cgto> cp_scgtos;
  for(int i=0;i<N_scgtos;i++){  cp_scgtos.push_back(scgtos[i]);  cp_scgtos[i].set_dI<Integ1e>(); }
  

  #ifdef _OPENMP
  #pragma omp parallel
  {
  int N_threads  = omp_get_num_threads();
  int thread_num = omp_get_thread_num();
  #else
  int N_threads  = 1;
  int thread_num = 0;
  #endif

  _CTRL ctrl;
  if(method==Overlap || method==Kinetic){
    ctrl.method=method; 
  }else{
    std::cout<<" ERROR in cal_NA of Fock1e_tmpl class, method="<<method<<std::endl;
  }

  std::vector<M_tmpl> omp_M(N123_c);
  for(int t=0;t<=zero_q;t++){
    omp_M[t].set_IJ(N_cgtos, N_cgtos);
  }

  std::vector<double> tmp_shell(max_num_cgto*max_num_cgto);

  for(int qc=0;qc<=zero_q;qc++){
    ctrl.qc=qc;
    for(int p=0;p<N_scgtos;p++){
      int start_q=0;
      if(qc==zero_q) start_q=p;
      for(int q=start_q;q<N_scgtos;q++){
        if( (q*N_scgtos+p)%N_threads==thread_num){  // open-mp
          double v_cutoff=fabs(cutoffM[qc].get_value(p,q));
          if(v_cutoff>CUTOFF_Fock1e){
            int min_i=scgtos[p].get_min_cgto_no();
            int min_j=scgtos[q].get_min_cgto_no();
            int max_i=scgtos[p].get_max_cgto_no();
            int max_j=scgtos[q].get_max_cgto_no();

            Fock1e_tmpl::cal_shell(tmp_shell,p,q,cp_scgtos,ctrl_pbc,ctrl);

            int cc=0;
            for(int i=min_i;i<=max_i;i++){
              for(int j=min_j;j<=max_j;j++){
//                if(qc==zero_q && j>=i) retM[qc]->add(i,j,tmp_shell[cc]);
//                if(qc!=zero_q)         retM[qc]->add(i,j,tmp_shell[cc]);
                if(qc==zero_q && j>=i) omp_M[qc].add(i,j,tmp_shell[cc]);
                if(qc!=zero_q)         omp_M[qc].add(i,j,tmp_shell[cc]);
                cc++; 
              }  
            }  
          } 
        }

      }
    }
  } 

  #ifdef _OPENMP
  #pragma omp critical(mat_add)
  #endif
  {
    for(int t=0;t<=zero_q;t++){
      for(int i=0;i<N_cgtos;i++){
        for(int j=0;j<N_cgtos;j++){
          retM[t]->add(i,j,omp_M[t].get_value(i,j));
        }
      }
    }
  }
 
  #ifdef _OPENMP
  }  // end of openMP parallel-loop
  #endif 

  for(int i=0;i<N_cgtos;i++){
    for(int j=i+1;j<N_cgtos;j++){
      double tmp_v=retM[zero_q]->get_value(i,j);
      retM[zero_q]->set_value(j,i,tmp_v);
    }
  }


  for(int q=1;q<=zero_q;q++) mat_transpose(*retM[zero_q+q],*retM[zero_q-q]);
 
}






template <typename M_tmpl,typename Integ1e>
void Fock1e_tmpl<M_tmpl,Integ1e>::cal_NA_base(std::vector<M_tmpl*> &retNA,const std::vector<Shell_Cgto> &scgtos,
                                  METHOD method,double omega,const std::vector<Charge> &charges,const CTRL_PBC &ctrl_pbc){

  using namespace std;

  int N_process=1;
  int process_num=0;
  #ifdef USE_MPI_LOTUS
  Util_MPI::get_size_rank(N_process,process_num);
  #endif

  int N_scgtos=scgtos.size();
  int N_cgtos=Util_GTO::get_N_cgtos(scgtos);
  std::vector<int> n_zero(3,0);
  int zero_q=ctrl_pbc.get_zero_qc();
  int N123_c=ctrl_pbc.get_N123_c();

  retNA.reserve(N123_c);     
  for(int i=0;i<N123_c;i++) retNA[i]->set_IJ(N_cgtos,N_cgtos);

  // cutoff
  std::vector<M_tmpl> cutoffM;
  cal_cutoffM_PBC(cutoffM,scgtos,ctrl_pbc);

  int max_num_cgto=Util_GTO::get_max_num_cgto(scgtos);

  // copy scgto
  std::vector<Shell_Cgto> cp_scgtos;
  for(int i=0;i<N_scgtos;i++){  cp_scgtos.push_back(scgtos[i]);  cp_scgtos[i].set_dI<Integ1e>(); }

  #ifdef _OPENMP
  #pragma omp parallel
  {
  int N_threads  = omp_get_num_threads();
  int thread_num = omp_get_thread_num();
  #else
  int N_threads  = 1; 
  int thread_num = 0;
  #endif
  int N_core     = N_threads*N_process;
  int core_num   = process_num*N_threads + thread_num;


  _CTRL ctrl;
  if(method==NA_Normal || method==NA_Erfc || method==NA_Erf){
    ctrl.method=method; 
    ctrl.omega =omega;
  }else{
    std::cout<<" ERROR in cal_NA of Fock1e_tmpl class, method="<<method<<std::endl;
  }

  std::vector<M_tmpl> omp_M(N123_c);
  for(int t=0;t<=zero_q;t++){
    omp_M[t].set_IJ(N_cgtos, N_cgtos);
  }

  std::vector<double> nai_shell(max_num_cgto*max_num_cgto);

  for(int qc=0;qc<=zero_q;qc++){
    ctrl.qc=qc;
    for(int p=0;p<N_scgtos;p++){
      int start_q=0;
      if(qc==zero_q) start_q=p;
      for(int q=start_q;q<N_scgtos;q++){
        if( (q*N_scgtos+p)%N_core==core_num){ // open-mp + mpi
          double v_cutoff=fabs(cutoffM[qc].get_value(p,q));
          if(v_cutoff>CUTOFF_Fock1e){

            int min_i=scgtos[p].get_min_cgto_no();
            int min_j=scgtos[q].get_min_cgto_no();
            int max_i=scgtos[p].get_max_cgto_no();
            int max_j=scgtos[q].get_max_cgto_no();

            for(int c=0;c<charges.size();c++){
              ctrl.Z=charges[c].charge;
              std::vector<double> Rc;
              Rc.push_back(charges[c].x);
              Rc.push_back(charges[c].y);
              Rc.push_back(charges[c].z);

              for(int qt=0;qt<ctrl_pbc.get_N123_t();qt++){  
                if(Util_PBC::check_range(qc,qt,ctrl_pbc.get_max_Nc(),ctrl_pbc.get_max_Nt())){
                  std::vector<int>    nt     = ctrl_pbc.get_nt_from_q(qt);
                  std::vector<double> Rc_pbc = ctrl_pbc.get_R_pbc(Rc,nt);
                  ctrl.Rc.clear();
                  ctrl.Rc.push_back(Rc_pbc[0]);
                  ctrl.Rc.push_back(Rc_pbc[1]);
                  ctrl.Rc.push_back(Rc_pbc[2]);
                  Fock1e_tmpl::cal_shell(nai_shell,p,q,cp_scgtos,ctrl_pbc,ctrl);

                  int cc=0;
                  for(int i=min_i;i<=max_i;i++){
                    for(int j=min_j;j<=max_j;j++){
//                      if(qc==zero_q && j>=i) retNA[qc]->add(i,j,nai_shell[cc]);
//                      if(qc!=zero_q)         retNA[qc]->add(i,j,nai_shell[cc]);
                      if(qc==zero_q && j>=i) omp_M[qc].add(i,j,nai_shell[cc]);
                      if(qc!=zero_q)         omp_M[qc].add(i,j,nai_shell[cc]);
                      cc++; 
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


  #ifdef _OPENMP
  #pragma omp critical(mat_add)
  #endif
  {
    for(int t=0;t<=zero_q;t++){
      for(int i=0;i<N_cgtos;i++){
        for(int j=0;j<N_cgtos;j++){
          retNA[t]->add(i,j,omp_M[t].get_value(i,j));
        }
      }
    }
  }


  #ifdef _OPENMP
  }  // end of openMP parallel-loop
  #endif 

  #ifdef USE_MPI_LOTUS
//  Util_MPI::allreduce(retNA);
  Util_MPI::isendrecv(retNA);
  #endif


  for(int i=0;i<N_cgtos;i++){
    for(int j=i+1;j<N_cgtos;j++){
      double tmp_v=retNA[zero_q]->get_value(i,j);
      retNA[zero_q]->set_value(j,i,tmp_v);
    }
  }


  for(int q=1;q<=zero_q;q++) mat_transpose(*retNA[zero_q+q],*retNA[zero_q-q]);
 
}



template <typename M_tmpl,typename Integ1e>
void Fock1e_tmpl<M_tmpl,Integ1e>::cal_grad_shell(std::vector<double> &ret_grad,int p,int q,
                                                 const std::vector<Shell_Cgto> &scgtos,const std::vector<M_tmpl*> &D_PBC,
                                                 const _CTRL &ctrl,const CTRL_PBC &ctrl_pbc){

  using namespace std;

  int qc=ctrl.qc;
  int zero_q=ctrl_pbc.get_zero_qc();
  std::vector<double> Rp     = scgtos[p].get_R();
  std::vector<double> Rq     = scgtos[q].get_R();
  std::vector<int>    nc     = ctrl_pbc.get_nc_from_q(qc);
  std::vector<double> Rq_pbc = ctrl_pbc.get_R_pbc(Rq,nc);

  int min_i=scgtos[p].get_min_cgto_no();
  int min_j=scgtos[q].get_min_cgto_no();
  int max_i=scgtos[p].get_max_cgto_no();
  int max_j=scgtos[q].get_max_cgto_no();

  std::vector<double> g_p = scgtos[p].get_g();
  std::vector<double> g_q = scgtos[q].get_g();

  int tn_p =scgtos[p].get_shell_type();
  int tn_q =scgtos[q].get_shell_type();
  int an_p =scgtos[p].get_atom_no();
  int an_q =scgtos[q].get_atom_no();

   int N_a =scgtos[p].get_num_pgto();
   int N_b =scgtos[q].get_num_pgto();

  int num_q=get_num(tn_q);
  int num_q_p=get_num(tn_q+1);
  int num_q_m;
  if(tn_q>=1) num_q_m=get_num(tn_q-1);
  int tn=tn_p+tn_q;

  Integ1e pint1e;
  std::vector<double> tmp_shell_p0,tmp_shell_0p,tmp_shell_m0,tmp_shell_0m,tmp_shell_c;

  std::vector<double> dI_1, dI_2;

  int N_atoms=ctrl.N_atoms;
  ret_grad.reserve(3*N_atoms);
  ret_grad.clear();
  for(int i=0;i<3*N_atoms;i++) ret_grad.push_back(0.0);

  for(int a=0;a<N_a;a++){
    scgtos[p].get_dI(dI_1,a);
    for(int b=0;b<N_b;b++){
      scgtos[q].get_dI(dI_2,b);
      if(ctrl.method==Overlap || ctrl.method==Kinetic){
        pint1e.set_gR_12(g_p[a],Rp,g_q[b],Rq_pbc);
      }else if(ctrl.method==NA_Normal){
        pint1e.set_gR_12_nuc(g_p[a],Rp,g_q[b],Rq_pbc,tn+1,ctrl.Rc,Integ1e::Normal,0.0);
      }else if(ctrl.method==NA_Erfc){
        pint1e.set_gR_12_nuc(g_p[a],Rp,g_q[b],Rq_pbc,tn+1,ctrl.Rc,Integ1e::Erfc,ctrl.omega);
      }else if(ctrl.method==NA_Erf){
        pint1e.set_gR_12_nuc(g_p[a],Rp,g_q[b],Rq_pbc,tn+1,ctrl.Rc,Integ1e::Erf,ctrl.omega);
      }else{
        cout<<" Error ctrl.method="<<ctrl.method<<" in cal_grad_shell of Fock1e_tmpl class "<<endl;
        exit(1);
      }

      if(ctrl.method==Overlap){
        pint1e.overlap(tmp_shell_p0,tn_p+1,tn_q);
        pint1e.overlap(tmp_shell_0p,tn_p,tn_q+1);
        if(tn_p>=1) pint1e.overlap(tmp_shell_m0,tn_p-1,tn_q);
        if(tn_q>=1) pint1e.overlap(tmp_shell_0m,tn_p,tn_q-1);
      }
      else if(ctrl.method==Kinetic){
        pint1e.kinetic(tmp_shell_p0,tn_p+1,tn_q);
        pint1e.kinetic(tmp_shell_0p,tn_p,tn_q+1);
        if(tn_p>=1) pint1e.kinetic(tmp_shell_m0,tn_p-1,tn_q);
        if(tn_q>=1) pint1e.kinetic(tmp_shell_0m,tn_p,tn_q-1);
      }
      else if(ctrl.method==NA_Normal || ctrl.method==NA_Erfc || ctrl.method==NA_Erf){
        pint1e.nuclear(tmp_shell_p0,tn_p+1,tn_q);
        pint1e.nuclear(tmp_shell_0p,tn_p,tn_q+1);
        if(tn_p>=1) pint1e.nuclear(tmp_shell_m0,tn_p-1,tn_q);
        if(tn_q>=1) pint1e.nuclear(tmp_shell_0m,tn_p,tn_q-1);
        if(ctrl.atom_no!=-1) pint1e.nuclear_c(tmp_shell_c,tn_p,tn_q,1);
      }

      for(int xyz=0;xyz<3;xyz++){
        for(int i=min_i;i<=max_i;i++){
          int start_j=min_j;
          if(qc==zero_q) start_j=((i>min_j)?i:min_j);
          for(int j=start_j;j<=max_j;j++){

            int ii=i-min_i;
            int jj=j-min_j;

            double tmp_v_i=0.0;
            double tmp_v_j=0.0;

            std::vector<int> ni=pint1e.get_no_to_n(tn_p,ii);
            std::vector<int> nj=pint1e.get_no_to_n(tn_q,jj);
            std::vector<int> ni_p=get_n_plus(ni,xyz);
            std::vector<int> nj_p=get_n_plus(nj,xyz);
            int i_p1=pint1e.get_n_to_no(ni_p); 
            int j_p1=pint1e.get_n_to_no(nj_p);
            tmp_v_i=2.0*g_p[a]*tmp_shell_p0[i_p1*num_q+jj];

            if(ni[xyz]>0){
              std::vector<int> ni_m=get_n_minus(ni,xyz);
              int i_m1=pint1e.get_n_to_no(ni_m);
              tmp_v_i-=ni[xyz]*tmp_shell_m0[i_m1*num_q+jj];
            }
            if(qc==zero_q){
              tmp_v_j=2.0*g_q[b]*tmp_shell_0p[ii*num_q_p+j_p1];
              if(nj[xyz]>0){
                std::vector<int> nj_m=get_n_minus(nj,xyz);
                int j_m1=pint1e.get_n_to_no(nj_m);
                tmp_v_j-=nj[xyz]*tmp_shell_0m[ii*num_q_m+j_m1];
              }
            }
            double vDij=D_PBC[qc]->get_value(i,j);
            double vDji=D_PBC[qc]->get_value(j,i);


            if(ctrl.atom_no!=-1){
              double tmp_v_c=tmp_shell_c[(ii*num_q+jj)*3+xyz];
              tmp_v_c*=dI_1[ii]*dI_2[jj];
              int an_c=ctrl.atom_no;
              ret_grad[an_c*3+xyz]+=tmp_v_c*vDij;
              if(i!=j) ret_grad[an_c*3+xyz]+=tmp_v_c*vDji;
            } 

            tmp_v_i*=dI_1[ii]*dI_2[jj];
            tmp_v_j*=dI_1[ii]*dI_2[jj];


            ret_grad[an_p*3+xyz]+=tmp_v_i*vDij;
            if(i!=j) ret_grad[an_p*3+xyz]+=tmp_v_i*vDji;
            if(qc==zero_q){
              ret_grad[an_q*3+xyz]+=tmp_v_j*vDij;
              if(i!=j) ret_grad[an_q*3+xyz]+=tmp_v_j*vDji;
            }   
          }     

        }
      }
    }
  }


  if(ctrl.method==NA_Normal || ctrl.method==NA_Erfc || ctrl.method==NA_Erf){
    for(int i=0;i<3*N_atoms;i++) ret_grad[i]*=-1.0*ctrl.Z;
  }
                
}



template <typename M_tmpl,typename Integ1e>
std::vector<double> Fock1e_tmpl<M_tmpl,Integ1e>::cal_grad_base(const std::vector<Shell_Cgto> &scgtos,const std::vector<M_tmpl*> &D_PBC,
                                                               METHOD method,const CTRL_PBC &ctrl_pbc){

  int N_process=1;
  int process_num=0;
  Util_MPI::get_size_rank(N_process,process_num);

  // cutoff
  std::vector<M_tmpl> cutoffM;
  cal_cutoffM_PBC(cutoffM,scgtos,ctrl_pbc);

  int zero_q=ctrl_pbc.get_zero_qc();
  int N_scgtos=scgtos.size();
  int N_atoms=scgtos[N_scgtos-1].get_atom_no()+1;
  std::vector<double> ret_grad; 
  ret_grad.reserve(3*N_atoms);
  ret_grad.clear();
  ret_grad.resize(N_atoms*3, 0.0);


  // copy scgto
  std::vector<Shell_Cgto> cp_scgtos;
  for(int i=0;i<N_scgtos;i++){  cp_scgtos.push_back(scgtos[i]);  cp_scgtos[i].set_dI<Integ1e>(); }

  #ifdef _OPENMP
  #pragma omp parallel
  {  // start of openMP parallel-loop
  #endif

  _CTRL ctrl;
  ctrl.method=method;
  ctrl.N_atoms=N_atoms;

  std::vector<double> omp_grad(3*N_atoms, 0.0),tmp_grad;
  
  for(int qc=0;qc<=zero_q;qc++){
    ctrl.qc=qc;
    for(int p=0;p<N_scgtos;p++){
      if(p%N_process==process_num){ // mpi
        int start_q=0;
        if(qc==zero_q) start_q=p;
        #ifdef _OPENMP
        #pragma omp for schedule(dynamic)
        #endif
        for(int q=start_q;q<N_scgtos;q++){
          double v_cutoff=fabs(cutoffM[qc].get_value(p,q));
          if(v_cutoff>CUTOFF_Fock1e){
            cal_grad_shell(tmp_grad,p,q,cp_scgtos,D_PBC,ctrl,ctrl_pbc);
            for(int i=0;i<3*N_atoms;i++)  omp_grad[i]+=tmp_grad[i];   
          }
        }
      }
    }
  }

  #ifdef _OPENMP
  #pragma omp critical(add_cal_grad_Fock1e)
  #endif
  {
    for(int i=0;i<3*N_atoms;i++) ret_grad[i]+=omp_grad[i];
  }


  #ifdef _OPENMP
  }  // end of openMP parallel-loop
  #endif 

  #ifdef USE_MPI_LOTUS
  Util_MPI::allreduce(ret_grad);
  #endif

  return ret_grad;

}




template <typename M_tmpl,typename Integ1e>
std::vector<double> Fock1e_tmpl<M_tmpl,Integ1e>::cal_grad_NA_base(const std::vector<Shell_Cgto> &scgtos,const std::vector<M_tmpl*> &D_PBC,
                                                                  METHOD method,double omega,const std::vector<Charge> &charges,const CTRL_PBC &ctrl_pbc){

using namespace std;

  int N_process=1;
  int process_num=0;
  #ifdef USE_MPI_LOTUS
  Util_MPI::get_size_rank(N_process,process_num);
  #endif

  // cutoff
  std::vector<M_tmpl> cutoffM;
  cal_cutoffM_PBC(cutoffM,scgtos,ctrl_pbc);

  int zero_q=ctrl_pbc.get_zero_qc();
  int N_scgtos=scgtos.size();
  int N_atoms=scgtos[N_scgtos-1].get_atom_no()+1;
  std::vector<double> ret_grad; 
  ret_grad.reserve(3*N_atoms);
  for(int i=0;i<N_atoms*3;i++) ret_grad.push_back(0.0);

  // copy scgto
  std::vector<Shell_Cgto> cp_scgtos;
  for(int i=0;i<N_scgtos;i++){  cp_scgtos.push_back(scgtos[i]);  cp_scgtos[i].set_dI<Integ1e>(); }

  #ifdef _OPENMP
  #pragma omp parallel
  {
  #endif

  _CTRL ctrl;
  if(method==NA_Normal || method==NA_Erfc || method==NA_Erf){
    ctrl.method=method; 
    ctrl.omega =omega;
    ctrl.N_atoms=N_atoms;
  }else{
    std::cout<<" ERROR in cal_NA of Fock1e_tmpl class, method="<<method<<std::endl;
  }


  std::vector<double> omp_grad(3*N_atoms,0.0),tmp_grad;
  for(int qc=0;qc<=zero_q;qc++){
    ctrl.qc=qc;
    for(int p=0;p<N_scgtos;p++){
      if(p%N_process==process_num){ // mpi
        int start_q=0;
        if(qc==zero_q) start_q=p;
        #ifdef _OPENMP
        #pragma omp for schedule(dynamic)
        #endif
        for(int q=start_q;q<N_scgtos;q++){
          double v_cutoff=fabs(cutoffM[qc].get_value(p,q));
          if(v_cutoff>CUTOFF_Fock1e){

            for(int c=0;c<charges.size();c++){
              ctrl.Z      =charges[c].charge;
              ctrl.atom_no=charges[c].atom_no;
              std::vector<double> Rc;
              Rc.push_back(charges[c].x);
              Rc.push_back(charges[c].y);
              Rc.push_back(charges[c].z);

              for(int qt=0;qt<ctrl_pbc.get_N123_t();qt++){  
                if(Util_PBC::check_range(qc,qt,ctrl_pbc.get_max_Nc(),ctrl_pbc.get_max_Nt())){
                  std::vector<int>    nt     = ctrl_pbc.get_nt_from_q(qt);
                  std::vector<double> Rc_pbc = ctrl_pbc.get_R_pbc(Rc,nt);
                  ctrl.Rc.clear();
                  ctrl.Rc.push_back(Rc_pbc[0]);
                  ctrl.Rc.push_back(Rc_pbc[1]);
                  ctrl.Rc.push_back(Rc_pbc[2]);
                  cal_grad_shell(tmp_grad,p,q,cp_scgtos,D_PBC,ctrl,ctrl_pbc);
                  for(int i=0;i<3*N_atoms;i++)  omp_grad[i]+=tmp_grad[i];   
                }
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
    for(int i=0;i<3*N_atoms;i++) ret_grad[i]+=omp_grad[i];
  }

  #ifdef _OPENMP
  }  // end of openMP parallel-loop
  #endif 

  #ifdef USE_MPI_LOTUS
  Util_MPI::allreduce(ret_grad);
  #endif

  return ret_grad;
 
}




}  // end of namespace "Lotus_core"

#endif // end of include-guard


