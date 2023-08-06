


#ifndef Fock2e_tmpl_H
#define Fock2e_tmpl_H

#include <stdio.h>
#include "unistd.h"

#include "Util_PBC.hpp"
#include "Util_MPI.hpp"
#include "gto.hpp"
#include <iostream>
#include <string>

namespace Lotus_core {



namespace Fock2e_Enum {
  enum MODE    {Normal=0,Erfc=1,Erf=2};
  enum MODE_U  {Restricted=0,Unrestricted=1};
}

struct ERI_data {
  int ij;
  int kl;
  double eri_ijkl;
  ERI_data(int in_ij,int in_kl,double in_eri_ijkl){ ij=in_ij; kl=in_kl; eri_ijkl=in_eri_ijkl; }
};

struct GRAD_data {
  int atom_no;
  int ij;
  int kl;
  double grad_ijkl[3];
  GRAD_data(int in_atom_no,int in_ij,int in_kl,const double in[3]){
    atom_no=in_atom_no;
    ij=in_ij;
    kl=in_kl; 
    grad_ijkl[0]=in[0]; 
    grad_ijkl[1]=in[1]; 
    grad_ijkl[2]=in[2];
  }
};


class  ERI_direct {
  ERI_direct &operator=(ERI_direct &in_m){ mode=Fock2e_Enum::Normal; omega=0.0; return *this;};
  Fock2e_Enum::MODE mode;
  double omega;

public:
  ERI_direct(){  mode=Fock2e_Enum::Normal; omega=0.0; }
  ERI_direct(Fock2e_Enum::MODE in_mode,double in_omega){ mode=in_mode,omega=in_omega; }
  ERI_direct(const ERI_direct &in){  // copy constructor
    int process_num = Util_MPI::get_mpi_rank();
    mode=Fock2e_Enum::Normal;
    omega=0.0; 
    if(process_num==0) std::cout<<" CAUTION!! copy constructor called in ERI_direct class"<<std::endl;
    exit(1);
  }

  Fock2e_Enum::MODE get_mode() const {   return mode; }
  double            get_omega() const {  return omega; }

  void show() const {
    std::cout<<"   ERI_direct: mode "<<mode<<" omega "<<omega
             <<" Fock2e_Enum::MODE, Normal "<<Fock2e_Enum::Normal<<" Erfc "<<Fock2e_Enum::Erfc<<" Erf "<<Fock2e_Enum::Erf<<std::endl;    
  }
};


template <typename T>
struct File_No_static{
  static int file_no;
};

template <typename T>
int File_No_static<T>::file_no=0;


class  ERI_file {
  std::string filename;
  ERI_file &operator=(ERI_file &in_m){ mode=Fock2e_Enum::Normal; omega=0.0; filename=""; return *this; };
  File_No_static<int> file_no_static;
  Fock2e_Enum::MODE mode;
  double omega;
  void set_file(){
    int process_num = Util_MPI::get_mpi_rank();

    std::string work_dir="";
    if(getenv("WORK_LOTUS")!=NULL){
      work_dir=getenv("WORK_LOTUS");
      if(work_dir.size()>0)
        if(work_dir.at(work_dir.size()-1)!='/') work_dir+='/';
    }

    int file_no=file_no_static.file_no;
    char buff[20];
    sprintf(buff,"_tmp_%d_%d_%d_",file_no,(int)getpid(),process_num);

    filename=work_dir+std::string(buff);
   
    #ifdef _OPENMP
    #pragma omp atomic
    #endif
    file_no_static.file_no++; 
  }

public:
  ERI_file(){ mode=Fock2e_Enum::Normal; omega=0.0; set_file(); }
  ERI_file(Fock2e_Enum::MODE in_mode,double in_omega){ mode=in_mode,omega=in_omega; set_file(); }

