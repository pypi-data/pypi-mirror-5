
#ifndef GRID_INTE_DETAIL_HPP
#define GRID_INTE_DETAIL_HPP


#ifdef _OPENMP
#include <omp.h>
#endif



namespace Lotus_core {

template <typename M_tmpl,typename Integ1e>
int Grid_Inte<M_tmpl,Integ1e>::cal_v_ao_PBC(str_V_AO &ret_str_v,
                            const std::vector<double> &xyz, const std::vector<Shell_Cgto> &tsc, const CTRL_PBC &ctrl_pbc)
{
  //
  //  calculation for v_ao, v_ao_deri
  int N_tsc=tsc.size();
  int max_Nc[3];
  ctrl_pbc.get_max_Nc(max_Nc);
  int N123_c = ctrl_pbc.get_N123_c();
  int N_cgtos=Util_GTO::get_N_cgtos(tsc)/N123_c;

  double *v_ao = &ret_str_v.ao[0];
  

  double tmp_v[200], tmp_v_deri[200];
  int flag_cutoff_cgto=0;
  for(int p=0;p<N_tsc;p++){
    int tmp_nu[3];
    tsc[p].get_nT_pbc(&tmp_nu[0]);
    int q_n=Util_PBC::cal_q(&tmp_nu[0], &max_Nc[0]);
    int min_i=tsc[p].get_min_cgto_no();
    int max_i=tsc[p].get_max_cgto_no();
    if(abs(tmp_nu[0])<=max_Nc[0] && abs(tmp_nu[1])<=max_Nc[1] && abs(tmp_nu[2])<=max_Nc[2]){
      tsc[p].grid_value<Integ1e>(&tmp_v[0], &xyz[0]);
      if(mode_deri==1) tsc[p].grid_deri_value<Integ1e>(&tmp_v_deri[0], &xyz[0]);
      for(int i=min_i;i<=max_i;i++){
        v_ao[q_n*N_cgtos+i%N_cgtos]=tmp_v[i-min_i];
        if(fabs(tmp_v[i-min_i])>CUTOFF_DFT) flag_cutoff_cgto=1;
        if(mode_deri==1){
          ret_str_v.deri[(q_n*N_cgtos+i%N_cgtos)*3+0]=tmp_v_deri[(i-min_i)*3+0];
          ret_str_v.deri[(q_n*N_cgtos+i%N_cgtos)*3+1]=tmp_v_deri[(i-min_i)*3+1];
          ret_str_v.deri[(q_n*N_cgtos+i%N_cgtos)*3+2]=tmp_v_deri[(i-min_i)*3+2];
        }
      }
    }else{
      for(int i=min_i;i<=max_i;i++){
        v_ao[q_n*N_cgtos+i%N_cgtos]=0.0;
        if(mode_deri==1){
          ret_str_v.deri[(q_n*N_cgtos+i%N_cgtos)*3+0]=0.0;
          ret_str_v.deri[(q_n*N_cgtos+i%N_cgtos)*3+1]=0.0;
          ret_str_v.deri[(q_n*N_cgtos+i%N_cgtos)*3+2]=0.0;
        }
      }
    }
  }
        
  return flag_cutoff_cgto;
}


template <typename M_tmpl,typename Integ1e> 
//void  Grid_Inte<M_tmpl,Integ1e>::cal_rou_PBC(str_Rou &ret_str_rou, const std::vector<M_tmpl*> &D_PBC,
void  Grid_Inte<M_tmpl,Integ1e>::cal_rou_PBC(double &rou, std::vector<double> &rou_deri, const std::vector<M_tmpl*> &D_PBC,
                             const std::vector<Shell_Cgto> &tsc, const CTRL_PBC &ctrl_pbc, const std::vector<M_tmpl> &cutoffM, const Env &env)
{
  using namespace std;

//  ret_str_rou.set_zero();

  rou=0.0;
  rou_deri.reserve(3);
  rou_deri[0]=0.0;
  rou_deri[1]=0.0;
  rou_deri[2]=0.0;

 
  int N123_c   = ctrl_pbc.get_N123_c();
  int N_tsc    = tsc.size();
  int N_scgtos = N_tsc/N123_c;
  int N_cgtos  = Util_GTO::get_N_cgtos(tsc)/N123_c;
  int max_Nc[3];
  ctrl_pbc.get_max_Nc(&max_Nc[0]);
                           
  int tmp_n[3],tmp_s[3],tmp_ns[3];

  const double *v_ao = static_cast<const double*>(&env.str_v_ao.ao[0]);


  for(int p=0;p<N_scgtos;p++){
    for(int q=0;q<N_tsc;q++){
      tsc[q].get_nT_pbc(&tmp_n[0]);
      int tmp_qc = Util_PBC::cal_q(&tmp_n[0],&max_Nc[0]);
      int q_pbc=q%N_scgtos;
      double cutoff_pq=cutoffM[tmp_qc].get_value(p,q_pbc);
      if(fabs(cutoff_pq)>CUTOFF_DFT){
        int min_a=tsc[p].get_min_cgto_no();  int max_a=tsc[p].get_max_cgto_no();
        int min_b=tsc[q].get_min_cgto_no();  int max_b=tsc[q].get_max_cgto_no();
        int q_n  = Util_PBC::cal_q(&tmp_n[0], &max_Nc[0]);
        int start_s1=-max_Nc[0]; int start_s2=-max_Nc[1]; int start_s3=-max_Nc[2];
        int stop_s1 = max_Nc[0]; int stop_s2 = max_Nc[1]; int stop_s3 = max_Nc[2];
        if((start_s1+tmp_n[0])<-max_Nc[0]) start_s1=-max_Nc[0]-tmp_n[0];
        if((start_s2+tmp_n[1])<-max_Nc[1]) start_s2=-max_Nc[1]-tmp_n[1];
        if((start_s3+tmp_n[2])<-max_Nc[2]) start_s3=-max_Nc[2]-tmp_n[2];
        if((stop_s1 +tmp_n[0])> max_Nc[0])  stop_s1= max_Nc[0]-tmp_n[0];
        if((stop_s2 +tmp_n[1])> max_Nc[1])  stop_s2= max_Nc[1]-tmp_n[1];
        if((stop_s3 +tmp_n[2])> max_Nc[2])  stop_s3= max_Nc[2]-tmp_n[2];
        for(int a=min_a;a<=max_a;a++){
          for(int b=min_b;b<=max_b;b++){
            int a_pbc,b_pbc;
            a_pbc=a%N_cgtos; b_pbc=b%N_cgtos;
            double v_D_ab = D_PBC[q_n]->get_value(a_pbc, b_pbc);

            if(fabs(v_D_ab)>CUTOFF_DFT){
              for(int s1=start_s1;s1<=stop_s1;s1++){
                for(int s2=start_s2;s2<=stop_s2;s2++){
                  for(int s3=start_s3;s3<=stop_s3;s3++){

                    tmp_s[0] =s1;     tmp_s[1] =s2;   tmp_s[2] =s3;
                    tmp_ns[0]=tmp_n[0]+s1; tmp_ns[1]=tmp_n[1]+s2; tmp_ns[2]=tmp_n[2]+s3;
                    int q_s  = Util_PBC::cal_q(&tmp_s[0], &max_Nc[0]);
                    int q_ns = Util_PBC::cal_q(&tmp_ns[0],&max_Nc[0]);
                    rou+=v_ao[N_cgtos*q_s+a_pbc]*v_ao[N_cgtos*q_ns+b_pbc]*v_D_ab;
                    if(mode_deri==1){
                      rou_deri[0]+=v_D_ab
                        *(env.str_v_ao.deri[(q_s *N_cgtos+a)*3+0]*env.str_v_ao.ao[q_ns*N_cgtos+b_pbc]
                         +env.str_v_ao.ao[q_s *N_cgtos+a_pbc]*env.str_v_ao.deri[(q_ns*N_cgtos+b_pbc)*3+0]);
                      rou_deri[1]+=v_D_ab
                        *(env.str_v_ao.deri[(q_s *N_cgtos+a)*3+1]*env.str_v_ao.ao[q_ns*N_cgtos+b_pbc]
                         +env.str_v_ao.ao[q_s *N_cgtos+a_pbc]*env.str_v_ao.deri[(q_ns*N_cgtos+b_pbc)*3+1]);
                      rou_deri[2]+=v_D_ab
                        *(env.str_v_ao.deri[(q_s *N_cgtos+a)*3+2]*env.str_v_ao.ao[q_ns*N_cgtos+b_pbc]
                         +env.str_v_ao.ao[q_s *N_cgtos+a_pbc]*env.str_v_ao.deri[(q_ns*N_cgtos+b_pbc)*3+2]);

//                      ret_str_rou.deri[0]+=D_PBC[q_n]->get_value(a_pbc,b_pbc)
//                        *(env.str_v_ao.deri[(q_s *N_cgtos+a)*3+0]*env.str_v_ao.ao[q_ns*N_cgtos+b_pbc]
//                         +env.str_v_ao.ao[q_s *N_cgtos+a_pbc]*env.str_v_ao.deri[(q_ns*N_cgtos+b_pbc)*3+0]);
//                      ret_str_rou.deri[1]+=D_PBC[q_n]->get_value(a_pbc,b_pbc)
//                        *(env.str_v_ao.deri[(q_s *N_cgtos+a)*3+1]*env.str_v_ao.ao[q_ns*N_cgtos+b_pbc]
//                         +env.str_v_ao.ao[q_s *N_cgtos+a_pbc]*env.str_v_ao.deri[(q_ns*N_cgtos+b_pbc)*3+1]);
//                      ret_str_rou.deri[2]+=D_PBC[q_n]->get_value(a_pbc,b_pbc)
//                        *(env.str_v_ao.deri[(q_s *N_cgtos+a)*3+2]*env.str_v_ao.ao[q_ns*N_cgtos+b_pbc]
//                         +env.str_v_ao.ao[q_s *N_cgtos+a_pbc]*env.str_v_ao.deri[(q_ns*N_cgtos+b_pbc)*3+2]);

                    }

                  }  // s3-loop
                }  // s2-loop
              }  // s1-loop 
            }  // if-cutoff_D_PBC

          }  // b-loop
        }  // a-loop
      }  // if-cutoff_pq
    }  // q-loop
  }  // p-loop


}



template <typename M_tmpl,typename Integ1e>
void Grid_Inte<M_tmpl,Integ1e>::set_rou_grid_for_PBC(str_Rou_pbc &ret_rou_pbc,const std::vector<Shell_Cgto> &scgtos, const std::vector<M_tmpl*> &D_PBC,
                                     const std::vector<double> &Rxyz, const CTRL_PBC &ctrl_pbc, const GInte_Functor &functor)
                                     
                                    
{
  using namespace std;

  int N_process=1;
  int process_num=0;
  Util_MPI::get_size_rank(N_process,process_num);

  // calculation conditions
  int N_atoms  = Rxyz.size()/3;
  int Ng       = grid_data.get_total_grid();
  int N123_c   = ctrl_pbc.get_N123_c();
  int N_cgtos  = Util_GTO::get_N_cgtos(scgtos);
  std::vector<int>  max_Nc = ctrl_pbc.get_max_Nc();
  std::vector<double> T123 = ctrl_pbc.get_T123();

  // set_zero
  ret_rou_pbc.set_zero(N_atoms*Ng);
 
  // set transform matrix
  M_tmpl T,T_rev;
  T.set_IJ(3,3);
  T_rev.set_IJ(3,3);
  Util_PBC::get_T_matrix(T, T_rev, ctrl_pbc.get_T123());
  double lc_1,lc_2,lc_3;
  lc_1 = sqrt(T123[0*3+0]*T123[0*3+0]+T123[0*3+1]*T123[0*3+1]+T123[0*3+2]*T123[0*3+2]);
  lc_2 = sqrt(T123[1*3+0]*T123[1*3+0]+T123[1*3+1]*T123[1*3+1]+T123[1*3+2]*T123[1*3+2]);
  lc_3 = sqrt(T123[2*3+0]*T123[2*3+0]+T123[2*3+1]*T123[2*3+1]+T123[2*3+2]*T123[2*3+2]);

  
  //  cgtos_pbc
  std::vector<Shell_Cgto> tsc = Util_GTO::get_scgtos_PBC(scgtos, ctrl_pbc.get_max_Nc(), ctrl_pbc.get_T123() );
  int N_tsc=tsc.size();
  for(int i=0;i<N_tsc;i++) tsc[i].set_dI<Integ1e>();

  //  cutoffM
  std::vector<M_tmpl> cutoffM;
  Util_GTO::cal_cutoffM_PBC<M_tmpl,Integ1e>(cutoffM, scgtos, ctrl_pbc);

  //  construct grid for atom
  std::vector<double> xyzw_g;
  grid_data.get_grid(xyzw_g);

  #ifdef _OPENMP
  #pragma omp parallel
  { // start of Open-MP parallel-loop
  int N_threads =omp_get_num_threads();
  int thread_num=omp_get_thread_num();
  #else
  int N_threads=1;
  int thread_num=0;
  #endif

  int N_cores=N_process*N_threads;
  int core_num=process_num*N_threads+thread_num;

  Env env;
  env.str_v_ao.initialize_N(N_cgtos*N123_c);
  env.N_cgtos=N_cgtos;
  env.N_cgtos_pbc=N_cgtos*N123_c;


  for(int a=0;a<N_atoms;a++){
//    #ifdef _OPENMP
//    #pragma omp for schedule(dynamic)
//    #endif
    for(int g=0;g<Ng;g++){
      if((g*N_atoms+a)%N_cores==core_num){  // mpi+openmp
        std::vector<double> xyz(3, 0.0);
        double x,y,z;
        x=xyzw_g[g*4+0]+Rxyz[a*3+0];  y=xyzw_g[g*4+1]+Rxyz[a*3+1];  z=xyzw_g[g*4+2]+Rxyz[a*3+2];

        double uvw_1 = x*T.get_value(0,0) + y*T.get_value(0,1) + z*T.get_value(0,2);
        double uvw_2 = x*T.get_value(1,0) + y*T.get_value(1,1) + z*T.get_value(1,2);
        double uvw_3 = x*T.get_value(2,0) + y*T.get_value(2,1) + z*T.get_value(2,2);

        if(max_Nc[0]!=0){
          uvw_1=fmod(uvw_1,lc_1);
          int uvw_n1=(int)(uvw_1/lc_1);
          if(uvw_1!=0) uvw_1=uvw_1-uvw_n1*lc_1;
        }
        if(max_Nc[1]!=0){
          uvw_2=fmod(uvw_2,lc_2);
          int uvw_n2=(int)(uvw_2/lc_2);
          if(uvw_2!=0) uvw_2=uvw_2-uvw_n2*lc_2;
        }
        if(max_Nc[2]!=0){
          uvw_3=fmod(uvw_3,lc_3);
          int uvw_n3=(int)(uvw_3/lc_3);
          if(uvw_3!=0) uvw_3=uvw_3-uvw_n3*lc_3;
        }
        double x_shift = T_rev.get_value(0,0)*uvw_1 + T_rev.get_value(0,1)*uvw_2 + T_rev.get_value(0,2)*uvw_3;
        double y_shift = T_rev.get_value(1,0)*uvw_1 + T_rev.get_value(1,1)*uvw_2 + T_rev.get_value(1,2)*uvw_3;
        double z_shift = T_rev.get_value(2,0)*uvw_1 + T_rev.get_value(2,1)*uvw_2 + T_rev.get_value(2,2)*uvw_3;
        xyz[0]=x_shift; xyz[1]=y_shift; xyz[2]=z_shift;

        double rou=0.0;
        std::vector<double> rou_deri(3, 0.0);

        //  calculation for v_ao, v_ao_deri
        int flag_cutoff_cgto=cal_v_ao_PBC(env.str_v_ao, xyz, tsc, ctrl_pbc);
        //  calculation for rou, deri_rou
        if(flag_cutoff_cgto==1)  cal_rou_PBC(rou, rou_deri, D_PBC, tsc, ctrl_pbc, cutoffM, env);
        
        //
        //  cal DFT functional
        double tmp_ene=0.0;
        std::vector<double> tv123(3, 0.0);
        if(rou>CUTOFF_DFT)  functor(tmp_ene, tv123, rou, rou_deri);

        //  write for return
        ret_rou_pbc.v123[(a*Ng+g)*3+0]=tv123[0];
        ret_rou_pbc.v123[(a*Ng+g)*3+1]=tv123[1];
        ret_rou_pbc.v123[(a*Ng+g)*3+2]=tv123[2];
        ret_rou_pbc.rou[a*Ng+g]=rou;
        ret_rou_pbc.ene_pbc[a*Ng+g]=tmp_ene;
        if(functor.get_flag_gga()==1 || mode_grad == GRADIENT){
          ret_rou_pbc.rou_deri[(a*Ng+g)*3+0]=rou_deri[0];
          ret_rou_pbc.rou_deri[(a*Ng+g)*3+1]=rou_deri[1];
          ret_rou_pbc.rou_deri[(a*Ng+g)*3+2]=rou_deri[2];
        }
      }
    }  // loop-g
  }  // loop-a

  #ifdef _OPENMP
  } // end of openMP parallel-loop
  #endif 

  #ifdef USE_MPI_LOTUS
  Util_MPI::allreduce(ret_rou_pbc.rou);
  Util_MPI::allreduce(ret_rou_pbc.rou_deri);
  Util_MPI::allreduce(ret_rou_pbc.ene_pbc);
  Util_MPI::allreduce(ret_rou_pbc.v123);
  #endif

}



template <typename M_tmpl,typename Integ1e>
void Grid_Inte<M_tmpl,Integ1e>::cal_Vxc_sub(std::vector<M_tmpl*> &ret_Vxc_PBC,  const str_Rou &str_rou, 
                                            const double *v123, const CTRL_PBC &ctrl_pbc, const Env &env )
{


  int N_cgtos_pbc = env.N_cgtos_pbc;
  int N_cgtos     = N_cgtos_pbc/ctrl_pbc.get_N123_c();
  int zero_qc     = ctrl_pbc.get_zero_qc();
  int max_Nc[3];
  ctrl_pbc.get_max_Nc(max_Nc);
 
  double rou_deri[3];
  rou_deri[0] = str_rou.deri[0];
  rou_deri[1] = str_rou.deri[1];
  rou_deri[2] = str_rou.deri[2];

  const double *v_ao   = static_cast<const double*>(&env.str_v_ao.ao[0]); 
  const double *v_deri = static_cast<const double*>(&env.str_v_ao.deri[0]); 
 
  for(int u=0;u<N_cgtos;u++){
    if(env.u_cutoff_flag[u*3+0]==1 || (flag_gga==1 && env.u_cutoff_flag[u*3+1])==1){
      double v0=v123[0]*v_ao[u];
      double v1a,v2a,v3a;
      double v1b,v2b,v3b;
      v1a=v2a=v3a=0.0;
      v1b=v2b=v3b=0.0;
      if(flag_gga==1){
        v1a=(v123[1]+v123[2])*rou_deri[0]*v_ao[u];
        v2a=(v123[1]+v123[2])*rou_deri[1]*v_ao[u];
        v3a=(v123[1]+v123[2])*rou_deri[2]*v_ao[u];
        v1b=(v123[1]+v123[2])*rou_deri[0]*v_deri[u*3+0];
        v2b=(v123[1]+v123[2])*rou_deri[1]*v_deri[u*3+1];
        v3b=(v123[1]+v123[2])*rou_deri[2]*v_deri[u*3+2];
      }
      for(int v=u;v<N_cgtos_pbc;v++){
        int n_v[3];
        env.cgtos_pbc[v].get_nT_pbc(&n_v[0]);
        int q_n=Util_PBC::cal_q(&n_v[0],&max_Nc[0]);
        if(q_n<=zero_qc){
          int u_pbc=u%N_cgtos; 
          int v_pbc=v%N_cgtos;
          double tmp_v=(v0+v1b+v2b+v3b)*v_ao[v]+v1a*v_deri[v*3+0]+v2a*v_deri[v*3+1]+v3a*v_deri[v*3+2];
          ret_Vxc_PBC[q_n]->add(u_pbc,v_pbc,tmp_v);
        }
      }
    }
  }
}


template <typename M_tmpl,typename Integ1e>
void Grid_Inte<M_tmpl,Integ1e>::cal_grad_sub(std::vector<double> &ret_grad, const std::vector<M_tmpl*> &D_PBC, const std::vector<double> &rou_deri, 
                                             const double *v123, const CTRL_PBC &ctrl_pbc, const Env &env)
{

  int N_cgtos_pbc = env.N_cgtos_pbc;
  int N_cgtos     = N_cgtos_pbc/ctrl_pbc.get_N123_c();
  int max_Nc[3];
  ctrl_pbc.get_max_Nc(max_Nc);
  int N_atoms = ret_grad.size()/3;


  double vDuv,vDvu;
  double v1=v123[0];
  double v2=v123[1];
  double v3=v123[2];
  for(int u=0;u<N_cgtos;u++){
    if(env.u_cutoff_flag[u*3+0]==1 || env.u_cutoff_flag[u*3+1]==1 || (flag_gga==1 && env.u_cutoff_flag[u*3+2]==1) ){
      for(int v=u;v<N_cgtos_pbc;v++){
        if(mode_pbc==0){
          vDuv=D_PBC[0]->get_value(u,v);
          vDvu=D_PBC[0]->get_value(v,u);
        }else{
          int n_v[3];
          env.cgtos_pbc[v].get_nT_pbc(&n_v[0]);
          int q_D=Util_PBC::cal_q(n_v,max_Nc);
          int u_pbc=u%N_cgtos; 
          int v_pbc=v%N_cgtos;
          vDuv=D_PBC[q_D]->get_value(u_pbc,v_pbc); 
          vDvu=D_PBC[q_D]->get_value(u_pbc,v_pbc); 
        }
        int atom_no_u=env.cgtos_pbc[u].get_atom_no();
        int atom_no_v=env.cgtos_pbc[v].get_atom_no();
        if(atom_no_u<N_atoms){
          ret_grad[atom_no_u*3+0]+=-1.0*vDuv*v1*env.str_v_ao.ao[v]*env.str_v_ao.deri[u*3+0];    
          ret_grad[atom_no_u*3+1]+=-1.0*vDuv*v1*env.str_v_ao.ao[v]*env.str_v_ao.deri[u*3+1];    
          ret_grad[atom_no_u*3+2]+=-1.0*vDuv*v1*env.str_v_ao.ao[v]*env.str_v_ao.deri[u*3+2];   
          if(u!=v){
            ret_grad[atom_no_u*3+0]+=-1.0*vDvu*v1*env.str_v_ao.ao[v]*env.str_v_ao.deri[u*3+0];    
            ret_grad[atom_no_u*3+1]+=-1.0*vDvu*v1*env.str_v_ao.ao[v]*env.str_v_ao.deri[u*3+1];    
            ret_grad[atom_no_u*3+2]+=-1.0*vDvu*v1*env.str_v_ao.ao[v]*env.str_v_ao.deri[u*3+2];   
          } 
        }
        if(atom_no_v<N_atoms){
          ret_grad[atom_no_v*3+0]+=-1.0*vDuv*v1*env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+0];    
          ret_grad[atom_no_v*3+1]+=-1.0*vDuv*v1*env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+1];    
          ret_grad[atom_no_v*3+2]+=-1.0*vDuv*v1*env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+2]; 
          if(u!=v){
            ret_grad[atom_no_v*3+0]+=-1.0*vDvu*v1*env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+0];    
            ret_grad[atom_no_v*3+1]+=-1.0*vDvu*v1*env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+1];    
            ret_grad[atom_no_v*3+2]+=-1.0*vDvu*v1*env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+2]; 
          }
        }   
        if(flag_gga==1){
          double xx,yy,zz;
          if(atom_no_u<N_atoms){
            xx=(env.str_v_ao.deri[u*3+0]*env.str_v_ao.deri[v*3+0]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+0])*rou_deri[0]
              +(env.str_v_ao.deri[u*3+0]*env.str_v_ao.deri[v*3+1]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+1])*rou_deri[1]
              +(env.str_v_ao.deri[u*3+0]*env.str_v_ao.deri[v*3+2]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+2])*rou_deri[2];
            yy=(env.str_v_ao.deri[u*3+1]*env.str_v_ao.deri[v*3+0]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+1])*rou_deri[0]
              +(env.str_v_ao.deri[u*3+1]*env.str_v_ao.deri[v*3+1]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+3])*rou_deri[1]
              +(env.str_v_ao.deri[u*3+1]*env.str_v_ao.deri[v*3+2]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+4])*rou_deri[2];
            zz=(env.str_v_ao.deri[u*3+2]*env.str_v_ao.deri[v*3+0]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+2])*rou_deri[0]
              +(env.str_v_ao.deri[u*3+2]*env.str_v_ao.deri[v*3+1]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+4])*rou_deri[1]
              +(env.str_v_ao.deri[u*3+2]*env.str_v_ao.deri[v*3+2]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+5])*rou_deri[2];
            ret_grad[atom_no_u*3+0]+=-1.0*vDuv*(v2+v3)*xx;
            ret_grad[atom_no_u*3+1]+=-1.0*vDuv*(v2+v3)*yy;
            ret_grad[atom_no_u*3+2]+=-1.0*vDuv*(v2+v3)*zz;
            if(u!=v){
              ret_grad[atom_no_u*3+0]+=-1.0*vDvu*(v2+v3)*xx;
              ret_grad[atom_no_u*3+1]+=-1.0*vDvu*(v2+v3)*yy;
              ret_grad[atom_no_u*3+2]+=-1.0*vDvu*(v2+v3)*zz;
            }
          }
          if(atom_no_v<N_atoms){
            xx=(env.str_v_ao.deri[v*3+0]*env.str_v_ao.deri[u*3+0]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+0])*rou_deri[0]
              +(env.str_v_ao.deri[v*3+0]*env.str_v_ao.deri[u*3+1]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+1])*rou_deri[1]
              +(env.str_v_ao.deri[v*3+0]*env.str_v_ao.deri[u*3+2]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+2])*rou_deri[2];
            yy=(env.str_v_ao.deri[v*3+1]*env.str_v_ao.deri[u*3+0]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+1])*rou_deri[0]
              +(env.str_v_ao.deri[v*3+1]*env.str_v_ao.deri[u*3+1]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+3])*rou_deri[1]
              +(env.str_v_ao.deri[v*3+1]*env.str_v_ao.deri[u*3+2]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+4])*rou_deri[2];
            zz=(env.str_v_ao.deri[v*3+2]*env.str_v_ao.deri[u*3+0]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+2])*rou_deri[0]
              +(env.str_v_ao.deri[v*3+2]*env.str_v_ao.deri[u*3+1]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+4])*rou_deri[1]
              +(env.str_v_ao.deri[v*3+2]*env.str_v_ao.deri[u*3+2]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+5])*rou_deri[2];
            ret_grad[atom_no_v*3+0]+=-1.0*vDuv*(v2+v3)*xx;
            ret_grad[atom_no_v*3+1]+=-1.0*vDuv*(v2+v3)*yy;
            ret_grad[atom_no_v*3+2]+=-1.0*vDuv*(v2+v3)*zz;
            if(u!=v){
              ret_grad[atom_no_v*3+0]+=-1.0*vDvu*(v2+v3)*xx;
              ret_grad[atom_no_v*3+1]+=-1.0*vDvu*(v2+v3)*yy;
              ret_grad[atom_no_v*3+2]+=-1.0*vDvu*(v2+v3)*zz;
            }
          }
        }

      }
    }
  }
}


