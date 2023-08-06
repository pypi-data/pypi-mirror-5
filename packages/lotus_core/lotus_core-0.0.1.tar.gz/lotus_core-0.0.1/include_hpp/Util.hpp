

#ifndef UTIL_H
#define UTIL_H



#include "gto.hpp"
#include "Charge.hpp"
#include "ECP_tmpl.hpp"

#include <vector>
#include <iostream>
#include <string>


namespace Lotus_core {


class Util {
public:


  static std::string get_string_from_file(const char *filename)
  {
    std::ifstream ifs(filename);
    if(!ifs){
      std::cout<<" Error: cannnot open file,  "<<filename<<std::endl;
      exit(1);
    }

    std::string line,ret_str="";
    while (std::getline(ifs,line)) ret_str+=line+"\n";
    ret_str+="\n";

    ifs.close();
    return ret_str;
  }

  template <typename M_tmpl1, typename M_tmpl2>
  static double cal_DV(const M_tmpl1 &D,const M_tmpl2 &V){
    int N_cgtos=D.get_I();
    double ret=0.0;
    for(int i=0;i<N_cgtos;i++){
      for(int j=0;j<N_cgtos;j++){
        ret  +=D.get_value(i,j)*V.get_value(i,j);
      }
    }
    return ret;
  }


  template <typename M_tmpl>
  static void cal_D(M_tmpl &retD, const M_tmpl &X, const std::vector<double> &occ){
    int k,l,p;
    int N_cgtos = X.get_I();
    retD.set_IJ(N_cgtos, N_cgtos);
    double x_k,x_l;
    double tmpD;
    for(k=0;k<N_cgtos;k++){
      for(l=0;l<N_cgtos;l++){
        tmpD=0;
        for(p=0;p<N_cgtos;p++){
          x_k=X.get_value(k,p);
          x_l=X.get_value(l,p);
          tmpD+=occ[p]*x_k*x_l;
        }
        retD.set_value(k,l,tmpD);
      }
    }
  }


  // energy-weighted density matrix
  template <typename M_tmpl>
  static void cal_W(M_tmpl &retW, const M_tmpl &X, const std::vector<double> &occ, const std::vector<double> &lamda){
    int k,l,p;
    int N_cgtos=X.get_I();
    retW.set_IJ(N_cgtos, N_cgtos);
    double x_k,x_l;
    double tmpW;
    for(k=0;k<N_cgtos;k++){
      for(l=0;l<N_cgtos;l++){
        tmpW=0;
        for(p=0;p<N_cgtos;p++){
          x_k=X.get_value(k,p);
          x_l=X.get_value(l,p);
          tmpW+=lamda[p]*occ[p]*x_k*x_l;
        }
        retW.set_value(k,l,tmpW);
      }
    }
  }


  static void cal_occ_ab(std::vector<double> &occ_a, std::vector<double> &occ_b, int N_cgtos, int N_ele, int spin)
  {
    occ_a.resize(N_cgtos);
    occ_b.resize(N_cgtos);

    if(N_ele%2==1 && spin==1){
      std::cout<<" ERROR:  number of electrons must be even for singlet-spin-state N_ele,spin "<<N_ele<<" "<<spin<<std::endl;
      exit(1);
    } 

    if(spin==1 && N_ele%2==0){
      for(int i=0;i<N_cgtos;i++){
        if(i<N_ele/2) occ_a[i]=occ_b[i]=1.0;
        else          occ_a[i]=occ_b[i]=0.0;
      }
    }else{
      int tmpN=N_ele-(spin-1);
      if(tmpN%2!=0){
        std::cout<<" Error: number of electron and spin dose not match, N_ele,spin "<<N_ele<<" "<<spin<<std::endl;
        exit(1); 
      }
      for(int i=0;i<N_cgtos;i++){ occ_a[i]=0.0; occ_b[i]=0.0; }
      for(int i=0;i<(tmpN/2);i++){
        occ_a[i]=1.0;
        occ_b[i]=1.0;
      }
      for(int i=(tmpN/2);i<tmpN/2+(spin-1);i++){
        occ_a[i]=1.0;
      }
    } 
  }



  static void cal_occ_ab(std::vector<double> &occ_a, std::vector<double> &occ_b,
                        const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps, int mol_charge, int spin){
    int N_cgtos = Util_GTO::get_N_cgtos(scgtos);
    int total_charge = get_total_charge(scgtos, ecps);
    int N_ele = total_charge - mol_charge;
    cal_occ_ab(occ_a, occ_b, N_cgtos, N_ele, spin);
  }

  static std::vector<double> cal_occ( const std::vector<Shell_Cgto> &scgtos,  const std::vector<ECP> &ecps, int mol_charge, int spin){
    std::vector<double> ret_occ, dmy_occ;
    cal_occ_ab(ret_occ, dmy_occ, scgtos, ecps, mol_charge, spin);
    return ret_occ;
  } 

  static std::vector<double> cal_occ( const std::vector<Shell_Cgto> &scgtos,  int mol_charge, int spin){
    std::vector<ECP> dmy_ecp(0);
    return cal_occ(scgtos, dmy_ecp, mol_charge, spin);
  }

