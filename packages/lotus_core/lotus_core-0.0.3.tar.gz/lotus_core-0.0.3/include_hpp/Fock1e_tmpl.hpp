

#ifndef Fock1e_tmpl_H
#define Fock1e_tmpl_H

#include "gto.hpp"
#include "Charge.hpp"
#include "Util_PBC.hpp"
#include "Util_MPI.hpp"

#include <math.h>
#include <iostream>

namespace Lotus_core {



class Fock1e_base {
public:

  enum   METHOD {Overlap=0,Kinetic=1,NA_Normal=2,NA_Erfc=3,NA_Erf=4};

  struct _CTRL {
     METHOD method;
     int  qc;
     // NA
     double omega;
     double Z;
     std::vector<double> Rc;
     // NA-gradient
     int  N_atoms;
     int  atom_no;
     _CTRL(){
       atom_no=-1; // must be set -1
       qc=0; omega=0.0; Z=0; N_atoms=0; method=Overlap;
     }
     void show() const {
       std::cout<<" method ="<<method<<"  : Overlap "<<Overlap<<" Kinetic "<<Kinetic
                <<" NA_Normal "<<NA_Normal<<" NA_erfc "<<NA_Erfc<<" NA_erf "<<NA_Erf<<std::endl;
       std::cout<<" qc "<<qc<<" omega "<<omega<<" Z "<<Z<<std::endl;
       if(Rc.size()>=3) std::cout<<" Rc "<<Rc[0]<<" "<<Rc[1]<<" "<<Rc[2]<<std::endl;
       std::cout<<" N_atoms "<<N_atoms<<" atom_no "<<atom_no<<std::endl;
     }
  };

  


};


template <typename M_tmpl,typename Integ1e>
class Fock1e_tmpl : public Fock1e_base{
  double CUTOFF_Fock1e;



  void cal_cutoffM_base(std::vector<M_tmpl*> &cutoffM,const std::vector<Shell_Cgto> &scgtos,const CTRL_PBC &ctrl_pbc);

  // Common
  void cal_shell(std::vector<double> &ret_shell,int p,int q,const std::vector<Shell_Cgto> &scgtos,const CTRL_PBC &ctrl_pbc,const _CTRL &ctrl);
  

  // Overlap,Kinetic base
  void cal_M(M_tmpl &retM,const std::vector<Shell_Cgto> &scgtos,METHOD method){
    CTRL_PBC ctrl_pbc;
    std::vector<M_tmpl*> tmpM(1);
    tmpM[0]=&retM;
    cal_M_base(tmpM,scgtos,method,ctrl_pbc);
  }
  void cal_M_PBC(std::vector<M_tmpl> &retM,const std::vector<Shell_Cgto> &scgtos,METHOD method,const CTRL_PBC &ctrl_pbc){
    int N123_c=ctrl_pbc.get_N123_c();
    retM.clear();
    retM.reserve(N123_c);
    retM.resize(N123_c); 
    std::vector<M_tmpl*> tmpM(N123_c);
    for(int q=0;q<N123_c;q++) tmpM[q]=&retM[q];
     cal_M_base(tmpM,scgtos,method,ctrl_pbc); 
  }
  void cal_M_base(std::vector<M_tmpl*> &retM,const std::vector<Shell_Cgto> &scgtos,METHOD method,const CTRL_PBC &ctrl_pbc);


  // NA base
  void _cal_NA(M_tmpl &retNA,const std::vector<Shell_Cgto> &scgtos,METHOD method,double omega,const std::vector<Charge> &charges){
    CTRL_PBC ctrl_pbc;
    std::vector<M_tmpl*> tmpM(1);
    tmpM[0]=&retNA;
    cal_NA_base(tmpM,scgtos,method,omega,charges,ctrl_pbc);
  }
  void _cal_NA_PBC(std::vector<M_tmpl> &retNA,const std::vector<Shell_Cgto> &scgtos,
                  METHOD method,double omega,const std::vector<Charge> &charges,const CTRL_PBC &ctrl_pbc){
    int N123_c=ctrl_pbc.get_N123_c(); 
    retNA.clear();
    retNA.reserve(N123_c);
    retNA.resize(N123_c); 
    std::vector<M_tmpl*> tmpM(N123_c);
    for(int q=0;q<N123_c;q++) tmpM[q]=&retNA[q];
    cal_NA_base(tmpM,scgtos,method,omega,charges,ctrl_pbc); 
  }

  void cal_NA_base(std::vector<M_tmpl*> &retNA,const std::vector<Shell_Cgto> &scgtos,
                   METHOD method,double omega,const std::vector<Charge> &charges,const CTRL_PBC &ctrl_pbc);


  // gradient_base

  static int get_num(int tn){  return (tn+2)*(tn+1)/2; }