template <typename M_tmpl,typename Integ1e>
void Grid_Inte<M_tmpl,Integ1e>::set_Rxyz_pbc(std::vector<double> &ret_Rxyz_pbc, std::vector<double> &ret_r_ab,
                             const std::vector<double> &Rxyz, const CTRL_PBC &ctrl_pbc)
{
  int N123_c=ctrl_pbc.get_N123_c();
  std::vector<double> T123=ctrl_pbc.get_T123();
  int N_atoms=Rxyz.size()/3;
  std::vector<int> max_Nc = ctrl_pbc.get_max_Nc();
  int N_A=N_atoms*N123_c;
  ret_Rxyz_pbc.reserve(N_A*3);
  ret_r_ab.reserve(N_A*N_A);
  ret_Rxyz_pbc.clear();
  ret_r_ab.clear();
  for(int i=0;i<N_A*3;i++)    ret_Rxyz_pbc.push_back(0.0);
  for(int i=0;i<N_A*N_A;i++)  ret_r_ab.push_back(0.0);
                           
  int cc=0;
  for(int a=0;a<N_atoms;a++){
    ret_Rxyz_pbc[cc*3+0]=Rxyz[a*3+0]; ret_Rxyz_pbc[cc*3+1]=Rxyz[a*3+1]; ret_Rxyz_pbc[cc*3+2]=Rxyz[a*3+2];
    cc++;
  }
  for(int n1=-max_Nc[0];n1<=max_Nc[0];n1++){
    for(int n2=-max_Nc[1];n2<=max_Nc[1];n2++){
      for(int n3=-max_Nc[2];n3<=max_Nc[2];n3++){
        if(n1==0 && n2==0 && n3==0){
        }else{
          for(int a=0;a<N_atoms;a++){
            ret_Rxyz_pbc[cc*3+0]=Rxyz[a*3+0]+n1*T123[0*3+0]+n2*T123[1*3+0]+n3*T123[2*3+0];
            ret_Rxyz_pbc[cc*3+1]=Rxyz[a*3+1]+n1*T123[0*3+1]+n2*T123[1*3+1]+n3*T123[2*3+1];
            ret_Rxyz_pbc[cc*3+2]=Rxyz[a*3+2]+n1*T123[0*3+2]+n2*T123[1*3+2]+n3*T123[2*3+2];
            cc++;
          }
        }
      }
    }
  }

  for(int a=0;a<N_A;a++){
    for(int b=0;b<N_A;b++){
      double tmp_r=sqrt((ret_Rxyz_pbc[a*3+0]-ret_Rxyz_pbc[b*3+0])*(ret_Rxyz_pbc[a*3+0]-ret_Rxyz_pbc[b*3+0])
                       +(ret_Rxyz_pbc[a*3+1]-ret_Rxyz_pbc[b*3+1])*(ret_Rxyz_pbc[a*3+1]-ret_Rxyz_pbc[b*3+1])
                       +(ret_Rxyz_pbc[a*3+2]-ret_Rxyz_pbc[b*3+2])*(ret_Rxyz_pbc[a*3+2]-ret_Rxyz_pbc[b*3+2]));
      ret_r_ab[a*N_A+b]=tmp_r;
    }
  }
}




