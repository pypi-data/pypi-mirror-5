
#ifndef GRID_H
#define GRID_H


#include <vector>


namespace Lotus_core {

class Grid {
public:


  // Gauss-Legendre quadrature,  Integral[f(x),{x,-1,1}]
  inline static void set_GL(std::vector<double> &gl_x,std::vector<double> &gl_w,int gl_n);
   
  // Gauss-Legendre quadrature,  Integral[f(r)*4*PI*r^2,{x,0,inf.}]
  inline static void radial_grid_GL(std::vector<double> &gl_r,std::vector<double> &gl_w,int gl_n,double R1);
  
  // Gauss-Legendre-based angular grid, sum[gl_w]=1.0;
  inline static void angular_grid_GL(std::vector<double> &gl_x, std::vector<double> &gl_y, std::vector<double> &gl_z,
                              std::vector<double> &gl_w,int gl_n);
 
  // Gauss-Chebyshev quadrature,  Integral[f(r)*4*PI*r^2,{r,0,inf.}],  r=((1+x)^(0.6))*(ln(2/(1-x))/ln2)
  inline static void radial_grid_GC(std::vector<double> &gc_r,std::vector<double> &gc_w,int n);

  // angular grid point for Lebedev quadrature, n=302, 50, or 38
  inline static void angular_grid_LEBEDEV(std::vector<double> &leb_x, std::vector<double> &leb_y, std::vector<double> &leb_z, 
                                   std::vector<double> &leb_w, int leb_n);

  inline static void construct_grid_LEB(std::vector<double> &ret_xyzw,double R1,int N302,int N50,int N38);

  inline static void construct_grid_GL(std::vector<double> &ret_xyzw,double R1_GL,int N1,int N2);

  inline static double cal_Ran(int atom_no,const std::vector<double> &Rxyz);


  inline static std::vector<double> grid_weight_ATOM(int atom_no, const std::vector<double> &Rxyz, const std::vector<double> &R_ab, 
                                              int g,const std::vector<double> &xyzw_g);
                                       


};



}  // end of namespace "Lotus_core"


#include "detail/Grid_detail.hpp"

#endif // include-Guard
