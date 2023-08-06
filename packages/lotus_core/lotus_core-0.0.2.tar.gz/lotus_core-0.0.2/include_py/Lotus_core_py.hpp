


#ifndef LOTUS_CORE_PY_H
#define LOTUS_CORE_PY_H

#include <boost/python.hpp>

#include "CVector_py.hpp"
#include "Charge_py.hpp"
#include "DFT_func_py.hpp"
#include "ECP_tmpl_py.hpp"
#include "Fock1e_tmpl_py.hpp"
#include "Fock2e_tmpl_py.hpp"
#include "GInte_Functor_py.hpp"
#include "Gradient_py.hpp"
#include "Grid_py.hpp"
#include "Grid_Inte_py.hpp"
#include "Matrixs_tmpl_py.hpp"
#include "Mixin_core_py.hpp"
#include "SCF_py.hpp"
#include "Util_py.hpp"
#include "Util_PBC_py.hpp"
#include "Util_MPI_py.hpp"
#include "gto_py.hpp"

namespace Lotus_core {

  BOOST_PYTHON_MODULE(lotus_core_hpp){
    CVector_def_boost_py();
    Charge_def_boost_py();
    DFT_func_def_boost_py();
    ECP_def_boost_py();
    Fock1e_def_boost_py();
    Fock2e_def_boost_py();
    GInte_Functor_def_boost_py();
    Gradiend_def_boost_py();
    Grid_def_boost_py();
    Grid_Inte_def_boost_py();
    Matrixs_def_boost_py();
    Mixin_core_def_boost_py();
    SCF_def_boost_py();
    Util_def_boost_py();
    Util_PBC_def_boost_py();
    Util_MPI_def_boost_py();
    gto_def_boost_py(); 
  }

}   // end of namespace "Lotus_core"

void append_inittab_lotus_core(){
  PyImport_AppendInittab("lotus_core_hpp",       Lotus_core::initlotus_core_hpp);
}


#endif //include-guard
