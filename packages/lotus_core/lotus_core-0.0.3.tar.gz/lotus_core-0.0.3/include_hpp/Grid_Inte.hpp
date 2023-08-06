

#ifndef GRID_INTE_H
#define GRID_INTE_H

#include "gto.hpp"
#include "Util_PBC.hpp"
#include "Util_MPI.hpp"
#include "Grid.hpp"
#include "GInte_Functor.hpp"

#include <vector>
namespace Lotus_core {



template <typename M_tmpl,typename Integ1e>
class Grid_Inte {
  int    mode_deri;
  int    mode_pbc;
  int    mode_grad;
  int    mode_unrestricted;
  int    flag_gga;
  double CUTOFF_DFT;



  struct str_Rou {
    double rou;
    std::vector<double> deri;
    str_Rou(){ set_zero(); }
    void set_zero(){ rou=0.0;  deri.reserve(3); deri[0]=0.0; deri[1]=0.0; deri[2]=0.0; } 
  };

  struct str_V_AO {
    std::vector<double> ao;
    std::vector<double> deri;
    std::vector<double> deri2;
    str_V_AO(){ }
    str_V_AO(int N){
      initialize_N(N);
    }
    void initialize_N(int N){
      ao.reserve(N);
      deri.reserve(N*3);
      deri2.reserve(N*6);
      for(int i=0;i<N;i++)   ao.push_back(0.0);
      for(int i=0;i<3*N;i++) deri.push_back(0.0);
      for(int i=0;i<6*N;i++) deri2.push_back(0.0);
    }
  };

  struct Env {
   str_V_AO str_v_ao;
   std::vector<int> u_cutoff_flag;
   double integ_w;
   int N_cgtos_pbc;
   Cgto *cgtos_pbc;
   int N_cgtos;
   // to use pbc calcualtions
   int N_atoms;
   int loop_g;
   int loop_a;
  };

  struct str_Rou_pbc {
    std::vector<double> rou;
    std::vector<double> rou_deri;
    std::vector<double> ene_pbc;
    std::vector<double> v123;
    void set_zero(int N){
      rou.clear();
      rou_deri.clear();
      ene_pbc.clear();
      v123.clear();
      rou.reserve(N);
      rou_deri.reserve(3*N);
      ene_pbc.reserve(N);
      v123.reserve(3*N);
      for(int i=0;i<N;i++){
        rou.push_back(0.0);
        ene_pbc.push_back(0.0);
        v123.push_back(0.0);  
        v123.push_back(0.0);  
        v123.push_back(0.0);  
        rou_deri.push_back(0.0);
        rou_deri.push_back(0.0);
        rou_deri.push_back(0.0);
      }
    }

  };

  int cal_v_ao_PBC(str_V_AO &str_v,const std::vector<double> &xyz, const std::vector<Shell_Cgto> &tsc, const CTRL_PBC &ctrl_pbc);


//  void  cal_rou_PBC(str_Rou &ret_str_rou, const std::vector<M_tmpl*> &D_PBC,
//                    const std::vector<Shell_Cgto> &tsc, const CTRL_PBC &ctrl_pbc, const std::vector<M_tmpl> &cutoffM, const Env &env);
  void  cal_rou_PBC(double &rou, std::vector<double> &rou_deri, const std::vector<M_tmpl*> &D_PBC,
                    const std::vector<Shell_Cgto> &tsc, const CTRL_PBC &ctrl_pbc, const std::vector<M_tmpl> &cutoffM, const Env &env);

  void set_rou_grid_for_PBC(str_Rou_pbc &str_rou_pbc,const std::vector<Shell_Cgto> &scgtos, const std::vector<M_tmpl*> &D_PBC,
                            const std::vector<double> &Rxyz, const CTRL_PBC &ctrl_pbc, const GInte_Functor &functor);


  void cal_Vxc_sub(std::vector<M_tmpl*> &ret_Vxc_PBC,  const str_Rou &str_rou, 
                   const double *v123, const CTRL_PBC &ctrl_pbc, const Env &env );

