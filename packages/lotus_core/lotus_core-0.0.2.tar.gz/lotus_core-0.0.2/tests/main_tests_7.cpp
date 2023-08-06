

#ifdef _OPENMP
#include <omp.h>
#endif

#ifdef USE_MPI_LOTUS
#include "mpi.h"
#endif

#include <sys/time.h>
#include <sys/utsname.h>

#include "math.h"
#include "stdlib.h"

#include "td_gradient.h"

#include <iostream>
using namespace std;



void Check(int check){
  int process_num = Util_MPI::get_mpi_rank();
  if(check){  
    if(process_num==0) cout<<" ******* ERROR !! "<<endl;
    exit(1);
  }else{
    if(process_num==0) cout<<" ok "<<endl;
  }
}


int main(int argc,char *argv[]){

  int N_process=1;
  int process_num=0;
  #ifdef USE_MPI_LOTUS
  MPI_Init(&argc,&argv);
  Util_MPI::set_MPI_COMM_LOTUS();
  N_process   = Util_MPI::get_mpi_size();
  process_num = Util_MPI::get_mpi_rank();
  struct utsname uts;
  uname(&uts);
  if(process_num==0)
    cout<<" /////////// MPI: number of process "<<N_process<<" hostname "<<uts.nodename<<" //////////"<<endl;
  Util_MPI::barrier();
  #endif

  #ifdef _OPENMP
  #pragma omp parallel
  {
  int N_threads  = omp_get_num_threads();
  int thread_num = omp_get_thread_num();
  if(thread_num==0) 
    cout<<" ---------- openMP: number of threads = "<<N_threads<<" ----------"<<endl;
  }
  #endif

  if(process_num==0) cout<<" ========== td_grad_hf =========="<<endl;
  Check( td_grad_hf(0) );

  if(process_num==0) cout<<" ========== td_grad_hf_u =========="<<endl;
  Check( td_grad_hf(1) );

  if(process_num==0) cout<<" ========== td_grad_hf_d =========="<<endl;
  Check( td_grad_hf_d(0) );

  if(process_num==0) cout<<" ========== td_grad_hf_du =========="<<endl;
  Check( td_grad_hf_d(1) );

  if(process_num==0) cout<<" ========== td_grad_svwn =========="<<endl;
  Check( td_grad_svwn(0) );

  if(process_num==0) cout<<" ========== td_grad_svwn_u =========="<<endl;
  Check( td_grad_svwn(1) );

  if(process_num==0) cout<<" ========== td_grad_svwn_d =========="<<endl;
  Check( td_grad_svwn_d(0) );

  if(process_num==0) cout<<" ========== td_grad_svwn_du =========="<<endl;
  Check( td_grad_svwn_d(1) );

  if(process_num==0) cout<<" ========== td_grad_blyp_d =========="<<endl;
  Check( td_grad_blyp_d(0) );

  if(process_num==0) cout<<" ========== td_grad_blyp_du =========="<<endl;
  Check( td_grad_blyp_d(1) );

  if(process_num==0) cout<<" ========== td_grad_b3lyp_d =========="<<endl;
  Check( td_grad_b3lyp_d(0) );

  if(process_num==0) cout<<" ========== td_grad_b3lyp_du =========="<<endl;
  Check( td_grad_b3lyp_d(1) );


  #ifdef USE_MPI_LOTUS
  MPI_Finalize(); 
  #endif

}


