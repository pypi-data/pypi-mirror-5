

#ifdef USE_MPI_LOTUS
#include "mpi.h"
#endif


#include <Python.h>


int main(int argc, char *argv[]){

  #ifdef USE_MPI_LOTUS
  MPI_Init(&argc,&argv);
  #endif


  Py_SetProgramName(argv[0]);
  Py_Initialize();
  Py_Main(argc,argv);
  Py_Finalize();


  #ifdef USE_MPI_LOTUS
  MPI_Finalize();
  #endif


}



