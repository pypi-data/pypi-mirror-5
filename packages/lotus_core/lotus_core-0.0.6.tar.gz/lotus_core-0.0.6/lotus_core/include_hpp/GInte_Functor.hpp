

 
#ifndef GInte_FUNCTOR_H
#define GInte_FUNCTOR_H

#include "DFT_func.hpp"
#include <iostream>


namespace Lotus_core {


class GInte_Functor {
protected:
  int flag_gga;
  int use_potential_energy;
  int use_grid_inte;
  double hybrid_hf_x;
public:
  GInte_Functor(){
    flag_gga=0;
    use_potential_energy=0;
    use_grid_inte=0;
    hybrid_hf_x=0.0;
  }  

  int    get_use_potential_energy() const { return use_potential_energy; }
  int    get_flag_gga() const {  return flag_gga; }
  int    get_use_grid_inte() const { return use_grid_inte; }
  double get_hybrid_hf_x() const {  return hybrid_hf_x; }

  virtual void operator()(double &ret_ene, std::vector<double> &ret_v123, double rou, const std::vector<double> &rou_deri) const{
    ret_ene=0.0;
    ret_v123.reserve(3);
    for(int i=0;i<3;i++) ret_v123.push_back(0.0);
  }
  virtual void operator()(double &ret_ene, std::vector<double> &ret_v123_a, std::vector<double> &ret_v123_b, 
                          double rou_a, const std::vector<double> &rou_deri_a, double rou_b, const std::vector<double> &rou_deri_b) const {
    ret_ene=0.0;
    ret_v123_a.reserve(3);
    for(int i=0;i<3;i++) ret_v123_a.push_back(0.0);
    ret_v123_b.reserve(3);
    for(int i=0;i<3;i++) ret_v123_b.push_back(0.0);
  }

  // for boost-python
  virtual void op_bp1(double &ret_ene, std::vector<double> &ret_v123, double rou, const std::vector<double> &rou_deri) const{
    this->operator()(ret_ene, ret_v123, rou, rou_deri);
  }
  virtual void op_bp2(double &ret_ene, std::vector<double> &ret_v123_a, std::vector<double> &ret_v123_b, 
                      double rou_a, const std::vector<double> &rou_deri_a, double rou_b, const std::vector<double> &rou_deri_b) const {
    this->operator()(ret_ene, ret_v123_a, ret_v123_b, rou_a, rou_deri_a, rou_b, rou_deri_b);
  }


};


// HF
class HF_Functor : public GInte_Functor {
public:
  HF_Functor(){
    flag_gga=0;  use_potential_energy=0; use_grid_inte=0;  hybrid_hf_x=1.0;
  }
  void operator()(double &ret_ene, std::vector<double> &ret_v123, double rou, const std::vector<double> &rou_deri) const{
    ret_ene=0.0;
    ret_v123.reserve(3);
    for(int i=0;i<3;i++) ret_v123.push_back(0.0);
  }
  void operator()(double &ret_ene, std::vector<double> &ret_v123_a, std::vector<double> &ret_v123_b, 
                  double rou_a, const std::vector<double> &rou_deri_a, double rou_b, const std::vector<double> &rou_deri_b) const {
    ret_ene=0.0;
    ret_v123_a.reserve(3);
    for(int i=0;i<3;i++) ret_v123_a.push_back(0.0);
    ret_v123_b.reserve(3);
    for(int i=0;i<3;i++) ret_v123_b.push_back(0.0);
  }

