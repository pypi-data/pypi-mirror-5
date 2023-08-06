

#ifndef MIXIN_CORE_HPP
#define MIXIN_CORE_HPP

#include "SCF.hpp"
#include "gto.hpp"
#include "Fock1e_tmpl.hpp"
#include "Fock2e_tmpl.hpp"
#include "ECP_tmpl.hpp"
#include "GInte_Functor.hpp"
#include "Util.hpp"
#include "Gradient.hpp"

#include <algorithm>

#include <iostream>
#include <string>

namespace Lotus_core {


template <typename Target, typename M_tmpl, typename Integ1e, typename Integ2e>
class Mixin_core {
  // CRTP(Curiously Recuursive Template Pattern) for Ruby-type Mixin

public:


  virtual void read_in_file(const char *filename){
    std::string string_in_file = Util::get_string_from_file(filename);
    read_in_string( string_in_file.c_str() );
  }
  virtual void read_in_string(const char *in_string){
    std::istringstream is(in_string);

    MolData *moldata_ptr = &static_cast<Target&>(*this).moldata;
    char read_str[256];
    for(;;){
      is>>read_str;
      if(is.eof()) break;
     
      if(strcmp("qm_file:",read_str)==0){
        std::string qm_filename; is>>qm_filename;
        moldata_ptr->set_basis_from_file<Integ1e>( qm_filename.c_str() );
      }
      if(strcmp("spin:",read_str)==0){
        int in_spin=1; is>>in_spin;
        moldata_ptr->spin=in_spin;
      }
      if(strcmp("mol_charge:",read_str)==0){
        int in_mol_charge=0; is>>in_mol_charge;
        moldata_ptr->mol_charge=in_mol_charge;
      }
    }
  }

  int get_N_cgtos() const {
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    return Util_GTO::get_N_cgtos(moldata_ptr->scgtos);
  }

  int get_N_atoms() const {
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    return Util_GTO::get_N_atoms(moldata_ptr->scgtos);
  }

  int get_N_scgtos() const {
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    return moldata_ptr->scgtos.size();
  }
  int get_N_ecps() const {
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    return moldata_ptr->ecps.size();
  }

  std::vector<double> get_Rxyz() const {
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    return Util_GTO::get_Rxyz(moldata_ptr->scgtos);
  }
  std::vector<Charge> get_charges() const {
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    return Util::get_charges(moldata_ptr->scgtos, moldata_ptr->ecps);
  }
  int get_total_charge() const {
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    return Util::get_total_charge(moldata_ptr->scgtos, moldata_ptr->ecps);
  }

  std::vector<double> get_occ() const {
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    return Util::cal_occ(moldata_ptr->scgtos, moldata_ptr->ecps, 
                         moldata_ptr->mol_charge, moldata_ptr->spin);
  }
  void get_occ_ab(std::vector<double> &occ_a, std::vector<double> &occ_b) const {
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    Util::cal_occ_ab(occ_a, occ_b, moldata_ptr->scgtos, moldata_ptr->ecps, 
                     moldata_ptr->mol_charge, moldata_ptr->spin);
  }

  void cal_matrix(const char *in_sel, M_tmpl &retM){
    const Target  *self         = &static_cast<const Target&>(*this);
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    const M_tmpl  *X_a_ptr     = &static_cast<const Target&>(*this).X_a;
    const M_tmpl  *X_b_ptr     = &static_cast<const Target&>(*this).X_b;
    int N_cgtos = get_N_cgtos();
    Fock1e_tmpl<M_tmpl,Integ1e> fock1e;
    ECP_matrix<M_tmpl,Integ1e>  ecp_mat;
    retM.set_IJ(N_cgtos, N_cgtos);
    std::string sel(in_sel);
    std::transform(sel.begin(), sel.end(), sel.begin(), ::toupper);
    std::vector<Charge> charges = get_charges();
    std::vector<double> occ_a, occ_b;
    Util::cal_occ_ab(occ_a, occ_b, moldata_ptr->scgtos, moldata_ptr->ecps, 
                     moldata_ptr->mol_charge, moldata_ptr->spin);
    if(sel=="S")              fock1e.cal_S(retM, moldata_ptr->scgtos);
    else if(sel=="K")         fock1e.cal_K(retM, moldata_ptr->scgtos);
    else if(sel=="ECP")       ecp_mat.cal_ECP(retM, moldata_ptr->scgtos, moldata_ptr->ecps);
    else if(sel=="NA")        fock1e.cal_NA(retM, moldata_ptr->scgtos, charges);
    else if(sel=="H_CORE")    self->scf_class.cal_h_core(retM, moldata_ptr->scgtos, moldata_ptr->ecps);
    else if(sel=="D")         Util::cal_D(retM, *X_a_ptr, occ_a);
    else if(sel=="D_A")       Util::cal_D(retM, *X_a_ptr, occ_a);
    else if(sel=="D_B")       Util::cal_D(retM, *X_b_ptr, occ_b);
    else{
      int process_num = Util_MPI::get_mpi_rank();
      if(process_num==0) std::cout<<"cal_matrix do not suport "<<in_sel<<std::endl; 
    }
  }


