
#ifndef CHARGE_H
#define CHARGE_H

#include <map>
#include <vector>
#include <iostream>

namespace Lotus_core {

class Charge{
public:
  double charge;
  double x,y,z;
  int  atom_no;
  Charge(){ charge=0.0; x=0.0; y=0.0; z=0.0; atom_no=-1; }
  Charge(double in_charge,double in_x,double in_y,double in_z){
    charge =in_charge;
    x      =in_x;
    y      =in_y;
    z      =in_z;
    atom_no=-1;
  }
  Charge(double in_charge,double in_x,double in_y,double in_z,int in_atom_no){
    charge =in_charge;
    x      =in_x;
    y      =in_y;
    z      =in_z;
    atom_no=in_atom_no;
  }
  bool operator==(const Charge &in){ 
    if((void*)this==(void*)&in) return true;
    else                        return false;
  }
  void show(){
    std::cout<<"   charge "<<charge<<" x,y,z "<<x<<" "<<y<<" "<<z<<" atom_no "<<atom_no<<std::endl;
  }
  std::vector<double> get_Rxyz(){
    std::vector<double> retR(3, 0.0);
    retR[0]=x;
    retR[1]=y;
    retR[2]=z;
    return retR;
  }
};

}  // end of namespace "Lotus_core"

#endif // end of include-gurad