  // for boost-python
  void op_bp1(double &ret_ene, std::vector<double> &ret_v123, double rou, const std::vector<double> &rou_deri) const{
    this->operator()(ret_ene, ret_v123, rou, rou_deri);
  }
  void op_bp2(double &ret_ene, std::vector<double> &ret_v123_a, std::vector<double> &ret_v123_b, 
                      double rou_a, const std::vector<double> &rou_deri_a, double rou_b, const std::vector<double> &rou_deri_b) const {
    this->operator()(ret_ene, ret_v123_a, ret_v123_b, rou_a, rou_deri_a, rou_b, rou_deri_b);
  }


}; 


// Slater
class Slater_Functor : public GInte_Functor {
public:
  Slater_Functor(){
    flag_gga=0;  use_potential_energy=0; use_grid_inte=1;
  }
  void operator()(double &ret_ene, std::vector<double> &ret_v123, double rou, const std::vector<double> &rou_deri) const{
    DFT_func::func_Slater(ret_ene,ret_v123,rou);
    ret_v123[1] = 0.0;
    ret_v123[2] = 0.0;
  }
  void operator()(double &ret_ene, std::vector<double> &ret_v123_a, std::vector<double> &ret_v123_b, 
                  double rou_a, const std::vector<double> &rou_deri_a, double rou_b, const std::vector<double> &rou_deri_b) const {
    DFT_func::func_USlater(ret_ene, ret_v123_a, ret_v123_b, rou_a, rou_b);
    ret_v123_a[1] = 0.0;
    ret_v123_a[2] = 0.0;
    ret_v123_b[1] = 0.0;
    ret_v123_b[2] = 0.0;
  }

  // for boost-python
  void op_bp1(double &ret_ene, std::vector<double> &ret_v123, double rou, const std::vector<double> &rou_deri) const{
    this->operator()(ret_ene, ret_v123, rou, rou_deri);
  }
  void op_bp2(double &ret_ene, std::vector<double> &ret_v123_a, std::vector<double> &ret_v123_b, 
                      double rou_a, const std::vector<double> &rou_deri_a, double rou_b, const std::vector<double> &rou_deri_b) const {
    this->operator()(ret_ene, ret_v123_a, ret_v123_b, rou_a, rou_deri_a, rou_b, rou_deri_b);
  }


}; 

// B88
class B88_Functor : public GInte_Functor {
public:
  B88_Functor(){
    flag_gga=1;  use_potential_energy=0; use_grid_inte=1;
  }
  void operator()(double &ret_ene, std::vector<double> &ret_v123, double rou, const std::vector<double> &rou_deri) const{
    double gamma_gga=rou_deri[0]*rou_deri[0]+rou_deri[1]*rou_deri[1]+rou_deri[2]*rou_deri[2];
    double ene_b88=0.0,f_rou=0.0,f_gamma_aa=0.0;
    DFT_func::func_B88(ene_b88,f_rou,f_gamma_aa,rou,gamma_gga);
    ret_v123[0] = f_rou;
    ret_v123[1] = 2.0*f_gamma_aa;
    ret_v123[2] = 0.0;
    ret_ene     = ene_b88;
  }

  void operator()(double &ret_ene, std::vector<double> &ret_v123_a, std::vector<double> &ret_v123_b, 
                  double rou_a, const std::vector<double> &rou_deri_a, double rou_b, const std::vector<double> &rou_deri_b) const {
    double gamma_aa, gamma_bb;
    gamma_aa=rou_deri_a[0]*rou_deri_a[0]+rou_deri_a[1]*rou_deri_a[1]+rou_deri_a[2]*rou_deri_a[2];
    gamma_bb=rou_deri_b[0]*rou_deri_b[0]+rou_deri_b[1]*rou_deri_b[1]+rou_deri_b[2]*rou_deri_b[2];
    double ene_b88,f_rou_a,f_rou_b,f_gamma_aa,f_gamma_bb;
    ene_b88=f_rou_a=f_rou_b=f_gamma_aa=f_gamma_bb=0.0;
    DFT_func::func_UB88(ene_b88,f_rou_a,f_rou_b,f_gamma_aa,f_gamma_bb,rou_a,rou_b,gamma_aa,gamma_bb);
    ret_v123_a[0] = f_rou_a; 
    ret_v123_a[1] = 2.0*f_gamma_aa;
    ret_v123_a[2] = 0.0;
    ret_v123_b[0] = f_rou_b; 
    ret_v123_b[1] = 2.0*f_gamma_bb;
    ret_v123_b[2] = 0.0;
    ret_ene       = ene_b88;
  }