  ~ERI_file()
  {
    std::string cmd="rm -f "+filename;
    cmd+="*";
    int dmy_int = system(cmd.c_str());
    int process_num = Util_MPI::get_mpi_rank();

    if(process_num==0) std::cout<<"  delete file by ERI_file class : "<<cmd<<std::endl;
  }

  ERI_file(const ERI_file &in)
  {
    int process_num = Util_MPI::get_mpi_rank();
    filename="";
    mode=Fock2e_Enum::Normal;
    omega=0.0; 
    if(process_num==0) std::cout<<" CAUTION!! copy constructor called in ERI_file class"<<std::endl;
    exit(1); 
  }


  std::string get_filename() const {return filename; }
  Fock2e_Enum::MODE get_mode() const {   return mode; }
  double            get_omega() const {  return omega; }
  void show() const {
    std::cout<<"   ERI_file: mode "<<mode<<" omega "<<omega<<" filename "<<filename
             <<"   Fock2e_Enum::MODE, Normal "<<Fock2e_Enum::Normal<<" Erfc "<<Fock2e_Enum::Erfc<<" Erf "<<Fock2e_Enum::Erf<<std::endl;    
  }
};






class ERI_incore {
  int num_data;
  std::vector<ERI_data> *ptr_eri_data;
  ERI_incore &operator=(ERI_incore &in_m){ mode=Fock2e_Enum::Normal; omega=0.0; num_data=0; ptr_eri_data=0; return *this; };
  Fock2e_Enum::MODE mode;
  double omega;
public:
  ERI_incore(){ num_data=0; mode=Fock2e_Enum::Normal; omega=0.0; ptr_eri_data=0; }
  ERI_incore(Fock2e_Enum::MODE in_mode,double in_omega){ num_data=0; mode=in_mode,omega=in_omega; ptr_eri_data=0; }
  ~ERI_incore(){
    clear();
  }

  ERI_incore(const ERI_incore &in)
  {
    int process_num = Util_MPI::get_mpi_rank();
    mode=Fock2e_Enum::Normal;
    omega=0.0;
    num_data=0;
    ptr_eri_data=0;
    if(process_num==0) std::cout<<" CAUTION!! copy constructor called in ERI_incore class"<<std::endl;
    exit(1); 
  }



  void clear(){
    if(num_data>0) delete [] ptr_eri_data;
    num_data=0;
  }
  void set_omp_N_threads(int in){
    clear();
    if(in>0){
      num_data=in;
      ptr_eri_data = new std::vector<ERI_data> [num_data];
    }
  }
  void set_data(int p,int ij,int kl,double eri){
    ptr_eri_data[p].push_back(ERI_data(ij,kl,eri));
  }
  void set_data(int p,ERI_data &in){
    ptr_eri_data[p].push_back(in);
  }
  const std::vector<ERI_data>* get_ptr_eri_data(int p){ return &ptr_eri_data[p]; }

  Fock2e_Enum::MODE get_mode() const {   return mode; }
  double            get_omega() const {  return omega; }
  void show() const {
    std::cout<<"   ERI_incore: mode "<<mode<<" omega "<<omega
             <<" Fock2e_Enum::MODE, Normal "<<Fock2e_Enum::Normal<<" Erfc "<<Fock2e_Enum::Erfc<<" Erf "<<Fock2e_Enum::Erf<<std::endl;    
  }
};





template <typename M_tmpl,typename Integ2e>
class Fock2e_tmpl {
protected:
  double CUTOFF_Fock2e;


  double _omega;
  Fock2e_Enum::MODE   _mode;
  Fock2e_Enum::MODE_U _mode_u;
  void set_mode_clear(){ _mode=Fock2e_Enum::Normal; _mode_u=Fock2e_Enum::Restricted; _omega=0.0; } 
 

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


  void cal_cutoffM_base(std::vector<M_tmpl*> &cutoffM,const std::vector<Shell_Cgto> &scgtos,const CTRL_PBC &ctrl_pbc);
                        

