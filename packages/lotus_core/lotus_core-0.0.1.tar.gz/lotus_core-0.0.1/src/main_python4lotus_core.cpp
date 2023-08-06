

#ifdef _OPENMP
#include <omp.h>
#endif

#ifdef USE_MPI_LOTUS
#include "mpi.h"
#endif


#include <sys/utsname.h>


#include <iostream>
#include <string>

#include <Python.h>


int main(int argc, char *argv[]){
  using namespace std;


  int process_num=0;
  int thread_num=0;
  int N_threads=1;
  int N_process=1;


  #ifdef USE_MPI_LOTUS
  MPI_Init(&argc,&argv);
  MPI_Comm_rank(MPI_COMM_WORLD,&process_num);
  MPI_Comm_size(MPI_COMM_WORLD,&N_process);
  struct utsname uts;
  uname(&uts);
  cout<<" ========== MPI: number of process "<<N_process<<" process_num "<<process_num
      <<" hostname "<<uts.nodename<<endl;
  Util_MPI::barrier();
  #endif

  #ifdef _OPENMP
  #pragma omp parallel
  {
  N_threads  = omp_get_num_threads();
  thread_num = omp_get_thread_num();
  if(thread_num==0 && process_num==0) 
    cout<<" ========== openMP: number of threads = "<<N_threads<<endl;
  }
  #endif

  Py_SetProgramName(argv[0]);
  string program_full_path=Py_GetProgramFullPath();
  string python_home_path=program_full_path+string("/..");
  Py_SetPythonHome((char *)python_home_path.c_str());

  Py_Initialize();

  PyRun_SimpleString("import os\n");
  PyRun_SimpleString("import sys\n");
  string argv0=argv[0];
  string cmd1="exe_path=os.path.abspath(\""+argv0+"\")\n";
  PyRun_SimpleString(cmd1.c_str());
  string cmd2="exe_dir=os.path.dirname(exe_path)\n";
  PyRun_SimpleString(cmd2.c_str());
  PyRun_SimpleString("lotus_core_dir    =exe_dir+'/..'\n");
  PyRun_SimpleString("lotus_core_lib_dir=exe_dir+'/../lib'\n");
  PyRun_SimpleString("sys.path.append(lotus_core_dir)\n");
  PyRun_SimpleString("sys.path.append(lotus_core_lib_dir)\n");


  Py_Main(argc,argv);
  Py_Finalize();


  #ifdef USE_MPI_LOTUS
  MPI_Finalize();
  #endif


}



