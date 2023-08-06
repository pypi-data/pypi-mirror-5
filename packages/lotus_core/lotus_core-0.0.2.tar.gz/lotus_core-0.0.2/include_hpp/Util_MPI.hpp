


#ifndef UTIL_MPI_H
#define UTIL_MPI_H


#ifdef USE_MPI_LOTUS
#include "mpi.h"
#endif


#include <string.h>

#include <string>
#include <vector>


namespace Lotus_core {

#ifdef USE_MPI_LOTUS
template <typename T>
struct MPI_LOTUS_static {
  static MPI_Comm MPI_COMM_LOTUS;
};
template <typename T>
MPI_Comm MPI_LOTUS_static<T>::MPI_COMM_LOTUS = NULL;
#else
typedef int MPI_Comm;
#endif

class Util_MPI {
public:


  static void set_MPI_COMM_LOTUS(MPI_Comm in_comm){ 
    #ifdef USE_MPI_LOTUS
    MPI_LOTUS_static<int> mpi_lotus_static;
    mpi_lotus_static.MPI_COMM_LOTUS=in_comm;
    #endif
  }

  static void set_MPI_COMM_LOTUS(int N_process_lotus, int *mpi_comm_lotus_ranks, MPI_Comm parent_mpi_comm)
  {
    #ifdef USE_MPI_LOTUS
    MPI_Group group_parent,group_lotus;
    MPI_Comm_group(parent_mpi_comm,&group_parent);
    MPI_Group_incl(group_parent,N_process_lotus,mpi_comm_lotus_ranks,&group_lotus);
    MPI_LOTUS_static<int> mpi_lotus_static;
    MPI_Comm_create(parent_mpi_comm,group_lotus,&(mpi_lotus_static.MPI_COMM_LOTUS));
    #endif
  }

  static void set_MPI_COMM_LOTUS()
  {
    #ifdef USE_MPI_LOTUS
    int N_process;
    MPI_Comm_size(MPI_COMM_WORLD,&N_process);
    std::vector<int> mpi_comm_lotus_ranks(N_process);
    for(int p=0;p<N_process;p++) mpi_comm_lotus_ranks[p]=p;
    set_MPI_COMM_LOTUS(N_process, &mpi_comm_lotus_ranks[0], MPI_COMM_WORLD);
    #endif
  }  

  // for boost-python
  static void set_MPI_COMM_LOTUS_bp1(MPI_Comm &in_comm){  set_MPI_COMM_LOTUS(in_comm); }
  static void set_MPI_COMM_LOTUS_bp2(int N_process_lotus, int *mpi_comm_lotus_ranks, MPI_Comm &parent_mpi_comm){
    set_MPI_COMM_LOTUS(N_process_lotus, mpi_comm_lotus_ranks, parent_mpi_comm);
  }
  static void set_MPI_COMM_LOTUS_bp3(){  set_MPI_COMM_LOTUS(); }
  // 



  static void barrier(){
    #ifdef USE_MPI_LOTUS
    MPI_LOTUS_static<int> mpi_lotus_static;
    MPI_Barrier(mpi_lotus_static.MPI_COMM_LOTUS);
    #endif
  }

  static void get_size_rank(int &N_process,int &process_num)
  {
    #ifdef USE_MPI_LOTUS
      MPI_LOTUS_static<int> mpi_lotus_static;
//      MPI_Barrier((mpi_lotus_static.MPI_COMM_LOTUS));
      MPI_Comm_size(mpi_lotus_static.MPI_COMM_LOTUS,&N_process);
      MPI_Comm_rank(mpi_lotus_static.MPI_COMM_LOTUS,&process_num);
    #else
      N_process=1;
      process_num=0;
    #endif
  }


  static int get_mpi_size()
  {
    int N_process;
    #ifdef USE_MPI_LOTUS
      MPI_LOTUS_static<int> mpi_lotus_static;
//      MPI_Barrier(mpi_lotus_static.MPI_COMM_LOTUS);
      MPI_Comm_size(mpi_lotus_static.MPI_COMM_LOTUS,&N_process);
    #else
      N_process=1;
    #endif
    return N_process;
  }