  static std::vector<int> get_n_minus(std::vector<int> n,int xyz){
    std::vector<int> ret_n;
    ret_n.push_back(n[0]);
    ret_n.push_back(n[1]);
    ret_n.push_back(n[2]);
    ret_n[xyz]--;
    return ret_n;
  }
  static std::vector<int> get_n_plus(std::vector<int> n,int xyz){
    std::vector<int> ret_n;
    ret_n.push_back(n[0]);
    ret_n.push_back(n[1]);
    ret_n.push_back(n[2]);
    ret_n[xyz]++;
    return ret_n;
  }

  void cal_grad_shell(std::vector<double> &ret_grad,int p,int q,const std::vector<Shell_Cgto> &scgtos,const std::vector<M_tmpl*> &D_PBC,
                      const _CTRL &ctrl,const CTRL_PBC &ctrl_pbc);

  std::vector<double> cal_grad_base(const std::vector<Shell_Cgto> &scgtos,const std::vector<M_tmpl*> &D_PBC,
                                    METHOD method,const CTRL_PBC &ctrl_pbc);

  std::vector<double> cal_grad(const std::vector<Shell_Cgto> &scgtos,const M_tmpl &D,METHOD method){
    CTRL_PBC ctrl_pbc;
    std::vector<M_tmpl*> tmpD(1);
    tmpD[0]=const_cast<M_tmpl*>(&D);
    return cal_grad_base(scgtos,tmpD,method,ctrl_pbc); 
  }

  std::vector<double> cal_grad_NA_base(const std::vector<Shell_Cgto> &scgtos,const std::vector<M_tmpl*> &D_PBC,
                                       METHOD method,double omega,const std::vector<Charge> &charges,const CTRL_PBC &ctrl_pbc);

  std::vector<double> cal_grad_NA_base2(const std::vector<Shell_Cgto> &scgtos,const M_tmpl &D,
                                        METHOD method,double omega,const std::vector<Charge> &charges){
    CTRL_PBC ctrl_pbc;
    std::vector<M_tmpl*> tmpD(1);
    tmpD[0]=const_cast<M_tmpl*>(&D);
    return cal_grad_NA_base(scgtos,tmpD,method,omega,charges,ctrl_pbc);
  }
  


public:
  Fock1e_tmpl(){
    CUTOFF_Fock1e=1.0e-13;
  }

  void show(){
    std::cout<<" CUTOFF_Fock1e  "<<CUTOFF_Fock1e<<std::endl;
  }
  void set_CUTOFF_Fock1e(double in){ CUTOFF_Fock1e=in; }

  std::vector<double> cal_s_shell(int p,const std::vector<Shell_Cgto> &scgtos){
    std::vector<double> ret_shell;
    CTRL_PBC ctrl_pbc;
    _CTRL ctrl;
    ctrl.method=Overlap;
    cal_shell(ret_shell,p,p,scgtos,ctrl_pbc,ctrl);
    return ret_shell;
  }


  // cutoffM
  void cal_cutoffM(M_tmpl &cutoffM,const std::vector<Shell_Cgto> &scgtos){
    CTRL_PBC ctrl_pbc;
    std::vector<M_tmpl*> tmpM(1);
    tmpM[0]=&cutoffM;
    cal_cutoffM_base(tmpM,scgtos,ctrl_pbc);
  }

  void cal_cutoffM_PBC(std::vector<M_tmpl> &cutoffM,const std::vector<Shell_Cgto> &scgtos,const CTRL_PBC &ctrl_pbc){
    int N123_c=ctrl_pbc.get_N123_c(); 
    cutoffM.clear();
    cutoffM.reserve(N123_c);
    cutoffM.resize(N123_c); 
    std::vector<M_tmpl*> tmpM(N123_c);
    for(int q=0;q<N123_c;q++) tmpM[q]=&cutoffM[q];
    cal_cutoffM_base(tmpM,scgtos,ctrl_pbc);
  }

  // Overlap
  void cal_S(M_tmpl &retS,const std::vector<Shell_Cgto> &scgtos){  cal_M(retS,scgtos,Overlap); }
  void cal_S_PBC(std::vector<M_tmpl> &retS,const std::vector<Shell_Cgto> &scgtos,const std::vector<int> &max_Nc,const std::vector<double> &T123){ 
    CTRL_PBC ctrl_pbc; ctrl_pbc.set_max_Nc(max_Nc); ctrl_pbc.set_T123(T123); cal_M_PBC(retS,scgtos,Overlap,ctrl_pbc); }
  void cal_S_PBC(std::vector<M_tmpl> &retS,const std::vector<Shell_Cgto> &scgtos,const CTRL_PBC &ctrl_pbc){ 
    cal_M_PBC(retS,scgtos,Overlap,ctrl_pbc); }