  // for boost-python
  void op_bp1(double &ret_ene, std::vector<double> &ret_v123, double rou, const std::vector<double> &rou_deri) const{
    this->operator()(ret_ene, ret_v123, rou, rou_deri);
  }
  void op_bp2(double &ret_ene, std::vector<double> &ret_v123_a, std::vector<double> &ret_v123_b, 
                      double rou_a, const std::vector<double> &rou_deri_a, double rou_b, const std::vector<double> &rou_deri_b) const {
    this->operator()(ret_ene, ret_v123_a, ret_v123_b, rou_a, rou_deri_a, rou_b, rou_deri_b);
  }


};



// SVWN
class SVWN_Functor : public GInte_Functor {
public:
  SVWN_Functor(){
    flag_gga=0;  use_potential_energy=0; use_grid_inte=1;
  }
  void operator()(double &ret_ene, std::vector<double> &ret_v123, double rou, const std::vector<double> &rou_deri) const{
    // Slater
    DFT_func::func_Slater(ret_ene,ret_v123,rou);
    ret_v123[1] = 0.0;
    ret_v123[2] = 0.0;
    // VWN
    double ene_vwn=0.0,f_rou=0.0;
    DFT_func::func_VWN(ene_vwn,f_rou,rou);
    ret_v123[0] += f_rou;
    ret_ene     += ene_vwn;
  }
  void operator()(double &ret_ene, std::vector<double> &ret_v123_a, std::vector<double> &ret_v123_b, 
                  double rou_a, const std::vector<double> &rou_deri_a, double rou_b, const std::vector<double> &rou_deri_b) const {
    // Slater
    DFT_func::func_USlater(ret_ene, ret_v123_a, ret_v123_b, rou_a, rou_b);
    ret_v123_a[1] = 0.0;
    ret_v123_a[2] = 0.0;
    ret_v123_b[1] = 0.0;
    ret_v123_b[2] = 0.0;
    // VWN
    double ene_vwn,f_rou_a,f_rou_b;
    ene_vwn=f_rou_a=f_rou_b=0.0;
    DFT_func::func_UVWN(ene_vwn,f_rou_a,f_rou_b,rou_a,rou_b);
    ret_v123_a[0] += f_rou_a;
    ret_v123_a[1] += 0.0;
    ret_v123_a[2] += 0.0;
    ret_v123_b[0] += f_rou_b;
    ret_v123_b[1] += 0.0;
    ret_v123_b[2] += 0.0;
    ret_ene       += ene_vwn;
  }

