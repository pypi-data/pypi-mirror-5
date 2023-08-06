
#ifndef GRADIENT_DETAIL_HPP
#define GRADIENT_DETAIL_HPP



#include "Gradient.hpp"
#include "Fock1e_tmpl.hpp"
#include "Fock2e_tmpl.hpp"
#include "Grid_Inte.hpp"
#include "Util.hpp"

#include <iostream>

namespace Lotus_core {


template <typename Integ1e,typename Integ2e>
std::vector<double> Gradient<Integ1e,Integ2e>::cal_Vnn_deri(const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, int in_atom_no)
{
 
  std::vector<Charge> charges = Util::get_charges(scgtos, ecps); 
  
  std::vector<double> R_k(3);
  double Z_k;
  for(int a=0;a<charges.size();a++){
    if(in_atom_no == charges[a].atom_no){
      R_k[0]=charges[a].x;
      R_k[1]=charges[a].y;
      R_k[2]=charges[a].z;
      Z_k   =charges[a].charge;
      break;
    }
  }
 
  std::vector<double> ret(3, 0.0);

  for(int a=0;a<charges.size();a++){
    std::vector<double> R_a(3);
    R_a[0] = charges[a].x;
    R_a[1] = charges[a].y;
    R_a[2] = charges[a].z;
    if(a!=in_atom_no){
      double Z_a=charges[a].charge;
      
      double tmp_sqrt=sqrt((R_k[0]-R_a[0])*(R_k[0]-R_a[0])+
                           (R_k[1]-R_a[1])*(R_k[1]-R_a[1])+
                           (R_k[2]-R_a[2])*(R_k[2]-R_a[2]));
      for(int xyz=0;xyz<3;xyz++){
        ret[xyz]-=((R_k[xyz]-R_a[xyz])
                 *((double)Z_k*Z_a))/(tmp_sqrt*tmp_sqrt*tmp_sqrt);
      }
    }
  }
  return ret;
}



template <typename Integ1e,typename Integ2e> template <typename M_tmpl>
std::vector<double> Gradient<Integ1e,Integ2e>::cal_force(const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, 
                                                         const M_tmpl &D, const M_tmpl &W, const GInte_Functor &dft_functor)
{
  using namespace std;

  int    N_atoms        = Util_GTO::get_N_atoms(scgtos);
  std::vector<double> ret_fxyz(3*N_atoms, 0.0);
  std::vector<double> tmp_grad;

  Fock1e_tmpl<M_tmpl,Integ1e>         fock1e;
  Fock2e_tmpl<M_tmpl,Integ2e>         fock2e;
  Grid_Inte<  M_tmpl,Integ1e>         grid_inte;
  ECP_matrix< M_tmpl,Integ1e>         ecp_mat;

  double hybrid_x = dft_functor.get_hybrid_hf_x();



  // ERI
  std::vector<double> grad_h, grad_x;
  fock2e.cal_grad(grad_h, grad_x, scgtos, D);
  for(int i=0;i<N_atoms*3;i++) ret_fxyz[i]=grad_h[i] + hybrid_x*grad_x[i];
  // DFT
  if(dft_functor.get_use_grid_inte()==1){  // set dft
    tmp_grad = grid_inte.cal_grad(scgtos, D, dft_functor);
    for(int i=0;i<3*N_atoms;i++) ret_fxyz[i]+=tmp_grad[i];
  }

  //  kinetic
  tmp_grad = fock1e.cal_grad_K(scgtos, D);
  for(int i=0;i<3*N_atoms;i++) ret_fxyz[i]+=tmp_grad[i];

  //  NA 
  std::vector<Charge> charges = Util::get_charges(scgtos, ecps); 
  tmp_grad = fock1e.cal_grad_NA(scgtos, D, charges);
  for(int i=0;i<3*N_atoms;i++) ret_fxyz[i]+=tmp_grad[i];

  //  SW
  tmp_grad = fock1e.cal_grad_S(scgtos, W);
  for(int i=0;i<3*N_atoms;i++) ret_fxyz[i]+=-1.0*tmp_grad[i];

  //  for ECP
  if(ecps.size()>0){
    tmp_grad = ecp_mat.cal_grad_ECP(scgtos, ecps, D);
    for(int i=0;i<3*N_atoms;i++) ret_fxyz[i]+=tmp_grad[i];
  }

  // x -2.0
  for(int i=0;i<3*N_atoms;i++) ret_fxyz[i]*=-2.0;


  //  for nuclear-nuclear repulsive
  for(int a=0;a<N_atoms;a++){
    std::vector<double> Vnn_deri = cal_Vnn_deri(scgtos, ecps, a);
    ret_fxyz[a*3+0]-=Vnn_deri[0];
    ret_fxyz[a*3+1]-=Vnn_deri[1];
    ret_fxyz[a*3+2]-=Vnn_deri[2];
  }


  return ret_fxyz;

}



template <typename Integ1e,typename Integ2e> template <typename M_tmpl>
std::vector<double> Gradient<Integ1e,Integ2e>::cal_force_u(const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, 
                                                           const M_tmpl &Da, const M_tmpl &Db, const M_tmpl &Wa, const M_tmpl &Wb,
                                                           const GInte_Functor &dft_functor)
{

  int    N_atoms        = Util_GTO::get_N_atoms(scgtos);
  std::vector<double> ret_fxyz(3*N_atoms, 0.0);
  std::vector<double> tmp_grad;

  Fock1e_tmpl<M_tmpl,Integ1e>         fock1e;
  Fock2e_tmpl<M_tmpl,Integ2e>         fock2e;
  Grid_Inte<  M_tmpl,Integ1e>         grid_inte;
  ECP_matrix< M_tmpl,Integ1e>         ecp_mat;

  int N_cgtos = Da.get_I();
  M_tmpl Dt_half(N_cgtos, N_cgtos);
  mat_add(Dt_half, Da, Db);
  mat_mul_v(Dt_half, 0.5, Dt_half);

  M_tmpl Wt_half(N_cgtos, N_cgtos);
  mat_add(Wt_half, Wa, Wb);
  mat_mul_v(Wt_half, 0.5, Wt_half);

  double hybrid_x = dft_functor.get_hybrid_hf_x();
  // ERI
  std::vector<double> grad_h, grad_x;
  fock2e.cal_grad_u(grad_h, grad_x, scgtos, Da, Db);
  for(int i=0;i<N_atoms*3;i++) ret_fxyz[i] = grad_h[i] + hybrid_x*grad_x[i];


  // DFT
  if(dft_functor.get_use_grid_inte()==1){  // set dft
    tmp_grad = grid_inte.cal_grad_u(scgtos, Da, Db, dft_functor);
    for(int i=0;i<3*N_atoms;i++) ret_fxyz[i]+=tmp_grad[i];
  }

  //  kinetic
  tmp_grad = fock1e.cal_grad_K(scgtos, Dt_half);
  for(int i=0;i<3*N_atoms;i++) ret_fxyz[i]+=tmp_grad[i];

  //  NA 
  std::vector<Charge> charges = Util::get_charges(scgtos, ecps); 
  tmp_grad = fock1e.cal_grad_NA(scgtos, Dt_half, charges);
  for(int i=0;i<3*N_atoms;i++) ret_fxyz[i]+=tmp_grad[i];

  //  SW
  tmp_grad = fock1e.cal_grad_S(scgtos, Wt_half);
  for(int i=0;i<3*N_atoms;i++) ret_fxyz[i]+=-1.0*tmp_grad[i];

  //  for ECP
  if(ecps.size()>0){
    tmp_grad = ecp_mat.cal_grad_ECP(scgtos, ecps, Dt_half);
    for(int i=0;i<3*N_atoms;i++) ret_fxyz[i]+=tmp_grad[i];
  }

  // x -2.0
  for(int i=0;i<3*N_atoms;i++) ret_fxyz[i]*=-2.0;


  //  for nuclear-nuclear repulsive
  for(int a=0;a<N_atoms;a++){
    std::vector<double> Vnn_deri = cal_Vnn_deri(scgtos, ecps, a);
    ret_fxyz[a*3+0]-=Vnn_deri[0];
    ret_fxyz[a*3+1]-=Vnn_deri[1];
    ret_fxyz[a*3+2]-=Vnn_deri[2];
  }

  return ret_fxyz;
}

/*

//
// cal_force

template 
std::vector<double> Gradient::cal_force<dMatrix>(const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, 
                                                 const dMatrix &D, const dMatrix &W, const GInte_Functor &dft_functor);


template 
std::vector<double> Gradient::cal_force<dMatrix_map>(const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, 
                                                     const dMatrix_map &D, const dMatrix_map &W, const GInte_Functor &dft_functor);


//
// cal_force_u

template 
std::vector<double> Gradient::cal_force_u<dMatrix>(const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, 
                                const dMatrix &Da, const dMatrix &Db, const dMatrix &Wa, const dMatrix &Wb, const GInte_Functor &dft_functor);


template 
std::vector<double> Gradient::cal_force_u<dMatrix_map>(const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, 
                                const dMatrix_map &Da, const dMatrix_map &Db, const dMatrix_map &Wa, const dMatrix_map &Wb, const GInte_Functor &dft_functor);

*/
}  // end of namespace "Lotus_core"


#endif // end of include-guard