template <typename M_tmpl,typename Integ1e>
void Grid_Inte<M_tmpl,Integ1e>::cal_v_ao(str_V_AO &ret_str_v_ao, const std::vector<Shell_Cgto> &scgtos, const std::vector<double> &xyz)
{

  std::vector<double> tmp_v(100);
  for(int p=0;p<scgtos.size();p++){
    int min_i=scgtos[p].get_min_cgto_no();
    int max_i=scgtos[p].get_max_cgto_no();
    scgtos[p].grid_value<Integ1e>(tmp_v,xyz);
    for(int i=min_i;i<=max_i;i++) ret_str_v_ao.ao[i]=tmp_v[i-min_i];
  }
}


template <typename M_tmpl,typename Integ1e>
void Grid_Inte<M_tmpl,Integ1e>::cal_v_ao_deri(str_V_AO &ret_str_v_ao, const std::vector<Shell_Cgto> &scgtos, const std::vector<double> &xyz)
{
  std::vector<double> tmp_deri(200);
  for(int p=0;p<scgtos.size();p++){
    int min_i=scgtos[p].get_min_cgto_no();
    int max_i=scgtos[p].get_max_cgto_no();
    scgtos[p].grid_deri_value<Integ1e>(tmp_deri,xyz);
    for(int i=min_i;i<=max_i;i++){
       ret_str_v_ao.deri[i*3+0]=tmp_deri[(i-min_i)*3+0];
       ret_str_v_ao.deri[i*3+1]=tmp_deri[(i-min_i)*3+1];
       ret_str_v_ao.deri[i*3+2]=tmp_deri[(i-min_i)*3+2];
    }
  }
}