  // for boost-python
  void op_bp1(double &ret_ene, std::vector<double> &ret_v123, double rou, const std::vector<double> &rou_deri) const{
    this->operator()(ret_ene, ret_v123, rou, rou_deri);
  }
  void op_bp2(double &ret_ene, std::vector<double> &ret_v123_a, std::vector<double> &ret_v123_b, 
                      double rou_a, const std::vector<double> &rou_deri_a, double rou_b, const std::vector<double> &rou_deri_b) const {
    this->operator()(ret_ene, ret_v123_a, ret_v123_b, rou_a, rou_deri_a, rou_b, rou_deri_b);
  }

}; 



// BLYP
class BLYP_Functor : public GInte_Functor {
public:
  BLYP_Functor(){
    flag_gga=1;  use_potential_energy=0; use_grid_inte=1;
  }
  void operator()(double &ret_ene, std::vector<double> &ret_v123, double rou, const std::vector<double> &rou_deri) const{
    // Becke
    double gamma_gga=rou_deri[0]*rou_deri[0]+rou_deri[1]*rou_deri[1]+rou_deri[2]*rou_deri[2];
    double ene_b88=0.0,f_rou=0.0,f_gamma_aa=0.0;
    DFT_func::func_B88(ene_b88,f_rou,f_gamma_aa,rou,gamma_gga);
    ret_v123[0] = f_rou;
    ret_v123[1] = 2.0*f_gamma_aa;
    ret_v123[2] = 0.0;
    ret_ene     = ene_b88;
    // LYP
    double ene_lyp, f_gamma_ab=0.0;
    ene_lyp=f_rou=f_gamma_aa=0.0;
    ene_lyp=f_rou=f_gamma_aa=f_gamma_ab=0.0;
    DFT_func::func_LYP(ene_lyp,f_rou,f_gamma_aa,f_gamma_ab,rou,rou,gamma_gga,gamma_gga,gamma_gga); 
    ret_v123[0] += f_rou;
    ret_v123[1] += 2.0*f_gamma_aa;
    ret_v123[2] += f_gamma_ab;
    ret_ene     += ene_lyp;
  }

  void operator()(double &ret_ene, std::vector<double> &ret_v123_a, std::vector<double> &ret_v123_b, 
                  double rou_a, const std::vector<double> &rou_deri_a, double rou_b, const std::vector<double> &rou_deri_b) const {

    using namespace std;

    // Becke
    double gamma_aa,gamma_ab,gamma_bb;
    gamma_aa=rou_deri_a[0]*rou_deri_a[0]+rou_deri_a[1]*rou_deri_a[1]+rou_deri_a[2]*rou_deri_a[2];
    gamma_bb=rou_deri_b[0]*rou_deri_b[0]+rou_deri_b[1]*rou_deri_b[1]+rou_deri_b[2]*rou_deri_b[2];
    gamma_ab=rou_deri_a[0]*rou_deri_b[0]+rou_deri_a[1]*rou_deri_b[1]+rou_deri_a[2]*rou_deri_b[2];
    double ene_b88,f_rou_a,f_rou_b,f_gamma_aa,f_gamma_bb;
    ene_b88=f_rou_a=f_rou_b=f_gamma_aa=f_gamma_bb=0.0;
    DFT_func::func_UB88(ene_b88,f_rou_a,f_rou_b,f_gamma_aa,f_gamma_bb,rou_a,rou_b,gamma_aa,gamma_bb);
    ret_v123_a[0] = f_rou_a; 
    ret_v123_a[1] = 2.0*f_gamma_aa;
    ret_v123_a[2] = 0.0;
    ret_v123_b[0] = f_rou_b; 
    ret_v123_b[1] = 2.0*f_gamma_bb;
    ret_v123_b[2] = 0.0;
    ret_ene       = ene_b88;
    // LYP
    double ene_lyp, f_gamma_ab;
    ene_lyp=f_rou_a=f_rou_b=f_gamma_ab=f_gamma_aa=f_gamma_bb=0.0;
    DFT_func::func_ULYP(ene_lyp,f_rou_a,f_rou_b,f_gamma_aa,f_gamma_ab,f_gamma_bb,rou_a,rou_b,gamma_aa,gamma_ab,gamma_bb);
    ret_v123_a[0] += f_rou_a;
    ret_v123_a[1] += 2.0*f_gamma_aa;
    ret_v123_a[2] += f_gamma_ab;
    ret_v123_b[0] += f_rou_b;
    ret_v123_b[1] += 2.0*f_gamma_bb;
    ret_v123_b[2] += f_gamma_ab;
    ret_ene       += ene_lyp;
  }

