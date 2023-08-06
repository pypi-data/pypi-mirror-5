


#
#  Please give C++ compiler and its options to "CXX" variable.
#


#CXX = ccache clang++ -O2
#CXX = g++     -O2
#CXX = g++  -fopenmp  -O2
CXX = clang++ -O2 
#CXX = mpicxx -fopenmp -DUSE_MPI_LOTUS -O2


#
#  Usually, you do not need to touch bellow.
#



PINT_DIR       = ../pint

SRCS   = main_tests_1.cpp main_tests_2.cpp main_tests_3.cpp main_tests_4.cpp main_tests_5.cpp \
         main_tests_6.cpp main_tests_7.cpp main_tests_8.cpp main_tests_9.cpp

EXE      = $(subst .cpp,.exe,$(SRCS))

INC_PATH = $(patsubst %,-I%,../include_hpp ../include_py $(PINT_DIR)/include_hpp $(PINT_DIR)/include_py)

all: $(PINT_DIR) $(EXE) 

$(PINT_DIR):
	cd ..; hg clone --insecure https://www.hpcu.aics.riken.jp/rhodecode/pint
#	cd ..; hg clone https://bitbucket.org/tshima/pint

$(EXE): %.exe:  %.cpp 
	$(CXX) $(INC_PATH) -o $@ $< -lm 

exec_tests:
	main_tests_1.exe
	main_tests_2.exe
	main_tests_3.exe
	main_tests_4.exe
	main_tests_5.exe
	main_tests_6.exe
	main_tests_7.exe
	main_tests_8.exe
	main_tests_9.exe

exec_tests_mpi:
	mpiexec -np 2 main_tests_1.exe
	mpiexec -np 2 main_tests_2.exe
	mpiexec -np 2 main_tests_3.exe
	mpiexec -np 2 main_tests_4.exe
	mpiexec -np 2 main_tests_5.exe
	mpiexec -np 2 main_tests_6.exe
	mpiexec -np 2 main_tests_7.exe
	mpiexec -np 2 main_tests_8.exe
	mpiexec -np 2 main_tests_9.exe


clean:
	-rm -rf *.exe
	-rm -rf *.exe.dSYM