  // for boost-python
  void _cal_S_PBC_bp1(std::vector<M_tmpl> &retS,const std::vector<Shell_Cgto> &scgtos,const std::vector<int> &max_Nc,const std::vector<double> &T123){ 
    cal_S_PBC(retS,scgtos,max_Nc,T123); } 
  void _cal_S_PBC_bp2(std::vector<M_tmpl> &retS,const std::vector<Shell_Cgto> &scgtos,const CTRL_PBC &ctrl_pbc){ cal_S_PBC(retS,scgtos,ctrl_pbc); }
  //

  // Kinetic
  void cal_K(M_tmpl &retK,const std::vector<Shell_Cgto> &scgtos){  cal_M(retK,scgtos,Kinetic); }
  void cal_K_PBC(std::vector<M_tmpl> &retS,const std::vector<Shell_Cgto> &scgtos,const std::vector<int> &max_Nc,const std::vector<double> &T123){ 
    CTRL_PBC ctrl_pbc; ctrl_pbc.set_max_Nc(max_Nc); ctrl_pbc.set_T123(T123); cal_M_PBC(retS,scgtos,Kinetic,ctrl_pbc); }
  void cal_K_PBC(std::vector<M_tmpl> &retS,const std::vector<Shell_Cgto> &scgtos,const CTRL_PBC &ctrl_pbc){ 
    cal_M_PBC(retS,scgtos,Kinetic,ctrl_pbc); }

  // for boost-python
  void _cal_K_PBC_bp1(std::vector<M_tmpl> &retS,const std::vector<Shell_Cgto> &scgtos,const std::vector<int> &max_Nc,const std::vector<double> &T123){ 
    cal_K_PBC(retS,scgtos,max_Nc,T123); } 
  void _cal_K_PBC_bp2(std::vector<M_tmpl> &retS,const std::vector<Shell_Cgto> &scgtos,const CTRL_PBC &ctrl_pbc){ cal_K_PBC(retS,scgtos,ctrl_pbc); }
  //


  // NA
  void cal_NA(M_tmpl &retNA,const std::vector<Shell_Cgto> &scgtos,const std::vector<Charge> &charges){
    _cal_NA(retNA,scgtos,NA_Normal,0.0,charges); }
  void cal_NA_erfc(M_tmpl &retNA,const std::vector<Shell_Cgto> &scgtos,double omega,const std::vector<Charge> &charges){
    _cal_NA(retNA,scgtos,NA_Erfc,omega,charges); }
  void cal_NA_erf(M_tmpl &retNA,const std::vector<Shell_Cgto> &scgtos,double omega,const std::vector<Charge> &charges){
    _cal_NA(retNA,scgtos,NA_Erf,omega,charges); }

  // NA_PBC 
  void cal_NA_PBC(std::vector<M_tmpl> &retNA,const std::vector<Shell_Cgto> &scgtos,const std::vector<Charge> &charges,
                  const std::vector<int> &max_Nc,const std::vector<int> &max_Nt,const std::vector<double> &T123){    
    CTRL_PBC ctrl_pbc;
    ctrl_pbc.set_max_Nc(max_Nc); ctrl_pbc.set_max_Nt(max_Nt); ctrl_pbc.set_T123(T123); 
    _cal_NA_PBC(retNA,scgtos,NA_Normal,0.0,charges,ctrl_pbc); }
  void cal_NA_PBC(std::vector<M_tmpl> &retNA,const std::vector<Shell_Cgto> &scgtos,const std::vector<Charge> &charges,const CTRL_PBC &ctrl_pbc){   
    _cal_NA_PBC(retNA,scgtos,NA_Normal,0.0,charges,ctrl_pbc); }

  // for boost-python
  void _cal_NA_PBC_bp1(std::vector<M_tmpl> &retNA,const std::vector<Shell_Cgto> &scgtos,const std::vector<Charge> &charges,
                       const std::vector<int> &max_Nc,const std::vector<int> &max_Nt,const std::vector<double> &T123){    
    cal_NA_PBC(retNA,scgtos,charges,max_Nc,max_Nt,T123); }   
  void _cal_NA_PBC_bp2(std::vector<M_tmpl> &retNA,const std::vector<Shell_Cgto> &scgtos,const std::vector<Charge> &charges,const CTRL_PBC &ctrl_pbc){    
    _cal_NA_PBC(retNA,scgtos,NA_Normal,0.0,charges,ctrl_pbc); }
  //
                       

