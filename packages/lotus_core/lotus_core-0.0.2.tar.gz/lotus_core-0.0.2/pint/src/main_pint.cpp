
#ifdef _OPENMP
#include <omp.h>
#endif

#ifdef USE_MPI_LOTUS
#include "mpi.h"
#endif

#include <sys/time.h>
#include "math.h"
#include "stdlib.h"

#include "PInt1e.hpp"
#include "PInt2e.hpp"



#include <iostream>
using namespace std;
using namespace PInt;




double performance_check(int max_ijkl,int mode,int max_loop){

  struct timeval start_t,stop_t;
  gettimeofday(&start_t,NULL);


  std::vector<double> Ri(3),Rj(3),Rk(3),Rl(3);
  Ri[0]=0.3;      Ri[1]=0.4;      Ri[2]=0.1;
  Rj[0]=-0.1;     Rj[1]=0.2;      Rj[2]=-0.3;
  Rk[0]=0.5;      Rk[1]=-0.4;     Rk[2]=0.2;
  Rl[0]=0.3;      Rl[1]=-0.2;     Rl[2]=-0.6;

  double gi=0.7;
  double gj=0.6;
  double gk=0.8;
  double gl=0.2;

  PInt2e_base<0>         pint2e_base;
  PInt2e_os_dp           pint2e_os;
  PInt2e_vhrr_dp         pint2e_vhrr;

  if(mode==0){
    pint2e_base.set_gR_12(gi,Ri,gj,Rj);
    pint2e_base.set_gR_34(gk,Rk,gl,Rl);
  }
 
  if(mode==1){
    pint2e_os.set_gR_12(gi,Ri,gj,Rj);
    pint2e_os.set_gR_34(gk,Rk,gl,Rl);
  }

  if(mode==2){
    pint2e_vhrr.set_gR_12(gi,Ri,gj,Rj);
    pint2e_vhrr.set_gR_34(gk,Rk,gl,Rl);
  }

  int     mode_erfc=0;
  double  omega_erfc=0.7;
  std::vector<double> dI_A(100),dI_B(100),dI_C(100),dI_D(100);
  std::vector<double> debug_eri(100000);
  std::vector<double> debug_grad(1000000);


  for(int loop=0;loop<max_loop;loop++){
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

            if(mode==0){
              pint2e_base.set_eri_ssss(tn,mode_erfc,omega_erfc);
              pint2e_base.ERI_recursion(debug_eri,i,j,k,l,dI_A,dI_B,dI_C,dI_D);
            }else if(mode==1){
              pint2e_os.set_eri_ssss(tn,mode_erfc,omega_erfc);
//              pint2e_os.set_flags(i,j,k,l);
              pint2e_os.ERI_init(i,j,k,l);
              pint2e_os.ERI(debug_eri,i,j,k,l,dI_A,dI_B,dI_C,dI_D);
              pint2e_os.ERI_finalize(i,j,k,l);
            }else if(mode==2){
              pint2e_vhrr.set_eri_ssss(tn,mode_erfc,omega_erfc);
//              pint2e_vhrr.set_flags(i,j,k,l);
              pint2e_vhrr.ERI_init(i,j,k,l);
              pint2e_vhrr.ERI(debug_eri,i,j,k,l,dI_A,dI_B,dI_C,dI_D);
              pint2e_vhrr.ERI_finalize(i,j,k,l);
            }else if(mode==3){
              pint2e_os.set_eri_ssss(tn+1,mode_erfc,omega_erfc);
              pint2e_os.grad_init(i, j, k, l);
              pint2e_os.grad_ERI(debug_grad,i,j,k,l,dI_A,dI_B,dI_C,dI_D);
              pint2e_os.grad_finalize(i, j, k, l);
            }else if(mode==4){
              pint2e_vhrr.set_eri_ssss(tn+1,mode_erfc,omega_erfc);
              pint2e_vhrr.grad_init(i, j, k, l);
              pint2e_vhrr.grad_ERI(debug_grad,i,j,k,l,dI_A,dI_B,dI_C,dI_D);
              pint2e_vhrr.grad_finalize(i, j, k, l);
            }
 
          }                              
        }
      }
    }
  }


  gettimeofday(&stop_t,NULL);
  double ret_time=(stop_t.tv_sec  - start_t.tv_sec)
                 +(stop_t.tv_usec - start_t.tv_usec)/1000000.0;
  return ret_time;


}



int main(){

  int check;
  // check for PInt1e
  check = DEBUG_PInt1e::debug_driver_overlap(3); 
  if(check!=0) exit(1);

  check = DEBUG_PInt1e::debug_driver_kinetic(3); 
  if(check!=0) exit(1);

  check = DEBUG_PInt1e::debug_driver_nuclear(3); 
  if(check!=0) exit(1);

  check = DEBUG_PInt1e::debug_driver_nuclear_c(3); 
  if(check!=0) exit(1);

  // check for PInt2e
  PInt2e_base<0>::debug_driver_os_recursion(2);
  if(check!=0) exit(1);

  PInt2e_os_dp::debug_driver_os_dp(3);
  if(check!=0) exit(1);

  PInt2e_vhrr_dp::debug_driver_vhrr_dp(4);
  if(check!=0) exit(1);

  PInt2e_os_dp::debug_driver_grad(2);
  if(check!=0) exit(1);

  PInt2e_vhrr_dp::debug_driver_grad(2);
  if(check!=0) exit(1);

  // perfomance
  cout<<" performance ... until P "<<endl;
  cout<<"   Obara-Saika (recursion)    "<<performance_check(1,0,2000)<<endl;
  cout<<"   Obara-Saika (DP)           "<<performance_check(1,1,2000)<<endl;
  cout<<"   VRR+HRR (DP)               "<<performance_check(1,2,2000)<<endl;

  cout<<" performance ... until D "<<endl;
  cout<<"   Obara-Saika (recursion)    "<<performance_check(2,0,200)<<endl;
  cout<<"   Obara-Saika (DP)           "<<performance_check(2,1,200)<<endl;
  cout<<"   VRR+HRR (DP)               "<<performance_check(2,2,200)<<endl;

  cout<<" performance ... until F "<<endl;
  cout<<"   Obara-Saika (recursion)    "<<performance_check(3,0,10)<<endl;
  cout<<"   Obara-Saika (DP)           "<<performance_check(3,1,10)<<endl;
  cout<<"   VRR+HRR (DP)               "<<performance_check(3,2,10)<<endl;

  cout<<" performance ... until G "<<endl;
  cout<<"   Obara-Saika (DP)           "<<performance_check(4,1,10)<<endl;
  cout<<"   VRR+HRR (DP)               "<<performance_check(4,2,10)<<endl;

  cout<<" performance grad ... until P "<<endl;
  cout<<"   Obara-Saika (DP)           "<<performance_check(1,3,2000)<<endl;
  cout<<"   VRR+HRR (DP)               "<<performance_check(1,4,2000)<<endl;

  cout<<" performance grad ... until D "<<endl;
  cout<<"   Obara-Saika (DP)           "<<performance_check(2,3,200)<<endl;
  cout<<"   VRR+HRR (DP)               "<<performance_check(2,4,200)<<endl;

  cout<<" performance grad ... until F "<<endl;
  cout<<"   Obara-Saika (DP)           "<<performance_check(3,3,10)<<endl;
  cout<<"   Obara-Saika (DP)           "<<performance_check(3,4,10)<<endl;

}