  void cal_grad_sub(std::vector<double> &ret_grad, const std::vector<M_tmpl*> &D_PBC, const std::vector<double> &rou_deri, 
                    const double *v123, const CTRL_PBC &ctrl_pbc, const Env &env);

  void set_Rxyz_pbc(std::vector<double> &ret_Rxyz_pbc, std::vector<double> &ret_r_ab,
                    const std::vector<double> &Rxyz, const CTRL_PBC &ctrl_pbc);


  void cal_v_ao(str_V_AO &ret_str_v_ao, const std::vector<Shell_Cgto> &scgtos, const std::vector<double> &xyz);
  void cal_v_ao_deri(str_V_AO &ret_str_v_ao, const std::vector<Shell_Cgto> &scgtos, const std::vector<double> &xyz);
  void cal_v_ao_deri2(str_V_AO &ret_str_v_ao, const std::vector<Shell_Cgto> &scgtos, const std::vector<double> &xyz);

  void cal_rou(str_Rou &ret_str_rou, const std::vector<M_tmpl*> &D_PBC, const Env &env);
//  void cal_rou(double &ret_rou, std::vector<double> &ret_deri, const std::vector<M_tmpl*> &D_PBC, const Env &env);


  void set_u_cutoff_flag(Env &env);

  void cal_Vxc_sub(std::vector<M_tmpl*> &ret_Vxc_a_PBC, std::vector<M_tmpl*> &ret_Vxc_b_PBC, 
                   const str_Rou &str_rou_a, const str_Rou &str_rou_b,
                   const double *v123_a, const double *v123_b, const CTRL_PBC &ctrl_pbc, const Env &env);
                  

  void cal_grad_sub(std::vector<double> &ret_grad, const std::vector<M_tmpl*> &Da_PBC, const std::vector<M_tmpl*> &Db_PBC,
                    const std::vector<double> &rou_deri_a, const std::vector<double> &rou_deri_b, 
                    const double *v123_a, const double *v123_b, const CTRL_PBC &ctrl_pbc, const Env &env);
                   

  void cal_rou_ab(str_Rou &ret_a, str_Rou &ret_b, const std::vector<M_tmpl*> &Da_PBC, const std::vector<M_tmpl*> &Db_PBC,
                  const Env &env);

  void grid_inte_sub_Matrix(double &ret_omp_ene, std::vector<M_tmpl*> &ret_Vxc, 
                            const std::vector<M_tmpl*> &D, const GInte_Functor &functor, const Env &env);

  void grid_inte_sub_grad(std::vector<double> &ret_grad, const std::vector<M_tmpl*> &D,  const GInte_Functor &functor,const Env &env);


  void grid_inte_sub_Matrix_u(double &ret_omp_ene, std::vector<M_tmpl*> &ret_Vxc_a, std::vector<M_tmpl*> &ret_Vxc_b, 
                              const std::vector<M_tmpl*> &Da, const std::vector<M_tmpl*> &Db, const GInte_Functor &functor, const Env &env);

  void grid_inte_sub_grad_u(std::vector<double> &ret_grad, const std::vector<M_tmpl*> &Da, const std::vector<M_tmpl*> &Db, 
                            const GInte_Functor &functor,  const Env &env);

  void grid_inte_sub_Matrix_PBC(double &ret_omp_ene, std::vector<M_tmpl*> &ret_Vxc_PBC, const str_Rou_pbc &str_rou_pbc,
                                const std::vector<M_tmpl*> &D_PBC, const GInte_Functor &functor, const CTRL_PBC &ctrl_pbc, const Env &env);

  double grid_integral_base(std::vector<M_tmpl*> &ret_Vxc_a_PBC, std::vector<M_tmpl*> &ret_Vxc_b_PBC, std::vector<double> &ret_grad,
                            const std::vector<M_tmpl*> &Da_PBC, const std::vector<M_tmpl*> &Db_PBC,
                            const std::vector<Shell_Cgto> &scgtos, const GInte_Functor &functor, const CTRL_PBC &ctrl_pbc);