  static int get_mpi_rank()
  {
    int process_num;
    #ifdef USE_MPI_LOTUS
      MPI_LOTUS_static<int> mpi_lotus_static;
//      MPI_Barrier(mpi_lotus_static.MPI_COMM_LOTUS);
      MPI_Comm_rank(mpi_lotus_static.MPI_COMM_LOTUS,&process_num);
    #else
      process_num=0;
    #endif
    return process_num;
  }


  template <typename M_tmpl>
  static void allreduce(M_tmpl &matA){
    #ifdef USE_MPI_LOTUS
    barrier();
    int I=matA.get_I();
    int J=matA.get_J();
    std::vector<double> send_mat(I*J, 0.0);
    std::vector<double> recv_mat(I*J, 0.0);
    for(int i=0;i<I;i++){
      for(int j=0;j<I;j++){
        send_mat[i*J+j]=matA.get_value(i,j);
      }
    }
    MPI_LOTUS_static<int> mpi_lotus_static;
    MPI_Allreduce(&send_mat[0], &recv_mat[0], I*J, MPI_DOUBLE, MPI_SUM, mpi_lotus_static.MPI_COMM_LOTUS);
    barrier();
    for(int i=0;i<I;i++){
      for(int j=0;j<J;j++){
        matA.set_value(i, j, recv_mat[i*J+j]);
      }
    }
    #endif
  }

  static void allreduce(std::vector<double> &data)
  {
    #ifdef USE_MPI_LOTUS
    barrier();
    int N_data = data.size();
    std::vector<double> tmp_data(N_data, 0.0);
    for(int i=0;i<N_data;i++){
      tmp_data[i]=data[i];
      data[i]=0.0;
    }
    MPI_LOTUS_static<int> mpi_lotus_static;
    MPI_Allreduce(&tmp_data[0], &data[0], N_data, MPI_DOUBLE, MPI_SUM, mpi_lotus_static.MPI_COMM_LOTUS); 
    barrier();
    #endif
  }

  static void allreduce(double &in_out_v)
  {
    std::vector<double> mpi_v(1);
    mpi_v[0]=in_out_v;
    allreduce(mpi_v);
    in_out_v=mpi_v[0];
  }
  template <typename M_tmpl>
  static void allreduce(std::vector<M_tmpl*> &vec_ptrM){
    for(int i=0;i<vec_ptrM.size();i++){
      allreduce(*vec_ptrM[i]);
    }
  }

  // for boost-python
  template <typename M_tmpl>
  static void allreduce_bp1(M_tmpl &matA){
    allreduce(matA);
  }
  static void allreduce_bp2(std::vector<double> &data){
    allreduce(data);
  }
  static void allreduce_bp3(double &in_out_v){
    allreduce_bp3(in_out_v);
  }
  template <typename M_tmpl>
  static void allreduce_bp4(std::vector<M_tmpl*> &vec_ptrM){
    allreduce(vec_ptrM);
  }




  template <typename M_tmpl>
  static void isendrecv(M_tmpl &matA){  isendrecv(matA, 0, 1.0e-14); }