template <typename M_tmpl,typename Integ1e>
void Grid_Inte<M_tmpl,Integ1e>::cal_v_ao_deri2(str_V_AO &ret_str_v_ao, const std::vector<Shell_Cgto> &scgtos, const std::vector<double> &xyz)
{
  std::vector<double> tmp_deri2(600);
  for(int p=0;p<scgtos.size();p++){
    int min_i=scgtos[p].get_min_cgto_no();
    int max_i=scgtos[p].get_max_cgto_no();
    scgtos[p].grid_deri2_value<Integ1e>(tmp_deri2,xyz);
    for(int i=min_i;i<=max_i;i++){
      ret_str_v_ao.deri2[i*6+0]=tmp_deri2[(i-min_i)*6+0]; 
      ret_str_v_ao.deri2[i*6+1]=tmp_deri2[(i-min_i)*6+1]; 
      ret_str_v_ao.deri2[i*6+2]=tmp_deri2[(i-min_i)*6+2]; 
      ret_str_v_ao.deri2[i*6+3]=tmp_deri2[(i-min_i)*6+3]; 
      ret_str_v_ao.deri2[i*6+4]=tmp_deri2[(i-min_i)*6+4]; 
      ret_str_v_ao.deri2[i*6+5]=tmp_deri2[(i-min_i)*6+5]; 
    }
  }
}


template <typename M_tmpl,typename Integ1e> 
void Grid_Inte<M_tmpl,Integ1e>::cal_rou(str_Rou &ret, const std::vector<M_tmpl*> &D_PBC, const Env &env)
//void Grid_Inte<M_tmpl,Integ1e>::cal_rou(double &ret_rou, std::vector<double> &ret_deri, const std::vector<M_tmpl*> &D_PBC, const Env &env)
{
//  ret.set_zero();        
//  ret_rou=0.0;
//  ret_deri.reserve(3);
//  ret_deri[0]=0.0;             
//  ret_deri[1]=0.0;             
//  ret_deri[2]=0.0;   
         
  int N_cgtos=D_PBC[0]->get_I();

  if(mode_pbc==0){ // for molecule
    if(mode_grad==1 || flag_gga==1){
      for(int u=0;u<N_cgtos;u++){
        if(env.u_cutoff_flag[u*3+0]==1 || env.u_cutoff_flag[u*3+1]==1){
          for(int v=u+1;v<N_cgtos;v++){
            double d_uv=2.0*D_PBC[0]->get_value(u,v);
            ret.rou+=d_uv*env.str_v_ao.ao[u]*env.str_v_ao.ao[v];
            ret.deri[0]+=d_uv*(env.str_v_ao.deri[u*3+0]*env.str_v_ao.ao[v]+env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+0]);
            ret.deri[1]+=d_uv*(env.str_v_ao.deri[u*3+1]*env.str_v_ao.ao[v]+env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+1]);
            ret.deri[2]+=d_uv*(env.str_v_ao.deri[u*3+2]*env.str_v_ao.ao[v]+env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+2]);
          }
          double d_uu=D_PBC[0]->get_value(u,u);
          ret.rou+=d_uu*env.str_v_ao.ao[u]*env.str_v_ao.ao[u];
          ret.deri[0]+=d_uu*(env.str_v_ao.deri[u*3+0]*env.str_v_ao.ao[u]+env.str_v_ao.ao[u]*env.str_v_ao.deri[u*3+0]);
          ret.deri[1]+=d_uu*(env.str_v_ao.deri[u*3+1]*env.str_v_ao.ao[u]+env.str_v_ao.ao[u]*env.str_v_ao.deri[u*3+1]);
          ret.deri[2]+=d_uu*(env.str_v_ao.deri[u*3+2]*env.str_v_ao.ao[u]+env.str_v_ao.ao[u]*env.str_v_ao.deri[u*3+2]);
        }
      }
    }else{
      for(int u=0;u<N_cgtos;u++){
        if(env.u_cutoff_flag[u*3+0]==1 || env.u_cutoff_flag[u*3+1]==1){
          for(int v=u+1;v<N_cgtos;v++){  ret.rou+=env.str_v_ao.ao[u]*env.str_v_ao.ao[v]*2.0*D_PBC[0]->get_value(u,v); }
          ret.rou+=env.str_v_ao.ao[u]*env.str_v_ao.ao[u]*D_PBC[0]->get_value(u,u);
        }
      }
    }
  }

}