  void cal_eri_shell(std::vector<double> &ret_eri,int p,int q,int r,int s,const std::vector<Shell_Cgto> &scgtos,
                     const std::vector<int> &Q_q, const std::vector<int> &Q_r, const std::vector<int> &Q_s, const CTRL_PBC &ctrl_pbc);


  void cal_eri_shell(std::vector<double> &ret_eri,int p,int q,int r,int s,const std::vector<Shell_Cgto> &scgtos){
    CTRL_PBC ctrl_pbc;
    std::vector<int> Q_q(3,0), Q_r(3,0), Q_s(3,0);
//    std::vector<double>   tmp_eri, dI_1, dI_2, dI_3, dI_4;
//    cal_eri_shell(ret_eri,p,q,r,s,scgtos,Q_q,Q_r,Q_s,ctrl_pbc,tmp_eri,dI_1,dI_2,dI_3,dI_4);
    cal_eri_shell(ret_eri,p,q,r,s,scgtos,Q_q,Q_r,Q_s,ctrl_pbc);
  }


  void set_data_eri(std::vector<ERI_data> &ret_eri_data,int p,int q,int r,int s,
                    const std::vector<Shell_Cgto> &scgtos,const std::vector<double> &eri_shell);

  template <typename M_tmpl2>
  void cal_Vh_and_Vx_sub(M_tmpl2 &Vh,M_tmpl2 &Vx, const M_tmpl &D,const std::vector<ERI_data> &eri_data);

  template <typename M_tmpl2>
  void cal_Vh_and_Vx_sub(M_tmpl2 &Vh,M_tmpl2 &Vx_a,M_tmpl2 &Vx_b, const M_tmpl &Da, const M_tmpl &Db,const std::vector<ERI_data> &eri_data);

  void cal_cutoffD(M_tmpl &cutoffDa, M_tmpl &cutoffDb, const M_tmpl &Da, const M_tmpl &Db,
                   const std::vector<Shell_Cgto> &scgtos);

  bool check_cutoffD(int p, int q, int r, int s, const M_tmpl &cutoffD);

  bool check_cutoffD_ab(int p, int q, int r, int s, const M_tmpl &cutoffDa, const M_tmpl &cutoffDb);

  //  direct                                                 
  void cal_Vh_and_Vx_base(M_tmpl &Vh,M_tmpl &Vx_a,M_tmpl &Vx_b, const M_tmpl &Da, const M_tmpl &Db,const std::vector<Shell_Cgto> &scgtos);
                          
  //  file
  void cal_Vh_and_Vx_from_file_base(M_tmpl &Vh, M_tmpl &Vx_a, M_tmpl &Vx_b, const M_tmpl &Da, const M_tmpl &Db,
                               const std::vector<Shell_Cgto> &scgtos,const ERI_file &eri_file);

  //  incore
  void cal_Vh_and_Vx_from_incore_base(M_tmpl &Vh, M_tmpl &Vx_a, M_tmpl &Vx_b, const M_tmpl &Da, const M_tmpl &Db,
                                      const std::vector<Shell_Cgto> &scgtos, const ERI_incore &eri_incore);


  int cal_n_cgto_pqrs(const std::vector<Shell_Cgto> &scgtos,int p,int q,int r,int s){
    int n_cgto_p=scgtos[p].get_num_cgto();
    int n_cgto_q=scgtos[q].get_num_cgto();
    int n_cgto_r=scgtos[r].get_num_cgto();
    int n_cgto_s=scgtos[s].get_num_cgto();
    int n_cgto_pqrs=n_cgto_p*n_cgto_q*n_cgto_r*n_cgto_s;
    return n_cgto_pqrs;
  }


  // direct
  void cal_Vh_and_Vx_direct_u(M_tmpl &Vh, M_tmpl &Vx_a, M_tmpl &Vx_b, const M_tmpl &Da, const M_tmpl &Db,
                              const std::vector<Shell_Cgto> &scgtos,const ERI_direct &eri_direct){
    _mode=eri_direct.get_mode(); _omega=eri_direct.get_omega(); _mode_u=Fock2e_Enum::Unrestricted;
    cal_Vh_and_Vx_base(Vh,Vx_a,Vx_b,Da,Db,scgtos);
    set_mode_clear();
  }
  
