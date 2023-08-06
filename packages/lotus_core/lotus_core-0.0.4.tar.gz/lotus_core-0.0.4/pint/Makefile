
CXX      = g++
CXX_FLAG = -O2


TARGET_CPP     = main_pint.cpp
TARGET_EXE     = pint.exe

INC_PATH = $(patsubst %,-I%,include_hpp)
  
all: bin  bin/$(TARGET_EXE)

bin:
	mkdir -p bin


bin/$(TARGET_EXE): src/main_pint.cpp
	$(CXX) $(CXX_FLAG) $(INC_PATH) -o $@ $< -lm 

exec:
	bin/pint.exe

clean:
	-rm -rf bin