  double grid_integral_base2(std::vector<M_tmpl> &ret_Vxc_a_PBC, std::vector<M_tmpl> &ret_Vxc_b_PBC, std::vector<double> &ret_grad,
                            const std::vector<M_tmpl> &Da_PBC, const std::vector<M_tmpl> &Db_PBC,
                            const std::vector<Shell_Cgto> &scgtos, const GInte_Functor &functor, const CTRL_PBC &ctrl_pbc){
    int N123_c=ctrl_pbc.get_N123_c();
    ret_Vxc_a_PBC.resize(N123_c);
    ret_Vxc_b_PBC.resize(N123_c);
    std::vector<M_tmpl*> tmpM_a(N123_c);
    std::vector<M_tmpl*> tmpM_b(N123_c);
    std::vector<M_tmpl*> tmpD_a(N123_c);
    std::vector<M_tmpl*> tmpD_b(N123_c);
    for(int q=0;q<N123_c;q++){
      tmpM_a[q]=&ret_Vxc_a_PBC[q];
      tmpM_b[q]=&ret_Vxc_b_PBC[q];
      tmpD_a[q]=const_cast<M_tmpl*>(&Da_PBC[q]);
      tmpD_b[q]=const_cast<M_tmpl*>(&Db_PBC[q]);
    }
    if(flag_gga==1) mode_deri=1;
    return grid_integral_base(tmpM_a, tmpM_b, ret_grad, tmpD_a, tmpD_b, scgtos, functor, ctrl_pbc);
  }


  double grid_integral_base3(M_tmpl &ret_Vxc_a, M_tmpl &ret_Vxc_b, std::vector<double> &ret_grad,
                            const M_tmpl &Da, const M_tmpl &Db,
                            const std::vector<Shell_Cgto> &scgtos, const GInte_Functor &functor, const CTRL_PBC &ctrl_pbc){
    std::vector<M_tmpl*> tmpM_a(1);
    std::vector<M_tmpl*> tmpM_b(1);
    std::vector<M_tmpl*> tmpD_a(1);
    std::vector<M_tmpl*> tmpD_b(1);
    tmpM_a[0]=&ret_Vxc_a;
    tmpM_b[0]=&ret_Vxc_b;
    tmpD_a[0]=const_cast<M_tmpl*>(&Da);
    tmpD_b[0]=const_cast<M_tmpl*>(&Db);
    if(flag_gga==1) mode_deri=1;
    return grid_integral_base(tmpM_a, tmpM_b, ret_grad, tmpD_a, tmpD_b, scgtos, functor, ctrl_pbc);
  }






public:


  class Grid_Data {
    double R1_GRID;
    int N1_GRID;
    int N2_GRID;
    int N3_GRID;
    int select_grid;
  public:
    Grid_Data(){
      R1_GRID=1.0;
      N1_GRID=25;
      N2_GRID=13;
      N3_GRID=12;
      select_grid=0;
    }
    double get_R1_GRID() const { return R1_GRID; }
    int    get_N1_GRID() const { return N1_GRID; }
    int    get_N2_GRID() const { return N2_GRID; }
    int    get_N3_GRID() const { return N3_GRID; }
    int    get_select_grid() const {  return select_grid; }
    int    get_total_grid()  const {
      int ret;
      if(select_grid==0) ret = 302*N1_GRID + 50*N2_GRID + 38*N3_GRID;
      else               ret = N1_GRID*N2_GRID*N2_GRID*2;
      return ret;
    }
    void   get_grid(std::vector<double> &ret_xyzw_g) const { 
      int Ng=get_total_grid();
      ret_xyzw_g.clear();
      ret_xyzw_g.reserve(Ng*4);
      if(select_grid==0) Grid::construct_grid_LEB(ret_xyzw_g,R1_GRID,N1_GRID,N2_GRID,N3_GRID); 
      else               Grid::construct_grid_GL( ret_xyzw_g,R1_GRID,N1_GRID,N2_GRID);
    }
  } grid_data;



  // constructor
  Grid_Inte(){
    set_clear();
  }
    
  void set_clear(){
    mode_pbc          = MOLECULE;
    mode_grad         = MATRIX;
    mode_unrestricted = RESTRICTED;
    flag_gga          = 0;
    mode_deri         = 0;
    CUTOFF_DFT=1.0e-10;
  }
               