  template <typename M_tmpl>
  static void isendrecv(M_tmpl &matA, int tag, double CUTOFF)
  {
    #ifdef USE_MPI_LOTUS
    MPI_LOTUS_static<int> mpi_lotus_static;
    MPI_Barrier(mpi_lotus_static.MPI_COMM_LOTUS);
    int N_process=1;
    int process_num=0;
    MPI_Comm_size(mpi_lotus_static.MPI_COMM_LOTUS,&N_process);
    MPI_Comm_rank(mpi_lotus_static.MPI_COMM_LOTUS,&process_num);

    MPI_Status  status_indx,status_data;
    MPI_Request request_indx,request_data;
    int I=matA.get_I();
    int J=matA.get_J();
  
    // max_data
    int max_data=0;
    for(int i=0;i<I;i++){
      for(int j=0;j<J;j++){
        double tmp_v=matA.get_value(i,j);
        if(fabs(tmp_v)>CUTOFF) max_data++;
        else matA.set_value(i,j,0.0);
      }
    }

    int tmp_num=max_data;
    MPI_Allreduce(&tmp_num, &max_data, 1, MPI_INT, MPI_MAX, mpi_lotus_static.MPI_COMM_LOTUS);
  
    // copy data
    std::vector<double> send_data(max_data);
    std::vector<int>    send_indx(max_data);
    int num_data=0;
    for(int i=0;i<I;i++){
      for(int j=0;j<J;j++){
        double tmp_v=matA.get_value(i,j);
        if(fabs(tmp_v)>CUTOFF){
          send_indx[num_data]=i*J+j;
          send_data[num_data]=tmp_v;
          num_data++;
        } 
      }
    }

    // isend
    for(int p=0;p<N_process;p++){
      if(p!=process_num){
        MPI_Isend(&send_indx[0], num_data, MPI_INT,    p, tag+1000, mpi_lotus_static.MPI_COMM_LOTUS, &request_indx);
        MPI_Isend(&send_data[0], num_data, MPI_DOUBLE, p, tag+1001, mpi_lotus_static.MPI_COMM_LOTUS, &request_data);
        MPI_Request_free(&request_indx);
        MPI_Request_free(&request_data);
      }
    }

    MPI_Barrier(mpi_lotus_static.MPI_COMM_LOTUS);

    // irecv
    std::vector<double> recv_data(max_data); 
    std::vector<int>    recv_indx(max_data); 
    for(int p=0;p<N_process;p++){
      if(p!=process_num){
        int num_recv;
        MPI_Irecv(&recv_indx[0], max_data, MPI_INT,    p, tag+1000, mpi_lotus_static.MPI_COMM_LOTUS, &request_indx);
        MPI_Irecv(&recv_data[0], max_data, MPI_DOUBLE, p, tag+1001, mpi_lotus_static.MPI_COMM_LOTUS, &request_data);
        MPI_Wait(&request_indx,&status_indx);
        MPI_Wait(&request_data,&status_data);
        MPI_Get_count(&status_indx, MPI_INT, &num_recv);
        for(int cc=0;cc<num_recv;cc++){
          int tmp_indx = recv_indx[cc];
          int tmp_i    = (tmp_indx%(I*J))/J;
          int tmp_j    = (tmp_indx%(I*J))%J;
          double tmp_v = recv_data[cc];
          matA.add(tmp_i,tmp_j,tmp_v);
        }
      }
    }

    MPI_Barrier(mpi_lotus_static.MPI_COMM_LOTUS);
    #endif
  }

  template <typename M_tmpl>
  static void isendrecv(std::vector<M_tmpl*> &vec_ptrM, int tag, double CUTOFF){
    for(int i=0;i<vec_ptrM.size();i++){
      isendrecv(*vec_ptrM[i], tag, CUTOFF);
    }
  }
  template <typename M_tmpl>
  static void isendrecv(std::vector<M_tmpl*> &vec_ptrM){
    for(int i=0;i<vec_ptrM.size();i++){
      isendrecv(*vec_ptrM[i], 0, 1.0e-14);
    }
  }


  template <typename M_tmpl>
  static void isendrecv_bp1(M_tmpl &matA, int tag, double CUTOFF){
    isendrecv(matA, tag, CUTOFF);
  }
  template <typename M_tmpl>
  static void isendrecv_bp2(M_tmpl &matA){
    isendrecv(matA);
  }
  template <typename M_tmpl>
  static void isendrecv_bp3(std::vector<M_tmpl*> &vec_ptrM, int tag, double CUTOFF){
    isendrecv(vec_ptrM, tag, CUTOFF);
  }
  template <typename M_tmpl>
  static void isendrecv_bp4(std::vector<M_tmpl*> &vec_ptrM){
    isendrecv(vec_ptrM);
  }