  void cal_Vh_and_Vx_direct(M_tmpl &Vh, M_tmpl &Vx, const M_tmpl &D, const std::vector<Shell_Cgto> &scgtos, const ERI_direct &eri_direct){
    M_tmpl dmyVx,dmyDb;
    _mode=eri_direct.get_mode(); _omega=eri_direct.get_omega(); _mode_u=Fock2e_Enum::Restricted;
    cal_Vh_and_Vx_base(Vh,Vx,dmyVx,D,dmyDb,scgtos); 
    set_mode_clear();
  }

  //  store_eri_to_file 
  void store_eri_to_file(const ERI_file &eri_file,const std::vector<Shell_Cgto> &scgtos);


  void cal_Vh_and_Vx_file_u(M_tmpl &Vh, M_tmpl &Vx_a, M_tmpl &Vx_b, const M_tmpl &Da, const M_tmpl &Db,
                               const std::vector<Shell_Cgto> &scgtos,const ERI_file &eri_file){
    _mode_u=Fock2e_Enum::Unrestricted;
    cal_Vh_and_Vx_from_file_base(Vh,Vx_a,Vx_b,Da,Db,scgtos,eri_file); 
    set_mode_clear();
  }
  void cal_Vh_and_Vx_file(M_tmpl &Vh, M_tmpl &Vx, const M_tmpl &D,const std::vector<Shell_Cgto> &scgtos,const ERI_file &eri_file){
    M_tmpl dumy_Vb,dumy_D;
    _mode_u=Fock2e_Enum::Restricted;
    cal_Vh_and_Vx_from_file_base(Vh,Vx,dumy_Vb,D,dumy_D,scgtos,eri_file); 
    set_mode_clear();
  }
  

  void store_eri_to_incore(ERI_incore &eri_incore,const std::vector<Shell_Cgto> &scgtos);

  void cal_Vh_and_Vx_from_incore_u(M_tmpl &Vh, M_tmpl &Vx_a, M_tmpl &Vx_b, const M_tmpl &Da, const M_tmpl &Db,
                                   const std::vector<Shell_Cgto> &scgtos, const ERI_incore &eri_incore){
    _mode_u=Fock2e_Enum::Unrestricted;
    cal_Vh_and_Vx_from_incore_base(Vh,Vx_a,Vx_b,Da,Db,scgtos,eri_incore);
    set_mode_clear();
  }
  void cal_Vh_and_Vx_from_incore(M_tmpl &Vh, M_tmpl &Vx, const M_tmpl &D, const std::vector<Shell_Cgto> &scgtos, const ERI_incore &eri_incore){
    M_tmpl dumy_Vb,dumy_D;
    _mode_u=Fock2e_Enum::Restricted;
    cal_Vh_and_Vx_from_incore_base(Vh,Vx,dumy_Vb,D,dumy_D,scgtos,eri_incore);
    set_mode_clear();
  }


  
  // Gradeint

  void cal_grad_shell(std::vector<double> &ret_grad_shell,int p,int q,int r,int s,const std::vector<Shell_Cgto> &scgtos);
                      
  void set_data_grad(std::vector<GRAD_data> &ret_grad_data,int p,int q,int r,int s,
                     const std::vector<Shell_Cgto> &scgtos,const std::vector<double> &eri_shell);

  void cal_gradient_sub(std::vector<double> &ret_grad_h,std::vector<double> &ret_grad_x,const M_tmpl &D,
                        const std::vector<GRAD_data> &grad_data);

  void cal_gradient_sub(std::vector<double> &ret_grad_h,std::vector<double> &ret_grad_x,
                        const M_tmpl &Da,const M_tmpl &Db,const std::vector<GRAD_data> &grad_data);

