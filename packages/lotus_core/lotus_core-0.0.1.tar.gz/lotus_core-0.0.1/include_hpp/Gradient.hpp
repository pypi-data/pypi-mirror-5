
#ifndef GRADIENT_H
#define GRADIENT_H

#include "gto.hpp"
#include "ECP_tmpl.hpp"
#include "GInte_Functor.hpp"
#include "Util.hpp"

#include <vector>

namespace Lotus_core {

template <typename Integ1e,typename Integ2e>
class Gradient {

public:


  inline std::vector<double> cal_Vnn_deri(const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, int in_atom_no);


  

  template <typename M_tmpl>
  std::vector<double> cal_force(const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, const M_tmpl &D, const M_tmpl &W, const GInte_Functor &dft_functor);
                                

  template <typename M_tmpl>
  std::vector<double> cal_force_u(const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, 
                                  const M_tmpl &Da, const M_tmpl &Db, const M_tmpl &Wa, const M_tmpl &Wb, const GInte_Functor &dft_functor);

  template <typename M_tmpl>
  std::vector<double> cal_force(const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, 
                                const M_tmpl &X, const std::vector<double> &occ, const std::vector<double> &lamda, const GInte_Functor &dft_functor){
    M_tmpl D, W;
    Util::cal_D(D, X, occ);
    Util::cal_W(W, X, occ, lamda); 
    return cal_force(scgtos, ecps, D, W, dft_functor);
  }

  

  template <typename M_tmpl>
  std::vector<double> cal_force_u(const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, 
                                  const M_tmpl &X_a, const M_tmpl &X_b, const std::vector<double> &occ_a, const std::vector<double> &occ_b,
                                  const std::vector<double> &lamda_a, const std::vector<double> &lamda_b, const GInte_Functor &dft_functor){

    M_tmpl D_a, D_b, W_a, W_b;
    Util::cal_D(D_a, X_a, occ_a);
    Util::cal_D(D_b, X_b, occ_b);
    Util::cal_W(W_a, X_a, occ_a, lamda_a); 
    Util::cal_W(W_b, X_b, occ_b, lamda_b); 
    return cal_force_u(scgtos, ecps, D_a, D_b, W_a, W_b, dft_functor);
  }

  // boost-python
  template <typename M_tmpl>
  std::vector<double> cal_force_bp1(const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, const M_tmpl &D, const M_tmpl &W, const GInte_Functor &dft_functor){
    return cal_force(scgtos, ecps, D, W, dft_functor);
  }

  template <typename M_tmpl>
  std::vector<double> cal_force_bp2(const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, const M_tmpl &D, const M_tmpl &W, const GInte_Functor &dft_functor){
    return cal_force(scgtos, ecps, D, W, dft_functor);
  }


  template <typename M_tmpl>
  std::vector<double> cal_force_u_bp1(const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, 
                                      const M_tmpl &Da, const M_tmpl &Db, const M_tmpl &Wa, const M_tmpl &Wb, const GInte_Functor &dft_functor){
    return cal_force_u(scgtos, ecps, Da, Db, Wa, Wb, dft_functor);
  }

  template <typename M_tmpl>
  std::vector<double> cal_force_u_bp2(const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, 
                                      const M_tmpl &X_a, const M_tmpl &X_b, const std::vector<double> &occ_a, const std::vector<double> &occ_b,
                                      const std::vector<double> &lamda_a, const std::vector<double> &lamda_b, const GInte_Functor &dft_functor){
    return cal_force_u_bp2(scgtos, ecps, X_a, X_b, occ_a, occ_b, lamda_a, lamda_b, dft_functor);
  }
  //
};




}  // end of namespace "Lotus_core"

#include "detail/Gradient_detail.hpp"

#endif // end of include-gurad