  // boost-python
  static void cal_occ_ab_bp1(std::vector<double> &occ_a, std::vector<double> &occ_b, int N_cgtos, int N_ele, int spin){
    cal_occ_ab(occ_a, occ_b, N_cgtos, N_ele, spin);
  }
  static void cal_occ_ab_bp2(std::vector<double> &occ_a, std::vector<double> &occ_b,
                            const std::vector<Shell_Cgto> &scgtos,  const std::vector<ECP> &ecps, int mol_charge, int spin){
    cal_occ_ab(occ_a, occ_b, scgtos,  ecps, mol_charge, spin);
  }
  static std::vector<double> cal_occ_bp1( const std::vector<Shell_Cgto> &scgtos,  const std::vector<ECP> &ecps, int mol_charge, int spin){
    return cal_occ(scgtos, ecps, mol_charge, spin);
  }
  static std::vector<double> cal_occ_bp2( const std::vector<Shell_Cgto> &scgtos,  int mol_charge, int spin){
    return cal_occ(scgtos, mol_charge, spin);
  }
  //



  template <typename Cgto>
  static std::vector<Charge> get_charges(const std::vector<Cgto> &cgtos){
    std::vector<Charge> ret_charges;

    for(int i=0;i<cgtos.size();i++){
      int atom_no=cgtos[i].get_atom_no();
      std::vector<double> R=cgtos[i].get_R();
      double Z = (double)cgtos[i].get_atom_type();
      int flag=0;
      for(int j=0;j<ret_charges.size();j++){
        if(ret_charges[j].atom_no==atom_no){
          flag=1;
          break;
        }
      }
      if(flag==0) ret_charges.push_back(Charge(Z,R[0],R[1],R[2],atom_no));
    }

    return ret_charges;

  }


  template <typename Cgto>
  static std::vector<Charge> get_charges(const std::vector<Cgto> &cgtos, const std::vector<ECP> &ecps){
    std::vector<Charge> ret_charges = get_charges(cgtos);
    for(int i=0;i<ret_charges.size();i++){
      int atom_no=ret_charges[i].atom_no;
      double core_ele = ECP::get_core_ele_from_ecps(ecps, atom_no);
      ret_charges[i].charge=ret_charges[i].charge - core_ele;
    }
    return ret_charges;
  }

  // for boost-python
  template <typename Cgto>
  static std::vector<Charge> get_charges_bp1(const std::vector<Cgto> &cgtos){
    return get_charges(cgtos);
  }
  template <typename Cgto>
  std::vector<Charge> get_charges_bp2(const std::vector<Cgto> &cgtos, const std::vector<ECP> &ecps){
    return get_charges(cgtos, ecps);
  }
  //


  template <typename Cgto>
  static int get_total_charge(const std::vector<Cgto> &cgtos, const std::vector<ECP> &ecps){
    std::vector<Charge> charges = get_charges(cgtos, ecps);
    int ret_total_charge=0;
    for(int i=0;i<charges.size();i++) ret_total_charge+= (int) charges[i].charge;
    return ret_total_charge;
  }


  template <typename Cgto>
  static int get_total_charge(const std::vector<Cgto> &cgtos){
    std::vector<ECP> dmy_ecps(0);
    return get_total_charge(cgtos, dmy_ecps);
  }

  // for boost-python
  template <typename Cgto>
  static int get_total_charge_bp1(const std::vector<Cgto> &cgtos, const std::vector<ECP> &ecps){
    return get_total_charge(cgtos, ecps);
  }
  template <typename Cgto>
  static int get_total_charge_bp2(const std::vector<Cgto> &cgtos){
    return get_total_charge(cgtos);
  }
  //


  template <typename Cgto>
  static double cal_energy_repul_nn(const std::vector<Cgto> &cgtos, const std::vector<ECP> &ecps){
    std::vector<Charge> charges = get_charges(cgtos, ecps);
    double ret_ene=0.0;
    int N_atoms = charges.size();
    for(int i=0;i<N_atoms;i++){
      for(int j=i+1;j<N_atoms;j++){
        std::vector<double> Ri = charges[i].get_Rxyz();
        std::vector<double> Rj = charges[j].get_Rxyz();
        ret_ene += (charges[i].charge*charges[j].charge)
                 / sqrt( (Ri[0]-Rj[0])*(Ri[0]-Rj[0]) + (Ri[1]-Rj[1])*(Ri[1]-Rj[1]) + (Ri[2]-Rj[2])*(Ri[2]-Rj[2]) );
      }
    }
    return ret_ene;
  }

  template <typename M_tmpl>
  static double get_max_d(const std::vector<M_tmpl> &vec_D, int ind, int pre_ind){
    int N_cgtos = vec_D[0].get_I();
    double max_d=0.0;
    for(int a=0;a<N_cgtos;a++){
      for(int b=a;b<N_cgtos;b++){
        double tmp_d=std::abs(vec_D[ind].get_value(a,b)-vec_D[pre_ind].get_value(a,b));
          if(tmp_d>max_d) max_d=tmp_d;
      }
    }
    return max_d;
  }


};


}  // end of namespace "Lotus_core"
#endif // end of include-guard