  // NA_erfc_PBC
  void cal_NA_erfc_PBC(std::vector<M_tmpl> &retNA,const std::vector<Shell_Cgto> &scgtos,double omega,const std::vector<Charge> &charges,
                       const std::vector<int> &max_Nc,const std::vector<int> &max_Nt,const std::vector<double> &T123){    
    CTRL_PBC ctrl_pbc;
    ctrl_pbc.set_max_Nc(max_Nc); ctrl_pbc.set_max_Nt(max_Nt); ctrl_pbc.set_T123(T123); 
    _cal_NA_PBC(retNA,scgtos,NA_Erfc,omega,charges,ctrl_pbc); }
  void cal_NA_erfc_PBC(std::vector<M_tmpl> &retNA,const std::vector<Shell_Cgto> &scgtos,double omega,
                       const std::vector<Charge> &charges,const CTRL_PBC &ctrl_pbc){
    _cal_NA_PBC(retNA,scgtos,NA_Erfc,omega,charges,ctrl_pbc); }

  // for boost-python
  void _cal_NA_erfc_PBC_bp1(std::vector<M_tmpl> &retNA,const std::vector<Shell_Cgto> &scgtos,double omega,const std::vector<Charge> &charges,
                       const std::vector<int> &max_Nc,const std::vector<int> &max_Nt,const std::vector<double> &T123){    
    cal_NA_erfc_PBC(retNA,scgtos,omega,charges,max_Nc,max_Nt,T123); }  
  void _cal_NA_erfc_PBC_bp2(std::vector<M_tmpl> &retNA,const std::vector<Shell_Cgto> &scgtos,double omega,
                       const std::vector<Charge> &charges,const CTRL_PBC &ctrl_pbc){
    _cal_NA_PBC(retNA,scgtos,NA_Erfc,omega,charges,ctrl_pbc); }
  //
                       

  // NA_erf
  void cal_NA_erf_PBC(std::vector<M_tmpl> &retNA,const std::vector<Shell_Cgto> &scgtos,double omega,const std::vector<Charge> &charges,
                       const std::vector<int> &max_Nc,const std::vector<int> &max_Nt,const std::vector<double> &T123){    
    CTRL_PBC ctrl_pbc;
    ctrl_pbc.set_max_Nc(max_Nc); ctrl_pbc.set_max_Nt(max_Nt); ctrl_pbc.set_T123(T123); 
    _cal_NA_PBC(retNA,scgtos,NA_Erf,omega,charges,ctrl_pbc); }
  void cal_NA_erf_PBC(std::vector<M_tmpl> &retNA,const std::vector<Shell_Cgto> &scgtos,double omega,
                      const std::vector<Charge> &charges,const CTRL_PBC &ctrl_pbc){
    _cal_NA_PBC(retNA,scgtos,NA_Erf,omega,charges,ctrl_pbc); }

  // for boost-python
  void _cal_NA_erf_PBC_bp1(std::vector<M_tmpl> &retNA,const std::vector<Shell_Cgto> &scgtos,double omega,const std::vector<Charge> &charges,
                       const std::vector<int> &max_Nc,const std::vector<int> &max_Nt,const std::vector<double> &T123){    
    cal_NA_erf_PBC(retNA,scgtos,omega,charges,max_Nc,max_Nt,T123); }   
  void _cal_NA_erf_PBC_bp2(std::vector<M_tmpl> &retNA,const std::vector<Shell_Cgto> &scgtos,double omega,
                      const std::vector<Charge> &charges,const CTRL_PBC &ctrl_pbc){
    _cal_NA_PBC(retNA,scgtos,NA_Erf,omega,charges,ctrl_pbc); }
  //
                       
  //
  //  Gradient
  // 

  // Overlap
  std::vector<double> cal_grad_S(const std::vector<Shell_Cgto> &scgtos,const M_tmpl &D){ return cal_grad(scgtos,D,Overlap); }

  // Kinetic
  std::vector<double> cal_grad_K(const std::vector<Shell_Cgto> &scgtos,const M_tmpl &D){ return cal_grad(scgtos,D,Kinetic); }

  // Nuclear-Atraction
  std::vector<double> cal_grad_NA(const std::vector<Shell_Cgto> &scgtos,const M_tmpl &D,const std::vector<Charge> &charges){
    return cal_grad_NA_base2(scgtos,D,NA_Normal,0.0,charges);
  } 
  std::vector<double> cal_grad_NA_erfc(const std::vector<Shell_Cgto> &scgtos,const M_tmpl &D,double omega,const std::vector<Charge> &charges){
    return cal_grad_NA_base2(scgtos,D,NA_Erfc,omega,charges);
  } 
  std::vector<double> cal_grad_NA_erf(const std::vector<Shell_Cgto> &scgtos,const M_tmpl &D,double omega,const std::vector<Charge> &charges){
    return cal_grad_NA_base2(scgtos,D,NA_Erf,omega,charges);
  } 


};


}  // end of namespace "Lotus_core"



#include "detail/Fock1e_detail.hpp"

#endif // end of include-guard

