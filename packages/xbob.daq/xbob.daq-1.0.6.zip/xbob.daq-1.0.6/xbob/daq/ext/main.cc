/**
 * @file daq/python/main.cc
 * @date Mon 06 Feb 2012 15:19:05 CET
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief Combines all modules to make up the complete bindings
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, version 3 of the License.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "bob/config.h"
#ifdef BOB_API_VERSION /* this macro is only available with bob >= 1.2.0 */
#include "bob/python/ndarray.h"
#else
#include "bob/core/python/ndarray.h"
#endif

void bind_daq_version();

#ifdef WITH_FFMPEG
void bind_daq_all();
#endif

BOOST_PYTHON_MODULE(_daq) {
  boost::python::docstring_options docopt(true, true, false);
  bob::python::setup_python("bob classes and sub-classes for data acquisition");

  bind_daq_version();

# ifdef WITH_FFMPEG
  bind_daq_all();
# endif
}
