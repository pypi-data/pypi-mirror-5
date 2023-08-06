
#ifdef _OPENMP
#include <omp.h>
#endif

#ifdef USE_MPI_LOTUS
#include "mpi.h"
#endif

#include <sys/time.h>
#include "math.h"
#include "stdlib.h"


#include "PInt.hpp"
#include "Lotus_core.hpp"

#include <iostream>


using namespace std;
using namespace Lotus_core;
using namespace PInt;



int main(){
  Lotus<dMatrix,PInt1e,PInt2e> lts;
  cout<<"   "<<lts.get_N_scgtos()<<endl;
  lts.read_in_file("h2o_sbkjc_plus_d.in"); 
  cout<<"  N_scgtos "<<lts.get_N_scgtos()<<endl;
  cout<<"  N_ecps   "<<lts.get_N_ecps()<<endl;
  cout<<"  N_atoms  "<<lts.get_N_atoms()<<endl;

  dMatrix S;
  lts.cal_matrix("s",S);
  cout<<" ----- S -----"<<endl;
  S.show();
  lts.guess_h_core();
  cout<<" ----- X_a -----"<<endl;
  lts.X_a.show();

  lts.u_guess_h_core();
  cout<<" ----- X_a -----"<<endl;
  lts.X_a.show();
  cout<<" ----- X_b -----"<<endl;
  lts.X_b.show();

  cout<<" ----- lamda_a -----"<<endl;
  for(int i=0;i<lts.lamda_a.size();i++){
    cout<<" i= "<<lts.lamda_a[i]<<endl;
  }
  cout<<" ----- lamda_b -----"<<endl;
  for(int i=0;i<lts.lamda_b.size();i++){
    cout<<" i= "<<lts.lamda_b[i]<<endl;
  }

  HF_Functor functor;
  lts.scf<ERI_direct>(functor);

  std::vector<double> fxyz = lts.cal_force(functor);
  cout<<" ---- force ----"<<endl;
  for(int i=0;i<fxyz.size()/3;i++){
    cout<<" i="<<i<<" fxyz "<<fxyz[i*3+0]<<" "<<fxyz[i*3+1]<<" "<<fxyz[i*3+2]<<endl;
  }


  lts.u_guess_h_core();
  lts.u_scf<ERI_incore>(functor);

  fxyz = lts.cal_force_u(functor);
  cout<<" ---- force ----"<<endl;
  for(int i=0;i<fxyz.size()/3;i++){
    cout<<" i="<<i<<" fxyz "<<fxyz[i*3+0]<<" "<<fxyz[i*3+1]<<" "<<fxyz[i*3+2]<<endl;
  }
}



