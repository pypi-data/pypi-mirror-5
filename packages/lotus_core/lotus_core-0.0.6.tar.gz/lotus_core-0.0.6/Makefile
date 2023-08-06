        

#
#  To build python-extension modules,
#  please install the BOOST-library (http://www.boost.org) in your computer system.
#
#  To compile executable files and python-extension modules,
#  please set appropriate "CXX" and "BOOST_INCLUDE_PATH" variables, which indicates 
#  C++ compiler and the include-path for header-files of the BOOST-library, respectively.
#
#  To build with the MPI-library, please use the flag of "-DUSE_MPI_LOTUS", 
#  such as "CXX = mpicxx -DUSE_MPI_LOTUS".
#
#  This makefile downloads the "pint" library from "https://bitbucket.org/tshima" or 
#  "https://www.hpcu.aics.riken.jp/rhodecode" by using the "hg" command.
#  Please check the makefile-target of "use_libs". 
#


#CXX = ccache clang++ -O2
#CXX = ccache g++ -O2
#CXX = clang++ -O2
CXX = g++     -O2
#CXX = g++     -O2  -DNOUSE_EIGEN_LOTUS
#CXX = g++  -fopenmp  -O2
#CXX = mpicxx -openmp -DUSE_MPI_LOTUS -w
#CXX = icpc -openmp -O2
#CXX = mpicxx -fopenmp -DUSE_MPI_LOTUS -O2
#CXX  = pgcpp -O2
#CXX = ccache mpicxx -DUSE_MPI_LOTUS -fopenmp  -O2


BOOST_INCLUDE_PATH = /opt/local/include  /usr/include  $(HOME)/local/lib
#BOOST_INCLUDE_PATH = /usr/include 



#
#  Usually, you do not need to touch bellow.
#

# list of download-modules.
use_libs        = pint 

# list of compile basenames of compile module. 
# This variable controls build-target python-extension-modules.
compile_modules = core 


TARGET_EXE     = lotus_core.exe
TARGET_PY_EXE  = python4lotus


OS = $(shell uname)
SHARED = -shared
ifeq ($(strip $(OS)),Darwin) # for mac
  SHARED = -bundle
endif


dires =  bin lib

vpath %.cpp   src
vpath %.h     include_hpp include_py
vpath %.hpp   include_hpp include_py


PYTHON_INCLUDE = $(shell python-config --include)
PYTHON_LDFLAGS = $(shell python-config --ldflags)
LOTUS_HPP_PATH = $(patsubst %,%/include_hpp,$(use_libs))
LOTUS_PY_PATH  = $(patsubst %,%/include_py, $(use_libs))
INC_PATH       = $(patsubst %,-I%,include_hpp include_py $(LOTUS_HPP_PATH) $(LOTUS_PY_PATH) $(BOOST_INCLUDE_PATH))
LOTUS_MODULES  = $(patsubst %,lib/lotus_%_hpp.so, $(compile_modules))

all: $(dires) $(use_libs) bin/$(TARGET_EXE) bin/$(TARGET_PY_EXE) $(LOTUS_MODULES)
  
$(dires): 
	mkdir -p $@

$(use_libs):
	hg clone --insecure https://www.hpcu.aics.riken.jp/rhodecode/$@
#	hg clone https://www.hpcu.aics.riken.jp/rhodecode/$@
#	hg clone https://bitbucket.org/tshima/$@


bin/$(TARGET_EXE): src/main_lotus.cpp
	$(CXX) $(INC_PATH) -o $@ src/main_lotus.cpp -lm  


bin/$(TARGET_PY_EXE): src/main_python4lotus_core.cpp 
	$(CXX) $(INC_PATH) $(PYTHON_INCLUDE) -o $@ src/main_python4lotus_core.cpp  -lm $(PYTHON_LDFLAGS) -lboost_python

$(LOTUS_MODULES):
	$(CXX) $(INC_PATH) $(PYTHON_INCLUDE) \
	-DPIC -fPIC $(SHARED) -o $@ src/module_$(patsubst lib/lotus_%_hpp.so,%,$@).cpp $(PYTHON_LDFLAGS) -lboost_python


sdist:  pint
	rm -rf dist
	cp -r include_hpp         lotus_core
	cp -r include_py          lotus_core
	cp -r tests_py            lotus_core
	mkdir -p                  lotus_core/pint
	cp -r pint/include_hpp    lotus_core/pint
	cp -r pint/include_py     lotus_core/pint
	python setup.py sdist	
#	rm -rf lotus_core/include_hpp
#	rm -rf lotus_core/include_py
#	rm -rf lotus_core/tests_py
#	rm -rf lotus_core/pint

sdist-upload: 
	make distclean
	make pint 
	cd pint; rm -rf .hg
	cp -r include_hpp         lotus_core
	cp -r include_py          lotus_core
	cp -r tests_py            lotus_core
	mkdir -p                  lotus_core/pint
	cp -r pint/include_hpp    lotus_core/pint
	cp -r pint/include_py     lotus_core/pint
	python setup.py sdist upload
	rm -rf lotus_core/include_hpp
	rm -rf lotus_core/include_py
	rm -rf lotus_core/tests_py
	rm -rf lotus_core/pint
	make distclean


exec_tests:
	cd tests; make clean; make

clean:
	-cd tests; make clean
	-cd tests_py; make clean
	-cd lotus_core; rm *.pyc
	-rm -rf $(bin)/$(TARGET_EXE)
	-rm -rf $(bin)/$(TARGET_PY_EXE)
	-rm -rf $(LOTUS_MODULES)
	-rm -rf dist
	-rm -rf bin
	-rm -rf lotus*.egg-info
	-rm -rf lotus_core/include_hpp
	-rm -rf lotus_core/include_py
	-rm -rf lotus_core/pint
	-rm -rf lotus_core/tests_py

distclean:
	make clean
	-rm -rf $(use_libs)
	-rm -rf bin
	-rm -rf lib
	-rm -rf build


