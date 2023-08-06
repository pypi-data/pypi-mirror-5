/**
 * @file io/cxx/SoxReader.cc
 * @date Tue Nov 12 11:54:30 CET 2013
 * @author Elie Khoury <elie.khoury@idiap.ch>
 *
 * @brief A class to help you read audio. This code is based on Sox 
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

#include <stdexcept>
#include <boost/format.hpp>
#include <boost/preprocessor.hpp>
#include <boost/filesystem.hpp>
#include <limits>
#include <bob/core/check.h>
#include <bob/core/blitz_array.h>
#include <bob/core/logging.h>
extern "C" {
#include <sox.h>
}
#include <assert.h>

#include "utilities.h"
#include "reader.h"



xbob::sox::SoxReader::SoxReader(const std::string& filename) {
  open(filename);
}


void xbob::sox::SoxReader::open(const std::string& filename) {
  m_filename = filename;
  if (!boost::filesystem::exists(filename)) {
    boost::format m("file '%s' is not readable");
    m % filename;
    throw std::runtime_error(m.str());
  }
  m_infile_cache = sox_open_read(m_filename.c_str(), NULL, NULL, NULL);
  m_offset = m_infile_cache->tell_off;
  
  m_signal_cache = m_infile_cache->signal;
  m_nchannels = m_signal_cache.channels;
  m_nsamples = (int)m_signal_cache.length/(int)m_signal_cache.channels; // This is number of samples 
  m_rate = m_signal_cache.rate;
  m_bits_per_sample = m_signal_cache.precision; 
  m_duration = (double)m_nsamples/m_rate;
  sox_encodinginfo_t encoding_info = m_infile_cache->encoding;
  encoderTypeToString(encoding_info.encoding, m_encoding_name);
  m_compression_factor = encoding_info.compression;
    
  // Set typeinfo variables
  m_typeinfo.dtype = bob::core::array::t_float32;
  m_typeinfo.nd = 2;
  m_typeinfo.shape[0] = m_nchannels;
  m_typeinfo.shape[1] = m_nsamples;
  m_typeinfo.update_strides();

}


xbob::sox::SoxReader::~SoxReader() {
 sox_close(m_infile_cache);
}

double xbob::sox::SoxReader::load(blitz::Array<float,2>& data) {
  bob::core::array::blitz_array tmp(data);
  return load(tmp);
}

void xbob::sox::SoxReader::reset(){
  sox_seek(m_infile_cache, m_offset, SOX_SEEK_SET);
  if ((size_t)m_infile_cache->tell_off != m_offset) // force it!!
  {
    sox_close(m_infile_cache);
    m_infile_cache = sox_open_read(m_filename.c_str(), NULL, NULL, NULL);
  }  
}

double xbob::sox::SoxReader::load(bob::core::array::interface& buffer)  {

  //checks if the output array shape conforms to the audio specifications,
  //otherwise, throw.
  if (!m_typeinfo.is_compatible(buffer.type())) {
    boost::format s("input buffer (%s) does not conform to the audio size specifications (%s)");
    s % buffer.type().str() % m_typeinfo.str();
    throw std::runtime_error(s.str());
  }
  
  sox_sample_t *row_pointer= (sox_sample_t *) malloc(sizeof(sox_sample_t) *m_nchannels);  

  //now we copy from one container to the other, using our Blitz++ technique
  blitz::TinyVector<int,2> shape;
  blitz::TinyVector<int,2> stride;
  
  shape = m_typeinfo.shape[0], m_typeinfo.shape[1];
  stride = m_typeinfo.stride[0], m_typeinfo.stride[1];

  blitz::Array<float,2> dst(static_cast<float*>(buffer.ptr()), shape, stride, blitz::neverDeleteData);

  for (int i=0; i<(int)m_nsamples; i++)
  {
    sox_read(m_infile_cache, row_pointer, m_nchannels);
    
    for (int j=0; j<(int)m_nchannels; j++)
      dst(j,i)=((float)row_pointer[j]) / SOX_CONVERSION_COEF;
  }
  reset();
  free(row_pointer);
  return m_rate;
}

