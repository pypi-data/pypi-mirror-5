

#ifndef GTO_H
#define GTO_H


#define _USE_MATH_DEFINES
#include <math.h>
#include <stdlib.h>
#include "Util_PBC.hpp"

#include <sstream>
#include <iostream>
#include <fstream>
#include <vector>

namespace Lotus_core {

 
class Cgto_base {
protected:
  struct GD {
    double g;      //!< gaussian exponent
    double d;      //!< coefficient of basis
    GD(double in_g,double in_d){ g=in_g; d=in_d; }
  }; 

  std::vector<GD>  gd;    

  std::vector<double>   R;          //!< Coordinate 
  int atom_type;                    //!< Atomic number (number of proton,Z)
  int atom_no;                      //!< index for atom

  std::vector<int>     nT_pbc;      //!< to use Periodic Boundary Condition
public:

  Cgto_base(){
    nT_pbc.reserve(3);
    R.reserve(3);
    gd.reserve(0);
    atom_type=atom_no=-1;
    for(int i=0;i<3;i++){
      nT_pbc.push_back(0);
      R.push_back(0.0);
    }
  }
  virtual ~Cgto_base(){};

  void set_atom_type(int in){   atom_type = in; }
  void set_atom_no(int in){     atom_no   = in; }

  void set_R(const std::vector<double> &in_R){
    R.clear(); R.reserve(3);
    R.push_back(in_R[0]);
    R.push_back(in_R[1]);
    R.push_back(in_R[2]);
  }
  void set_nT_pbc(const std::vector<int> &in_nT){
    nT_pbc.clear(); nT_pbc.reserve(3);
    nT_pbc.push_back(in_nT[0]);
    nT_pbc.push_back(in_nT[1]);
    nT_pbc.push_back(in_nT[2]);
  }
  virtual void set_gd(const std::vector<double> &in_g,const std::vector<double> &in_d){
    gd.clear();
    gd.reserve(in_g.size());
    for(int i=0;i<in_g.size();i++){
      gd.push_back(GD(in_g[i],in_d[i]));
    }
  }
  void set_new_d(int nth,double in_new_d){ gd[nth].d=in_new_d; }

 
  int  get_num_pgto()  const {  return gd.size(); }
  int  get_atom_type() const {  return atom_type; }
  int  get_atom_no()   const {  return atom_no; }


  double get_nth_g(int nth)   const { return gd[nth].g; }
  double get_nth_d(int nth)   const { return gd[nth].d; }
  std::vector<double> get_g() const{
    std::vector<double> ret_g;
    for(int i=0;i<gd.size();i++) ret_g.push_back(gd[i].g);
    return ret_g;
  }
  std::vector<double> get_d() const{
    std::vector<double> ret_d;
    for(int i=0;i<gd.size();i++) ret_d.push_back(gd[i].d);
    return ret_d;
  }
  std::vector<double> get_R() const {
    return R;
  }
  const std::vector<double> *get_R_ptr() const {
    return &R;
  }
  void get_R_array(double *ret_R) const {
    ret_R[0]=R[0];
    ret_R[1]=R[1];
    ret_R[2]=R[2];
  }

  std::vector<int> get_nT_pbc() const {
    return nT_pbc;
  } 
  void get_nT_pbc(int *ret_nT) const {
    ret_nT[0]=nT_pbc[0];
    ret_nT[1]=nT_pbc[1];
    ret_nT[2]=nT_pbc[2];
  }
  // for boost-python
  std::vector<int> get_nT_pbc_bp() const {
    return nT_pbc;
  }
  //
 
  int get_num(int tn) const {  return (tn+2)*(tn+1)/2; }
  double cal_I(double in_g,const std::vector<int> &in_n) const {
    return cal_I(in_g, &in_n[0]);
  }
  double cal_I(double in_g,const int *in_n) const {
    const int nnn[11]={1,1,1,2,3,8,15,48,105,384,945};
    double ret=pow((2*in_g/M_PI),3.0/4.0)*pow(4*in_g,(in_n[0]+in_n[1]+in_n[2])/2.0)
              /sqrt((double)nnn[2*in_n[0]]*nnn[2*in_n[1]]*nnn[2*in_n[2]]);
    return ret;
  }