  // for boost-python
  void op_bp1(double &ret_ene, std::vector<double> &ret_v123, double rou, const std::vector<double> &rou_deri) const{
    this->operator()(ret_ene, ret_v123, rou, rou_deri);
  }
  void op_bp2(double &ret_ene, std::vector<double> &ret_v123_a, std::vector<double> &ret_v123_b, 
                      double rou_a, const std::vector<double> &rou_deri_a, double rou_b, const std::vector<double> &rou_deri_b) const {
    this->operator()(ret_ene, ret_v123_a, ret_v123_b, rou_a, rou_deri_a, rou_b, rou_deri_b);
  }

};




// B3LYP
class B3LYP_Functor : public GInte_Functor {
  double hybrid_slater, hybrid_vwn, hybrid_b88, hybrid_lyp;
public:
  B3LYP_Functor(){
    flag_gga=1;  use_potential_energy=0; use_grid_inte=1;
    hybrid_hf_x   = 0.2;
    hybrid_slater = 0.08;
    hybrid_vwn    = 0.19;
    hybrid_b88    = 0.72;
    hybrid_lyp    = 0.81;
  }
  B3LYP_Functor(const std::vector<double> &in){
    flag_gga=1;  use_potential_energy=0; use_grid_inte=1;
    hybrid_hf_x   = in[0];
    hybrid_slater = in[1];
    hybrid_vwn    = in[2];
    hybrid_b88    = in[3];
    hybrid_lyp    = in[4];
  }
  void operator()(double &ret_ene, std::vector<double> &ret_v123, double rou, const std::vector<double> &rou_deri) const{
    ret_ene=0.0;
    // Slater
    DFT_func::func_Slater(ret_ene,ret_v123,rou);
    ret_ene     *= hybrid_slater;
    ret_v123[0] *= hybrid_slater;
    ret_v123[1]  = 0.0;
    ret_v123[2]  = 0.0;
    // VWN
    double ene_vwn=0.0,f_rou=0.0;
    DFT_func::func_VWN(ene_vwn,f_rou,rou);
    ret_v123[0] += hybrid_vwn*f_rou;
    ret_ene     += hybrid_vwn*ene_vwn;
    // Becke
    double gamma_gga=rou_deri[0]*rou_deri[0]+rou_deri[1]*rou_deri[1]+rou_deri[2]*rou_deri[2];
    double ene_b88=0.0, f_gamma_aa=0.0;
    DFT_func::func_B88(ene_b88,f_rou,f_gamma_aa,rou,gamma_gga);
    ret_v123[0] += hybrid_b88*f_rou;
    ret_v123[1] += hybrid_b88*2.0*f_gamma_aa;
    ret_v123[2] += 0.0;
    ret_ene     += hybrid_b88*ene_b88;
    // LYP
    double ene_lyp, f_gamma_ab=0.0;
    ene_lyp=f_rou=f_gamma_aa=0.0;
    ene_lyp=f_rou=f_gamma_aa=f_gamma_ab=0.0;
    DFT_func::func_LYP(ene_lyp,f_rou,f_gamma_aa,f_gamma_ab,rou,rou,gamma_gga,gamma_gga,gamma_gga); 
    ret_v123[0] += hybrid_lyp*f_rou;
    ret_v123[1] += hybrid_lyp*2.0*f_gamma_aa;
    ret_v123[2] += hybrid_lyp*f_gamma_ab;
    ret_ene     += hybrid_lyp*ene_lyp;
  }

