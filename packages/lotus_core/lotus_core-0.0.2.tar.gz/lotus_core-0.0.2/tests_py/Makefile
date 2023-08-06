


all: exec_tests


exec_tests:
	../bin/python4lotus test1.py
	../bin/python4lotus test2.py
	../bin/python4lotus test3.py
	../bin/python4lotus test4.py
	../bin/python4lotus test5.py
	../bin/python4lotus test6.py
	../bin/python4lotus test7.py
	../bin/python4lotus test8.py

exec_tests_mpi:
	mpiexec -np 2 ../bin/python4lotus test1.py
	mpiexec -np 2 ../bin/python4lotus test2.py
	mpiexec -np 2 ../bin/python4lotus test3.py
	mpiexec -np 2 ../bin/python4lotus test4.py
	mpiexec -np 2 ../bin/python4lotus test5.py
	mpiexec -np 2 ../bin/python4lotus test6.py
	mpiexec -np 2 ../bin/python4lotus test7.py
	mpiexec -np 2 ../bin/python4lotus test8.py


clean:
	rm *.pyc