  virtual void show() const {
    std::cout<<" atom_type: "<<atom_type<<" atom_no: "<<atom_no<<std::endl;
    std::cout<<" nT_pbc     "<<nT_pbc[0]<<"  "<<nT_pbc[1]<<"  "<<nT_pbc[2]<<std::endl;
    std::cout<<" R[0]: "<<R[0]<<" R[1]: "<<R[1]<<" R[2]: "<<R[2]<<std::endl;
    std::cout<<" g d "<<std::endl;
    for(int j=0;j<gd.size();j++){
      std::cout<<"         "<<gd[j].g<<"   "<<gd[j].d<<std::endl;
    }
  }

  bool operator==(const Cgto_base &in){ 
    if((void*)this==(void*)&in) return true;
    else                        return false;
  }
};


class Cgto : public Cgto_base {
  std::vector<int>      n;          //!< angular momentum 
  std::vector<double>  dI;          //!< dI = coeeficient(d) * normalized constant(I)
public:
  Cgto(){  n.reserve(3); n.push_back(0); n.push_back(0); n.push_back(0); }

  void set_n(const std::vector<int> &in_n){
    n.clear(); n.reserve(3);
    n.push_back(in_n[0]);
    n.push_back(in_n[1]);
    n.push_back(in_n[2]);
  }
  virtual void set_gd(const std::vector<double> &in_g,const std::vector<double> &in_d){
    gd.clear();
    gd.reserve(in_g.size());
    dI.clear();
    dI.reserve(in_g.size());
    for(int i=0;i<in_g.size();i++){
      double tmp_dI=in_d[i]*cal_I(in_g[i],n);
      gd.push_back(GD(in_g[i],in_d[i]));
      dI.push_back(tmp_dI);
    }
  }

  double get_nth_dI(int nth)  const { return dI[nth]; }
  std::vector<double> get_dI() const{
    std::vector<double> ret_dI;
    for(int i=0;gd.size();i++) ret_dI.push_back(dI[i]);
    return ret_dI;
  }
  int    get_total_n() const {return n[0]+n[1]+n[2];}
  std::vector<int> get_n() const {
    std::vector<int> ret_n(3);
    ret_n[0]=n[0];  ret_n[1]=n[1];  ret_n[2]=n[2];
    return ret_n;  
  }

  inline double cal_grid_value(const std::vector<double> &xyz) const;
  inline std::vector<double> cal_deri_grid_value(const std::vector<double> &xyz) const; 
  inline std::vector<double> cal_deri2_grid_value(const std::vector<double> &xyz) const;

  void show() const {
    std::cout<<" atom_type: "<<atom_type<<" atom_no: "<<atom_no<<std::endl;
    std::cout<<" nT_pbc     "<<nT_pbc[0]<<"  "<<nT_pbc[1]<<"  "<<nT_pbc[2]<<std::endl;
    std::cout<<" R[0]: "<<R[0]<<" R[1]: "<<R[1]<<" R[2]: "<<R[2]<<std::endl;
    std::cout<<" n: "<<n[0]<<" "<<n[1]<<" "<<n[2]<<std::endl;
    std::cout<<" g d dI"<<std::endl;
    for(int j=0;j<gd.size();j++){
      std::cout<<"         "<<gd[j].g<<"   "<<gd[j].d<<"  "<<dI[j]<<std::endl;
    }
  }

  bool operator==(const Cgto &in){ 
    if((void*)this==(void*)&in) return true;
    else                        return false;
  }
};
   
 
class Shell_Cgto : public Cgto_base {
  int shell_type;                   //!< S=>0, P=>1, D=>2, F=>3, ...
  int min_cgto_no;                  //!< index for minimum number for in cgtos
  std::vector<double>  dI;          //!< dI = coeeficient(d) * normalized constant(I)
public:

  void set_shell_type(int in){  shell_type=in; }
  void set_min_cgto_no(int in){  min_cgto_no=in;}
 
  int get_shell_type()  const {  return shell_type; }   // S=0, P=1, SP=11, D=2, F=3
  int get_max_tn()      const {  return shell_type; }   // S=0, P=1, SP=11, D=2, F=3
  int get_num_cgto()    const {  return get_num(shell_type); }
  int get_min_cgto_no() const {  return min_cgto_no;}
  int get_max_cgto_no() const {
    int ret=min_cgto_no;
    ret+=(*this).get_num_cgto();
    ret--;
    return ret;
  }


  template <typename Integ1e>
  void set_dI(){
    int num_cgto=get_num_cgto();
    int num_pgto=get_num_pgto();
    dI.clear();
    dI.reserve(num_cgto*num_pgto);
    for(int i=0;i<num_pgto;i++){
      for(int cc=0;cc<num_cgto;cc++){
        std::vector<int> tmp_n = Integ1e::get_no_to_n(shell_type, cc);
//        int tmp_n[3];
//        Integ1e::get_no_to_n_speed(&tmp_n[0], shell_type, cc);
        dI.push_back(gd[i].d*cal_I(gd[i].g, &tmp_n[0]));
      }
    }
  }

  
  void get_dI(std::vector<double> &ret_dI, int a) const {
    int num_cgto=get_num_cgto(); 
    ret_dI.clear(); 
    ret_dI.reserve(num_cgto);
    for(int cc=0;cc<num_cgto;cc++) ret_dI.push_back(dI[a*num_cgto+cc]);
  }


  template <typename Integ1e>
  inline void grid_value(double *ret,const double *xyz) const;

  template <typename Integ1e>
  void grid_value(std::vector<double> &ret,const std::vector<double> &xyz) const{
    int num_cgto=get_num_cgto();
    ret.reserve(num_cgto);
    ret.clear();
    for(int cc=0;cc<num_cgto;cc++) ret.push_back(0.0);
    grid_value<Integ1e>(&ret[0], &xyz[0]);
  }


  template <typename Integ1e>
  inline void grid_deri_value(double *ret_deri,const double *xyz) const;

  template <typename Integ1e>
  void grid_deri_value(std::vector<double> &ret_deri,const std::vector<double> &xyz) const{
    ret_deri.clear(); 
    int num_cgto=get_num_cgto();
    ret_deri.reserve(3*num_cgto);
    ret_deri.clear();
    for(int cc=0;cc<3*num_cgto;cc++) ret_deri.push_back(0.0);

    grid_deri_value<Integ1e>(&ret_deri[0], &xyz[0]);
  }


  template <typename Integ1e>
  inline void grid_deri2_value(double *ret_deri2,const double *xyz) const;

  template <typename Integ1e>
  void grid_deri2_value(std::vector<double> &ret_deri2,const std::vector<double> &xyz) const{
    ret_deri2.clear(); 
    int num_cgto=get_num_cgto();
    ret_deri2.reserve(6*num_cgto);
    ret_deri2.clear();
    for(int cc=0;cc<6*num_cgto;cc++) ret_deri2.push_back(0.0);
    grid_deri2_value<Integ1e>( &ret_deri2[0], &xyz[0]);
  }

  // for boost-python
  template <typename Integ1e>
  void grid_value_bp(std::vector<double> &ret,const std::vector<double> &xyz) const{
    grid_value<Integ1e>(ret, xyz);
  }
  template <typename Integ1e>
  void grid_deri_value_bp(std::vector<double> &ret_deri,const std::vector<double> &xyz) const{
    grid_deri_value<Integ1e>(ret_deri, xyz);
  }
  template <typename Integ1e>
  void grid_deri2_value_bp(std::vector<double> &ret_deri2,const std::vector<double> &xyz) const{
    grid_deri2_value<Integ1e>(ret_deri2, xyz);
  }
  //