template <typename M_tmpl,typename Integ1e>
void Grid_Inte<M_tmpl,Integ1e>::set_u_cutoff_flag(Env &env)
{
  int N_cgtos=env.N_cgtos;                               
  // set u_cutoff_flag
  for(int u=0;u<N_cgtos;u++){
    env.u_cutoff_flag[u*3+0]=env.u_cutoff_flag[u*3+1]=env.u_cutoff_flag[u*3+2]=0;
    if(fabs(env.str_v_ao.ao[u])>CUTOFF_DFT) env.u_cutoff_flag[u*3+0]=1;
    if( (mode_grad==1 || flag_gga==1) && 
        (fabs(env.str_v_ao.deri[u*3+0])>CUTOFF_DFT || fabs(env.str_v_ao.deri[u*3+1])>CUTOFF_DFT || fabs(env.str_v_ao.deri[u*3+2])>CUTOFF_DFT) ){
      env.u_cutoff_flag[u*3+1]=1;
    }
    if( (flag_gga==1 && mode_grad==1) && 
        (fabs(env.str_v_ao.deri2[u*3+0])>CUTOFF_DFT || fabs(env.str_v_ao.deri2[u*3+1])>CUTOFF_DFT || fabs(env.str_v_ao.deri2[u*3+2])>CUTOFF_DFT ||
         fabs(env.str_v_ao.deri2[u*3+3])>CUTOFF_DFT || fabs(env.str_v_ao.deri2[u*3+4])>CUTOFF_DFT || fabs(env.str_v_ao.deri2[u*3+5])>CUTOFF_DFT) ){
      env.u_cutoff_flag[u*3+2]=1;
    }
  }
}




template <typename M_tmpl,typename Integ1e>
void Grid_Inte<M_tmpl,Integ1e>::cal_Vxc_sub(std::vector<M_tmpl*> &ret_Vxc_a_PBC, std::vector<M_tmpl*> &ret_Vxc_b_PBC, 
                            const str_Rou &str_rou_a, const str_Rou &str_rou_b,
                            const double *v123_a, const double *v123_b, const CTRL_PBC &ctrl_pbc, const Env &env)
                           
{


  int N_cgtos_pbc = env.N_cgtos_pbc;
  int N_cgtos     = N_cgtos_pbc/ctrl_pbc.get_N123_c();
  int zero_qc     = ctrl_pbc.get_zero_qc();
  int max_Nc[3];
  ctrl_pbc.get_max_Nc(&max_Nc[0]);

  double rou_deri_a[3], rou_deri_b[3];
  rou_deri_a[0] = str_rou_a.deri[0];
  rou_deri_a[1] = str_rou_a.deri[1];
  rou_deri_a[2] = str_rou_a.deri[2];
  rou_deri_b[0] = str_rou_b.deri[0];
  rou_deri_b[1] = str_rou_b.deri[1];
  rou_deri_b[2] = str_rou_b.deri[2];

  const double *v_ao   = static_cast<const double*>(&env.str_v_ao.ao[0]); 
  const double *v_deri = static_cast<const double*>(&env.str_v_ao.deri[0]); 

  double v1_a=v123_a[0];
  double v2_a=v123_a[1];
  double v3_a=v123_a[2];
  double v1_b=v123_b[0];
  double v2_b=v123_b[1];
  double v3_b=v123_b[2];
  for(int u=0;u<N_cgtos;u++){
    if(env.u_cutoff_flag[u*3+0]==1 || (flag_gga==1 && env.u_cutoff_flag[u*3+1])==1){
      double v1_au  =v1_a*v_ao[u];
      double a_sub1=rou_deri_a[0]*v_ao[u];
      double a_sub2=rou_deri_a[1]*v_ao[u];
      double a_sub3=rou_deri_a[2]*v_ao[u];
      double a_sub4=rou_deri_a[0]*v_deri[u*3+0]+rou_deri_a[1]*v_deri[u*3+1]+rou_deri_a[2]*v_deri[u*3+2];
      double v1_bu  =v1_b*v_ao[u];
      double b_sub1=rou_deri_b[0]*v_ao[u];
      double b_sub2=rou_deri_b[1]*v_ao[u];
      double b_sub3=rou_deri_b[2]*v_ao[u];
      double b_sub4=rou_deri_b[0]*v_deri[u*3+0]+rou_deri_b[1]*v_deri[u*3+1]+rou_deri_b[2]*v_deri[u*3+2];

      for(int v=u;v<N_cgtos_pbc;v++){
        int n_v[3];
        env.cgtos_pbc[v].get_nT_pbc(&n_v[0]);
        int q_n=Util_PBC::cal_q(&n_v[0],&max_Nc[0]);
        if(q_n<=zero_qc){
          int u_pbc=u%N_cgtos; 
          int v_pbc=v%N_cgtos;

          double dot_a=a_sub1*v_deri[v*3+0]+a_sub2*v_deri[v*3+1]+a_sub3*v_deri[v*3+2]+a_sub4*v_ao[v];
          double dot_b=b_sub1*v_deri[v*3+0]+b_sub2*v_deri[v*3+1]+b_sub3*v_deri[v*3+2]+b_sub4*v_ao[v];
          double tmp_v_a=v1_au*v_ao[v]+v2_a*dot_a+v3_a*dot_b;
          double tmp_v_b=v1_bu*v_ao[v]+v2_b*dot_b+v3_b*dot_a;

          ret_Vxc_a_PBC[q_n]->add(u_pbc,v_pbc,tmp_v_a);
          ret_Vxc_b_PBC[q_n]->add(u_pbc,v_pbc,tmp_v_b);
        }
      }
    }
  }
}




template <typename M_tmpl,typename Integ1e>
void Grid_Inte<M_tmpl,Integ1e>::cal_grad_sub(std::vector<double> &ret_grad, const std::vector<M_tmpl*> &Da_PBC, const std::vector<M_tmpl*> &Db_PBC,
                                             const std::vector<double> &rou_deri_a, const std::vector<double> &rou_deri_b, 
                                             const double *v123_a,const double *v123_b, const CTRL_PBC &ctrl_pbc, const Env &env)
                            
