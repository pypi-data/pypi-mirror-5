
#ifndef GRID_DETAIL_HPP
#define GRID_DETAIL_HPP


#define _USE_MATH_DEFINES
#include <math.h>
#include <stdlib.h>

#include "Grid.hpp"

#include <iostream>
namespace Lotus_core {


void Grid::set_GL(std::vector<double> &gl_x,std::vector<double> &gl_w,int gl_n)
{
  // Gauss-Legendre quadrature
  // Integrals[f(x),{x,-1,1}]
  double z1,z,xm,xl,pp,p3,p2,p1;
  const double gl_cutoff=1.0e-15; 

 
  int m=(gl_n+1)/2;
  xm= 0.0;
  xl= 1.0;

  gl_x.reserve(gl_n); 
  gl_w.reserve(gl_n);
  gl_x.clear(); 
  gl_w.clear();
  for(int i=0;i<gl_n;i++){
    gl_x.push_back(0.0);
    gl_w.push_back(0.0);
  } 

  for(int i=1;i<=m;i++){
    z=cos(M_PI*(i-0.25)/(gl_n+0.5));
     do{
       p1=1.0;
       p2=0.0;
       for(int j=1;j<=gl_n;j++){
         p3=p2;
         p2=p1;
         p1=((2.0*j-1.0)*z*p2-(j-1.0)*p3)/j;
       }
       pp=gl_n*(z*p1-p2)/(z*z-1.0);
       z1=z;
       z=z1-p1/pp;
    }while(fabs(z-z1)>gl_cutoff);
    gl_x[i-1]=xm-xl*z;
    gl_x[gl_n+1-i-1]=xm+xl*z;
    gl_w[i-1]=2.0*xl/((1.0-z*z)*pp*pp);
    gl_w[gl_n+1-i-1]=gl_w[i-1];
  }

}

void Grid::radial_grid_GL(std::vector<double> &gl_r,std::vector<double> &gl_w,int gl_n,double R1)
{
  // Gauss-Legendre quadrature
  // Integral[f(r)*4*M_PI*r^2,{r,0,inf.}]
  // r=4.0*R1*(1+x)/(1-x)

  gl_r.reserve(gl_n); 
  gl_w.reserve(gl_n);
  gl_r.clear(); 
  gl_w.clear();
  for(int i=0;i<gl_n;i++){
    gl_r.push_back(0.0);
    gl_w.push_back(0.0);
  } 


  double b_x,r,w_r;
  Grid::set_GL(gl_r,gl_w,gl_n);
  for(int i=0;i<gl_n;i++){
    b_x=gl_r[i];
    r=R1*(1.0+b_x)/(1.0-b_x);
    gl_r[i]=r;
    w_r=4.0*M_PI*gl_w[i]*r*r*2.0*R1/((1.0-b_x)*(1.0-b_x));
    gl_w[i]=w_r;
  }
}

void Grid::angular_grid_GL(std::vector<double> &gl_x, std::vector<double> &gl_y, std::vector<double> &gl_z,
                           std::vector<double> &gl_w,int gl_n)
{
  gl_x.reserve(gl_n*gl_n*2);
  gl_y.reserve(gl_n*gl_n*2);
  gl_z.reserve(gl_n*gl_n*2);
  gl_w.reserve(gl_n*gl_n*2);
  gl_x.clear();
  gl_y.clear();
  gl_z.clear();
  gl_w.clear();


  // Gauss-Legendre-based angular grid, sum[gl_w]=1.0
  double x,y,z,w,cos_theta,sin_theta,phai;
  std::vector<double> gl_x_theta,gl_w_theta,gl_x_phai,gl_w_phai;
  Grid::set_GL(gl_x_theta,gl_w_theta,gl_n);
  Grid::set_GL(gl_x_phai,gl_w_phai,2*gl_n);
  for(int j=0;j<gl_n;j++){
    cos_theta=gl_x_theta[j];
    sin_theta=sqrt(1-cos_theta*cos_theta);
    for(int k=0;k<2*gl_n;k++){
      phai=M_PI*(gl_x_phai[k]+1.0);
      x=sin_theta*cos(phai);
      y=sin_theta*sin(phai);
      z=cos_theta;
      w=gl_w_theta[j]*gl_w_phai[k]/4.0;
      gl_x.push_back(x);
      gl_y.push_back(y);
      gl_z.push_back(z);
      gl_w.push_back(w);
    }
  }
}

void Grid::radial_grid_GC(std::vector<double> &gc_r,std::vector<double> &gc_w,int n)
{
  // Gauss-Chebyshev quadrature
  // Integral[f(r)*4*M_PI*r^2,{r,0,inf.}]
  // r=((1+x)^(0.6))*(ln(2/(1-x))/ln2)


  gc_r.reserve(n);
  gc_w.reserve(n);
  gc_r.clear();
  gc_w.clear();
  for(int i=0;i<n;i++){
    gc_r.push_back(0.0);
    gc_w.push_back(0.0);
  }

  int j;
  double x,r; 
  for(int i=0;i<n;i++){
    j=i+1;
    x=cos((M_PI/(n+1))*j);
    r=pow(1+x,0.6)*(log(2.0/(1.0-x))/log(2.0));
    gc_r[i]=r;
    gc_w[i]=4.0*M_PI*r*r*(M_PI/(n+1))*sin((M_PI/(n+1))*j)*(1.0/log(2.0))
           *( 0.6*pow(1+x,-0.4)*log(2.0/(1.0-x)) + pow(1+x,0.6)/(1.0-x) );
  }


}

void Grid::angular_grid_LEBEDEV(std::vector<double> &leb_x, std::vector<double> &leb_y, std::vector<double> &leb_z, 
                                std::vector<double> &leb_w, int leb_n)
{
  using namespace std;
                               
  leb_x.reserve(302);
  leb_y.reserve(302);
  leb_z.reserve(302);
  leb_w.reserve(302);
  leb_x.clear();
  leb_y.clear();
  leb_z.clear();
  leb_w.clear();

  double L302x[12]={1.000000000000e0, 0.577350269190e0, 0.701176641609e0, 0.656632941022e0,
                    0.472905413258e0, 0.351564034558e0, 0.221964523631e0, 0.961830852303e-1,
                    0.820326419828e0, 0.964408914879e0, 0.251003475177e0, 0.902442529533e0};
  double L302y[12]={0.000000000000e0, 0.577350269190e0, 0.701176641609e0, 0.656632941022e0,
                    0.472905413258e0, 0.351564034558e0, 0.221964523631e0, 0.961830852303e-1,
                    0.571895589188e0, 0.264415288706e0, 0.800072749407e0, 0.412772408317e0};
  double L302z[12]={0.000000000000e0, 0.577350269190e0, 0.129238672710e0, 0.371034178385e0,
                    0.743452042987e0, 0.867643624544e0, 0.949454317226e0, 0.990705621379e0,
                    0.000000000000e0, 0.000000000000e0, 0.544867737258e0, 0.123354853258e0};
  double L302w[12]={8.545911728780e-4,3.599119285020e-3,3.650045807680e-3,3.604822601420e-3,
                    3.576729661730e-3,3.449788424290e-3,3.108953122380e-3,2.352101413660e-3,
                    3.600820932220e-3,2.982344963170e-3,3.571540554270e-3,3.392312205010e-3};
                    

  double L50x[4]  ={1.000000000000e0, 0.707106781187e0, 0.577350269190e0, 0.301511344578e0};
  double L50y[4]  ={0.000000000000e0, 0.707106781187e0, 0.577350269190e0, 0.301511344578e0};
  double L50z[4]  ={0.000000000000e0, 0.000000000000e0, 0.577350269190e0, 0.904534033733e0};
  double L50w[4]  ={1.269841269850e-2,2.257495590830e-2,2.109375000000e-2,2.017333553790e-2};

  double L38x[3]  ={1.000000000000e0, 0.577350269190e0, 0.888073833977e0};
  double L38y[3]  ={0.000000000000e0, 0.577350269190e0, 0.459700843381e0};
  double L38z[3]  ={0.000000000000e0, 0.577350269190e0, 0.000000000000e0};
  double L38w[3]  ={9.523809523870e-3,3.214285714290e-2,2.857142857140e-2};

  int max_i,min_j,max_j;
  double sum_w;

  double LNx[12],LNy[12],LNz[12],LNw[12];
  if(leb_n==302){
    for(int i=0;i<12;i++){
      LNx[i]=L302x[i]; LNy[i]=L302y[i]; LNz[i]=L302z[i]; LNw[i]=L302w[i];
    } 
    max_i=12;
  }else if(leb_n==50){
    for(int i=0;i<4;i++){
      LNx[i]=L50x[i]; LNy[i]=L50y[i]; LNz[i]=L50z[i]; LNw[i]=L50w[i];
    } 
    max_i=4;
  }else if(leb_n==38){
    for(int i=0;i<3;i++){
      LNx[i]=L38x[i]; LNy[i]=L38y[i]; LNz[i]=L38z[i]; LNw[i]=L38w[i];
    }
    max_i=3;
  }else{
    cout<<" Error in angular_grid_LEBEDEV, n=302,50 or 38, input value="<<leb_n<<endl;
    exit(1);
  }

  int k=0;
  for(int i=0;i<max_i;i++){
    leb_x[k]=LNx[i]; leb_y[k]=LNy[i]; leb_z[k]=LNz[i]; leb_w[k]=LNw[i];
    min_j=k;
    k++;
//    if( LNx[i]!=LNy[i] || LNy[i]!=LNz[i] || LNz[i]!=LNx[i]){
    if( fabs(LNx[i]-LNy[i])>1.0e-14 || fabs(LNy[i]-LNz[i])>1.0e-14 || fabs(LNz[i]-LNx[i])>1.0e-14){
      leb_x[k]=LNy[i]; leb_y[k]=LNz[i]; leb_z[k]=LNx[i]; leb_w[k]=LNw[i];
      k++;
      leb_x[k]=LNz[i]; leb_y[k]=LNx[i]; leb_z[k]=LNy[i]; leb_w[k]=LNw[i];
      k++;
    }
//    if( LNx[i]!=LNy[i] && LNy[i]!=LNz[i] && LNz[i]!=LNx[i]){
    if( fabs(LNx[i]-LNy[i])>1.0e-14 && fabs(LNy[i]-LNz[i])>1.0e-14 && fabs(LNz[i]-LNx[i])>1.0e-14){
      leb_x[k]=LNy[i]; leb_y[k]=LNx[i]; leb_z[k]=LNz[i]; leb_w[k]=LNw[i];
      k++;
      leb_x[k]=LNx[i]; leb_y[k]=LNz[i]; leb_z[k]=LNy[i]; leb_w[k]=LNw[i];
      k++;
      leb_x[k]=LNz[i]; leb_y[k]=LNy[i]; leb_z[k]=LNx[i]; leb_w[k]=LNw[i];
      k++;
    }
    max_j=k;
    for(int j=min_j;j<max_j;j++){
//      if( leb_x[j]!=0.0 ){
      if( fabs(leb_x[j])>1.0e-14 ){
        leb_x[k]=-1.0*leb_x[j]; leb_y[k]=leb_y[j]; leb_z[k]=leb_z[j]; leb_w[k]=leb_w[j];
        k++;
      }
    }
    max_j=k;
    for(int j=min_j;j<max_j;j++){
//      if( leb_y[j]!=0.0 ){
      if( fabs(leb_y[j])>1.0e-14 ){
        leb_x[k]=leb_x[j]; leb_y[k]=-1.0*leb_y[j]; leb_z[k]=leb_z[j]; leb_w[k]=leb_w[j];
        k++;
      }
    }
    max_j=k;
    for(int j=min_j;j<max_j;j++){
//      if( leb_z[j]!=0.0 ){
      if( fabs(leb_z[j])>1.0e-14 ){
        leb_x[k]=leb_x[j]; leb_y[k]=leb_y[j]; leb_z[k]=-1.0*leb_z[j]; leb_w[k]=leb_w[j];
        k++;
      }
    }
  }

  if( k!=leb_n ){
    cout<<" Error in angular_grid_LEBEDEV of Grid class, k="<<k<<endl;
    exit(1);
  }
  sum_w=0.0;
  for(int j=0;j<leb_n;j++){
    sum_w+=leb_w[j];
  }
  if( fabs(sum_w-1.0) > 1.0e-10 ){
    cout<<" Error in angular_grid_LEBEDEV of Grid class, sum_w "<<sum_w<<endl;
    exit(1);
  }

}



void Grid::construct_grid_LEB(std::vector<double> &ret_xyzw,double R1,int N302,int N50,int N38)
{
  ret_xyzw.clear();
                                 
  int total_N=N302+N50+N38;
  double R2; 
  std::vector<double> gc_r,gc_w;
  Grid::radial_grid_GC(gc_r,gc_w,total_N);

  std::vector<double> leb_x,leb_y,leb_z,leb_w;

  Grid::angular_grid_LEBEDEV(leb_x,leb_y,leb_z,leb_w,302);
  for(int i=0;i<N302;i++){
    R2=gc_r[i];
    for(int j=0;j<302;j++){
      ret_xyzw.push_back(R1*R2*leb_x[j]);
      ret_xyzw.push_back(R1*R2*leb_y[j]); 
      ret_xyzw.push_back(R1*R2*leb_z[j]); 
      ret_xyzw.push_back(R1*R1*R1*gc_w[i]*leb_w[j]);
    }
  }
  Grid::angular_grid_LEBEDEV(leb_x,leb_y,leb_z,leb_w,50);
  for(int i=N302;i<(N302+N50);i++){
    R2=gc_r[i];
    for(int j=0;j<50;j++){
      ret_xyzw.push_back(R1*R2*leb_x[j]); 
      ret_xyzw.push_back(R1*R2*leb_y[j]); 
      ret_xyzw.push_back(R1*R2*leb_z[j]); 
      ret_xyzw.push_back(R1*R1*R1*gc_w[i]*leb_w[j]);
    }
  }
  Grid::angular_grid_LEBEDEV(leb_x,leb_y,leb_z,leb_w,38);
  for(int i=(N302+N50);i<(N302+N50+N38);i++){
    R2=gc_r[i];
    for(int j=0;j<38;j++){
      ret_xyzw.push_back(R1*R2*leb_x[j]);
      ret_xyzw.push_back(R1*R2*leb_y[j]);
      ret_xyzw.push_back(R1*R2*leb_z[j]); 
      ret_xyzw.push_back(R1*R1*R1*gc_w[i]*leb_w[j]);
    }
  }

}



void Grid::construct_grid_GL(std::vector<double> &ret_xyzw,double R1_GL,int N1,int N2)
{

  ret_xyzw.reserve(N1*N2*N2*2);
  ret_xyzw.clear();
                                
  std::vector<double> gl_r,gl_w;
  Grid::radial_grid_GL(gl_r,gl_w,N1,R1_GL);
  std::vector<double> ag_x,ag_y,ag_z,ag_w;
  Grid::angular_grid_GL(ag_x,ag_y,ag_z,ag_w,N2);
  for(int i=0;i<N1;i++){
    for(int j=0;j<2*N2*N2;j++){
      ret_xyzw.push_back(gl_r[i]*ag_x[j]);
      ret_xyzw.push_back(gl_r[i]*ag_y[j]);
      ret_xyzw.push_back(gl_r[i]*ag_z[j]);
      ret_xyzw.push_back(gl_w[i]*ag_w[j]);
    }
  }
}


double Grid::cal_Ran(int atom_no,const std::vector<double> &Rxyz)
{
  int N_atoms=Rxyz.size()/3;
  int a=atom_no;
  double Ran=1.0e5;
  for(int b=0;b<N_atoms;b++){
    double tmp_v=sqrt((Rxyz[a*3+0]-Rxyz[b*3+0])*(Rxyz[a*3+0]-Rxyz[b*3+0])
                     +(Rxyz[a*3+1]-Rxyz[b*3+1])*(Rxyz[a*3+1]-Rxyz[b*3+1])
                     +(Rxyz[a*3+2]-Rxyz[b*3+2])*(Rxyz[a*3+2]-Rxyz[b*3+2]));
    if(tmp_v<Ran) Ran=tmp_v;
  }
  return Ran;
}      


std::vector<double> Grid::grid_weight_ATOM(int atom_no, const std::vector<double> &Rxyz,
                                           const std::vector<double> &R_ab,int g,const std::vector<double> &xyzw_g)
{
  int N_atoms=Rxyz.size()/3;
  double Ran=cal_Ran(atom_no,Rxyz);
  std::vector<double> ret_xyzw(4, 0.0);
                           
  int a=atom_no;
  //
  double x,y,z;
  std::vector<double> r_p(N_atoms,0.0);

  x=xyzw_g[g*4+0]+Rxyz[a*3+0];  y=xyzw_g[g*4+1]+Rxyz[a*3+1];  z=xyzw_g[g*4+2]+Rxyz[a*3+2];
  if(fabs(xyzw_g[g*4+3])>1.0e-12){
    const double SSF_a=0.64;
    double r=sqrt(xyzw_g[g*4+0]*xyzw_g[g*4+0]+xyzw_g[g*4+1]*xyzw_g[g*4+1]+xyzw_g[g*4+2]*xyzw_g[g*4+2]);
    //
    // calculation for w_atom, integ_w;
    double w_atom=0,integ_w;
    if(r<0.5*(1.0-SSF_a)*Ran){
      w_atom=1.0;
    }else{
      double sum_w_myu=0.0;
      for(int pa=0;pa<N_atoms;pa++){
        r_p[pa]=sqrt((x-Rxyz[pa*3+0])*(x-Rxyz[pa*3+0])+(y-Rxyz[pa*3+1])*(y-Rxyz[pa*3+1])+(z-Rxyz[pa*3+2])*(z-Rxyz[pa*3+2]));
      }
      for(int pa=0;pa<N_atoms;pa++){
        double r_pa=r_p[pa];
        double w_myu=1.0;
        for(int pb=0;pb<N_atoms;pb++){
          if(pa!=pb){
            double r_pb=r_p[pb];
            double myu_ab=(r_pa-r_pb)/R_ab[pa*N_atoms+pb];
            if(myu_ab<-SSF_a){        // g_myu=-1.0; s_myu=1.0;
            }else if(myu_ab>=SSF_a){  // g_myu=1.0;  s_myu=0.0; 
              w_myu=0.0; 
              break;
            }else{
              double myu_div=myu_ab/SSF_a;
              double g_myu=(1.0/16.0)*(35.0*myu_div -35.0*myu_div*myu_div*myu_div
                                      +21.0*myu_div*myu_div*myu_div*myu_div*myu_div
                                       -5.0*myu_div*myu_div*myu_div*myu_div*myu_div*myu_div*myu_div);
              double s_myu=0.5*(1.0-g_myu);
              w_myu*=s_myu;
            }
          }
        }
        if(a==pa) w_atom=w_myu;
        sum_w_myu+=w_myu;
      }
      w_atom/=sum_w_myu;
    }
    integ_w=w_atom*xyzw_g[g*4+3];
    //
    ret_xyzw[0]=x; ret_xyzw[1]=y; ret_xyzw[2]=z; ret_xyzw[3]=integ_w;
  }else{
    ret_xyzw[0]=x; ret_xyzw[1]=y; ret_xyzw[2]=z; ret_xyzw[3]=0.0;
  }

  return ret_xyzw;
}     


}  // end of namespace "Lotus_core"

#endif // end of include-guard


