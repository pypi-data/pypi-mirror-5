
#ifndef PINT_PY_HPP
#define PINT_PY_HPP

#define BOOST_PYTHON_STATIC_LIB
#include <boost/python.hpp>
#include "PInt1e_py.hpp"


void append_inittab_pint(){

  PyImport_AppendInittab("PInt1e",        PInt::initPInt1e);

}


#endif 