{

  int N_cgtos_pbc = env.N_cgtos_pbc;
  int N_cgtos     = N_cgtos_pbc/ctrl_pbc.get_N123_c();
  int N_atoms     = ret_grad.size()/3;

  double vDuv_v1,vDuv_v23_x,vDuv_v23_y,vDuv_v23_z;
  double v1_a=v123_a[0];
  double v2_a=v123_a[1];
  double v3_a=v123_a[2];
  double v1_b=v123_b[0];
  double v2_b=v123_b[1];
  double v3_b=v123_b[2];
  for(int u=0;u<N_cgtos;u++){
    if(env.u_cutoff_flag[u*3+0]==1 || env.u_cutoff_flag[u*3+1]==1 || (flag_gga==1 && env.u_cutoff_flag[u*3+2]==1) ){
      for(int v=u;v<N_cgtos_pbc;v++){
        if(mode_pbc==0){
          vDuv_v1    = -0.5*(v1_a*Da_PBC[0]->get_value(u,v) + v1_b*Db_PBC[0]->get_value(u,v));
          vDuv_v23_x = -0.5*( (v2_a*rou_deri_a[0]+v3_b*rou_deri_b[0])*Da_PBC[0]->get_value(u,v)
                             +(v2_b*rou_deri_b[0]+v3_a*rou_deri_a[0])*Db_PBC[0]->get_value(u,v) );
          vDuv_v23_y = -0.5*( (v2_a*rou_deri_a[1]+v3_b*rou_deri_b[1])*Da_PBC[0]->get_value(u,v)
                             +(v2_b*rou_deri_b[1]+v3_a*rou_deri_a[1])*Db_PBC[0]->get_value(u,v) );
          vDuv_v23_z = -0.5*( (v2_a*rou_deri_a[2]+v3_b*rou_deri_b[2])*Da_PBC[0]->get_value(u,v)
                             +(v2_b*rou_deri_b[2]+v3_a*rou_deri_a[2])*Db_PBC[0]->get_value(u,v) );
        }else{
          std::cout<<" not implemented yet "<<std::endl;
          exit(1);
        }
        int atom_no_u=env.cgtos_pbc[u].get_atom_no();
        int atom_no_v=env.cgtos_pbc[v].get_atom_no();
        if(atom_no_u<N_atoms){
          ret_grad[atom_no_u*3+0]+=vDuv_v1*env.str_v_ao.ao[v]*env.str_v_ao.deri[u*3+0];    
          ret_grad[atom_no_u*3+1]+=vDuv_v1*env.str_v_ao.ao[v]*env.str_v_ao.deri[u*3+1];    
          ret_grad[atom_no_u*3+2]+=vDuv_v1*env.str_v_ao.ao[v]*env.str_v_ao.deri[u*3+2];   
          if(u!=v){
            ret_grad[atom_no_u*3+0]+=vDuv_v1*env.str_v_ao.ao[v]*env.str_v_ao.deri[u*3+0];    
            ret_grad[atom_no_u*3+1]+=vDuv_v1*env.str_v_ao.ao[v]*env.str_v_ao.deri[u*3+1];    
            ret_grad[atom_no_u*3+2]+=vDuv_v1*env.str_v_ao.ao[v]*env.str_v_ao.deri[u*3+2];   
          } 
        }
        if(atom_no_v<N_atoms){
          ret_grad[atom_no_v*3+0]+=vDuv_v1*env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+0];    
          ret_grad[atom_no_v*3+1]+=vDuv_v1*env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+1];    
          ret_grad[atom_no_v*3+2]+=vDuv_v1*env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+2]; 
          if(u!=v){
            ret_grad[atom_no_v*3+0]+=vDuv_v1*env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+0];    
            ret_grad[atom_no_v*3+1]+=vDuv_v1*env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+1];    
            ret_grad[atom_no_v*3+2]+=vDuv_v1*env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+2]; 
          }
        }   
        if(flag_gga==1){
          double xx,xy,xz,yx,yy,yz,zx,zy,zz;
          if(atom_no_u<N_atoms){
            xx=(env.str_v_ao.deri[u*3+0]*env.str_v_ao.deri[v*3+0]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+0]);
            xy=(env.str_v_ao.deri[u*3+0]*env.str_v_ao.deri[v*3+1]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+1]);
            xz=(env.str_v_ao.deri[u*3+0]*env.str_v_ao.deri[v*3+2]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+2]);
            yx=(env.str_v_ao.deri[u*3+1]*env.str_v_ao.deri[v*3+0]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+1]);
            yy=(env.str_v_ao.deri[u*3+1]*env.str_v_ao.deri[v*3+1]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+3]);
            yz=(env.str_v_ao.deri[u*3+1]*env.str_v_ao.deri[v*3+2]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+4]);
            zx=(env.str_v_ao.deri[u*3+2]*env.str_v_ao.deri[v*3+0]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+2]);
            zy=(env.str_v_ao.deri[u*3+2]*env.str_v_ao.deri[v*3+1]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+4]);
            zz=(env.str_v_ao.deri[u*3+2]*env.str_v_ao.deri[v*3+2]+env.str_v_ao.ao[v]*env.str_v_ao.deri2[u*6+5]);
            ret_grad[atom_no_u*3+0]+=vDuv_v23_x*xx+vDuv_v23_y*xy+vDuv_v23_z*xz;
            ret_grad[atom_no_u*3+1]+=vDuv_v23_x*yx+vDuv_v23_y*yy+vDuv_v23_z*yz;
            ret_grad[atom_no_u*3+2]+=vDuv_v23_x*zx+vDuv_v23_y*zy+vDuv_v23_z*zz;
            if(u!=v){
              ret_grad[atom_no_u*3+0]+=vDuv_v23_x*xx+vDuv_v23_y*xy+vDuv_v23_z*xz;
              ret_grad[atom_no_u*3+1]+=vDuv_v23_x*yx+vDuv_v23_y*yy+vDuv_v23_z*yz;
              ret_grad[atom_no_u*3+2]+=vDuv_v23_x*zx+vDuv_v23_y*zy+vDuv_v23_z*zz;
            }
          }
          if(atom_no_v<N_atoms){
            xx=(env.str_v_ao.deri[v*3+0]*env.str_v_ao.deri[u*3+0]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+0]);
            xy=(env.str_v_ao.deri[v*3+0]*env.str_v_ao.deri[u*3+1]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+1]);
            xz=(env.str_v_ao.deri[v*3+0]*env.str_v_ao.deri[u*3+2]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+2]);
            yx=(env.str_v_ao.deri[v*3+1]*env.str_v_ao.deri[u*3+0]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+1]);
            yy=(env.str_v_ao.deri[v*3+1]*env.str_v_ao.deri[u*3+1]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+3]);
            yz=(env.str_v_ao.deri[v*3+1]*env.str_v_ao.deri[u*3+2]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+4]);
            zx=(env.str_v_ao.deri[v*3+2]*env.str_v_ao.deri[u*3+0]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+2]);
            zy=(env.str_v_ao.deri[v*3+2]*env.str_v_ao.deri[u*3+1]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+4]);
            zz=(env.str_v_ao.deri[v*3+2]*env.str_v_ao.deri[u*3+2]+env.str_v_ao.ao[u]*env.str_v_ao.deri2[v*6+5]);
            ret_grad[atom_no_v*3+0]+=vDuv_v23_x*xx+vDuv_v23_y*xy+vDuv_v23_z*xz;
            ret_grad[atom_no_v*3+1]+=vDuv_v23_x*yx+vDuv_v23_y*yy+vDuv_v23_z*yz;
            ret_grad[atom_no_v*3+2]+=vDuv_v23_x*zx+vDuv_v23_y*zy+vDuv_v23_z*zz;
            if(u!=v){
              ret_grad[atom_no_v*3+0]+=vDuv_v23_x*xx+vDuv_v23_y*xy+vDuv_v23_z*xz;
              ret_grad[atom_no_v*3+1]+=vDuv_v23_x*yx+vDuv_v23_y*yy+vDuv_v23_z*yz;
              ret_grad[atom_no_v*3+2]+=vDuv_v23_x*zx+vDuv_v23_y*zy+vDuv_v23_z*zz;
            }
          }
        }
      }
    }
  }
}

template <typename M_tmpl,typename Integ1e> 
void Grid_Inte<M_tmpl,Integ1e>::cal_rou_ab(str_Rou &ret_a, str_Rou &ret_b, const std::vector<M_tmpl*> &Da_PBC, const std::vector<M_tmpl*> &Db_PBC, const Env &env)
                          
{
                          
  int N_cgtos=Da_PBC[0]->get_I();
  ret_a.rou=0.0; ret_a.deri[0]=0.0;  ret_a.deri[1]=0.0;  ret_a.deri[2]=0.0; 
  ret_b.rou=0.0; ret_b.deri[0]=0.0;  ret_b.deri[1]=0.0;  ret_b.deri[2]=0.0; 
  if(mode_pbc==0){ // for molecule
    for(int u=0;u<N_cgtos;u++){
      if(env.u_cutoff_flag[u*3+0]==1 || env.u_cutoff_flag[u*3+1]==1){
        for(int v=u+1;v<N_cgtos;v++){
          double Da_uv2=2.0*Da_PBC[0]->get_value(u,v);
          double Db_uv2=2.0*Db_PBC[0]->get_value(u,v);
          ret_a.rou+=Da_uv2*env.str_v_ao.ao[u]*env.str_v_ao.ao[v];
          ret_b.rou+=Db_uv2*env.str_v_ao.ao[u]*env.str_v_ao.ao[v];
          if(mode_grad==1 || flag_gga==1){
            ret_a.deri[0]+=Da_uv2*(env.str_v_ao.deri[u*3+0]*env.str_v_ao.ao[v]+env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+0]);
            ret_a.deri[1]+=Da_uv2*(env.str_v_ao.deri[u*3+1]*env.str_v_ao.ao[v]+env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+1]);
            ret_a.deri[2]+=Da_uv2*(env.str_v_ao.deri[u*3+2]*env.str_v_ao.ao[v]+env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+2]);
            ret_b.deri[0]+=Db_uv2*(env.str_v_ao.deri[u*3+0]*env.str_v_ao.ao[v]+env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+0]);
            ret_b.deri[1]+=Db_uv2*(env.str_v_ao.deri[u*3+1]*env.str_v_ao.ao[v]+env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+1]);
            ret_b.deri[2]+=Db_uv2*(env.str_v_ao.deri[u*3+2]*env.str_v_ao.ao[v]+env.str_v_ao.ao[u]*env.str_v_ao.deri[v*3+2]);
          }
        }
        double Da_uu=Da_PBC[0]->get_value(u,u);
        double Db_uu=Db_PBC[0]->get_value(u,u);
        ret_a.rou+=Da_uu*env.str_v_ao.ao[u]*env.str_v_ao.ao[u];
        ret_b.rou+=Db_uu*env.str_v_ao.ao[u]*env.str_v_ao.ao[u];
        if(mode_grad==1 || flag_gga==1){
          ret_a.deri[0]+=Da_uu*(env.str_v_ao.deri[u*3+0]*env.str_v_ao.ao[u]+env.str_v_ao.ao[u]*env.str_v_ao.deri[u*3+0]);
          ret_a.deri[1]+=Da_uu*(env.str_v_ao.deri[u*3+1]*env.str_v_ao.ao[u]+env.str_v_ao.ao[u]*env.str_v_ao.deri[u*3+1]);
          ret_a.deri[2]+=Da_uu*(env.str_v_ao.deri[u*3+2]*env.str_v_ao.ao[u]+env.str_v_ao.ao[u]*env.str_v_ao.deri[u*3+2]);
          ret_b.deri[0]+=Db_uu*(env.str_v_ao.deri[u*3+0]*env.str_v_ao.ao[u]+env.str_v_ao.ao[u]*env.str_v_ao.deri[u*3+0]);
          ret_b.deri[1]+=Db_uu*(env.str_v_ao.deri[u*3+1]*env.str_v_ao.ao[u]+env.str_v_ao.ao[u]*env.str_v_ao.deri[u*3+1]);
          ret_b.deri[2]+=Db_uu*(env.str_v_ao.deri[u*3+2]*env.str_v_ao.ao[u]+env.str_v_ao.ao[u]*env.str_v_ao.deri[u*3+2]);
        }
      }
    }
  }else{ // for pbc
    std::cout<<" not implemented yet "<<std::endl;
    exit(1);
  }
}


template <typename M_tmpl,typename Integ1e> 
void Grid_Inte<M_tmpl,Integ1e>::grid_inte_sub_Matrix(double &ret_omp_ene, std::vector<M_tmpl*> &ret_Vxc, 
                                     const std::vector<M_tmpl*> &D, const GInte_Functor &functor, const Env &env)
                                    
{

  //  calculation for rou, deri_rou
  str_Rou str_rou;
  cal_rou(str_rou, D, env);
//  cal_rou(str_rou.rou, str_rou.deri, D, env);

  if(str_rou.rou>CUTOFF_DFT){
    std::vector<double> v123(3, 0.0);
    double tmp_ene;
    functor(tmp_ene, v123, str_rou.rou, str_rou.deri);
    double integ_w=env.integ_w;
    ret_omp_ene+=tmp_ene*integ_w;
    v123[0]*=integ_w; v123[1]*=integ_w; v123[2]*=integ_w;
    CTRL_PBC tmp_ctrl_pbc;
    cal_Vxc_sub(ret_Vxc, str_rou, &v123[0], tmp_ctrl_pbc, env);
  }

}