  void show() const {
    Cgto_base::show();
    std::cout<<" shell_type  "<<shell_type<<std::endl;
    std::cout<<" min_cgto_no "<<min_cgto_no<<std::endl;
    std::cout<<" dI "<<dI.size()<<std::endl;
  }

  bool operator==(const Shell_Cgto &in){ 
    if((void*)this==(void*)&in) return true;
    else                        return false;
  }

  template <typename Integ1e>
  std::vector<Cgto> get_cgtos() const {
    int num_cgto = get_num_cgto();
    std::vector<Cgto> ret_cgtos(num_cgto);
    std::vector<double> tmp_g = get_g();
    std::vector<double> tmp_d = get_d();
    for(int i=0;i<ret_cgtos.size();i++){
      std::vector<int> tmp_n = Integ1e::get_no_to_n(shell_type,i);
      ret_cgtos[i].set_atom_type(atom_type);
      ret_cgtos[i].set_atom_no(atom_no);
      ret_cgtos[i].set_nT_pbc(nT_pbc);
      ret_cgtos[i].set_R(R);
      ret_cgtos[i].set_n(tmp_n);
      ret_cgtos[i].set_gd(tmp_g,tmp_d);
    } 
    return ret_cgtos;
  }

};

class Util_GTO {
public:


  static int get_N_cgtos(const std::vector<Shell_Cgto> &scgtos){
    int ret=0;
    for(int i=0;i<scgtos.size();i++) ret+=scgtos[i].get_num_cgto();
    return ret;
  }

  static int get_max_num_cgto(const std::vector<Shell_Cgto> &scgtos){
    int N_scgtos=scgtos.size();
    int max_num_cgto=scgtos[0].get_num_cgto();
    for(int i=1;i<N_scgtos;i++) if(max_num_cgto<scgtos[i].get_num_cgto()) max_num_cgto=scgtos[i].get_num_cgto(); 
    return max_num_cgto;
  }

  static int get_N_scgtos_PBC(int N_scgtos,const std::vector<int> &max_Nc){
    int ret=N_scgtos*(2*max_Nc[0]+1)*(2*max_Nc[1]+1)*(2*max_Nc[2]+1);
    return ret;
  }


  static std::vector<Shell_Cgto> get_scgtos(const std::vector<Shell_Cgto> &scgtos){ 
    std::vector<Shell_Cgto> ret_scgtos;               
    for(int i=0;i<scgtos.size();i++) ret_scgtos.push_back(scgtos[i]);
    return ret_scgtos; 
  }


  template <typename Integ1e>
  static std::vector<Cgto> get_cgtos(const std::vector<Shell_Cgto> &scgtos)
  {
    std::vector<Cgto> ret_cgtos;
    for(int i=0;i<scgtos.size();i++){
      std::vector<Cgto> tmp_cgtos = scgtos[i].get_cgtos<Integ1e>();
      for(int j=0;j<tmp_cgtos.size();j++){
        ret_cgtos.push_back(tmp_cgtos[j]);
      }
    }
    return ret_cgtos;
  }


  inline static std::vector<Shell_Cgto> get_scgtos_PBC(const std::vector<Shell_Cgto> &scgtos,  
                                                const std::vector<int> &max_Nc,const std::vector<double> &T123);


  template <typename M_tmpl,typename Integ1e>
  static void cal_cutoffM_base(std::vector<M_tmpl*> &cutoffM,const std::vector<Shell_Cgto> &scgtos,const CTRL_PBC &ctrl_pbc);




  template <typename B>
  static int get_N_atoms(const std::vector<B> &cgtos)
  {
    std::vector<int> stock_atom_no;
    for(int i=0;i<cgtos.size();i++){
      int an=cgtos[i].get_atom_no();
      int flag=0;
      for(int j=0;j<stock_atom_no.size();j++){
        if(stock_atom_no[j]==an){
          flag=1;
          break;
        }
      }
      if(flag==0) stock_atom_no.push_back(an);
    }

    return stock_atom_no.size();
  }