  void cal_grad_base(std::vector<double> &ret_grad_h,std::vector<double> &ret_grad_x,
                     const std::vector<Shell_Cgto> &scgtos,const M_tmpl &Da,const M_tmpl &Db);

public:
  Fock2e_tmpl(){  CUTOFF_Fock2e=1.0e-13; _mode=Fock2e_Enum::Normal; _mode_u=Fock2e_Enum::Restricted; _omega=0.0;  }


  void   set_CUTOFF_Fock2e(double in){  CUTOFF_Fock2e=in; }
  double get_CUTOFF_Fock2e(){  return   CUTOFF_Fock2e;    }
  void   show(){
    std::cout<<"     CUTOFF_Fock2e = "<<CUTOFF_Fock2e<<std::endl;
    std::cout<<"     _mode         = "<<_mode  <<" : Normal=>"<<Fock2e_Enum::Normal<<", Erfc=>"<<Fock2e_Enum::Erfc<<", Erf=>"<<Fock2e_Enum::Erf<<std::endl;
    std::cout<<"     _mode_u       = "<<_mode_u<<" : Restricted=>"<<Fock2e_Enum::Restricted<<", Unrestricted=>"<<Fock2e_Enum::Unrestricted<<std::endl;
  }

  // overload 
  void prepare_eri(ERI_direct &eri_direct,  const std::vector<Shell_Cgto> &scgtos){}  // do nothing
  void prepare_eri(ERI_file   &eri_file,    const std::vector<Shell_Cgto> &scgtos){   store_eri_to_file(eri_file,scgtos); }
  void prepare_eri(ERI_incore &eri_incore,  const std::vector<Shell_Cgto> &scgtos){   store_eri_to_incore(eri_incore,scgtos); }
 
   
  void cal_Vh_and_Vx_u(M_tmpl &Vh, M_tmpl &Vx_a, M_tmpl &Vx_b, const M_tmpl &Da, const M_tmpl &Db,
                       const std::vector<Shell_Cgto> &scgtos, const ERI_direct &eri_direct){
    cal_Vh_and_Vx_direct_u(Vh,Vx_a,Vx_b,Da,Db,scgtos,eri_direct);
  }
  void cal_Vh_and_Vx_u(M_tmpl &Vh, M_tmpl &Vx_a, M_tmpl &Vx_b, const M_tmpl &Da, const M_tmpl &Db,
                       const std::vector<Shell_Cgto> &scgtos, const ERI_file &eri_file){
    cal_Vh_and_Vx_file_u(Vh,Vx_a,Vx_b,Da,Db,scgtos,eri_file);
  }
  void cal_Vh_and_Vx_u(M_tmpl &Vh, M_tmpl &Vx_a, M_tmpl &Vx_b, const M_tmpl &Da, const M_tmpl &Db, 
                       const std::vector<Shell_Cgto> &scgtos, const ERI_incore &eri_incore){
    cal_Vh_and_Vx_from_incore_u(Vh,Vx_a,Vx_b,Da,Db,scgtos,eri_incore);
  }

  void cal_Vh_and_Vx(M_tmpl &Vh, M_tmpl &Vx, const M_tmpl &D, const std::vector<Shell_Cgto> &scgtos, const ERI_direct &eri_direct){
    cal_Vh_and_Vx_direct(Vh,Vx,D,scgtos,eri_direct); }
  void cal_Vh_and_Vx(M_tmpl &Vh, M_tmpl &Vx, const M_tmpl &D,const std::vector<Shell_Cgto> &scgtos, const ERI_file &eri_file){
    cal_Vh_and_Vx_file(Vh,Vx,D,scgtos,eri_file); }
  void cal_Vh_and_Vx(M_tmpl &Vh, M_tmpl &Vx, const M_tmpl &D, const std::vector<Shell_Cgto> &scgtos, const ERI_incore &eri_incore){
    cal_Vh_and_Vx_from_incore(Vh, Vx, D, scgtos, eri_incore); }

