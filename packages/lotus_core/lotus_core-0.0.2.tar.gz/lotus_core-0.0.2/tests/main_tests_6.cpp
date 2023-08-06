


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

#include "td_scf.h"

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


  //
  // td_scf_h_core
    
  if(process_num==0) cout<<" ========== td_h_core =========="<<endl;
  Check( td_h_core() );

  if(process_num==0) cout<<" ========== td_h_core_d =========="<<endl;
  Check( td_h_core_d() );

  //
  // guess_h_core

  if(process_num==0) cout<<" ========== td_guess_h_core =========="<<endl;
  Check( td_guess_h_core() );

  if(process_num==0) cout<<" ========== td_guess_h_core_d =========="<<endl;
  Check( td_guess_h_core_d() );

  //
  // fock_sub

  // hf
  if(process_num==0) cout<<" ========== td_fock_sub_direct_hf =========="<<endl;
  Check( td_fock_sub_hf(0, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_direct_hf_d =========="<<endl;
  Check( td_fock_sub_hf(0, 1) );

  if(process_num==0) cout<<" ========== td_fock_sub_file_hf =========="<<endl;
  Check( td_fock_sub_hf(1, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_file_hf_d =========="<<endl;
  Check( td_fock_sub_hf(1, 1) );

  if(process_num==0) cout<<" ========== td_fock_sub_incore_hf =========="<<endl;
  Check( td_fock_sub_hf(2, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_incore_hf_d =========="<<endl;
  Check( td_fock_sub_hf(2, 1) );

  // slater
  if(process_num==0) cout<<" ========== td_fock_sub_direct_slater =========="<<endl;
  Check( td_fock_sub_slater(0, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_direct_slater_d =========="<<endl;
  Check( td_fock_sub_slater(0, 1) );

  if(process_num==0) cout<<" ========== td_fock_sub_file_slater =========="<<endl;
  Check( td_fock_sub_slater(1, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_file_slater_d =========="<<endl;
  Check( td_fock_sub_slater(1, 1) );

  if(process_num==0) cout<<" ========== td_fock_sub_incore_slater =========="<<endl;
  Check( td_fock_sub_slater(2, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_incore_slater_d =========="<<endl;
  Check( td_fock_sub_slater(2, 1) );

  // svwn
  if(process_num==0) cout<<" ========== td_fock_sub_direct_svwn =========="<<endl;
  Check( td_fock_sub_svwn(0, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_direct_svwn_d =========="<<endl;
  Check( td_fock_sub_svwn(0, 1) );

  if(process_num==0) cout<<" ========== td_fock_sub_file_svwn =========="<<endl;
  Check( td_fock_sub_svwn(1, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_file_svwn_d =========="<<endl;
  Check( td_fock_sub_svwn(1, 1) );

  if(process_num==0) cout<<" ========== td_fock_sub_incore_svwn =========="<<endl;
  Check( td_fock_sub_svwn(2, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_incore_svwn_d =========="<<endl;
  Check( td_fock_sub_svwn(2, 1) );


  // b3lyp
  if(process_num==0) cout<<" ========== td_fock_sub_direct_b3lyp =========="<<endl;
  Check( td_fock_sub_b3lyp(0, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_direct_b3lyp_d =========="<<endl;
  Check( td_fock_sub_b3lyp(0, 1) );

  if(process_num==0) cout<<" ========== td_fock_sub_file_b3lyp =========="<<endl;
  Check( td_fock_sub_b3lyp(1, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_file_b3lyp_d =========="<<endl;
  Check( td_fock_sub_b3lyp(1, 1) );

  if(process_num==0) cout<<" ========== td_fock_sub_incore_b3lyp =========="<<endl;
  Check( td_fock_sub_b3lyp(2, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_incore_b3lyp_d =========="<<endl;
  Check( td_fock_sub_b3lyp(2, 1) );

  //
  // scf 
  if(process_num==0) cout<<" ========== td_scf_direct_hf =========="<<endl;
  Check( td_scf_hf(0, 0) );

  if(process_num==0) cout<<" ========== td_scf_direct_hf_d =========="<<endl;
  Check( td_scf_hf(0, 1) );

  if(process_num==0) cout<<" ========== td_scf_file_hf =========="<<endl;
  Check( td_scf_hf(1, 0) );

  if(process_num==0) cout<<" ========== td_scf_file_hf_d =========="<<endl;
  Check( td_scf_hf(1, 1) );

  if(process_num==0) cout<<" ========== td_scf_incore_hf =========="<<endl;
  Check( td_scf_hf(2, 0) );

  if(process_num==0) cout<<" ========== td_scf_incore_hf_d =========="<<endl;
  Check( td_scf_hf(2, 1) );


  if(process_num==0) cout<<" ========== td_scf_direct_svwn =========="<<endl;
  Check( td_scf_svwn(0, 0) );

  if(process_num==0) cout<<" ========== td_scf_direct_svwn_d =========="<<endl;
  Check( td_scf_svwn(0, 1) );


  if(process_num==0) cout<<" ========== td_scf_direct_b88 =========="<<endl;
  Check( td_scf_b88(0, 0) );


  if(process_num==0) cout<<" ========== td_scf_direct_b88_d =========="<<endl;
  Check( td_scf_b88(0, 1) );


  if(process_num==0) cout<<" ========== td_scf_direct_blyp =========="<<endl;
  Check( td_scf_blyp(0, 0) );

  if(process_num==0) cout<<" ========== td_scf_direct_blyp_d =========="<<endl;
  Check( td_scf_blyp(0, 1) );


  if(process_num==0) cout<<" ========== td_scf_direct_b3lyp =========="<<endl;
  Check( td_scf_b3lyp(0, 0) );

  if(process_num==0) cout<<" ========== td_scf_direct_b3lyp_d =========="<<endl;
  Check( td_scf_b3lyp(0, 1) );

  if(process_num==0) cout<<" ========== td_scf_file_b3lyp =========="<<endl;
  Check( td_scf_b3lyp(1, 1) );

  if(process_num==0) cout<<" ========== td_scf_file_b3lyp_d =========="<<endl;
  Check( td_scf_b3lyp(1, 0) );

  if(process_num==0) cout<<" ========== td_scf_incore_b3lyp =========="<<endl;
  Check( td_scf_b3lyp(2, 0) );

  if(process_num==0) cout<<" ========== td_scf_incore_b3lyp_d =========="<<endl;
  Check( td_scf_b3lyp(2, 1) );



  //
  // fock_sub

  // hf
  if(process_num==0) cout<<" ========== td_fock_sub_direct_hf_u =========="<<endl;
  Check( td_fock_sub_hf_u(0, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_direct_hf_du =========="<<endl;
  Check( td_fock_sub_hf_u(0, 1) );

  if(process_num==0) cout<<" ========== td_fock_sub_file_hf_u =========="<<endl;
  Check( td_fock_sub_hf_u(1, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_file_hf_du =========="<<endl;
  Check( td_fock_sub_hf_u(1, 1) );

  if(process_num==0) cout<<" ========== td_fock_sub_incore_hf_u =========="<<endl;
  Check( td_fock_sub_hf_u(2, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_incore_hf_du =========="<<endl;
  Check( td_fock_sub_hf_u(2, 1) );

  // b3lyp
  if(process_num==0) cout<<" ========== td_fock_sub_direct_b3lyp_u =========="<<endl;
  Check( td_fock_sub_b3lyp_u(0, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_direct_b3lyp_du =========="<<endl;
  Check( td_fock_sub_b3lyp_u(0, 1) );

  if(process_num==0) cout<<" ========== td_fock_sub_file_b3lyp_u =========="<<endl;
  Check( td_fock_sub_b3lyp_u(1, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_file_b3lyp_du =========="<<endl;
  Check( td_fock_sub_b3lyp_u(1, 1) );

  if(process_num==0) cout<<" ========== td_fock_sub_incore_b3lyp_u =========="<<endl;
  Check( td_fock_sub_b3lyp_u(2, 0) );

  if(process_num==0) cout<<" ========== td_fock_sub_incore_b3lyp_du =========="<<endl;
  Check( td_fock_sub_b3lyp_u(2, 1) );



  //
  // u_scf 
  if(process_num==0) cout<<" ========== td_scf_direct_hf_u =========="<<endl;
  Check( td_scf_hf_u(0, 0) );

  if(process_num==0) cout<<" ========== td_scf_direct_hf_du =========="<<endl;
  Check( td_scf_hf_u(0, 1) );

  if(process_num==0) cout<<" ========== td_scf_file_hf_u =========="<<endl;
  Check( td_scf_hf_u(1, 0) );

  if(process_num==0) cout<<" ========== td_scf_file_hf_du =========="<<endl;
  Check( td_scf_hf_u(1, 1) );

  if(process_num==0) cout<<" ========== td_scf_incore_hf_u =========="<<endl;
  Check( td_scf_hf_u(2, 0) );

  if(process_num==0) cout<<" ========== td_scf_incore_hf_du =========="<<endl;
  Check( td_scf_hf_u(2, 1) );


  if(process_num==0) cout<<" ========== td_scf_direct_svwn_u =========="<<endl;
  Check( td_scf_svwn_u(0, 0) );

  if(process_num==0) cout<<" ========== td_scf_direct_svwn_du =========="<<endl;
  Check( td_scf_svwn_u(0, 1) );


  if(process_num==0) cout<<" ========== td_scf_direct_b88_u =========="<<endl;
  Check( td_scf_b88_u(0, 0) );

  if(process_num==0) cout<<" ========== td_scf_direct_b88_du =========="<<endl;
  Check( td_scf_b88_u(0, 1) );

  if(process_num==0) cout<<" ========== td_scf_direct_blyp_u =========="<<endl;
  Check( td_scf_blyp_u(0, 0) );

  if(process_num==0) cout<<" ========== td_scf_direct_b3lyp_u =========="<<endl;
  Check( td_scf_b3lyp_u(0, 0) );

  if(process_num==0) cout<<" ========== td_scf_direct_b3lyp_du =========="<<endl;
  Check( td_scf_b3lyp_u(0, 1) );

  if(process_num==0) cout<<" ========== td_scf_file_b3lyp_u =========="<<endl;
  Check( td_scf_b3lyp_u(1, 0) );

  if(process_num==0) cout<<" ========== td_scf_file_b3lyp_du =========="<<endl;
  Check( td_scf_b3lyp_u(1, 1) );

  if(process_num==0) cout<<" ========== td_scf_incore_b3lyp_u =========="<<endl;
  Check( td_scf_b3lyp_u(2, 0) );

  if(process_num==0) cout<<" ========== td_scf_incore_b3lyp_du =========="<<endl;
  Check( td_scf_b3lyp_u(2, 1) );


  if(process_num==0) cout<<" ========== td_scf_direct_hf_ediis =========="<<endl;
  Check( td_scf_hf_ediis(0, 0) );

  if(process_num==0) cout<<" ========== td_scf_direct_hf_ediis_d =========="<<endl;
  Check( td_scf_hf_ediis(0, 1) );

  if(process_num==0) cout<<" ========== td_scf_direct_hf_ediis_u =========="<<endl;
  Check( td_scf_hf_ediis_u(0, 0) );

  if(process_num==0) cout<<" ========== td_scf_direct_hf_ediis_du =========="<<endl;
  Check( td_scf_hf_ediis_u(0, 1) );



  #ifdef USE_MPI_LOTUS
  MPI_Finalize(); 
  #endif

}

