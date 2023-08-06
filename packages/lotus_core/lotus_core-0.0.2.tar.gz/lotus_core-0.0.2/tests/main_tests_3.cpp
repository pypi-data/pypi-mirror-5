


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

#include "td_dft.h"

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
 
  if(process_num==0) cout<<" ========== td_dft_mat_Slater =========="<<endl;
  Check( td_dft_mat_Slater(0) );

  if(process_num==0) cout<<" ========== td_dft_mat_Slater_u =========="<<endl;
  Check( td_dft_mat_Slater(1) );

  if(process_num==0) cout<<" ========== td_dft_mat_B88 =========="<<endl;
  Check( td_dft_mat_B88(0) );

  if(process_num==0) cout<<" ========== td_dft_mat_B88_u =========="<<endl;
  Check( td_dft_mat_B88(1) );

  if(process_num==0) cout<<" ========== td_dft_mat_SVWN =========="<<endl;
  Check( td_dft_mat_SVWN(0) );

  if(process_num==0) cout<<" ========== td_dft_mat_SVWN_u =========="<<endl;
  Check( td_dft_mat_SVWN(1) );

  if(process_num==0) cout<<" ========== td_dft_mat_BLYP =========="<<endl;
  Check( td_dft_mat_BLYP(0) );

  if(process_num==0) cout<<" ========== td_dft_mat_BLYP_u =========="<<endl;
  Check( td_dft_mat_BLYP(1) );

  if(process_num==0) cout<<" ========== td_dft_mat_B3LYP =========="<<endl;
  Check( td_dft_mat_B3LYP(0) );

  if(process_num==0) cout<<" ========== td_dft_mat_B3LYP_u =========="<<endl;
  Check( td_dft_mat_B3LYP(1) );

  // plus_d

  if(process_num==0) cout<<" ========== td_dft_mat_Slater_d =========="<<endl;
  Check( td_dft_mat_Slater_d(0) );

  if(process_num==0) cout<<" ========== td_dft_mat_Slater_du =========="<<endl;
  Check( td_dft_mat_Slater_d(1) );

  if(process_num==0) cout<<" ========== td_dft_mat_B88_d =========="<<endl;
  Check( td_dft_mat_B88_d(0) );

  if(process_num==0) cout<<" ========== td_dft_mat_B88_du =========="<<endl;
  Check( td_dft_mat_B88_d(1) );

  if(process_num==0) cout<<" ========== td_dft_mat_SVWN_d =========="<<endl;
  Check( td_dft_mat_SVWN_d(0) );

  if(process_num==0) cout<<" ========== td_dft_mat_SVWN_du =========="<<endl;
  Check( td_dft_mat_SVWN_d(1) );

  if(process_num==0) cout<<" ========== td_dft_mat_BLYP_d =========="<<endl;
  Check( td_dft_mat_BLYP_d(0) );

  if(process_num==0) cout<<" ========== td_dft_mat_BLYP_du =========="<<endl;
  Check( td_dft_mat_BLYP_d(1) );

  if(process_num==0) cout<<" ========== td_dft_mat_B3LYP_d =========="<<endl;
  Check( td_dft_mat_B3LYP_d(0) );

  if(process_num==0) cout<<" ========== td_dft_mat_B3LYP_du =========="<<endl;
  Check( td_dft_mat_B3LYP_d(1) );

  //
  //  gradient
  //

  if(process_num==0) cout<<" ========== td_dft_grad_Slater =========="<<endl;
  Check( td_dft_grad_Slater(0) );

  if(process_num==0) cout<<" ========== td_dft_grad_Slater_u =========="<<endl;
  Check( td_dft_grad_Slater(1) );

  if(process_num==0) cout<<" ========== td_dft_grad_B88 =========="<<endl;
  Check( td_dft_grad_B88(0) );

  if(process_num==0) cout<<" ========== td_dft_grad_B88_u =========="<<endl;
  Check( td_dft_grad_B88(1) );

  if(process_num==0) cout<<" ========== td_dft_grad_SVWN =========="<<endl;
  Check( td_dft_grad_SVWN(0) );

  if(process_num==0) cout<<" ========== td_dft_grad_SVWN_u =========="<<endl;
  Check( td_dft_grad_SVWN(1) );

  if(process_num==0) cout<<" ========== td_dft_grad_BLYP =========="<<endl;
  Check( td_dft_grad_BLYP(0) );

  if(process_num==0) cout<<" ========== td_dft_grad_BLYP_u =========="<<endl;
  Check( td_dft_grad_BLYP(1) );

  if(process_num==0) cout<<" ========== td_dft_grad_B3LYP =========="<<endl;
  Check( td_dft_grad_B3LYP(0) );

  if(process_num==0) cout<<" ========== td_dft_grad_B3LYP_u =========="<<endl;
  Check( td_dft_grad_B3LYP(1) );

  // plus_d

  if(process_num==0) cout<<" ========== td_dft_grad_Slater_d =========="<<endl;
  Check( td_dft_grad_Slater_d(0) );

  if(process_num==0) cout<<" ========== td_dft_grad_Slater_du =========="<<endl;
  Check( td_dft_grad_Slater_d(1) );

  if(process_num==0) cout<<" ========== td_dft_grad_B88_d =========="<<endl;
  Check( td_dft_grad_B88_d(0) );

  if(process_num==0) cout<<" ========== td_dft_grad_B88_du =========="<<endl;
  Check( td_dft_grad_B88_d(1) );

  if(process_num==0) cout<<" ========== td_dft_grad_SVWN_d =========="<<endl;
  Check( td_dft_grad_SVWN_d(0) );

  if(process_num==0) cout<<" ========== td_dft_grad_SVWN_du =========="<<endl;
  Check( td_dft_grad_SVWN_d(1) );

  if(process_num==0) cout<<" ========== td_dft_grad_BLYP_d =========="<<endl;
  Check( td_dft_grad_BLYP_d(0) );

  if(process_num==0) cout<<" ========== td_dft_grad_BLYP_du =========="<<endl;
  Check( td_dft_grad_BLYP_d(1) );

  if(process_num==0) cout<<" ========== td_dft_grad_B3LYP_d =========="<<endl;
  Check( td_dft_grad_B3LYP_d(0) );

  if(process_num==0) cout<<" ========== td_dft_grad_B3LYP_du =========="<<endl;
  Check( td_dft_grad_B3LYP_d(1) );


  #ifdef USE_MPI_LOTUS
  MPI_Finalize(); 
  #endif

}