  template <typename select_ERI>
  void prepare_eri(select_ERI &sel_eri){
    const Target  *self         = &static_cast<const Target&>(*this);
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    self->scf_class.template prepare_eri<M_tmpl,select_ERI>(sel_eri, moldata_ptr->scgtos);
  } 

  template <typename select_ERI>
  void cal_Fock_sub(M_tmpl &ret_Fock_sub, const M_tmpl &D, 
                    const select_ERI &sel_eri, const GInte_Functor &functor){
    Target  *self         = &static_cast<Target&>(*this);
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    self->scf_class.cal_Fock_sub(ret_Fock_sub, D, moldata_ptr->scgtos, sel_eri, functor);
  }


  template <typename select_ERI>
  void cal_Fock_sub_u(M_tmpl &ret_Fock_sub_a, M_tmpl &ret_Fock_sub_b, 
                      const M_tmpl &D_a, const M_tmpl &D_b,
                      const select_ERI &sel_eri, const GInte_Functor &functor){
    Target  *self         = &static_cast<Target&>(*this);
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    self->scf_class.cal_Fock_sub_u(ret_Fock_sub_a, ret_Fock_sub_b, D_a, D_b, moldata_ptr->scgtos, sel_eri, functor);
  }

  void guess_h_core(M_tmpl &retM, std::vector<double> &ret_lamda){
    const Target  *self         = &static_cast<const Target&>(*this);
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    self->scf_class.guess_h_core(retM, ret_lamda, moldata_ptr->scgtos, moldata_ptr->ecps);
  }
  void guess_h_core(){
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    int spin=moldata_ptr->spin;
    if(spin==1)  r_guess_h_core();
    else         u_guess_h_core();
  }

  // boost-python
  void guess_h_core_bp1(M_tmpl &retM, std::vector<double> &ret_lamda){
    guess_h_core(retM, ret_lamda);
  }
  void guess_h_core_bp2(){
    guess_h_core();
  }

  void r_guess_h_core(){
    const Target  *self              = &static_cast<const Target&>(*this);
    const MolData *moldata_ptr       = &static_cast<const Target&>(*this).moldata;
    std::vector<double> *lamda_a_ptr = &static_cast<Target&>(*this).lamda_a;
    M_tmpl *X_a_ptr                  = &static_cast<Target&>(*this).X_a;
    self->scf_class.guess_h_core(*X_a_ptr, *lamda_a_ptr, moldata_ptr->scgtos, moldata_ptr->ecps);
  }
  void u_guess_h_core(){
    const Target  *self              = &static_cast<const Target&>(*this);
    const MolData *moldata_ptr       = &static_cast<const Target&>(*this).moldata;
    std::vector<double> *lamda_a_ptr = &static_cast<Target&>(*this).lamda_a;
    std::vector<double> *lamda_b_ptr = &static_cast<Target&>(*this).lamda_b;
    M_tmpl *X_a_ptr                  = &static_cast<Target&>(*this).X_a;
    M_tmpl *X_b_ptr                  = &static_cast<Target&>(*this).X_b;
    self->scf_class.guess_h_core(*X_a_ptr, *lamda_a_ptr, moldata_ptr->scgtos, moldata_ptr->ecps);
    mat_copy(*X_b_ptr,*X_a_ptr);
    lamda_b_ptr->clear();
    for(int i=0;i<lamda_a_ptr->size();i++) lamda_b_ptr->push_back((*lamda_a_ptr)[i]);
  }

  template <typename select_ERI>
  void r_scf(GInte_Functor &functor){
    select_ERI sel_eri;
    Target  *self                    = &static_cast<Target&>(*this);
    const MolData *moldata_ptr       = &static_cast<const Target&>(*this).moldata;
    std::vector<double> *lamda_a_ptr = &static_cast<Target&>(*this).lamda_a;
    M_tmpl *X_a_ptr                  = &static_cast<Target&>(*this).X_a;
    double *ene_total_ptr            = &static_cast<Target&>(*this).ene_total;
    self->scf_class.r_scf(*X_a_ptr, *lamda_a_ptr, *moldata_ptr, sel_eri, functor);
    *ene_total_ptr=self->scf_class.get_ene_total();
  }