  void operator()(double &ret_ene, std::vector<double> &ret_v123_a, std::vector<double> &ret_v123_b, 
                  double rou_a, const std::vector<double> &rou_deri_a, double rou_b, const std::vector<double> &rou_deri_b) const {
    ret_ene=0.0;
    // Slater
    DFT_func::func_USlater(ret_ene, ret_v123_a, ret_v123_b, rou_a, rou_b);
    ret_v123_a[1]  = 0.0;
    ret_v123_a[2]  = 0.0;
    ret_v123_b[1]  = 0.0;
    ret_v123_b[2]  = 0.0;
    ret_ene       *= hybrid_slater;
    ret_v123_a[0] *= hybrid_slater;
    ret_v123_b[0] *= hybrid_slater;
    //  VWN
    double ene_vwn,f_rou_a,f_rou_b;
    ene_vwn=f_rou_a=f_rou_b=0.0;
    DFT_func::func_UVWN(ene_vwn,f_rou_a,f_rou_b,rou_a,rou_b);
    ret_v123_a[0] += hybrid_vwn*f_rou_a;
    ret_v123_a[1] += 0.0;
    ret_v123_a[2] += 0.0;
    ret_v123_b[0] += hybrid_vwn*f_rou_b;
    ret_v123_b[1] += 0.0;
    ret_v123_b[2] += 0.0;
    ret_ene       += hybrid_vwn*ene_vwn;
    // Becke
    double gamma_aa,gamma_ab,gamma_bb;
    gamma_aa=rou_deri_a[0]*rou_deri_a[0]+rou_deri_a[1]*rou_deri_a[1]+rou_deri_a[2]*rou_deri_a[2];
    gamma_bb=rou_deri_b[0]*rou_deri_b[0]+rou_deri_b[1]*rou_deri_b[1]+rou_deri_b[2]*rou_deri_b[2];
    gamma_ab=rou_deri_a[0]*rou_deri_b[0]+rou_deri_a[1]*rou_deri_b[1]+rou_deri_a[2]*rou_deri_b[2];
    double ene_b88, f_gamma_aa,f_gamma_bb;
    ene_b88=f_rou_a=f_rou_b=f_gamma_aa=f_gamma_bb=0.0;
    DFT_func::func_UB88(ene_b88,f_rou_a,f_rou_b,f_gamma_aa,f_gamma_bb,rou_a,rou_b,gamma_aa,gamma_bb);
    ret_v123_a[0] += hybrid_b88*f_rou_a; 
    ret_v123_a[1] += hybrid_b88*2.0*f_gamma_aa;
    ret_v123_a[2] += 0.0;
    ret_v123_b[0] += hybrid_b88*f_rou_b; 
    ret_v123_b[1] += hybrid_b88*2.0*f_gamma_bb;
    ret_v123_b[2] += 0.0;
    ret_ene       += hybrid_b88*ene_b88;
    // LYP
    double ene_lyp, f_gamma_ab;
    ene_lyp=f_rou_a=f_rou_b=f_gamma_ab=f_gamma_aa=f_gamma_bb=0.0;
    DFT_func::func_ULYP(ene_lyp,f_rou_a,f_rou_b,f_gamma_aa,f_gamma_ab,f_gamma_bb,rou_a,rou_b,gamma_aa,gamma_ab,gamma_bb);
    ret_v123_a[0] += hybrid_lyp*f_rou_a;
    ret_v123_a[1] += hybrid_lyp*2.0*f_gamma_aa;
    ret_v123_a[2] += hybrid_lyp*f_gamma_ab;
    ret_v123_b[0] += hybrid_lyp*f_rou_b;
    ret_v123_b[1] += hybrid_lyp*2.0*f_gamma_bb;
    ret_v123_b[2] += hybrid_lyp*f_gamma_ab;
    ret_ene       += hybrid_lyp*ene_lyp;
  }

  // for boost-python
  void op_bp1(double &ret_ene, std::vector<double> &ret_v123, double rou, const std::vector<double> &rou_deri) const{
    this->operator()(ret_ene, ret_v123, rou, rou_deri);
  }
  void op_bp2(double &ret_ene, std::vector<double> &ret_v123_a, std::vector<double> &ret_v123_b, 
                      double rou_a, const std::vector<double> &rou_deri_a, double rou_b, const std::vector<double> &rou_deri_b) const {
    this->operator()(ret_ene, ret_v123_a, ret_v123_b, rou_a, rou_deri_a, rou_b, rou_deri_b);
  }

};


}  // end of namespace "Lotus_core"
#endif //include-guard