  // for boost-python
  void prepare_eri_bp1(ERI_direct &eri_direct,  const std::vector<Shell_Cgto> &scgtos){}  // do nothing
  void prepare_eri_bp2(ERI_file   &eri_file,    const std::vector<Shell_Cgto> &scgtos){   store_eri_to_file(eri_file,scgtos); }
  void prepare_eri_bp3(ERI_incore &eri_incore,  const std::vector<Shell_Cgto> &scgtos){   store_eri_to_incore(eri_incore,scgtos); }
  //

  void cal_Vh_and_Vx_bp1(M_tmpl &Vh, M_tmpl &Vx, const M_tmpl &D, const std::vector<Shell_Cgto> &scgtos, const ERI_direct &eri_direct){
    cal_Vh_and_Vx_direct(Vh,Vx,D,scgtos,eri_direct); }
  void cal_Vh_and_Vx_bp2(M_tmpl &Vh, M_tmpl &Vx, const M_tmpl &D,const std::vector<Shell_Cgto> &scgtos, const ERI_file &eri_file){
    cal_Vh_and_Vx_file(Vh,Vx,D,scgtos,eri_file); }
  void cal_Vh_and_Vx_bp3(M_tmpl &Vh, M_tmpl &Vx, const M_tmpl &D, const std::vector<Shell_Cgto> &scgtos, const ERI_incore &eri_incore){
    cal_Vh_and_Vx_from_incore(Vh, Vx, D, scgtos, eri_incore); }
  
  // for boost-python 
  void cal_Vh_and_Vx_u_bp1(M_tmpl &Vh, M_tmpl &Vx_a, M_tmpl &Vx_b, const M_tmpl &Da, const M_tmpl &Db,
                       const std::vector<Shell_Cgto> &scgtos, const ERI_direct &eri_direct){
    cal_Vh_and_Vx_direct_u(Vh,Vx_a,Vx_b,Da,Db,scgtos,eri_direct);
  }
  void cal_Vh_and_Vx_u_bp2(M_tmpl &Vh, M_tmpl &Vx_a, M_tmpl &Vx_b, const M_tmpl &Da, const M_tmpl &Db,
                       const std::vector<Shell_Cgto> &scgtos, const ERI_file &eri_file){
    cal_Vh_and_Vx_file_u(Vh,Vx_a,Vx_b,Da,Db,scgtos,eri_file);
  }
  void cal_Vh_and_Vx_u_bp3(M_tmpl &Vh, M_tmpl &Vx_a, M_tmpl &Vx_b, const M_tmpl &Da, const M_tmpl &Db, 
                       const std::vector<Shell_Cgto> &scgtos, const ERI_incore &eri_incore){
    cal_Vh_and_Vx_from_incore_u(Vh,Vx_a,Vx_b,Da,Db,scgtos,eri_incore);
  }
  //

  // gradietn
  void cal_grad(std::vector<double> &ret_grad_h,std::vector<double> &ret_grad_x,
                const std::vector<Shell_Cgto> &scgtos,const M_tmpl &D){
    _mode=Fock2e_Enum::Normal; _omega=0.0;  _mode_u=Fock2e_Enum::Restricted;
    cal_grad_base(ret_grad_h,ret_grad_x,scgtos,D,D);
    set_mode_clear();
  }
  void cal_grad_u(std::vector<double> &ret_grad_h,std::vector<double> &ret_grad_x,
                  const std::vector<Shell_Cgto> &scgtos,const M_tmpl &Da,const M_tmpl &Db){
    _mode=Fock2e_Enum::Normal; _omega=0.0;  _mode_u=Fock2e_Enum::Unrestricted;
    cal_grad_base(ret_grad_h,ret_grad_x,scgtos,Da,Db);
    set_mode_clear();
  }

};


}  // end of namespace "Lotus_core"

#include "detail/Fock2e_detail.hpp"

#endif // end of include-guard