  template <typename select_ERI>
  void u_scf(GInte_Functor &functor){
    select_ERI sel_eri;
    Target  *self                    = &static_cast<Target&>(*this);
    const MolData *moldata_ptr       = &static_cast<const Target&>(*this).moldata;
    std::vector<double> *lamda_a_ptr = &static_cast<Target&>(*this).lamda_a;
    std::vector<double> *lamda_b_ptr = &static_cast<Target&>(*this).lamda_b;
    M_tmpl *X_a_ptr                  = &static_cast<Target&>(*this).X_a;
    M_tmpl *X_b_ptr                  = &static_cast<Target&>(*this).X_b;
    double *ene_total_ptr            = &static_cast<Target&>(*this).ene_total;
    self->scf_class.u_scf(*X_a_ptr, *X_b_ptr, *lamda_a_ptr, *lamda_b_ptr, *moldata_ptr, sel_eri, functor);
    *ene_total_ptr=self->scf_class.get_ene_total();
  }


  template <typename select_ERI>
  void scf(GInte_Functor &functor){
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    int spin=moldata_ptr->spin;
    if(spin==1) r_scf<select_ERI>(functor);
    else        u_scf<select_ERI>(functor);
  } 

  std::vector<double> cal_force_r(GInte_Functor &functor){
    Gradient<Integ1e,Integ2e> grad;
    std::vector<double> occ = get_occ(); 
    const MolData *moldata_ptr             = &static_cast<const Target&>(*this).moldata;
    const M_tmpl *X_a_ptr                  = &static_cast<const Target&>(*this).X_a;
    const std::vector<double> *lamda_a_ptr = &static_cast<const Target&>(*this).lamda_a;
    return grad.cal_force(moldata_ptr->scgtos, moldata_ptr->ecps, *X_a_ptr, occ, *lamda_a_ptr, functor);
  }

  std::vector<double> cal_force_u(GInte_Functor &functor){
    Gradient<Integ1e,Integ2e> grad;
    std::vector<double> occ_a, occ_b;
    get_occ_ab(occ_a, occ_b);
    const MolData *moldata_ptr             = &static_cast<const Target&>(*this).moldata;
    const M_tmpl *X_a_ptr                  = &static_cast<const Target&>(*this).X_a;
    const M_tmpl *X_b_ptr                  = &static_cast<const Target&>(*this).X_b;
    const std::vector<double> *lamda_a_ptr = &static_cast<const Target&>(*this).lamda_a;
    const std::vector<double> *lamda_b_ptr = &static_cast<const Target&>(*this).lamda_b;
    return grad.cal_force_u(moldata_ptr->scgtos, moldata_ptr->ecps, *X_a_ptr, *X_b_ptr, occ_a, occ_b,
                            *lamda_a_ptr, *lamda_b_ptr, functor);
  }

  std::vector<double> cal_force(GInte_Functor &functor){
    const MolData *moldata_ptr = &static_cast<const Target&>(*this).moldata;
    int spin=moldata_ptr->spin;
    if(spin==1)  return cal_force_r(functor);
    else         return cal_force_u(functor);
  }

  
  double cal_energy(const M_tmpl &D, const M_tmpl &H_core, const MolData &moldata){
    return cal_energy_u(D, D, H_core, moldata);
  }

  double cal_energy_u(const M_tmpl &D_a, const M_tmpl &D_b, const M_tmpl &H_core, const MolData &moldata){
    Target  *self         = &static_cast<Target&>(*this);
    return self->scf_class.cal_energy_u(D_a, D_b, H_core, moldata);
  }

  double cal_show_energy(const M_tmpl &D, const M_tmpl &H_core, const MolData &moldata){
    return cal_show_energy_u(D, D, H_core, moldata);
  }

  double cal_show_energy_u(const M_tmpl &D_a, const M_tmpl &D_b, const M_tmpl &H_core, const MolData &moldata){
    Target  *self         = &static_cast<Target&>(*this);
    return self->scf_class.cal_show_energy_u(D_a, D_b, H_core, moldata);
  }

  void diis(std::vector<M_tmpl> &F, std::vector<M_tmpl> &D, M_tmpl &S, int n_scf, int max_diis){
    Target  *self         = &static_cast<Target&>(*this);
    self->scf_class.diis(F, D, S, n_scf, max_diis);
  }

  void ediis(std::vector<M_tmpl> &F, std::vector<M_tmpl> &D, const std::vector<double> &E, int n_scf, int max_diis){
    Target  *self         = &static_cast<Target&>(*this);
    self->scf_class.ediis(F, D, E, n_scf, max_diis);
  }



};


template <typename M_tmpl,typename Integ1e,typename Integ2e>
class Lotus: public Mixin_core< Lotus<M_tmpl,Integ1e,Integ2e>,M_tmpl,Integ1e,Integ2e > {
public:
  SCF<Integ1e,Integ2e>        scf_class;
  double ene_total;
  MolData moldata;
  M_tmpl X_a, X_b;
  std::vector<double> lamda_a, lamda_b;
};



}  // end of namespace "Lotus_core"
#endif
