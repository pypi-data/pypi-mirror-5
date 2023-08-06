
#ifndef SCF_DETAIL_HPP
#define SCF_DETAIL_HPP


//#include "SCF.h"


namespace Lotus_core {





template <typename Integ1e, typename Integ2e> template <typename M_tmpl>
void SCF<Integ1e,Integ2e>::cal_h_core(M_tmpl &ret_h_core, const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps) const
{
  int N_cgtos = Util_GTO::get_N_cgtos(scgtos);

  ret_h_core.set_IJ(N_cgtos, N_cgtos);

  Fock1e_tmpl<M_tmpl,Integ1e>         fock1e;
  ECP_matrix<M_tmpl,Integ1e>          ecp_mat;

  fock1e.cal_K(ret_h_core, scgtos);
  M_tmpl tmpM;
  std::vector<Charge> charges = Util::get_charges(scgtos, ecps); 
  fock1e.cal_NA(tmpM, scgtos, charges);
  mat_add(ret_h_core, ret_h_core, tmpM);

  if(ecps.size()>0){
    ecp_mat.cal_ECP(tmpM, scgtos, ecps);
    mat_add(ret_h_core, ret_h_core, tmpM);
  }
}



template <typename Integ1e, typename Integ2e> template <typename M_tmpl>
void SCF<Integ1e,Integ2e>::guess_h_core(M_tmpl &retX, std::vector<double> &ret_lamda, 
       const std::vector<Shell_Cgto> &scgtos, const std::vector<ECP> &ecps) const
{
  M_tmpl H_core, S;
  Fock1e_tmpl<M_tmpl,Integ1e>         fock1e;
  fock1e.cal_S(S, scgtos);
  cal_h_core(H_core, scgtos, ecps);

  // calculation eigen matrix
//  call_dsygv(H_core,S,retX,ret_lamda);
  cal_eigen(H_core,S,retX,ret_lamda);
}



template <typename Integ1e, typename Integ2e> template <typename M_tmpl,typename select_ERI>
void SCF<Integ1e,Integ2e>::cal_Fock_sub(M_tmpl &retM, const M_tmpl &D, const std::vector<Shell_Cgto> &scgtos, 
                       const select_ERI &sel_eri, const GInte_Functor &dft_functor)
{
using namespace std;
  Fock2e_tmpl<M_tmpl,Integ2e> fock2e;
  Grid_Inte<M_tmpl,Integ1e>   grid_inte;

  M_tmpl tmpMx;
  fock2e.cal_Vh_and_Vx(retM, tmpMx, D, scgtos, sel_eri ); 
  double hybrid_x = dft_functor.get_hybrid_hf_x();

  if(fabs(hybrid_x)>1.0e-14)  mat_mul_v(tmpMx, hybrid_x, tmpMx);
  else                        tmpMx.set_zero();

  ene_vh   = Util::cal_DV(D,retM);
  ene_vx   = Util::cal_DV(D,tmpMx);

  mat_add(retM, retM, tmpMx);
  ene_dft=0.0;
  if(dft_functor.get_use_grid_inte()!=0){
    ene_dft = grid_inte.grid_integral_mat(tmpMx, D, scgtos, dft_functor);
    mat_add(retM,retM,tmpMx);
  }

}


template <typename Integ1e, typename Integ2e> template <typename M_tmpl,typename select_ERI>
void SCF<Integ1e,Integ2e>::cal_Fock_sub_u(M_tmpl &retM_a, M_tmpl &retM_b, const M_tmpl &D_a, const M_tmpl &D_b, const std::vector<Shell_Cgto> &scgtos, 
                         const select_ERI &sel_eri, const GInte_Functor &dft_functor)
{
  Fock2e_tmpl<M_tmpl,Integ2e> fock2e;
  Grid_Inte<M_tmpl,Integ1e>   grid_inte;

  M_tmpl tmpM;
  fock2e.cal_Vh_and_Vx_u(tmpM, retM_a, retM_b, D_a, D_b, scgtos, sel_eri ); 
  double hybrid_x = dft_functor.get_hybrid_hf_x();

  if(fabs(hybrid_x)>1.0e-14) mat_mul_v(retM_a, hybrid_x, retM_a);
  else                       retM_a.set_zero();
  if(fabs(hybrid_x)>1.0e-14) mat_mul_v(retM_b, hybrid_x, retM_b);
  else                       retM_b.set_zero();

  ene_vh   = 0.5*(Util::cal_DV(D_a, tmpM)   + Util::cal_DV(D_b, tmpM));
  ene_vx   = 0.5*(Util::cal_DV(D_a, retM_a) + Util::cal_DV(D_b, retM_b));

  mat_add(retM_a, retM_a, tmpM);
  mat_add(retM_b, retM_b, tmpM);

  ene_dft=0.0;
  if(dft_functor.get_use_grid_inte()!=0){
    M_tmpl tmpMx_a, tmpMx_b;
    ene_dft = grid_inte.grid_integral_mat_u(tmpMx_a, tmpMx_b, D_a, D_b, scgtos, dft_functor);
    mat_add(retM_a, retM_a, tmpMx_a);
    mat_add(retM_b, retM_b, tmpMx_b);
  }

}





template <typename Integ1e, typename Integ2e> template <typename vec_M_tmpl,typename M_tmpl>
void SCF<Integ1e,Integ2e>::diis(vec_M_tmpl &F, vec_M_tmpl &D, M_tmpl &S, int n_scf, int max_diis) const
{

  int N_cgtos=F[0].get_I();
  int size_of_diis=n_scf+1;
  if(size_of_diis>=max_diis) size_of_diis=max_diis;
  int ind_p1 = (n_scf+max_diis+1)%max_diis;

  vec_M_tmpl Err(size_of_diis);
  for(int i=0;i<size_of_diis;i++){
    Err[i].set_IJ(N_cgtos,N_cgtos);
  }

  M_tmpl tmpM;
  M_tmpl MM,BB,CC;

  tmpM.set_IJ(N_cgtos, N_cgtos);
  MM.set_IJ(size_of_diis+1,size_of_diis+1);
  BB.set_IJ(size_of_diis+1,1);
  CC.set_IJ(size_of_diis+1,1);

  for(int i=0;i<size_of_diis;i++){
    mat_mul(Err[i],F[i],D[i]);
    mat_mul(Err[i],Err[i],S);
    mat_mul(tmpM,S,D[i]);
    mat_mul(tmpM,tmpM,F[i]);
    mat_sub(Err[i],Err[i],tmpM);
  }
 
  for(int i=0;i<size_of_diis;i++){ 
    for(int j=i;j<size_of_diis;j++){ 
      mat_mul(tmpM,Err[i],Err[j]);
      double tmp_err=tmpM.trace();
      MM.set_value(i,j,tmp_err);
      MM.set_value(j,i,tmp_err);
    }
    MM.set_value(i,size_of_diis,-1);
    MM.set_value(size_of_diis,i,-1);
  }
  BB.set_value(size_of_diis,0,-1);

//  int info=call_dgesv(MM, CC, BB);
//  if(info!=0){
//    std::cout<<" ******** failure in call_dgesv, info="<<info<<" *********"<<std::endl;
//    exit(1);
//  }
  cal_simultaneous_eq(MM, CC, BB);
   
  mat_mul_v(F[ind_p1],CC.get_value(ind_p1,0),F[ind_p1]);
  for(int k=0;k<size_of_diis;k++){
    if(k!=ind_p1){
      mat_mul_v(tmpM, CC.get_value(k,0), F[k]);
      mat_add(F[ind_p1], F[ind_p1], tmpM);
    }
  }

}




template <typename Integ1e, typename Integ2e> template <typename M_tmpl>
void SCF<Integ1e,Integ2e>::ediis_sub(std::vector<double> &ret_coef,
       const std::vector<double> &E, M_tmpl &MM,int size_of_ediis,int ind) const
{

  using namespace std;

  double minE=1.0e10;
  for(int i=0;i<size_of_ediis+1;i++) ret_coef[i]=0.0;
  for(int n=0;n<size_of_ediis;n++){
    int num=i_pow(size_of_ediis,n);
    for(int i=0;i<num;i++){
      std::vector<double> tmp_coef;
      tmp_coef.resize(size_of_ediis+1, 0.0);
      std::vector<int> comb;
      comb.resize(n+1, 0);
      comb[0]=i/i_pow(size_of_ediis,n-1);
      for(int j=1;j<n;j++){
        if(j==n-1){
          comb[j]=i%size_of_ediis;
        }else{
          int tmp_i=i;
          for(int k=0;k<j;k++) tmp_i-=comb[k]*i_pow(size_of_ediis,n-1-k);
          comb[j]=tmp_i/i_pow(size_of_ediis,n-j-1);
        }
      }
      int flag=1;
      for(int j=0;j<n;j++){
        if(comb[j]==ind){
          flag=0;
          break;
        }
        for(int k=j+1;k<n;k++){
          if(comb[j]>=comb[k]){
            flag=0;
            break;
          }
        }
      }
      if(flag==1){
        std::vector<int> ntab;
        ntab.resize(size_of_ediis-n+1, 0);
        int ii_ntab=0;
        for(int j=0;j<size_of_ediis;j++){
          int flag2=1;
          for(int k=0;k<n;k++)
            if(comb[k]==j) flag2=0;
            if(flag2==1){
            ntab[ii_ntab]=j;
            ii_ntab++;
          }
        }

        M_tmpl rMM, rBB, rCC;

        rMM.set_IJ(size_of_ediis-n+1,size_of_ediis-n+1);
        rBB.set_IJ(size_of_ediis-n+1,1);
        rCC.set_IJ(size_of_ediis-n+1,1);
        for(int a=0;a<size_of_ediis-n;a++){
          for(int b=0;b<size_of_ediis-n;b++){
            double tmp_ab=MM.get_value(ntab[a],ntab[b]);
            rMM.set_value(a,b,tmp_ab);
          }
          rMM.set_value(a,size_of_ediis-n,1);
          rMM.set_value(size_of_ediis-n,a,1);
          rBB.set_value(a,0,E[ntab[a]]);
        }
        rBB.set_value(size_of_ediis-n,0,1);
//        int info=call_dgesv(rMM,rCC,rBB);
//        if(info!=0){
//          cout<<" ******** failure in call_dgesv, info="<<info<<" *********"<<endl;
//          exit(1);
//        }
        cal_simultaneous_eq(rMM, rCC, rBB);

        int flag_plus=1;
        double tmpE=0.0;
        for(int j=0;j<size_of_ediis+1;j++) tmp_coef[j]=0.0;
        for(int j=0;j<size_of_ediis-n;j++){
          if(rCC.get_value(j,0)<0) flag_plus=0;
          tmp_coef[ntab[j]]=rCC.get_value(j,0);
          tmpE+=E[ntab[j]]*tmp_coef[ntab[j]];
        }

        if(tmpE<minE && flag_plus==1){
          minE=tmpE;
          for(int j=0;j<size_of_ediis+1;j++) ret_coef[j]=tmp_coef[j];     
        }

      }
    }
  }


}


template <typename Integ1e, typename Integ2e> template <typename vec_M_tmpl,typename M_tmpl>
void SCF<Integ1e,Integ2e>::ediis(vec_M_tmpl &F, vec_M_tmpl &D, const std::vector<double> &E, int n_scf, int max_ediis) const
{

  int N_cgtos=F[0].get_I();
  int size_of_ediis=n_scf+1;
  if(size_of_ediis>=max_ediis) size_of_ediis=max_ediis;
  int ind    = n_scf%max_ediis;
  int ind_p1 = (n_scf+max_ediis+1)%max_ediis;

  M_tmpl tmpM1, tmpM2, MM;
  tmpM1.set_IJ(N_cgtos,N_cgtos);
  tmpM2.set_IJ(N_cgtos,N_cgtos);

  MM.set_IJ(size_of_ediis+1,size_of_ediis+1);

  for(int i=0;i<size_of_ediis;i++){ 
    for(int j=i;j<size_of_ediis;j++){ 
      mat_sub(tmpM1,F[i],F[j]); 
      mat_sub(tmpM2,D[i],D[j]); 
      mat_mul(tmpM1,tmpM1,tmpM2);
      double tmp_err=tmpM1.trace();
      MM.set_value(i,j,tmp_err);
      MM.set_value(j,i,tmp_err);
    }
    MM.set_value(i,size_of_ediis,1);
    MM.set_value(size_of_ediis,i,1);
  }

  std::vector<double> coef(size_of_ediis+1, 0.0);
  ediis_sub(coef, E, MM, size_of_ediis, ind);

  mat_mul_v(F[ind_p1], coef[ind_p1], F[ind_p1]);
  for(int k=0;k<size_of_ediis;k++){
    if(k!=ind_p1){
      mat_mul_v(tmpM1, coef[k], F[k]);
      mat_add(F[ind_p1], F[ind_p1], tmpM1);
    }
  }


}




template <typename Integ1e, typename Integ2e> template <typename vec_M_tmpl>
double SCF<Integ1e,Integ2e>::get_max_d(vec_M_tmpl &D, int ind, int pre_ind) const
{
  int N_cgtos = D[0].get_I();
  double max_d=0.0;
  for(int a=0;a<N_cgtos;a++){
    for(int b=a;b<N_cgtos;b++){
      double tmp_d=std::abs(D[ind].get_value(a,b)-D[pre_ind].get_value(a,b));
        if(tmp_d>max_d) max_d=tmp_d;
    }
  }
  return max_d;
}


template <typename Integ1e, typename Integ2e> template <typename M_tmpl>
double SCF<Integ1e,Integ2e>::cal_energy_u(const M_tmpl &D_a, const M_tmpl &D_b, const M_tmpl &H_core, const MolData &moldata)
{
  ene_h_core    = Util::cal_DV(D_a, H_core) + Util::cal_DV(D_b, H_core);
  ene_ele = ene_h_core + ene_vh + ene_vx + ene_dft;
  ene_vnn = Util::cal_energy_repul_nn(moldata.scgtos, moldata.ecps);
  ene_total = ene_ele + ene_vnn;
  return ene_total;
}


template <typename Integ1e, typename Integ2e> template <typename M_tmpl>
double SCF<Integ1e,Integ2e>::cal_show_energy_u(const M_tmpl &D_a, const M_tmpl &D_b, const M_tmpl &H_core, const MolData &moldata)
{
  double ret_ene_total=cal_energy_u(D_a, D_b, H_core, moldata);
  int process_num = Util_MPI::get_mpi_rank();
  if(process_num==0){
    std::cout.precision(10);
    std::cout<<std::fixed<<"    ene_h_core,vh,vx,dft "<<ene_h_core<<" "<<ene_vh<<" "<<ene_vx<<" "<<ene_dft
                         <<" ene_ele "<<ene_ele<<" ene_vnn "<<ene_vnn<<"  ene_total "<<ene_total<<std::endl;
  }
  return ret_ene_total;
}


template <typename Integ1e, typename Integ2e> template <typename M_tmpl,typename select_ERI>
void SCF<Integ1e,Integ2e>::r_scf(M_tmpl &X, std::vector<double> &lamda,
		const MolData &moldata,  select_ERI &sel_eri, const GInte_Functor &functor)
	       
{
  int process_num = Util_MPI::get_mpi_rank();


  Fock1e_tmpl<M_tmpl,Integ1e>         fock1e;
  int N_cgtos = Util_GTO::get_N_cgtos(moldata.scgtos);
  std::vector<double> E(max_diis, 0.0);
  std::vector<M_tmpl> D(max_diis), F(max_diis);
  M_tmpl  tmpM;
  std::vector<double> occ = Util::cal_occ(moldata.scgtos, moldata.ecps, moldata.mol_charge, 1);
  for(int i=0;i<max_diis;i++){
    D[i].set_IJ(N_cgtos, N_cgtos);
    F[i].set_IJ(N_cgtos, N_cgtos);
  }
  tmpM.set_IJ(N_cgtos, N_cgtos);  

  prepare_eri<M_tmpl,select_ERI>(sel_eri, moldata.scgtos);


  Util::cal_D(D[max_diis-1], X, occ);
  cal_Fock_sub(F[0], D[max_diis-1], moldata.scgtos, sel_eri, functor);

  M_tmpl S, H_core; 
  cal_h_core(H_core, moldata.scgtos, moldata.ecps);
  fock1e.cal_S(S, moldata.scgtos);
  mat_add(F[0], H_core, F[0]);

  int n_scf=0;
  double max_d=10;
  for(n_scf=0; n_scf<max_scf; n_scf++){
    int     ind=n_scf%max_diis;
    int pre_ind=(n_scf+max_diis-1)%max_diis;
    if(process_num==0) std::cout<<" ----- in r_scf cycle n_scf="<<n_scf<<" ind,pre_ind "<<ind<<" "<<pre_ind<<" ----- "<<std::endl;

    // calculate eigen and fock matrix
    cal_eigen(F[ind], S, X, lamda);
    Util::cal_D(D[ind], X, occ);                             

    mat_mul_v(D[ind], mix_dens, D[ind]);
    mat_mul_v(tmpM, (1.0-mix_dens), D[pre_ind]);
    mat_add(D[ind], tmpM, D[ind]);

    cal_Fock_sub(F[ind], D[ind], moldata.scgtos, sel_eri, functor);
    mat_add(F[ind], F[ind], H_core);

    // calculate energy
    E[ind]=cal_show_energy(D[ind], H_core, moldata);

    // convergency check
    max_d=get_max_d(D, ind, pre_ind);
    if(process_num==0) std::cout<<std::scientific<<"    max_d "<<max_d<<std::endl;
    if(n_scf>0 && max_d<threshold_scf) break;

    if(flag_do_diis==true)   diis(F, D, S, n_scf, max_diis);
    if(flag_do_ediis==true)  ediis<std::vector<M_tmpl>,M_tmpl>(F, D, E, n_scf, max_diis);
    
    

  }  // end of scf-loop
  if(n_scf==max_scf && process_num==0){
    std::cout<<" ******************* CAUTION !! *******************"<<std::endl;
    std::cout<<" dose not convegy in scf_loop, max_diis="<<max_diis <<std::endl;
    std::cout<<" **************************************************"<<std::endl;
  }
  std::cout<<" ----- end of scf-loop -----"<<std::endl;

}


template <typename Integ1e, typename Integ2e> template <typename M_tmpl,typename select_ERI>
void SCF<Integ1e,Integ2e>::u_scf(M_tmpl &X_a, M_tmpl &X_b, std::vector<double> &lamda_a, std::vector<double> &lamda_b,
		const MolData &moldata,  select_ERI &sel_eri, const GInte_Functor &functor)
	       
{
  int process_num = Util_MPI::get_mpi_rank();

  ene_vnn = Util::cal_energy_repul_nn(moldata.scgtos, moldata.ecps);
  Fock1e_tmpl<M_tmpl,Integ1e>         fock1e;
  int N_cgtos = Util_GTO::get_N_cgtos(moldata.scgtos);
  std::vector<double> E(max_diis, 0.0);
  std::vector<M_tmpl> D_a(max_diis), D_b(max_diis), F_a(max_diis), F_b(max_diis);
  M_tmpl  tmpM;
  std::vector<double> occ_a, occ_b;
  Util::cal_occ_ab(occ_a, occ_b, moldata.scgtos, moldata.ecps, moldata.mol_charge, moldata.spin);
  for(int i=0;i<max_diis;i++){
    D_a[i].set_IJ(N_cgtos, N_cgtos);
    D_b[i].set_IJ(N_cgtos, N_cgtos);
    F_a[i].set_IJ(N_cgtos, N_cgtos);
    F_b[i].set_IJ(N_cgtos, N_cgtos);
  }
  tmpM.set_IJ(N_cgtos, N_cgtos);  

  prepare_eri<M_tmpl,select_ERI>(sel_eri, moldata.scgtos);


  Util::cal_D(D_a[max_diis-1], X_a, occ_a);
  Util::cal_D(D_b[max_diis-1], X_b, occ_b);
  cal_Fock_sub_u(F_a[0], F_b[0], D_a[max_diis-1], D_b[max_diis-1], moldata.scgtos, sel_eri, functor);

  M_tmpl S, H_core; 
  cal_h_core(H_core, moldata.scgtos, moldata.ecps);
  fock1e.cal_S(S, moldata.scgtos);
  mat_add(F_a[0], H_core, F_a[0]);
  mat_add(F_b[0], H_core, F_b[0]);

  int n_scf=0;
  double max_d_a=10;
  double max_d_b=10;
  for(n_scf=0; n_scf<max_scf; n_scf++){
    int     ind=n_scf%max_diis;
    int pre_ind=(n_scf+max_diis-1)%max_diis;
    if(process_num==0){
      std::cout<<" ----- in u_scf cycle n_scf="<<n_scf<<" ind,pre_ind "<<ind<<" "<<pre_ind;
      if(flag_do_ediis)  std::cout<<", use ediis, ";
      std::cout<<" ----- "<<std::endl;
    }

    // calculate eigen and fock matrix
    cal_eigen(F_a[ind], S, X_a, lamda_a);
    cal_eigen(F_b[ind], S, X_b, lamda_b);
    Util::cal_D(D_a[ind], X_a, occ_a);                             
    Util::cal_D(D_b[ind], X_b, occ_b);                             

    mat_mul_v(D_a[ind], mix_dens, D_a[ind]);
    mat_mul_v(D_b[ind], mix_dens, D_b[ind]);
    mat_mul_v(tmpM, (1.0-mix_dens), D_a[pre_ind]);
    mat_add(D_a[ind], tmpM, D_a[ind]);
    mat_mul_v(tmpM, (1.0-mix_dens), D_b[pre_ind]);
    mat_add(D_b[ind], tmpM, D_b[ind]);

    cal_Fock_sub_u(F_a[ind], F_b[ind], D_a[ind], D_b[ind], moldata.scgtos, sel_eri, functor);
    mat_add(F_a[ind], F_a[ind], H_core);
    mat_add(F_b[ind], F_b[ind], H_core);

    // calculate energy
    E[ind]=cal_show_energy_u(D_a[ind], D_b[ind], H_core, moldata);

    // convergency check
    max_d_a=get_max_d(D_a, ind, pre_ind);
    max_d_b=get_max_d(D_b, ind, pre_ind);
    if(process_num==0) std::cout<<std::scientific<<"    max_d_a,b "<<max_d_a<<" "<<max_d_b<<std::endl;
    if(n_scf>0 && max_d_a<threshold_scf && max_d_b<threshold_scf) break;

    if(flag_do_diis==true){
      diis(F_a, D_a, S, n_scf, max_diis);
      diis(F_b, D_b, S, n_scf, max_diis);
    }else if(flag_do_ediis==true){
      ediis<std::vector<M_tmpl>,M_tmpl>(F_a, D_a, E, n_scf, max_diis);
      ediis<std::vector<M_tmpl>,M_tmpl>(F_b, D_b, E, n_scf, max_diis);
    }

  }  // end of scf-loop
  if(n_scf==max_scf && process_num==0){
    std::cout<<" ******************* CAUTION !! *******************"<<std::endl;
    std::cout<<" dose not convegy in scf_loop, max_diis="<<max_diis <<std::endl;
    std::cout<<" **************************************************"<<std::endl;
  }
  std::cout<<" ----- end of scf-loop -----"<<std::endl;

}




}  // end of namespace "Lotus_core"



#endif   // end of include-guard


