

#ifdef _OPENMP
#include <omp.h>
#endif


#define _USE_MATH_DEFINES
#include <math.h>


#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <cstdlib>

#ifndef ECP_DETAIL_HPP
#define ECP_DETAIL_HPP


namespace Lotus_core {


std::vector<ECP> ECP::get_ecps_from_file(const char *filename)
{
  std::string qm_string=Util_GTO::get_string_from_file(filename);
  return ECP::get_ecps_from_string(qm_string.c_str());
}


std::vector<ECP> ECP::get_ecps_from_string(const char *qm_string)
{
  std::vector<ECP> ret_ecps;

  std::istringstream is(qm_string);
//  std::ifstream is(filename);
//  if(!is){
//    std::cout<<" Error: cannnot open (get_ecps_from_file) "<<filename<<std::endl;
//    exit(1);
//  }


  int N_scgtos,N_ecps,N_atoms;
  char nop[512];
  N_scgtos=N_ecps=N_atoms=0;
 
  is>>nop;
  is>>nop;
  is>>N_scgtos;  is>>N_ecps;  is>>N_atoms;

  // MOLECULE_COORDINATE
  int atom_no,in_atom_Z;
  double x,y,z;
  is>>nop;
  for(int a=0;a<N_atoms;a++){
    is>>nop;  is>>in_atom_Z; is>>nop; is>>atom_no; is>>nop; 
    is>>x;  is>>y;  is>>z;
  }

  // SCGTOS
  int no_scgtos,num_pgto,shell_type;
  int atom_type;
  double g,d;
  is>>nop;
  for(int i=0;i<N_scgtos;i++){
    is>>nop; is>>nop; is>>no_scgtos; is>>nop; is>>shell_type; 
    is>>nop; is>>atom_no; is>>nop; is>>nop; is>>nop; is>>atom_type; is>>nop;
    is>>x; is>>y; is>>z;
    is>>num_pgto;
    for(int j=0;j<num_pgto;j++){
      is>>g; is>>d;
    }
    
  }

  // ECP
  is>>nop;
  if(N_ecps!=0){
    for(int i=0;i<N_ecps;i++){
      std::vector<double> C(3,0.0);
      int k_ecp;
      int no_ecps,num_core_ele,num,L;
      is>>nop; is>>nop; is>>no_ecps; is>>nop; is>>num_core_ele; 
      is>>nop; is>>L; is>>nop; is>>atom_no; is>>nop; is>>nop;
      is>>nop; is>>atom_type; is>>nop; is>>x; is>>y; is>>z;
      is>>num; 
      C[0]=x; C[1]=y; C[2]=z;
      ret_ecps.push_back(ECP());
      ret_ecps[i].set_L(L);
      ret_ecps[i].set_atom_no(atom_no);
      ret_ecps[i].set_C(C);
      ret_ecps[i].set_core_ele(num_core_ele);
      for(int j=0;j<num;j++){
        double g_ecp,d_ecp;
        is>>d_ecp; is>>k_ecp; is>>g_ecp;
        ret_ecps[i].set_gkd(g_ecp,k_ecp,d_ecp);
      }
    }
  }

  return ret_ecps;
}


void RealSphericalHarmonic::set_init(){
//
//
  num[0][0]=1;
  r[0][0][0]=0; s[0][0][0]=0; t[0][0][0]=0;    keisu[0][0][0]=sqrt(1.0/(4*M_PI));
//
//   
  num[1][0]=1;    //  1,-1     y
  r[1][0][0]=0; s[1][0][0]=1; t[1][0][0]=0;    keisu[1][0][0]=-1.0*sqrt(3.0/(4*M_PI));

  num[1][1]=1;   //   1,0      z
  r[1][1][0]=0; s[1][1][0]=0; t[1][1][0]=1;    keisu[1][1][0]=     sqrt(3.0/(4*M_PI));

  num[1][2]=1;   //   1,1      x
  r[1][2][0]=1; s[1][2][0]=0; t[1][2][0]=0;    keisu[1][2][0]=-1.0*sqrt(3.0/(4*M_PI));
//
//
  num[2][0]=1;   //   2,-2     xy
  r[2][0][0]=1; s[2][0][0]=1; t[2][0][0]=0;    keisu[2][0][0]=-1.0*sqrt(15.0/(4*M_PI));

  num[2][1]=1;   //   2,-1     yz
  r[2][1][0]=0; s[2][1][0]=1; t[2][1][0]=1;    keisu[2][1][0]=-1.0*sqrt(15.0/(4*M_PI));
 

  num[2][2]=3;   //   2,0      3z^2 - r^2 = 2z^2 - x^2 - y^2
  r[2][2][0]=0; s[2][2][0]=0; t[2][2][0]=2;    keisu[2][2][0]= 2.0*sqrt(5.0/(16*M_PI));
  r[2][2][1]=2; s[2][2][1]=0; t[2][2][1]=0;    keisu[2][2][1]=-1.0*sqrt(5.0/(16*M_PI));
  r[2][2][2]=0; s[2][2][2]=2; t[2][2][2]=0;    keisu[2][2][2]=-1.0*sqrt(5.0/(16*M_PI));

  num[2][3]=1;   //   2,1       zx
  r[2][3][0]=1; s[2][3][0]=0; t[2][3][0]=1;    keisu[2][3][0]= -1.0*sqrt(15.0/(4*M_PI));

  num[2][4]=2;   //   2,2       x^2 - y^2
  r[2][4][0]=2; s[2][4][0]=0; t[2][4][0]=0;    keisu[2][4][0]= 1.0*sqrt(15.0/(16*M_PI));
  r[2][4][1]=0; s[2][4][1]=2; t[2][4][1]=0;    keisu[2][4][1]=-1.0*sqrt(15.0/(16*M_PI));
//
//
  num[3][0]=2;   //   3,-3    -  3yx^2 + y^3
  r[3][0][0]=2; s[3][0][0]=1; t[3][0][0]=0;    keisu[3][0][0]= -(3.0/4.0)*sqrt(35.0/(2*M_PI));
  r[3][0][1]=0; s[3][0][1]=3; t[3][0][1]=0;    keisu[3][0][1]=  (1.0/4.0)*sqrt(35.0/(2*M_PI));

  num[3][1]=1;  //    3,-2       xyz
  r[3][1][0]=1; s[3][1][0]=1; t[3][1][0]=1;    keisu[3][1][0]= -(1.0/2.0)*sqrt(105/M_PI);
 

  num[3][2]=3;  //    3,-1       x2y + y3 - yz2
  r[3][2][0]=2; s[3][2][0]=1; t[3][2][0]=0;    keisu[3][2][0]= (1.0/4.0)*sqrt(21/(2*M_PI));
  r[3][2][1]=0; s[3][2][1]=3; t[3][2][1]=0;    keisu[3][2][1]= (1.0/4.0)*sqrt(21/(2*M_PI));
  r[3][2][2]=0; s[3][2][2]=1; t[3][2][2]=2;    keisu[3][2][2]=      -1.0*sqrt(21/(2*M_PI));

  num[3][3]=3;  //    3,0        x2z - y2z + z3
  r[3][3][0]=2; s[3][3][0]=0; t[3][3][0]=1;    keisu[3][3][0]= -(3.0/4.0)*sqrt(7/M_PI);
  r[3][3][1]=0; s[3][3][1]=2; t[3][3][1]=1;    keisu[3][3][1]= -(3.0/4.0)*sqrt(7/M_PI);
  r[3][3][2]=0; s[3][3][2]=0; t[3][3][2]=3;    keisu[3][3][2]=  (1.0/2.0)*sqrt(7/M_PI);

  num[3][4]=3;  //    3,1        x3 + xy2 -xz2
  r[3][4][0]=3; s[3][4][0]=0; t[3][4][0]=0;    keisu[3][4][0]= (1.0/4.0)*sqrt(21/(2*M_PI));
  r[3][4][1]=1; s[3][4][1]=2; t[3][4][1]=0;    keisu[3][4][1]= (1.0/4.0)*sqrt(21/(2*M_PI));
  r[3][4][2]=1; s[3][4][2]=0; t[3][4][2]=2;    keisu[3][4][2]=      -1.0*sqrt(21/(2*M_PI));
 

  num[3][5]=2;  //    3,2        zx^2 - zy^2
  r[3][5][0]=2; s[3][5][0]=0; t[3][5][0]=1;    keisu[3][5][0]= (1.0/4.0)*sqrt(105/M_PI);
  r[3][5][1]=0; s[3][5][1]=2; t[3][5][1]=1;    keisu[3][5][1]=-(1.0/4.0)*sqrt(105/M_PI);

  num[3][6]=2;  //    3,3        x^3 - 3xy^2 
  r[3][6][0]=3; s[3][6][0]=0; t[3][6][0]=0;    keisu[3][6][0]= -(1.0/4.0)*sqrt(35/(2*M_PI));
  r[3][6][1]=1; s[3][6][1]=2; t[3][6][1]=0;    keisu[3][6][1]=  (3.0/4.0)*sqrt(35/(2*M_PI));
//
//
  num[4][0]=2;  //    4,-4       xy^3 - x^3y
  r[4][0][0]=3; s[4][0][0]=1; t[4][0][0]=0;    keisu[4][0][0]=-(3.0/4.0)*sqrt(35/M_PI);
  r[4][0][1]=1; s[4][0][1]=3; t[4][0][1]=0;    keisu[4][0][1]= (3.0/4.0)*sqrt(35/M_PI);

  num[4][1]=2;  //    4,-3    - x2yz  + y3z
  r[4][1][0]=2; s[4][1][0]=1; t[4][1][0]=1;    keisu[4][1][0]=-(9.0/4.0)*sqrt(35/(2*M_PI));
  r[4][1][1]=0; s[4][1][1]=3; t[4][1][1]=1;    keisu[4][1][1]= (3.0/4.0)*sqrt(35/(2*M_PI));

  num[4][2]=3;  //    4,-2    x3y + xy3 - xyz2 
  r[4][2][0]=3; s[4][2][0]=1; t[4][2][0]=0;    keisu[4][2][0]= (3.0/4.0)*sqrt(5/M_PI);
  r[4][2][1]=1; s[4][2][1]=3; t[4][2][1]=0;    keisu[4][2][1]= (3.0/4.0)*sqrt(5/M_PI);
  r[4][2][2]=1; s[4][2][2]=1; t[4][2][2]=2;    keisu[4][2][2]=-(9.0/2.0)*sqrt(5/M_PI);

  num[4][3]=3;  //    4,-1     x2yz + y3z - yz3
  r[4][3][0]=2; s[4][3][0]=1; t[4][3][0]=1;    keisu[4][3][0]= (9.0/4.0)*sqrt(5/(2*M_PI));
  r[4][3][1]=0; s[4][3][1]=3; t[4][3][1]=1;    keisu[4][3][1]= (9.0/4.0)*sqrt(5/(2*M_PI));
  r[4][3][2]=0; s[4][3][2]=1; t[4][3][2]=3;    keisu[4][3][2]= -3.0*sqrt(5/(2*M_PI));

  num[4][4]=6;  //    4,4      x4 + x2y2 + y4 - x2z2 - y2z2 + z4
  r[4][4][0]=4; s[4][4][0]=0; t[4][4][0]=0;    keisu[4][4][0]=(9.0/16.0)*sqrt(1/M_PI);
  r[4][4][1]=2; s[4][4][1]=2; t[4][4][1]=0;    keisu[4][4][1]= (9.0/8.0)*sqrt(1/M_PI);
  r[4][4][2]=0; s[4][4][2]=4; t[4][4][2]=0;    keisu[4][4][2]=(9.0/16.0)*sqrt(1/M_PI);
  r[4][4][3]=2; s[4][4][3]=0; t[4][4][3]=2;    keisu[4][4][3]=-(9.0/2.0)*sqrt(1/M_PI);
  r[4][4][4]=0; s[4][4][4]=2; t[4][4][4]=2;    keisu[4][4][4]=-(9.0/2.0)*sqrt(1/M_PI);
  r[4][4][5]=0; s[4][4][5]=0; t[4][4][5]=4;    keisu[4][4][5]= (3.0/2.0)*sqrt(1/M_PI);

  num[4][5]=3;  //    4,1      x3z + xy2z - xz3
  r[4][5][0]=3; s[4][5][0]=0; t[4][5][0]=1;    keisu[4][5][0]=  (9.0/4.0)*sqrt(5/(2*M_PI));
  r[4][5][1]=1; s[4][5][1]=2; t[4][5][1]=1;    keisu[4][5][1]=  (9.0/4.0)*sqrt(5/(2*M_PI));
  r[4][5][2]=1; s[4][5][2]=0; t[4][5][2]=3;    keisu[4][5][2]=       -3.0*sqrt(5/(2*M_PI));

  num[4][6]=4;  //    4,2      x4 + y4 L x2z2 - y2z2 
  r[4][6][0]=4; s[4][6][0]=0; t[4][6][0]=0;    keisu[4][6][0]= -(3.0/8.0)*sqrt(5/M_PI);
  r[4][6][1]=0; s[4][6][1]=4; t[4][6][1]=0;    keisu[4][6][1]=  (3.0/8.0)*sqrt(5/M_PI);
  r[4][6][2]=2; s[4][6][2]=0; t[4][6][2]=2;    keisu[4][6][2]=  (9.0/4.0)*sqrt(5/M_PI);
  r[4][6][3]=0; s[4][6][3]=2; t[4][6][3]=2;    keisu[4][6][3]= -(9.0/4.0)*sqrt(5/M_PI);

  num[4][7]=2;  //    4,3    - x3z + xy2z 
  r[4][7][0]=3; s[4][7][0]=0; t[4][7][0]=1;    keisu[4][7][0]= -(3.0/4.0)*sqrt(35/(2*M_PI));
  r[4][7][1]=1; s[4][7][1]=2; t[4][7][1]=1;    keisu[4][7][1]=  (9.0/4.0)*sqrt(35/(2*M_PI));
 

  num[4][8]=3;  //    4,4    x4 - x2y2 + y4
  r[4][8][0]=4; s[4][8][0]=0; t[4][8][0]=0;    keisu[4][8][0]= (3.0/16.0)*sqrt(35/M_PI);
  r[4][8][1]=2; s[4][8][1]=2; t[4][8][1]=0;    keisu[4][8][1]= -(9.0/8.0)*sqrt(35/M_PI);
  r[4][8][2]=0; s[4][8][2]=4; t[4][8][2]=0;    keisu[4][8][2]= (3.0/16.0)*sqrt(35/M_PI);
//
//
  num[5][0]=3;  //    5,-5   
  r[5][0][0]=4; s[5][0][0]=1; t[5][0][0]=0;    keisu[5][0][0]=-(15.0/16.0)*sqrt(77/(2*M_PI));
  r[5][0][1]=2; s[5][0][1]=3; t[5][0][1]=0;    keisu[5][0][1]=  (15.0/8.0)*sqrt(77/(2*M_PI));
  r[5][0][2]=0; s[5][0][2]=5; t[5][0][2]=0;    keisu[5][0][2]= -(3.0/16.0)*sqrt(77/(2*M_PI));

  num[5][1]=2;  //    5,-4
  r[5][1][0]=3; s[5][1][0]=1; t[5][1][0]=1;    keisu[5][1][0]=-(3.0/4.0)*sqrt(385/M_PI);
  r[5][1][1]=1; s[5][1][1]=3; t[5][1][1]=1;    keisu[5][1][1]= (3.0/4.0)*sqrt(385/M_PI);

  num[5][2]=5;  //    5,-3
  r[5][2][0]=4; s[5][2][0]=1; t[5][2][0]=0;    keisu[5][2][0]= (3.0/16.0)*sqrt(385/(2*M_PI));
  r[5][2][1]=2; s[5][2][1]=3; t[5][2][1]=0;    keisu[5][2][1]=  (1.0/8.0)*sqrt(385/(2*M_PI));
  r[5][2][2]=0; s[5][2][2]=5; t[5][2][2]=0;    keisu[5][2][2]=-(1.0/16.0)*sqrt(385/(2*M_PI));
  r[5][2][3]=2; s[5][2][3]=1; t[5][2][3]=2;    keisu[5][2][3]= -(3.0/2.0)*sqrt(385/(2*M_PI));
  r[5][2][4]=0; s[5][2][4]=3; t[5][2][4]=2;    keisu[5][2][4]=  (1.0/2.0)*sqrt(385/(2*M_PI));

  num[5][3]=3;  //    5,-2
  r[5][3][0]=3; s[5][3][0]=1; t[5][3][0]=1;    keisu[5][3][0]= (1.0/4.0)*sqrt(1155/M_PI);
  r[5][3][1]=1; s[5][3][1]=3; t[5][3][1]=1;    keisu[5][3][1]= (1.0/4.0)*sqrt(1155/M_PI);
  r[5][3][2]=1; s[5][3][2]=1; t[5][3][2]=3;    keisu[5][3][2]=-(1.0/2.0)*sqrt(1155/M_PI);

  num[5][4]=6;  //    5,-1
  r[5][4][0]=4; s[5][4][0]=1; t[5][4][0]=0;    keisu[5][4][0]=-(1.0/16.0)*sqrt(165/M_PI);
  r[5][4][1]=2; s[5][4][1]=3; t[5][4][1]=0;    keisu[5][4][1]= -(1.0/8.0)*sqrt(165/M_PI);
  r[5][4][2]=0; s[5][4][2]=5; t[5][4][2]=0;    keisu[5][4][2]=-(1.0/16.0)*sqrt(165/M_PI);
  r[5][4][3]=2; s[5][4][3]=1; t[5][4][3]=2;    keisu[5][4][3]=  (3.0/4.0)*sqrt(165/M_PI);
  r[5][4][4]=0; s[5][4][4]=3; t[5][4][4]=2;    keisu[5][4][4]=  (3.0/4.0)*sqrt(165/M_PI);
  r[5][4][5]=0; s[5][4][5]=1; t[5][4][5]=4;    keisu[5][4][5]= -(1.0/2.0)*sqrt(165/M_PI);
    
  num[5][5]=6;  //    5,0
  r[5][5][0]=4; s[5][5][0]=0; t[5][5][0]=1;    keisu[5][5][0]= (15.0/16.0)*sqrt(11/M_PI);
  r[5][5][1]=2; s[5][5][1]=2; t[5][5][1]=1;    keisu[5][5][1]=  (15.0/8.0)*sqrt(11/M_PI);
  r[5][5][2]=0; s[5][5][2]=4; t[5][5][2]=1;    keisu[5][5][2]= (15.0/16.0)*sqrt(11/M_PI);
  r[5][5][3]=2; s[5][5][3]=0; t[5][5][3]=3;    keisu[5][5][3]=  -(5.0/2.0)*sqrt(11/M_PI);
  r[5][5][4]=0; s[5][5][4]=2; t[5][5][4]=3;    keisu[5][5][4]=  -(5.0/2.0)*sqrt(11/M_PI);
  r[5][5][5]=0; s[5][5][5]=0; t[5][5][5]=5;    keisu[5][5][5]=   (1.0/2.0)*sqrt(11/M_PI);

  num[5][6]=6;  //    5,1
  r[5][6][0]=5; s[5][6][0]=0; t[5][6][0]=0;    keisu[5][6][0]=-(1.0/16.0)*sqrt(165/M_PI);
  r[5][6][1]=3; s[5][6][1]=2; t[5][6][1]=0;    keisu[5][6][1]= -(1.0/8.0)*sqrt(165/M_PI);
  r[5][6][2]=1; s[5][6][2]=4; t[5][6][2]=0;    keisu[5][6][2]=-(1.0/16.0)*sqrt(165/M_PI);
  r[5][6][3]=3; s[5][6][3]=0; t[5][6][3]=2;    keisu[5][6][3]=  (3.0/4.0)*sqrt(165/M_PI);
  r[5][6][4]=1; s[5][6][4]=2; t[5][6][4]=2;    keisu[5][6][4]=  (3.0/4.0)*sqrt(165/M_PI);
  r[5][6][5]=1; s[5][6][5]=0; t[5][6][5]=4;    keisu[5][6][5]= -(1.0/2.0)*sqrt(165/M_PI);

  num[5][7]=4;  //    5,2
  r[5][7][0]=4; s[5][7][0]=0; t[5][7][0]=1;    keisu[5][7][0]=-(1.0/8.0)*sqrt(1155/M_PI);
  r[5][7][1]=0; s[5][7][1]=4; t[5][7][1]=1;    keisu[5][7][1]= (1.0/8.0)*sqrt(1155/M_PI);
  r[5][7][2]=2; s[5][7][2]=0; t[5][7][2]=3;    keisu[5][7][2]= (1.0/4.0)*sqrt(1155/M_PI);
  r[5][7][3]=0; s[5][7][3]=2; t[5][7][3]=3;    keisu[5][7][3]=-(1.0/4.0)*sqrt(1155/M_PI);

  num[5][8]=5;  //    5,3
  r[5][8][0]=5; s[5][8][0]=0; t[5][8][0]=0;    keisu[5][8][0]= (1.0/16.0)*sqrt(385/(2*M_PI));
  r[5][8][1]=3; s[5][8][1]=2; t[5][8][1]=0;    keisu[5][8][1]= -(1.0/8.0)*sqrt(385/(2*M_PI));
  r[5][8][2]=1; s[5][8][2]=4; t[5][8][2]=0;    keisu[5][8][2]=-(3.0/16.0)*sqrt(385/(2*M_PI));
  r[5][8][3]=3; s[5][8][3]=0; t[5][8][3]=2;    keisu[5][8][3]= -(1.0/2.0)*sqrt(385/(2*M_PI));
  r[5][8][4]=1; s[5][8][4]=2; t[5][8][4]=2;    keisu[5][8][4]=  (3.0/2.0)*sqrt(385/(2*M_PI));

  num[5][9]=3;  //    5,4
  r[5][9][0]=4; s[5][9][0]=0; t[5][9][0]=1;    keisu[5][9][0]=(3.0/16.0)*sqrt(385/M_PI);
  r[5][9][1]=2; s[5][9][1]=2; t[5][9][1]=1;    keisu[5][9][1]=-(9.0/8.0)*sqrt(385/M_PI);
  r[5][9][2]=0; s[5][9][2]=4; t[5][9][2]=1;    keisu[5][9][2]=(3.0/16.0)*sqrt(385/M_PI);
 

  num[5][10]=3; //    5,5
  r[5][10][0]=5; s[5][10][0]=0; t[5][10][0]=0;    keisu[5][10][0]= -(3.0/16.0)*sqrt(77/(2*M_PI));
  r[5][10][1]=3; s[5][10][1]=2; t[5][10][1]=0;    keisu[5][10][1]=  (15.0/8.0)*sqrt(77/(2*M_PI));
  r[5][10][2]=1; s[5][10][2]=4; t[5][10][2]=0;    keisu[5][10][2]=-(15.0/16.0)*sqrt(77/(2*M_PI));
//
//
  num[6][0]=3;  //    6,-6
  r[6][0][0]=5; s[6][0][0]=1; t[6][0][0]=0;    keisu[6][0][0]=-(3.0/16.0)*sqrt(3003/(2*M_PI));
  r[6][0][1]=3; s[6][0][1]=3; t[6][0][1]=0;    keisu[6][0][1]=  (5.0/8.0)*sqrt(3003/(2*M_PI));
  r[6][0][2]=1; s[6][0][2]=5; t[6][0][2]=0;    keisu[6][0][2]=-(3.0/16.0)*sqrt(3003/(2*M_PI));
 
  num[6][1]=3;  //    6,-5
  r[6][1][0]=4; s[6][1][0]=1; t[6][1][0]=1;    keisu[6][1][0]=-(15.0/16.0)*sqrt(1001/(2*M_PI));
  r[6][1][1]=2; s[6][1][1]=3; t[6][1][1]=1;    keisu[6][1][1]=  (15.0/8.0)*sqrt(1001/(2*M_PI));
  r[6][1][2]=0; s[6][1][2]=5; t[6][1][2]=1;    keisu[6][1][2]= -(3.0/16.0)*sqrt(1001/(2*M_PI));

  num[6][2]=4;  //    6,-4
  r[6][2][0]=5; s[6][2][0]=1; t[6][2][0]=0;    keisu[6][2][0]=  (3.0/8.0)*sqrt(91/M_PI);
  r[6][2][1]=1; s[6][2][1]=5; t[6][2][1]=0;    keisu[6][2][1]= -(3.0/8.0)*sqrt(91/M_PI);
  r[6][2][2]=3; s[6][2][2]=1; t[6][2][2]=2;    keisu[6][2][2]=-(15.0/4.0)*sqrt(91/M_PI);
  r[6][2][3]=1; s[6][2][3]=3; t[6][2][3]=2;    keisu[6][2][3]= (15.0/4.0)*sqrt(91/M_PI);
   
  num[6][3]=5;  //    6,-3
  r[6][3][0]=4; s[6][3][0]=1; t[6][3][0]=1;    keisu[6][3][0]= (9.0/16.0)*sqrt(1365/(2*M_PI));
  r[6][3][1]=2; s[6][3][1]=3; t[6][3][1]=1;    keisu[6][3][1]=  (3.0/8.0)*sqrt(1365/(2*M_PI));
  r[6][3][2]=0; s[6][3][2]=5; t[6][3][2]=1;    keisu[6][3][2]=-(3.0/16.0)*sqrt(1365/(2*M_PI));
  r[6][3][3]=2; s[6][3][3]=1; t[6][3][3]=3;    keisu[6][3][3]= -(3.0/2.0)*sqrt(1365/(2*M_PI));
  r[6][3][4]=0; s[6][3][4]=3; t[6][3][4]=3;    keisu[6][3][4]=  (1.0/2.0)*sqrt(1365/(2*M_PI));

  num[6][4]=6;  //    6,-2
  r[6][4][0]=5; s[6][4][0]=1; t[6][4][0]=0;    keisu[6][4][0]=-(1.0/16.0)*sqrt(1365/(2*M_PI));
  r[6][4][1]=3; s[6][4][1]=3; t[6][4][1]=0;    keisu[6][4][1]= -(1.0/8.0)*sqrt(1365/(2*M_PI));
  r[6][4][2]=1; s[6][4][2]=5; t[6][4][2]=0;    keisu[6][4][2]=-(1.0/16.0)*sqrt(1365/(2*M_PI));
  r[6][4][3]=3; s[6][4][3]=1; t[6][4][3]=2;    keisu[6][4][3]=            sqrt(1365/(2*M_PI));
  r[6][4][4]=1; s[6][4][4]=3; t[6][4][4]=2;    keisu[6][4][4]=            sqrt(1365/(2*M_PI));
  r[6][4][5]=1; s[6][4][5]=1; t[6][4][5]=4;    keisu[6][4][5]=       -1.0*sqrt(1365/(2*M_PI));

  num[6][5]=6;  //    6,-1
  r[6][5][0]=4; s[6][5][0]=1; t[6][5][0]=1;    keisu[6][5][0]=-(5.0/16.0)*sqrt(273/M_PI);
  r[6][5][1]=2; s[6][5][1]=3; t[6][5][1]=1;    keisu[6][5][1]= -(5.0/8.0)*sqrt(273/M_PI);
  r[6][5][2]=0; s[6][5][2]=5; t[6][5][2]=1;    keisu[6][5][2]=-(5.0/16.0)*sqrt(273/M_PI);
  r[6][5][3]=2; s[6][5][3]=1; t[6][5][3]=3;    keisu[6][5][3]=  (5.0/4.0)*sqrt(273/M_PI);
  r[6][5][4]=0; s[6][5][4]=3; t[6][5][4]=3;    keisu[6][5][4]=  (5.0/4.0)*sqrt(273/M_PI);
  r[6][5][5]=0; s[6][5][5]=1; t[6][5][5]=5;    keisu[6][5][5]= -(1.0/2.0)*sqrt(273/M_PI);

  num[6][6]=10;  //   6,0
  r[6][6][0]=6; s[6][6][0]=0; t[6][6][0]=0;    keisu[6][6][0]= -(5.0/32.0)*sqrt(13/M_PI);
  r[6][6][1]=4; s[6][6][1]=2; t[6][6][1]=0;    keisu[6][6][1]=-(15.0/32.0)*sqrt(13/M_PI);
  r[6][6][2]=2; s[6][6][2]=4; t[6][6][2]=0;    keisu[6][6][2]=-(15.0/32.0)*sqrt(13/M_PI);
  r[6][6][3]=0; s[6][6][3]=6; t[6][6][3]=0;    keisu[6][6][3]= -(5.0/32.0)*sqrt(13/M_PI);
  r[6][6][4]=4; s[6][6][4]=0; t[6][6][4]=2;    keisu[6][6][4]= (45.0/16.0)*sqrt(13/M_PI);
  r[6][6][5]=2; s[6][6][5]=2; t[6][6][5]=2;    keisu[6][6][5]=  (45.0/8.0)*sqrt(13/M_PI);
  r[6][6][6]=0; s[6][6][6]=4; t[6][6][6]=2;    keisu[6][6][6]= (45.0/16.0)*sqrt(13/M_PI);
  r[6][6][7]=2; s[6][6][7]=0; t[6][6][7]=4;    keisu[6][6][7]= -(15.0/4.0)*sqrt(13/M_PI);
  r[6][6][8]=0; s[6][6][8]=2; t[6][6][8]=4;    keisu[6][6][8]= -(15.0/4.0)*sqrt(13/M_PI);
  r[6][6][9]=0; s[6][6][9]=0; t[6][6][9]=6;    keisu[6][6][9]=   (1.0/2.0)*sqrt(13/M_PI);

  num[6][7]=6;   //   6,1
  r[6][7][0]=5; s[6][7][0]=0; t[6][7][0]=1;    keisu[6][7][0]=-(5.0/16.0)*sqrt(273/M_PI);
  r[6][7][1]=3; s[6][7][1]=2; t[6][7][1]=1;    keisu[6][7][1]= -(5.0/8.0)*sqrt(273/M_PI);
  r[6][7][2]=1; s[6][7][2]=4; t[6][7][2]=1;    keisu[6][7][2]=-(5.0/16.0)*sqrt(273/M_PI);
  r[6][7][3]=3; s[6][7][3]=0; t[6][7][3]=3;    keisu[6][7][3]=  (5.0/4.0)*sqrt(273/M_PI);
  r[6][7][4]=1; s[6][7][4]=2; t[6][7][4]=3;    keisu[6][7][4]=  (5.0/4.0)*sqrt(273/M_PI);
  r[6][7][5]=1; s[6][7][5]=0; t[6][7][5]=5;    keisu[6][7][5]= -(1.0/2.0)*sqrt(273/M_PI);
 
  num[6][8]=8;   //   6,2
  r[6][8][0]=6; s[6][8][0]=0; t[6][8][0]=0;    keisu[6][8][0]= (1.0/32.0)*sqrt(1365/(2*M_PI));
  r[6][8][1]=4; s[6][8][1]=2; t[6][8][1]=0;    keisu[6][8][1]= (1.0/32.0)*sqrt(1365/(2*M_PI));
  r[6][8][2]=2; s[6][8][2]=4; t[6][8][2]=0;    keisu[6][8][2]=-(1.0/32.0)*sqrt(1365/(2*M_PI));
  r[6][8][3]=0; s[6][8][3]=6; t[6][8][3]=0;    keisu[6][8][3]=-(1.0/32.0)*sqrt(1365/(2*M_PI));
  r[6][8][4]=4; s[6][8][4]=0; t[6][8][4]=2;    keisu[6][8][4]= -(1.0/2.0)*sqrt(1365/(2*M_PI));
  r[6][8][5]=0; s[6][8][5]=4; t[6][8][5]=2;    keisu[6][8][5]=  (1.0/2.0)*sqrt(1365/(2*M_PI));
  r[6][8][6]=2; s[6][8][6]=0; t[6][8][6]=4;    keisu[6][8][6]=  (1.0/2.0)*sqrt(1365/(2*M_PI));
  r[6][8][7]=0; s[6][8][7]=2; t[6][8][7]=4;    keisu[6][8][7]= -(1.0/2.0)*sqrt(1365/(2*M_PI));

  num[6][9]=5;   //   6,3
  r[6][9][0]=5; s[6][9][0]=0; t[6][9][0]=1;    keisu[6][9][0]= (3.0/16.0)*sqrt(1365/(2*M_PI));
  r[6][9][1]=3; s[6][9][1]=2; t[6][9][1]=1;    keisu[6][9][1]= -(3.0/8.0)*sqrt(1365/(2*M_PI));
  r[6][9][2]=1; s[6][9][2]=4; t[6][9][2]=1;    keisu[6][9][2]=-(9.0/16.0)*sqrt(1365/(2*M_PI));
  r[6][9][3]=3; s[6][9][3]=0; t[6][9][3]=3;    keisu[6][9][3]= -(1.0/2.0)*sqrt(1365/(2*M_PI));
  r[6][9][4]=1; s[6][9][4]=2; t[6][9][4]=3;    keisu[6][9][4]=  (3.0/2.0)*sqrt(1365/(2*M_PI));
 

  num[6][10]=7;  //   6,4
  r[6][10][0]=6; s[6][10][0]=0; t[6][10][0]=0;    keisu[6][10][0]= -(3.0/32.0)*sqrt(91/M_PI);
  r[6][10][1]=4; s[6][10][1]=2; t[6][10][1]=0;    keisu[6][10][1]= (15.0/32.0)*sqrt(91/M_PI);
  r[6][10][2]=2; s[6][10][2]=4; t[6][10][2]=0;    keisu[6][10][2]= (15.0/32.0)*sqrt(91/M_PI);
  r[6][10][3]=0; s[6][10][3]=6; t[6][10][3]=0;    keisu[6][10][3]= -(3.0/32.0)*sqrt(91/M_PI);
  r[6][10][4]=4; s[6][10][4]=0; t[6][10][4]=2;    keisu[6][10][4]= (15.0/16.0)*sqrt(91/M_PI);
  r[6][10][5]=2; s[6][10][5]=2; t[6][10][5]=2;    keisu[6][10][5]= -(45.0/8.0)*sqrt(91/M_PI);
  r[6][10][6]=0; s[6][10][6]=4; t[6][10][6]=2;    keisu[6][10][6]= (15.0/16.0)*sqrt(91/M_PI);
 

  num[6][11]=3;  //   6,5
  r[6][11][0]=5; s[6][11][0]=0; t[6][11][0]=1;    keisu[6][11][0]= -(3.0/16.0)*sqrt(1001/(2*M_PI));
  r[6][11][1]=3; s[6][11][1]=2; t[6][11][1]=1;    keisu[6][11][1]=  (15.0/8.0)*sqrt(1001/(2*M_PI));
  r[6][11][2]=1; s[6][11][2]=4; t[6][11][2]=1;    keisu[6][11][2]=-(15.0/16.0)*sqrt(1001/(2*M_PI));
 

  num[6][12]=4;  //   6,6
  r[6][12][0]=6; s[6][12][0]=0; t[6][12][0]=0;    keisu[6][12][0]=  (1.0/32.0)*sqrt(3003/(2*M_PI));
  r[6][12][1]=4; s[6][12][1]=2; t[6][12][1]=0;    keisu[6][12][1]=-(15.0/32.0)*sqrt(3003/(2*M_PI));
  r[6][12][2]=2; s[6][12][2]=4; t[6][12][2]=0;    keisu[6][12][2]= (15.0/32.0)*sqrt(3003/(2*M_PI));
  r[6][12][3]=0; s[6][12][3]=6; t[6][12][3]=0;    keisu[6][12][3]= -(1.0/32.0)*sqrt(3003/(2*M_PI));
 
//
//
}

template <typename Integ1e>
double ECP_integral<Integ1e>::cal_I(double in_g,const std::vector<int> &in_n){
  int aaa[12];
  aaa[0] =1;  aaa[1] =1;  aaa[2] =1;  aaa[3] =2;  aaa[4] =3; aaa[5] =8;
  aaa[6] =15; aaa[7] =48; aaa[8] =105;aaa[9] =384;aaa[10] =945;
  return pow((2*in_g/M_PI),3.0/4.0)*pow(4*in_g,(in_n[0]+in_n[1]+in_n[2])/2.0)/
             sqrt((double)aaa[2*in_n[0]]*aaa[2*in_n[1]]*aaa[2*in_n[2]]);
}

template <typename Integ1e>
void ECP_integral<Integ1e>::set_init(){
  //
  alpha=0.0;
  CA[0]=CA[1]=CA[2]=0.0;
  CB[0]=CB[1]=CB[2]=0.0;
  k_xyz[0]=k_xyz[1]=k_xyz[2]=0.0;
  k_xyz_A[0]=k_xyz_A[1]=k_xyz_A[2];
  k_xyz_B[0]=k_xyz_B[1]=k_xyz_B[2];
  k_length=k_length_A=k_length_B=0.0;
  n_dash=0;
  Dabc=0.0;
  a_value=0.0;
  rc_div_sqrt_alpha=0;
  v_y_k_xyz[0][0]=0.0; 
  v_y_k_xyz_A[0][0]=0.0; 
  v_y_k_xyz_B[0][0]=0.0;
  check_type1_radial[0][0]=0; 
  Omega_type1_radial[0][0]=0; 
  check_type2_radial[0][0][0]=0; 
  Omega_type2_radial[0][0][0]=0; 
  //

  n_kaizyou[0]=1.0;   n_kaizyou[1]=1.0;
  nnn[0]=1.0;         nnn[1]=1.0;
  nnn_m1[0]=1.0;         nnn_m1[1]=1.0;     nnn_m1[2]=1.0; 
  for(int i=2;i<301;i++){
    n_kaizyou[i]=i*n_kaizyou[i-1];
    nnn[i]=i*nnn[i-2];
    nnn_m1[i]=nnn[i-1];
  }

  for(int i=0;i<15;i++){
    for(int j=0;j<15;j++){
      for(int k=0;k<15;k++){
        if((i%2)==0 && (j%2)==0 && (k%2)==0){
          v_xyz_integral_over_omega[i][j][k]=4*M_PI*((nnn_m1[i]*nnn_m1[j]*nnn_m1[k])/nnn[i+j+k+1]);
        }else{
          v_xyz_integral_over_omega[i][j][k]=0.0;
        }
      }
    }
  }

  C_na[0][0]=1.0; 
  C_na[1][0]=1.0;
  C_na[1][1]=1.0;
  C_na[2][0]=1.0; C_na[2][1]=2.0; C_na[2][2]=1.0;
  C_na[3][0]=1.0; C_na[3][1]=3.0; C_na[3][2]=3.0; C_na[3][3]=1.0;
  C_na[4][0]=1.0; C_na[4][1]=4.0; C_na[4][2]=6.0; C_na[4][3]=4.0; C_na[4][4]=1.0;


  

  int num_rsh_rst,num_rsh_uvw;
  int r,s,t,u,v,w;
  double keisu_rst;
  double keisu_uvw;
  double tmp_wa;


  for(int a=0;a<=6;a++){
    for(int b=0;b<=6;b++){
      for(int c=0;c<=6;c++){
        for(int lamda=0;lamda<=6;lamda++){
          for(int myu=-lamda;myu<=lamda;myu++){
            num_rsh_rst=rsh.get_num(lamda,myu);
            tmp_wa=0.0;
            for(int i=0;i<num_rsh_rst;i++){
              r=rsh.get_r(lamda,myu,i);
              s=rsh.get_s(lamda,myu,i);
              t=rsh.get_t(lamda,myu,i);
              keisu_rst=rsh.get_keisu(lamda,myu,i);
              tmp_wa+=keisu_rst*v_xyz_integral_over_omega[a+r][b+s][c+t];
            }
            v_y_xyz_integral_over_omega[lamda][lamda+myu][a][b][c]=tmp_wa;
          }
        }
      }
    }
  }

  for(int a=0;a<=3;a++){
    for(int b=0;b<=3;b++){
      for(int c=0;c<=3;c++){
        for(int lamda=0;lamda<=6;lamda++){
          for(int myu=-lamda;myu<=lamda;myu++){
            num_rsh_rst=rsh.get_num(lamda,myu);  
            for(int l=0;l<=3;l++){
              for(int m=-l;m<=l;m++){
                num_rsh_uvw=rsh.get_num(l,m);
                tmp_wa=0.0;
                for(int i=0;i<num_rsh_rst;i++){
                  r=rsh.get_r(lamda,myu,i);
                  s=rsh.get_s(lamda,myu,i);
                  t=rsh.get_t(lamda,myu,i);
                  keisu_rst=rsh.get_keisu(lamda,myu,i);
                  for(int j=0;j<num_rsh_uvw;j++){
                    u=rsh.get_r(l,m,j);
                    v=rsh.get_s(l,m,j);
                    w=rsh.get_t(l,m,j);
                    keisu_uvw=rsh.get_keisu(l,m,j);
                    tmp_wa+=keisu_rst*keisu_uvw*v_xyz_integral_over_omega[a+r+u][b+s+v][c+t+w];
                      
                  }
                }
                v_yy_xyz_integral_over_omega[lamda][lamda+myu][l][l+m][a][b][c]=tmp_wa;
              }
            }
          }
        }
      }
    }
  }

  for(int a=0;a<=3;a++){
    for(int b=0;b<=3;b++){
      for(int c=0;c<=3;c++){
        for(int l=0;l<=3;l++){
          for(int m=-l;m<=l;m++){
            v_xyz_Ylm_integral_over_omega[a][b][c][l][l+m]
              =cal_xyz_Ylm_integral_over_omega(a,b,c,l,m);
          }
        }
      }
    }
  }

}


//
//   type 1
//  

template <typename Integ1e>
double ECP_integral<Integ1e>::cal_xyz_integral_over_omega(int i,int j,int k){
  double ret;
  if( (i%2)==0 && (j%2)==0 && (k%2)==0){
    ret=4*M_PI*((nnn_m1[i]*nnn_m1[j]*nnn_m1[k])/nnn[i+j+k+1]);
  }else{
    ret=0.0;
  }
  return ret;
}



template <typename Integ1e>
double ECP_integral<Integ1e>::cal_ECP_type1_ANGULAR_integral(int I,int J,int K,int lamda){
  int myu;
  double tmp1,tmp2;
  double ret=0.0;
  int r,s,t;
  int num_rsh;
  double keisu;
//  double k_length=sqrt(k_xyz[0]*k_xyz[0]+k_xyz[1]*k_xyz[1]+k_xyz[2]*k_xyz[2]);
  for(myu=-lamda;myu<=lamda;myu++){
    tmp1=tmp2=0.0;
    num_rsh=rsh.get_num(lamda,myu);
    for(int i=0;i<num_rsh;i++){
      r=rsh.get_r(lamda,myu,i);
      s=rsh.get_s(lamda,myu,i);
      t=rsh.get_t(lamda,myu,i);
      keisu=rsh.get_keisu(lamda,myu,i);

      tmp1+=keisu*pow(k_xyz[0]/k_length,r)*pow(k_xyz[1]/k_length,s)*pow(k_xyz[2]/k_length,t);
 //     tmp2+=keisu*cal_xyz_integral_over_omega(I+r,J+s,K+t);
      tmp2+=keisu*v_xyz_integral_over_omega[I+r][J+s][K+t];
    }
    ret+=tmp1*tmp2;
  }
  return ret;
}

template <typename Integ1e>
double ECP_integral<Integ1e>::cal_ECP_type1_ANGULAR_integral2(int I,int J,int K,int lamda){
  int myu;
  double ret=0.0;
  for(myu=-lamda;myu<=lamda;myu++){
    ret+=v_y_k_xyz[lamda][lamda+myu]*v_y_xyz_integral_over_omega[lamda][lamda+myu][I][J][K];
  }
  return ret;
}



template <typename Integ1e>
double ECP_integral<Integ1e>::hypergeometric_function(double a,double c,double z){
  const int N_for_hyper=100;
  double a_div_c_k[N_for_hyper];
  double z_div_k_k[N_for_hyper];
  a_div_c_k[0]=1.0;
  z_div_k_k[0]=1.0;
  a_div_c_k[1]=a/c;
  z_div_k_k[1]=z;
  double ret=0.0;
  double pre_ret;
  ret+=a_div_c_k[0]*z_div_k_k[0];
  ret+=a_div_c_k[1]*z_div_k_k[1];
  pre_ret=ret;
  for(int i=2;i<N_for_hyper;i++){ 
    a_div_c_k[i]=a_div_c_k[i-1]*((double)(a+i-1)/((double)(c+i-1)));
    z_div_k_k[i]=z_div_k_k[i-1]*(z/(double)(1+i-1));
    ret+=a_div_c_k[i]*z_div_k_k[i];
    if(fabs(pre_ret-ret)<1.0e-15) return ret;
    pre_ret=ret;
  }
  return ret;
}


template <typename Integ1e>
double ECP_integral<Integ1e>::cal_ECP_type1_RADIAL_integral(double in_k_length,double alpha,int n,int l){
  double R;

  if((n+l)%2==0){
    R=(nnn_m1[n+l]/nnn[2*l+1])*(pow(2.0,l+1)/pow(2,(n+l)*0.5));
  }else{
    R=(n_kaizyou[(n+l-1)/2]/nnn[2*l+1])*(pow(2.0,l+1)/sqrt(M_PI));
  }
    
  double ret;
  ret=sqrt(M_PI)*pow(in_k_length,l)*pow(2.0,-l-2)*pow(alpha,-(l+n+1)*0.5)*R
     *hypergeometric_function((l+n+1)*0.5,l+1.5,(in_k_length*in_k_length)/(4.0*alpha));
  return ret;
}



template <typename Integ1e>
double ECP_integral<Integ1e>::cal_ECP_type1_integral_for_primitive3(int *n1,int *n2){

  if(Dabc<1.0e-15) return 0.0;

  int max_lamda;
  max_lamda=n1[0]+n1[1]+n1[2]+n2[0]+n2[1]+n2[2];

  double ret=0.0;
  double tmp_wa,tmp_value1,tmp_value2;
  for(int a=0;a<=n1[0];a++){
    for(int b=0;b<=n1[1];b++){
      for(int c=0;c<=n1[2];c++){
        for(int d=0;d<=n2[0];d++){
          for(int e=0;e<=n2[1];e++){
            for(int f=0;f<=n2[2];f++){
              if(k_length>1.0e-12){
                tmp_wa=0.0;
                for(int lamda=0;lamda<=max_lamda;lamda++){
                if((a+b+c+d+e+f-lamda)%2==0){
                  tmp_value1=cal_ECP_type1_ANGULAR_integral2(a+d,b+e,c+f,lamda);
                    if(fabs(tmp_value1)<1.0e-13){
                      tmp_wa+=0.0;
                    }else{
                      if(check_type1_radial[a+b+c+d+e+f+n_dash][lamda]==0){
                        tmp_value2=cal_ECP_type1_RADIAL_integral(k_length,alpha,a+b+c+d+e+f+n_dash,lamda);
                        Omega_type1_radial[a+b+c+d+e+f+n_dash][lamda]=tmp_value2;
                        check_type1_radial[a+b+c+d+e+f+n_dash][lamda]=1;
                      }else{
                        tmp_value2=Omega_type1_radial[a+b+c+d+e+f+n_dash][lamda];
                      } 
                      tmp_wa+=tmp_value1*tmp_value2;
                    }
                  }
                }
              }else{
                double tmp1,tmp2;
                int t_n=a+b+c+d+e+f+n_dash;
                tmp1=v_xyz_integral_over_omega[a+d][b+e][c+f]/(4.0*M_PI);
                if(t_n%2==0) tmp2=nnn_m1[t_n]*(sqrt(M_PI)/pow(2.0,t_n/2.0));
                else         tmp2=n_kaizyou[(t_n-1)/2];
                tmp2*=0.5*pow(alpha,-0.5*(t_n+1));
                tmp_wa=tmp1*tmp2;
              }
              if(fabs(tmp_wa)>1.0e-12){
                ret+=tmp_wa*C_na[n1[0]][a]*C_na[n1[1]][b]*C_na[n1[2]][c]*C_na[n2[0]][d]*C_na[n2[1]][e]*C_na[n2[2]][f]
                    *pow(CA[0],n1[0]-a)*pow(CA[1],n1[1]-b)*pow(CA[2],n1[2]-c)*pow(CB[0],n2[0]-d)*pow(CB[1],n2[1]-e)*pow(CB[2],n2[2]-f);
              }

            }
          }
        }
      }
    }
  }
  return Dabc*ret;  

}

//
//   type 2
//

template <typename Integ1e>
double ECP_integral<Integ1e>::cal_ECP_type2_ANGULAR_integral(int a,int b,int c,int lamda,int l,int m,double *in_k_xyz){

  int myu;
  double tmp1;
  double ret=0.0;
  int r,s,t;
  int num_rsh_rst;
  double keisu_rst;
  double in_k_length=sqrt(in_k_xyz[0]*in_k_xyz[0]+in_k_xyz[1]*in_k_xyz[1]+in_k_xyz[2]*in_k_xyz[2]);
  for(myu=-lamda;myu<=lamda;myu++){
    tmp1=0.0;
    num_rsh_rst=rsh.get_num(lamda,myu);
    for(int i=0;i<num_rsh_rst;i++){
      r=rsh.get_r(lamda,myu,i);
      s=rsh.get_s(lamda,myu,i);
      t=rsh.get_t(lamda,myu,i);
      keisu_rst=rsh.get_keisu(lamda,myu,i);
      tmp1+=keisu_rst*pow(in_k_xyz[0]/in_k_length,r)*pow(in_k_xyz[1]/in_k_length,s)*pow(in_k_xyz[2]/in_k_length,t);
    }
    ret+=tmp1*v_yy_xyz_integral_over_omega[lamda][lamda+myu][l][l+m][a][b][c];
  }
  return ret;

}

template <typename Integ1e>
double ECP_integral<Integ1e>::cal_ECP_type2_ANGULAR_integral_A(int a,int b,int c,int lamda,int l,int m){
  double ret=0.0;
  for(int myu=-lamda;myu<=lamda;myu++){
    ret+=v_y_k_xyz_A[lamda][lamda+myu]
        *v_yy_xyz_integral_over_omega[lamda][lamda+myu][l][l+m][a][b][c];
  }
  return ret;
}

template <typename Integ1e>
double ECP_integral<Integ1e>::cal_ECP_type2_ANGULAR_integral_B(int a,int b,int c,int lamda,int l,int m){
  double ret=0.0;
  for(int myu=-lamda;myu<=lamda;myu++){
    ret+=v_y_k_xyz_B[lamda][lamda+myu]
        *v_yy_xyz_integral_over_omega[lamda][lamda+myu][l][l+m][a][b][c];
  }
  return ret;
}

template <typename Integ1e>
double ECP_integral<Integ1e>::cal_ECP_type2_RADIAL_integral(int n,int lamda,int lamda_bar){
  double Q_2j_lamda_bar_0,Q_2j_lamda_bar_1,Q_2j_lamda_bar_2;
  Q_2j_lamda_bar_0=cal_ECP_type1_RADIAL_integral(k_length_B/sqrt(alpha),1.0,n+lamda,lamda_bar);
  Q_2j_lamda_bar_1=cal_ECP_type1_RADIAL_integral(k_length_B/sqrt(alpha),1.0,n+lamda+2,lamda_bar);
  double tmp_keisu_1=1.0;
  double tmp_keisu_2=1.0;
  double tmp=0.0;
  double pre_tmp;
  double v1=2.0*(k_length_A*k_length_A)/(2.0*alpha);
  double v2=(k_length_B*k_length_B)/(4.0*alpha);
  double v3=(n+lamda)-2.5;
  double v2_plus_v3=v2+v3;
  int tt=2*lamda+1;

  //  j=0
  tmp_keisu_1=1;
  tmp_keisu_2=nnn[tt];  
  tmp=(tmp_keisu_1/tmp_keisu_2)*Q_2j_lamda_bar_0;
  //  j=1
  tmp_keisu_1=0.5*v1;
  tmp_keisu_2=nnn[tt+2];
  tmp+=(tmp_keisu_1/tmp_keisu_2)*Q_2j_lamda_bar_1;
  //  j>=2
  pre_tmp=tmp;
  for(int J=4;J<200;J=J+2){
    Q_2j_lamda_bar_2=(v2_plus_v3+J)*Q_2j_lamda_bar_1
                     +((double)(((lamda_bar-n-lamda-J+4.0)*(lamda_bar+n+lamda+J-3.0)))/4.0)*Q_2j_lamda_bar_0;
    tmp_keisu_1*=v1/(double)J;
    tmp_keisu_2=nnn[tt+J];
    tmp+=(tmp_keisu_1/tmp_keisu_2)*Q_2j_lamda_bar_2;

    if(fabs(pre_tmp-tmp)<1.0e-13) break;
    pre_tmp=tmp;    

    Q_2j_lamda_bar_0=Q_2j_lamda_bar_1;   
    Q_2j_lamda_bar_1=Q_2j_lamda_bar_2;   
  }
  
  return (pow(k_length_A,lamda)/pow(alpha,0.5*(n+lamda+1)))*tmp;  

}

template <typename Integ1e>
double ECP_integral<Integ1e>::cal_ECP_type2_integral_for_primitive3(int *n1,int *n2,int L){
  if(Dabc<1.0e-13) return 0.0;
  int max_lamda,max_lamda_bar;
  max_lamda    =n1[0]+n1[1]+n1[2]+L;
  max_lamda_bar=n2[0]+n2[1]+n2[2]+L;

  double ret=0.0;
  double tmp_wa_1,tmp_wa_2;

  if(k_length_A>1.0e-12 && k_length_B>1.0e-12){   
  //  cout<<" in case of 1 "<<endl;  
    for(int a=0;a<=n1[0];a++){
      for(int b=0;b<=n1[1];b++){
        for(int c=0;c<=n1[2];c++){
          for(int d=0;d<=n2[0];d++){
            for(int e=0;e<=n2[1];e++){
              for(int f=0;f<=n2[2];f++){
                tmp_wa_1=0.0;
                for(int lamda=std::max(0,L-a-b-c);lamda<=max_lamda;lamda++){
                  for(int lamda_bar=std::max(0,L-d-e-f);lamda_bar<=max_lamda_bar;lamda_bar++){
                    if((a+b+c+L-lamda)%2==0 && (d+e+f+L-lamda_bar)%2==0){
                      tmp_wa_2=0.0;
                      for(int m=-L;m<=L;m++){
                        double tmp_value=cal_ECP_type2_ANGULAR_integral_A(a,b,c,lamda,L,m);
                        if(fabs(tmp_value)<1.0e-13){
                          tmp_wa_2+=0.0;
                        }else{
                          tmp_wa_2+=tmp_value
                                 *cal_ECP_type2_ANGULAR_integral_B(d,e,f,lamda_bar,L,m);
                        }
                      } 
                      if(fabs(tmp_wa_2)<1.0e-13 || 
                         (a_value*pow(rc_div_sqrt_alpha,a+b+c+d+e+f+n_dash-2))<1.0e-13){
                        tmp_wa_1+=0.0;
                      }else{
                        double tmp_value2;
                        if(check_type2_radial[a+b+c+d+e+f+n_dash][lamda][lamda_bar]==0){
                          tmp_value2=cal_ECP_type2_RADIAL_integral(a+b+c+d+e+f+n_dash,lamda,lamda_bar);
                          Omega_type2_radial[a+b+c+d+e+f+n_dash][lamda][lamda_bar]=tmp_value2;
                          check_type2_radial[a+b+c+d+e+f+n_dash][lamda][lamda_bar]=1;
                        }else{
                          tmp_value2=Omega_type2_radial[a+b+c+d+e+f+n_dash][lamda][lamda_bar];
                        } 
                        tmp_wa_1+=tmp_value2*tmp_wa_2;
                      }
                    }
                  }
                }
                if(fabs(tmp_wa_1)>1.0e-13){
                  ret+=C_na[n1[0]][a]*C_na[n1[1]][b]*C_na[n1[2]][c]*C_na[n2[0]][d]*C_na[n2[1]][e]*C_na[n2[2]][f]
                      *pow(CA[0],n1[0]-a)*pow(CA[1],n1[1]-b)*pow(CA[2],n1[2]-c)
                      *pow(CB[0],n2[0]-d)*pow(CB[1],n2[1]-e)*pow(CB[2],n2[2]-f)
                      *tmp_wa_1;
                }
              }
            }
          }
        }
      }
    }
    return 4*M_PI*Dabc*ret;
  }else if(k_length_A<1.0e-12 && k_length_B>1.0e-12){
  //  cout<<" in case of 2 "<<endl;  
    for(int d=0;d<=n2[0];d++){
      for(int e=0;e<=n2[1];e++){
        for(int f=0;f<=n2[2];f++){
          tmp_wa_1=0.0;
          for(int lamda_bar=0;lamda_bar<=max_lamda_bar;lamda_bar++){
            if((d+e+f+L-lamda_bar)%2==0){
              tmp_wa_2=0.0;
              for(int m=-L;m<=L;m++){
                tmp_wa_2+=cal_ECP_type2_ANGULAR_integral_B(d,e,f,lamda_bar,L,m)
                         *v_xyz_Ylm_integral_over_omega[n1[0]][n1[1]][n1[2]][L][L+m];
              }
              if(fabs(tmp_wa_2)<1.0e-13){
                tmp_wa_1+=0.0;
              }else{
                tmp_wa_1+=cal_ECP_type1_RADIAL_integral(k_length_B,alpha,
                                                      n1[0]+n1[1]+n1[2]+d+e+f+n_dash,lamda_bar)
                         *tmp_wa_2;
              }
            }
          }
          if(fabs(tmp_wa_1)>1.0e-13){
            ret+=C_na[n2[0]][d]*C_na[n2[1]][e]*C_na[n2[2]][f]
                *pow(CB[0],n2[0]-d)*pow(CB[1],n2[1]-e)*pow(CB[2],n2[2]-f)
                *tmp_wa_1;
          }
        }
      }
    }
    return Dabc*ret;
  }else if(k_length_A>1.0e-12 && k_length_B<1.0e-12){
 //   cout<<" in case of 3 "<<endl; 
    for(int a=0;a<=n1[0];a++){
      for(int b=0;b<=n1[1];b++){
        for(int c=0;c<=n1[2];c++){
          tmp_wa_1=0.0;
          for(int lamda=0;lamda<=max_lamda;lamda++){
            if((a+b+c+L-lamda)%2==0){
              tmp_wa_2=0.0;
              for(int m=-L;m<=L;m++){
                tmp_wa_2+=cal_ECP_type2_ANGULAR_integral_A(a,b,c,lamda,L,m)
                         *v_xyz_Ylm_integral_over_omega[n2[0]][n2[1]][n2[2]][L][L+m];
              }
              if(fabs(tmp_wa_2)<1.0e-13){
                tmp_wa_1+=0.0;
              }else{
                tmp_wa_1+=cal_ECP_type1_RADIAL_integral(k_length_A,alpha,
                                                        a+b+c+n2[0]+n2[1]+n2[2]+n_dash,lamda)
                         *tmp_wa_2;
              }
            }
          }
          if(fabs(tmp_wa_1)>1.0e-13){
            ret+=C_na[n1[0]][a]*C_na[n1[1]][b]*C_na[n1[2]][c]
                *pow(CA[0],n1[0]-a)*pow(CA[1],n1[1]-b)*pow(CA[2],n1[2]-c)
                *tmp_wa_1;
          }
        }
      }
    }
    return Dabc*ret;
  }else{   // for k_length_A<1.0e-10 && k_length_B<1.0e-10
    double tmp1,tmp2;
    tmp1=0.0;
    for(int m=-L;m<=L;m++){
      tmp1+=v_xyz_Ylm_integral_over_omega[n1[0]][n1[1]][n1[2]][L][L+m]
           *v_xyz_Ylm_integral_over_omega[n2[0]][n2[1]][n2[2]][L][L+m];

    }
    int t_n=n1[0]+n1[1]+n1[2]+n2[0]+n2[1]+n2[2]+n_dash;
    if((t_n%2)==0){
      tmp2=nnn_m1[t_n]*(sqrt(M_PI)/pow(2.0,t_n/2.0));
    }else{
      tmp2=n_kaizyou[(t_n-1)/2];
    }
    tmp2*=0.5*pow(alpha,-0.5*(t_n+1));
    return tmp1*tmp2;
  } 
}

template <typename Integ1e>
double ECP_integral<Integ1e>::cal_xyz_Ylm_integral_over_omega(int I,int J,int K,int l,int m){
  double ret=0.0;
  int r,s,t;
  int num_rsh;
  double keisu;
  num_rsh=rsh.get_num(l,m);
  for(int i=0;i<num_rsh;i++){
    r=rsh.get_r(l,m,i);
    s=rsh.get_s(l,m,i);
    t=rsh.get_t(l,m,i);
    keisu=rsh.get_keisu(l,m,i);
    ret+=keisu*v_xyz_integral_over_omega[I+r][J+s][K+t];
  }
  return ret;
}


template <typename Integ1e>
void ECP_integral<Integ1e>::set_primitives4_sub1(double g1,const double R1[3],double g2,const double R2[3],double gc,const double C[3]){
                                        
                                   
  alpha=g1+g2+gc;
  CA[0]=C[0]-R1[0]; CA[1]=C[1]-R1[1]; CA[2]=C[2]-R1[2];
  CB[0]=C[0]-R2[0]; CB[1]=C[1]-R2[1]; CB[2]=C[2]-R2[2];
  Dabc=4*M_PI*exp(-g1*(CA[0]*CA[0]+CA[1]*CA[1]+CA[2]*CA[2])
                -g2*(CB[0]*CB[0]+CB[1]*CB[1]+CB[2]*CB[2]));

}

template <typename Integ1e>
void ECP_integral<Integ1e>::set_primitives4_sub2(double g1,double g2,int n_dash_c,int t_n1,int t_n2,int cth_L){
  int num_rsh_rst,r,s,t;
  double tmp_wa,keisu_rsh;
  k_xyz[0]=-2.0*(g1*CA[0]+g2*CB[0]); k_xyz[1]=-2.0*(g1*CA[1]+g2*CB[1]); k_xyz[2]=-2.0*(g1*CA[2]+g2*CB[2]);
  k_length=sqrt(k_xyz[0]*k_xyz[0]+k_xyz[1]*k_xyz[1]+k_xyz[2]*k_xyz[2]);
  n_dash=n_dash_c;
  k_length_A=k_length_B=0.0;

  if(cth_L<0){
    for(int lamda=0;lamda<=t_n1+t_n2;lamda++){
      for(int myu=-lamda;myu<=lamda;myu++){
        tmp_wa=0;
        num_rsh_rst=rsh.get_num(lamda,myu);
        for(int i=0;i<num_rsh_rst;i++){
          r=rsh.get_r(lamda,myu,i);
          s=rsh.get_s(lamda,myu,i);
          t=rsh.get_t(lamda,myu,i);
          keisu_rsh=rsh.get_keisu(lamda,myu,i);
          tmp_wa+=keisu_rsh*pow(k_xyz[0]/k_length,r)*pow(k_xyz[1]/k_length,s)*pow(k_xyz[2]/k_length,t);
        }
        v_y_k_xyz[lamda][myu+lamda]=tmp_wa;
      }
    }

    for(int n=n_dash;n<=t_n1+t_n2+n_dash;n++){
      for(int lamda=0;lamda<=t_n1+t_n2;lamda++){
        check_type1_radial[n][lamda]=0;
      }
    }
  }else{
    k_xyz_A[0]=-2.0*g1*CA[0];
    k_xyz_A[1]=-2.0*g1*CA[1];
    k_xyz_A[2]=-2.0*g1*CA[2];
    k_length_A=sqrt(k_xyz_A[0]*k_xyz_A[0]+k_xyz_A[1]*k_xyz_A[1]+k_xyz_A[2]*k_xyz_A[2]);

    for(int lamda=0;lamda<=t_n1+cth_L;lamda++){
      for(int myu=-lamda;myu<=lamda;myu++){
        tmp_wa=0;
        num_rsh_rst=rsh.get_num(lamda,myu);
        for(int i=0;i<num_rsh_rst;i++){
          r=rsh.get_r(lamda,myu,i);
          s=rsh.get_s(lamda,myu,i);
          t=rsh.get_t(lamda,myu,i);
          keisu_rsh=rsh.get_keisu(lamda,myu,i);
          tmp_wa+=keisu_rsh
                 *pow(k_xyz_A[0]/k_length_A,r)*pow(k_xyz_A[1]/k_length_A,s)*pow(k_xyz_A[2]/k_length_A,t);
        }
        v_y_k_xyz_A[lamda][myu+lamda]=tmp_wa;
      }
    }

    k_xyz_B[0]=-2.0*g2*CB[0];
    k_xyz_B[1]=-2.0*g2*CB[1];
    k_xyz_B[2]=-2.0*g2*CB[2];
    k_length_B=sqrt(k_xyz_B[0]*k_xyz_B[0]+k_xyz_B[1]*k_xyz_B[1]+k_xyz_B[2]*k_xyz_B[2]);

    for(int lamda=0;lamda<=t_n2+cth_L;lamda++){
      for(int myu=-lamda;myu<=lamda;myu++){
        tmp_wa=0;
        num_rsh_rst=rsh.get_num(lamda,myu);
        for(int i=0;i<num_rsh_rst;i++){
          r=rsh.get_r(lamda,myu,i);
          s=rsh.get_s(lamda,myu,i);
          t=rsh.get_t(lamda,myu,i);
          keisu_rsh=rsh.get_keisu(lamda,myu,i);
          tmp_wa+=keisu_rsh
                 *pow(k_xyz_B[0]/k_length_B,r)*pow(k_xyz_B[1]/k_length_B,s)*pow(k_xyz_B[2]/k_length_B,t);
        }
        v_y_k_xyz_B[lamda][myu+lamda]=tmp_wa;
      }
    }


    for(int n=n_dash;n<=t_n1+t_n2+n_dash;n++){
      for(int lamda=0;lamda<=t_n1+cth_L;lamda++){
        for(int lamda_bar=0;lamda_bar<=t_n2+cth_L;lamda_bar++){
          check_type2_radial[n][lamda][lamda_bar]=0;
        }
      }
    }
    double rc=0.5*(k_length_A+k_length_B)/sqrt(alpha);
    a_value=exp(rc*rc)*sqrt(M_PI)/(4.0*k_length_A*k_length_B);
    rc_div_sqrt_alpha=rc/sqrt(alpha);

  }
}



template <typename M_tmpl,typename Integ1e>                         
void ECP_matrix<M_tmpl,Integ1e>::cal_shell(std::vector<double> &ret_shell,int p,int q,int cth,
                                           const std::vector<int> &nc,const std::vector<int> &nt,
                                           const std::vector<Shell_Cgto> &scgtos,const std::vector<ECP> &ecps,
                                           const CTRL_PBC &ctrl_pbc,ECP_integral<Integ1e> &ecp_integ)
{
  std::vector<double> Rp     = scgtos[p].get_R();
  std::vector<double> Rq     = scgtos[q].get_R();
  std::vector<double> C      = ecps[cth].get_C();
  std::vector<double> Rq_pbc = ctrl_pbc.get_R_pbc(Rq,nc);
  std::vector<double> C_pbc  = ctrl_pbc.get_R_pbc(C,nt);
  int QC=Util_PBC::cal_q(nc,ctrl_pbc.get_max_Nc());
  int zero_QC=ctrl_pbc.get_zero_qc();

  int tn_p=scgtos[p].get_max_tn();
  int tn_q=scgtos[q].get_max_tn();

  int n_cgto_p=scgtos[p].get_num_cgto();
  int n_cgto_q=scgtos[q].get_num_cgto();
  int n_cgto_pq=n_cgto_p*n_cgto_q;
  ret_shell.reserve(n_cgto_pq);
  ret_shell.clear();
  for(int i=0;i<n_cgto_pq;i++) ret_shell.push_back(0.0);

  std::vector<double> g_p = scgtos[p].get_g();
  std::vector<double> d_p = scgtos[p].get_d();
  std::vector<double> g_q = scgtos[q].get_g();
  std::vector<double> d_q = scgtos[q].get_d();


  int min_i=scgtos[p].get_min_cgto_no();
  int min_j=scgtos[q].get_min_cgto_no();
  int max_i=scgtos[p].get_max_cgto_no();
  int max_j=scgtos[q].get_max_cgto_no();

  //
  // loop for pgto
  for(int a=0;a<scgtos[p].get_num_pgto();a++){
    for(int b=0;b<scgtos[q].get_num_pgto();b++){
      for(int c=0;c<ecps[cth].get_num_pc();c++){

        double g_c=ecps[cth].get_nth_g(c);
        ecp_integ.set_primitives4_sub1(g_p[a],&Rp[0],g_q[b],&Rq_pbc[0],g_c,&C_pbc[0]);
        double v_Dabc=fabs(ecp_integ.get_Dabc());
        if(v_Dabc>CUTOFF_ECP){
          int cth_L=ecps[cth].get_L();
          int ecp_k=ecps[cth].get_nth_k(c);
          double tmp_kth_d=ecps[cth].get_nth_d(c);
          ecp_integ.set_primitives4_sub2(g_p[a],g_q[b],ecp_k,tn_p,tn_q,cth_L);
          for(int i=min_i;i<=max_i;i++){
            int start_j=min_j;
            if(QC==zero_QC) start_j=((i>min_j)?i:min_j);
            for(int j=start_j;j<=max_j;j++){
              std::vector<int> n1=ecp_integ.get_no_to_n(tn_p,i-min_i);
              std::vector<int> n2=ecp_integ.get_no_to_n(tn_q,j-min_j);
              double I_a=ecp_integ.cal_I(g_p[a],n1);
              double I_b=ecp_integ.cal_I(g_q[b],n2);
              double value=0.0;
              if(cth_L<0){ // for type1 integral
                value=ecp_integ.cal_ECP_type1_integral_for_primitive3(&n1[0],&n2[0]);
              }else{       // for type2 integral
                value=ecp_integ.cal_ECP_type2_integral_for_primitive3(&n1[0],&n2[0],cth_L);
              }
              value*=d_p[a]*d_q[b]*tmp_kth_d*I_a*I_b;
              ret_shell[(i-min_i)*(max_j-min_j+1)+(j-min_j)]+=value;
            }
          }
        }
      }
    }
  }
}


template <typename M_tmpl,typename Integ1e>
void ECP_matrix<M_tmpl,Integ1e>::cal_ECP_matrix_base(std::vector<M_tmpl*> &ret_ecpM, const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps,
                                       const CTRL_PBC &ctrl_pbc)
{

  int N_process=1;
  int process_num=0;
  #ifdef USE_MPI_LOTUS
  Util_MPI::get_size_rank(N_process,process_num);
  #endif


  int N_scgtos=scgtos.size();
  int N_cgtos=Util_GTO::get_N_cgtos(scgtos);
  std::vector<int> n_zero(3,0);
  int zero_q=ctrl_pbc.get_zero_qc();
  int N123_c=ctrl_pbc.get_N123_c();
  // cutoff

  std::vector<M_tmpl> cutoffM;
  Util_GTO::cal_cutoffM_PBC<M_tmpl,Integ1e>(cutoffM,scgtos,ctrl_pbc);

  ret_ecpM.reserve(N123_c);                       
  for(int i=0;i<N123_c;i++) ret_ecpM[i]->set_IJ(N_cgtos,N_cgtos);

  std::vector<int> max_Nc=ctrl_pbc.get_max_Nc();
  std::vector<int> max_nc(3,0), max_nt(3,0);
  if(max_Nc[0]!=0) max_nc[0]=1;
  if(max_Nc[1]!=0) max_nc[1]=1;
  if(max_Nc[2]!=0) max_nc[2]=1;

  if(max_Nc[0]!=0) max_nt[0]=max_Nc[0];
  if(max_Nc[1]!=0) max_nt[1]=max_Nc[1];
  if(max_Nc[2]!=0) max_nt[2]=max_Nc[2];
 
  #ifdef _OPENMP
  #pragma omp parallel
  {  // start of openMP parallel-loop
  int N_threads  = omp_get_num_threads();
  int thread_num = omp_get_thread_num();
  #else
  int N_threads  = 1;
  int thread_num = 0;
  #endif
  int N_core     = N_threads*N_process;
  int core_num   = process_num*N_threads + thread_num;

  std::vector<M_tmpl> omp_M(N123_c);
  for(int t=0;t<=zero_q;t++){
    omp_M[t].set_IJ(N_cgtos, N_cgtos);
  }

  std::vector<double> tmp_shell;
  ECP_integral<Integ1e> ecp_integ;
 
  for(int qc=0;qc<=Util_PBC::get_zero_q(max_nc);qc++){
    std::vector<int> nc=Util_PBC::cal_n_from_q(qc,max_nc);
    int QC=Util_PBC::cal_q(nc,max_Nc);
    for(int p=0;p<N_scgtos;p++){
      int start_q=0;
      if(qc==Util_PBC::get_zero_q(max_nc)) start_q=p; 
      for(int q=start_q;q<N_scgtos;q++){
        if( (q*N_scgtos+p)%N_core==core_num ){ //mpi+openmp
          double v_cutoff=fabs(cutoffM[QC].get_value(p,q));
          if(v_cutoff>CUTOFF_ECP){
            int min_i=scgtos[p].get_min_cgto_no();
            int min_j=scgtos[q].get_min_cgto_no();
            int max_i=scgtos[p].get_max_cgto_no();
            int max_j=scgtos[q].get_max_cgto_no();
            for(int cth=0;cth<ecps.size();cth++){
              for(int qt=0;qt<Util_PBC::get_N123(max_nt);qt++){
                std::vector<int> nt=Util_PBC::cal_n_from_q(qt,max_nt); 
                if(Util_PBC::check_range(qc,qt,max_nc,max_nt)){

                  cal_shell(tmp_shell,p,q,cth,nc,nt,scgtos,ecps,ctrl_pbc,ecp_integ);
                  int cc=0;
                  for(int i=min_i;i<=max_i;i++){
                    for(int j=min_j;j<=max_j;j++){
//                      if(QC==zero_q && j>=i) ret_ecpM[QC]->add(i,j,tmp_shell[cc]);
//                      if(QC!=zero_q)         ret_ecpM[QC]->add(i,j,tmp_shell[cc]);
                      if(QC==zero_q && j>=i) omp_M[QC].add(i,j,tmp_shell[cc]);
                      if(QC!=zero_q)         omp_M[QC].add(i,j,tmp_shell[cc]);
                      cc++; 
                    }  
                  }
                }

              } 
            }
              
          }
        }
      }
    }
  }


  #ifdef _OPENMP
  #pragma omp critical(mat_add)
  #endif
  {
    for(int t=0;t<=zero_q;t++){
      for(int i=0;i<N_cgtos;i++){
        for(int j=0;j<N_cgtos;j++){
          ret_ecpM[t]->add(i,j,omp_M[t].get_value(i,j));
        }
      }
    }
  }

  #ifdef _OPENMP
  }  // end of openMP parallel-loop
  #endif 

  #ifdef USE_MPI_LOTUS
//  Util_MPI::allreduce(ret_ecpM);
  Util_MPI::isendrecv(ret_ecpM); 
  #endif

  for(int i=0;i<N_cgtos;i++){
    for(int j=i+1;j<N_cgtos;j++){
      double tmp_v=ret_ecpM[zero_q]->get_value(i,j);
      ret_ecpM[zero_q]->set_value(j,i,tmp_v);
    }
  }


  for(int q=1;q<=zero_q;q++) mat_transpose(*ret_ecpM[zero_q+q],*ret_ecpM[zero_q-q]);

} 
  


template <typename M_tmpl,typename Integ1e>                         
void ECP_matrix<M_tmpl,Integ1e>::cal_grad_shell(std::vector<double> &ret_grad_shell, int p, int q, int cth, 
                                                const std::vector<int> &nc, const std::vector<int> &nt,
                                                const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, 
                                                const std::vector<M_tmpl*> &D_PBC, const CTRL_PBC &ctrl_pbc, ECP_integral<Integ1e> &ecp_integ)
{
  std::vector<double> Rp     = scgtos[p].get_R();
  std::vector<double> Rq     = scgtos[q].get_R();
  std::vector<double> C      = ecps[cth].get_C();
  std::vector<double> Rq_pbc = ctrl_pbc.get_R_pbc(Rq,nc);
  std::vector<double> C_pbc  = ctrl_pbc.get_R_pbc(C,nt);
  int QC=Util_PBC::cal_q(nc,ctrl_pbc.get_max_Nc());
  int zero_QC=ctrl_pbc.get_zero_qc();
  int N_scgtos=scgtos.size();
  int N_atoms=scgtos[N_scgtos-1].get_atom_no()+1;

  int tn_p=scgtos[p].get_max_tn();
  int tn_q=scgtos[q].get_max_tn();

  ret_grad_shell.reserve(N_atoms*3);
  ret_grad_shell.clear();
  for(int i=0;i<N_atoms*3;i++) ret_grad_shell.push_back(0.0);

  std::vector<double> g_p = scgtos[p].get_g();
  std::vector<double> d_p = scgtos[p].get_d();
  std::vector<double> g_q = scgtos[q].get_g();
  std::vector<double> d_q = scgtos[q].get_d();


  int min_i=scgtos[p].get_min_cgto_no();
  int min_j=scgtos[q].get_min_cgto_no();
  int max_i=scgtos[p].get_max_cgto_no();
  int max_j=scgtos[q].get_max_cgto_no();

  int an_p=scgtos[p].get_atom_no();
  int an_q=scgtos[q].get_atom_no();
  int an_c=ecps[cth].get_atom_no();
  //
  // loop for pgto
  for(int a=0;a<scgtos[p].get_num_pgto();a++){
    for(int b=0;b<scgtos[q].get_num_pgto();b++){
      for(int c=0;c<ecps[cth].get_num_pc();c++){

        double g_c=ecps[cth].get_nth_g(c);
        ecp_integ.set_primitives4_sub1(g_p[a],&Rp[0],g_q[b],&Rq_pbc[0],g_c,&C_pbc[0]);
        double v_Dabc=fabs(ecp_integ.get_Dabc());
        if(v_Dabc>CUTOFF_ECP){
          int cth_L=ecps[cth].get_L();
          int ecp_k=ecps[cth].get_nth_k(c);
          double tmp_kth_d=ecps[cth].get_nth_d(c);
          ecp_integ.set_primitives4_sub2(g_p[a],g_q[b],ecp_k,(tn_p+1),(tn_q+1),cth_L);

          for(int i=min_i;i<=max_i;i++){
            int start_j=min_j;
            if(QC==zero_QC) start_j=((i>min_j)?i:min_j);
            for(int j=start_j;j<=max_j;j++){
              double vDij=D_PBC[QC]->get_value(i,j); 
              if(fabs(vDij)>CUTOFF_ECP){

                for(int xyz=0;xyz<3;xyz++){
                  std::vector<int> n1=ecp_integ.get_no_to_n(tn_p,i-min_i);
                  std::vector<int> n2=ecp_integ.get_no_to_n(tn_q,j-min_j);
                  double I_a=ecp_integ.cal_I(g_p[a],n1);
                  double I_b=ecp_integ.cal_I(g_q[b],n2);
                  std::vector<int> n1_p=ecp_integ.get_no_to_n(tn_p,i-min_i);
                  std::vector<int> n1_m=ecp_integ.get_no_to_n(tn_p,i-min_i);
                  std::vector<int> n2_p=ecp_integ.get_no_to_n(tn_q,j-min_j);
                  std::vector<int> n2_m=ecp_integ.get_no_to_n(tn_q,j-min_j);
                  n1_p[xyz]++; n1_m[xyz]--;
                  n2_p[xyz]++; n2_m[xyz]--;
                  double v1_p,v1_m,v2_p,v2_m;
                  v1_p=v1_m=v2_p=v2_m=0.0;
                  if(cth_L<0){
                    v1_p=ecp_integ.cal_ECP_type1_integral_for_primitive3(&n1_p[0],&n2[0]);
                    if(n1_m[xyz]>=0) v1_m=ecp_integ.cal_ECP_type1_integral_for_primitive3(&n1_m[0],&n2[0]);
                    if(QC==zero_QC){
                      v2_p=ecp_integ.cal_ECP_type1_integral_for_primitive3(&n1[0],&n2_p[0]);
                      if(n2_m[xyz]>=0) v2_m=ecp_integ.cal_ECP_type1_integral_for_primitive3(&n1[0],&n2_m[0]);
                    }else{
                      v2_p=0.0;  v2_m=0.0; 
                    }
                  }else{
                    v1_p=ecp_integ.cal_ECP_type2_integral_for_primitive3(&n1_p[0],&n2[0],cth_L);
                    if(n1_m[xyz]>=0) v1_m=ecp_integ.cal_ECP_type2_integral_for_primitive3(&n1_m[0],&n2[0],cth_L);
                    if(QC==zero_QC){
                      v2_p=ecp_integ.cal_ECP_type2_integral_for_primitive3(&n1[0],&n2_p[0],cth_L);
                      if(n2_m[xyz]>=0) v2_m=ecp_integ.cal_ECP_type2_integral_for_primitive3(&n1[0],&n2_m[0],cth_L);
                    }else{
                      v2_p=0.0;  v2_m=0.0; 
                    }
                  }
                  double v_c=-2.0*(g_p[a]*v1_p+g_q[b]*v2_p); 
                  double v_p=2.0*g_p[a]*v1_p; 
                  double v_q=2.0*g_q[b]*v2_p;

                  if(n1_m[xyz]>=0){ v_c+=n1[xyz]*v1_m; v_p-=n1[xyz]*v1_m; }
                  if(n2_m[xyz]>=0){ v_c+=n2[xyz]*v2_m; v_q-=n2[xyz]*v2_m; }

                  double ddIId=d_p[a]*d_q[b]*I_a*I_b*tmp_kth_d;
                  v_c*=ddIId*vDij; 
                  v_p*=ddIId*vDij; 
                  v_q*=ddIId*vDij; 

                  ret_grad_shell[an_c*3+xyz]+=v_c;
                  ret_grad_shell[an_p*3+xyz]+=v_p;
                  if(i!=j){
                    ret_grad_shell[an_c*3+xyz]+=v_c;
                    ret_grad_shell[an_p*3+xyz]+=v_p;
                  }
                  if(QC==zero_QC){  
                    ret_grad_shell[an_q*3+xyz]+=v_q;
                    if(i!=j){
                      ret_grad_shell[an_q*3+xyz]+=v_q; 
                    }
                  }
                }

              }
            }
          }
        }
      }
    }
  }
}


template <typename M_tmpl,typename Integ1e>
std::vector<double> ECP_matrix<M_tmpl,Integ1e>::cal_grad_ECP_base(const std::vector<Shell_Cgto> &scgtos,const std::vector<ECP> &ecps,
                                           const std::vector<M_tmpl*> &D_PBC,const CTRL_PBC &ctrl_pbc)
{
                                       
  int N_process=1;
  int process_num=0;
  Util_MPI::get_size_rank(N_process,process_num);

  int N_scgtos=scgtos.size();
  int N_atoms=scgtos[N_scgtos-1].get_atom_no()+1;
  // cutoff

  std::vector<M_tmpl> cutoffM;
  Util_GTO::cal_cutoffM_PBC<M_tmpl,Integ1e>(cutoffM,scgtos,ctrl_pbc);

  std::vector<int> max_Nc=ctrl_pbc.get_max_Nc();
  std::vector<int> max_nc(3,0), max_nt(3,0);
  if(max_Nc[0]!=0) max_nc[0]=1;
  if(max_Nc[1]!=0) max_nc[1]=1;
  if(max_Nc[2]!=0) max_nc[2]=1;

  if(max_Nc[0]!=0) max_nt[0]=max_Nc[0];
  if(max_Nc[1]!=0) max_nt[1]=max_Nc[1];
  if(max_Nc[2]!=0) max_nt[2]=max_Nc[2];

  std::vector<double> ret_grad(3*N_atoms,0.0); 

   
  #ifdef _OPENMP
  #pragma omp parallel
  {  // start of openMP parallel-loop
  #endif

  std::vector<double> omp_grad(3*N_atoms,0.0);
  std::vector<double> tmp_grad(3*N_atoms,0.0);
 
  ECP_integral<Integ1e> ecp_integ;

  for(int qc=0;qc<=Util_PBC::get_zero_q(max_nc);qc++){
    std::vector<int> nc=Util_PBC::cal_n_from_q(qc,max_nc);
    for(int p=0;p<N_scgtos;p++){
      if(p%N_process==process_num){ //mpi
        int start_q=0;
        if(qc==Util_PBC::get_zero_q(max_nc)) start_q=p; 
        #ifdef _OPENMP 
        #pragma omp for schedule(dynamic)
        #endif
        for(int q=start_q;q<N_scgtos;q++){
          int QC=Util_PBC::cal_q(nc,max_Nc);
          double v_cutoff=fabs(cutoffM[QC].get_value(p,q));
          if(v_cutoff>CUTOFF_ECP){
            for(int cth=0;cth<ecps.size();cth++){
              for(int qt=0;qt<Util_PBC::get_N123(max_nt);qt++){
                std::vector<int> nt=Util_PBC::cal_n_from_q(qt,max_nt); 
                if(Util_PBC::check_range(qc,qt,nc,nt)){
                  cal_grad_shell(tmp_grad,p,q,cth,nc,nt,scgtos,ecps,D_PBC,ctrl_pbc,ecp_integ);
                  for(int i=0;i<N_atoms*3;i++) omp_grad[i]+=tmp_grad[i];
                }
              }
            }
          }
        }
      }
    }
  }

  #ifdef _OPENMP
  #pragma omp critical(add_cal_ECP_grad)
  #endif
  {
    for(int i=0;i<3*N_atoms;i++) ret_grad[i]+=omp_grad[i];
  }

  #ifdef _OPENMP
  }  // end of openMP parallel-loop
  #endif


  #ifdef USE_MPI_LOTUS
  Util_MPI::allreduce(ret_grad);
  #endif

  return ret_grad;
}



}  // end of namespace "Lotus_core"

#endif // end of include-guard
