/**
 * @file bob/io/SoxReader.h
 * @date Thu Nov 14 20:46:52 CET 2013
 * @author Elie Khoury <elie.khoury@idiap.ch>
 *
 * @brief A class for some utilities using sox. This code is based on Sox 
 * <http://sox.sourceforge.net/>.
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

#ifndef SOX_UTILITIES_H
#define SOX_UTILITIES_H

#include <stdexcept>
#include <boost/format.hpp>
#include <boost/preprocessor.hpp>
#include <limits>
#include <bob/core/check.h>
#include <bob/core/blitz_array.h>
#include <bob/core/logging.h>
#include <assert.h>
extern "C" {
#include <sox.h>
}

#define SOX_CONVERSION_COEF 2147483648.

namespace xbob { namespace sox {
   
   void encoderTypeToString(const sox_encoding_t encoding, std::string& encoding_name); 

   void encoderStringToType(const std::string& encoding_name, sox_encoding_t *encoding ); 
}}
#endif //SOX_UTILITIES_H