  enum { MOLECULE=0, PBC=1};
  enum { RESTRICTED=0, UNRESTRICTED=1 };
  enum { MATRIX=0,    GRADIENT=1 };






  double grid_integral_mat_u(M_tmpl &ret_V_a, M_tmpl &ret_V_b, const M_tmpl &D_a, const M_tmpl &D_b,
                             const std::vector<Shell_Cgto> &scgtos, const GInte_Functor &functor){
    if(functor.get_flag_gga()==1) mode_deri=1;
    flag_gga = functor.get_flag_gga();
    std::vector<double> dmy_grad;
    CTRL_PBC dmy_ctrl_pbc;
    mode_unrestricted = UNRESTRICTED; 
    double ret_ene=grid_integral_base3(ret_V_a, ret_V_b, dmy_grad, D_a, D_b, scgtos, functor, dmy_ctrl_pbc);
    set_clear();
    return ret_ene;
  }


  double grid_integral_mat(M_tmpl &ret_V,  const M_tmpl &D, const std::vector<Shell_Cgto> &scgtos, const GInte_Functor &functor){
    if(functor.get_flag_gga()==1) mode_deri=1;
    flag_gga = functor.get_flag_gga();
    std::vector<double> dmy_grad;
    M_tmpl dmy_V, dmy_D;
    CTRL_PBC dmy_ctrl_pbc;
    double ret_ene=grid_integral_base3(ret_V, dmy_V, dmy_grad, D, dmy_D, scgtos, functor, dmy_ctrl_pbc);
    set_clear();
    return ret_ene;
  }

  
  double grid_integral_mat_PBC(std::vector<M_tmpl> &retV_PBC,  const std::vector<M_tmpl> &D_PBC,
                               const std::vector<Shell_Cgto> &scgtos, const CTRL_PBC &ctrl_pbc, const GInte_Functor &functor){
    if(functor.get_flag_gga()==1) mode_deri=1;
    flag_gga = functor.get_flag_gga();
    std::vector<double> dmy_grad;
    std::vector<M_tmpl> dmyV_PBC;
    mode_pbc = PBC;
    double ret_ene=grid_integral_base2(retV_PBC, dmyV_PBC, dmy_grad, D_PBC, D_PBC, scgtos, functor, ctrl_pbc);
    set_clear();
    return ret_ene;
  }


  std::vector<double> cal_grad_u(const std::vector<Shell_Cgto> &scgtos, const M_tmpl &D_a, const M_tmpl &D_b,
                                 const GInte_Functor &functor){
    int N_atoms = Util_GTO::get_N_atoms(scgtos);
    std::vector<double> ret_grad(N_atoms*3,0.0);
    mode_deri=1;
    flag_gga = functor.get_flag_gga();
    M_tmpl dmy_Va, dmy_Vb;
    CTRL_PBC dmy_ctrl_pbc;
    mode_grad         = GRADIENT;
    mode_unrestricted = UNRESTRICTED; 
    double dmy_ene=grid_integral_base3(dmy_Va, dmy_Vb, ret_grad, D_a, D_b, scgtos, functor, dmy_ctrl_pbc);
    set_clear();
    return ret_grad;
  }


  std::vector<double> cal_grad(const std::vector<Shell_Cgto> &scgtos, const M_tmpl &D, const GInte_Functor &functor){
    int N_atoms = Util_GTO::get_N_atoms(scgtos);
    std::vector<double> ret_grad(N_atoms*3,0.0);
    mode_deri=1;
    flag_gga = functor.get_flag_gga();
    M_tmpl dmy_Va, dmy_Vb, dmy_D;
    CTRL_PBC dmy_ctrl_pbc;
    mode_grad         = GRADIENT;
    double dmy_ene=grid_integral_base3(dmy_Va, dmy_Vb, ret_grad, D, dmy_D, scgtos, functor, dmy_ctrl_pbc);
    set_clear();
    return ret_grad;
  }




};

}  // end of namespace "Lotus_core"

#include "detail/Grid_Inte_detail.hpp"

#endif // include-guard