template <typename M_tmpl,typename Integ1e>
void Grid_Inte<M_tmpl,Integ1e>::grid_inte_sub_grad(std::vector<double> &ret_grad, const std::vector<M_tmpl*> &D,  const GInte_Functor &functor,const Env &env)
                                   
{

  str_Rou str_rou;
  //  calculation for rou, deri_rou
  cal_rou(str_rou, D, env);
//  cal_rou(str_rou.rou, str_rou.deri, D, env);

  if(str_rou.rou>CUTOFF_DFT){
    std::vector<double> v123(3, 0.0);
    double tmp_ene;
    functor(tmp_ene, v123, str_rou.rou, str_rou.deri);

    double integ_w=env.integ_w;
    v123[0]*=integ_w; v123[1]*=integ_w; v123[2]*=integ_w;
    CTRL_PBC tmp_ctrl_pbc;
    cal_grad_sub(ret_grad, D,  str_rou.deri, &v123[0], tmp_ctrl_pbc, env);
  }

}



template <typename M_tmpl,typename Integ1e> 
void Grid_Inte<M_tmpl,Integ1e>::grid_inte_sub_Matrix_u(double &ret_omp_ene, std::vector<M_tmpl*> &ret_Vxc_a, std::vector<M_tmpl*> &ret_Vxc_b, 
                                       const std::vector<M_tmpl*> &Da, const std::vector<M_tmpl*> &Db, const GInte_Functor &functor, const Env &env)
                                      
                                      
{

  str_Rou str_rou_a, str_rou_b;  
  //  calculation for rou, deri_rou
  cal_rou_ab(str_rou_a, str_rou_b, Da, Db, env);

  if(str_rou_a.rou>CUTOFF_DFT || str_rou_b.rou>CUTOFF_DFT){

    std::vector<double> v123_a(3, 0.0);
    std::vector<double> v123_b(3, 0.0);
    double tmp_ene;
    functor(tmp_ene, v123_a, v123_b, str_rou_a.rou, str_rou_a.deri, str_rou_b.rou, str_rou_b.deri);
    double integ_w=env.integ_w;
    ret_omp_ene+=tmp_ene*integ_w;
    v123_a[0]*=integ_w; v123_a[1]*=integ_w; v123_a[2]*=integ_w;
    v123_b[0]*=integ_w; v123_b[1]*=integ_w; v123_b[2]*=integ_w; 
    CTRL_PBC tmp_ctrl_pbc;
    cal_Vxc_sub(ret_Vxc_a, ret_Vxc_b, str_rou_a, str_rou_b,  &v123_a[0], &v123_b[0], tmp_ctrl_pbc, env); 
               
  }

}


template <typename M_tmpl,typename Integ1e>
void Grid_Inte<M_tmpl,Integ1e>::grid_inte_sub_grad_u(std::vector<double> &ret_grad, const std::vector<M_tmpl*> &Da, const std::vector<M_tmpl*> &Db, 
                                     const GInte_Functor &functor,  const Env &env)
                                     
{

  str_Rou str_rou_a, str_rou_b;  
  //  calculation for rou, deri_rou
  cal_rou_ab(str_rou_a, str_rou_b, Da, Db, env);

  if(str_rou_a.rou>CUTOFF_DFT || str_rou_b.rou>CUTOFF_DFT){
    std::vector<double> v123_a(3, 0.0);
    std::vector<double> v123_b(3, 0.0);
    double tmp_ene;
    functor(tmp_ene, v123_a, v123_b, str_rou_a.rou, str_rou_a.deri, str_rou_b.rou, str_rou_b.deri);
    double integ_w=env.integ_w;
    v123_a[0]*=integ_w; v123_a[1]*=integ_w; v123_a[2]*=integ_w;
    v123_b[0]*=integ_w; v123_b[1]*=integ_w; v123_b[2]*=integ_w; 
    CTRL_PBC tmp_ctrl_pbc;
    cal_grad_sub(ret_grad, Da, Db,  str_rou_a.deri, str_rou_b.deri, &v123_a[0], &v123_b[0], tmp_ctrl_pbc, env);
                
  }

}


template <typename M_tmpl,typename Integ1e>
void Grid_Inte<M_tmpl,Integ1e>::grid_inte_sub_Matrix_PBC(double &ret_omp_ene, std::vector<M_tmpl*> &ret_Vxc_PBC, const str_Rou_pbc &str_rou_pbc,
                                         const std::vector<M_tmpl*> &D_PBC, const GInte_Functor &functor, const CTRL_PBC &ctrl_pbc, const Env &env)
                                    
{

  //  read rou, deri_rou
  int N_atoms=env.N_atoms;
  int Ng     =grid_data.get_total_grid();
  int  g     =env.loop_g;
  int  a     =env.loop_a;
  double integ_w = env.integ_w;
  std::vector<double> rou_deri(3, 0.0);

  int an=(a%N_atoms)*Ng+g;
  double rou=str_rou_pbc.rou[an];
  if(mode_grad==1 || flag_gga==1){
    rou_deri[0]=str_rou_pbc.rou_deri[an*3+0];
    rou_deri[1]=str_rou_pbc.rou_deri[an*3+1];
    rou_deri[2]=str_rou_pbc.rou_deri[an*3+2];  
  }
  double v123[3]={0.0};
  v123[0]=str_rou_pbc.v123[an*3+0];
  v123[1]=str_rou_pbc.v123[an*3+1];
  v123[2]=str_rou_pbc.v123[an*3+2];
  if(a<N_atoms)  ret_omp_ene+=str_rou_pbc.ene_pbc[an]*integ_w;

  if(rou>CUTOFF_DFT){
    str_Rou tmp_str_rou;
    tmp_str_rou.rou=rou;
    tmp_str_rou.deri[0]=rou_deri[0];
    tmp_str_rou.deri[1]=rou_deri[1];
    tmp_str_rou.deri[2]=rou_deri[2];
    v123[0]*=integ_w; v123[1]*=integ_w; v123[2]*=integ_w;
    cal_Vxc_sub(ret_Vxc_PBC, tmp_str_rou, v123, ctrl_pbc, env);
  }

}




