


#ifndef SCF_H
#define SCF_H

#include "gto.hpp"
#include "ECP_tmpl.hpp"
#include "GInte_Functor.hpp"

#include "Fock1e_tmpl.hpp"
#include "Fock2e_tmpl.hpp"
#include "Grid_Inte.hpp"
#include "Util.hpp"

namespace Lotus_core {

class MolData {
public:
  std::vector<Shell_Cgto> scgtos;
  std::vector<ECP>        ecps;
  int mol_charge;
  int spin;

  MolData(){
    mol_charge=0;
    spin      =1;
  }
  template <typename Integ1e> 
  void set_basis_from_string(const char *qm_string)
  {
    scgtos = Util_GTO::get_scgtos_from_string<Integ1e>(qm_string);
    ecps   = ECP::get_ecps_from_string(qm_string);
  }

  template <typename Integ1e> 
  void set_basis_from_file(const char *filename)
  {
    scgtos = Util_GTO::get_scgtos_from_file<Integ1e>(filename);
    ecps   = ECP::get_ecps_from_file(filename);
  }

};

template <typename Integ1e, typename Integ2e>
class SCF {
  bool flag_do_diis;
  bool flag_do_ediis;

  double ene_vh, ene_vx, ene_dft, ene_h_core, ene_ele, ene_vnn, ene_total;

  void set_diis(){
    flag_do_diis  = true;
    flag_do_ediis = false;
  }

  int i_pow(int x,int n) const {
    int ret=1;
    for(int i=0;i<n;i++) ret*=x;
    return ret;
  }

public:
  int  max_diis;
  int  max_scf;
  double threshold_scf;
  double mix_dens;

  SCF(){
    ene_vh=ene_vx=ene_dft=ene_h_core=ene_ele=ene_vnn=ene_total=0.0;

    flag_do_diis  = true;
    flag_do_ediis = false;
    max_diis=6;
    max_scf=100;
    threshold_scf=1.0e-6;
    mix_dens=0.3;
  }
  double get_ene_vh(){     return ene_total; }
  double get_ene_vx(){     return ene_total; }
  double get_ene_dft(){    return ene_total; }
  double get_ene_h_core(){ return ene_total; }
  double get_ene_ele(){    return ene_total; }
  double get_ene_vnn(){    return ene_total; }
  double get_ene_total(){  return ene_total; }

  void do_diis(){ set_diis(); }
  void do_ediis(){ set_diis(); flag_do_diis=false; flag_do_ediis=true; }

  template <typename M_tmpl>
  void cal_h_core(M_tmpl &ret_h_core, const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps) const;
    

  template <typename M_tmpl>
  void guess_h_core(M_tmpl &retX, std::vector<double> &ret_lamda,
                    const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps) const;

  template <typename M_tmpl, typename select_ERI>
  void prepare_eri(select_ERI &sel_eri, const std::vector<Shell_Cgto> &scgtos) const {
    Fock2e_tmpl<M_tmpl, Integ2e> fock2e;
    fock2e.prepare_eri(sel_eri, scgtos);
  }


  template <typename M_tmpl, typename select_ERI>
  void cal_Fock_sub(M_tmpl &retM, const M_tmpl &D, const std::vector<Shell_Cgto> &scgtos,
                    const select_ERI &sel_eri, const GInte_Functor &dft_functor);

  template <typename M_tmpl, typename select_ERI>
  void cal_Fock_sub_u(M_tmpl &retM_a, M_tmpl &retM_b, const M_tmpl &D_a, const M_tmpl &D_b, const std::vector<Shell_Cgto> &scgtos, 
                      const select_ERI &sel_eri, const GInte_Functor &dft_functor);

  template <typename vec_M_tmpl, typename M_tmpl>
  void diis(vec_M_tmpl &F, vec_M_tmpl &D, M_tmpl &S, int n_scf, int max_diis) const;


  template <typename M_tmpl>
  void ediis_sub(std::vector<double> &ret_coef,const std::vector<double> &E, M_tmpl &MM,int size_of_ediis,int ind) const;

  template <typename vec_M_tmpl,typename M_tmpl>
  void ediis(vec_M_tmpl &F, vec_M_tmpl &D, const std::vector<double> &E, int n_scf, int max_ediis) const;


  template <typename vec_M_tmpl>
  double get_max_d(vec_M_tmpl &D, int ind, int pre_ind) const;

  template <typename M_tmpl>
  double cal_energy(const M_tmpl &D, const M_tmpl &H_core, const MolData &moldata){
    return cal_energy_u(D, D, H_core, moldata);
  }

  template <typename M_tmpl>
  double cal_energy_u(const M_tmpl &D_a, const M_tmpl &D_b, const M_tmpl &H_core, const MolData &moldata);

  template <typename M_tmpl>
  double cal_show_energy(const M_tmpl &D, const M_tmpl &H_core, const MolData &moldata){
    return cal_show_energy_u(D, D, H_core, moldata);
  }

  template <typename M_tmpl>
  double cal_show_energy_u(const M_tmpl &D_a, const M_tmpl &D_b, const M_tmpl &H_core, const MolData &moldata);

  template <typename M_tmpl, typename select_ERI>
  void r_scf(M_tmpl &X, std::vector<double> &lamda,
             const MolData &moldata,  select_ERI &sel_eri, const GInte_Functor &functor);

  template <typename M_tmpl, typename select_ERI>
  void u_scf(M_tmpl &X_a, M_tmpl &X_b, std::vector<double> &lamda_a, std::vector<double> &lamda_b,
             const MolData &moldata,  select_ERI &sel_eri, const GInte_Functor &functor);
};


}  // end of namespace "Lotus_core"

#include "detail/SCF_detail.hpp"

#endif // end of include-gurad

