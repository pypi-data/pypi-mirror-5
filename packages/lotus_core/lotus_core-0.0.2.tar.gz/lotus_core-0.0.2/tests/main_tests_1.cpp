


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

#include "td_fock1e.h"

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
    if(thread_num==0 && process_num==0) 
      cout<<" ---------- openMP: number of threads = "<<N_threads<<" ----------"<<endl;
  }
  Util_MPI::barrier();
  #endif
  
  int check;
  if(process_num==0) cout<<" ========== td_fock1e_K_mat =========="<<endl;
  Check( td_fock1e_K_mat() );
  
  if(process_num==0) cout<<" ========== td_fock1e_K_mat2 =========="<<endl;
  Check( td_fock1e_K_mat2() );
 
  if(process_num==0) cout<<" ========== td_fock1e_NA_mat =========="<<endl;
  Check( td_fock1e_NA_mat() );

  if(process_num==0) cout<<" ========== td_fock1e_NA_mat2 =========="<<endl;
  Check( td_fock1e_NA_mat2() );

  if(process_num==0) cout<<" ========== td_fock1e_ECP_mat =========="<<endl;
  Check( td_fock1e_ECP_mat() );

  if(process_num==0) cout<<" ========== td_fock1e_ECP_mat2 =========="<<endl;
  Check( td_fock1e_ECP_mat2() );

  if(process_num==0) cout<<" ========== td_fock1e_grad_S =========="<<endl;
  Check( td_fock1e_grad_S() );
 
  if(process_num==0) cout<<" ========== td_fock1e_grad_S2 =========="<<endl;
  Check( td_fock1e_grad_S2() );

  if(process_num==0) cout<<" ========== td_fock1e_grad_K =========="<<endl;
  Check( td_fock1e_grad_K() );

  if(process_num==0) cout<<" ========== td_fock1e_grad_K2 =========="<<endl;
  Check( td_fock1e_grad_K2() );

  if(process_num==0) cout<<" ========== td_fock1e_grad_NA =========="<<endl;
  Check( td_fock1e_grad_NA() );

  if(process_num==0) cout<<" ========== td_fock1e_grad_NA2 =========="<<endl;
  Check( td_fock1e_grad_NA2() );

  if(process_num==0) cout<<" ========== td_fock1e_grad_ECP =========="<<endl;
  Check( td_fock1e_grad_ECP() );

  if(process_num==0) cout<<" ========== td_fock1e_grad_ECP2 =========="<<endl;
  Check( td_fock1e_grad_ECP2() );

  if(process_num==0) cout<<" ========== td_fock1e_K_PBC =========="<<endl;
  Check( td_fock1e_K_PBC() );

  if(process_num==0) cout<<" ========== td_fock1e_K_PBC2 =========="<<endl;
  Check( td_fock1e_K_PBC2() );

  if(process_num==0) cout<<" ========== td_fock1e_NA_PBC =========="<<endl;
  Check( td_fock1e_NA_PBC() );

  if(process_num==0) cout<<" ========== td_fock1e_NA_PBC2 =========="<<endl;
  Check( td_fock1e_NA_PBC2() );

  if(process_num==0) cout<<" ========== td_fock1e_ECP_PBC =========="<<endl;
  Check( td_fock1e_ECP_PBC() );

  if(process_num==0) cout<<" ========== td_fock1e_ECP_PBC2 =========="<<endl;
  Check( td_fock1e_ECP_PBC2() );

  #ifdef USE_MPI_LOTUS
  MPI_Finalize(); 
  #endif
}