  static std::string broadcast_text(const char *in_text){
    int in_N = strlen(in_text);
    int N_char=in_N;
    #ifdef USE_MPI_LOTUS
    MPI_LOTUS_static<int> mpi_lotus_static;
    MPI_Allreduce(&in_N, &N_char, 1, MPI_INT, MPI_MAX, mpi_lotus_static.MPI_COMM_LOTUS);
    #endif

    if(N_char==0){
      std::string ret("");
      return ret;
    }

    char *message = new char [N_char+1];
    int process_num = Util_MPI::get_mpi_rank();
    if(process_num==0) strcpy(message, in_text);

    #ifdef USE_MPI_LOTUS
    MPI_Bcast(message, N_char, MPI_CHAR, 0, mpi_lotus_static.MPI_COMM_LOTUS); 
    #endif
    std::string ret(message);

    delete [] message;
    return ret;
  }

  static std::string broadcast_text(const std::string &in_text){
    return broadcast_text(in_text.c_str());
  }

  // for boost-python
  static std::string broadcast_text_bp1(const char *in_text){         return broadcast_text(in_text); }
  static std::string broadcast_text_bp2(const std::string &in_text){  return broadcast_text(in_text); }
  // 


  static int broadcast_int(int in){
    int message;
    int process_num = Util_MPI::get_mpi_rank();
    if(process_num==0) message=in;
    #ifdef USE_MPI_LOTUS
    MPI_LOTUS_static<int> mpi_lotus_static;
    MPI_Bcast(&message, 1, MPI_INT, 0, mpi_lotus_static.MPI_COMM_LOTUS); 
    #endif
    return message;
  }

  static double broadcast_double(double in){
    double message;
    int process_num = Util_MPI::get_mpi_rank();
    if(process_num==0) message=in;
    #ifdef USE_MPI_LOTUS
    MPI_LOTUS_static<int> mpi_lotus_static;
    MPI_Bcast(&message, 1, MPI_DOUBLE, 0, mpi_lotus_static.MPI_COMM_LOTUS); 
    #endif
    return message;
  }

//  int copy_textfile(const char *filename);

};


/*
int Util_MPI::copy_textfile(const char *filename)
{
  int is_file=1;
  #ifdef USE_MPI_LOTUS
    MPI_Barrier(Util_MPI::MPI_COMM_LOTUS);
    int N_process=1;
    int process_num=0;
    MPI_Comm_size(Util_MPI::MPI_COMM_LOTUS,&N_process);
    MPI_Comm_rank(Util_MPI::MPI_COMM_LOTUS,&process_num);

    ifstream check_ifs(filename);
    if(!check_ifs) is_file=0;
    check_ifs.close();

    ifstream ifs;
    ofstream ofs;
    const int N_len=1024; 
    char line[N_len];
    int N_lines=0;
    if(process_num==0){
      ifs.open(filename);
      if(!ifs){
        cout<<" cannot open file "<<filename<<endl;
        exit(1);
      }
      for(;;){
        if(!ifs.getline(line,sizeof(line))) break;
        N_lines++;
      } 
      ifs.close();
      ifs.open(filename);
    }else{
      if(is_file==0){
        ofs.open(filename);
        if(!ofs){
           cout<<" cannot open file "<<filename<<endl;
           exit(1);
        }
      }
    }
    MPI_Barrier(Util_MPI::MPI_COMM_LOTUS);
    MPI_Bcast(&N_lines, 1, MPI_INT, 0, Util_MPI::MPI_COMM_LOTUS);

    for(int i=0;i<N_lines;i++){
      MPI_Barrier(Util_MPI::MPI_COMM_LOTUS);
      if(process_num==0) ifs.getline(line,sizeof(line));
      MPI_Bcast((void*)line,N_len, MPI_CHAR, 0, Util_MPI::MPI_COMM_LOTUS);
      if(process_num!=0 && is_file==0) ofs<<line<<endl;
    }
    
    MPI_Barrier(Util_MPI::MPI_COMM_LOTUS);
    if(process_num==0)               ifs.close();
    if(process_num!=0 && is_file==0) ofs.close(); 
    MPI_Barrier(Util_MPI::MPI_COMM_LOTUS);
  #endif
   return is_file;
}
*/





}  // end of namespace "Lotus_core"

#endif // end of include-guard