template <typename M_tmpl,typename Integ1e>
double Grid_Inte<M_tmpl,Integ1e>::grid_integral_base(std::vector<M_tmpl*> &ret_Vxc_a_PBC, std::vector<M_tmpl*> &ret_Vxc_b_PBC, std::vector<double> &ret_grad,
                                     const std::vector<M_tmpl*> &Da_PBC, const std::vector<M_tmpl*> &Db_PBC,
                                     const std::vector<Shell_Cgto> &scgtos, const GInte_Functor &functor, const CTRL_PBC &ctrl_pbc)
{

  using namespace std;

  int N_process=1;
  int process_num=0;
  Util_MPI::get_size_rank(N_process,process_num);

  // set variables
  int N_cgtos  = Util_GTO::get_N_cgtos(scgtos);
  std::vector<int> n_zero(3,0);
  int zero_q=ctrl_pbc.get_zero_qc();
  int N123_c=ctrl_pbc.get_N123_c();
  int N_atoms=Util_GTO::get_N_atoms(scgtos);
  std::vector<double> Rxyz = Util_GTO::get_Rxyz(scgtos);
  if(functor.get_flag_gga()==1) mode_deri=1;

  // set zero
  double ret_ene=0.0;
  if(mode_grad==MATRIX){
    ret_Vxc_a_PBC.reserve(N123_c);
    ret_Vxc_b_PBC.reserve(N123_c);
    for(int i=0;i<N123_c;i++){
      ret_Vxc_a_PBC[i]->set_IJ(N_cgtos,N_cgtos);
      if(mode_unrestricted==UNRESTRICTED) ret_Vxc_b_PBC[i]->set_IJ(N_cgtos,N_cgtos);
    }
  } else if(mode_grad==GRADIENT){
    ret_grad.clear();
    ret_grad.reserve(3*N_atoms);
    for(int i=0;i<N_atoms*3;i++) ret_grad.push_back(0.0); 
  }

  if(functor.get_use_grid_inte()==0) return 0.0;

  // construct base-grid
  std::vector<double> xyzw_g;
  grid_data.get_grid(xyzw_g);

  // preparation of Rxyz_pbc 
  int N_A=N_atoms*N123_c;
  std::vector<double> Rxyz_pbc, r_ab;
  set_Rxyz_pbc(Rxyz_pbc, r_ab, Rxyz, ctrl_pbc);


  // calculate rou for PBC
  int Ng = grid_data.get_total_grid();

  // set rou_pbc 
  time_t start_t2,stop_t2;
  time(&start_t2);
  str_Rou_pbc str_rou_pbc;
  if(mode_pbc==PBC && mode_unrestricted==RESTRICTED){
    set_rou_grid_for_PBC(str_rou_pbc, scgtos, Da_PBC, Rxyz, ctrl_pbc, functor);
  }
  time(&stop_t2);
  if(process_num==0) std::cout<<"  time: "<<difftime(stop_t2,start_t2)<<std::endl;

  //  preparation of cgtos
  std::vector<Shell_Cgto> tsc = Util_GTO::get_scgtos_PBC(scgtos, ctrl_pbc.get_max_Nc(), ctrl_pbc.get_T123() );
  std::vector<Cgto> cgtos_pbc = Util_GTO::get_cgtos<Integ1e>(tsc);
  for(int i=0;i<tsc.size();i++) tsc[i].set_dI<Integ1e>();

  time_t start_t,stop_t;
  time(&start_t);

  #ifdef _OPENMP
  #pragma omp parallel
  { // start of Open-MP parallel-loop
  int N_threads =omp_get_num_threads();
  int thread_num=omp_get_thread_num();
  #else
  int N_threads=1;
  int thread_num=0;
  #endif
  int N_cores=N_process*N_threads;
  int core_num=process_num*N_threads+thread_num;
  if(thread_num==0 && process_num==0) 
    std::cout<<"    Grid-integ(N_process="<<N_process<<", N_threads="<<N_threads<<") mode_unrestricted="
             <<mode_unrestricted<<" : "<<std::flush;

  std::vector<M_tmpl*> omp_Vxc_a_PBC(N123_c), omp_Vxc_b_PBC(N123_c);
  std::vector<M_tmpl>  tmp_Vxc_a_PBC(N123_c), tmp_Vxc_b_PBC(N123_c);
  for(int t=0;t<=zero_q;t++){
    omp_Vxc_a_PBC[t]=&tmp_Vxc_a_PBC[t];
    omp_Vxc_b_PBC[t]=&tmp_Vxc_b_PBC[t];
    omp_Vxc_a_PBC[t]->set_IJ(N_cgtos, N_cgtos);
    if(mode_unrestricted!=RESTRICTED) omp_Vxc_b_PBC[t]->set_IJ(N_cgtos, N_cgtos);
  }


  //  preparation of env
  Env env;
  env.str_v_ao.initialize_N(N_cgtos*N123_c);
  env.u_cutoff_flag.reserve(N_cgtos*3);
  env.cgtos_pbc=&cgtos_pbc[0];
  env.N_cgtos=N_cgtos;
  env.N_cgtos_pbc=N_cgtos*N123_c;
  env.N_atoms=N_atoms;

  double omp_ene=0.0;
  std::vector<double> omp_grad(N_atoms*3, 0.0);
//  int N_paralles   = N_process;
//  int parallel_num = process_num;
  int N_paralles   = N_cores;
  int parallel_num = core_num;
  if(mode_grad==GRADIENT){
    N_paralles   = N_cores;
    parallel_num = core_num;
  }

  //
  //  grid-loop start
  for(int a=0;a<N_A;a++){
    if(thread_num==0 && process_num==0) std::cout<<a<<" "<<std::flush;
    for(int g=0;g<Ng;g++){
      if((g*N_A+a)%N_paralles==parallel_num){  // mpi+omp or omp
        double integ_w;
        std::vector<double> xyz(3);
        std::vector<double> xyzw_grid = Grid::grid_weight_ATOM(a, Rxyz_pbc, r_ab, g, xyzw_g);
        xyz[0]=xyzw_grid[0]; xyz[1]=xyzw_grid[1]; xyz[2]=xyzw_grid[2]; integ_w=xyzw_grid[3];
        env.integ_w=integ_w;
        if(fabs(integ_w)>CUTOFF_DFT){
          //  calcuation for v_ao, v_ao_deri
          int flag_v_ao=0;
          cal_v_ao(env.str_v_ao, tsc, xyz);
          for(int u=0;u<N_cgtos;u++) if(fabs(env.str_v_ao.ao[u])>CUTOFF_DFT) flag_v_ao=1;
          if(flag_v_ao==1){
            // calcualtion for v_ao_deri
            if(mode_grad==GRADIENT || flag_gga==1)  cal_v_ao_deri(env.str_v_ao, tsc, xyz);
            if(mode_grad==GRADIENT && flag_gga==1)  cal_v_ao_deri2(env.str_v_ao, tsc, xyz);

            // set u_cutoff_flag
            set_u_cutoff_flag(env);

            //
            // calculation -block 
            if(mode_pbc==MOLECULE){  // molecule
              if(mode_unrestricted==RESTRICTED){
                if(mode_grad==MATRIX){ 
             //     grid_inte_sub_Matrix(omp_ene, ret_Vxc_a_PBC, Da_PBC, functor, env);
                  grid_inte_sub_Matrix(omp_ene, omp_Vxc_a_PBC, Da_PBC, functor, env);
                }else{  // gradient
                  grid_inte_sub_grad(omp_grad, Da_PBC, functor, env);
                }
              }else{  // unrestricted
                if(mode_grad==MATRIX){ 
              //    grid_inte_sub_Matrix_u(omp_ene, ret_Vxc_a_PBC, ret_Vxc_b_PBC, Da_PBC, Db_PBC, functor, env);
                  grid_inte_sub_Matrix_u(omp_ene, omp_Vxc_a_PBC, omp_Vxc_b_PBC, Da_PBC, Db_PBC, functor, env);
                }else{  // gradient
                  grid_inte_sub_grad_u(omp_grad, Da_PBC, Db_PBC, functor, env);
                }
              }
            }
            if(mode_pbc==PBC){  // pbc
              if(mode_unrestricted==RESTRICTED){
                if(mode_grad==MATRIX){
                  env.loop_a=a;
                  env.loop_g=g;
               //   grid_inte_sub_Matrix_PBC(omp_ene, ret_Vxc_a_PBC, str_rou_pbc, Da_PBC, functor, ctrl_pbc, env);
                  grid_inte_sub_Matrix_PBC(omp_ene, omp_Vxc_a_PBC, str_rou_pbc, Da_PBC, functor, ctrl_pbc, env);
                }else{
                  if(process_num==0) std::cout<<"  not implemneted yet "<<std::endl;
                }
              }else{
                if(process_num==0) std::cout<<"  not implemneted yet "<<std::endl;
              }
            }
            //
            //

          }  // cutoff_v_ao
        }  // cutoff-integ_w
      }  // if-core_num
    }  // loop-g
  }  // loop-a
//  if(thread_num==0 && process_num==0) cout<<endl;

  #ifdef _OPENMP
  #pragma omp critical(add_grad_grid_integral_DFT)
  #endif
  {
    ret_ene+=omp_ene;

    if(mode_grad==MATRIX){
      for(int t=0;t<=zero_q;t++){
        for(int i=0;i<N_cgtos;i++){
          for(int j=0;j<N_cgtos;j++){
            ret_Vxc_a_PBC[t]->add(i,j,omp_Vxc_a_PBC[t]->get_value(i,j));
            if(mode_unrestricted!=RESTRICTED) ret_Vxc_b_PBC[t]->add(i,j,omp_Vxc_b_PBC[t]->get_value(i,j));
          }
        }
      }
    }
    if(mode_grad==GRADIENT)  for(int i=0;i<3*N_atoms;i++) ret_grad[i]+=omp_grad[i];
  }

  #ifdef _OPENMP
  #pragma omp barrier
  } // end of openMP parallel-loop
  #endif 

  time(&stop_t);
  if(process_num==0) std::cout<<"  time: "<<difftime(stop_t,start_t)<<std::endl;

  #ifdef USE_MPI_LOTUS
  Util_MPI::allreduce(ret_ene);
  if(mode_grad==MATRIX){
    if(mode_unrestricted==RESTRICTED){
//      Util_MPI::allreduce(ret_Vxc_a_PBC); 
      Util_MPI::isendrecv(ret_Vxc_a_PBC); 
    }else{
//      Util_MPI::allreduce(ret_Vxc_a_PBC); 
//      Util_MPI::allreduce(ret_Vxc_b_PBC); 
      Util_MPI::isendrecv(ret_Vxc_a_PBC); 
      Util_MPI::isendrecv(ret_Vxc_b_PBC); 
    }
  }
  if(mode_grad==GRADIENT){
    Util_MPI::allreduce(ret_grad); 
  }
  #endif

  //  symmetry operation
  if(mode_grad==MATRIX){
    for(int u=0;u<N_cgtos;u++){
      for(int v=u;v<N_cgtos;v++){
        if(u!=v){
          double tmp_v_a=ret_Vxc_a_PBC[zero_q]->get_value(u,v);
          ret_Vxc_a_PBC[zero_q]->add(v,u,tmp_v_a); 
          if(mode_unrestricted!=0){
            double tmp_v_b=ret_Vxc_b_PBC[zero_q]->get_value(u,v);
            ret_Vxc_b_PBC[zero_q]->add(v,u,tmp_v_b); 
          }
        }
      }
    }
  }
  if(mode_pbc==PBC && mode_grad==MATRIX){
    for(int q=1;q<=zero_q;q++){
      mat_transpose(*ret_Vxc_a_PBC[zero_q+q],*ret_Vxc_a_PBC[zero_q-q]);
      if(mode_unrestricted!=0)
        mat_transpose(*ret_Vxc_b_PBC[zero_q+q],*ret_Vxc_b_PBC[zero_q-q]);
    }
  }

  // calculate potential energy instead of dft-energy
  if(functor.get_use_potential_energy()==1){
    if(mode_unrestricted==0){
      ret_ene=2.0*Util_PBC::cal_DV(Da_PBC, ret_Vxc_a_PBC, N123_c);
    }else{
      ret_ene=Util_PBC::cal_DV(Da_PBC, ret_Vxc_a_PBC, N123_c)+Util_PBC::cal_DV(Db_PBC, ret_Vxc_b_PBC, N123_c);
    }
  }

  return ret_ene;



}

//
//
//






}  // end of namespace "Lotus_core"

#endif // end of include guard