  template <typename B>
  static std::vector<double> get_Rxyz(const std::vector<B> &cgtos)
  {
    std::vector<int> stock_atom_no;
    std::vector<double> ret_Rxyz;
    for(int i=0;i<cgtos.size();i++){
      int an=cgtos[i].get_atom_no();
      int flag=0;
      for(int j=0;j<stock_atom_no.size();j++){
        if(stock_atom_no[j]==an){
          flag=1;
          break;
        }
      }
      if(flag==0){
        stock_atom_no.push_back(an);
        std::vector<double> tmp_R = cgtos[i].get_R();
        ret_Rxyz.push_back(tmp_R[0]);
        ret_Rxyz.push_back(tmp_R[1]);
        ret_Rxyz.push_back(tmp_R[2]);
      }
    }

    return ret_Rxyz;
  }


  // cutoffM
  template <typename M_tmpl,typename Integ1e>
  static void cal_cutoffM(M_tmpl &cutoffM,const std::vector<Shell_Cgto> &scgtos){
    CTRL_PBC ctrl_pbc;
    std::vector<M_tmpl*> tmpM(1);
    tmpM[0]=&cutoffM;
    cal_cutoffM_base<M_tmpl,Integ1e>(tmpM,scgtos,ctrl_pbc);
  }

  template <typename M_tmpl,typename Integ1e>
  static void cal_cutoffM_PBC(std::vector<M_tmpl> &cutoffM,const std::vector<Shell_Cgto> &scgtos,const CTRL_PBC &ctrl_pbc){
    int N123_c=ctrl_pbc.get_N123_c(); 
    cutoffM.clear();
    cutoffM.reserve(N123_c);
    cutoffM.resize(N123_c); 
    std::vector<M_tmpl*> tmpM(N123_c);
    for(int q=0;q<N123_c;q++) tmpM[q]=&cutoffM[q];
    cal_cutoffM_base<M_tmpl,Integ1e>(tmpM,scgtos,ctrl_pbc);
  }


  template <typename Integ1e>
  static void normalize_scgtos(std::vector<Shell_Cgto> &scgtos)
  {
    std::vector<double> nv;
    for(int p=0;p<scgtos.size();p++){
      std::vector<double> shell=cal_s_shell<Integ1e>(p, scgtos);
      nv.push_back(sqrt(fabs(shell[0])));
    }
    for(int i=0;i<scgtos.size();i++){
      for(int j=0;j<scgtos[i].get_num_pgto();j++){
        double old_d=scgtos[i].get_nth_d(j);
        double new_d=old_d/nv[i];
        scgtos[i].set_new_d(j,new_d);
      }
    }
  }

  template <typename Integ1e>
  static std::vector<double> cal_s_shell(int p,const std::vector<Shell_Cgto> &scgtos);

  template <typename Integ1e>
  static std::vector<Shell_Cgto> get_scgtos_from_string(const char *qm_string);

  template <typename Integ1e>
  static std::vector<Shell_Cgto> get_scgtos_from_file(const char *filename)
  {
    std::string qm_string=get_string_from_file(filename);
    return get_scgtos_from_string<Integ1e>(qm_string.c_str());
  }

 
  inline static std::string get_string_from_file(const char *filename)
  {
    using namespace std;
    ifstream ifs(filename);
    if(!ifs){
      cout<<" Error: cannnot open file,  "<<filename<<endl;
      exit(1);
    }

    string line,ret_str="";
    while (getline(ifs,line)) ret_str+=line+"\n";
    ret_str+="\n";

    ifs.close();
    return ret_str;
  }



};



}  // end of namespace "Lotus_core"

#include "detail/gto_detail.hpp"

#endif // end of include-guard
 
